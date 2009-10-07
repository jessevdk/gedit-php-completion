# -*- coding: utf-8 -*-

#  phpprovider.py - PHP completion using the completion framework
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
from phpdb import PHPDb
import gobject
from phpproposals import PHPProposal, PHPProposalFunction, PHPProposalClass
import utils

PHP_PROVIDER_IS_CLASS_DATA_KEY = 'PHPProviderIsClassData'
PHP_PROVIDER_IS_CLASS_CONST_DATA_KEY = 'PHPProviderIsClassConstantData'
PHP_PROVIDER_IS_PHP_STATEMENT_DATA_KEY = 'PHPProviderIsPHPStatementData'

class PHPProvider(gobject.GObject, gsv.CompletionProvider):
    MARK_NAME = 'PHPProviderCompletionMark'

    def __init__(self, database):
        gobject.GObject.__init__(self)

        self.mark = None
        self.db = PHPDb(database)
    
    def move_mark(self, buf, start):
        # TODO: see do_get_mark_iter
        mark = buf.get_mark(self.MARK_NAME)
        
        if not mark:
            buf.create_mark(self.MARK_NAME, start, True)
        else:
            buf.move_mark(mark, start)
    
    def get_proposals(self, is_class, is_class_const, is_php_statement, word):
        # Just get functions and classes for now
        proposals = []
        
        if is_class_const:
            const = word.split('::')
            for class_const in self.db.complete_class_const(const[0], const[1]):
                proposals.append(PHPProposal(self.db, class_const[0], class_const[1]))
        elif is_class:
            for class_name in self.db.complete_class(word):
                proposals.append(PHPProposalClass(self.db, class_name[0], class_name[1], class_name[2]))
        elif not is_php_statement:
            for func in self.db.complete_function(word):
                if len(func) > 2:
                    if func[3]:
                        doc = func[3]
                    else:
                        doc = func[2]
                else:
                    doc = ''

                proposals.append(PHPProposalFunction(self.db, func[0], func[1], doc))
            
            for const in self.db.complete_const(word):
                proposals.append(PHPProposal(self.db, const[0], const[1]))
        
        return proposals
    
    def do_get_start_iter(self, context, proposal):
        buf = context.get_iter().get_buffer()
        mark = buf.get_mark(self.MARK_NAME)

        if not mark:
            return None
        
        return buf.get_iter_at_mark(mark)
    
    def do_match(self, context):
        lang = context.get_iter().get_buffer().get_language()
        
        if not lang:
            return False
            
        if lang.get_id() != 'php' and lang.get_id() != 'html':
            return False

        start, word = utils.get_word(context.get_iter())
        is_class = context.get_data(PHP_PROVIDER_IS_CLASS_DATA_KEY)
        return is_class or (word and len(word) > 2)

    def do_populate(self, context):
        is_class = context.get_data(PHP_PROVIDER_IS_CLASS_DATA_KEY)
        is_class_const = context.get_data(PHP_PROVIDER_IS_CLASS_CONST_DATA_KEY)
        is_php_statement = context.get_data(PHP_PROVIDER_IS_PHP_STATEMENT_DATA_KEY)
        
        start, word = utils.get_word(context.get_iter())
        if not is_class:
            if not word:
                context.add_proposals(self, [], True)
                return
            elif is_class_const:
                # FIXME: This should be implemented in activation
                start = context.get_iter()
        else:
            if not word:
                start = context.get_iter()
        
        proposals = self.get_proposals(is_class, is_class_const, is_php_statement, word)
        self.move_mark(context.get_iter().get_buffer(), start)
        
        context.add_proposals(self, proposals, True)
    
    def do_get_name(self):
        return _('PHP')
    
    def do_get_activation(self):
        return gsv.COMPLETION_ACTIVATION_INTERACTIVE | gsv.COMPLETION_ACTIVATION_USER_REQUESTED
    
    def do_activate_proposal(self, proposal, piter):
        # TODO: implement
        return False

gobject.type_register(PHPProvider)

# ex:ts=4:et:
