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

# <pep8-80 compliant>

import bpy
from ..layouts.mesh_brush.mesh_brush_ui import draw_mesh_brush_ui
from ..layouts.shrinkwrap.shrinkwrap_ui import draw_shrinkwrap_ui
from ..layouts.surface_constraint.surface_constraint_ui import (
    draw_surface_constraint_ui
)
from ..layouts.smooth_vertices.smooth_vertices_ui import (
    draw_smooth_vertices_ui
)

class SurfaceConstraintToolsPanel(bpy.types.Panel):
    bl_category = "Surface Constraint Tools"
    bl_idname = "VIEW3D_PT_surface_constraint_tools"
    bl_label = "Surface Constraint Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_MESH', 'OBJECT'}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        draw_mesh_brush_ui(layout)
        draw_shrinkwrap_ui(layout)
        draw_smooth_vertices_ui(layout)
        draw_surface_constraint_ui(layout)