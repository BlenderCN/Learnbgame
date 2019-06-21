#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

# Release Log 
# ============
# 0.1 
# initial release
# ------------

import bpy
import time

class dotext:

    def __init__(self, tname, filepath=None):
        self.txtobj = None
        self.filepath = None
        self.ff = None

        if tname:
            print ("*** using text object to log script")
            self.txtobj = bpy.data.texts.get(tname)
            if (self.txtobj is None):
                print (tname, "*** text object not found and created!")
                self.txtobj = bpy.data.texts.new(tname)
            else:
                print (tname, "*** text object found and cleared!")
                self.txtobj.clear()

        self.tofile(filepath)

        self.tname = tname
        self.write("--== NEW RUN ==--\n")
        self.write(time.asctime())
        self.write("\n")
    # end def __init__

    def tofile(self, filepath):
        if filepath:
            self.ff = open(filepath, "w", encoding="utf8", newline="\n")
            self.filepath = filepath
    # end def tofile

    def closefile(self):
        self.ff.close()
        self.ff = None
    # end def tofile

    def write(self, wstring, maxlen=100, nl=False):
        if not(self.txtobj or self.ff): return
        while (1):
            ll = len(wstring)
            if (ll>maxlen):
                if self.txtobj:
                    self.txtobj.write((wstring[:maxlen]))
                    self.txtobj.write("\n")
                if self.ff:
                    self.ff.write((wstring[:maxlen]))
                    self.ff.write("\n")
                    self.ff.flush() #write at once, cause application can crash
                wstring = (wstring[maxlen:])
            else:
                if self.txtobj:
                    self.txtobj.write(wstring)
                    if nl:
                        self.txtobj.write("\n")
                if self.ff:
                    self.ff.write(wstring)
                    if nl:
                        self.ff.write("\n")
                    self.ff.flush() #as above
                break
    # end def write

    def writeln(self, wlnstring):
        # just backward compat
        self.write(wlnstring, nl=True)
    # end def writeln

    def pstring(self, ppstring, nl=True):
        print (ppstring)
        self.write(ppstring, nl=nl)
    # end def pstring

    def plist(self, pplist):
        self.pprint ("list:[")
        for pp in range(len(pplist)):
            self.pprint ("[", pp, "] -> ", pplist[pp])
        self.pprint ("]")
    # end def plist

    def pdict(self, pdict):
        self.pprint ("dict:{")
        for pp in pdict.keys():
            self.pprint ("[", pp, "] -> ", pdict[pp])
        self.pprint ("}")
    # end def plist

    def pprint(self, *args):
        for parg in args:
            if parg == None:
                self.pstring("_None_", False)
            elif type(parg) == type ([]):
                self.plist(parg)
            elif type(parg) == type ({}):
                self.pdict(parg)
            else:
                self.pstring(str(parg), False)
            self.write(" ")
        self.pstring("") #newline after sequence
    # end def pprint

# endclass dotext
