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

# Module: options.py
# Description: user options from import/export menu.

class ImportOptions:

    def __init__(self, mdcFilepath, gamePath, toNewScene, normals, normalsLayer):

        # general
        self.mdcFilepath = mdcFilepath
        self.gamePath = gamePath
        self.toNewScene = toNewScene

        # vertex normals
        self.normals = normals
        self.normalsLayer = normalsLayer


class ExportOptions:

    def __init__(self, mdcFilepath, selection, normalObjects):

        # general
        self.mdcFilepath = mdcFilepath
        self.selection = selection

        # vertex normals
        self.normalObjects = normalObjects
