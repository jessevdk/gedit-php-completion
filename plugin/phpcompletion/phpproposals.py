# -*- coding: utf-8 -*-

#  phpproposals.py - PHP completion using the completion framework
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

import gtksourceview2 as gsv
import gobject

class PHPProposal(gobject.GObject, gsv.CompletionProposal):
    def __init__(self, db, fid, name):
        gobject.GObject.__init__(self)

        self.db = db
        self.fid = fid
        self.name = name
    
    def do_get_text(self):
        return self.name
    
    def do_get_label(self):
        return self.name
    
    def do_get_info(self):
        # FIXME: gettext
        return 'No extra info available'

class PHPProposalFunction(PHPProposal):
    def __init__(self, db, fid, name, description):
        PHPProposal.__init__(self, db, fid, name)
        
        self.description = description
    
    def do_get_info(self):
        return "%s (%s)\n\n%s" % (self.name, self.db.function_info(self.fid), self.description)

class PHPProposalClass(PHPProposal):
    def __init__(self, db, fid, name, doc):
        PHPProposal.__init__(self, db, fid, name)
        
        self.doc = doc
    
    def do_get_info(self):
        return "%s (%s)\n\n%s" % (self.name, self.db.class_info(self.fid), self.doc)

gobject.type_register(PHPProposal)

# ex:ts=4:et:
