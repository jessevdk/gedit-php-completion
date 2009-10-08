# -*- coding: utf-8 -*-

#  phpcompletion.py - PHP completion using the completion framework
#  
#  Copyright (C) 2009 - Jesse van den Kieboom
#  Copyright (C) 2009 - Ignacio Casal Quinteiro
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import gtk
import gedit
from gettext import gettext as _
import gtksourceview2 as gsv
import phpprovider
import utils
import os

class PHPCompletionWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        
        # TODO: use get_data_dir when db is nicely installed in the correct place
        self._provider = phpprovider.PHPProvider(os.path.join(plugin.get_install_dir(), 'phpcompletion', 'phpsymbols.db'))
        
        for view in self._window.get_views():
            self.add_view(view)

        self._tab_added_id = self._window.connect('tab-added', self.on_tab_added)
        self._tab_removed_id = self._window.connect('tab-removed', self.on_tab_removed)

    def deactivate(self):
        # Remove the provider from all the views
        for view in self._window.get_views():
            view.get_completion().completion.remove_provider(self._provider)

        self._window.disconnect(self._tab_added_id)
        self._window.disconnect(self._tab_removed_id)

        self._window = None
        self._plugin = None

    def update_ui(self):
        pass
    
    def add_view(self, view):
       view.get_completion().add_provider(self._provider)
       view.get_completion().connect('populate-context', self.on_populate_context)

    def remove_view(self, view):
        view.get_completion().remove_provider(self._provider)

    def on_tab_added(self, window, tab):
        # Add provider to the new view
        self.add_view(tab.get_view())
    
    def on_tab_removed(self, window, tab):
        # Remove provider from the view
        self.remove_view(tab.get_view())

    def check_is_class(self, context):
        piter = context.get_iter()
        
        start = piter.copy()
        start.backward_char()
        ch = start.get_char()
        
        #Move to the start of the word
        while ch.isalnum() or ch == '_' or ch == ':' and not start.starts_line():
            if not start.backward_char():
                break

            ch = start.get_char()

        #Now we check that the previous word is 'new'
        start2, word = utils.get_word(start)
        if word == 'new':
            return True
        else:
            return False

    def check_is_class_const(self, context):
        start, word = utils.get_word(context.get_iter())
        
        if word:
            split = word.split('::')
            if len(split) == 2:
                return True
            else:
                return False
        else:
            return False

    def is_php_statement(self, context):
        end, word = utils.get_word(context.get_iter())
        
        if not word == 'php' or not end:
            return False

        start = end.copy()
        return start.backward_chars(2) and start.get_text(end) == '<?'

    def on_populate_context(self, completion, context):
        is_class = self.check_is_class(context)
        is_class_const = self.check_is_class_const(context)
        is_php_statement = self.is_php_statement(context)
        context.set_data(phpprovider.PHP_PROVIDER_IS_CLASS_DATA_KEY, is_class)
        context.set_data(phpprovider.PHP_PROVIDER_IS_CLASS_CONST_DATA_KEY, is_class_const)
        context.set_data(phpprovider.PHP_PROVIDER_IS_PHP_STATEMENT_DATA_KEY, is_php_statement)

class PHPCompletionPlugin(gedit.Plugin):
    WINDOW_DATA_KEY = "PHPCompletionPluginWindowData"
    
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        helper = PHPCompletionWindowHelper(self, window)
        window.set_data(self.WINDOW_DATA_KEY, helper)
    
    def deactivate(self, window):
        window.get_data(self.WINDOW_DATA_KEY).deactivate()
        window.set_data(self.WINDOW_DATA_KEY, None)
        
    def update_ui(self, window):
        window.get_data(self.WINDOW_DATA_KEY).update_ui()

# ex:ts=4:et:
