# 3D Navigation_x TOOLBAR v1.2 - 3Dview Addon - Blender 2.5x
#
# THIS SCRIPT IS LICENSED UNDER GPL,
# please read the license block.
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
"name": "Compact Properties",
"author": "bookyakuno",
"version": (1,2),
"blender": (2, 77),
"location": "Cmd + Ctrl + 3, Shift + Ctrl + 3",
"description": "Simple Panel",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Learnbgame"
}
import bpy
################################################################
from bl_ui.properties_data_modifier import DATA_PT_modifiers
#
#
# import bpy
# from bpy.types import Menu
#
# import os
# from bpy.types import (
#         Panel,
#         Menu,
#         Operator,
#         UIList,
#         )
# from rna_prop_ui import PropertyPanel
# from bl_ui.properties_data_modifier import DATA_PT_modifiers
# from bpy.props import *
################################################################
class compact_prop(bpy.types.Operator):
    bl_idname = "object.compact_prop"
    bl_label = "Compact Properties"
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value*6, height=300)
    def draw(self, context):
        mp = DATA_PT_modifiers(context)
        ob = context.object
        layout = self.layout
        row = layout.row()
#         if context.active_object is None:
#             row.alignment = 'CENTER'
#             row.label("No Object!", icon = 'INFO')
#             return
################################################################
        col = layout.column(align=True)
#        col.label(text="Hello World!!")
        view = context.space_data
        scene = context.scene
        obj = context.object
        obj_type = obj.type
################################################################
################################################################
### Amaranth Toolset のフレームオンシェード(displayWireframe)
        row = col.row(align=True)
        row.operator("object.amth_wire_toggle" ,
                                 icon="MOD_WIREFRAME", text="Wire").clear = False
        row.operator("object.amth_wire_toggle" ,
                                 icon="X", text="Clear").clear = True
        row = col.row(align=True)
        row.operator("mesh.presel", text="PreSel" ,icon="LOOPSEL")
        row.operator("presel.stop", text="PreSel" ,icon="X")
################################################################
################################################################
### その他いろいろ
        col = layout.column(align=True)
        layout.separator()

        row = layout.row()
### 透視/並行投影
        row.operator("view3d.view_persportho", icon="OUTLINER_OB_CAMERA", text="")
        ### ワールドの背景
        row.prop(view, "show_world", text="World.",icon="WORLD")
### レンズ
        view = context.space_data
        row.active = bool(view.region_3d.view_perspective != 'CAMERA' or view.region_quadviews)
        row.prop(view, "lens",icon="SCENE")
### 描画タイプ
        obj = context.object
        row = layout.row()
        row.prop(obj, "draw_type", text="",icon="TEXTURE_SHADED")
#        col.prop(view, "show_only_render")
        row = layout.row()
### X-Ray
        row.prop(obj, "show_x_ray", text="X-Ray.",icon="VISIBLE_IPO_ON")
### バックフェースカーリング
        row.prop(view, "show_backface_culling", text="B.cul",icon="FACESEL")
### ワイヤーフレーム表示
        row.prop(obj, "show_wire", text="Wire.",icon="OUTLINER_OB_LATTICE")
### AO
        rd = scene.render
        ### AO
        col = layout.column(align=True)
        fx_settings = view.fx_settings
#             if fx_settings.use_ssao:
#                 ssao_settings = fx_settings.ssao
#                 subcol = col.column(align=True)
#                 subcol.prop(ssao_settings, "factor")
#                 subcol.prop(ssao_settings, "distance_max")
#                 subcol.prop(ssao_settings, "attenuation")
#                 subcol.prop(ssao_settings, "samples")
#                 subcol.prop(ssao_settings, "color")
        #
        # if view.viewport_shade not in {'BOUNDBOX', 'WIREFRAME'}:
        row = col.row(align=True)
        row.prop(fx_settings, "use_ssao", text="AO",icon="PINNED")
### Matcap
        row.prop(view, "use_matcap",icon="COLOR_RED")
### 被写界深度
        row = col.row(align=True)
        if view.viewport_shade not in {'BOUNDBOX', 'WIREFRAME'}:
            row.active = view.region_3d.view_perspective == 'CAMERA'
            row.prop(fx_settings, "use_dof", text="dof",icon="FORCE_HARMONIC")
### Matcap アイコン
        if view.use_matcap:
            row = col.row(align=True)
            row.template_icon_view(view, "matcap_icon")
################################################################

################################################################

addon_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')

    # compact_prop
    kmi = km.keymap_items.new(compact_prop.bl_idname, 'THREE', 'PRESS', shift=True, ctrl=True)
    kmi = km.keymap_items.new(compact_prop.bl_idname, 'THREE', 'PRESS', oskey=True, ctrl=True)
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


################################################################
################################################################
#
# def register():
#     bpy.utils.register_module(__name__)
# def unregister():
#     bpy.utils.unregister_module(__name__)
# if __name__ == "__main__":
#     register()
