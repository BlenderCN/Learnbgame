import bpy

from bpy.props import FloatProperty


class HOPS_OT_SculptDecimate(bpy.types.Operator):
    bl_idname = "sculpt.decimate_mesh"
    bl_label = "Decimate Sculpt"
    bl_description = "Decimates mesh for continued sculpting"
    bl_options = {"REGISTER", "UNDO"}

    ratio: FloatProperty(name="Ratio", description="Amount Of Decimation", default=0.3, min=0.01, max=1.0)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "ratio")

    def invoke(self, context, event):
        self.execute(context)
        return {"FINISHED"}

    def execute(self, context):
        if bpy.context.active_object.mode == 'SCULPT':
            exit_sculpt()
        add_decimate(self.ratio)
        bpy.ops.object.mode_set(mode='SCULPT')

        return {"FINISHED"}


def exit_sculpt():
    bpy.ops.sculpt.sculptmode_toggle()


def add_decimate(ratio):
    bpy.ops.object.modifier_add(type='DECIMATE')
    bpy.context.object.modifiers["Decimate"].ratio = ratio
    bpy.context.object.modifiers["Decimate"].use_symmetry = True
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
