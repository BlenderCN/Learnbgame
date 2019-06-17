import bpy
import bmesh
from bpy.types import Operator
from bpy.props import (StringProperty, 
                       IntProperty, 
                       FloatProperty,
                       EnumProperty,
                       BoolProperty)
from .utils.text_to_draw import *
from .utils.fonctions import *


class BevelModal(Operator):
    bl_idname = "object.bevel_width"
    bl_label = "Modal Bevel"
 
    first_mouse_x = IntProperty()
    width = FloatProperty()
    bevel_w_value = FloatProperty()
    segments = FloatProperty()
    profile = FloatProperty()
    edge_index = IntProperty()
    action_enabled = EnumProperty(
            items=(('width', "width", ""),
                   ('segments', "segments", ""),
                   ('profile', "profile", "")),
                   default='width'
                   )
    mode = StringProperty()
    input = StringProperty()
    slow_down = BoolProperty(default=False)
    
    def update_values(self):
        MPM = bpy.context.window_manager.MPM
        if MPM.bevel_weight_enabled and not MPM.keep_bevel_weight:
            self.bevel_w_value = bpy.context.active_object.data.edges[self.edge_index].bevel_weight
        self.width = bpy.context.active_object.modifiers['Bevel'].width
        self.segments = bpy.context.active_object.modifiers['Bevel'].segments
        self.profile = bpy.context.active_object.modifiers['Bevel'].profile
            
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
                if self.action_enabled == 'segments':
                    if int(self.input) < 1:
                        self.input = "1"
                    if int(self.input) > 10:
                        self.input = "10"
                    for obj in context.selected_objects:
                        obj.modifiers['Bevel'].segments = int(self.input)
                    
                    self.segments = int(self.input)
                    self.first_mouse_x = event.mouse_x
                        
                elif self.action_enabled == 'profile':
                    if float(self.input) < 0:
                        self.input = "0"
                    if float(self.input) > 10:
                        self.input = "10"
                    for obj in context.selected_objects:
                        obj.modifiers['Bevel'].profile = float(self.input)
                    
                    self.profile = float(self.input)
                    self.first_mouse_x = event.mouse_x
                
                else:
                    if MPM.bevel_weight_enabled and not MPM.keep_bevel_weight:
                        if float(self.input) < 0:
                            self.input = "0"
                        if float(self.input) > 1:
                            self.input = "1"
                            
                        for edges in context.active_object.data.edges:
                            if edges.select:
                                edges.bevel_weight = float(self.input)
                        
                        self.bevel_w_value = float(self.input)
                        self.first_mouse_x = event.mouse_x
                        
                    else:
                        if float(self.input) < 0:
                            self.input = "0"
                        if float(self.input) > 10:
                            self.input = "10"
                        
                        for obj in context.selected_objects:
                            obj.modifiers['Bevel'].width = float(self.input)
                            
                        self.width = float(self.input)
                        self.first_mouse_x = event.mouse_x
                    
                self.input = ""
                self.action_enabled = 'width'
                    
        
        elif event.type in {'RET', 'NUMPAD_ENTER', 'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':
            if self.action_enabled == 'segments' or self.action_enabled == 'profile':
                self.action_enabled = 'width'
                bpy.context.active_object.modifiers['Bevel'].width = self.width
                self.first_mouse_x = event.mouse_x
            else:    
                MPM.bevel_enabled = False
                for obj in context.selected_objects:
                    if not self.wire:
                        obj.show_wire = False
                        obj.show_all_edges = False
                bpy.types.SpaceView3D.draw_handler_remove(self._bevel_handle, 'WINDOW')
                bpy.ops.object.mode_set(mode=self.mode)
         
                return {'FINISHED'}
         
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'} 
        
        #change Position
        if event.type == 'DOWN_ARROW' and event.value=='PRESS':
            bpy.ops.object.modifier_move_down(modifier="Bevel")
 
        if event.type == 'UP_ARROW' and event.value=='PRESS':
            bpy.ops.object.modifier_move_up(modifier="Bevel")
            
        if event.type == 'S' and event.value == 'PRESS':
            if not self.input:
                self.action_enabled = 'segments'
                self.first_mouse_x = event.mouse_x
                self.width = bpy.context.active_object.modifiers['Bevel'].width
                self.segments = bpy.context.active_object.modifiers['Bevel'].segments
        
        if event.type == 'D' and event.value == 'PRESS':
            if not self.input:
                self.action_enabled = 'profile'
                self.first_mouse_x = event.mouse_x
                self.width = bpy.context.active_object.modifiers['Bevel'].width
                self.profile = bpy.context.active_object.modifiers['Bevel'].profile

        #Bevel
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
                delta = (self.first_mouse_x - event.mouse_x) / 8 if event.shift else self.first_mouse_x - event.mouse_x
                if MPM.bevel_weight_enabled and not MPM.keep_bevel_weight:
                    if self.action_enabled == 'width':
                        for edges in context.active_object.data.edges:
                            if edges.select:
                                edges.bevel_weight = self.bevel_w_value + min(1,-(delta/400)*self.modal_speed)
                        
                    elif self.action_enabled == 'segments':
                        bpy.context.active_object.modifiers['Bevel'].segments = self.segments + min(10,-(delta/40)*self.modal_speed)   
                    elif self.action_enabled == 'profile':
                        bpy.context.active_object.modifiers['Bevel'].profile = self.profile + min(10,-(delta/150)*self.modal_speed)

                else:
                    for obj in context.selected_objects:
                        if self.action_enabled == 'width':
                            obj.modifiers['Bevel'].width = self.width + min(10,-(delta/400)*self.modal_speed)
                        elif self.action_enabled == 'segments':
                            obj.modifiers['Bevel'].segments = self.segments + min(10,-(delta/40)*self.modal_speed)   
                        elif self.action_enabled == 'profile':
                            obj.modifiers['Bevel'].profile = self.profile + min(10,-(delta/150)*self.modal_speed)


        elif self.pref_tool == 'mouse':  
            value = 0    
            if event.type == 'WHEELUPMOUSE':
                if self.action_enabled == 'segments':
                    value = 1
                else:
                    value = 0.01 if event.shift else 0.1
                    
            elif event.type ==  'WHEELDOWNMOUSE':
                if self.action_enabled == 'segments':
                    value = -1
                else:
                    value = -0.01 if event.shift else -0.1
                
            
            if MPM.bevel_weight_enabled and not MPM.keep_bevel_weight:
                if self.action_enabled == 'width':
                    for edges in context.active_object.data.edges:
                        if edges.select:
                            edges.bevel_weight += value
             
                elif self.action_enabled == 'segments':
                    bpy.context.active_object.modifiers['Bevel'].segments += value
                elif self.action_enabled == 'profile':
                    bpy.context.active_object.modifiers['Bevel'].profile += value 
            
            else:
                for obj in context.selected_objects:
                    if self.action_enabled == 'width':
                        obj.modifiers['Bevel'].width += value
                    elif self.action_enabled == 'segments':
                        obj.modifiers['Bevel'].segments += value
                    elif self.action_enabled == 'profile':
                        obj.modifiers['Bevel'].profile += value
            
            
        if event.type == 'F' and event.value=='PRESS':
            act_obj = bpy.context.active_object
            
            if not MPM.subdiv_mode:
                self.segments = act_obj.modifiers['Bevel'].segments
                self.profile = act_obj.modifiers['Bevel'].profile
 
            for obj in context.selected_objects:
                bpy.context.scene.objects.active = obj    
                bpy.ops.object.mode_set(mode="EDIT")
 
                #Edge mode
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
 
                #Clear all
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.transform.edge_crease(value=-1)
                if MPM.subdiv_mode:
                    bpy.ops.transform.edge_bevelweight(value=-1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                    bpy.ops.mesh.mark_sharp()
                    bpy.ops.transform.edge_crease(value=1)
                    bpy.ops.transform.edge_bevelweight(value=1)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode="OBJECT")
                    add_smooth()
 
                    if self.segments == 2 and self.profile == 1:
                        obj.modifiers["Bevel"].segments = 4
                        obj.modifiers["Bevel"].profile = 0.7
                    else:    
                        obj.modifiers["Bevel"].segments = self.segments
                        obj.modifiers["Bevel"].profile = self.profile
                else:
                    obj.modifiers["Bevel"].segments = 2
                    obj.modifiers["Bevel"].profile = 1
                    bpy.ops.object.mode_set(mode="OBJECT")
 
            bpy.context.scene.objects.active = act_obj
            MPM.subdiv_mode = False if MPM.subdiv_mode else True
            get_addon_preferences().subdiv_mode = False if get_addon_preferences().subdiv_mode else True
 
        if event.type == 'R' and event.value =='PRESS':
            MPM.bevel_weight_enabled = False if MPM.bevel_weight_enabled else True
            if MPM.bevel_weight_enabled:
                bpy.context.scene.tool_settings.mesh_select_mode = (False, True, False)
 
                MPM.bevel_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._bevel_handle, 'WINDOW')
                bpy.ops.object.mode_set(mode='EDIT')
                return {'FINISHED'}
            else:
                self.first_mouse_x = event.mouse_x
 
        if event.type == 'C' and event.value=='PRESS':
            act_obj = bpy.context.active_object
            if act_obj.modifiers['Bevel'].limit_method == 'WEIGHT':
                act_obj.modifiers['Bevel'].limit_method = 'ANGLE'
                bpy.context.object.modifiers["Bevel"].angle_limit = 1.56905
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.transform.edge_crease(value=-1)
                bpy.ops.transform.edge_bevelweight(value=-1)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')
            elif act_obj.modifiers['Bevel'].limit_method == 'ANGLE' :
                act_obj.modifiers['Bevel'].limit_method = 'WEIGHT'
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                add_edge_bevel_weight()
                bpy.ops.object.mode_set(mode='OBJECT')
 
        if event.type == 'H' and event.value == 'PRESS':
            bpy.context.active_object.modifiers['Bevel'].show_viewport = False if bpy.context.active_object.modifiers['Bevel'].show_viewport else True
 
        if event.type == 'G' and event.value == 'PRESS':
            current_dir = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
            user_preferences = bpy.context.user_preferences
            addon_prefs = user_preferences.addons[current_dir].preferences 
            if addon_prefs.wire_bevel:
                addon_prefs.wire_bevel = False
                self.wire = False
            else:
                addon_prefs.wire_bevel = True
                self.wire = True

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if self.action_enabled == 'segments':
                self.action_enabled = 'width'
                self.input = ""
                for obj in bpy.context.selected_objects:
                    obj.modifiers["Bevel"].segments = self.segments
            elif self.action_enabled == 'profile':
                self.action_enabled = 'width'
                self.input = ""
                for obj in bpy.context.selected_objects:
                    obj.modifiers["Bevel"].profile = self.profile
            else:
                MPM.bevel_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._bevel_handle, 'WINDOW')
                #Restaure la valeur initiale du width
                for obj in context.selected_objects:
                    obj.modifiers['Bevel'].width = self.width
                    obj.modifiers['Bevel'].segments = self.segments
                    if not self.wire:
                        obj.show_wire = False
                        obj.show_all_edges = False
                bpy.ops.object.mode_set(mode=self.mode)
     
                return {'CANCELLED'}
 
        if event.type in {'DEL', 'BACK_SPACE'} and event.value == 'PRESS':
            if event.type == 'BACK_SPACE' and self.input:
                self.input = self.input[:-1] 
            else:    
                MPM.bevel_enabled = False
                bpy.types.SpaceView3D.draw_handler_remove(self._bevel_handle, 'WINDOW')
                act_obj = bpy.context.active_object
                for obj in context.selected_objects:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier="Bevel")
                    if not self.wire:
                        obj.show_wire = False
                        obj.show_all_edges = False
     
                bpy.context.scene.objects.active = act_obj
                bpy.ops.object.mode_set(mode=self.mode)
     
                return {'CANCELLED'} 
 
        if event.type == 'A':
            MPM.bevel_enabled = False
            bpy.types.SpaceView3D.draw_handler_remove(self._bevel_handle, 'WINDOW')
            act_obj = bpy.context.active_object
            for obj in context.selected_objects:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Bevel")
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.transform.edge_crease(value=-1)
                bpy.ops.transform.edge_bevelweight(value=-1)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT') 
                if not self.wire:
                    obj.show_wire = False
                    obj.show_all_edges = False
 
            bpy.context.scene.objects.active = act_obj
            bpy.ops.object.mode_set(mode=self.mode)
            return {'FINISHED'} 
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.active_object.type == 'MESH':
                MPM = context.window_manager.MPM
                subdiv_mode = get_addon_preferences().subdiv_mode
                bevel_width = get_addon_preferences().sub_bevel_width if subdiv_mode else get_addon_preferences().nosub_bevel_width
                segments = get_addon_preferences().sub_bevel_segments if subdiv_mode else get_addon_preferences().nosub_bevel_segments
                profile = get_addon_preferences().sub_bevel_profil if subdiv_mode else get_addon_preferences().nosub_bevel_profil
                self.wire = get_addon_preferences().wire_bevel
                self.mode = context.object.mode
                self.pref_tool = get_addon_preferences().work_tool
                self.modal_speed = get_addon_preferences().modal_speed
                act_obj = bpy.context.active_object

                if context.object.mode == 'EDIT' and len(context.selected_objects) == 1:
                    mesh = act_obj.data
                    bm = bmesh.from_edit_mesh(mesh)
                    
                    act_obj_bevel = False
                    for mod in act_obj.modifiers:
                        if mod.type == 'BEVEL':
                            act_obj_bevel = True

#                    edges = [edges.index for edges in bm.edges if edges.select]
                    act_obj.update_from_editmode()
                    edges = [edg.index for edg in act_obj.data.edges if edg.select]
                    
                    if not act_obj_bevel:
                        MPM.subdiv_mode = True if subdiv_mode else False
                        
                        act_obj.modifiers.new("Bevel", "BEVEL")
                        act_obj.modifiers['Bevel'].width = bevel_width
                        act_obj.modifiers['Bevel'].segments = segments
                        act_obj.modifiers['Bevel'].profile = profile
                        act_obj.modifiers['Bevel'].use_clamp_overlap = False
                        act_obj.modifiers['Bevel'].limit_method = 'WEIGHT'

 
                        if edges:
                            if MPM.subdiv_mode:
                                bpy.ops.transform.edge_bevelweight(value=1)
                            else:
                                bpy.ops.mesh.mark_sharp()
                                bpy.ops.transform.edge_crease(value=1)
                                for edg in bm.edges:
                                    if edg.index not in edges:
                                        edg.select=False
                                bpy.ops.transform.edge_bevelweight(value=1)
                                for edg in bm.edges:
                                    if edg.index not in edges:
                                        edg.select=False
                                
                                
                                    
                            bpy.ops.object.mode_set(mode='OBJECT')
                            if not MPM.subdiv_mode:
                                add_smooth()
                            act_obj.show_wire = True
                            act_obj.show_all_edges = True
 
                            args = (self, context)
                            self._bevel_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
                            self.first_mouse_x = event.mouse_x
 
                            self.width = act_obj.modifiers['Bevel'].width
                            self.segments = act_obj.modifiers['Bevel'].segments
                            self.profile = act_obj.modifiers['Bevel'].profile 
 
                            MPM.bevel_enabled = True
                            context.window_manager.modal_handler_add(self)
                            return {'RUNNING_MODAL'}
 
                        else:
                            if MPM.subdiv_mode: 
                                add_edge_bevel_weight()
                            else:
                                bpy.ops.mesh.select_all(action='DESELECT')
                                bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                bpy.ops.mesh.mark_sharp()
                                bpy.ops.transform.edge_crease(value=1)
                                bpy.ops.mesh.select_all(action='DESELECT')
                                bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                bpy.ops.transform.edge_bevelweight(value=1)
                                bpy.ops.mesh.select_all(action='DESELECT')
                                
                        act_obj.show_wire = True
                        act_obj.show_all_edges = True
 
                        if not MPM.subdiv_mode:
                            bpy.ops.object.mode_set(mode='OBJECT')
                            add_smooth()
                            bpy.ops.object.mode_set(mode='EDIT')
 
                    if not MPM.bevel_weight_enabled:
#                        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
#                            bpy.ops.mesh.select_all(action='DESELECT')

                        if edges:

                            if MPM.subdiv_mode:
                                if act_obj.data.edges[edges[0]].bevel_weight:
                                    bpy.ops.transform.edge_bevelweight(value=-1)
                                    for edg in bm.edges:
                                        if edg.index not in edges:
                                            edg.select=False
 
                                else:
                                    bpy.ops.transform.edge_bevelweight(value=1)
                                    for edg in bm.edges:
                                        if edg.index not in edges:
                                            edg.select=False
 
                                return {'CANCELLED'}
 
                            else:
                                if act_obj.data.edges[edges[0]].bevel_weight:
                                    bpy.ops.mesh.mark_sharp(clear=True)
                                    bpy.ops.transform.edge_crease(value=-1)
                                    for edg in bm.edges:
                                        if edg.index not in edges:
                                            edg.select=False
                                    bpy.ops.transform.edge_bevelweight(value=-1)
                                    for edg in bm.edges:
                                        if edg.index not in edges:
                                            edg.select=False
 
                                else:
                                    bpy.ops.mesh.mark_sharp()
                                    bpy.ops.transform.edge_crease(value=1)
                                    for edg in bm.edges:
                                        if edg.index not in edges:
                                            edg.select=False
                                    bpy.ops.transform.edge_bevelweight(value=1)
                                    for edg in bm.edges:
                                        if edg.index not in edges:
                                            edg.select=False
 
                                return {'CANCELLED'}
 
                            act_obj.show_wire = True
                            act_obj.show_all_edges = True
                    else:
                        if not edges:
                            MPM.bevel_weight_enabled = False
                        else:
                            MPM.keep_bevel_weight = False  
                            self.bevel_w_value = act_obj.data.edges[edges[0]].bevel_weight if edges else 1
                            self.edge_index = edges[0]
 
                else:
                    if context.object.mode == 'OBJECT' and MPM.bevel_weight_enabled:
                        MPM.keep_bevel_weight = True
 
                    for obj in context.selected_objects:
 
                        if obj.type != 'MESH':
                            obj.select=False
                        else:
                            bpy.context.scene.objects.active = obj
                            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                            obj.show_wire = True
                            obj.show_all_edges = True
 
                            is_bevel=False
                            for mod in obj.modifiers:
                                if mod.type == 'BEVEL':
                                    is_bevel=True
 
                            if not is_bevel:
                                
                                MPM.subdiv_mode = True if subdiv_mode else False

                                obj.modifiers.new("Bevel", "BEVEL")
                                obj.modifiers['Bevel'].width = bevel_width
                                obj.modifiers['Bevel'].segments = segments
                                obj.modifiers['Bevel'].profile = profile
                                obj.modifiers['Bevel'].use_clamp_overlap = False
                                obj.modifiers['Bevel'].limit_method = 'WEIGHT'    
                                bpy.ops.object.mode_set(mode='EDIT')
                                if MPM.subdiv_mode: 
                                    add_edge_bevel_weight()
                                else:
                                    bpy.ops.mesh.select_all(action='DESELECT')
                                    bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                    bpy.ops.mesh.mark_sharp()
                                    bpy.ops.transform.edge_crease(value=1)
                                    bpy.ops.mesh.select_all(action='DESELECT')
                                    bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                    bpy.ops.transform.edge_bevelweight(value=1)
                                    bpy.ops.mesh.select_all(action='DESELECT')
 
                            # update
                            if not MPM.subdiv_mode:
                                bpy.ops.object.mode_set(mode='EDIT')
                                bpy.ops.mesh.select_all(action='DESELECT')
                                bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                bpy.ops.mesh.mark_sharp()
                                bpy.ops.transform.edge_crease(value=1)
                                bpy.ops.mesh.select_all(action='DESELECT')
                                bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
                                bpy.ops.transform.edge_bevelweight(value=1)
                                bpy.ops.mesh.select_all(action='DESELECT')
                                
 
                #Auto Smooth
 
                        if not MPM.subdiv_mode:
                            bpy.ops.object.mode_set(mode='OBJECT')
                            add_smooth()
                        bpy.ops.object.mode_set(mode='OBJECT')
 
                bpy.context.scene.objects.active = act_obj    
                bpy.ops.object.mode_set(mode='OBJECT')
                args = (self, context)
                self._bevel_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
                self.first_mouse_x = event.mouse_x
 
                self.width = act_obj.modifiers['Bevel'].width
                self.segments = act_obj.modifiers['Bevel'].segments
                self.profile = act_obj.modifiers['Bevel'].profile 
 
                MPM.bevel_enabled = True
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
 
            else:
                self.report({'WARNING'}, "Active object is not a Mesh")
                return {'CANCELLED'}
 
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
