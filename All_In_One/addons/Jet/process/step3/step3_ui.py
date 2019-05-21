import bpy
from ... common_utils import apply_to_selected, get_hotkey
from . step3_utils import EnableAndConfigAutosmooth, ManageSharp

#Panel
class VIEW3D_PT_jet_step3(bpy.types.Panel):
    bl_label = "3. Smooth/Sharp"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "smoothing_sharpening", text="", icon="INFO")

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator("jet_flat_smooth.btn", text="Flat").smooth=False
        row.operator("jet_flat_smooth.btn", text="Smooth").smooth=True

        col = layout.column(align=True)

        col.operator("jet_autosmooth.btn", text="Autosmooth 180º").angle = 180

        row = col.row(align=True)
        row.prop(context.scene.Jet, "autosmooth", text="Autosmooth angle")
        row.operator("jet_autosmooth.btn", text="", icon="RIGHTARROW").angle = context.scene.Jet.autosmooth

        text = "Disable" if context.scene.Jet.tag.sharp else "Enable"
        col.prop(context.scene.Jet.tag, "sharp",
                 text=text + " Sharp Tagging - " + get_hotkey(context, "mesh.shortest_path_pick"),
                 icon="BLANK1")

        row = col.row(align=True)
        row.operator("jet_sharp.btn", text="Mark Sharp").mark = True
        row.operator("jet_sharp.btn", text="Clear Sharp").mark = False


#Operators
class VIEW3D_OT_jet_autosmooth(bpy.types.Operator):
    bl_idname = "jet_autosmooth.btn"
    bl_label = "Autosmooth"
    bl_description = "Enable Autosmooth and apply the smooth angle to all selected objects"

    angle = bpy.props.IntProperty(default=180)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        apply_to_selected(context, EnableAndConfigAutosmooth, value=self.angle*0.0174533)
        return {'FINISHED'}


class VIEW3D_OT_jet_sharp(bpy.types.Operator):
    bl_idname = "jet_sharp.btn"
    bl_label = "Sharp"
    bl_description = "Manage Sharp"

    mark = bpy.props.BoolProperty(default=True)

    def execute(self, context):
        ManageSharp(context, self.mark)
        return {'FINISHED'}