import bpy

from bpy.utils import register_class, unregister_class
from bpy.utils.toolsystem import ToolDef

from .. utility import addon

from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools


@ToolDef.from_fn
def boxcutter():
    def draw_settings(context, layout, tool):
        running = context.window_manager.bc.running
        option = tool.operator_properties('bc.draw_shape')

        layout.prop(option, 'mode', expand=True, text='')

        layout.separator()

        row = layout.row()
        row.enabled = not running
        row.prop(option, 'shape', expand=True, text='')

        layout.separator()

        layout.prop(option, 'operation', expand=True, text='')
        layout.separator()
        layout.prop(option, 'behavior', expand=True)
        layout.separator()
        # layout.prop(option, 'axis', expand=True)
        # layout.separator()
        layout.prop(option, 'origin', expand=True, text='')
        layout.separator()
        # layout.prop(option, 'mirror', text='', icon='MOD_MIRROR')
        # layout.separator()

        row = layout.row()
        row.enabled = not running
        row.prop(option, 'align_to_view', text='', icon='VIEW_ORTHO' if option.align_to_view else 'VIEW_PERSPECTIVE')

        row = layout.row()
        row.enabled = not running
        row.prop(option, 'expand', text='', icon='ORIENTATION_NORMAL')

        layout.prop(option, 'live', text='', icon='PLAY' if not option.live else 'PAUSE')

        layout.separator()
        layout.popover(panel='bc.settings', text='', icon='PREFERENCES')

    return dict(
        text = 'BoxCutter',
        icon='ops.transform.resize',
        widget = None,
        operator = 'bc.draw_shape',
        keymap = None,
        draw_settings = draw_settings)


def register():
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

    modes = ('OBJECT', 'EDIT_MESH')
    space_type = 'VIEW_3D'
    tool_def = boxcutter

    for context_mode in modes:
        view3d_tools._tools[context_mode].append(None) # adds a separator, need a safe way to remove?
                                                       # ignoring for now

        cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)

        tools = cls._tools[context_mode]
        tools.append(tool_def)


    addon.log(value='Added toolbar buttons')


def unregister():
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

    modes = ('OBJECT', 'EDIT_MESH')
    space_type = 'VIEW_3D'
    tool_def = boxcutter

    for context_mode in modes:
        try:
            cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)

            tools = cls._tools[context_mode]
            tools.remove(tool_def)

        except:
            addon.log(trace=True)

    addon.log(value='Removed toolbar buttons')
