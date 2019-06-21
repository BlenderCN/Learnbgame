import bpy

from bpy.types import Panel

from . import general, start_operation
from ... utility import addon, active_tool


class BC_PT_help(Panel):
    bl_label = 'Help'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = '.workspace'
    bl_options = {'HIDE_HEADER'}


    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'BoxCutter'

    def draw(self, context):
        layout = self.layout
