import os
import bpy
from bpy.types import Menu
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... utils.objects import get_inactive_selected_objects
from ... preferences import use_asset_manager, get_preferences, right_handed_enabled, pro_mode_enabled, BC_unlock_enabled, mira_handler_enabled


class HOPS_MT_SettingsSubmenu(bpy.types.Menu):
    bl_label = 'Settings Submenu'
    bl_idname = 'HOPS_MT_SettingsSubmenu'

    def draw(self, context):
        layout = self.layout

        obj = context.object

        if pro_mode_enabled() == False:
            #Learning Hard Ops Button
            layout.operator("hops.learning_popup", text="Hard Ops Learning", icon_value=get_icon_id("Noicon"))
            layout.separator()

        if pro_mode_enabled():
            if context.active_object.type == 'CAMERA':
                cam = bpy.context.space_data
                row = layout.row(align=False)
                col = row.column(align=True)

                #col.label(text="Lock Camera To View")
                col.prop(cam, "lock_camera", text="Lock To View")

#                obj = bpy.context.object.data
#                col.label(text="Passepartout")
#                col.prop(obj, "passepartout_alpha", text="")
#                col.label(text="DOF")
#                col.prop(obj, "dof_object", text="")
#                col.label(text="Aperture")
#                obj = bpy.context.object.data.cycles
#                col.prop(obj, "aperture_size", text="")
                layout.separator()

        if context.active_object.type == 'MESH':
            #Wire/Solid Toggle
            if context.object.display_type == 'WIRE':
                layout.operator("object.solid_all", text="Shade Solid", icon='MESH_CUBE')
            else :
                layout.operator("showwire.objects", text="Shade Wire", icon='OUTLINER_OB_LATTICE')

#            layout.operator_context = 'INVOKE_DEFAULT'
#            layout.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

#            if pro_mode_enabled():
#                layout.operator("hops.viewport_buttons", text="Dots", icon_value=get_icon_id("dots"))

#            if len(context.selected_objects) == 1:
#                layout.menu("HOPS_MT_BasicObjectOptionsSubmenu", text="Object Options")

        view = context.space_data
        layout.prop(view.overlay, 'show_wireframes')

        #Viewport Submenu
        layout = self.layout
        #layout.separator()

        #layout.operator("hops.helper", text="Modifier Helper", icon="SCRIPTPLUGINS")

        layout.separator()

        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("HOPS_MT_MaterialListMenu", text = "Material List", icon_value=get_icon_id("StatusOveride"))

        layout.menu("HOPS_MT_ViewportSubmenu", text="ViewPort", icon_value=get_icon_id("StarConnect"))


        #Order Pizza Button Haha
        layout.operator("view3d.pizzapopup", text="Pizza Ops", icon_value=get_icon_id("Pizzaops"))
        layout.separator()

        #Render Sets
        layout = self.layout
        scene = context.scene.cycles

        row = layout.row(align=False)
        col = row.column(align=True)

        layout.menu("HOPS_MT_RenderSetSubmenu", text="RenderSetups", icon_value=get_icon_id("StatusOveride"))

        if bpy.context.scene.render.engine == 'CYCLES':
            scene = context.scene.cycles
            col.prop(scene, "preview_samples")
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            scene = context.scene.eevee
            col.prop(scene, 'taa_samples')
        else:
            pass

        layout.separator()

        #FrameRange Settings
        layout = self.layout
        scene = context.scene

        row = layout.row(align=False)
        col = row.column(align=True)

        if pro_mode_enabled():
            col.prop(scene, 'frame_end')

            layout.menu("HOPS_MT_FrameRangeSubmenu", text="Frame Range Options",  icon_value=get_icon_id("SetFrame"))


        layout.menu("HOPS_MT_SelectViewSubmenu", text="Selection Options",  icon_value=get_icon_id("ShowNgonsTris"))
