import bpy
from .modifier_combo import *
from bpy.types import UIList, Panel


class ComboListComponent(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, index):
        split = layout.split(0)
        split.prop(item, "combo_name", text = "", emboss = False, translate = False, icon = 'NONE')


class ComboListInterface(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = 'VIEW_3D_PT_modifier_combo'
    bl_category = 'Modifier Combo'
    bl_label = 'Modifier Combo List'

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        item = scene.combo_list_cache
        row = layout.row()
        row.template_list("ComboListComponent", "", scene, "combo_list_cache", scene, "combo_list_selected_index", rows = 10)

        col = row.column(align = True)
        col.operator("modifier_combo.register_combo", icon = 'ZOOMIN', text = '')
        col.operator("modifier_combo.unregister_combo", icon = 'ZOOMOUT', text = '')
        col.operator("modifier_combo.make_combo", icon = 'MODIFIER', text = '')
        col.separator()
        col.operator("modifier_combo.swap_up", icon = 'TRIA_UP', text = '')
        col.operator("modifier_combo.swap_down", icon = 'TRIA_DOWN', text = '')


class ComboMenu(bpy.types.Menu):
    bl_label = "Modifier Combo Menu"
    bl_idname = "modifier_combo_menu"

    def draw(self, context):
        layout = self.layout

        for index in range(len(bpy.context.scene.combo_list_cache)):
            props = layout.operator("modifier_combo.make_combo_via_menu", text = bpy.context.scene.combo_list_cache[index].combo_name) #TODO
            props.index = index

