import bpy

from bpy.utils import register_class, unregister_class
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

from . import shape, topbar, cursor3d, grid, help, modifiers, transform
from .. utility import addon

classes = (
    cursor3d.BC_OT_CursorTranslate,
    cursor3d.BC_OT_CursorRotate,
    cursor3d.BC_WGT_GizmoGroup,
    cursor3d.BC_OT_AddCursorGizmo,
    cursor3d.BC_OT_RemoveCursorGizmo,
    cursor3d.BC_GT_CustomFace,
    cursor3d.BC_GT_CustomCursorCube,
    grid.BC_WGT_GridGizmo,
    grid.BC_OT_AddGridGizmo,
    grid.BC_OT_RemoveGridGizmo,
    grid.BC_GT_GridLayout,
    help.BC_OT_help_link,
    modifiers.BC_OT_ApplyModifiers,
    transform.BC_OT_Translate,
    transform.BC_OT_Rotate,
    transform.BC_OT_Resize,
    transform.BC_WGT_TransformGizmoGroup,
    transform.BC_OT_AddTransformGizmo,
    transform.BC_OT_RemoveTransformGizmo,
    transform.BC_GT_TransformCustomGizmo)


def register():
    for cls in classes:
        register_class(cls)

    shape.register()
    topbar.register()


def unregister():
    for cls in classes:
        unregister_class(cls)

    shape.unregister()
    topbar.unregister()
