import bpy
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import pro_mode_enabled


class HOPS_MT_ObjectToolsSubmenu(bpy.types.Menu):
    bl_label = 'Objects Tools Submenu'
    bl_idname = 'HOPS_MT_ObjectToolsSubmenu'

    def draw(self, context):
        layout = self.layout

        if not hasattr(context.window_manager, 'bc'):
            layout.operator("wm.url_open", text="Get BoxCutter!", icon_value=get_icon_id("BoxCutter")).url = "https://gum.co/BoxCutter/iamanoperative"

        layout.operator("hops.reset_axis_modal", text="Reset Axis", icon_value=get_icon_id("Xslap"))

        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("HOPS_MT_MaterialListMenu", text = "Material List", icon_value=get_icon_id("StatusOveride"))
            if len(context.selected_objects) >= 2:
                layout.operator("material.simplify", text="Material Link", icon_value=get_icon_id("Applyall"))

        layout.separator()

        layout.menu("HOPS_MT_SymmetrySubmenu", text="Symmetry", icon_value=get_icon_id("Xslap"))

        layout.separator()
        layout.operator("hops.bevel_helper", text="Bevel Helper", icon_value=get_icon_id("CSharpen"))
        layout.operator("hops.sharp_manager", text="Edge Manager", icon_value=get_icon_id("Diagonal"))
        layout.operator("view3d.bevel_multiplier", text="Bevel Exponent", icon_value=get_icon_id("BevelMultiply"))

        layout.separator()

        if pro_mode_enabled():
            if context.active_object.type == 'MESH':
                layout = self.layout.column_flow(columns=1)

                if len(context.selected_objects) == 1:
                    #layout.operator("view3d.status_helper_popup", text="HOPS Overide", icon_value=get_icon_id("StatusOveride"))
                    layout.operator("hops.reset_status", text="HOPS Reset", icon_value=get_icon_id("StatusReset"))
                    layout.separator()
                else:
                    pass

        layout = self.layout

        layout.operator("array.twist", text="Twist 360", icon_value=get_icon_id("ATwist360"))
        #layout.operator("nw.radial_array", text="Radial 360", icon_value=get_icon_id("ATwist360"))
        layout.operator("clean.reorigin", text="Apply 360", icon_value=get_icon_id("Applyall")).origin_set = True
        #layout.operator("hops.boolshape_status_swap", text="Green", icon_value=get_icon_id("Green")).red = False

        layout.separator()

        layout.operator("hops.xunwrap", text="Auto Unwrap", icon_value=get_icon_id("CUnwrap"))

        if len(context.selected_objects) == 2:
            layout.operator("hops.shrinkwrap2", text="ShrinkTo", icon_value=get_icon_id("ShrinkTo"))

        layout.separator()

        layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")



class HOPS_MT_MeshToolsSubmenu(bpy.types.Menu):
    bl_label = 'Mesh Tools Submenu'
    bl_idname = 'HOPS_MT_MeshToolsSubmenu'

    def draw(self, context):
        layout = self.layout
