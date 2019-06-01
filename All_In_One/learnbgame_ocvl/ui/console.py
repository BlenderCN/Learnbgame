import bpy
from bpy.types import Header, Menu
from bpy.types import CONSOLE_HT_header as CONSOLE_HT_header_old



class CONSOLE_MT_console_new(Menu):
    bl_label = "Console"

    def draw(self, context):
        layout = self.layout

        layout.operator("console.indent")
        layout.operator("console.unindent")

        layout.separator()

        layout.operator("console.clear")
        layout.operator("console.clear_line")

        layout.separator()

        layout.operator("console.copy_as_script")
        layout.operator("console.copy")
        layout.operator("console.paste")
        layout.menu("CONSOLE_MT_language")

        layout.separator()

        layout.operator("screen.area_dupli")


class CONSOLE_MT_editor_menus_new(Menu):
    bl_idname = "CONSOLE_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("CONSOLE_MT_console_new")


class CONSOLE_HT_header_new(Header):
    bl_space_type = 'CONSOLE'

    def draw(self, context):
        layout = self.layout.row()

        layout.label(icon='CONSOLE')
        # row.template_header()

        CONSOLE_MT_editor_menus_new.draw_collapsible(context, layout)

        layout.operator("console.autocomplete", text="Autocomplete")




classes_to_unregister = [
    CONSOLE_HT_header_old,
    ]


classes = [
    CONSOLE_HT_header_new,
    CONSOLE_MT_editor_menus_new,
    CONSOLE_MT_console_new,
]