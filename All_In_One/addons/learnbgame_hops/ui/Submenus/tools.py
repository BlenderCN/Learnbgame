import bpy
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import pro_mode_enabled


class HOPS_MT_ObjectToolsSubmenu(bpy.types.Menu):
    bl_label = 'Objects Tools Submenu'
    bl_idname = 'hops.object_tools_submenu'

    def draw(self, context):
        layout = self.layout

        if hasattr(context.window_manager, 'boxcutter'):
            layout.operator("boxcutter.toolbar_activate", text="BoxCutter", icon_value=get_icon_id("BoxCutter"))
        else:
            layout.operator("wm.url_open", text="Get BoxCutter!", icon_value=get_icon_id("BoxCutter")).url = "https://gum.co/BoxCutter/iamanoperative"

        if pro_mode_enabled():
            if context.active_object.type == 'MESH':
                layout = self.layout.column_flow(columns=1)

                if len(context.selected_objects) == 1:
                    layout.operator("view3d.status_helper_popup", text="StatusOveride")
                    layout.operator("hops.reset_status", text="StatusReset")
                else:
                    pass
                layout.separator()

        layout = self.layout

        layout.operator("array.twist", text="Twist 360", icon_value=get_icon_id("ATwist360"))
        #layout.operator("nw.radial_array", text="Radial 360", icon_value=get_icon_id("ATwist360"))

        layout.separator()
        layout.operator("view3d.hops_helper_popup", text="Modifier Helper", icon="SCRIPTPLUGINS").tab = "MODIFIERS"

        layout.separator()
        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("hops.material_list_menu", icon_value=get_icon_id("Noicon"))

        layout.separator()
        layout.operator("hops.reset_axis_modal", text="Reset Axis", icon_value=get_icon_id("Xslap"))
        layout.operator("hops.reset_axis", text="Reset Axis New", icon_value=get_icon_id("Xslap"))
        layout.separator()
        layout.menu("hops.symetry_submenu", text="Symmetry Options", icon_value=get_icon_id("Xslap"))

        layout.separator()

        layout.operator("hops.xunwrap", text="(X) Unwrap", icon_value=get_icon_id("CUnwrap"))
        # layout.operator("object.cunwrap", text="(C) Unwrap", icon_value=get_icon_id("CUnwrap"))

        layout.separator()

        layout.operator("clean.reorigin", text="(S) Clean Recenter", icon_value=get_icon_id("SCleanRecenter"))

        if pro_mode_enabled():
            layout.operator("stomp2.object", text="ApplyAll (-L)", icon_value=get_icon_id("Applyall"))
            layout.separator()
            layout.operator("hops.sphere_cast", text="SphereCast", icon_value=get_icon_id("SphereCast"))

        layout.separator()
        #layout.operator("hops.shrinkwrap", text="Shrinkwrap")
        #layout.operator("hops.shrinkwrap_refresh", text="Shrinkwrap Refresh")
        layout.operator("hops.shrinkwrap2", text="ShrinkTo")


class HOPS_MT_MeshToolsSubmenu(bpy.types.Menu):
    bl_label = 'Mesh Tools Submenu'
    bl_idname = 'hops.mesh_tools_submenu'

    def draw(self, context):
        layout = self.layout
