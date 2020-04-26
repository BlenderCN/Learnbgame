import bpy
from bpy.types import Operator
from bpy.props import (StringProperty,
                       FloatProperty)
from .utils.text_to_draw import *
from .utils.fonctions import *


class SubrsurfModal(Operator):
    bl_idname = "object.subsurf_modal"
    bl_label = "Modal Subsurf"
 
    first_mouse_x = FloatProperty()
    mode = StringProperty()
 
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
        modal_speed = get_addon_preferences().modal_speed
        #change Position
        if event.type == 'UP_ARROW' and event.value=='PRESS':
            bpy.ops.object.modifier_move_up(modifier="Subsurf")
 
        if event.type == 'DOWN_ARROW' and event.value=='PRESS':
            bpy.ops.object.modifier_move_down(modifier="Subsurf")
 
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'} 
 
        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_x - event.mouse_x
            for obj in context.selected_objects:
                obj.modifiers["Subsurf"].levels = min(7 if event.shift else 2,-(delta/60)*modal_speed)
 
        #Levels Wheelmouse
        if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Subsurf"].levels += 1
 
        if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Subsurf"].levels -= 1  
 
        #Optimal display   
        if event.type == 'S' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Subsurf"].show_only_control_edges = False if obj.modifiers["Subsurf"].show_only_control_edges else True 
 
        #Open Subdiv
        if(hasattr(bpy.context.user_preferences.system, 'opensubdiv_compute_type')):
            if event.type == 'D' and event.value=='PRESS':
                for obj in context.selected_objects:
                    obj.modifiers["Subsurf"].use_opensubdiv = False if obj.modifiers["Subsurf"].use_opensubdiv else True
 
        if event.type == 'H' and event.value == 'PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Subsurf"].show_viewport = False if obj.modifiers["Subsurf"].show_viewport else True
 
        if event.type == 'A':
            act_obj = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT')
            for obj in context.selected_objects:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
 
            MPM.subsurf_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._subsurf_handle, 'WINDOW')
            bpy.context.scene.objects.active = act_obj
            bpy.ops.object.mode_set(mode=self.mode)
            return {'FINISHED'} 
 
        if event.type == 'LEFTMOUSE':
            MPM.subsurf_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._subsurf_handle, 'WINDOW')
            return {'FINISHED'}
 
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            MPM.subsurf_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._subsurf_handle, 'WINDOW')
            return {'CANCELLED'}
 
        if event.type == 'DEL' and event.value == 'PRESS':
            act_obj = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT')
            for obj in context.selected_objects:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_remove(modifier="Subsurf")
 
            MPM.subsurf_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._subsurf_handle, 'WINDOW')
            bpy.context.scene.objects.active = act_obj
            bpy.ops.object.mode_set(mode=self.mode)
            return {'FINISHED'} 
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            object = bpy.context.active_object
            self.subsurf_modifier = None
            MPM = context.window_manager.MPM
            MPM.subsurf_enabled = True
            self.mode = context.object.mode
 
            for obj in context.selected_objects:
                if obj.type not in {'MESH', 'CURVE'}:
                    obj.select = False
                    pass
 
                else:
                    subsurf = False
                    for mod in obj.modifiers:
                        if mod.type == "SUBSURF":
                            subsurf = True
 
                    if not subsurf:
                        obj.modifiers.new("Subsurf", "SUBSURF")
                        obj.modifiers["Subsurf"].levels = 2
                        obj.modifiers["Subsurf"].show_only_control_edges = True
                        if(hasattr(bpy.context.user_preferences.system, 'opensubdiv_compute_type')):
                            obj.modifiers["Subsurf"].use_opensubdiv = False
 
            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._subsurf_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
            self.first_mouse_x = event.mouse_x
 
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}