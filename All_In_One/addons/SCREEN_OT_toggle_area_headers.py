  # -*- coding: utf-8 -*-
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

# <pep8 compliant>

bl_info = {
    "name": "Toggle Screen Areas Header Display",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "location": "Bring up the Operator Search menu and type 'Toggle All Areas Header' ",
    "description": "Toggle area headers display in all the screen areas",
    "warning": "",
    "category": "Learnbgame"
}

"""Toggle Display of Screen Areas Header"""

import bpy

def main(context):
    for area in bpy.context.screen.areas:
        area.show_menus = not area.show_menus
        area.tag_redraw()
        
class SCREEN_OT_toggle_area_headers(bpy.types.Operator):
    """Toggles the Area headers for the current screen"""
    bl_idname = "screen.toggle_area_headers"
    bl_label = "Toggle Area Headers"
    bl_options = {'REGISTER'}

    def execute(self, context):
        main(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCREEN_OT_toggle_area_headers)

def unregister():
    bpy.utils.unregister_class(SCREEN_OT_toggle_area_headers)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.screen.toggle_area_headers()
