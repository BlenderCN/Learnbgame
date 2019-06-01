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

# <pep8 compliant>

# Todo:
#   - make it possible to add more custom tool panels
#   - list all tools in an orderly fashion
#   - add icons to tools that have one
#   - save tool panel so you can load it later
#   - make tools callable with a hotkey as floating menu

bl_info = {
    "name": "Add Custom Tool Panel",
    "description": "Add tools to a custom tool shelf",
    "author": "jasperge",
    "version": (0, 1),
    "blender": (2, 69, 0),
    "location": "View 3D > Toolbar",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy

from bpy.props import (StringProperty,
                       EnumProperty)


def panel_types():
    basetype = bpy.types.Panel
    for typename in dir(bpy.types):
        btype = getattr(bpy.types, typename)
        if issubclass(btype, basetype):
            yield btype


def panels_by_label(label):
    for ptype in panel_types():
        if getattr(ptype.bl_rna, "bl_label", None) == label:
            yield ptype


def create_panel(label):
    class CustomToolPanel(bpy.types.Panel):
        bl_label = label
        bl_idname = "VIEW3D_PT_custom_tool_panel"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'TOOLS'

        def draw(self, context):
            layout = self.layout
            col = layout.column(align=True)

    bpy.utils.register_class(CustomToolPanel)


def remove_panel():
    bpy.utils.unregister_class(
        getattr(bpy.types, 'VIEW3D_PT_custom_tool_panel'))


class WM_OT_add_panel(bpy.types.Operator):

    """Add a panel to the Tool Shelf"""

    bl_description = "Add a panel to the Tool Shelf"
    bl_idname = "wm.panel_add"
    bl_label = "Add Custom Panel"
    bl_space_type = 'VIEW_3D'

    label = StringProperty(
                name='Panel name',
                description='The name for the custom tool panel',
                default='Custom')

    def execute(self, context):
        existing_panels = panels_by_label(self.label)
        if not list(existing_panels):
            create_panel(self.label)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'label')


class WM_OT_remove_panel(bpy.types.Operator):

    """Remove a panel from the Tool Shelf"""

    bl_description = "Remove a panel from the Tool Shelf"
    bl_idname = "wm.panel_remove"
    bl_label = "Remove Custom Panel"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        remove_panel()

        return {'FINISHED'}

class WM_OT_add_tool(bpy.types.Operator):

    """Add a tool to the custom panel"""

    bl_description = "Add a tool to the custom panel"
    bl_idname = "wm.tool_add"
    bl_label = "Add Tool"
    bl_space_type = 'VIEW_3D'

    tools = EnumProperty(
                name="Tool",
                items=(('mesh.primitive_monkey_add', "Monkey", "Construct a Suzanne mesh"),
                       ('mesh.primitive_cube_add', "Cube", "Construct a cube mesh"),
                       ),
                default='mesh.primitive_monkey_add'
                )

    def execute(self, context):
        tool_to_add = self.tools
        def draw_my_buttons(self, context):

            self.layout.operator(tool_to_add)

        bpy.types.VIEW3D_PT_custom_tool_panel.append(draw_my_buttons)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'tools')


class WM_OT_remove_tool(bpy.types.Operator):

    """Remove a tool from the custom panel"""

    bl_description = "Remove a tool from the custom panel"
    bl_idname = "wm.tool_remove"
    bl_label = "Remove Tool"
    bl_space_type = 'VIEW3D'

    def execute(self, context):
        print('oeps')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=240)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        layout.operator_menu_enum("mesh.primitive_circle_add",
                property="fill_type",
                text="Fill type"
                )


class AddCustomToolsPanel(bpy.types.Panel):
    bl_label = "Add Custom Tools Panel"
    bl_idname = "VIEW3D_PT_add_custom_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):

        layout = self.layout
        col = layout.column(align=True)
        col.operator('wm.panel_add')
        col.operator('wm.panel_remove')
        col.separator()
        col.operator('wm.tool_add')
        col.operator('wm.tool_remove')


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
