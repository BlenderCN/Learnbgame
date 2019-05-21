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
# Author Linus Yng
#
# pep8


bl_info = {
    "name":        "Generic Note Node",
    "description": "A generic note node",
    "author":      "Linus Yng",
    "version":     (0, 2, 0),
    "blender":     (2, 7, 7),
    "location":    "Node Editor, N-Panel or menu Layout",
    "category":    "Node",
    "warning":     "The note will not work for people without this addon",
    "wiki-url":    "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Nodes/Generic_Note",
}

import textwrap
import importlib

import bpy
import nodeitems_builtins
from nodeitems_utils import NodeItem
from nodeitems_builtins import (CompositorNodeCategory,
                                ShaderNewNodeCategory,
                                ShaderOldNodeCategory,
                                TextureNodeCategory)
from bpy.props import StringProperty, FloatVectorProperty, BoolProperty


TEXT_WIDTH = 6

# every textwrap.wrap call creates an instance of of TectWrap
# we wan't to avoid overhead since draw is called very often
TW = textwrap.TextWrapper()


def get_lines(text_file):
    for line in text_file.lines:
        yield line.body


class GenericNoteNode(bpy.types.Node):
    ''' Note '''
    bl_idname = 'GenericNoteNode'
    bl_label = 'Note'
    bl_icon = 'OUTLINER_OB_EMPTY'

    @classmethod
    def poll(cls, ntree):
        return True

    text = StringProperty(name='text',
                          default='',
                          description="Text to show, if set will overide file")

    text_file = StringProperty(description="Textfile to show")

    def format_text(self):
        global TW
        out = []
        if self.text:
            lines = self.text.splitlines()
        elif self.text_file:
            text_file = bpy.data.texts.get(self.text_file)
            if text_file:
                lines = get_lines(text_file)
            else:
                return []
        else:
            return []
        width = self.width
        TW.width = int(width) // TEXT_WIDTH
        for t in lines:
            out.extend(TW.wrap(t))
            out.append("")
        return out

    def init(self, context):
        self.width = 400
        pref = bpy.context.user_preferences.addons[__name__].preferences
        self.color = pref.note_node_color[:]
        self.use_custom_color = True

    def draw_buttons(self, context, layout):
        has_text = self.text or self.text_file
        if has_text:
            col = layout.column(align=True)
            text_lines = self.format_text()
            for l in text_lines:
                if l:
                    col.label(text=l)
        else:
            col = layout.column(align=True)
            col.operator("node.generic_note_from_clipboard", text="From clipboard")
            col.prop(self, "text", text="Text")
            col.prop_search(self, 'text_file', bpy.data, 'texts', text='Text file', icon='TEXT')

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "text", text="Text")
        layout.prop_search(self, 'text_file', bpy.data, 'texts', text='Text file', icon='TEXT')
        layout.operator("node.generic_note_from_clipboard", text="From clipboard")
        layout.operator("node.generic_note_to_text", text="To text editor")
        layout.operator("node.generic_note_clear")

    def clear(self):
        self.text = ""
        self.text_file = ""

    def to_text(self):
        text_name = "Generic Note Text"
        text = bpy.data.texts.get(text_name)
        if not text:
            text = bpy.data.texts.new(text_name)
        text.clear()
        text.write(self.text)


class GenericNoteTextFromClipboard(bpy.types.Operator):
    """
    Update note text from clipboard
    """
    bl_idname = "node.generic_note_from_clipboard"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        text = bpy.context.window_manager.clipboard
        if not text:
            self.report({"INFO"}, "No text selected")
            return {'CANCELLED'}
        node = context.node
        node.text = text
        return {'FINISHED'}


class GenericNoteClear(bpy.types.Operator):
    """
    Clear Note Node
    """
    bl_idname = "node.generic_note_clear"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = context.node
        node.clear()
        return {'FINISHED'}


class GenericNoteNodeToText(bpy.types.Operator):
    """
    Put note into a text buffer
    """
    bl_idname = "node.generic_note_to_text"
    bl_label = "To text"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = context.node
        text = node.text
        if not text:
            self.report({"INFO"}, "No text in node")
            return {'CANCELLED'}
        node.to_text()
        self.report({"INFO"}, "See text editor: Generic Note Text")
        return {'FINISHED'}


class GenericNoteNodePanel(bpy.types.Panel):
    bl_idname = "generic_note_node_panel"
    bl_label = "Note"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Generic'
    bl_options = {'DEFAULT_CLOSED'}
    use_pin = True

    @classmethod
    def poll(cls, context):
        return bool(context.space_data.node_tree)

    def draw(self, context):
        layout = self.layout
        op = layout.operator("node.add_node", text="New Note")
        op.type = "GenericNoteNode"
        op.use_transform = True

        op = layout.operator("node.add_node",
                             text="New note from clipboard")
        op.type = "GenericNoteNode"
        op.use_transform = False
        item = op.settings.add()
        item.name = "text"
        #  item.value get through eval later
        item.value = repr(bpy.context.window_manager.clipboard)

        pref = context.user_preferences.addons[__name__].preferences
        layout.prop(pref, "note_node_color")


class GenericNotePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def menu_switch(self, context):
        if self.register_menus:
            register_menus()
        else:
            unregister_menus()

    note_node_color = FloatVectorProperty(name="Note Color",
                                          description='Default color for note node',
                                          size=3, min=0.0, max=1.0,
                                          default=(.5, 0.5, .5), subtype='COLOR')

    register_menus = BoolProperty(name="Register Menus",
                                  description="Register the note node in the layout category",
                                  default=False,
                                  update=menu_switch)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "register_menus")
        row = layout.row()
        row.prop(self, "note_node_color")


#  code for registering menus. would like a proper interface for this
# replacement layout categories

menu_categories = {
    "CMP_LAYOUT": (CompositorNodeCategory, "CMP_LAYOUT", "Layout", [
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("GenericNoteNode"),
        NodeItem("CompositorNodeSwitch"),
    ]),
    "TEX_LAYOUT": (TextureNodeCategory, "TEX_LAYOUT", "Layout", [
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("GenericNoteNode"),
    ]),
    "SH_NEW_LAYOUT": (ShaderNewNodeCategory, "SH_NEW_LAYOUT", "Layout", [
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("GenericNoteNode"),
    ]),
    "SH_LAYOUT": (ShaderOldNodeCategory, "SH_LAYOUT", "Layout", [
        NodeItem("NodeFrame"),
        NodeItem("NodeReroute"),
        NodeItem("GenericNoteNode"),
    ])
}

"""
Really prefer there would be an interface for this instead of
patching this in as done here. Also happy for suggestions for
better methods.
"""


def register_menus():
    # remove, replace, add back the menus
    nodeitems_builtins.unregister()

    menus = [
        nodeitems_builtins.shader_node_categories,
        nodeitems_builtins.compositor_node_categories,
        nodeitems_builtins.texture_node_categories,
    ]
    for menu in menus:
        for index, node_cat in enumerate(menu):
            if node_cat.identifier in menu_categories:
                cls, c_type, text, items = menu_categories[node_cat.identifier]
                menu[index] = cls(c_type, text, items=items)

    nodeitems_builtins.register()


def unregister_menus():
    #  if this fails menus aren't loaded. this ensure that they can load
    try:
        nodeitems_builtins.unregister()
    except:
        pass
    #  reload the code dumps all changes
    importlib.reload(nodeitems_builtins)
    nodeitems_builtins.register()


def register():
    bpy.utils.register_module(__name__)
    pref = bpy.context.user_preferences.addons[__name__].preferences

    if pref.register_menus:
        register_menus()


def unregister():
    bpy.utils.unregister_module(__name__)
    unregister_menus()

if __name__ == "__main__":
    register()
