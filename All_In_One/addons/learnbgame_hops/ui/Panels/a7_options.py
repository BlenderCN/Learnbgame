import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import os
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import pro_mode_enabled

class HOPS_PT_OptionsPanel(bpy.types.Panel):
    bl_label = "Hops Options"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout.column(1)
        active_object = context.active_object

        layout.operator("hops.viewport_buttons")
        layout.separator()

        if active_object is None:
            layout.menu("hops.render_set_submenu", text="RenderSets", icon_value=get_icon_id("Gui"))
            layout.menu("hops.vieport_submenu", text="ViewPort", icon_value=get_icon_id("Viewport"))
        elif active_object.mode == "OBJECT":

            obj = context.object


            if pro_mode_enabled():
                if context.active_object.type == 'CAMERA':
                    cam = bpy.context.space_data
                    row = layout.row(align=False)
                    col = row.column(align=True)

                    col.prop(cam, "lock_camera", text="Lock To View")

            if context.active_object.type == 'MESH':
                if context.object.display_type == 'WIRE':
                    layout.operator("object.solid_all", text="Solid Mode", icon='MESH_CUBE')
                else :
                    layout.operator("showwire.objects", text="Wire Mode", icon='OUTLINER_OB_LATTICE')

                layout.operator_context = 'INVOKE_DEFAULT'
                layout.operator("hops.draw_uv", text="UV Preview", icon_value=get_icon_id("CUnwrap"))

                if len(context.selected_objects) == 1:
                    layout.menu("hops.basic_objects_options_submenu", text="Object Options")


            if bpy.context.object and bpy.context.object.type == 'MESH':
                layout.menu("hops.material_list_menu", icon_value=get_icon_id("Noicon"))

            layout.menu("hops.vieport_submenu", text="ViewPort", icon_value=get_icon_id("Noicon"))
            layout.operator("view3d.pizzapopup", text="Pizza Ops", icon_value=get_icon_id("Pizzaops"))
            layout.separator()

            scene = context.scene.cycles

            row = layout.row(align=False)
            col = row.column(align=True)

            layout.menu("hops.render_set_submenu", text="RenderSetups", icon_value=get_icon_id("Noicon"))

            col.prop(scene, "preview_samples")

            layout.separator()

            #FrameRange Settings
            layout = self.layout
            scene = context.scene

            row = layout.row(align=False)
            col = row.column(align=True)

            if pro_mode_enabled():
                col.prop(scene, 'frame_end')

                layout.menu("hops.frame_range_submenu", text="Frame Range Options")

            layout.menu("hops.selection_submenu", text="Selection Options")

            layout.label(text ="Cutting Material:")
            # layout.separator()
            material_option = context.window_manager.Hard_Ops_material_options
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(material_option, "material_mode", expand=True)
            row = col.row(align=True)
            if material_option.material_mode == "ALL":
                row.prop_search(material_option, "active_material", bpy.data, "materials", text="")
            else:
                row.prop_search(material_option, "active_material", context.active_object, "material_slots", text="")
            row.prop(material_option, "force", text="", icon="FORCE_FORCE")
        elif active_object.mode == "EDIT":
            self.draw_edit_mode_menu(layout, active_object)

    def draw_edit_mode_menu(self, layout, object):

        if pro_mode_enabled():
            if addon_exists("mira_tools"):
                layout.menu("hops.mira_submenu", text="Mira (T)", icon="PLUGIN")

        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.menu("hops.material_list_menu", text="Material", icon_value=get_icon_id("Noicon"))
