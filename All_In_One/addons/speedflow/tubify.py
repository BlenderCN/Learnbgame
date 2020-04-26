import bpy
from bpy.types import Operator
from bpy.props import (StringProperty, 
                       IntProperty, 
                       FloatProperty,
                       BoolProperty,
                       FloatVectorProperty,
                       EnumProperty
                       )
from .utils.text_to_draw import *
from .utils.fonctions import *


class TubifyModal(Operator):
    bl_idname = "object.tubify_modal"
    bl_label = "Tubify"
 
    first_mouse_x = IntProperty()
    choose_profile = BoolProperty(default=False)
    bevel_depth = FloatProperty()
    reso_u = IntProperty()
    reso_v= IntProperty()
    profile = BoolProperty(default=False)
    profile_reso = IntProperty()
    profile_scale = FloatVectorProperty(default=(1, 1, 1))
    action_enabled = EnumProperty(
            items=(('depth', "depth", ""),
                   ('reso_u', "reso_u", ""),
                   ('reso_v', "reso_v", ""),
                   ('free', "free", "")),
                   default='depth'
                   )
    poly_bezier = EnumProperty(
            items=(('poly', "poly", ""),
                   ('bezier', "bezier", "")),
                   default='bezier'
                   )
    input = StringProperty()
    slow_down = BoolProperty(default=False)


#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------              
 
    def convert_as_curve(self, obj):
        bpy.context.scene.objects.active = obj
        bpy.ops.object.convert(target='CURVE')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type='BEZIER')
        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        bpy.ops.object.mode_set(mode='OBJECT') 

#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------              

    def check_mesh_validity(self):
        objs = []
        for obj in bpy.context.selected_objects:
            if obj.type == 'CURVE':
                objs.append(obj)
            elif obj.type == 'MESH':
                faces = [face for face in obj.data.polygons]  
     
                if not faces:
                    objs.append(obj)
     
        return objs

#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------              

    def get_input_value(self, value):
        if value == "-":
            if self.input.startswith("-"):
                pass
            else:
                self.input = "-" + self.input
        elif value == "+":
            if self.input.startswith("-"):
                self.input = self.input.split("-")[-1]
        else:
            self.input += value
            
#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------              
    
    def apply_input(self):
        if self.action_enabled == 'depth':
            if self.profile:
                for i in range(3):
                    self.act_obj.data.bevel_object.scale[i] = self.profile_scale[i] * (float(self.input)/self.profile_scale[i])
                    self.profile_scale[i] = self.profile_scale[i] * (float(self.input)/self.profile_scale[i])
            else:
                for obj in bpy.context.selected_objects:
                    obj.data.bevel_depth = float(self.input)
         
                self.bevel_depth = float(self.input)
         
        elif self.action_enabled == 'reso_u':
            if int(self.input) < 1:
                self.input = "1"
         
            if self.profile:
                self.act_obj.data.resolution_u = int(self.input)
         
            else:
                for obj in bpy.context.selected_objects:
                    obj.data.resolution_u = int(self.input)
         
            self.reso_u = int(self.input)
         
        elif self.action_enabled == 'reso_v':
            if int(self.input) < 1:
                self.input = "1"
         
            if self.profile:
                self.act_obj.data.bevel_object.data.resolution_u = int(self.input)
                self.profile_reso = int(self.input)
         
            else:
                for obj in bpy.context.selected_objects:
                    obj.data.bevel_resolution = int(self.input)
                self.reso_v = int(self.input)

#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------              

    def update_properties(self):
        if self.action_enabled == 'depth':
            if self.profile:
                for i in range(3):
                    self.profile_scale[i] = self.act_obj.data.bevel_object.scale[i]
            else:
                self.bevel_depth = self.act_obj.data.bevel_depth
         
        elif self.action_enabled == 'reso_u':
            self.reso_u = self.act_obj.data.resolution_u
         
        elif self.action_enabled == 'reso_v':
            if self.profile:
                self.profile_reso = self.act_obj.data.bevel_object.data.resolution_u 
            else:
                self.reso_v = self.act_obj.data.bevel_resolution
        
#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------
 
    def update_values(self):
        if self.action_enabled == 'depth':
            if self.profile:
                for i in range(3):
                    self.act_obj.data.bevel_object.scale[i] = self.profile_scale[i]
            else:
                for obj in bpy.context.selected_objects:
                    obj.data.bevel_depth = self.bevel_depth
 
        elif self.action_enabled == 'reso_u':
            for obj in bpy.context.selected_objects:
                obj.data.resolution_u = self.reso_u
 
        elif self.action_enabled == 'reso_v':
            if self.profile:
                self.act_obj.data.bevel_object.data.resolution_u = self.profile_reso
            else:
                for obj in bpy.context.selected_objects:
                    obj.data.bevel_resolution = self.reso_v
 
#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------

 
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
        input_list = ['0', '1', '2', '3', '4','5', '6', '7', '8', '9', '-', '+', '.'] 
        

        if event.unicode in input_list:
            self.get_input_value(event.unicode)
        
        #---------------------------------
        # Mode Input
        #---------------------------------
        if self.input:
            if event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':
                
                self.apply_input()

                self.input = ""
                self.action_enabled = 'free'        
                self.first_mouse_x = event.mouse_x    
        
        
        elif event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':
            if self.choose_profile:
                return {'PASS_THROUGH'} 
            else:
                if self.action_enabled in {'depth', 'reso_u', 'reso_v'}:
                    self.update_properties()
                    self.action_enabled = 'free'
                    self.first_mouse_x = event.mouse_x
                else:    
                    self.profile = False
                    MPM.tubify_enabled = False
                    bpy.types.SpaceView3D.draw_handler_remove(self._tubify_handle, 'WINDOW')
                    return {'CANCELLED'}
            
        
        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'} 
        
        #---------------------------------
        # Mode Depth
        #---------------------------------
        if event.type == 'S' and event.value == 'PRESS':
            if self.input:
                self.apply_input()
                self.input = ""
            else:
                self.update_properties()
            self.action_enabled = 'depth'
            self.first_mouse_x = event.mouse_x 
        
        #---------------------------------
        # Mode Reso_U
        #---------------------------------
        if event.type == 'D' and event.value == 'PRESS':
            if self.input:
                self.apply_input()
                self.input = ""
            else:
                self.update_properties()
            self.action_enabled = 'reso_u'
            self.first_mouse_x = event.mouse_x 
            
        #---------------------------------
        # Mode Reso_V
        #---------------------------------
        if event.type == 'F' and event.value == 'PRESS':
            if self.input:
                self.apply_input()
                self.input = ""
            else:
                self.update_properties()
            self.action_enabled = 'reso_v'
            self.first_mouse_x = event.mouse_x
        
        #---------------------------------
        # Setup Values
        #---------------------------------
        if self.pref_tool == 'pen':
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'}
            
            if event.type == 'LEFT_SHIFT' or event.type == 'RIGHT_SHIFT':
                if event.value == 'PRESS':
                    if not self.slow_down:
                        self.first_mouse_x = event.mouse_x
                        self.update_properties()
                        self.slow_down = True
         
                elif event.value == 'RELEASE':
                    self.first_mouse_x = event.mouse_x
                    self.update_properties()
                    self.slow_down = False
        
            if event.type == 'MOUSEMOVE' and not self.input:
                if self.choose_profile:
                    obj = context.active_object
                    if obj.type != 'CURVE':
                        return {'PASS_THROUGH'}
                    else:
                        if obj != self.act_obj:
                            bpy.context.scene.objects.active = self.act_obj
                            self.act_obj.select = True
                            self.profile_scale = obj.scale
                            self.first_mouse_x = event.mouse_x
                            self.act_obj.data.bevel_object = obj
                            self.choose_profile = False
                            self.action_enabled = 'free'
                            self.profile = True
                else:
                    delta = (self.first_mouse_x - event.mouse_x) / 8 if event.shift else self.first_mouse_x - event.mouse_x
                    
                    if self.action_enabled == 'depth':
                        if self.profile:
                            for i in range(3):
                                self.act_obj.data.bevel_object.scale[i] = self.profile_scale[i] + min(10, -(delta/500)*self.modal_speed)
                        else:
                            for obj in context.selected_objects:
                                obj.data.bevel_depth = self.bevel_depth + min(10, -(delta/500)*self.modal_speed)
                                
                    elif self.action_enabled == 'reso_u':
                        if self.profile:
                            self.act_obj.data.resolution_u = self.reso_u + min(50,-(delta/60)*self.modal_speed)
                        else:
                            for obj in context.selected_objects:
                                obj.data.resolution_u = self.reso_u + min(50,-(delta/60)*self.modal_speed)
                                
                    elif self.action_enabled == 'reso_v':
                        if self.profile:
                            self.act_obj.data.bevel_object.data.resolution_u = self.profile_reso + min(50,-(delta/60)*self.modal_speed) 
                        else:
                            for obj in context.selected_objects:
                                obj.data.bevel_resolution = self.reso_v + min(50,-(delta/60)*self.modal_speed)

        elif self.pref_tool == 'mouse':
            if self.action_enabled == 'free' and event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'}
            
            elif event.type == 'MOUSEMOVE' and self.choose_profile:
                obj = context.active_object
                if obj.type != 'CURVE':
                    return {'PASS_THROUGH'}
                else:
                    if obj != self.act_obj:
                        bpy.context.scene.objects.active = self.act_obj
                        self.act_obj.select = True
                        self.profile_scale = obj.scale
                        self.first_mouse_x = event.mouse_x
                        self.act_obj.data.bevel_object = obj
                        self.choose_profile = False
                        self.action_enabled = 'free'
                        self.profile = True
            
            else:
                value = 0
                if event.type == 'WHEELUPMOUSE':
                    if self.action_enabled == 'depth':
                        value = 0.01 if event.shift else 0.1
                    else:
                        value = 1
                elif event.type == 'WHEELDOWNMOUSE':
                    if self.action_enabled == 'depth':
                        value = -0.01 if event.shift else -0.1
                    else:
                        value = -1

                if self.action_enabled == 'depth':
                    if self.profile:
                        for i in range(3):
                            self.act_obj.data.bevel_object.scale[i] += value
                    else:
                        for obj in context.selected_objects:
                            obj.data.bevel_depth += value
                
                elif self.action_enabled == 'reso_u':
                    if self.profile:
                        self.act_obj.data.resolution_u += value
                    else:
                        for obj in context.selected_objects:
                            obj.data.resolution_u += value
                
                elif self.action_enabled == 'reso_v':
                    if self.profile:
                        self.act_obj.data.bevel_object.data.resolution_u += value 
                    else:
                        for obj in context.selected_objects:
                            obj.data.bevel_resolution += value                 
        
        #---------------------------------
        # Use Cyclic
        #---------------------------------
        if event.type == 'G' and event.value == 'PRESS':
            if self.profile:
                self.act_obj.data.splines[0].use_cyclic_u = False if self.act_obj.data.splines[0].use_cyclic_u else True
            else:
                for obj in context.selected_objects:
                    obj.data.splines[0].use_cyclic_u = False if obj.data.splines[0].use_cyclic_u else True
        
        #---------------------------------
        # Mode Select Profil
        #---------------------------------
        if event.type == 'Z' and event.value == 'PRESS':
            if self.choose_profile:
                # si l'objet actif n'est plus le meme quand in clique sur rmb ou esc, on remet les objets precedents
                if bpy.context.active_object != self.act_obj:
                    bpy.context.active_object.select = False
                    self.act_obj.select = True
                    bpy.context.scene.objects.active = self.act_obj
                    self.act_obj.data.bevel_object.select = True
            
            self.choose_profile = False if self.choose_profile else True
        
        #---------------------------------
        # Convert Curve To Mesh
        #---------------------------------
        if event.type == 'A':
            if self.profile:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.convert(target='MESH')
            else:   
                for obj in context.selected_objects:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.convert(target='MESH')
                bpy.context.scene.objects.active = self.act_obj
            MPM.tubify_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._tubify_handle, 'WINDOW')
            return {'FINISHED'} 
        
        #---------------------------------
        # Add Edge Split Modifier
        #---------------------------------
        if event.type == 'E' and event.value == 'PRESS':
            if self.profile:
                edge_split = False
                for mod in self.act_obj.modifiers:
                    if mod.type == 'EDGE_SPLIT':
                        edge_split = True
                if edge_split:
                    bpy.ops.object.modifier_remove(modifier="EdgeSplit")
 
                else:
                    self.act_obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
                    self.act_obj.modifiers["EdgeSplit"].split_angle = 1.0472
            else:  
                for obj in context.selected_objects:
                    edge_split = False
                    for mod in obj.modifiers:
                        if mod.type == 'EDGE_SPLIT':
                            edge_split = True
                    if edge_split:
                        bpy.context.scene.objects.active = obj
                        bpy.ops.object.modifier_remove(modifier="EdgeSplit")
 
                    else:
                        obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
                        obj.modifiers["EdgeSplit"].split_angle = 1.0472
                bpy.context.scene.objects.active = self.act_obj
        
        #---------------------------------
        # Remove The Bevel Object
        #---------------------------------
        if event.type == 'O' and event.value == 'PRESS':
            if self.profile:
                bevelobject = self.act_obj.data.bevel_object
                self.act_obj.data.bevel_object = None
                self.profile = False
                bevelobject.select = False
                self.act_obj.data.fill_mode = 'FULL'

        #---------------------------------
        # Toggle Spline Type Poly/Bezier
        #---------------------------------
        if event.type == 'R' and event.value == 'PRESS':
            if self.profile:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.curve.select_all(action='SELECT')
                if self.poly_bezier == 'poly':
                    bpy.ops.curve.spline_type_set(type='BEZIER')
                    bpy.ops.curve.handle_type_set(type='AUTOMATIC')
                else:
                    bpy.ops.curve.spline_type_set(type='POLY')
                bpy.ops.object.mode_set(mode='OBJECT')

            else:
                for obj in context.selected_objects:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.curve.select_all(action='SELECT')
                    if self.poly_bezier == 'poly':
                        bpy.ops.curve.spline_type_set(type='BEZIER')
                        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
                    else:
                        bpy.ops.curve.spline_type_set(type='POLY')
                    bpy.ops.object.mode_set(mode='OBJECT')
                 
                bpy.context.scene.objects.active = self.act_obj
                
            self.poly_bezier = 'poly' if self.poly_bezier == 'bezier' else 'poly'

      
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if self.input:
                self.input = ""
                self.action_enabled = 'free'
                
            elif self.action_enabled in {'depth', 'reso_u', 'reso_v'}:
                self.update_values()
                self.action_enabled = 'free'
            
            elif self.profile and self.choose_profile:
                # si l'objet actif n'est plus le meme quand in clique sur rmb ou esc, on remet les objets precedents
                if bpy.context.active_object != self.act_obj:
                    bpy.context.active_object.select = False
                    self.act_obj.select = True
                    bpy.context.scene.objects.active = self.act_obj
                    self.act_obj.data.bevel_object.select = True
                self.choose_profile = False
            else:
                self.profile = False
                MPM.tubify_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._tubify_handle, 'WINDOW')
                return {'CANCELLED'}
 
        if event.type in {'DEL', 'BACK_SPACE'} and event.value == 'PRESS':
            if event.type == 'BACK_SPACE' and self.input:
                self.input = self.input[:-1]
            else:
                if self.profile:
                    self.act_obj.data.fill_mode = 'HALF'
                    self.act_obj.data.bevel_depth = 0
                    self.act_obj.data.bevel_resolution = 0
                    self.act_obj.data.bevel_object = None
                else:  
                    for obj in  context.selected_objects:
                        obj.data.fill_mode = 'HALF'
                        obj.data.bevel_depth = 0
                        obj.data.bevel_resolution = 0
                self.profile = False
                MPM.tubify_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._tubify_handle, 'WINDOW')
                return {'FINISHED'} 
 
        return {'RUNNING_MODAL'}

#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------              
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            MPM = context.window_manager.MPM
            self.act_obj = context.active_object
            depth_value = get_addon_preferences().depth_value
            reso_u = get_addon_preferences().reso_u
            reso_v = get_addon_preferences().reso_v
            self.pref_tool = get_addon_preferences().work_tool
            self.modal_speed = get_addon_preferences().modal_speed
            
            if self.act_obj.type == 'MESH':
                self.convert_as_curve(self.act_obj)
 
            if len([obj for obj in context.selected_objects if obj.type == 'CURVE']) == 2:
                obj_profile = context.selected_objects[0] if context.selected_objects[1] == self.act_obj else context.selected_objects[1]
                self.act_obj.data.show_normal_face = False
 
                #Show Wire
                self.act_obj.show_wire = True
                self.act_obj.show_all_edges = True
 
                if not self.act_obj.data.bevel_resolution:
                    self.act_obj.data.bevel_depth = depth_value
                    self.act_obj.data.resolution_u = reso_u
                    self.act_obj.data.bevel_resolution = reso_v
                self.act_obj.data.splines[0].tilt_interpolation = 'BSPLINE'
                self.act_obj.data.splines[0].radius_interpolation = 'BSPLINE'
 
                self.act_obj.data.bevel_object = obj_profile
 
                self.act_obj = self.act_obj if self.act_obj.select else context.selected_objects[-1]
 
                bpy.context.scene.objects.active = self.act_obj
                
                # passage du mean radius a 1 au cas ou les transforms de la curve on etaient appliquees
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.curve.select_all(action='SELECT')
                bpy.ops.curve.radius_set(radius=1)
                bpy.ops.object.mode_set(mode='OBJECT')
                
                args = (self, context)
 
                self._tubify_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
                self.first_mouse_x = event.mouse_x
                self.bevel_depth = self.act_obj.data.bevel_depth
                self.reso_u = self.act_obj.data.resolution_u
                self.reso = self.act_obj.data.bevel_resolution
                self.profile = True
                self.profile_reso = obj_profile.data.resolution_u
                self.profile_scale = obj_profile.scale
                MPM.tubify_enabled = True
                context.window_manager.modal_handler_add(self)
 
                return {'RUNNING_MODAL'}
 
            elif self.check_mesh_validity():
                for obj in context.selected_objects:
                    if obj not in self.check_mesh_validity():
                        obj.select=False
                        pass
                    else:
                        if obj.type == 'MESH':
                            self.convert_as_curve(obj)
 
                        obj.data.fill_mode = 'FULL'
                        obj.data.show_normal_face = False
 
                        #Show Wire
                        obj.show_wire = True
                        obj.show_all_edges = True
 
                    if not obj.data.bevel_resolution:
                        obj.data.bevel_depth = depth_value
                        obj.data.resolution_u = reso_u
                        obj.data.bevel_resolution = reso_v
 
                    obj.data.splines[0].tilt_interpolation = 'BSPLINE'
                    obj.data.splines[0].radius_interpolation = 'BSPLINE'
 
                if self.act_obj.data.bevel_object:
                    self.profile = True
                    self.profile_scale = self.act_obj.data.bevel_object.scale
                    self.act_obj.data.bevel_object.select = True
                
                # passage du mean radius a 1 au cas ou les transforms de la curve on etaient appliquees
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.curve.select_all(action='SELECT')
                bpy.ops.curve.radius_set(radius=1)
                bpy.ops.object.mode_set(mode='OBJECT')
                
                self.act_obj = self.act_obj if self.act_obj.select else context.selected_objects[-1]
 
                bpy.context.scene.objects.active = self.act_obj
 
                args = (self, context)
 
                self._tubify_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
                self.first_mouse_x = event.mouse_x
                self.bevel_depth = self.act_obj.data.bevel_depth
                self.reso_u = self.act_obj.data.resolution_u
                self.reso = self.act_obj.data.bevel_resolution
 
                MPM.tubify_enabled = True
                context.window_manager.modal_handler_add(self)
 
                return {'RUNNING_MODAL'}
 
            else:
                self.report({'WARNING'}, "Active object is not a Mesh or a Curve")
                return {'CANCELLED'}
 
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}