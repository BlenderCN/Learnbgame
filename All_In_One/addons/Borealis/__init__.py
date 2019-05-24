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


bl_info = {
    'name': 'Neverwinter Mdl importer/exporter',
    'author': 'Erik Ylipää',
    'version': '0.1',
    'blender': (2, 5, 8),
    'location': 'File > Import-Export > Neverwinter',
    'description': 'Import and Export Bioware Neverwinter Nights Models files (.mdl)',
    'warning': '',  # used for warning icon and text in addons panel
    'wiki_url': '',
    'tracker_url': '',
    "category": "Learnbgame",
}


import bpy
from bpy.props import StringProperty, CollectionProperty

import os
from . import blend_props
from . import gui
from . import operators
from . import mdl_import
from . import mdl_export


def register():
    bpy.utils.register_module(__name__)
    blend_props.register()

    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)


def menu_import(self, context):
    self.layout.operator(BorealisImport.bl_idname, text="Nwn Mdl(.mdl)").filepath = "*.mdl"


def menu_export(self, context):
    import os
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mdl"
    self.layout.operator(mdl_export.BorealisExport.bl_idname, text="Nwn Mdl(.mdl)").filepath = default_path


if __name__ == "__main__":
    register()
