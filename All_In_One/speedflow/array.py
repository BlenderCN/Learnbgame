import bpy
from bpy.types import Operator
from bpy.props import (StringProperty, 
                       IntProperty, 
                       FloatProperty,
                       BoolProperty,
                       EnumProperty)
from .utils.text_to_draw import *
from .utils.fonctions import *

       
class ArrayModal(Operator):
    bl_idname = "object.array_modal"
    bl_label = "Modal Array"
 
    first_mouse_x = IntProperty()
    on_curve = BoolProperty(default=False)
    choose_start = BoolProperty(default=False)
    choose_end = BoolProperty(default=False)
    choose_profile = BoolProperty(default=False) 
    count_value = IntProperty()
    relative_offset_enabled = BoolProperty(default=True)
    offset_x = FloatProperty()
    offset_y = FloatProperty()
    offset_z = FloatProperty()
    action_enabled = EnumProperty(
            items=(('free', "free", ""),
                   ('count', "count", ""),
                   ('offset', "offset", "")),
                   default='count'
                   )
    axis_value = IntProperty(default=0)
    mode = StringProperty()
    key = StringProperty()
    input = StringProperty()
    slow_down = BoolProperty(default=False)
    
    def main_ray_cast(self, context, event):
        """Run this function on left mouse, execute the ray cast"""
        # get the context arguments
        MPM = bpy.context.window_manager.MPM
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y
     
        # get the ray from the viewport and mouse
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
     
        ray_target = ray_origin + view_vector
     
        def visible_objects_and_duplis():
            """Loop over (object, matrix) pairs (mesh only)"""
     
            for obj in context.visible_objects:
                if obj.type == 'MESH':
                    yield (obj, obj.matrix_world.copy())
     
                if obj.dupli_type != 'NONE':
                    obj.dupli_list_create(scene)
                    for dob in obj.dupli_list:
                        obj_dupli = dob.object
                        if obj_dupli.type == 'MESH':
                            yield (obj_dupli, dob.matrix.copy())
     
                obj.dupli_list_clear()
     
        def obj_ray_cast(obj, matrix):
            """Wrapper for ray casting that moves the ray into object space"""
     
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv * ray_origin
            ray_target_obj = matrix_inv * ray_target
            ray_direction_obj = ray_target_obj - ray_origin_obj
     
            # cast the ray
            success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
     
            if success:
                return location, normal, face_index
            else:
                return None, None, None
     
        # cast rays and find the closest object
        best_length_squared = -1.0
        best_obj = None
     
        for obj, matrix in visible_objects_and_duplis():
            if obj.type == 'MESH':
                hit, normal, face_index = obj_ray_cast(obj, matrix)
                if hit is not None:
                    hit_world = matrix * hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if best_obj is None or length_squared < best_length_squared:
                        best_length_squared = length_squared
                        best_obj = obj
     
        if best_obj is not None:
            if self.on_curve:
                if best_obj != bpy.context.active_object:
                    if self.choose_start:
                        bpy.context.active_object.modifiers["Array_on_curve"].start_cap = None if bpy.context.active_object.modifiers["Array_on_curve"].start_cap == best_obj else best_obj
                        self.choose_start = False
     
                    if self.choose_end:
                        bpy.context.active_object.modifiers["Array_on_curve"].end_cap = None if bpy.context.active_object.modifiers["Array_on_curve"].end_cap == best_obj else best_obj
                        self.choose_end = False
     
                    if self.choose_profile:
     
                        curve = bpy.context.active_object.modifiers["Curve"].object
                        start = bpy.context.active_object.modifiers["Array_on_curve"].start_cap if bpy.context.active_object.modifiers["Array_on_curve"].start_cap else ""
                        end = bpy.context.active_object.modifiers["Array_on_curve"].end_cap if bpy.context.active_object.modifiers["Array_on_curve"].end_cap else ""
     
                        bpy.ops.object.modifier_remove(modifier = "Array_on_curve")
                        bpy.ops.object.modifier_remove(modifier = "Curve")
                        bpy.context.active_object.select = False
                        best_obj.select = True
                        bpy.context.scene.objects.active = best_obj
                        best_obj.modifiers.new("Array_on_curve", 'ARRAY')
                        MPM.array_name = "Array_on_curve"
                        best_obj.modifiers["Array_on_curve"].relative_offset_displace[self.axis_value] = 1
                        for i in range(3):
                            if i != self.axis_value:
                                best_obj.modifiers["Array_on_curve"].relative_offset_displace[i]=0
                        best_obj.modifiers["Array_on_curve"].fit_type = 'FIT_CURVE'
                        best_obj.modifiers["Array_on_curve"].curve = curve
                        best_obj.modifiers["Array_on_curve"].use_merge_vertices = True
                        if start:
                            best_obj.modifiers["Array_on_curve"].start_cap = start if start != best_obj else None
     
                        if end:
                            best_obj.modifiers["Array_on_curve"].end_cap = end if end != best_obj else None
     
                        # setup the curve modifier
                        best_obj.modifiers.new("Curve", 'CURVE')
                        best_obj.modifiers["Curve"].object = curve
                        self.setup_deform_axis(best_obj.modifiers, self.axis_value)
     
                        self.choose_profile = False     
    
    
    def array_on_curve_validity(self, act_obj):
        if len(bpy.context.selected_objects) == 2:
            obj1, obj2 = bpy.context.selected_objects
            sec_obj = obj1 if obj2 == act_obj else obj2
            if act_obj.type == 'MESH' and sec_obj.type == 'CURVE':
                return sec_obj
            return None
        return None
    
    
    def setup_array_on_curve(self, act_obj):
        # mise en place du modifier Array
        act_obj.modifiers.new("Array_on_curve", 'ARRAY')
        curve = self.array_on_curve_validity(act_obj)
        if self.offset_type == 'relative':
            act_obj.modifiers["Array_on_curve"].relative_offset_displace[0] = 0
            act_obj.modifiers["Array_on_curve"].relative_offset_displace[2] = 1.0
        else:
            act_obj.modifiers["Array"].use_constant_offset = True
            act_obj.modifiers["Array"].use_relative_offset = False  
            act_obj.modifiers["Array_on_curve"].relative_offset_displace[2] = 1.0
            
        act_obj.modifiers["Array_on_curve"].fit_type = 'FIT_CURVE'
        act_obj.modifiers["Array_on_curve"].curve = curve
        act_obj.modifiers["Array_on_curve"].use_merge_vertices = True
         
        # mise en place du modifier Curve
        act_obj.modifiers.new("Curve", 'CURVE')
        act_obj.modifiers["Curve"].object = curve
        act_obj.modifiers["Curve"].deform_axis = 'POS_Z'
         
        # passage du mean radius a 1 au cas ou les transforms de la curve on etaient appliquees
        bpy.context.scene.objects.active = curve
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.radius_set(radius=1)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = act_obj
        
        
    def update_values(self):
        MPM = bpy.context.window_manager.MPM
        act_obj = bpy.context.active_object
        self.count_value = act_obj.modifiers[MPM.array_name].count
        relative = act_obj.modifiers[MPM.array_name].relative_offset_displace
        constant = act_obj.modifiers[MPM.array_name].constant_offset_displace
        
        self.offset_x, self.offset_y, self.offset_z = [relative[0], relative[1], relative[2]] if self.relative_offset_enabled else [constant[0], constant[1], constant[2]]
            
        self.axis_value = self.get_current_axis()[0]
        
 
    def get_current_axis(self):
        MPM = bpy.context.window_manager.MPM
        if self.relative_offset_enabled:
            index = [i for i in range(3) if bpy.context.object.modifiers[MPM.array_name].relative_offset_displace[i] != 0]
        else:
            index = [i for i in range(3) if bpy.context.object.modifiers[MPM.array_name].constant_offset_displace[i] != 0]

        return index
    
    
    def get_offset_type(self, act_obj):
        MPM = bpy.context.window_manager.MPM
        if act_obj.modifiers[MPM.array_name].use_relative_offset:
            return True
        return False
 
 
    def setup_deform_axis(self, modifier, index):
        if index == 0:
            modifier["Curve"].deform_axis = 'POS_X' if self.offset_x >= 0 else 'NEG_X'
        elif index == 1:
            modifier["Curve"].deform_axis = 'POS_Y' if self.offset_y >= 0 else 'NEG_Y'
        elif index == 2:
            modifier["Curve"].deform_axis = 'POS_Z' if self.offset_z >= 0 else 'NEG_Z'
        
        
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
        act_obj = bpy.context.active_object
        modifier = act_obj.modifiers
        event_list = ['x', 'y', 'z']
        input_list = ['0', '1', '2', '3', '4','5', '6', '7', '8', '9', '-', '+', '.']
         
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}
        

        # ADD NEW ARRAY
        if event.shift:
            if event.unicode in [key.upper() for key in event_list]:
                self.on_curve = False
                index = event_list.index(event.unicode.lower())
                bpy.ops.object.modifier_add(type='ARRAY')
                if MPM.array_name:
                    offset = modifier[MPM.array_name].relative_offset_displace[self.axis_value] if self.relative_offset_enabled else modifier[MPM.array_name].constant_offset_displace[self.axis_value]
         
                    count = modifier[MPM.array_name].count
                    MPM.array_name = get_modifier_list(act_obj, 'ARRAY')[-1]
                    if self.relative_offset_enabled:
                        modifier[MPM.array_name].relative_offset_displace[index] = offset
                    else:
                        modifier[MPM.array_name].use_relative_offset = False
                        modifier[MPM.array_name].use_constant_offset = True
                        modifier[MPM.array_name].constant_offset_displace[index] = offset
                    modifier[MPM.array_name].count = count
                else:
                    MPM.array_name = "Array"
                    if self.relative_offset_enabled:
                        modifier["Array"].relative_offset_displace[index] = 1
                    else:
                        modifier["Array"].constant_offset_displace[index] = 1
         
         
                if index != 0:
                    if self.relative_offset_enabled:
                        modifier[MPM.array_name].relative_offset_displace[0]=0
                    else:
                        modifier[MPM.array_name].constant_offset_displace[0]=0
         
                self.update_values()
 
        if MPM.array_name:
            
            # input to enter custom value directly
            if event.unicode in input_list:
                if event.unicode == "-":
                    if self.input.startswith("-"):
                        pass
                    else:
                        self.input = "-" + self.input
                elif event.unicode == "+":
                    if self.input.startswith("-"):
                        self.input = self.input.split("-")[-1]
                else:
                    self.input += event.unicode
            
            
            if self.input:
                if event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':
                    if self.action_enabled == 'count':
                        if int(self.input) < 0:
                            self.input = "0"
                        modifier[MPM.array_name].count = int(self.input)
                        
                        self.count_value = int(self.input)
                        self.first_mouse_x = event.mouse_x
                    
                    elif self.action_enabled == 'offset':
                        if self.relative_offset_enabled:
                            if self.axis_value == 0:
                                modifier[MPM.array_name].relative_offset_displace[self.axis_value] = float(self.input)
                            elif self.axis_value == 1:
                                modifier[MPM.array_name].relative_offset_displace[self.axis_value] = float(self.input)
                            elif self.axis_value == 2:
                                modifier[MPM.array_name].relative_offset_displace[self.axis_value] = float(self.input)
                        else:
                            if self.axis_value == 0:
                                modifier[MPM.array_name].constant_offset_displace[self.axis_value] = float(self.input)
                            elif self.axis_value == 1:
                                modifier[MPM.array_name].constant_offset_displace[self.axis_value] = float(self.input)
                            elif self.axis_value == 2:
                                modifier[MPM.array_name].constant_offset_displace[self.axis_value] = float(self.input)
                        
                        self.update_values()
                        self.first_mouse_x = event.mouse_x
                        
                    self.input = ""
                    
                    
            else:
                if event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':
                    if self.on_curve and (self.choose_start or self.choose_end or self.choose_profile):
                        self.main_ray_cast(context, event)
                     
                        return {'RUNNING_MODAL'}

                    if self.action_enabled == 'count' or self.action_enabled == 'offset':
                        self.action_enabled = 'free'
       
                    else:        
                        MPM.array_enabled = False
                        bpy.types.SpaceView3D.draw_handler_remove(self._array_handle, 'WINDOW')
                        return {'FINISHED'}
            
            if event.type == 'BACK_SPACE' and event.value == 'PRESS' and self.input:
                self.input = self.input[:-1]
                
            # CHANGE POSITION
            if event.type == 'UP_ARROW' and event.value=='PRESS':
                bpy.ops.object.modifier_move_up(modifier=MPM.array_name)
 
            if event.type == 'DOWN_ARROW' and event.value=='PRESS':
                bpy.ops.object.modifier_move_down(modifier=MPM.array_name)
            
            # CHANGE ARRAY
            if (event.type == 'GRLESS' or event.type == 'LEFT_ARROW') and event.value=='PRESS':
                array_list = get_modifier_list(act_obj, 'ARRAY')
                index = array_list.index(MPM.array_name)
                MPM.array_name = array_list[index-1 if index != 0 else -1]
                if MPM.array_name == "Array_on_curve":
                    self.on_curve = True
                else:
                    self.on_curve = False
                self.relative_offset_enabled = self.get_offset_type(act_obj)
                self.update_values()
 
            if (event.type == 'GRLESS' and event.shift) or (event.type == 'RIGHT_ARROW' and event.value=='PRESS'):
                array_list = get_modifier_list(act_obj, 'ARRAY')
                index = array_list.index(MPM.array_name)
                MPM.array_name = array_list[index+1 if index != len(array_list)-1 else 0]
                if MPM.array_name == "Array_on_curve":
                    self.on_curve = True
                else:
                    self.on_curve = False
                self.relative_offset_enabled = self.get_offset_type(act_obj)
                self.update_values()
        
            if event.type == 'S' and event.value == 'PRESS' and not self.on_curve and not self.input:
                self.action_enabled = 'count'
                self.first_mouse_x = event.mouse_x
                self.count_value = modifier[MPM.array_name].count
            
            if event.type == 'D' and event.value == 'PRESS' and not self.input:
                self.action_enabled = 'offset'
                self.first_mouse_x = event.mouse_x
                self.update_values()
                
            # CHANGE OFFSET AXIS
            if event.unicode and event.unicode in event_list:
                self.key = event.unicode
 
            if event.type == self.key.upper():
                index = event_list.index(self.key)
                
                # assigns the offset value of the previous axis to the new axis
                if self.relative_offset_enabled:
                    modifier[MPM.array_name].relative_offset_displace[index] = modifier[MPM.array_name].relative_offset_displace[self.axis_value]
     
                    for i in range(3):
                        if i != index:
                            modifier[MPM.array_name].relative_offset_displace[i]=0
                else:
                    modifier[MPM.array_name].constant_offset_displace[index] = modifier[MPM.array_name].constant_offset_displace[self.axis_value]
                     
                    for i in range(3):
                        if i != index:
                            modifier[MPM.array_name].constant_offset_displace[i]=0
 
                if self.on_curve:
                    self.setup_deform_axis(modifier, index)
 
                self.axis_value = index
            
            # HIDE MODIFIER
            if event.type == 'H' and event.value == 'PRESS':
                modifier[MPM.array_name].show_viewport = False if modifier[MPM.array_name].show_viewport else True
                if self.on_curve:
                    modifier["Curve"].show_viewport = False if modifier["Curve"].show_viewport else True
 
            # REMOVE ACTIVE MODIFIER
            if event.type == 'DEL' and event.value == 'PRESS':
                self.input = ""
                self.action_enabled = 'free'
                array_list = get_modifier_list(act_obj, 'ARRAY')
                if len(array_list) > 1:
                    bpy.ops.object.modifier_remove(modifier=MPM.array_name)
                    if self.on_curve:
                        bpy.ops.object.modifier_remove(modifier="Array_on_curve")
                        bpy.ops.object.modifier_remove(modifier="Curve")
                        self.on_curve = False
 
                    MPM.array_name = get_modifier_list(act_obj, 'ARRAY')[-1]
                    if MPM.array_name == "Array_on_curve":
                        self.on_curve = True
                    else:
                        self.on_curve = False
                    self.update_values()
 
                else:
                    bpy.ops.object.modifier_remove(modifier=MPM.array_name)
                    if self.on_curve:
                        bpy.ops.object.modifier_remove(modifier="Curve")
                        self.on_curve = False
                    MPM.array_name = ""
 
            if self.pref_tool == 'pen':
                if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                    return {'PASS_THROUGH'}
                
                if event.type == 'LEFT_SHIFT' or event.type == 'RIGHT_SHIFT':
                    if event.value == 'PRESS':
                        if not self.slow_down:
                            self.first_mouse_x = event.mouse_x
                            self.update_values()
                            self.slow_down = True
                            
                    elif event.value == 'RELEASE':
                        self.first_mouse_x = event.mouse_x
                        self.update_values()
                        self.slow_down = False
                
                if event.type == 'MOUSEMOVE':
                    delta = -(self.first_mouse_x - event.mouse_x)/8 if event.shift else -(self.first_mouse_x - event.mouse_x)
                    if self.action_enabled == 'count':
                        modifier[MPM.array_name].count = min(200,(delta/40)*self.modal_speed) + self.count_value
                        
                    elif self.action_enabled == 'offset':
                        if self.relative_offset_enabled:
                            if self.axis_value == 0:
                                modifier[MPM.array_name].relative_offset_displace[self.axis_value] = self.offset_x + (delta * 0.01)*self.modal_speed
                            elif self.axis_value == 1:
                                modifier[MPM.array_name].relative_offset_displace[self.axis_value] = self.offset_y + (delta * 0.01)*self.modal_speed
                            elif self.axis_value == 2:
                                modifier[MPM.array_name].relative_offset_displace[self.axis_value] = self.offset_z + (delta * 0.01)*self.modal_speed
                        else:
                            if self.axis_value == 0:
                                modifier[MPM.array_name].constant_offset_displace[self.axis_value] = self.offset_x + (delta * 0.01)*self.modal_speed
                            elif self.axis_value == 1:
                                modifier[MPM.array_name].constant_offset_displace[self.axis_value] = self.offset_y + (delta * 0.01)*self.modal_speed
                            elif self.axis_value == 2:
                                modifier[MPM.array_name].constant_offset_displace[self.axis_value] = self.offset_z + (delta * 0.01)*self.modal_speed
            
            elif self.pref_tool == 'mouse':
                value = 0
                if event.type == 'WHEELUPMOUSE':
                    if self.action_enabled == 'count':
                        value = 1
                    elif self.action_enabled == 'offset':
                        value = 0.01 if event.shift else 0.1
                    else:
                        return {'PASS_THROUGH'}
                        
                elif event.type == 'WHEELDOWNMOUSE':
                    if self.action_enabled == 'count':
                        value = -1
                    elif self.action_enabled == 'offset':
                        value = -0.01 if event.shift else -0.1
                    else:
                        return {'PASS_THROUGH'}
                    
                        
                if self.action_enabled == 'count':
                    modifier[MPM.array_name].count += value
                
                elif self.action_enabled == 'offset':
                    if self.relative_offset_enabled:
                        modifier[MPM.array_name].relative_offset_displace[self.axis_value] += value
                    else:
                        modifier[MPM.array_name].constant_offset_displace[self.axis_value] += value
                        
            
            # CHANGE OFFSET TYPE
            if event.type == 'F' and event.value == 'PRESS' and not self.on_curve:
                if self.relative_offset_enabled:
                    for mod in modifier:
                        if mod.type == 'ARRAY':
                            if mod.name == "Array_on_curve":
                                pass
                            else:
                                # recuperation de l'axe actif du constant_offset
                                constant_index = [i for i in range(3) if mod.constant_offset_displace[i] != 0]
                                # si pas d'axe actif
                                if not constant_index:
                                    # on recupere l'axe actif du relative_offset
                                    relative_index = [i for i in range(3) if mod.relative_offset_displace[i] != 0][0]
                                    # on defini le meme axe au constant_offset
                                    mod.constant_offset_displace[relative_index] = mod.relative_offset_displace[relative_index]
                                mod.use_relative_offset = False
                                mod.use_constant_offset = True
                    
                    get_addon_preferences().offset_type = 'constant'           
                    self.relative_offset_enabled = False
                else:
                    for mod in modifier:
                        if mod.type == 'ARRAY':
                            constant_index = [i for i in range(3) if mod.constant_offset_displace[i] != 0][0]
                            relative_index = [i for i in range(3) if mod.relative_offset_displace[i] != 0][0]
                            # si l'axe du relative_offset et different de celui du constant_offset
                            if relative_index != constant_index:
                                # on attribu la valeur de l'axe actuel du relative_offset au meme axe que le constant_offset
                                # si l'axe du constant et 0 et celui du relative et 1 avec une valeur de 0.5, l'axe 0 du relative prend la valeur 0.5
                                mod.relative_offset_displace[constant_index] = mod.relative_offset_displace[relative_index]
                                for i in range(3):
                                    if i != constant_index:
                                        mod.relative_offset_displace[i] = 0
                            mod.use_relative_offset = True
                            mod.use_constant_offset = False
                            
                    get_addon_preferences().offset_type = 'relative' 
                    self.relative_offset_enabled = True
                    
                self.update_values()
                
            # APPLY ACTIVE ARRAY
            if event.type == 'A' and event.value == 'PRESS':
                bpy.ops.object.mode_set(mode='OBJECT')
                array_list = get_modifier_list(act_obj, 'ARRAY')
                if len(array_list) > 1:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=MPM.array_name)
                    if self.on_curve:
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Curve")
                        self.on_curve = False
                    MPM.array_name = get_modifier_list(act_obj, 'ARRAY')[-1]
                    if MPM.array_name == "Array_on_curve":
                        self.on_curve = True
                    else:
                        self.on_curve = False
                    self.update_values()
 
                else:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=MPM.array_name)
                    if self.on_curve:
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Curve")
                        self.on_curve = False
                    MPM.array_enabled = False
                    bpy.types.SpaceView3D.draw_handler_remove(self._array_handle, 'WINDOW')
                    bpy.ops.object.mode_set(mode=self.mode)
                    return {'CANCELLED'} 
            
            if self.on_curve:
                if event.type == 'P' and event.value == 'PRESS':
                    self.choose_profile = False if self.choose_profile else True
                    self.choose_start = False
                    self.choose_end = False
                
                if event.type == 'E' and event.value == 'PRESS':
                    self.choose_start = False if self.choose_start else True
                    self.choose_end = False
                    self.choose_profile = False
                 
                if event.type == 'R' and event.value == 'PRESS':
                    self.choose_end = False if self.choose_end else True
                    self.choose_start = False
                    self.choose_profile = False
                    
                
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if MPM.array_name:
                if self.input:
                    self.input = ""

                elif self.choose_start:
                    self.choose_start = False
                
                elif self.choose_end:
                    self.choose_end = False
                
                elif self.choose_profile:
                    self.choose_profile = False
                    
                else:            
                    MPM.array_enabled = False
                    bpy.types.SpaceView3D.draw_handler_remove(self._array_handle, 'WINDOW')
                    return {'CANCELLED'}
            
            else:            
                MPM.array_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._array_handle, 'WINDOW')
                return {'CANCELLED'}
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            act_obj = bpy.context.active_object
            MPM = context.window_manager.MPM
            MPM.array_enabled = True
            self.mode = context.object.mode
            self.offset_type = get_addon_preferences().offset_type
            self.pref_tool = get_addon_preferences().work_tool
            self.modal_speed = get_addon_preferences().modal_speed
            
            is_array = False
            is_curve = False
            array_on_curve = False
            for mod in act_obj.modifiers:
                if mod.type == 'ARRAY':
                    is_array = True
                if mod.type == 'CURVE':
                    is_curve = True
                if mod.name == "Array_on_curve":
                    array_on_curve = True
 
            if not is_array: # si l'objet actif n'a pas de modifier ARRAY
                if self.array_on_curve_validity(act_obj): # on test les conditions pour voir si on passe en array_on_curve => obj actif = MESH, second obj = CURVE
                    self.setup_array_on_curve(act_obj)
                    array_on_curve = True

                else:
                    act_obj.modifiers.new("Array", 'ARRAY')
                    MPM.array_name = "Array"
                    if self.offset_type == 'relative':
                        act_obj.modifiers["Array"].relative_offset_displace[0] = 1.0
                    else:
                        act_obj.modifiers["Array"].use_constant_offset = True
                        act_obj.modifiers["Array"].use_relative_offset = False
                        act_obj.modifiers["Array"].constant_offset_displace[0] = 1.0
                        
 
            if self.array_on_curve_validity(act_obj):
                if not array_on_curve:
                    self.setup_array_on_curve(act_obj)
                MPM.array_name = "Array_on_curve"
                self.on_curve = True
 
            elif is_curve:
                self.on_curve = True
 
            else:
                mod_list = get_modifier_list(act_obj, 'ARRAY')
                if MPM.array_name not in mod_list:
                    MPM.array_name = mod_list[-1]
                    self.update_values()
                
                self.relative_offset_enabled = self.get_offset_type(act_obj)
            
            args = (self, context)
            self._array_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
            
            relative = act_obj.modifiers[MPM.array_name].relative_offset_displace
            constant = act_obj.modifiers[MPM.array_name].constant_offset_displace
             
            self.offset_x, self.offset_y, self.offset_z = [relative[0], relative[1], relative[2]] if self.relative_offset_enabled else [constant[0], constant[1], constant[2]]        
 
            self.count_value = act_obj.modifiers[MPM.array_name].count
            self.axis_value = self.get_current_axis()[0]
            self.first_mouse_x = event.mouse_x
            self.action_enabled = 'count'
 
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}