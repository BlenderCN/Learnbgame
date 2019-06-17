import bpy

from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from . import behavior, operation, shape, surface, snap, settings, help

classes = [
    behavior.BC_PT_behavior,
    shape.BC_PT_shape,
    operation.BC_PT_operation,
    surface.BC_PT_surface,
    snap.BC_PT_snap,
    settings.BC_PT_settings,
    settings.display.BC_PT_display_settings,
    settings.behavior.BC_PT_behavior_settings,
    settings.shape.BC_PT_shape_settings,
    settings.input.BC_PT_input_settings,
    settings.hardops.BC_PT_hardops_settings,
    help.BC_PT_help,
    help.general.BC_PT_help_general,
    help.start_operation.BC_PT_help_start_operation]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
