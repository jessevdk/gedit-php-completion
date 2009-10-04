# -*- coding: utf-8 -*-

#  phpdb.py - PHP completion using the completion framework
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

import sqlite3
import os
import sys

class PHPDb:
    def __init__(self, database):
        self.db = None

        if os.path.isfile(database):
            try:
                self.db = sqlite3.connect(database)
            except:
                pass

    def function_info(self, fid):
        if not self.db:
            return ''

        try:
            result = self.db.execute('SELECT `name`, `optional`, `type` FROM arguments WHERE `function` = ? ORDER BY `index`', (fid,))
        except Exception as e:
            sys.stderr.write("PHPCompletion: Error in query: %s\n" % (str(e), ))
            return ''

        ret = ''

        for arg in result:
            name = ('%s %s' % (arg[2], arg[0])).strip()
            if ret != '':
                if arg[1]:
                    ret += ' <i>[, %s]</i>' % (name,)
                    continue
                else:
                    ret += ', '

            if arg[1]:
                ret += '<i>[, %s]</i>' % (name,)
            else:
                ret += name

        return ret

    def complete_function(self, func, maxresults = -1):
        if not self.db:
            return []

        if maxresults > 0:
            extra = 'LIMIT %d' % (maxresults,)
        else:
            extra = ''

        try:
            query = "SELECT `id`, `name`, `description`, `short_description` FROM functions WHERE `class` = 0 AND `name` LIKE ? || '%%' ORDER BY `name` %s" % (extra,)
            result = self.db.execute(query, (func,))
        except Exception as e:
            sys.stderr.write("PHPCompletion: Error in query: %s\n" % (str(e), ))
            return []
        
        return list(result)

# ex:ts=4:et:
