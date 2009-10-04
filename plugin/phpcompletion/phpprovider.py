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
from phpproposals import PHPProposalFunction

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
    
    def get_proposals(self, word):
        # Just get functions for now
        proposals = []
        
        for func in self.db.complete_function(word):
            if func[3]:
                doc = func[3]
            else:
                doc = func[2]

            proposals.append(PHPProposalFunction(self.db, func[0], func[1], doc))
        
        return proposals
    
    def do_get_start_iter(self, context, proposal):
        buf = context.get_iter().get_buffer()
        mark = buf.get_mark(self.MARK_NAME)

        if not mark:
            return None
        
        return buf.get_iter_at_mark(mark)
    
    def get_word(self, context):
        piter = context.get_iter()
        
        if not piter.ends_word or piter.get_char() == '_':
            return None, None
        
        start = piter.copy()
        
        while True:
            if start.starts_line():
                break
            
            start.backward_char()
            ch = start.get_char()
            
            if not (ch.isalnum() or ch == '_' or ch == ':'):
                break
        
        if start.equal(piter):
            return None, None
        
        while (not start.equal(piter)) and start.get_char().isdigit():
            start.forward_char()

        if start.equal(piter):
            return None, None

        return start, start.get_text(piter)
    
    def do_match(self, context):
        lang = context.get_iter().get_buffer().get_language()
        
        if not lang:
            return False
            
        if lang.get_id() != 'php' and lang.get_id() != 'html':
            return False

        start, word = self.get_word(context)
        return word and len(word) > 2

    def do_populate(self, context):
        start, word = self.get_word(context)
        
        if not word:
            context.add_proposals(self, [], True)
            return
        
        proposals = self.get_proposals(word)
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
