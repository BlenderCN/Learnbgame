import os

import bpy

from bpy.utils import register_class, unregister_class
from bpy.utils.toolsystem import ToolDef
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools

from . utility import addon, active_tool


def change_prop(context, prop, value):
    for tool in context.workspace.tools:
        if tool.idname == 'BoxCutter':
            setattr(tool.operator_properties('bc.draw_shape'), prop, value)

    context.workspace.tools.update()


def change_mode_behavior(ot, context):
    bc = context.window_manager.bc

    if not context.window_manager.bc.running:
        if ot.shape_type == 'BOX':
            change_prop(context, 'origin', 'CORNER' if ot.shape_type in 'BOX' else 'CENTER')
        elif ot.shape_type == 'CIRCLE':
            change_prop(context, 'origin', 'CENTER')
        elif ot.shape_type == 'CUSTOM':
            bc.collection = bc.stored_collection
            bc.shape = bc.stored_shape


def change_mode(ot, context):
    if not context.window_manager.bc.running:
        if ot.mode == 'KNIFE':
            change_prop(context, 'shape_type', 'BOX')
            change_mode_behavior(ot, context)


def update_operator(ot, context):
    if active_tool().idname == 'BoxCutter':

        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                ot.tool = tool
                prop = tool.operator_properties('bc.draw_shape')
                ot.mode = prop.mode
                ot.shape_type = prop.shape_type
                ot.operation = prop.operation
                ot.behavior = prop.behavior
                ot.axis = prop.axis
                ot.origin = prop.origin
                ot.align_to_view = prop.align_to_view
                ot.live = prop.live
                ot.active_only = prop.active_only

                return True

    else:
        return False


@ToolDef.from_fn
def boxcutter():
    def draw_settings(context, layout, tool):
        bc = context.window_manager.bc
        preference = addon.preference()
        option = tool.operator_properties('bc.draw_shape')

        if context.space_data.type != 'PROPERTIES':
            row = layout.row(align=True)
            row.prop(option, 'mode', text='', expand=True, icon_only=True)

            if preference.display.mode_label:
                box = row.box()
                box.ui_units_x = 2.8
                box.scale_y = 0.5
                box.label(text=option.mode.title())

            if preference.display.topbar_pad:
                for _ in range(preference.display.padding):
                    layout.separator()

            icons = {
                'BOX': 'MESH_PLANE',
                'CIRCLE': 'MESH_CIRCLE',
                'NGON': 'MOD_SIMPLIFY',
                'CUSTOM': 'FILE_NEW'}

            row = layout.row(align=True)

            row.prop(option, 'shape_type', expand=True, text='')
            row.popover(panel='BC_PT_shape', text='', icon=icons[option.shape_type])

            if preference.display.shape_label:
                box = row.box()
                box.ui_units_x = 3.0
                box.scale_y = 0.5
                box.label(text=option.shape_type.title())

            if preference.display.topbar_pad:
                for _ in range(preference.display.padding):
                    layout.separator()

            row = layout.row(align=True)
            row.prop(bc, 'start_operation', expand=True, icon_only=True)

            icons = {
                'NONE': 'LOCKED',
                'DRAW': 'GREASEPENCIL',
                'EXTRUDE': 'ORIENTATION_NORMAL',
                'OFFSET': 'MOD_OFFSET',
                'MOVE': 'RESTRICT_SELECT_ON',
                #'ROTATE': 'DRIVER_ROTATIONAL_DIFFERENCE',
                #'SCALE': 'FULLSCREEN_EXIT',
                'ARRAY': 'MOD_ARRAY',
                'SOLIDIFY': 'MOD_SOLIDIFY',
                'BEVEL': 'MOD_BEVEL',
                'MIRROR': 'MOD_MIRROR'}

            row.popover(panel='BC_PT_operation', text='', icon=icons[option.operation])

            if preference.display.operation_label:
                box = row.box()
                box.ui_units_x = 3.5
                box.scale_y = 0.5
                lock_label = 'Locked' if bc.running else 'Default'
                box.label(text=option.operation.title() if option.operation != 'NONE' else lock_label)

            icons = {
                'OBJECT': 'OBJECT_DATA',
                'CURSOR': 'PIVOT_CURSOR',
                'CENTER': 'VIEW_PERSPECTIVE'}

            if preference.display.topbar_pad:
                for _ in range(preference.display.padding):
                    layout.separator()

            for _ in range(preference.display.middle_pad):
                layout.separator()

            row = layout.row(align=True)
            row.popover(panel='BC_PT_surface', text='', icon=icons[preference.surface])

            if preference.display.surface_label:
                box = row.box()
                box.ui_units_x = 3.25
                box.scale_y = 0.5
                box.label(text=preference.surface.title() if preference.surface != 'CENTER' else 'World')

            if preference.display.snap:
                layout.separator()

                row = layout.row(align=True)
                row.prop(preference.behavior, 'snap', text='', icon=F'SNAP_O{"N" if preference.behavior.snap else "FF"}')

                row.popover('BC_PT_snap', text='', icon='SNAP_GRID')


            if preference.display.topbar_pad and preference.display.pad_menus:
                padding = preference.display.padding

                if not preference.display.destructive_menu:
                    padding = 0

                for _ in range(padding):
                    layout.separator()

            if preference.display.destructive_menu:
                row = layout.row(align=True)
                row.prop(preference.keymap, 'allow_selection', text='', icon='RESTRICT_SELECT_ON' if not preference.keymap.allow_selection else 'RESTRICT_SELECT_OFF')
                sub = row.row(align=True)
                sub.active = context.workspace.tools_mode == 'OBJECT'
                sub.prop(option, 'behavior', text='')
                sub2 = sub.row(align=True)
                sub2.enabled = sub.active
                sub2.operator('bc.apply_modifiers', text='', icon='FILE_TICK')

            if preference.display.topbar_pad and preference.display.pad_menus:
                for _ in range(preference.display.padding):
                    layout.separator()

            row = layout.row(align=True)
            row.popover(panel='BC_PT_settings', text='', icon='PREFERENCES')
            row.prop(option, 'live', text='', icon='PLAY' if not option.live else 'PAUSE')


    return dict(
        idname="BoxCutter",
        label="BoxCutter",
        icon=os.path.join(os.path.dirname(__file__), '..', 'icons', 'toolbar'),
        widget = None,
        keymap = '3D View Tool: BoxCutter',
        draw_settings = draw_settings)


def register():
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    from bl_keymap_utils.io import keyconfig_init_from_data

    modes = ('OBJECT', 'EDIT_MESH')
    space_type = 'VIEW_3D'

    for context_mode in modes:
        view3d_tools._tools[context_mode].append(None)

        cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)

        tools = cls._tools[context_mode]
        tools.append(boxcutter)


def unregister():
    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

    modes = ('OBJECT', 'EDIT_MESH')
    space_type = 'VIEW_3D'

    for context_mode in modes:
        cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)

        tools = cls._tools[context_mode]
        tools.remove(boxcutter)

        if tools[-1] == None:
            del tools[-1]
