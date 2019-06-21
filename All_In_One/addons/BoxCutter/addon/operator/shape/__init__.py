import bpy

from bpy.utils import register_class, unregister_class

from . import draw, snap

classes = (
    draw.BC_OT_draw_shape,
    snap.BC_OT_display_snap)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in classes:
        unregister_class(cls)
