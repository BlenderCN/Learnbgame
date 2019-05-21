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
    "name": "Ogre XML mesh format (.mesh.xml)",
    "description": "Import-Export Ogre XML",
    "author": "Jesse van Herk",
    "version": (0, 1),
    "blender": (2, 5, 7),
    "api": 36103,
    "location": "File > Import-Export > Ogre XML (.mesh.xml) ",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Import-Export/Ogre_Mesh_XML_IO",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    #imp.reload(import_ogre_xml)
    imp.reload(export_ogre_xml)
else:
    #from . import import_ogre_xml
    from . import export_ogre_xml


import bpy

def menu_import(self, context):
    self.layout.operator(import_ogre_xml.OgreImporter.bl_idname, text="Ogre XML (.mesh.xml)").filepath = "*.mesh.xml"


def menu_export(self, context):
    import os
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mesh.xml"
    self.layout.operator(export_ogre_xml.OgreExporter.bl_idname, text="Ogre XML (.mesh.xml)").filepath = default_path


def register():
    bpy.utils.register_module(__name__)

    #bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)

def unregister():
    bpy.utils.unregister_module(__name__)

    #bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)

# this allows the module to work when being called directly (not via blender)
if __name__ == "__main__":
    register()
