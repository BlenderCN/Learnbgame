# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
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
    "name": "Ultimate Trim UV",
    "author": "Justen Lazzaro",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "UV/Image editor > Tool Panel, UV/Image editor UVs > menu",
    "description": "Allows automatic scaling/positioning of UVs on Ultimate Trim based texture sheets",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }


if "bpy" in locals():
    import imp
    imp.reload(ui)
    imp.reload(global_def)
    imp.reload(operator_manager)
    imp.reload(align_resize)
else:
    from . import ui
    from . import global_def
    from . import operator_manager
    from . import align_resize

# NOTE: important: must be placed here and not on top as pep8 would, or it give
# import errors...
import bpy
import os


def register():

# Registers all the classes tied to operator manager??
    class_list = operator_manager.om.classList()
    for c in class_list:
        bpy.utils.register_class(c)

    #Register parameters that allow user to set their own padding and pixel height for each trim index
    bpy.types.WindowManager.uv_padding = bpy.props.FloatProperty(name = "", default = 3.0, 
        description = "Shrinks UV islands to avoid touching trim edges. Prevents UVs from bleeding into neighboring "
        "trims when using lower res textures in realtime applications. Use the 'redo last' panel to tweak interactively"
        )
    bpy.types.WindowManager.trim_pixel_height_1 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 1st trim. Starts at top of UV space")
    bpy.types.WindowManager.trim_pixel_height_2 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 2nd trim. Starts at bottom of 1st trim")
    bpy.types.WindowManager.trim_pixel_height_3 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 3rd trim. Starts at bottom of 2nd trim")
    bpy.types.WindowManager.trim_pixel_height_4 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 4th trim. Starts at bottom of 3rd trim")
    bpy.types.WindowManager.trim_pixel_height_5 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 5th trim. Starts at bottom of 4th trim")
    bpy.types.WindowManager.trim_pixel_height_6 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 6th trim. Starts at bottom of 5th trim")
    bpy.types.WindowManager.trim_pixel_height_7 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 7th trim. Starts at bottom of 6th trim")
    bpy.types.WindowManager.trim_pixel_height_8 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 8th trim. Starts at bottom of 7th trim")
    bpy.types.WindowManager.trim_pixel_height_9 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 9th trim. Starts at bottom of 8th trim")
    bpy.types.WindowManager.trim_pixel_height_10 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 10th trim. Starts at bottom of 9th trim")
    bpy.types.WindowManager.trim_pixel_height_11 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 11th trim. Starts at bottom of 10th trim")
    bpy.types.WindowManager.trim_pixel_height_12 = bpy.props.IntProperty(name = "Pixels", default = 32,
    description = "Pixel height for 12th trim. Starts at bottom of 11th trim")


def unregister():
    # Unregisters all the classes tied to operator manager??
    class_list = operator_manager.om.classList()
    for c in class_list:
        bpy.utils.unregister_class(c)

    #Unregister parameters that allow user to set their own padding and pixel height for each trim index
    del bpy.types.WindowManager.uv_padding
    del bpy.types.WindowManager.trim_pixel_height_1
    del bpy.types.WindowManager.trim_pixel_height_2
    del bpy.types.WindowManager.trim_pixel_height_3
    del bpy.types.WindowManager.trim_pixel_height_4
    del bpy.types.WindowManager.trim_pixel_height_5
    del bpy.types.WindowManager.trim_pixel_height_6
    del bpy.types.WindowManager.trim_pixel_height_7
    del bpy.types.WindowManager.trim_pixel_height_8
    del bpy.types.WindowManager.trim_pixel_height_9
    del bpy.types.WindowManager.trim_pixel_height_10
    del bpy.types.WindowManager.trim_pixel_height_11
    del bpy.types.WindowManager.trim_pixel_height_12


if __name__ == "__main__":
    register()
