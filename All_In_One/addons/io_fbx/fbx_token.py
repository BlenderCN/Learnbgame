# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import sys
import shlex

from .fbx_basic import *


#------------------------------------------------------------------
#   ParseNode
#------------------------------------------------------------------

class ParseNode:

    def __init__(self, key, parent):
        self.key = key.rstrip(':')
        self.values = []        
        self.parent = parent
        if parent:
            parent.values.append(self)
            self.level = self.parent.level+1
        else:
            self.level = 0
            
    def __repr__(self):
        return ("<ParseNode %s %d>" % (self.key, self.level))

    def write(self, fp=sys.stdout):
        fp.write('\n%s("%s" ' % (("  "*self.level), self.key))
        for val in self.values:
            if isinstance(val, ParseNode):
                val.write(fp)
            else:
                fp.write("%s " % val)
        fp.write('\n%s)' % (("  "*self.level)))
        
        
        
#------------------------------------------------------------------
#   Lexer
#------------------------------------------------------------------

class FbxLex(shlex.shlex):

    def __init__(self, stream):
        shlex.shlex.__init__(self, stream)
        self.commenters = ';'
        self.wordchars += ':+-.'
        self.quotes = '"'
        
#------------------------------------------------------------------
#   Tokenizing
#------------------------------------------------------------------

def tokenizeFbxFile(filepath):
    proot = pnode = ParseNode("RootNode:", None)
    fp = open(filepath, "rU")
    
    prevline = ""
    for line in fp:
        line = line.strip()
        if len(line) > 0:
            if line[0] == ';':
                pass
            elif line[-1] == ',':
                prevline += line
            else:
                pnode = tokenizeLine(prevline+line, pnode)
                prevline = ""
    fp.close()    
    return proot
        
        
def tokenizeLine(line, pnode):

    tokens = list(FbxLex(line))
    if len(tokens) > 0:
        key = tokens[0]
        if key == '}':
            return pnode.parent
        elif key[-1] == ':':
            node1 = ParseNode(key, pnode)
            for token in tokens[1:]:
                if token == '{':
                    return node1
                elif token in ['Y','N']:
                    node1.values.append(token)
                elif token[0] == '"':
                    node1.values.append(token[1:-1])
                elif token not in [',','*']:
                    node1.values.append(eval(token))

    return pnode                        
            

def tokenizePropertyString(string):

    proot = pnode = ParseNode("RootNode:", None)
    lines = string.split('\n')
    
    for line in lines:
        pnode = tokenizeLine(line, pnode)
        
    #proot.write()
    values = []
    for pnode in proot.values[0].values[1].values:
        if pnode.key == "P":
            values.append(pnode.values)
        else:
            pnode.write()
            halt

    return values
    
    