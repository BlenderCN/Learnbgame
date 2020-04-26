import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from .utils.text_to_draw import *
from .utils.fonctions import *
 
 
class BooleanModal(Operator):
    bl_idname = "object.boolean_modal"
    bl_label = "Modal Boolean"
 
    mode = StringProperty()
 
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
 
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'} 
 
        #change Position
        if MPM.boolean_name:
            if event.type == 'UP_ARROW' and event.value=='PRESS':
                bpy.ops.object.modifier_move_up(modifier=MPM.boolean_name)
 
            if event.type == 'DOWN_ARROW' and event.value=='PRESS':
                bpy.ops.object.modifier_move_down(modifier=MPM.boolean_name)
 
 
            if event.type in {'GRLESS', 'LEFT_ARROW', 'RIGHT_ARROW'} and event.value =='PRESS':
                bool_list = get_modifier_list(context.active_object, 'BOOLEAN')
                prev_bool_obj = bpy.context.active_object.modifiers[MPM.boolean_name].object.name
                index = bool_list.index(MPM.boolean_name)
                if event.type == 'GRLESS' and event.shift or event.type == 'RIGHT_ARROW':
                    MPM.boolean_name = bool_list[index+1 if index != len(bool_list)-1 else 0]
                else:
                    MPM.boolean_name = bool_list[index-1 if index != 0 else -1]
                new_bool_obj = bpy.context.active_object.modifiers[MPM.boolean_name].object.name
                bpy.data.objects[prev_bool_obj].select=False
                bpy.data.objects[new_bool_obj].select=True
 
 
            if event.type == 'S' and event.value =='PRESS':
                bpy.context.object.modifiers[MPM.boolean_name].operation = 'UNION'
                
            elif event.type == 'D' and event.value =='PRESS':
                bpy.context.object.modifiers[MPM.boolean_name].operation = 'DIFFERENCE'
            
            elif event.type == 'F' and event.value =='PRESS':
                bpy.context.object.modifiers[MPM.boolean_name].operation = 'INTERSECT'
 
            elif event.type == 'A' and event.value == 'PRESS':
                bool_count= len(get_modifier_list(context.active_object, 'BOOLEAN'))
                act_obj = context.active_object
                bool_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects[0] != act_obj else bpy.context.selected_objects[1]
                apply_boolean(self, act_obj, bool_obj, bool_count)
 
                if bool_count == 1:
                    MPM.boolean_enabled = False
                    bool_obj.select=False
                    bpy.types.SpaceView3D.draw_handler_remove(self._boolean_handle, 'WINDOW')
 
                    return {'FINISHED'}
 
            if event.type == 'R' and event.value == 'PRESS':
                bool_count= len(get_modifier_list(context.active_object, 'BOOLEAN'))
                act_obj = context.active_object
                bool_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects[0] != act_obj else bpy.context.selected_objects[1]
                bpy.ops.object.mode_set(mode='OBJECT')
                prepare_reverse_bool(self, act_obj, bool_obj, bool_count)
 
                if bool_count == 1:
                    MPM.boolean_enabled = False
                    bool_obj.select=False
                    bpy.types.SpaceView3D.draw_handler_remove(self._boolean_handle, 'WINDOW')
 
                    return {'FINISHED'}
 
            if event.type == 'H' and event.value == 'PRESS':
                bpy.context.active_object.modifiers[MPM.boolean_name].show_viewport = False if bpy.context.active_object.modifiers[MPM.boolean_name].show_viewport else True
 
            if event.type == 'DEL' and event.value == 'PRESS':
                bool_list = get_modifier_list(context.active_object, 'BOOLEAN')
                if len(bool_list) > 1:
                    prev_bool_obj = bpy.context.active_object.modifiers[MPM.boolean_name].object.name
                    bpy.ops.object.modifier_remove(modifier=MPM.boolean_name)
                    MPM.boolean_name = get_modifier_list(context.active_object, 'BOOLEAN')[-1]
                    new_bool_obj = bpy.context.active_object.modifiers[MPM.boolean_name].object.name
                    bpy.data.objects[prev_bool_obj].select=False
                    bpy.data.objects[new_bool_obj].select=True
 
                else:
                    bpy.context.active_object.modifiers[MPM.boolean_name].object.select=False
                    bpy.ops.object.modifier_remove(modifier=MPM.boolean_name)
                    MPM.boolean_name = ""
                    MPM.boolean_enabled = False
                    bpy.types.SpaceView3D.draw_handler_remove(self._boolean_handle, 'WINDOW')
                    return {'FINISHED'}
 
        if event.type in {'RIGHTMOUSE', 'ESC', 'LEFTMOUSE'}:
            MPM.boolean_enabled = False
            bpy.context.active_object.modifiers[MPM.boolean_name].object.select=False
            bpy.types.SpaceView3D.draw_handler_remove(self._boolean_handle, 'WINDOW')
            return {'FINISHED'}
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.active_object.type == 'MESH':
                object = bpy.context.active_object
                MPM = context.window_manager.MPM
                MPM.boolean_enabled = True
                self.mode = context.object.mode
 
                bpy.ops.object.mode_set(mode='OBJECT')
 
                if len(context.selected_objects) == 1:
                    for mod in object.modifiers:
                        if mod.type== 'BOOLEAN':
                            if not mod.object:
                                bpy.ops.object.modifier_remove(modifier=mod.name)
 
                    is_boolean = False
                    for modifier in object.modifiers:
                        if modifier.type == "BOOLEAN":
                            is_boolean = True
 
                    if is_boolean:
                        mod_list = get_modifier_list(object, 'BOOLEAN')
                        if MPM.boolean_name not in mod_list:
                            MPM.boolean_name = mod_list[-1]
                        bool_object = object.modifiers[MPM.boolean_name].object.name
                        bpy.data.objects[bool_object].select=True
 
                    else:
                        self.report({'WARNING'}, "Need second object")
                        return {'CANCELLED'}
 
                else:
                    #Ref Object 
                    obj_bool_list = [obj for obj in context.selected_objects if obj != object and obj.type == 'MESH']
 
                    for mod in object.modifiers:
                        if mod.type== 'BOOLEAN':
                            if not mod.object:
                                bpy.ops.object.modifier_remove(modifier=mod.name)
 
                    for obj in obj_bool_list:
                        if "Bool_"+obj.name in [mod.name for mod in object.modifiers if mod.type == 'BOOLEAN']:
                            pass
 
                        else:
                            bool_name = "Bool_"+obj.name
                            object.modifiers.new(bool_name, 'BOOLEAN')
                            object.modifiers[bool_name].object = obj
                            object.modifiers[bool_name].operation = 'DIFFERENCE'
                            obj.draw_type = 'WIRE'
                            obj.select=False
 
                    MPM.boolean_name = "Bool_"+obj_bool_list[-1].name
 
                    for obj in obj_bool_list:
                        obj.select = False
                        obj.hide_render = True
                    obj_bool_list[-1].select = True
 
                args = (self, context)
                self._boolean_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
 
            else:
                self.report({'WARNING'}, "Active object is not a Mesh")
                return {'CANCELLED'}
 
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'FINISHED'}