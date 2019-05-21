import bpy
from ... icons import get_icon_id
from ... preferences import pro_mode_enabled
from ... utils.addons import addon_exists
from ... utils.objects import get_inactive_selected_objects
from ... preferences import use_asset_manager, get_preferences, right_handed_enabled, pro_mode_enabled, BC_unlock_enabled, mira_handler_enabled
 
 
class HOPS_MT_MeshOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for various mesh utilities and functions in Edit Mode
 
    """
    bl_label = 'Mesh Operators Submenu'
    bl_idname = 'hops.mesh_operators_submenu'
 
    def draw(self, context):
        layout = self.layout
 
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.set_edit_sharpen", text="Set SSharp", icon_value=get_icon_id("MakeSharpE"))
        layout.operator("hops.bevel_weight", text="Bweight", icon_value=get_icon_id("AdjustBevel"))
        layout.separator()
        layout.operator("clean1.objects", text="Clean SSharps", icon_value=get_icon_id("CleansharpsE"))
        layout.operator("view3d.clean_mesh", text="Clean Mesh", icon_value=get_icon_id("CleansharpsE"))
        layout.separator()

        if pro_mode_enabled():
            layout.menu("hops.edge_wizzard_submenu", text="AUX", icon="PLUGIN")

        layout.operator("hops.meshdisp", text="M_Disp", icon="PLUGIN")

        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        
        layout.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

        layout.operator("view3d.vertcircle", text="Circle (E)", icon_value=get_icon_id("NthCircle"))

        layout.operator("view3d.vertcircle", text="Circle (Nth)(E)", icon_value=get_icon_id("NthCircle")).nth_mode = True

        layout.operator("hops.circle", text="NEW Circle", icon_value=get_icon_id("NthCircle"))

        layout.separator()

        layout.operator("fgrate.op", text="Grate (Face)", icon_value=get_icon_id("FaceGrate"))

        layout.operator("fknurl.op", text="Knurl (Face)", icon_value=get_icon_id("FaceKnurl"))

        layout.separator()

        layout.operator("quick.panel", text="Panel (Face)", icon_value=get_icon_id("EdgeRingPanel"))

        layout.operator("entrench.selection", text="Panel (Edge)", icon_value=get_icon_id("FacePanel"))

        layout.operator("hops.star_connect", text="Star Connect", icon_value=get_icon_id("Machine"))

        if any("mira_tools" in s for s in bpy.context.preferences.addons.keys()):
            layout.separator()
            layout.menu("hops.mira_submenu", text="Mira (T)", icon="PLUGIN")
        else:
            layout.separator()
 
        if addon_exists("MESHmachine"):
            layout.separator()
            layout.menu("machin3.mesh_machine_menu", text="MESHmachine", icon_value=get_icon_id("Machine"))
        
        layout.separator()
        
        layout.menu("hops.bool_menu", text="Booleans", icon="MOD_BOOLEAN")
        
        layout.separator()
        
        #layout.operator("hops.shrinkwrap_refresh", text="Shrinkwrap Refresh")


class HOPS_MT_ObjectsOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for various mesh utilities and functions in Object Mode

    """
    bl_label = 'Objects Operators Submenu'
    bl_idname = 'hops.object_operators_submenu'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = layout.row(align=False)
        col = row.column(align=True)

        object = context.active_object

        # layout.operator_context = 'INVOKE_DEFAULT'
        # layout.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))
        # layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.adjust_bevel", text="(B) Width", icon_value=get_icon_id("AdjustBevel"))

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.2d_bevel", text="Bevel (2d)", icon_value=get_icon_id("AdjustBevel"))

        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.soft_sharpen", text="(S) Sharpen", icon_value=get_icon_id("Ssharpen"))

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.complex_sharpen", text="(C) Sharpen", icon_value=get_icon_id("CSharpen"))

        layout.separator()

        layout.operator("hops.step", text="Step", icon_value=get_icon_id("Sstep"))

        layout.separator()

        layout.operator("hops.slash", text="(C) Slash", icon_value=get_icon_id("Csplit"))
        layout.operator("hops.cut_in", text="Cut-in", icon_value=get_icon_id("Cutin"))

        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.adjust_array", text="(Q) Array", icon_value=get_icon_id("Qarray"))

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("hops.adjust_tthick", text="(T) Thick", icon_value=get_icon_id("Tthick"))

        layout.separator()

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("clean.sharps", text="Clear S/C/Sharps", icon_value=get_icon_id("CleansharpsE"))

        # layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("view3d.clean_mesh", text="Clean Mesh (E)", icon_value=get_icon_id("CleansharpsE"))

        layout.separator()

        for mod in object.modifiers:
            if mod.type == "BEVEL":
                col.prop(object.modifiers['Bevel'], "segments")
                col.separator()

        layout.operator("material.simplify", text="Material Link", icon_value=get_icon_id("Noicon"))

        if pro_mode_enabled():
            if addon_exists("MESHmachine"):
                layout.separator()
                layout.menu("machin3.mesh_machine_menu", text="MESHmachine", icon_value=get_icon_id("Machine"))

        layout.separator()

        layout.operator("view3d.bevel_multiplier", text="Bevel Multiplier", icon_value=get_icon_id("BevelMultiply"))
        layout.operator("hops.sharp_manager", text="Sharps Manager", icon_value=get_icon_id("Diagonal"))

        layout.separator()

        layout.menu("hops.bool_scroll_operators_submenu", text="Bool Scroll")




class HOPS_MT_MergeOperatorsSubmenu(bpy.types.Menu):
    """
    Operations for merging insert meshes.

    """
    bl_label = 'Merge Operators Submenu'
    bl_idname = 'hops.merge_operators_submenu'

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
    bl_idname = 'hops.bool_scroll_operators_submenu'

    def draw(self, context):
        layout = self.layout

        layout.operator_context = "INVOKE_DEFAULT"
        single = layout.operator("hops.bool_scroll", text="Scroll Booleans")
        single.additive = False
        additive = layout.operator("hops.bool_scroll", text="Additive Scroll")
        additive.additive = True
        layout.operator("hops.bool_scroll_objects", text="Object Scroll")
        layout.operator("hops.bool_toggle_viewport", text= "Toggle Boolean Visibility")
