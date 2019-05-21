# ##### BEGIN GPL LICENSE BLOCK #####
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

if "bpy" in locals():
    import imp
    imp.reload(gdal_module)
    imp.reload(ui_module)
    imp.reload(blender_module)
    imp.reload(flyover_module)
else:
    from . import blender_module
    from . import flyover_module
    from . import ui_module
    from . import gdal_module

import bpy

bl_info = {
    "name": "Import and SpaceBlend DEM (.IMG)",
    "author": "Andrew Carter, Eric Ghazal, Jason Hedlund, Terence Luther",
    "version": (1, 0, 0),
    "blender": (2, 65, 0),
    "warning": "Requires GDAL and System Python 2.7+ to be installed.",
    "location": "File > Import > Import and SpaceBlend DEM (.IMG)",
    "description": "Import DEM, apply texture, and create flyover.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

############################## REGISTRATION #################################
def menu_import(self, context):
    self.layout.operator(ui_module.UI_Driver.bl_idname, text="Import and SpaceBlend DEM(.IMG)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)

## How to register the script inside of Blender
if __name__ == "__main__":
    register()