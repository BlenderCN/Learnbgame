import bpy
import math
from ... icons import get_icon_id
from ... preferences import pro_mode_enabled
from ... utils.addons import addon_exists
from ... utils.objects import get_inactive_selected_objects
from ... preferences import use_asset_manager, get_preferences, right_handed_enabled, pro_mode_enabled, BC_unlock_enabled, mira_handler_enabled


class HOPS_MT_ObjectsOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for various mesh utilities and functions in Object Mode

    """
    bl_label = 'Objects Operators Submenu'
    bl_idname = 'HOPS_MT_ObjectsOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = layout.row(align=False)
        col = row.column(align=True)

        object = context.active_object

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.bevel_helper", text="Bevel Helper", icon_value=get_icon_id("CSharpen"))

        op = layout.operator("hops.modifier_scroll", text="Modifier Scroll", icon_value=get_icon_id("Diagonal"))
        op.additive = True
        op.all = True

        op = layout.operator("hops.bool_toggle_viewport", text= "Modifier Toggle", icon_value=get_icon_id("Tris"))
        op.all_modifiers = True

        layout.menu("HOPS_MT_ModSubmenu", text="Add Modifier", icon_value=get_icon_id("Diagonal"))

        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))

        layout.separator()

        layout.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))

        #layout.separator()

        #layout.operator("hops.adjust_bevel", text="Bevel", icon_value=get_icon_id("AdjustBevel"))

        layout.separator()

        #layout.label(text = "____2.8 Gizmos")

        layout.operator("hops.mirror_gizmo", text="Mirror", icon_value=get_icon_id("Mirror"))
        layout.operator("hops.array_gizmo", text="Array", icon_value=get_icon_id("Qarray"))

        layout.separator()

#        for mod in object.modifiers:
#            if mod.type == "BEVEL":
#                col.prop(object.modifiers['Bevel'], "segments")
#                col.separator()

        if pro_mode_enabled():
            if addon_exists("MESHmachine"):
                layout.separator()
                layout.menu("machin3.mesh_machine_menu", text="MESHmachine", icon_value=get_icon_id("Machine"))

        # layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("view3d.clean_mesh", text="Clean Mesh", icon_value=get_icon_id("FaceGrate"))

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("clean.sharps", text="Clear Sharps", icon_value=get_icon_id("CleansharpsE"))

        layout.separator()

        layout.menu("HOPS_MT_BoolScrollOperatorsSubmenu", text="Bool Scroll", icon_value=get_icon_id("Diagonal"))

        layout.separator()

        layout.operator("hops.apply_modifiers", text="Smart Apply", icon_value=get_icon_id("Applyall")).modifier_types='BOOLEAN'


class HOPS_MT_MeshOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for various mesh utilities and functions in Edit Mode

    """
    bl_label = 'Mesh Operators Submenu'
    bl_idname = 'HOPS_MT_MeshOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'
        
        layout.menu("HOPS_MT_ModSubmenu", text = 'Add Modifier',  icon_value=get_icon_id("Tris"))
        layout.separator()
        layout.operator("hops.set_edit_sharpen", text="Set SSharp", icon_value=get_icon_id("MakeSharpE"))
        layout.operator("hops.bevel_weight", text="Bweight", icon_value=get_icon_id("AdjustBevel"))
        layout.separator()
        layout.operator("clean1.objects", text="Clean SSharps", icon_value=get_icon_id("CleansharpsE"))
        layout.operator("view3d.clean_mesh", text="Clean Mesh", icon_value=get_icon_id("CleansharpsE"))
        layout.separator()

        #layout.operator_context = 'EXEC_DEFAULT'
        op = layout.operator("mesh.spin", text = 'Spin')
        op.steps = 6
        op.angle = 6.28319
        #if event.ctrl:
        #    op.axis =( 0, 1, 0)
        #else:
        #    pass

        layout.separator()

        layout.operator("view3d.vertcircle", text="Circle (E)", icon_value=get_icon_id("NthCircle"))
        layout.operator("view3d.vertcircle", text="Circle (Nth)(E)", icon_value=get_icon_id("NthCircle")).nth_mode = True
        #layout.operator("hops.circle", text="NEW Circle", icon_value=get_icon_id("NthCircle"))

        layout.separator()
        layout.operator("fgrate.op", text="Grate (Face)", icon_value=get_icon_id("FaceGrate"))
        layout.operator("fknurl.op", text="Knurl (Face)", icon_value=get_icon_id("FaceKnurl"))
        layout.separator()

        layout.operator("quick.panel", text="Panel (Face)", icon_value=get_icon_id("EdgeRingPanel"))
        layout.operator("entrench.selection", text="Panel (Edge)", icon_value=get_icon_id("FacePanel"))
        layout.operator("hops.star_connect", text="Star Connect", icon_value=get_icon_id("Machine"))
        layout.separator()

        # if any("mira_tools" in s for s in bpy.context.preferences.addons.keys()):
        #     layout.separator()
        #     layout.menu("HOPS_MT_MiraSubmenu", text="Mira (T)", icon="PLUGIN")
        # else:
        #     layout.separator()

        if addon_exists("MESHmachine"):
            layout.separator()
            layout.menu("machin3.mesh_machine_menu", text="MESHmachine", icon_value=get_icon_id("Machine"))
            layout.separator()

        if len(bpy.context.selected_objects) == 2:
            layout.operator("object.to_selection", text="Obj To Selection", icon_value=get_icon_id("dots"))
            layout.separator()

        layout.operator("hops.meshdisp", text="M_Disp", icon="PLUGIN")
        layout.menu("HOPS_MT_edgeWizardSubmenu", text="Plugin", icon="PLUGIN")
        layout.separator()
        layout.operator("hops.reset_axis", text="Reset Axis / Flatten", icon_value=get_icon_id("Xslap"))
        layout.menu("HOPS_MT_BoolSumbenu", text="Booleans", icon="MOD_BOOLEAN")
        layout.separator()

class HOPS_MT_MergeOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for merging insert meshes.

    """
    bl_label = 'Merge Operators Submenu'
    bl_idname = 'HOPS_MT_MergeOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.parent_merge", text="(C) merge")#, icon_value=get_icon_id("Merge"))
        layout.operator("hops.parent_merge_soft", text="(C) merge(soft)", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.simple_parent_merge", text="(S) merge")#, icon_value=get_icon_id("Merge"))
        layout.operator("hops.remove_merge", text="Remove Merge")#, icon_value=get_icon_id("Merge"))

class HOPS_MT_BoolScrollOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for bool scroll stuff

    """
    bl_label = 'Bool Scroll Operators Submenu'
    bl_idname = 'HOPS_MT_BoolScrollOperatorsSubmenu'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("hops.bool_scroll_objects", text="Object Scroll", icon_value=get_icon_id("StatusReset"))

        op = layout.operator("hops.modifier_scroll", text="Cycle Booleans", icon_value=get_icon_id("StatusOveride"))
        op.additive = False
        op.type = 'BOOLEAN'

        op = layout.operator("hops.modifier_scroll", text="Additive Scroll", icon_value=get_icon_id("Diagonal"))
        op.additive = True
        op.type = 'BOOLEAN'

        layout.operator("hops.bool_toggle_viewport", text= "Toggle Modifiers", icon_value=get_icon_id("Tris")).all_modifiers = False
