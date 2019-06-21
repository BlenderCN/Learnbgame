# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


from bpy.types import Panel


class VIEW3D_PT_messythings(Panel):
    bl_label = "Messy Things"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        flow = layout.grid_flow()

        col = flow.column()
        col.label(text="Tweak")
        col.operator("scene.messythings_normalize", text="Object Display", icon="SHADING_WIRE")
        col.operator("scene.messythings_profile_render", text="Render Profile", icon="OUTPUT")

        col = flow.column()
        col.label(text="Sort")
        col.operator("scene.messythings_sort", text="Collections", icon="OUTLINER")
        col.operator("scene.messythings_deps_select", text="Dependencies", icon="LINKED")

        col = flow.column()
        col.label(text="Cleanup")
        col.operator("scene.messythings_cleanup", text="Scene", icon="SCENE_DATA")
