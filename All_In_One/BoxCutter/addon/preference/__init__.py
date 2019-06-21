import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences
from bpy.props import *

from . import behavior, color, display, expand, keymap, shape
from .. utility import addon, names

# label row text names


class bc(AddonPreferences):
    bl_idname = addon.name

    settings: EnumProperty(
        name = 'Settings',
        description = 'Settings to display',
        items = [
            ('BEHAVIOR', 'Behavior', ''),
            ('COLOR', 'Color', ''),
            ('DISPLAY', 'Display', ''),
            ('SHAPE', 'Shape', ''),
            ('KEYMAP', 'Keymap', '')],
        default = 'BEHAVIOR')

    # TODO: add update handler to gizmo toggles that calls gizmo ot
    cursor: BoolProperty(
        name = names['cursor'],
        description = 'Show cursor gizmo',
        default = False)

    transform_gizmo: BoolProperty(
        name = names['transform_gizmo'],
        description = 'Show transform gizmo',
        default = False)

    cursor_axis: EnumProperty(
        name = 'Axis',
        description = 'Axis to be used',
        items = [
            ('X', 'X', ''),
            ('Y', 'Y', ''),
            ('Z', 'Z', '')],
        default = 'Z')

    surface: EnumProperty(
        name = 'Surface',
        description = 'Draw Surface',
        items = [
            ('OBJECT', 'Object', 'Modal Shortcut: ,', 'OBJECT_DATA', 0),
            ('CURSOR', 'Cursor', 'Modal Shortcut: ,', 'PIVOT_CURSOR', 1),
            ('CENTER', 'World', 'Modal Shortcut: ,', 'WORLD', 2)],
        default = 'OBJECT')

    behavior: PointerProperty(type=behavior.bc)
    color: PointerProperty(type=color.bc)
    display: PointerProperty(type=display.bc)
    keymap: PointerProperty(type=keymap.bc)
    expand: PointerProperty(type=expand.bc)
    shape: PointerProperty(type=shape.bc)


    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        row = column.row(align=True)
        row.prop(self, 'settings', expand=True)

        box = column.box()
        globals()[self.settings.lower()].draw(self, context, box)

classes = (
    behavior.bc,
    color.bc,
    display.bc,
    keymap.bc,
    expand.bc,
    shape.bc,
    bc)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
