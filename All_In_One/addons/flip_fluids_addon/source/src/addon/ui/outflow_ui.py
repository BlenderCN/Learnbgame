# Blender FLIP Fluid Add-on
# Copyright (C) 2019 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy

from ..utils import version_compatibility_utils as vcu


class FlipFluidOutflowTypePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_category = "FLIP Fluid"
    bl_label = "FLIP Fluid"

    @classmethod
    def poll(cls, context):
        obj_props = vcu.get_active_object(context).flip_fluid
        return obj_props.is_active and obj_props.object_type == "TYPE_OUTFLOW"

    def draw(self, context):
        obj = vcu.get_active_object(context)
        obj_props = obj.flip_fluid
        outflow_props = obj_props.outflow

        column = self.layout.column()
        column.prop(obj_props, "object_type")

        column = self.layout.column()
        column.prop(outflow_props, "is_enabled")

        column = self.layout.column()
        split = column.split()
        column = split.column()
        column.prop(outflow_props, "remove_fluid")
        column = split.column()
        column.prop(outflow_props, "remove_whitewater")

        self.layout.separator()
        column = self.layout.column()
        column.prop(outflow_props, "is_inversed")
        column.prop(outflow_props, "export_animated_mesh")
    

def register():
    bpy.utils.register_class(FlipFluidOutflowTypePanel)


def unregister():
    bpy.utils.unregister_class(FlipFluidOutflowTypePanel)
