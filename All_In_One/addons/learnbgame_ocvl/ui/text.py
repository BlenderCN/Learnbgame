import bpy
from bpy.types import Header, Menu
from bpy.types import TEXT_HT_header as TEXT_HT_header_old
from bpy.app.translations import pgettext_iface as iface_


class TEXT_MT_view_new(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        layout.operator("text.properties", icon='MENU_PANEL')

        layout.separator()

        layout.operator("text.move",
                        text="Top of File",
                        ).type = 'FILE_TOP'
        layout.operator("text.move",
                        text="Bottom of File",
                        ).type = 'FILE_BOTTOM'

        layout.separator()

        layout.operator("screen.area_dupli")


class TEXT_MT_text_new(Menu):
    bl_label = "Text"

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        text = st.text

        layout.operator("text.new")
        layout.operator("text.open")

        if text:
            layout.operator("text.reload")

            layout.column()
            layout.operator("text.save")
            layout.operator("text.save_as")

            if text.filepath:
                layout.operator("text.make_internal")


class TEXT_MT_editor_menus_new(Menu):
    bl_idname = "TEXT_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        st = context.space_data
        text = st.text

        layout.menu("TEXT_MT_view_new")
        layout.menu("TEXT_MT_text_new")

        if text:
            layout.menu("TEXT_MT_edit_new")
            layout.menu("TEXT_MT_format")


class TEXT_MT_edit_new(Menu):
    bl_label = "Edit"

    @classmethod
    def poll(cls, context):
        return (context.space_data.text)

    def draw(self, context):
        layout = self.layout

        layout.operator("ed.undo")
        layout.operator("ed.redo")

        layout.separator()

        layout.operator("text.cut")
        layout.operator("text.copy")
        layout.operator("text.paste")
        layout.operator("text.duplicate_line")

        layout.separator()

        layout.operator("text.move_lines",
                        text="Move line(s) up").direction = 'UP'
        layout.operator("text.move_lines",
                        text="Move line(s) down").direction = 'DOWN'

        layout.separator()

        layout.menu("TEXT_MT_edit_select")

        layout.separator()

        layout.operator("text.jump")
        layout.operator("text.start_find", text="Find...")
        layout.operator("text.autocomplete")



class TEXT_HT_header_new(Header):
    bl_space_type = 'TEXT_EDITOR'

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        text = st.text

        row = layout.row(align=True)
        layout.label(icon='TEXT')
        # row.template_header()

        TEXT_MT_editor_menus_new.draw_collapsible(context, layout)

        if text and text.is_modified:
            sub = row.row(align=True)
            sub.alert = True
            sub.operator("text.resolve_conflict", text="", icon='HELP')

        row = layout.row(align=True)
        row.template_ID(st, "text", new="text.new", unlink="text.unlink", open="text.open")

        row = layout.row(align=True)
        row.prop(st, "show_line_numbers", text="")
        row.prop(st, "show_word_wrap", text="")
        row.prop(st, "show_syntax_highlight", text="")

        if text:
            row = layout.row()
            if text.filepath:
                if text.is_dirty:
                    row.label(text=iface_("File: *%r (unsaved)") %
                              text.filepath, translate=False)
                else:
                    row.label(text=iface_("File: %r") %
                              text.filepath, translate=False)
            else:
                row.label(text="Text: External"
                          if text.library
                          else "Text: Internal")


classes_to_unregister = [
    TEXT_HT_header_old,
]


classes = [
    TEXT_HT_header_new,
    TEXT_MT_editor_menus_new,
    TEXT_MT_view_new,
    TEXT_MT_text_new,
    TEXT_MT_edit_new,
]
