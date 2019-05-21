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
    def __init__(self, ver, un6, un7, un8, un9, const, filepath):
        """
        ver - version of tobj file
        un6 - should be 1
        un7 - should be 50528258
        un8 - should be 3 or 33685506
        un9 - should be 256 or 0
        const - should be 256 or 65792
        filepath - dds file path
        """
        self.__version = ver #1890650625 for ETS2
        self.__un2 = 0
        self.__un3 = 0
        self.__un4 = 0
        self.__un5 = 0
        self.__un6 = un6 #should be 1
        self.__un7 = un7 #should be 50528258
        self.__un8 = un8 #should be 3, shadow.tobj -> 33685506
        self.__un9 = un9 #00 10 00 00 or 00 00 00 00
        self.__const = const #00 10 00 00 or 00 01 01 00
        self.__size = len(filepath) 
        self.__un = 0 #0
        self.__dds_path = filepath
        
    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__version)
        bytes += help_funcs.UInt32ToByts(self.__un2)
        bytes += help_funcs.UInt32ToByts(self.__un3)
        bytes += help_funcs.UInt32ToByts(self.__un4)
        bytes += help_funcs.UInt32ToByts(self.__un5)
        bytes += help_funcs.UInt32ToByts(self.__un6)
        bytes += help_funcs.UInt32ToByts(self.__un7)
        bytes += help_funcs.UInt32ToByts(self.__un8)
        bytes += help_funcs.UInt32ToByts(self.__un9)
        bytes += help_funcs.UInt32ToByts(self.__const)
        bytes += help_funcs.UInt32ToByts(self.__size)
        bytes += help_funcs.UInt32ToByts(self.__un)
        for ch in self.__dds_path:
            bytes += help_funcs.CharToByts(ord(ch))
        return bytes

"""
tobj = TOBJ(1890650625, 1, 50528258, 33685507, 256, 256, "/vehicle/truck/daf_xf/color.dds")
with open("E:\\test.tobj", "wb")as f:
    f.write(tobj.to_scs_bytes())
"""