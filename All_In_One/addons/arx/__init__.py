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
    "name": "arx_toolkit",
    "author": "Milovann Yanatchkov",
    "version": (0,1),
    "blender": (2, 6, 4),
    "location": "in various locations ...",
    "description": "architecture render helpfull plugins",
    "wiki_url": "none",
    "tracker_url": "none",
    "category": "Learnbgame",
}

if "bpy" in locals():
	import imp
	imp.reload(arx_util)
	imp.reload(arx_index)
	imp.reload(arx_cad)
	imp.reload(arx_contour)
	imp.reload(arx_texture)
	imp.reload(arx_image)
	imp.reload(arx_material)
	imp.reload(arx_object)
else:
	from . import arx_util
	from . import arx_index
	from . import arx_cad
	from . import arx_contour
	from . import arx_texture
	from . import arx_image
	from . import arx_material
	from . import arx_object

import bpy
from . arx_image import import_human
from . arx_image import import_vegetal
from . arx_image import import_image
from . arx_cad import EdgeIntersections
from . arx_cad import menu_func


def unregister():
	bpy.utils.unregister_module(__name__)

	bpy.types.INFO_MT_mesh_add.remove(import_human)
	bpy.types.INFO_MT_mesh_add.remove(import_vegetal)
	bpy.types.INFO_MT_mesh_add.remove(import_image)

	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

def register():
	bpy.utils.register_module(__name__)

	bpy.types.INFO_MT_file_import.append(import_human)
	bpy.types.INFO_MT_file_import.append(import_vegetal)
	bpy.types.INFO_MT_file_import.append(import_image)
	bpy.types.INFO_MT_mesh_add.append(import_human)
	bpy.types.INFO_MT_mesh_add.append(import_vegetal)
	bpy.types.INFO_MT_mesh_add.append(import_image)

	bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)


if __name__ == "__main__":
	register()
