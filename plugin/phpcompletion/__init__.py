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
from phpprovider import PHPProvider
import os

class PHPCompletionWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        
        # TODO: use get_data_dir when db is nicely installed in the correct place
        self._provider = PHPProvider(os.path.join(plugin.get_install_dir(), 'phpcompletion', 'phpsymbols.db'))
        
        for view in self._window.get_views():
            self.add_view(view)

        self._window.connect('tab-added', self.on_tab_added)
        self._window.connect('tab-removed', self.on_tab_removed)

    def deactivate(self):
        # Remove the provider from all the views
        for view in self._window.get_views():
            view.remove_provider(self._provider)

        self._window = None
        self._plugin = None

    def update_ui(self):
        pass
    
    def add_view(self, view):
       view.get_completion().add_provider(self._provider)

    def remove_view(self, view):
        view.get_completion().remove_provider(self._provider)

    def on_tab_added(self, window, tab):
        # Add provider to the new view
        self.add_view(tab.get_view())
    
    def on_tab_removed(self, window, tab):
        # Remove provider from the view
        self.remove_view(tab.get_view())

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