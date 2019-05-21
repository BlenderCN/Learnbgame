# This file is part of Hypermesh.
#
# Hypermesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hypermesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hypermesh.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
from .hyperpreset import ensure_scene_is_hyper
from .hypermeshpreferences import debug_message


class MakeHyperOperator(bpy.types.Operator):
    bl_idname = "hyper.makehyper"
    bl_label = "Make hyper"
    bl_options = {'REGISTER', 'UNDO'}

    selected_preset = bpy.props.IntProperty(
        name="Projection",
        description="Which projection to use when interpreting the 3-mesh as a 4-mesh")

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        if context.active_object.type != 'MESH':
            return False
        # TODO: check whether object is hyper?
        return context.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        layout.row()
        layout.template_list("preset_list", "notsurewhattoputhere", context.scene,
                             "hyperpresets", self, "selected_preset")

    def execute(self, context):
        debug_message("Making hyper")

        ensure_scene_is_hyper(context.scene)
        debug_message("Ensured scene is hyper")
        me = context.active_object.data

        if me.hypersettings.hyper:
            self.report({'ERROR_INVALID_INPUT'}, "Mesh is already hyper")
            return {'FINISHED'}

        me.hypersettings.hyper = True
        me["hypermesh-dirty"] = True
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.layers.float.new('hyperw')
        bm.verts.layers.float.new('hyperx')
        bm.verts.layers.float.new('hypery')
        bm.verts.layers.float.new('hyperz')
        bm.to_mesh(me)
        me["hypermesh-justcleaned"] = False
        me.hypersettings.set_preset_without_reprojecting(self.selected_preset)
        return {'FINISHED'}
