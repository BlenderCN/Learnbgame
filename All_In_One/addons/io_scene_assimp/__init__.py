# import_assimp.py Copyright (C) 2010, Matthias Fauconneau
#
# Import Multiple File Formats
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    'name': 'Import Assimp File Formats',
    'author': 'Matthias Fauconneau',
    'version': (0, 1),
    'blender': (2, 5, 6),
    'api': 35353,
    'location': 'File > Import > Assimp',
    'description': 'Import using Assimp (.3ds .ase .lwo .md3 .obj .ply .x ...)',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/' \
        'Scripts/',
    'category': 'Import-Export',}

"""
This script imports any files supported by Assimp to Blender.
"""

if "bpy" in locals():
    import imp
    imp.reload(import_assimp)

import bpy

def menu_import(self, context):
    self.layout.operator(import_assimp.IMPORT_OT_assimp.bl_idname, text="using Assimp (.3ds .ase .lwo .md3 .obj .ply .x ...)", icon='PLUGIN')

def register():
    from . import import_assimp
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
