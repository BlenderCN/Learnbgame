import bpy
from mathutils import Vector
from bpy.types import Operator
from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       EnumProperty
                       )
from .utils.text_to_draw import *
from .utils.fonctions import *

 
class SymmetrizeModal(Operator):
    bl_idname = "object.symetrize_modal"
    bl_label = "Modal Symetrize"
    
    x_symmetrize = IntProperty(
            default=0,
            min=-1, max=1
            )
            
    y_symmetrize = IntProperty(
            default=0,
            min=-1, max=1
            )
            
    z_symmetrize = IntProperty(
            default=0,
            min=-1, max=1
            )
    
    axis_value = StringProperty()
    
    symmetrize_type = EnumProperty(
            items = (('add', "Add", ""),
                     ('only', "Only", "")),
                     default='only'
                     )
    
    
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
            axis_index = self.event_list.index(self.axis_value)
            
            if hit_world[axis_index] < self.mesh_center()[axis_index]:
                self.axis_value = "-" + self.axis_value
            
            self.setup_symmetrize()
    
    def setup_symmetrize(self):
        MPM = bpy.context.window_manager.MPM
        value = "{}_{}".format('POSITIVE' if self.axis_value.startswith("-") else 'NEGATIVE', self.axis_value.split("-")[-1].upper())
        if self.symmetrize_type == 'only':
            self.x_symmetrize = self.y_symmetrize = self.z_symmetrize = 0
            for obj in bpy.context.selected_objects:
                obj.data = MPM.meshes_list[obj.name].copy()
                obj.data.update()
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.symmetrize(direction=value)
                bpy.ops.object.mode_set(mode='OBJECT')
                
            if "x" in self.axis_value:
                self.x_symmetrize = -1 if self.axis_value.startswith("-") else 1
            elif "y" in self.axis_value:
                self.y_symmetrize = -1 if self.axis_value.startswith("-") else 1
            elif "z" in self.axis_value:
                self.z_symmetrize = -1 if self.axis_value.startswith("-") else 1
        
        elif self.symmetrize_type == 'add':
            for obj in bpy.context.selected_objects:
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.symmetrize(direction=value)
                bpy.ops.object.mode_set(mode='OBJECT')
            
            if "x" in self.axis_value:
                self.x_symmetrize = -1 if self.axis_value.startswith("-") else 1
            elif "y" in self.axis_value:
                self.y_symmetrize = -1 if self.axis_value.startswith("-") else 1
            elif "z" in self.axis_value:
                self.z_symmetrize = -1 if self.axis_value.startswith("-") else 1
             
        self.axis_value = ""
        
               
    def mesh_center(self):
        cursor_loc = bpy.context.scene.cursor_location.copy()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.view3d.snap_cursor_to_selected()
        mesh_center = bpy.context.scene.cursor_location.copy()
        bpy.ops.object.mode_set(mode='OBJECT') 
        bpy.context.scene.cursor_location = cursor_loc
        
        return mesh_center       
                        
    def modal(self, context, event):
        MPM = context.window_manager.MPM
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
                
        if event.shift and event.unicode.lower() in self.event_list:
            self.axis_value = event.unicode.lower()
            self.symmetrize_type = 'add'
            bpy.context.area.tag_redraw()
        
        elif event.alt and event.unicode.lower() in self.event_list:
            self.axis_value = event.unicode.lower()
             
            if self.axis_value == "x":
                self.x_symmetrize = 0
            elif self.axis_value == "y":
                self.y_symmetrize = 0
            elif self.axis_value == "z":
                self.z_symmetrize = 0
            
            for obj in context.selected_objects:
                obj.data = MPM.meshes_list[obj.name].copy()
                obj.data.update()
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                if self.x_symmetrize:
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_X' if self.x_symmetrize == -1 else 'NEGATIVE_X')
                if self.y_symmetrize:
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_Y' if self.y_symmetrize == -1 else 'NEGATIVE_Y')
                if self.z_symmetrize:
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_Z' if self.z_symmetrize == -1 else 'NEGATIVE_Z')
                bpy.ops.object.mode_set(mode='OBJECT')
            
            self.axis_value = ""
            
        
        elif event.unicode in self.event_list:
            self.axis_value = event.unicode.lower()
            self.symmetrize_type = 'only'
            bpy.context.area.tag_redraw()
              
 
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.axis_value:
                self.main_ray_cast(context, event)
               
            else:
                MPM.meshes_list.clear()
                MPM.symmetrize_enabled = False
                bpy.context.area.tag_redraw()
                bpy.types.SpaceView3D.draw_handler_remove(self._symmetrize_handle, 'WINDOW')
                return {'FINISHED'}
 
        elif event.type in {'RIGHTMOUSE', 'ESC', 'DEL', 'BACK_SPACE'}:
            if self.axis_value:
                self.axis_value = ""
            else:
                MPM.symmetrize_enabled = False
                self.x_symmetrize = self.y_symmetrize = self.z_symmetrize = 0
                self.axis_value = ""
                bpy.context.area.tag_redraw()
                for obj in context.selected_objects:
                    obj.data = MPM.meshes_list[obj.name].copy()
                    obj.data.update()
                MPM.meshes_list.clear()
                bpy.types.SpaceView3D.draw_handler_remove(self._symmetrize_handle, 'WINDOW')
                return {'CANCELLED'}
 
        return {'RUNNING_MODAL'}
 
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            MPM = context.window_manager.MPM
            MPM.symmetrize_enabled = True
            bpy.ops.object.mode_set(mode='OBJECT')
            self.event_list = ['x', 'y', 'z']
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    obj.select = False
                    pass
                bpy.context.scene.objects.active = obj
                MPM.meshes_list[obj.name] = obj.data.copy()
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.symmetrize(direction='POSITIVE_X')
                bpy.ops.object.mode_set(mode='OBJECT')
                self.x_symmetrize = -1
                
 
            args = (self, context)
 
            self._symmetrize_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_callback_mpm, args, 'WINDOW', 'POST_PIXEL')
 
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}