import bpy

from bpy.types import Operator

from ... import topbar
from ... utility import addon, active_tool, activate_by_name


class BC_OT_topbar_activate(Operator):
    bl_idname = 'bc.topbar_activate'
    bl_label = 'Activate BoxCutter'

    def execute(self, context):
        preference = addon.preference()

        if preference.cursor:
            context.window_manager.gizmo_group_type_ensure('bc.gizmogroup')
            context.window_manager.gizmo_group_type_ensure('bc.gridgizmo')

        if active_tool().idname != 'BoxCutter':
            activate_by_name('BoxCutter')

            if context.workspace.tools_mode == 'EDIT_MESH':
                topbar.change_prop(context, 'mode', 'KNIFE')

            else:
                topbar.change_prop(context, 'mode', 'CUT')

            self.report({'INFO'}, 'Activated BoxCutter')

            context.workspace.tools.update()

            return {'FINISHED'}

        elif preference.keymap.enable_surface_toggle:
            if preference.transform_gizmo:
                context.window_manager.gizmo_group_type_ensure('bc.transformgizmogroup')

            if preference.surface == 'OBJECT':
                preference.surface = 'CURSOR'
                preference.cursor = True
                context.window_manager.gizmo_group_type_ensure('bc.gizmogroup')
                context.window_manager.gizmo_group_type_ensure('bc.gridgizmo')

            else:
                preference.surface = 'OBJECT'
                preference.cursor = False
                context.window_manager.gizmo_group_type_unlink_delayed('bc.gizmogroup')
                context.window_manager.gizmo_group_type_unlink_delayed('bc.gridgizmo')

            if preference.surface == 'OBJECT':
                self.report({'INFO'}, 'Drawing from Object')

            else:
                self.report({'INFO'}, 'Drawing from Cursor')

            context.workspace.tools.update()

            return {'FINISHED'}

        else:
            return {'PASS_THROUGH'}
