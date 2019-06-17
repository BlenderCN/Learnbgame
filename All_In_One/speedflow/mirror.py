import bpy
from bpy.types import Operator
from bpy.props import (StringProperty, 
                       FloatProperty,
                       BoolProperty)
from .utils.text_to_draw import *
from .utils.fonctions import *


class MirrorModal(Operator):
    bl_idname = "object.mirror_modal"
    bl_label = "Modal Mirror"
 
    x_axis = BoolProperty()
    y_axis = BoolProperty()
    z_axis = BoolProperty()
    clip_value = BoolProperty()
    merge_value = FloatProperty()
    mode = StringProperty()
 
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
        modifier = bpy.context.active_object.modifiers
 
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
 
        if MPM.mirror_name:
            #change Position
            if event.type == 'UP_ARROW' and event.value=='PRESS':
                bpy.ops.object.modifier_move_up(modifier=MPM.mirror_name)
 
            if event.type == 'DOWN_ARROW' and event.value=='PRESS':
                bpy.ops.object.modifier_move_down(modifier=MPM.mirror_name)
 
            if event.type in {'GRLESS', 'LEFT_ARROW', 'RIGHT_ARROW'} and event.value =='PRESS':
                mirror_list = get_modifier_list(context.active_object, 'MIRROR')
                mirror_obj = modifier[MPM.mirror_name].mirror_object if modifier[MPM.mirror_name].mirror_object else ""
                index = mirror_list.index(MPM.mirror_name)
                if event.type == 'GRLESS' and event.shift or event.type == 'RIGHT_ARROW':
                    MPM.mirror_name = mirror_list[index+1 if index != len(mirror_list)-1 else 0]
                else:
                    MPM.mirror_name = mirror_list[index-1 if index != 0 else -1]
                if modifier[MPM.mirror_name].mirror_object:
                    if mirror_obj:
                        mirror_obj.select=False
                    modifier[MPM.mirror_name].mirror_object.select=True
                else:
                    if mirror_obj:
                        mirror_obj.select=False
 
            if event.type == 'F' and event.value == 'PRESS':
                mirror = [mod.name for mod in context.active_object.modifiers if mod.type == 'MIRROR']
                mirror_obj = modifier[MPM.mirror_name].mirror_object if modifier[MPM.mirror_name].mirror_object else ""
                bpy.context.active_object.modifiers.new("Mirror", "MIRROR")
                MPM.mirror_name = get_modifier_list(context.active_object, 'MIRROR')[-1]
                modifier[MPM.mirror_name].use_x = True
                modifier[MPM.mirror_name].use_y = False
                modifier[MPM.mirror_name].use_z = False
                modifier[MPM.mirror_name].use_clip = True
                modifier[MPM.mirror_name].use_mirror_merge = True
                if mirror_obj:
                    mirror_obj.select=False
 
            #Choose Axes 
            if event.type == 'X' and event.value == 'PRESS':
                if event.shift:
                    modifier[MPM.mirror_name].use_x = True
                elif event.alt:
                    modifier[MPM.mirror_name].use_x = False 
                else:     
                    modifier[MPM.mirror_name].use_x = True  
                    modifier[MPM.mirror_name].use_y = False  
                    modifier[MPM.mirror_name].use_z = False  
 
            elif event.type == 'Y' and event.value == 'PRESS':
                if event.shift:
                    modifier[MPM.mirror_name].use_y = True
                elif event.alt:
                    modifier[MPM.mirror_name].use_y = False 
                else:
                    modifier[MPM.mirror_name].use_x = False
                    modifier[MPM.mirror_name].use_y = True  
                    modifier[MPM.mirror_name].use_z = False 
 
            elif event.type == 'Z' and event.value == 'PRESS':
                if event.shift:
                    modifier[MPM.mirror_name].use_z = True
                elif event.alt:
                    modifier[MPM.mirror_name].use_z = False 
                else:
                    modifier[MPM.mirror_name].use_x = False
                    modifier[MPM.mirror_name].use_y = False  
                    modifier[MPM.mirror_name].use_z = True  
 
            #Mirror Object
            if event.type == 'S' and event.value == 'PRESS':
                act_obj = context.active_object
                if modifier[MPM.mirror_name].mirror_object:
                    modifier[MPM.mirror_name].mirror_object.select=False
                    modifier[MPM.mirror_name].mirror_object = None
                    modifier[MPM.mirror_name].name = "Mirror"
                    MPM.mirror_name = "Mirror"
                elif not modifier[MPM.mirror_name].mirror_object:
                    bpy.ops.object.empty_add()
                    empty = context.active_object
                    bpy.context.scene.objects.active = act_obj
                    act_obj.select=True
                    act_obj.modifiers[MPM.mirror_name].mirror_object = empty
                    act_obj.modifiers[MPM.mirror_name].name = "Mirror_" + empty.name
                    MPM.mirror_name = "Mirror_" + empty.name
 
            #Clip
            if event.type == 'C' and event.value=='PRESS':
                modifier[MPM.mirror_name].use_clip = False if modifier[MPM.mirror_name].use_clip else True
 
            #Merge      
            if event.type == 'D' and event.value=='PRESS':
                modifier[MPM.mirror_name].use_mirror_merge = False if modifier[MPM.mirror_name].use_mirror_merge else True              
 
            if event.type == 'A' and event.value=='PRESS':
                mirror_count = len(get_modifier_list(context.active_object, 'MIRROR'))
                mirror_obj = modifier[MPM.mirror_name].mirror_object if modifier[MPM.mirror_name].mirror_object else ""
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=MPM.mirror_name)
                if mirror_count > 1:
                    MPM.mirror_name = get_modifier_list(context.active_object, 'MIRROR')[-1]
                    if modifier[MPM.mirror_name].mirror_object:
                        if mirror_obj:
                            mirror_obj.select=False
                        modifier[MPM.mirror_name].mirror_object.select=True
                    else:
                        if mirror_obj:
                            mirror_obj.select=False
                    bpy.ops.object.mode_set(mode=self.mode)
 
                if mirror_count == 1:
                    MPM.mirror_enabled = False
                    if mirror_obj:
                        mirror_obj.select=False
                    MPM.mirror_name = ""
                    bpy.types.SpaceView3D.draw_handler_remove(self._mirror_handle, 'WINDOW')
                    bpy.ops.object.mode_set(mode=self.mode)
                    return {'FINISHED'} 
 
            if event.type == 'H' and event.value == 'PRESS':
                bpy.context.active_object.modifiers[MPM.mirror_name].show_viewport = False if bpy.context.active_object.modifiers[MPM.mirror_name].show_viewport else True
 
            if event.type == 'DEL' and event.value == 'PRESS':
                mirror_list = get_modifier_list(context.active_object, 'MIRROR')
                mirror_obj = modifier[MPM.mirror_name].mirror_object if modifier[MPM.mirror_name].mirror_object else ""
                bpy.ops.object.modifier_remove(modifier=MPM.mirror_name)
                if len(mirror_list) > 1:
                    if mirror_obj:
                        mirror_obj.select=False
                    MPM.mirror_name = get_modifier_list(context.active_object, 'MIRROR')[-1]
                    if modifier[MPM.mirror_name].mirror_object:
                        modifier[MPM.mirror_name].mirror_object.select=True
 
                else:
                    MPM.mirror_enabled = False
                    if mirror_obj:
                        mirror_obj.select=False
                    bpy.types.SpaceView3D.draw_handler_remove(self._mirror_handle, 'WINDOW')
                    return {'FINISHED'} 
 
 
        if event.type == 'LEFTMOUSE':
            MPM.mirror_enabled = False
            if bpy.context.active_object.modifiers[MPM.mirror_name].mirror_object:
                bpy.context.active_object.modifiers[MPM.mirror_name].mirror_object.select=False
 
            bpy.types.SpaceView3D.draw_handler_remove(self._mirror_handle, 'WINDOW')
            return {'FINISHED'}
 
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            MPM.mirror_enabled = False
            if bpy.context.active_object.modifiers[MPM.mirror_name].mirror_object:
                bpy.context.active_object.modifiers[MPM.mirror_name].mirror_object.select=False
 
            modifier[MPM.mirror_name].use_x = self.x_axis
            modifier[MPM.mirror_name].use_y = self.y_axis
            modifier[MPM.mirror_name].use_z = self.z_axis
            bpy.types.SpaceView3D.draw_handler_remove(self._mirror_handle, 'WINDOW')
            return {'CANCELLED'}
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.object.type == 'MESH':
                MPM = context.window_manager.MPM
                act_obj = context.active_object
                self.mode = context.object.mode
                MPM.mirror_enabled = True
                mirror = [mod.name for mod in act_obj.modifiers if mod.type == 'MIRROR']
 
                if len(context.selected_objects) == 1:
                    if mirror:
                        MPM.mirror_name = mirror[-1]
                        if act_obj.modifiers[MPM.mirror_name].mirror_object:
                            act_obj.modifiers[MPM.mirror_name].mirror_object.select=True
 
                    else:
                        act_obj.modifiers.new("Mirror", "MIRROR")
                        MPM.mirror_name = "Mirror"
                        act_obj.modifiers["Mirror"].use_x = True
                        act_obj.modifiers["Mirror"].use_y = False
                        act_obj.modifiers["Mirror"].use_z = False
                        act_obj.modifiers["Mirror"].use_clip = True
                        act_obj.modifiers["Mirror"].use_mirror_merge = True
 
                else:
                    mirror_obj = context.selected_objects[0] if context.selected_objects[0] != act_obj else context.selected_objects[1]
 
                    if mirror and "Mirror_" + mirror_obj.name in mirror:
                        MPM.mirror_name = "Mirror_" + mirror_obj.name
 
                    else:
                        act_obj.modifiers.new("Mirror_" + mirror_obj.name, "MIRROR")
                        MPM.mirror_name = "Mirror_" + mirror_obj.name
                        act_obj.modifiers[MPM.mirror_name].mirror_object = mirror_obj
                        act_obj.modifiers[MPM.mirror_name].use_x = True
                        act_obj.modifiers[MPM.mirror_name].use_y = False
                        act_obj.modifiers[MPM.mirror_name].use_z = False
                        act_obj.modifiers[MPM.mirror_name].use_clip = True
                        act_obj.modifiers[MPM.mirror_name].use_mirror_merge = True
 
                args = (self, context)
                self._mirror_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
                self.x_axis = bpy.context.object.modifiers[MPM.mirror_name].use_x 
                self.y_axis = bpy.context.object.modifiers[MPM.mirror_name].use_y 
                self.z_axis = bpy.context.object.modifiers[MPM.mirror_name].use_z           
                self.clip_value = bpy.context.object.modifiers[MPM.mirror_name].use_clip           
                self.merge_value = bpy.context.object.modifiers[MPM.mirror_name].use_mirror_merge
 
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
 
            else:
                self.report({'WARNING'}, "Active object is not a Mesh")
                return {'CANCELLED'}
 
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'FINISHED'}