import bpy
from bpy.props import *
from . icons import icons
from . ui.addon_checker import draw_addon_diagnostics


class HOPS_OT_LearningPopup(bpy.types.Operator):
    """
    Learn more about Hard Ops / Boxcutter and how to use them.

    """
    bl_idname = "hops.learning_popup"
    bl_label = "Learning Popup Helper"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=200)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row()
        box = col.box()

        for name, url in weblinks:
            col.operator("wm.url_open", text=name).url = url

weblinks = [
    ("Hard Ops Documentation",  "http://hardops-manual.readthedocs.io/en/latest/"),
    ("Version 9 Release Log",   "http://masterxeon1001.com/2018/06/05/hard-ops-0095-americium/"),
    ("Version 9 Videos",        "https://www.youtube.com/playlist?list=PL0RqAjByAphEUuI2JDxIjjCQtfTRQlRh0"),
    ("Hard Ops 8 P5 Notes",     "https://masterxeon1001.com/2017/02/10/hard-ops-0087-hassium-update/"),
    ("Hard Ops 8 P4 Notes",     "https://masterxeon1001.com/2016/09/13/hard-ops-8-p4-update/"),
    ("Hard Ops 8 P3 Notes",     "https://masterxeon1001.com/2016/05/28/hard-ops-8-release-notes/"),
    ("Hard Ops Manual",         "http://hardops-manual.readthedocs.io/en/latest/"),
    ("Hard Ops Video Playlist", "https://www.youtube.com/playlist?list=PL0RqAjByAphGEVeGn9QdPdjk3BLJXu0ho"),
    ("Hard Ops User Gallery",   "https://www.pinterest.com/masterxeon1001/hard-ops-users/"),
    ("Challenge Board",         "https://www.pinterest.com/masterxeon1001/-np/"),
    ("Hard Ops Facebook Group", "https://www.facebook.com/groups/HardOps/"),
    ("Hard Ops Discord Channel","https://discord.gg/aKn5u7g"),
    ("Box Cutter Latest Guide", "https://masterxeon1001.com/2018/06/04/boxcutter-6-8-8-ghostscythe/")
]


class HOPS_OT_InsertsPopupPreview(bpy.types.Operator):
    """
    Interactive insert popup scroller

    """
    bl_idname = "view3d.insertpopup"
    bl_label = "Asset Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*2, height=200)

    def draw(self, context):
        layout = self.layout
        # AM = context.window_manager.asset_m
        wm = context.window_manager

        layout = self.layout.column_flow(columns=1)
        row = layout.row()
        sub = row.row()
        sub.scale_y = 1.2

        layout.label(text="Classic Inserts")
        layout.template_icon_view(wm, "Hard_Ops_previews")

        layout.separator()

        layout.label(text="Red Series")
        layout.template_icon_view(wm, "sup_preview")

        if context.object is not None and context.selected_objects:

            layout.separator()
            if len(context.selected_objects) > 1 and context.object.mode == 'EDIT':
                row = layout.row()
                row.operator("object.to_selection", text="Obj to selection", icon="MOD_MULTIRES")

            # Link Objects
            if len(context.selected_objects) > 1 and context.object.mode == 'OBJECT':
                row = layout.split(align=True)
                row.operator("make.link", text="Link Objects", icon='CONSTRAINT')

            # Unlink Objects
            if context.object.mode == 'OBJECT':
                row = layout.split(align=True)
                row.operator("unlink.objects", text="Unlink Objects", icon='UNLINKED')

    def check(self, context):
        return True

class HOPS_OT_AddonPopupPreview(bpy.types.Operator):
    """
    Addon checker popup

    """
    bl_idname = "view3d.addoncheckerpopup"
    bl_label = "Addon Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3, height=200)

    def draw(self, context):
        draw_addon_diagnostics(self.layout, columns=2)

    def check(self, context):
        return True


class HOPS_OT_PizzaPopupPreview(bpy.types.Operator):
    """
    Order A Pizza!

    """
    bl_idname = "view3d.pizzapopup"
    bl_label = "Pizza Popup"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.preferences.system.dpi

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*2, height=200)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.label(text="Pizza Ops")
        layout.label(text="")
        layout.label(text="")

        row = layout.row()

        layout.label(text="Dominos Pizza")
        layout.operator("wm.url_open", text="Order Dominoes").url = "https://order.dominos.com/"
        layout.label(text="")
        layout.separator()

        layout.label(text="Pizza Hut Pizza")
        layout.operator("wm.url_open", text="Order Pizza Hut").url = "http://www.pizzahut.com/"
        layout.label(text="")
        layout.separator()

        layout.label(text="Papa John's Pizza")
        layout.operator("wm.url_open", text="Order Papa John's").url = "https://www.papajohns.com/order/menu"
        layout.label(text="")
        layout.separator()
