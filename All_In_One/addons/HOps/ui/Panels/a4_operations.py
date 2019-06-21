import bpy
from bpy.props import *
from ... icons import get_icon_id


class HOPS_PT_OperationsPanel(bpy.types.Panel):
    bl_label = "Operations"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        active_object = context.active_object

        if active_object is None:
            layout.label(text="Select object first")
        elif active_object.mode == "OBJECT":

            layout = self.layout

            col = layout.column(align=True)

            col.separator()

            colrow = col.row(align=True)
            colrow.operator_context = 'INVOKE_DEFAULT'

            colrow.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))
            colrow.operator("hops.soft_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))

            colrow = col.row(align=True)
            colrow.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))

            colrow = col.row(align=True)
            colrow.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("Csplit"))

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("hops.cut_in", text="Cut-in")

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("hops.adjust_array", text="(Q) Array", icon_value=get_icon_id("Qarray"))
            colrow.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("clean.sharps", text="Clear S/C/Sharps", icon_value=get_icon_id("CleansharpsE"))
            colrow.operator("view3d.clean_mesh", text="Clean Mesh (E)", icon_value=get_icon_id("CleansharpsE"))

            colrow = col.row(align=True)
            colrow.operator("hops.2d_bevel", text="Bevel (2d)", icon_value=get_icon_id("AdjustBevel"))

            col.separator()
            colrow = col.row(align=True)
            colrow.operator("hops.parent_merge", text="(C) merge", icon_value=get_icon_id("Merge"))
            colrow.operator("hops.parent_merge_soft", text="(C) merge(soft)", icon_value=get_icon_id("CSharpen"))
            colrow = col.row(align=True)
            colrow.operator("hops.simple_parent_merge", text="(S) merge", icon_value=get_icon_id("Merge"))
            colrow.operator("hops.remove_merge", text="Remove Merge", icon_value=get_icon_id("Merge"))

            col.separator()
            colrow = col.row(align=True)
            colrow.operator("material.simplify", text="Material Link", icon_value=get_icon_id("Noicon"))

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("view3d.bevel_multiplier", text="Bevel Multiplier", icon_value=get_icon_id("Noicon"))

            col.separator()

            colrow = col.row(align=True)
            colrow.operator("hops.sharp_manager", text="Sharps Manager", icon_value=get_icon_id("Noicon"))

        elif active_object.mode == "EDIT":

            layout = self.layout
            col = layout.column(align=True)

            col.separator()

            colrow = col.row(align=True)
            colrow.operator_context = 'INVOKE_DEFAULT'
            colrow.operator("hops.set_edit_sharpen", text="Set SSharp", icon_value=get_icon_id("MakeSharpE"))
            colrow = col.row(align=True)
            colrow.operator("hops.bevel_weight", text="Bweight", icon_value=get_icon_id("AdjustBevel"))
            col.separator()
            colrow = col.row(align=True)
            colrow.operator("clean1.objects", text="Clean SSharps", icon_value=get_icon_id("CleansharpsE")).clearsharps = False
            col.separator()

            colrow = col.row(align=True)
            colrow.menu("HOPS_MT_edgeWizardSubmenu", text="AUX", icon="PLUGIN")
            colrow.operator("hops.meshdisp", text="M_Disp", icon="PLUGIN")

            col.separator()

            colrow.operator_context = 'INVOKE_DEFAULT'
            colrow = col.row(align=True)
            colrow.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))
            colrow = col.row(align=True)
            colrow.operator("view3d.vertcircle", text="Circle (E)", icon_value=get_icon_id("NthCircle"))
            colrow = col.row(align=True)
            colrow.operator("view3d.vertcircle", text="Circle (Nth)(E)", icon_value=get_icon_id("NthCircle")).nth_mode = True
            colrow = col.row(align=True)
            colrow.operator("hops.circle", text="NEW Circle", icon_value=get_icon_id("NthCircle"))

            col.separator()
            colrow = col.row(align=True)
            colrow.operator("fgrate.op", text="Grate (Face)", icon_value=get_icon_id("FaceGrate"))
            colrow = col.row(align=True)
            colrow.operator("fknurl.op", text="Knurl (Face)", icon_value=get_icon_id("FaceKnurl"))

            col.separator()
            colrow = col.row(align=True)
            colrow.operator("quick.panel", text="Panel (Face)", icon_value=get_icon_id("EdgeRingPanel"))
            colrow = col.row(align=True)
            colrow.operator("entrench.selection", text="Panel (Edge)", icon_value=get_icon_id("FacePanel"))
            colrow = col.row(align=True)
            colrow.operator("hops.star_connect", text="Star Connect")

            if any("mira_tools" in s for s in bpy.context.preferences.addons.keys()):
                col.separator()
                colrow = col.row(align=True)
                colrow.menu("HOPS_MT_MiraSubmenu", text="Mira (T)", icon="PLUGIN")
            else:
                col.separator()
            colrow = col.row(align=True)
            colrow.menu("HOPS_MT_SymmetrySubmenu", text="Symmetrize", icon_value=get_icon_id("Xslap"))
