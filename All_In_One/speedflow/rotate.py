import bpy
from bpy.types import Operator
from bpy.props import (FloatProperty,
                       IntProperty)
from .utils.text_to_draw import *
from .utils.fonctions import *


class RotateModal(Operator):
    """Draw a line with the mouse"""
    bl_idname = "object.rotate_modal"
    bl_label = "Modal Rotate"
 
    first_mouse_x = IntProperty()
    first_value = FloatProperty()
 
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
        
 
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'} 
        
        if event.type == 'R' and event.value == 'PRESS':
            bpy.context.space_data.transform_orientation = 'LOCAL' if bpy.context.space_data.transform_orientation == 'GLOBAL' else 'GLOBAL'   
 
        elif event.type == 'MOUSEMOVE':
            delta = round((self.first_mouse_x - event.mouse_x)/80)
            a=context.object.rotation_euler
            if event.ctrl :
                a[self.axis]=-(delta*self.modal_speed)* 1.57079633/18 # 5
            elif event.shift :  
                a[self.axis]=-(delta*self.modal_speed)* 1.57079633/9 # 10
            else :  
                a[self.axis]=-(delta*self.modal_speed)* 1.57079633/2 # 45
         
            context.object.rotation_euler=a
         
        elif event.type == 'X':
            self.axis=0
        elif event.type == 'Y':
            self.axis=1
        elif event.type == 'Z':
            self.axis=2
        
        elif event.type == 'LEFTMOUSE':
            MPM.rotate_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._rotate_handle, 'WINDOW')
            bpy.context.space_data.transform_orientation = 'GLOBAL'
            return {'FINISHED'}
 
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            MPM.rotate_enabled = False
            bpy.context.space_data.transform_orientation = 'GLOBAL'
            bpy.types.SpaceView3D.draw_handler_remove(self._rotate_handle, 'WINDOW')
            return {'CANCELLED'}
 
        elif event.type in {'DEL', 'BACK_SPACE'}:
            MPM.rotate_enabled = False
            bpy.context.space_data.transform_orientation = 'GLOBAL'
            bpy.types.SpaceView3D.draw_handler_remove(self._rotate_handle, 'WINDOW')
            return {'CANCELLED'} 
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.axis=0
            MPM = context.window_manager.MPM
            self.modal_speed = get_addon_preferences().modal_speed
            MPM.rotate_enabled = True
            if context.object:
                self.first_mouse_x = event.mouse_x
                self.first_value = context.object.location.x
                bpy.context.space_data.transform_orientation = 'GLOBAL'
                context.window_manager.modal_handler_add(self)
                
                args = (self, context)
               
                self._rotate_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
     
                return {'RUNNING_MODAL'}
        
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}