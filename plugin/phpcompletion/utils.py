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

def get_word(piter):
    if not piter.ends_word or piter.get_char() == '_':
        return None, None

    start = piter.copy()

    while True:
        if start.starts_line():
            break
        
        start.backward_char()
        ch = start.get_char()
        
        if not (ch.isalnum() or ch == '_' or ch == ':'):
            start.forward_char()
            break

    if start.equal(piter):
        return None, None

    while (not start.equal(piter)) and start.get_char().isdigit():
        start.forward_char()

    if start.equal(piter):
        return None, None

    return start, start.get_text(piter)

# ex:ts=4:et:
