import bpy

from bpy.types import Operator

from ... __init__ import bl_info


class BC_OT_help_link(Operator):
    bl_idname = 'bc.help_link'
    bl_label = 'Help'
    bl_description = ('Visit HOps discord server for help\n'
                      '  Ctrl - Visit Documentation Website')

    def invoke(self, context, event):
        if not event.ctrl:
            bpy.ops.wm.url_open(url='https://discord.gg/ySRW6u9')

        else:
            bpy.ops.wm.url_open(url=bl_info['wiki_url'])

        return {"FINISHED"}
