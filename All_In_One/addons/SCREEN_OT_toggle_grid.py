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
    "name": "Toggle Grid Display",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "location": "Bring up the Operator Search menu and type 'Toggle Grid' ",
    "description": "Toggle Grid Display in all the viewports",
    "warning": "",
    "category": "Learnbgame",
}

"""Toggle Grid Display"""

import bpy

def main(context):
    screen = context.screen
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            active_space = area.spaces[0]
            attrs = ['show_floor', 'show_axis_x', 'show_axis_y', 'show_axis_z']
            for attr, toggle in map(lambda attr: (attr, getattr(active_space, attr)), attrs):
                setattr(active_space, attr, not toggle)
    
class SCREEN_OT_toggle_grid(bpy.types.Operator):
    """Toggles the Grid display in all 3D Views for the current screen"""
    bl_idname = "screen.toggle_grid"
    bl_label = "Toggle Grid Display"
    bl_options = {'REGISTER'}

    def execute(self, context):
        main(context)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SCREEN_OT_toggle_grid)

def unregister():
    bpy.utils.unregister_class(SCREEN_OT_toggle_grid)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.screen.toggle_grid()
