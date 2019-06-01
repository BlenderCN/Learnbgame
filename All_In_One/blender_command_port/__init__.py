bl_info = {
    "name": "Blender Command Port",
    "description": "Command Port implementation for blender. "
                   "www.github.com/p4vv37/blender_command_port",
    "author": "Pawel Kowalski",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Data > Blender Command Port",
    "support": "COMMUNITY",
    "wiki_url": "www.github.com/p4vv37/blender_command_port",
    "category": "Learnbgame",
}

import bpy
from bpy.types import Panel

from .command_port import register as register_command_port
from .command_port import unregister as unregister_command_port
from .command_port import open_command_port
from .tools import close_command_port


class OpenCommandPortOperator(bpy.types.Operator):
    bl_idname = "wm.open_command_port"
    bl_label = "Open Port"

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def execute(self, context):
        open_command_port()
        return {'FINISHED'}


class CloseCommandPortOperator(bpy.types.Operator):
    bl_idname = "wm.close_command_port"
    bl_label = "Close Port"

    # noinspection PyMethodMayBeStatic
    def execute(self, context):
        close_command_port()
        return {'FINISHED'}


class BlenderCommandPortPanel(Panel):
    bl_label = 'Blender Command Port'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, 'bcp_queue_size')
        layout.prop(scene, 'bcp_timeout')
        layout.prop(scene, 'bcp_port')
        layout.prop(scene, 'bcp_buffersize')
        layout.prop(scene, 'bcp_max_connections')
        layout.prop(scene, 'bcp_return_result')
        layout.prop(scene, 'bcp_result_as_json')
        layout.prop(scene, 'bcp_redirect_output')
        row = layout.row()
        try:
            port_running = bpy.context.window_manager.keep_command_port_running
        except AttributeError:
            port_running = False

        if port_running:
            row.operator("wm.close_command_port")
        else:
            row.operator("wm.open_command_port")


def register():
    bpy.utils.register_class(OpenCommandPortOperator)
    bpy.utils.register_class(CloseCommandPortOperator)
    register_command_port()
    bpy.utils.register_class(BlenderCommandPortPanel)


def unregister():
    bpy.utils.unregister_class(OpenCommandPortOperator)
    bpy.utils.unregister_class(CloseCommandPortOperator)
    unregister_command_port()
    bpy.utils.unregister_class(BlenderCommandPortPanel)

