import bpy
from bpy.props import BoolProperty
import bmesh
from .. utils import MACHIN3 as m3


class MarkLoop(bpy.types.Operator):
    bl_idname = "machin3.mark_loop"
    bl_label = "MACHIN3: Mark Loop"
    bl_options = {'REGISTER', 'UNDO'}

    clear = BoolProperty(name="Clear", default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "clear")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)

        return len([e for e in bm.edges if e.select]) > 0

    def execute(self, context):
        bpy.ops.mesh.mark_freestyle_edge(clear=self.clear)

        return {'FINISHED'}
