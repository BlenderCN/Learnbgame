import bpy
from console_python import add_scrollback

from .bc_command_dispatch import (
    in_scene_commands,
    in_search_commands,
    in_sverchok_commands,
    in_core_dev_commands,
    in_modeling_tools,
    in_upgrade_commands,
    in_bpm_commands,
    in_fast_ops_commands)

from .bc_utils import set_keymap


history_append = bpy.ops.console.history_append
addon_enable = bpy.ops.preferences.addon_enable


def print_most_useful():
    content = '''\

for full verbose descriptor use -man

command    |  description
-----------+----------------
tt | tb    |  turntable / trackball nav.
cen        |  centers 3d cursor
cenv       |  centers 3d cursor, aligns views to it
cento      |  centers to selected
endswith!  |  copy current console line if ends with exclm.
x?bpy      |  search blender python for x
x?bs       |  search blenderscripting.blogspot for x
x?py       |  search python docs for x
x?se       |  search B3D StackExchange
x??se      |  regular StackExchange search
vtx, xl    |  enable or trigger tinyCAD vtx (will download)
ico        |  enables icon addon in texteditor panel (Dev)
123        |  use 1 2 3 to select vert, edge, face
-img2p     |  enabled image to plane import addon
-or2s      |  origin to selected.
-dist      |  gives local distance between two selected verts
-gist -o x |  uploads all open text views as x to anon gist.
-debug     |  dl + enable extended mesh index visualiser. it's awesome.
--sort     |  sorting operator: sorts open edgeloop, by index handy for polyline export
-----------+----------------------------------------------------------
-idxv          |  enable by shortcut name (user defined)
enable x       |  where 'x' is package name or folder name
v2rdim         |  sets render dimensions to current strip.
fc             |  fcurrent -> end.frame
gif dir        |  make animated gif of *.png sequence found in dir's path
nodeview white |  set bg col of nodeview
----------------------------------------------------------------------
'''

    add_scrollback(content, 'OUTPUT')


class TextSyncOps(bpy.types.Operator):

    bl_idname = "text.text_upsync"
    bl_label = "Upsyncs Text from disk changes"

    def execute(self, context):
        text_block = context.edit_text
        bpy.ops.text.resolve_conflict(resolution='RELOAD')
        return{'FINISHED'}


class ConsoleDoAction(bpy.types.Operator):
    bl_label = "ConsoleDoAction"
    bl_idname = "console.do_action"

    def execute(self, context):
        m = bpy.context.space_data.history[-1].body
        m = m.strip()

        DONE = {'FINISHED'}
        if any([
            in_scene_commands(context, m),
            in_search_commands(context, m),
            in_sverchok_commands(context, m),
            in_core_dev_commands(context, m),
            in_modeling_tools(context, m),
            in_upgrade_commands(context, m),
            in_bpm_commands(context, m),
            in_fast_ops_commands(context, m)
        ]):
            return DONE

        elif m == '-ls':
            print_most_useful()
            return DONE

        elif m == 'cl':
            bpy.ops.console.clear()
            return DONE

        return {'FINISHED'}


class ConsoleShortCutButtons(bpy.types.Operator):
    bl_label = "ConsoleEditModePushButton"
    bl_idname = "wm.set_editmode_shortcuts"

    def execute(self, context):
        set_keymap()
        return {'FINISHED'}

classes = [TextSyncOps, ConsoleDoAction, ConsoleShortCutButtons]
register, unregister = bpy.utils.register_classes_factory(classes)

