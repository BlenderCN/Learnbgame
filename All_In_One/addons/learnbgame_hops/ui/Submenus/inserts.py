import os
import bpy,bgl,blf
from bpy.types import Menu
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... utils.objects import get_inactive_selected_objects
from ... preferences import use_asset_manager, get_preferences, right_handed_enabled, pro_mode_enabled



#Insert Object
class HOPS_MT_InsertsObjectsSubmenu(bpy.types.Menu):
    bl_idname = "hops.insert_objects_submenu"
    bl_label = "Inserts Objects"

    def draw(self, context):
        layout = self.layout

        wm = context.window_manager
        preferences = bpy.context.preferences

        if pro_mode_enabled():
            layout.operator("view3d.asset_scroller_window", text="(Asset Window)", icon_value=get_icon_id("HardOps"))

        layout.template_icon_view(wm, "Hard_Ops_previews")
        layout.template_icon_view(wm, "sup_preview")
        if addon_exists("MESHmachine"):
            #layout.template_icon_view(wm, "pluglib_")
            layout.separator()
            layout.menu("machin3.mesh_machine_plug_libraries", text="Machin3")
            layout.menu("machin3.mesh_machine_plug_utils_menu", text="Plug Utils")
        layout.separator()

        if len(context.selected_objects) > 1:
            layout.operator("object.to_selection", text="Obj to selection", icon="MOD_MULTIRES")
            layout.operator("make.link", text="Link Objects", icon='CONSTRAINT' )
            layout.operator("unlink.objects", text="Unlink Objects", icon='UNLINKED' )

        if addon_exists("asset_management"):
            #box = pie.box()
            #col = box.column()
            asset_manager = wm.asset_m
            layout.prop(asset_manager, "libraries", text="")
            layout.prop(asset_manager, "categories", text="")
            layout.template_icon_view(wm, "AssetM_previews", show_labels = True)
