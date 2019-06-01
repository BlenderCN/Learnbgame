import bpy
from bpy.props import IntProperty, BoolProperty
from ... utils.addons import addon_exists
from ... utils.operations import invoke_individual_resizing


class HOPS_OT_VertcircleOperator(bpy.types.Operator):
    bl_idname = "view3d.vertcircle"
    bl_label = "Vert To Circle"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Converts selected verts to circle. W/ Nth options"

    divisions: IntProperty(name="Division Count", description="Amount Of Vert divisions", default=5, min=3, max=10)

    message = "< Default >"

    nth_mode: BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "divisions")

    def execute(self, context):
        if addon_exists("mesh_looptools"):
            setup_verts(context.active_object, self.divisions, self.nth_mode)
            invoke_individual_resizing()

        return {"FINISHED"}


def setup_verts(object, divisions, nth_mode):
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    if nth_mode:
        bpy.ops.mesh.select_nth()
    bpy.ops.mesh.bevel(offset=0.2, segments=divisions, vertex_only=True)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.dissolve_mode()
    bpy.ops.mesh.looptools_circle()
