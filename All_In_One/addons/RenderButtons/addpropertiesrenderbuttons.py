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
    "name": "Blender 2.80beta PorpertiesRenderButtons",
    "author": "Olaf Haag",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Output > Dimensions",
    "description": "Adds Render Buttons to Output tab in Properties.",
    "warning": "Blender 2.8 is still in development, so usability of this addon might change.",
    "wiki_url": "https://github.com/OlafHaag/Blender2_80beta_RenderButtons/blob/master/README.md",
    "tracker_url": "https://github.com/OlafHaag/Blender2_80beta_RenderButtons/issues",
    "category": "Learnbgame",
    }

import bpy
from bpy.types import Panel

class AddRenderButtons(Panel):
    """Creates a Panel with Render buttons in the Properties Output Panel"""
    bl_label = "Render"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_parent_id = "RENDER_PT_dimensions"
    bl_options = {'HIDE_HEADER'}
    #bl_idname = "OBJECT_PT_Add_RenderButtons"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("render.render", text="Render", icon='RENDER_STILL')
        row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True

def register():
    bpy.utils.register_class(AddRenderButtons)

def unregister():
    bpy.utils.unregister_class(AddRenderButtons)

if __name__ == "__main__":
    register()
