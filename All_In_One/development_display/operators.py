import bpy
from bpy.props import *
from bpy.types import Operator

class DisplayClear(Operator):
    """"""
    bl_idname = "scene.display_clear"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear Display data"
    
    ##### POLL #####
    @classmethod
    def poll(cls, context):
        return hasattr(bpy.types.WindowManager, 'display')
    
    ##### EXECUTE #####
    def execute(self, context):
        bpy.types.WindowManager.display.clear()
        return {'FINISHED'}



class DisplayClearPlots(Operator):
    """"""
    bl_idname = "scene.display_clear_plots"
    bl_label = "Clear Plots"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear Display Plots"
    
    ##### POLL #####
    @classmethod
    def poll(cls, context):
        return hasattr(bpy.types.WindowManager, 'display')
    
    ##### EXECUTE #####
    def execute(self, context):
        bpy.types.WindowManager.display.plots.clear()
        bpy.types.WindowManager.display.tag_redraw_all_view3d()
        return {'FINISHED'}
