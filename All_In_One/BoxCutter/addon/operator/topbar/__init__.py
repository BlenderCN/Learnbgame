import bpy

from bpy.utils import register_class, unregister_class
from . import activate, set_shape

classes = (
    activate.BC_OT_topbar_activate,
    set_shape.BC_OT_box,
    set_shape.BC_OT_circle,
    set_shape.BC_OT_ngon,
    set_shape.BC_OT_custom)


def register():

    for cls in classes:
        register_class(cls)


def unregister():

    for cls in classes:
        unregister_class(cls)
