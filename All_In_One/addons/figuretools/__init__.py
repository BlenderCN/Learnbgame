# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.6 FigureTools Addon
# --------------------------------------------------------------------------
#
# Authors:
# Tony Edwards
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import bpy

from . import dson
from . import prefs
from . utils import ftlog

bl_info = {
    "name": "FigureTools",
    "author": "Tony Edwards (tnydwrds)",
    "version": (0, 0, 1),
    "blender": (2, 69, 0),
    "category": "Import-Export",
    "location": "File > Import-Export"
}

def add_to_import_menu(self, context):
    self.layout.operator(dson.DSONImporter.bl_idname, text='DAZ DSON (.duf/.dsf)')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(add_to_import_menu)
    ftlog('Addon registered')

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(add_to_import_menu)
    ftlog('Addon unregistered')
