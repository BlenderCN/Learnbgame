import bpy
from bpy.types import Operator
from bpy.props import (StringProperty, 
                       IntProperty, 
                       FloatProperty,
                       BoolProperty)
from .utils.text_to_draw import *
from .utils.fonctions import *


class SolidifyModal(Operator):
    bl_idname = "object.solidify_modal"
    bl_label = "Modal Solidify"
 
    first_mouse_x = IntProperty()
    thickness = FloatProperty()
    mode = StringProperty()
    input = StringProperty()
    slow_down = BoolProperty(default=False)
 
    def modal(self, context, event):
        context.area.tag_redraw()
        MPM = context.window_manager.MPM
        input_list = ['0', '1', '2', '3', '4','5', '6', '7', '8', '9', '-', '+', '.']
        
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
                for obj in context.selected_objects:
                    obj.modifiers["Solidify"].thickness = float(self.input)
                
                self.thickness = float(self.input)
                self.first_mouse_x = event.mouse_x
                self.input = ""
            
 
        #change Position
        if event.type == 'UP_ARROW' and event.value=='PRESS':
            bpy.ops.object.modifier_move_up(modifier="Solidify")
 
        if event.type == 'DOWN_ARROW' and event.value=='PRESS':
            bpy.ops.object.modifier_move_down(modifier="Solidify")
 
        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'} 
 
        #Solidify
        if self.pref_tool == 'pen':
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'} 
            
            if event.type == 'LEFT_SHIFT' or event.type == 'RIGHT_SHIFT':
                if event.value == 'PRESS':
                    if not self.slow_down:
                        self.first_mouse_x = event.mouse_x
                        self.thickness = context.active_object.modifiers["Solidify"].thickness
                        self.slow_down = True
                        
                elif event.value == 'RELEASE':
                    self.first_mouse_x = event.mouse_x
                    self.thickness = context.active_object.modifiers["Solidify"].thickness
                    self.slow_down = False
            
            if event.type == 'MOUSEMOVE':       
                delta = (self.first_mouse_x - event.mouse_x) / 8 if event.shift else self.first_mouse_x - event.mouse_x
                for obj in context.selected_objects:
                    obj.modifiers["Solidify"].thickness = self.thickness + min(100,-(delta/70)*self.modal_speed) 
        
        elif self.pref_tool == 'mouse':
            value = 0
            if event.type == 'WHEELUPMOUSE':
                value = 0.01 if event.shift else 0.1
            
            elif event.type == 'WHEELDOWNMOUSE':
                value = -0.01 if event.shift else -0.1
            
            for obj in context.selected_objects:
                obj.modifiers["Solidify"].thickness += value

             
        #Even thickness
        if event.type == 'E' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Solidify"].use_even_offset = False if obj.modifiers["Solidify"].use_even_offset else True
 
        #Fill Rim
        if event.type == 'R' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Solidify"].use_rim = False if obj.modifiers["Solidify"].use_rim else True 
 
        #Only Rim
        if event.type == 'T' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Solidify"].use_rim_only = False if obj.modifiers["Solidify"].use_rim_only else True 
 
        #Crease
        if event.type == 'C' and event.value=='PRESS':
            for obj in context.selected_objects:
                if obj.modifiers["Solidify"].edge_crease_inner == 0 :
                    obj.modifiers["Solidify"].edge_crease_inner = 1
                    obj.modifiers["Solidify"].edge_crease_outer = 1
                    obj.modifiers["Solidify"].edge_crease_rim = 1
                elif obj.modifiers["Solidify"].edge_crease_inner == 1 :
                    obj.modifiers["Solidify"].edge_crease_inner = 0
                    obj.modifiers["Solidify"].edge_crease_outer = 0
                    obj.modifiers["Solidify"].edge_crease_rim = 0
 
        #Offset
        if event.type == 'O' and event.value=='PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Solidify"].offset = 0 if obj.modifiers["Solidify"].offset == 1 else 1        
 
        if event.type == 'B' and event.value == 'PRESS':
            act_obj = context.active_object
            act_obj_bevel = False
            for mod in act_obj.modifiers:
                if mod.type == 'BEVEL':
                    act_obj_bevel = True
            if act_obj_bevel:
                for obj in context.selected_objects:
                    bevel = False
                    for mod in obj.modifiers:
                        if mod.type == 'BEVEL':
                            bevel = True
                    if bevel:
                        bpy.context.scene.objects.active = obj
                        bpy.ops.object.modifier_remove(modifier="Bevel")
                        obj.show_wire = False
                        obj.show_all_edges = False
 
                bpy.context.scene.objects.active = act_obj
 
            else:     
                for obj in context.selected_objects:
                    bpy.context.scene.objects.active = obj
                    obj.show_wire = True
                    obj.show_all_edges = True
                    obj_bevel = False
                    for mod in obj.modifiers:
                        if mod.type == 'BEVEL':
                            obj_bevel = True
                    if not obj_bevel:
                        obj.modifiers.new("Bevel", 'BEVEL')
 
                    obj.modifiers['Bevel'].limit_method = 'ANGLE'
                    obj.modifiers['Bevel'].angle_limit = 1.535889744758606
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.mark_sharp(clear=True)
                    bpy.ops.transform.edge_crease(value=-1)
                    bpy.ops.transform.edge_bevelweight(value=-1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    obj.modifiers['Bevel'].segments = 2
                    obj.modifiers['Bevel'].profile = 1
                bpy.context.scene.objects.active = act_obj
 
 
        if event.type == 'S' and event.value == 'PRESS':
            act_obj = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT')
            act_obj_subsurf = False
            for mod in act_obj.modifiers:
                if mod.type == 'SUBSURF':
                    act_obj_subsurf = True
 
            if act_obj_subsurf:
                for obj in context.selected_objects:
                    subsurf = False
                    for mod in obj.modifiers:
                        if mod.type == 'SUBSURF':
                            subsurf = True
                    if subsurf:
                        bpy.context.scene.objects.active = obj
                        bpy.ops.object.modifier_remove(modifier="Subsurf")
                bpy.context.scene.objects.active = act_obj
                bpy.ops.object.shade_flat()
                bpy.ops.object.mode_set(mode=self.mode)
 
            else:
                for obj in context.selected_objects:
                    bpy.context.scene.objects.active = obj
                    obj_subsurf = False
                    for mod in obj.modifiers:
                        if mod.type == 'SUBSURF':
                            obj_subsurf = True
 
                    if not obj_subsurf:
                        obj.modifiers.new("Subsurf", 'SUBSURF')
                        obj.modifiers["Subsurf"].levels = 2
                        obj.modifiers["Subsurf"].show_only_control_edges = True
 
                    add_smooth()
 
                bpy.context.scene.objects.active = act_obj
                bpy.ops.object.mode_set(mode=self.mode)
 
 
        if event.type == 'H' and event.value == 'PRESS':
            for obj in context.selected_objects:
                obj.modifiers["Solidify"].show_viewport = False if obj.modifiers["Solidify"].show_viewport else True
 
        if event.type == 'A':
            act_obj = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT')
            for obj in context.selected_objects:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
 
            bpy.context.scene.objects.active = act_obj
            MPM.solidify_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._solidify_handle, 'WINDOW')
            bpy.ops.object.mode_set(mode=self.mode)
            return {'FINISHED'} 
 
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if self.input:
                self.input = ""
            else:
                MPM.solidify_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._solidify_handle, 'WINDOW')
                return {'CANCELLED'}
 
        if event.type in {'DEL', 'BACK_SPACE'} and event.value == 'PRESS':
            if event.type == 'BACK_SPACE' and self.input:
                self.input = self.input[:-1]
            else:
                act_obj = context.active_object
                bpy.ops.object.mode_set(mode='OBJECT')
                for obj in context.selected_objects:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier="Solidify")
     
                bpy.context.scene.objects.active = act_obj
                MPM.solidify_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._solidify_handle, 'WINDOW')
                bpy.ops.object.mode_set(mode=self.mode)
                return {'FINISHED'} 
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.active_object.type in {'MESH', 'CURVE'}:
                act_obj = bpy.context.active_object
                MPM = context.window_manager.MPM
                self.mode = context.object.mode
                self.pref_tool = get_addon_preferences().work_tool
                self.modal_speed = get_addon_preferences().modal_speed
                
                act_obj_solidify = False
                for mod in act_obj.modifiers:
                    if mod.type == 'SOLIDIFY':
                        act_obj_solidify = True
 
                if not act_obj_solidify:
                    act_obj.modifiers.new("Solidify", 'SOLIDIFY')
                    act_obj.modifiers["Solidify"].thickness = 0.1
                    act_obj.modifiers["Solidify"].use_even_offset = True
                    act_obj.modifiers["Solidify"].offset = 1
                    act_obj.modifiers["Solidify"].use_rim = True
                    act_obj.modifiers["Solidify"].use_quality_normals = True
                    act_obj.modifiers["Solidify"].edge_crease_inner = 0
 
 
                self.thickness = act_obj.modifiers["Solidify"].thickness
 
                for obj in context.selected_objects:
                    if obj.type not in  {'MESH', 'CURVE'}:
                        obj.select=False
                        pass
 
                    elif obj == act_obj:
                        pass
 
                    else:
                        solidify = False
                        for mod in obj.modifiers:
                            if mod.type == 'SOLIDIFY':
                                solidify = True
 
                        if not solidify:
                            obj.modifiers.new("Solidify", 'SOLIDIFY')
                            obj.modifiers["Solidify"].thickness = self.thickness
                            obj.modifiers["Solidify"].use_even_offset = act_obj.modifiers["Solidify"].use_even_offset
                            obj.modifiers["Solidify"].offset = act_obj.modifiers["Solidify"].offset
                            obj.modifiers["Solidify"].use_quality_normals = True
                            obj.modifiers["Solidify"].edge_crease_inner = act_obj.modifiers["Solidify"].edge_crease_inner
 
 
                # the arguments we pass the the callback
                args = (self, context)
                # Add the region OpenGL drawing callback
                # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
                self._solidify_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
                self.first_mouse_x = event.mouse_x
 
                MPM.solidify_enabled = True
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
 
            else:
                self.report({'WARNING'}, "Active object is not a Mesh")
                return {'CANCELLED'}    
 
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
