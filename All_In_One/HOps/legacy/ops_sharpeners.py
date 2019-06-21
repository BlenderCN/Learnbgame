import bpy
from bpy.props import BoolProperty
import bpy.utils.previews

# Clean Off Bevel and Sharps In Edit Mode


class HOPS_OT_UnsharpOperatorE(bpy.types.Operator):
    """
    Removes marking from edges.

    """
    bl_idname = "clean1.objects"
    bl_label = "UnsharpBevelE"
    bl_options = {'REGISTER', 'UNDO'}

    clearsharps: BoolProperty(default=True)
    clearbevel: BoolProperty(default=True)
    clearcrease: BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop(self, 'clearsharps', text="Clear Sharps")
        box.prop(self, 'clearbevel', text="Clear Bevels")
        box.prop(self, 'clearcrease', text="Clear Crease")

    def execute(self, context):

        if self.clearsharps is True:
            bpy.ops.mesh.mark_sharp(clear=True)
        if self.clearbevel is True:
            bpy.ops.transform.edge_bevelweight(value=-1)
        if self.clearcrease is True:
            bpy.ops.transform.edge_crease(value=-1)

        return {'FINISHED'}

# Bevel and Sharps In Edit Mode to Selection
class HOPS_OT_SharpandbevelOperatorE(bpy.types.Operator):
    """
    Mark Sharps And Bevels In Edit Mode

    """
    bl_idname = "bevelandsharp1.objects"
    bl_label = "SharpBevelE"
    bl_options = {'REGISTER', 'UNDO'}

    marksharps: BoolProperty(default=True)
    markbevel: BoolProperty(default=True)
    markcrease: BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        # DRAW YOUR PROPERTIES IN A BOX
        box.prop(self, 'marksharps', text="Mark Sharps")
        box.prop(self, 'markbevel', text="Mark Bevels")
        box.prop(self, 'markcrease', text="Mark Crease")

    def execute(self, context):
        marksharps = self.marksharps
        markbevel = self.markbevel
        markcrease = self.markcrease

        # (former)
        # bpy.ops.transform.edge_bevelweight(value=1)
        # bpy.ops.transform.edge_crease(value=1)
        # bpy.ops.mesh.mark_sharp()

        if marksharps is True:
            bpy.ops.mesh.mark_sharp()
        if markbevel is True:
            bpy.ops.transform.edge_bevelweight(value=1)
        if markcrease is True:
            bpy.ops.transform.edge_crease(value=1)

        return {'FINISHED'}
