##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

from . import help_funcs


class TOBJ:
    def __init__(self, filepath):
        with open(filepath, "rb") as f:
            self.version = help_funcs.ReadUInt32(f)
            self.un2 = help_funcs.ReadUInt32(f)
            self.un3 = help_funcs.ReadUInt32(f)
            self.un4 = help_funcs.ReadUInt32(f)
            self.un5 = help_funcs.ReadUInt32(f)
            self.un6 = help_funcs.ReadUInt32(f) #should be 1
            self.un7 = help_funcs.ReadUInt32(f) #should be 50528258
            self.un8 = help_funcs.ReadUInt32(f) #should be 3, shadow.tobj -> 33685506
            self.un9 = help_funcs.ReadUInt32(f) #00 00 01 00 or 00 00 00 00
            self.const = help_funcs.ReadUInt32(f) #00 00 01 00 or 00 01 01 00
            self.size = help_funcs.ReadUInt32(f)
            self.un = help_funcs.ReadUInt32(f)
            ch = help_funcs.ReadChar(f)
            self.tex_path = ""
            i=0
            while i < self.size:
                self.tex_path += chr(ch)
                ch = help_funcs.ReadChar(f)
                i+=1
            self.tobj_name = filepath[filepath.rfind("/")+1:filepath.rfind(".")]
            self.tex_name = self.tex_path[self.tex_path.rfind("/")+1:self.tex_path.rfind(".")]