import bpy
from bpy.props import *
from . icons import icons
from . ui.addon_checker import draw_addon_diagnostics
from . utils.addons import addon_exists
from . preferences import get_preferences


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
    KitOps Insert Popup Window

    """
    bl_idname = "view3d.insertpopup"
    bl_label = "Kit Ops"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        preference = get_preferences()
        dpi_value = bpy.context.preferences.system.dpi

        if preference.use_kitops_popup:
            return context.window_manager.invoke_popup(self, width=dpi_value*2.5, height=200)
        else:
            return context.window_manager.invoke_props_dialog(self, width=dpi_value*2.5, height=200)

    def draw(self, context):
        if addon_exists("kitops"):
            from kitops.addon.interface.panel import KO_PT_ui
            KO_PT_ui.draw(self,context)

            from kitops.addon.utility.addon import preference

            preference = preference()

            self.layout.separator()

            row = self.layout.row()
            row.label(text='Sort Modifiers')
            row.prop(preference, 'sort_modifiers', text='')

            if preference.sort_modifiers:
                row = self.layout.row(align=True)
                row.alignment = 'RIGHT'
                row.prop(preference, 'sort_bevel', text='', icon='MOD_BEVEL')
                row.prop(preference, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
                row.prop(preference, 'sort_array', text='', icon='MOD_ARRAY')
                row.prop(preference, 'sort_mirror', text='', icon='MOD_MIRROR')
                row.prop(preference, 'sort_simple_deform', text='', icon='MOD_SIMPLEDEFORM')
                row.prop(preference, 'sort_triangulate', text='', icon='MOD_TRIANGULATE')

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

        return context.window_manager.invoke_props_dialog(self, width=dpi_value*3.5, height=200)

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
