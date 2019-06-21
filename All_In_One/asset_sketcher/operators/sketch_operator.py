'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    
import bpy,bgl,blf
import bpy_extras
import bpy_extras.view3d_utils
from math import radians
import mathutils
from mathutils.bvhtree import BVHTree
from mathutils import Vector, Matrix, Quaternion
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent
from .. functions import *
from .. draw_callbacks import *
from collections import OrderedDict   
import random
    
import traceback
    
class SketchAssets(bpy.types.Operator):
    bl_idname = "asset_sketcher.sketch_assets"
    bl_label = "Sketch Assets"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def __init__(self):
        self.asset_preview = None
        ### mouse coords and information
        self.last_asset_pos = Vector()
        self.mouse_on_canvas = False
        self.projected_mouse = Vector((0,0,0))
        self.projected_mouse_hist = Vector((0,0,0))
        self.projected_mouse_last = Vector((0,0,0))
        self.projected_mouse_stamp = Vector((0,0,0))
        self.projected_mouse_direction = Vector((0,0,0))
        self.projected_mouse_direction_current = Vector((0,0,0))
        self.ground_normal = Vector((0,0,0))
        self.ground_normal_hist = Vector((0,0,0))
        self.ground_normal_current = Vector((0,0,0))
        self.ground_normal_mat = Matrix()
        self.mouse_on_plane = Vector((0,0,0))
        
        ### Button and Mouse Handling
        ### variables needed to check if buttons are released, just_pressed, pressed or just_released
        self.value_hist = ""
        self.value_pressed = False
        self.type_hist = ""
        
        self.mod_x = False
        self.mod_y = False
        self.mod_z = False
        
        
        self.brush_stroke = False
        self.scale_stroke = False
        self.delete_stroke = False
        self.ctrl = False
        self.shift = False
        self.alt = False
        self.f_key = False
        self.f_key_shift = False
        
        self.asset_item = None
        self.in_view_3d = False
        self.ray_data_list = []
        ### brush stroke data
        self.pen_pressure = 1.0
        
        self.stroke_start_pos = Vector()
        self.stroke_start_pos_ground_normal = Vector()
        self.stroke_start_pos2d = Vector()
        self.stroke_length = 0.0
        self.stroke_direction = Vector()
        self.stroke_distance = 0.0
        self.stroke_last_pos = Vector()
        self.stroke_assets = []
        
        self.sketch_plane_axis_idx = 0
        self.sketch_plane_axis = ["XY","XZ","YZ"]
        
        self.sketch_mode = ["PAINT","SCALE","GRID"]
        self.sketch_mode_idx = 0
        
        self.stroke_length = 0.0
        self.stroke_direction = Vector()
        self.asset_transform_queue = []
        self.asset_count = 0
        self.picked_asset_name = ""
        self.cyclic_item_idx = 0
        self.canvas_found = False
        self.timer = 0
        self.canvas_all = False 
        self.delete_objects_queue = []   
    
    @classmethod
    def poll(cls, context):
        return True
    
    _timer = None
    
    def invoke(self, context, event):
        wm = context.window_manager
        args = (context,event)
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        self.draw_handler2 = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_view, args, "WINDOW", "POST_VIEW")
        self._timer = wm.event_timer_add(0.001, context.window)
        context.window_manager.modal_handler_add(self)
        
        wm.asset_sketcher.sketch_mode_active = True
        
        if wm.asset_sketcher.sketch_mode == "PAINT":
            self.sketch_mode_idx = 0
        elif wm.asset_sketcher.sketch_mode == "SCALE":
            self.sketch_mode_idx = 1
        elif wm.asset_sketcher.sketch_mode == "GRID":
            self.sketch_mode_idx = 2
        
        if wm.asset_sketcher.sketch_plane_axis == "XY":
            self.sketch_plane_axis_idx = 0
        elif wm.asset_sketcher.sketch_plane_axis == "XZ":
            self.sketch_plane_axis_idx = 1
        elif wm.asset_sketcher.sketch_plane_axis == "YZ":
            self.sketch_plane_axis_idx = 2    
            
        
        return {"RUNNING_MODAL"} 
    
    def modal(self, context, event):
        self.timer += 1
        wm = context.window_manager
        self.set_pen_pressure(context,event)
        wm.asset_sketcher.pen_pressure = event.pressure
        try:
            if context.area != None:
                if context.area.type == "VIEW_3D":
                    context.area.tag_redraw()
                    
            ### change asset sketcher mode with m shortcut
            if event.type == "M" and event.value == "PRESS":
                self.sketch_mode_idx += 1
                wm.asset_sketcher.sketch_mode = self.sketch_mode[self.sketch_mode_idx%3]
            
                    
            ### check if mouse is within 3D view
            self.in_view_3d = self.check_region(context,event)
            
            
            ### get asset item if asset list is not emtpy, otherwise return None
            if len(wm.asset_sketcher.asset_list) > 0:
                self.asset_item = wm.asset_sketcher.asset_list[wm.asset_sketcher.asset_list_index]
                
                if self.asset_item.distance_constraint:
                    self.stroke_distance = wm.asset_sketcher.brush_size*0.5 * self.pen_pressure
                else:    
                    self.stroke_distance = self.asset_item.asset_distance 
            else:
                self.asset_item = None
            
            self.update_ray_data_with_position(context,event,depth=-1)            
                   
            
            ### search for canvas objects
            canvas_objects = []
            for canvas in wm.asset_sketcher.canvas_list:
                if canvas.canvas_item != None:
                    canvas_objects.append(canvas.canvas_item)
            for ray_data in self.ray_data_list:
                self.canvas_found = ("as_asset" not in ray_data[1] and not wm.asset_sketcher.use_canvas_objects) or (ray_data[1] in canvas_objects and wm.asset_sketcher.use_canvas_objects) or wm.asset_sketcher.canvas_all
                if self.canvas_found:
                    break
            
            ### If mouse is pressed and cursor is in View 3D perform brush stroke
            
            if wm.asset_sketcher.sketch_mode == "PAINT":
                self.paint_mode_handling(context,event)
            elif wm.asset_sketcher.sketch_mode == "SCALE":
                self.scale_mode_handling(context,event)
            elif wm.asset_sketcher.sketch_mode == "GRID":
                self.grid_mode_handling(context,event)
            self.asset_preview_handling(context,event)
            
            if not self.scale_stroke:
                self.delete_asset_handling(context,event)
                self.pick_asset_handling(context,event)
            
            
            ### store old event values in history variables
            if (self.projected_mouse - self.projected_mouse_stamp).length > .5*get_zoom(self,context)*.01:
                self.projected_mouse_direction = (self.projected_mouse - self.projected_mouse_stamp).normalized()
                self.projected_mouse_stamp = Vector(self.projected_mouse)
            self.projected_mouse_direction_current[0] = self.projected_mouse_direction_current[0] * 0.7 + self.projected_mouse_direction[0] * 0.3
            self.projected_mouse_direction_current[1] = self.projected_mouse_direction_current[1] * 0.7 + self.projected_mouse_direction[1] * 0.3
            self.projected_mouse_direction_current[2] = self.projected_mouse_direction_current[2] * 0.7 + self.projected_mouse_direction[2] * 0.3  
            
            self.value_hist = str(event.value)
            self.type_hist = str(event.type)
            self.projected_mouse_hist = Vector(self.projected_mouse)
            self.ground_normal_hist = Vector(self.ground_normal)
            
            ### exit Sketch Mode
            if ((event.type in {"ESC"} and event.value == "PRESS" and self.in_view_3d) or not wm.asset_sketcher.sketch_mode_active) and not self.f_key:
                return self.finish(wm)
            
            ### brush size handling
            self.set_brush_size(context,event)
            self.set_brush_density(context,event)
            
            ### cursor icon handling
            self.cursor_icon_handling(context,event)
            
            ### if left mouse is just pressed return running modal -> prevends setting the 3d cursor and other not wanted operations.
            if self.in_view_3d and (self.brush_stroke or self.scale_stroke or self.delete_stroke or event.type == "LEFTMOUSE") or event.type in ["F","Q","M"]:
                return{'RUNNING_MODAL'}
        except: 
            self.finish(wm)
            traceback.print_exc()    
        
        return {"PASS_THROUGH"}

    def finish(self,wm):
        wm.event_timer_remove(self._timer)
        
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler2, "WINDOW")
        bpy.context.window.cursor_modal_set("DEFAULT")
        wm.asset_sketcher.sketch_mode_active = False
        if self.asset_preview != None:
            self.delete_objects(self.get_parent_child_objects(self.asset_preview,[]))
            self.asset_preview = None
        return {"FINISHED"}

    def draw_callback_px(self,context,event):
        wm = context.window_manager
        if ((self.mouse_on_canvas and self.in_view_3d and wm.asset_sketcher.sketch_mode in ["PAINT","GRID"]) or self.f_key or event.ctrl) and not self.scale_stroke and not event.alt:
            draw_brush_cursor(self,context,event)
        if event.alt or self.f_key or self.f_key_shift or self.scale_stroke:
            draw_text(self,context,event)  

        if wm.asset_sketcher.sketch_mode == "SCALE":      
            draw_scale_line(self,context,event)
        
    def draw_callback_view(self,context,event):
        wm = context.window_manager        
        if wm.asset_sketcher.sketch_mode == "GRID":
            draw_grid(self,context,event)    
    
    def check_region(self,context,event):
        in_view_3d = False
        if context.area != None:
            if context.area.type == "VIEW_3D":
                t_panel = context.area.regions[1]
                n_panel = context.area.regions[3]
                
                view_3d_region_x = Vector((context.area.x + t_panel.width, context.area.x + context.area.width - n_panel.width))
                view_3d_region_y = Vector((context.region.y, context.region.y+context.region.height))
                
                if event.mouse_x > view_3d_region_x[0] and event.mouse_x < view_3d_region_x[1] and event.mouse_y > view_3d_region_y[0] and event.mouse_y < view_3d_region_y[1]:
                    in_view_3d = True
                else:
                    in_view_3d = False
            else:
                in_view_3d = False 
        return in_view_3d    
    
    
    def get_asset_name(self,context):
        if self.asset_item.type in ["EMPTY","OBJECT"]:
            return self.asset_item.name
        elif self.asset_item.type in ["GROUP"]:
            if self.asset_item.group_mode == "RANDOM":
                rand_idx = random.randint(0,len(self.asset_item.group_objects)-1)
                return self.asset_item.group_objects[rand_idx].name
            elif self.asset_item.group_mode == "CYCLIC":
                idx = self.cyclic_item_idx%(len(self.asset_item.group_objects))
                self.cyclic_item_idx += 1
                return self.asset_item.group_objects[idx].name
    
    def instance_object(self,ob,parent,asset_name,single_user = True):
        wm = bpy.context.window_manager
        
        new_ob = ob.copy()
        #new_ob = bpy.data.objects[ob.name].copy()
        if single_user:
            new_mesh_data = new_ob.data.copy()
            new_ob.data = new_mesh_data
        bpy.context.scene.objects.link(new_ob)
        new_ob.hide = False
        #new_ob.hide_select = False
        new_ob['as_asset'] = True
        new_ob['as_type'] = 'OBJECT'
        new_ob['as_asset_name'] = asset_name
        
        if wm.asset_sketcher.sketch_mode in ["GRID"]:
            if self.asset_item.offset_x != 0.0 or self.asset_item.offset_y != 0.0 or self.asset_item.offset_z != 0.0:
                grid_size = wm.asset_sketcher.sketch_grid_size
                new_ob["as_offset"] = str([self.asset_item.offset_x * grid_size,self.asset_item.offset_y * grid_size,self.asset_item.offset_z * grid_size])
        
        new_ob.select = False
        new_ob.name = ob.name + "_as"
        if ob != parent:
           new_ob.parent = parent
        else:
            new_ob.parent = None   
            
        new_ob.matrix_local = bpy.data.objects[ob.name].matrix_local
        
        new_ob.hide_select = self.asset_item.hide_select
                
            
        for child in ob.children:
            self.instance_object(child,new_ob,asset_name,single_user)
        return new_ob
    
    def snap_direction(self,context,dir_vec,):
        rot_mat = self.ground_normal.rotation_difference(Vector((0,0,1))).to_matrix().to_3x3()
        final_mat = rot_mat
        directions = []
        angle = 15
        start_vec = Vector((0,1,0))
        for i in range(int(360/angle)):
            rot = mathutils.Euler((0.0,0.0,math.radians(angle)), 'XYZ')
            
            rotated_vec = (Vector(start_vec).normalized() ) * final_mat
            
            directions.append(rotated_vec + Vector((.000005,0,0)))
            
            start_vec.rotate(rot)
        
        nearest_alignment = 0.0
        idx = 0
        for i,dir in enumerate(directions):
            alignment = dir.dot(dir_vec)
            if alignment > nearest_alignment:
                nearest_alignment = alignment
                idx = i
        return directions[idx]
        return dir_vec     
    
    def transform_object(self,context,event,obj,custom_direction=None,custom_ground_normal=None,custom_location=None,custom_scale=None,custom_z_offset=None,use_projection_offset=True,no_random_rot=False):
        wm = context.window_manager
        ### apply ground normal to asset
        if custom_ground_normal:
            ground_normal = custom_ground_normal + Vector((0.00001,0,0))
        else:
            ground_normal = self.ground_normal + Vector((0.00001,0,0))
            
        if wm.asset_sketcher.sketch_mode in ["PAINT","SCALE"]:
            fallback = Vector((0,0,1)).lerp(ground_normal,self.asset_item.surface_orient)
            ground_normal = Vector((0,0,1)).slerp(ground_normal,self.asset_item.surface_orient,fallback)
        elif wm.asset_sketcher.sketch_mode in ["GRID"]:
            ground_normal = Vector((0,0,1)).slerp(ground_normal,0,Vector((0,0,1)))
        surface_normal = Vector((0,0,1)).rotation_difference(ground_normal)
        mat_normal_rot = surface_normal.to_matrix().to_4x4()
        
        ### apply stroke direction to asset  
        mat_normal = surface_normal.to_matrix().to_4x4()
        
        ### dir_vec -> stroke direction multiplied with ground normal which gives the proper direction to rotate to
        dir_vec = Vector((0,1,0))
        if custom_direction == None:
            dir_vec = (self.stroke_direction - self.stroke_direction.dot(ground_normal) * ground_normal) * mat_normal
        elif custom_direction != None and not self.asset_item.use_no_rotation:
            #custom_direction = (self.projected_mouse - obj.location).normalized()
            dir_vec = (custom_direction - custom_direction.dot(ground_normal) * ground_normal) * mat_normal
        
        if dir_vec == Vector((0,0,0)):
            dir_vec = Vector((0,1,0)) 
        
        dir = Vector((0.0,1,0.0))
        object_direction = dir.rotation_difference(dir_vec)
        mat_direction_rot = object_direction.to_matrix().to_4x4()

        ### apply rotation settings to normal. Normal and Random rotation
        mat_rot = mathutils.Euler((self.asset_item.rot_x, self.asset_item.rot_y, self.asset_item.rot_z), 'XYZ').to_matrix().to_4x4()
        if no_random_rot:
            mat_rand_rot = mathutils.Matrix()
        else:
            mat_rand_rot = self.get_random_rotation()
        
        ### apply location to asset    
        loc = self.projected_mouse
        if custom_location != None:
            loc = custom_location
        
        if use_projection_offset:
            offset = ground_normal * 0.01 ### used so objects do not stand directly on the hit position. makes raycasting better
        else:
            offset = Vector((0,0,0))

        if custom_z_offset == None:
            z_offset = self.asset_item.z_offset * self.asset_item.scale * self.get_scale_pressure(context,event)
        else:
            z_offset = custom_z_offset
        
        rotated_z_offset = (Vector((0,0,1)) * mat_normal_rot.inverted()).normalized() * z_offset
            
        grid_offset = Vector((0,0,0))
        if wm.asset_sketcher.sketch_mode in ["GRID"]:
            grid_offset = Vector((self.asset_item.offset_x,self.asset_item.offset_y,self.asset_item.offset_z)) * wm.asset_sketcher.sketch_grid_size
        
        mat_loc = Matrix.Translation(loc + rotated_z_offset + offset + grid_offset)
        
        ### apply scale and random to asset
        random_scale = self.get_random_scale()
        
        scale_x = self.asset_item.scale
        scale_y = self.asset_item.scale
        scale_z = self.asset_item.scale
        if custom_scale == None:
            scale_x = self.asset_item.scale * self.get_scale_pressure(context,event) * random_scale[0]
            scale_y = self.asset_item.scale * self.get_scale_pressure(context,event) * random_scale[1]
            scale_z = self.asset_item.scale * self.get_scale_pressure(context,event) * random_scale[2]  
        elif custom_scale != None:# and not self.asset_item.use_no_scale:
            scale_x = custom_scale[0]
            scale_y = custom_scale[1]
            scale_z = custom_scale[2]    
        
        mat_scale = Matrix.Scale(scale_x,4,(0,1,0)) * Matrix.Scale(scale_y,4,(1,0,0)) * Matrix.Scale(scale_z,4,(0,0,1))
        
        
        ### apply final matrix onto object
        final_mat = mat_loc * mat_normal_rot * mat_direction_rot * mat_rot * mat_rand_rot * mat_scale
        obj.matrix_local = final_mat.to_4x4()
        obj.location = obj.location
    
    def get_parent_child_objects(self,obj,objs=[]):
        context = bpy.context
        
        
        if obj not in objs:
            objs.append(obj)    
        
        if obj.parent == None or obj.parent in objs:
            for child in obj.children:
                self.get_parent_child_objects(child,objs)
        elif obj.parent != None and obj.parent not in objs:
            self.get_parent_child_objects(obj.parent,objs)
                    
        return objs
    
    def get_random_rotation(self):
        random_rot_x = random.uniform(-self.asset_item.rand_rot_x*.5,self.asset_item.rand_rot_x*.5)
        random_rot_y = random.uniform(-self.asset_item.rand_rot_y*.5,self.asset_item.rand_rot_y*.5)
        random_rot_z = random.uniform(-self.asset_item.rand_rot_z*.5,self.asset_item.rand_rot_z*.5)
        
        rand_rot_mat = mathutils.Euler((random_rot_x, random_rot_y, random_rot_z), 'XYZ').to_matrix().to_4x4()
        return rand_rot_mat
    
    def get_random_scale(self):
        random_scale_x = random.uniform(1.0,self.asset_item.rand_scale_x)
        random_scale_y = random.uniform(1.0,self.asset_item.rand_scale_y)
        random_scale_z = random.uniform(1.0,self.asset_item.rand_scale_z)
        if self.asset_item.constraint_rand_scale:
            return random_scale_x,random_scale_x,random_scale_x
        else:
            return random_scale_x,random_scale_y,random_scale_z
    
    def set_pen_pressure(self,context,event):
        wm = context.window_manager
        if self.brush_stroke and wm.asset_sketcher.use_brush_size_pressure:
            self.pen_pressure = event.pressure
        return self.pen_pressure
    
    def get_scale_pressure(self,context,event):
        wm = context.window_manager
        pressure = 1.0
        if self.asset_item.scale_pressure:
            pressure = event.pressure
        return pressure
    
    ################################################################### BRUSH SIZE AND DENSITY ###################################################################        
    def set_brush_size(self,context,event):
        wm = context.window_manager
        if not event.shift and event.type == "F" and event.value == "PRESS" and not self.f_key:
            self.f_key = True
            self.brush_size_tmp = wm.asset_sketcher.brush_size
            self.stroke_start_pos2d = Vector((event.mouse_region_x,event.mouse_region_y))
        elif event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.f_key:
            self.f_key = False
        elif event.type in ["ESC","RIGHTMOUSE"] and event.value == "PRESS" and self.f_key:
            self.f_key = False
            wm.asset_sketcher.brush_size = self.brush_size_tmp
                    
        if self.f_key:
            zoom = (get_zoom(self,context) * get_zoom(self,context))*.0001
            mouse_pos = Vector((event.mouse_region_x,event.mouse_region_y))
            length = (self.stroke_start_pos2d - mouse_pos)
            wm.asset_sketcher.brush_size = self.brush_size_tmp + (-length[0])*zoom
    
    def set_brush_density(self,context,event):
        wm = context.window_manager
        if event.shift and event.type == "F" and event.value == "PRESS" and not self.f_key_shift:
            self.f_key_shift = True
            self.brush_density_tmp = wm.asset_sketcher.brush_density
            self.stroke_start_pos2d = Vector((event.mouse_region_x,event.mouse_region_y))
        elif event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.f_key_shift:
            self.f_key_shift = False
        elif event.type in ["ESC","RIGHTMOUSE"] and event.value == "PRESS" and self.f_key_shift:
            self.f_key_shift = False
            wm.asset_sketcher.brush_density = self.brush_density_tmp
                    
        if self.f_key_shift:
            zoom = (get_zoom(self,context) * get_zoom(self,context))*.0001
            mouse_pos = Vector((event.mouse_region_x,event.mouse_region_y))
            length = (self.stroke_start_pos2d - mouse_pos)
            wm.asset_sketcher.brush_density = self.brush_density_tmp + (-length[0])
            
            
    ################################################################### GET RAY DATA WITH 3D MOUSE COORDINATES ###################################################################        
    def update_ray_data_with_position(self,context,event,depth=-1,custom_position=None):
        wm = context.window_manager
        ### mouse projection on surface
        if event.alt:
            self.ray_data_list = project_cursor(self,context,event,depth=-1,custom_position=custom_position,ignore_assets=False)
        else:    
            self.ray_data_list = project_cursor(self,context,event,depth=-1,custom_position=custom_position,ignore_assets=not(wm.asset_sketcher.canvas_all))
        
        ### get first canvas item in list
        if wm.asset_sketcher.sketch_mode in ["SCALE","PAINT"]:
            self.mouse_on_canvas = False
            for ray_data in self.ray_data_list:
                
                canvas_objects = []
                for canvas in wm.asset_sketcher.canvas_list:
                    if canvas.canvas_item != None:
                        canvas_objects.append(canvas.canvas_item)
                canvas_found = ("as_asset" not in ray_data[1] and not wm.asset_sketcher.use_canvas_objects) or (ray_data[1] in canvas_objects and wm.asset_sketcher.use_canvas_objects) or wm.asset_sketcher.canvas_all
                if canvas_found:# and not self.scale_stroke and not "as_preview" in ray_data[1]:
                    self.mouse_on_canvas = True
                    if not self.f_key and not self.f_key_shift:
                        self.projected_mouse = ray_data[3]
                    
                        self.ground_normal = ray_data[4]
                        if hasattr(context.space_data,"region_3d"):
                            view_vec = Vector((0,0,1))
                            view_vec.rotate(context.space_data.region_3d.view_rotation)
                            #if ray_data[4].dot(view_vec) < 0.15:
                            if ray_data[4].dot(view_vec) < 0.0:
                                self.ground_normal = -ray_data[4]
                                print("test")
                            else:
                                print("")    
                                
                        self.ground_normal_current[0] = self.ground_normal_current[0] * 0.8 + self.ground_normal[0] * 0.2
                        self.ground_normal_current[1] = self.ground_normal_current[1] * 0.8 + self.ground_normal[1] * 0.2
                        self.ground_normal_current[2] = self.ground_normal_current[2] * 0.8 + self.ground_normal[2] * 0.2
                        
                        surface_normal = Vector((0,0,1)).rotation_difference(self.ground_normal)
                        self.ground_normal_mat = surface_normal.to_matrix().to_4x4()
                    break
            if (not self.mouse_on_canvas and not self.f_key) or self.scale_stroke:
                view_ray = get_view_ray(self,context,event)
                if view_ray != None:
                    point_on_plane = mathutils.geometry.intersect_line_plane(view_ray[0], view_ray[1], self.projected_mouse_hist, self.ground_normal_hist)
                    if point_on_plane != None:
                        self.projected_mouse = point_on_plane      
        
        elif wm.asset_sketcher.sketch_mode == "GRID":
            view_ray = get_view_ray(self,context,event)
            if view_ray != None:
                self.mouse_on_canvas = True
                
                if wm.asset_sketcher.sketch_plane_axis == "XY":
                    self.ground_normal = Vector((0,0,1))
                    layer = Vector((0,0,wm.asset_sketcher.sketch_layer*wm.asset_sketcher.sketch_grid_size))
                elif wm.asset_sketcher.sketch_plane_axis == "XZ":
                    self.ground_normal = Vector((0,-1,0))
                    layer = Vector((0,-wm.asset_sketcher.sketch_layer*wm.asset_sketcher.sketch_grid_size,0))
                elif wm.asset_sketcher.sketch_plane_axis == "YZ":
                    self.ground_normal = Vector((1,0,0))        
                    layer = Vector((wm.asset_sketcher.sketch_layer*wm.asset_sketcher.sketch_grid_size,0,0))
                
                
                
                self.projected_mouse = mathutils.geometry.intersect_line_plane(view_ray[0], view_ray[1], layer, self.ground_normal)
                if self.projected_mouse == None:
                    self.projected_mouse = Vector((0,0,0))             
                self.projected_mouse[0] = snap_value(self.projected_mouse[0],wm.asset_sketcher.sketch_grid_size)
                self.projected_mouse[1] = snap_value(self.projected_mouse[1],wm.asset_sketcher.sketch_grid_size)
                self.projected_mouse[2] = snap_value(self.projected_mouse[2],wm.asset_sketcher.sketch_grid_size)
    
            
    ################################################################### ASSET PREVIEW HANDLING ###################################################################        
    def asset_preview_handling(self,context,event):
        wm = context.window_manager
        self.asset_preview = bpy.data.objects["__as_preview_asset__"] if "__as_preview_asset__" in bpy.data.objects else None
        if self.asset_preview == None and wm.asset_sketcher.asset_preview:
            active_obj = context.scene.objects.active
            context.scene.objects.active = None
            selected_objects = []
            cursor_location = Vector(context.scene.cursor_location)
            for obj in context.scene.objects:
                if obj.select:
                    selected_objects.append(obj)
                    obj.select = False
            
            if self.asset_item.type == "EMPTY":
                if self.asset_item.name not in bpy.data.objects:
                    return
                for obj in bpy.data.objects[self.asset_item.name].dupli_group.objects:
                    if obj.parent == None:
                        
                        reference_obj = obj
                        self.asset_preview = self.instance_object(reference_obj,reference_obj,self.asset_item.name,True)
                        if self.asset_preview == None:
                            return
                        self.asset_preview.select = True
                        context.scene.cursor_location = self.asset_preview.location - obj.location
                        for child in self.asset_preview.children:
                            child.select = True
                        context.scene.objects.active = self.asset_preview
                
                if len(context.selected_objects) > 1:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    bpy.ops.object.join()
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
     
            elif self.asset_item.type in ["OBJECT","GROUP"]:
                asset_name = self.get_asset_name(context)
                if asset_name not in bpy.data.objects:
                    return    
                reference_obj = bpy.data.objects[asset_name]
                self.asset_preview = self.instance_object(reference_obj,reference_obj,self.asset_item.name,True)
                self.asset_preview.select = True
                for child in self.asset_preview.children:
                    child.select = True
                context.scene.objects.active = self.asset_preview
                if len(context.selected_objects) > 1:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    bpy.ops.object.join()
            
            layers = []
            for i in range(len(self.asset_preview.layers)):
                layers.append(True)
            self.asset_preview.layers = layers
            
            self.asset_preview.name = "__as_preview_asset__"
            self.asset_preview["as_preview"] = True
            self.asset_preview["as_asset_name"] = self.asset_item.name
            del (self.asset_preview["as_asset"])
            self.asset_preview.hide_select = True
            self.asset_preview.select = False
            
            context.scene.cursor_location = cursor_location
            for obj in selected_objects:
                obj.select = True
            if active_obj != self.asset_preview:  
                context.scene.objects.active = active_obj
            
        elif self.asset_preview != None and wm.asset_sketcher.asset_preview:
            if ((self.scale_stroke or self.brush_stroke) and not self.asset_preview.hide) or event.ctrl or event.alt or not self.in_view_3d:
                self.asset_preview.hide = True
            elif not self.scale_stroke and not self.brush_stroke and self.asset_preview.hide:    
                self.asset_preview.hide = False
                
            custom_z_offset = self.asset_item.z_offset * self.asset_item.scale
            custom_location = self.projected_mouse
            
            if self.asset_item.stroke_orient:
                custom_dir = self.projected_mouse_direction_current
            else:
                custom_dir = Vector((0,1,0))
            
            self.transform_object(context,event,self.asset_preview,custom_direction=custom_dir,custom_z_offset=custom_z_offset,custom_ground_normal=self.ground_normal_current, custom_scale = Vector((self.asset_item.scale,self.asset_item.scale,self.asset_item.scale)),no_random_rot=True)
            
            if "as_asset_name" in self.asset_preview and self.asset_preview["as_asset_name"] != self.asset_item.name:
                self.delete_objects(self.get_parent_child_objects(self.asset_preview,[]))
                self.asset_preview = None
                    
            #self.asset_transform_queue.append([new_asset,hit_position,ground_normal,self.projected_mouse])
        elif self.asset_preview != None and not wm.asset_sketcher.asset_preview:
            self.delete_objects(self.get_parent_child_objects(self.asset_preview,[]))
            self.asset_preview = None
            
    
    ################################################################### DELETE ASSETS HANDLING ###################################################################
    
    def get_linked_verts(self,bm,start_verts):
        verts = {}
        for vert in start_verts:
            verts[vert] = None

        prev_verts = verts
        while True:
            new_verts = {}
            
            for vert in prev_verts.keys():
                edges = vert.link_edges
                for edge in edges:
                    other = edge.other_vert(vert)
                    if other not in verts:
                        new_verts[other] = None
            for vert in new_verts.keys():
                vert.select = True
                verts[vert] = None
            
            prev_verts = new_verts
            
            if len(new_verts.keys()) == 0:
                break 
        return list(verts.keys())
    
    def delete_asset_handling(self,context,event):
        wm = context.window_manager
                
        if event.type == "LEFTMOUSE" and event.value == "PRESS" and self.in_view_3d and event.ctrl and not event.shift:
            self.delete_stroke = True
        elif event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.delete_stroke:
            self.delete_stroke = False
            bpy.ops.ed.undo_push(message="Delete Stroke")
            
        #if self.mouse_on_canvas and ((event.type == "LEFTMOUSE" and event.value == "PRESS") or event.type == "MOUSEMOVE") and self.delete_stroke and event.ctrl:
        if ((event.type == "LEFTMOUSE" and event.value == "PRESS") or event.type == "MOUSEMOVE") and self.delete_stroke and event.ctrl:
            merge_object = None
            face_index = None
            for ray_data in self.ray_data_list:
                if "as_merge_object" in ray_data[1]:
                    merge_object = ray_data[1]
                    face_index = ray_data[5]
                    break
                    
            for i,ray_data in enumerate(self.ray_data_list):
                obj = ray_data[1]
                if wm.asset_sketcher.sketch_mode in ["SCALE","PAINT"] and not "as_merge_object" in obj:
                    if i == 0:
                        if "as_asset" in obj and "as_dupli_group" not in obj and "as_preview" not in obj:
                            if (wm.asset_sketcher.delete_only_selected and obj.select) or not wm.asset_sketcher.delete_only_selected:
                                delete_objects = self.get_parent_child_objects(obj,[])
                                for o in delete_objects:
                                    if o not in self.delete_objects_queue:
                                        self.delete_objects_queue.append(o)
                    for obj in bpy.context.visible_objects:
                        distance = (obj.location - self.projected_mouse).length
                        
                        if distance < wm.asset_sketcher.brush_size*.5*self.pen_pressure and "as_asset" in obj and "as_preview" not in obj and "as_merge_object" not in obj:
                            if (wm.asset_sketcher.delete_only_selected and obj.select) or not wm.asset_sketcher.delete_only_selected:
                                delete_objects = self.get_parent_child_objects(obj,[])
                                for o in delete_objects:
                                    if o not in self.delete_objects_queue:
                                        self.delete_objects_queue.append(o)
                ############## Delete meshes in Merge Object ###############################################
                if wm.asset_sketcher.sketch_mode in ["SCALE","PAINT"]:
                    for obj in context.visible_objects:
                        if ("as_merge_object" in obj):# and obj.name == context.scene.asset_sketcher.merge_object):
                            context.scene.objects.active = obj
                            
                            distance = (obj.matrix_world.inverted() * Vector((wm.asset_sketcher.brush_size*.5,0,0))).magnitude
                            coord = obj.matrix_world.inverted() * ray_data[3]
                            
                            bpy.ops.object.mode_set(mode="EDIT")
                            bm = bmesh.from_edit_mesh(obj.data)
                            bm.faces.ensure_lookup_table()
                            bm.verts.ensure_lookup_table()
                            delete_verts = []
                            if face_index != None and face_index < len(bm.faces):
                                delete_verts.append(bm.faces[face_index].verts[0])
                                face_index = None
                            for vert in bm.verts:
                                if (vert.co - coord).magnitude < distance:
                                    delete_verts.append(vert)
                            delete_verts = self.get_linked_verts(bm,delete_verts)    
                            bmesh.ops.delete(bm,geom=delete_verts,context=1)
                            bmesh.update_edit_mesh(obj.data)
                            bpy.ops.object.mode_set(mode="OBJECT")
                            
            if wm.asset_sketcher.sketch_mode == "GRID":
                for obj in bpy.context.visible_objects:
                    
                    grid_offset = Vector((0,0,0))
                    if "as_offset"in obj:
                        grid_offset = Vector(eval(obj["as_offset"]))
                    distance = (obj.location - (self.projected_mouse+grid_offset)).length            

                    if distance < wm.asset_sketcher.sketch_grid_size * .5 and "as_asset" in obj and "as_preview" not in obj:
                        if (wm.asset_sketcher.delete_only_selected and obj.select) or not wm.asset_sketcher.delete_only_selected:
                            delete_objects = self.get_parent_child_objects(obj,[])
                            for o in delete_objects:
                                if o not in self.delete_objects_queue:
                                    self.delete_objects_queue.append(o)
            
            ### delete objects in queue
            self.delete_objects(self.delete_objects_queue)
                           
            
    def delete_objects(self,objs):
        context = bpy.context
        for obj in objs: 
            if obj.name in context.scene.objects:
                bpy.data.objects.remove(obj,do_unlink=True) 
        self.delete_objects_queue = []     

    ################################################################### CURSOR ICON HANDLING ###################################################################
    def cursor_icon_handling(self,context,event):
        if (event.alt and not (event.ctrl and (self.f_key or self.f_key_shift)) and not self.scale_stroke  and not self.brush_stroke) or (event.shift and event.ctrl):
            bpy.context.window.cursor_modal_set("EYEDROPPER")
        elif event.ctrl and not (event.alt or (self.f_key or self.f_key_shift)) and not self.scale_stroke:
            bpy.context.window.cursor_modal_set("KNIFE")
        elif (self.f_key or self.f_key_shift) and not (event.alt and event.ctrl):
            bpy.context.window.cursor_modal_set("SCROLL_X")    
        elif not event.alt and not event.ctrl and self.in_view_3d:
            if self.brush_stroke:
                bpy.context.window.cursor_modal_set("PAINT_BRUSH")
            elif self.scale_stroke:
                bpy.context.window.cursor_modal_set("SCROLL_XY")
            else:
                bpy.context.window.cursor_modal_set("PAINT_BRUSH")
            
        elif not event.alt and not event.ctrl and not self.in_view_3d:
            bpy.context.window.cursor_modal_set("DEFAULT")
    
    
    ################################################################### PICK ASSET HANDLING ###################################################################
    def pick_asset_handling(self,context,event):
        wm = context.window_manager
        asset_sketcher = wm.asset_sketcher
        if event.alt:
            self.picked_asset_name  = ""
            asset_name = ""
            for ray_data in self.ray_data_list:
                if "as_asset" in ray_data[1]:
                    obj = ray_data[1]
                    if "as_asset_name" in obj:
                        asset_name = obj["as_asset_name"]
                    elif "as_merge_object" in obj:
                        asset_name = obj.name    
                    elif "as_dupli_group" in obj:
                        asset_name = obj["as_dupli_group"]
                    self.picked_asset_name = asset_name           
            if event.type == "LEFTMOUSE" and event.value == "PRESS" and self.in_view_3d:
                for i,item in enumerate(context.window_manager.asset_sketcher.asset_list):
                    if item.name == asset_name:
                        if len(item.categories) > 0:
                            category = item.categories[0].name
    
                        try:
                            wm.asset_sketcher.categories_enum = category
                        except:
                            wm.asset_sketcher.categories_enum = "DEFAULT"
                        
                        found_in_active_cat = False        
                        for i,item in enumerate(asset_sketcher.display_asset_list):
                            if item.name == asset_name:
                                asset_sketcher.display_asset_list_index = i
        
        ### pick layer for grid mode
        if event.ctrl and event.shift:    
            if event.type == "RIGHTMOUSE" and event.value == "RELEASE" and self.in_view_3d:
                obj = context.active_object
                if obj != None:
                    obj.select = False
                    context.scene.objects.active = None
                    
                    if asset_sketcher.sketch_plane_axis == "XY":
                        layer = obj.location[2] / asset_sketcher.sketch_grid_size
                        asset_sketcher.sketch_layer = layer
                    elif asset_sketcher.sketch_plane_axis == "XZ":
                        layer = obj.location[1] / asset_sketcher.sketch_grid_size
                        asset_sketcher.sketch_layer = -layer
                    elif asset_sketcher.sketch_plane_axis == "YZ":
                        layer = obj.location[0] / asset_sketcher.sketch_grid_size
                        asset_sketcher.sketch_layer = layer        
    
    
    
    ################################################################### SCALE MODE HANDLING ###################################################################
    def calc_average_object_scale(self,obj):
        if obj.type == "MESH":
            return (obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2]) / 3
        elif obj.type == "EMPTY":
            if len(obj.dupli_group.objects) > 0:
                average = 0
                for i,obj in enumerate(obj.dupli_group.objects):
                    obj_average  = (obj.dimensions[0] * obj.dimensions[1] * obj.dimensions[2]) / 3
                    if obj_average > average:
                        average = obj_average
                return average
            else:
                return 1.0        
                
    
    def get_mouse_on_plane(self,context,event,coord,normal):
        view_ray = get_view_ray(self,context,event)
        if view_ray != None:
            point_on_plane = mathutils.geometry.intersect_line_plane(view_ray[0], view_ray[1], coord, normal)
            if point_on_plane != None:
                return point_on_plane  
            else:
                return Vector((0,0,0))
        return Vector((0,0,0))
    
    def scale_mode_handling(self,context,event):
        wm = context.window_manager
        
        
        ### check for press states and set undo and brush stroke
        if event.type == "LEFTMOUSE" and event.value == "PRESS" and self.in_view_3d and self.mouse_on_canvas and not event.ctrl and not self.f_key and not self.f_key_shift and not event.alt:
            self.scale_stroke = True
            self.stroke_start_pos = self.projected_mouse
            self.stroke_start_pos_ground_normal = self.ground_normal
            
            asset_name = self.get_asset_name(context)
            if asset_name not in bpy.data.objects:
                return
            reference_obj = bpy.data.objects[asset_name]
            
            new_asset = self.instance_object(reference_obj,reference_obj,self.asset_item.name,self.asset_item.make_single_user)
            self.transform_object(context,event,new_asset)
            
            asset_dimension_average = self.calc_average_object_scale(new_asset)
            self.asset_transform_queue.append([new_asset,self.projected_mouse,self.ground_normal,asset_dimension_average])
            self.stroke_assets.append(new_asset)
            self.random_scale = self.get_random_scale()
            
        elif event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.scale_stroke:
            ### merge assets into merge object
            if len(self.stroke_assets) > 0 and context.scene.asset_sketcher.merge_object != "":
                assets = self.convert_group_instance(context,wm,self.stroke_assets)
                self.merge_asset(context,wm,assets)
            self.stroke_assets = []    
            
            self.scale_stroke = False
            self.asset_transform_queue = []
            bpy.ops.ed.undo_push(message="Scale Stroke")
        
        if self.scale_stroke and not self.f_key:
            zoom = get_zoom(self,context)/400
            
            for item in self.asset_transform_queue:
                asset = item[0]
                projected_mouse_hist = item[1]
                ground_normal = item[2]
                dimension_average = item[3]
                
                self.mouse_on_plane = self.get_mouse_on_plane(context,event,self.stroke_start_pos,self.stroke_start_pos_ground_normal)
                
                
                self.stroke_direction = (self.mouse_on_plane - self.stroke_start_pos).normalized()   

                multiplier = (.1 * (1/math.pow(dimension_average,1/2.0)) + 1 * .9) / self.asset_item.scale
                
                self.stroke_length = (self.stroke_start_pos - self.mouse_on_plane).length * multiplier
                if event.shift:
                    self.stroke_direction = self.snap_direction(context,self.stroke_direction)
                    
                custom_direction = self.stroke_direction
                
                if event.ctrl:
                    zoom_snap = max(snap_value(get_zoom(self,context) / 280,.1),.1)
                    self.stroke_length = snap_value(self.stroke_length,grid=zoom_snap)
                self.stroke_length = max(self.stroke_length,0.0001)
                if not self.asset_item.use_no_scale:
                    custom_scale = self.asset_item.scale * Vector((self.stroke_length,self.stroke_length,self.stroke_length))
                else:
                    custom_scale = Vector(self.random_scale)
                
                if self.asset_item.use_no_scale:
                    custom_z_offset = None
                else:    
                    custom_z_offset = self.asset_item.z_offset * self.asset_item.scale * (self.stroke_length/self.asset_item.scale)
                    
                location = projected_mouse_hist
                self.transform_object(context,event,asset,custom_direction=custom_direction,custom_ground_normal=ground_normal,custom_location=location,custom_scale=custom_scale,custom_z_offset=custom_z_offset)
    
    ################################################################### GRID MODE HANDLING ###################################################################
    def grid_mode_handling(self,context,event):
        wm = context.window_manager
        
        if event.type == "Q" and event.value == "PRESS":
            self.sketch_plane_axis_idx += 1
            wm.asset_sketcher.sketch_plane_axis = self.sketch_plane_axis[self.sketch_plane_axis_idx%3]
            
        
        ### check for press states and set undo and brush stroke
        if event.type == "LEFTMOUSE" and event.value == "PRESS" and self.in_view_3d and not event.alt:
            self.brush_stroke = True
            if self.mouse_on_canvas:
                self.stroke_start_pos = Vector(self.projected_mouse)
            else:
                self.stroke_start_pos = Vector((float('inf'),float('inf'),float('inf')))
            
        elif event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.brush_stroke:
            ### merge assets into merge object
            if len(self.stroke_assets) > 0 and context.scene.asset_sketcher.merge_object != "":
                assets = self.convert_group_instance(context,wm,self.stroke_assets)
                self.merge_asset(context,wm,assets)
            self.stroke_assets = []   
            
            self.brush_stroke = False
            self.asset_transform_queue = []
            if self.asset_count > 0:
                bpy.ops.ed.undo_push(message="Grid Stroke")
                self.asset_count = 0
        
        if event.type == "PAGE_UP" and event.value == "PRESS":
            wm.asset_sketcher.sketch_layer += 1
        elif event.type == "PAGE_DOWN" and event.value == "PRESS":
            wm.asset_sketcher.sketch_layer -= 1
                    
                
                
        if self.brush_stroke and not event.ctrl and not self.f_key and not self.f_key_shift:
            brush_vec = self.stroke_start_pos - Vector(self.projected_mouse)
            current_length = (brush_vec).length
            inbetween_objs = int(current_length/self.stroke_distance) if self.asset_count != 0 else 1
                    
            self.stroke_length = (self.stroke_start_pos - self.projected_mouse).length
            
            asset_found = False
            for obj in context.visible_objects:
                grid_offset = Vector((0,0,0))
                if "as_offset"in obj:
                    grid_offset = Vector(eval(obj["as_offset"]))
                if "as_asset" in obj and obj.location - grid_offset == self.projected_mouse and "as_asset_name" in obj and obj["as_asset_name"] == self.asset_item.name:
                    asset_found = True
                    break
                
            
            for item in self.asset_transform_queue:
                asset = item[0]
                projected_mouse_hist = item[1]
                ground_normal = item[2]
                custom_direction = self.projected_mouse - item[3]
                location = projected_mouse_hist
                if self.asset_item.stroke_orient:
                    self.transform_object(context,event,asset,custom_direction=custom_direction,custom_ground_normal=ground_normal,custom_location=location,custom_z_offset=0,use_projection_offset=False)
                else:
                    self.transform_object(context,event,asset,custom_direction=Vector((0,1,0)),custom_ground_normal=ground_normal,custom_location=location,custom_z_offset=0,use_projection_offset=False)
            
            #if (self.stroke_length >= wm.asset_sketcher.sketch_grid_size or self.asset_count == 0) and not asset_found:
            if not asset_found:    
                self.asset_transform_queue = []
                self.stroke_start_pos = self.projected_mouse
                
                asset_name = self.get_asset_name(context)
                if asset_name not in bpy.data.objects:
                    return
                reference_obj = bpy.data.objects[asset_name]
                
                new_asset = self.instance_object(reference_obj,reference_obj,self.asset_item.name,self.asset_item.make_single_user)
                self.transform_object(context,event,new_asset,use_projection_offset=False)        
                self.asset_count += 1
                self.asset_transform_queue.append([new_asset,self.projected_mouse,self.ground_normal,self.projected_mouse])
                self.stroke_assets.append(new_asset)
    
    
    ################################################################### PAINT MODE HANDLING ###################################################################
    def create_new_merge_object(self,context,wm):
        ob_data = bpy.data.meshes.new(context.scene.asset_sketcher.merge_object)
        merge_object = bpy.data.objects.new(context.scene.asset_sketcher.merge_object,ob_data)
        context.scene.objects.link(merge_object)
        return merge_object
    
    def convert_group_instance(self,context,wm,assets):
        for obj in context.selected_objects:
            obj.select = False
        for obj in assets:
            obj.select = True
        bpy.ops.object.duplicates_make_real(use_base_parent=False,use_hierarchy=False)
        for obj in context.selected_objects:
            if obj.type == "EMPTY" and obj.dupli_type == "NONE":
                bpy.data.objects.remove(obj,do_unlink=True)
        return context.selected_objects        
    
    def merge_asset(self,context,wm,assets):
        if context.scene.asset_sketcher.merge_object != "":
            merge_obj = bpy.data.objects[context.scene.asset_sketcher.merge_object] if context.scene.asset_sketcher.merge_object in bpy.data.objects else self.create_new_merge_object(context,wm)
        
#            for obj in assets:
#                pos = list(obj.matrix_world.to_translation())
#                pos = [round(pos[0],4),round(pos[1],4),round(pos[2],4)]
#                name = str(pos)
#                group = obj.vertex_groups.new(name)
#                index = range(0,len(obj.data.vertices))    
#                group.add(index,1.0,"ADD")
        
            if "as_asset" not in merge_obj:
                merge_obj["as_asset"] = True
            if "as_merge_object" not in merge_obj:
                merge_obj["as_merge_object"] = True
            if merge_obj != None:
                bpy.context.scene.objects.active = None
                for obj in context.scene.objects:
                    obj.select = False
                for asset in assets: 
                    asset.select = True
                merge_obj.select = True
                context.scene.objects.active = merge_obj
                bpy.ops.object.join()
                
    def paint_mode_handling(self,context,event):
        wm = context.window_manager
        ### check for press states and set undo and brush stroke
        if event.type == "LEFTMOUSE" and event.value == "PRESS" and self.in_view_3d and not event.alt and self.canvas_found:
            self.brush_stroke = True
            if self.mouse_on_canvas:
                self.stroke_start_pos = Vector(self.projected_mouse)
            else:
                self.stroke_start_pos = Vector((float('inf'),float('inf'),float('inf')))
        
        elif (event.type == "LEFTMOUSE" and event.value == "RELEASE" and self.brush_stroke):
            ### merge assets into merge object
            if len(self.stroke_assets) > 0 and context.scene.asset_sketcher.merge_object != "":
                assets = self.convert_group_instance(context,wm,self.stroke_assets)
                self.merge_asset(context,wm,assets)
            self.stroke_assets = []    
            
            self.brush_stroke = False
            self.asset_transform_queue = []
            if self.asset_count > 0:
                bpy.ops.ed.undo_push(message="Brush Stroke")
                self.asset_count = 0
        
        ### run only if mouse projects on a canvas and mouse is within 3d view and not on ui elements
        if not self.mouse_on_canvas:
            self.asset_transform_queue = []
            #self.stroke_assets = []
            self.brush_stroke = False
        
        if True:#else:
            ### create assets and transform them if brush stroke is executed
            if ((event.type == "LEFTMOUSE" and event.value == "PRESS") or event.type == "MOUSEMOVE") and self.brush_stroke and not event.ctrl and not self.f_key and not self.f_key_shift:
                ### get stroke direction of cursor
                self.stroke_direction = (self.projected_mouse - self.stroke_start_pos).normalized()
                self.stroke_length = (self.stroke_start_pos - self.projected_mouse).length
                    
                
                if self.stroke_direction != Vector((0,0,0)) and self.stroke_length > .5:
                    ### apply transformations for asset queue. needed for directional vector
                    for item in self.asset_transform_queue:
                        asset = item[0]
                        projected_mouse_hist = item[1]
                        ground_normal = item[2]
                        
                        custom_direction = (self.projected_mouse - item[3]).normalized()
                        location = item[4]#self.projected_mouse_last
                        if self.asset_item.stroke_orient:
                            self.transform_object(context,event,asset,custom_direction=custom_direction,custom_ground_normal=ground_normal,custom_location=location)
                        else:
                            self.transform_object(context,event,asset,custom_direction=Vector((0,1,0)),custom_ground_normal=ground_normal,custom_location=location)
            
                self.update_ray_data_with_position(context,event,depth=-1)
                ### add new assets if min stroke distance is reached or asset count is yet 0
                if self.stroke_length > self.stroke_distance or self.asset_count == 0:
                    self.projected_mouse_last = Vector(self.projected_mouse) if self.asset_count == 0 else self.projected_mouse_last
                    brush_vec = self.stroke_start_pos - Vector(self.projected_mouse)
                    current_length = (brush_vec).length
                    inbetween_objs = int(current_length/self.stroke_distance) if self.asset_count != 0 else 1

                    self.stroke_start_pos = Vector(self.projected_mouse)
                    
                    self.asset_transform_queue = []
                    if self.asset_count == 1 and inbetween_objs > 1:
                        inbetween_objs -= 1
                    for j in range(inbetween_objs):
                        rot_mat = self.ground_normal.rotation_difference(Vector((0,0,1))).to_matrix().to_3x3()
                        ### loop over amount of the density settings
                        for i in range(wm.asset_sketcher.brush_density):
                            ### calc random distribution within brush circle
                            angle = 2 * math.pi * random.random()
                            radius = wm.asset_sketcher.brush_size*.5 * math.sqrt(random.random()) * self.pen_pressure
                            
                            
                            x = radius * math.cos(angle) + self.projected_mouse[0]
                            y = radius * math.sin(angle) + self.projected_mouse[1]
                            z = self.projected_mouse[2]
                            
                            ### rotate random point within the ground normal 
                            p = Vector((x,y,z))
                            p -= self.projected_mouse
                            p = p * rot_mat
                            p += self.projected_mouse
                            
                            final_p = p + (brush_vec.normalized() * current_length * ((j) / (inbetween_objs)))
                            start = final_p + (self.ground_normal *  get_zoom(self,context)*.001*10000)
                            end  = final_p - (self.ground_normal * wm.asset_sketcher.brush_size*.5*100000)
                            
                            p_ray_data = xray_cast(start, end, depth = -1, delta = 0.0001, ignore_assets=not(wm.asset_sketcher.canvas_all))
                            index = 0
                            p_ray_distance = 1000000
                            for i,ray_data in enumerate(p_ray_data):
                                if (final_p - ray_data[3]).length < p_ray_distance:
                                    index = i
                                    p_ray_distance = (final_p - ray_data[3]).length    
                            if len(p_ray_data) > 0 and ((final_p - p_ray_data[index][3]).length < current_length*1.5 or self.asset_count == 0):
                                #if "as_asset" not in p_ray_data[index][1] or wm.asset_sketcher.canvas_all:
                                if True:
                                    ground_normal = p_ray_data[index][4]
                                    if hasattr(context.space_data,"region_3d"):
                                        view_vec = Vector((0,0,1))
                                        view_vec.rotate(context.space_data.region_3d.view_rotation)
                                        #if p_ray_data[index][4].dot(view_vec) < -.3:
                                        if p_ray_data[index][4].dot(view_vec) < 0.0:
                                            ground_normal = -p_ray_data[index][4]
                                            ground_normal_direction = -1
                                    
                                    
                                    hit_position = p_ray_data[index][3]
                                    
                        
                                    ### place new assets into scene
                                    asset_name = self.get_asset_name(context)
                                    if asset_name not in bpy.data.objects:
                                        return  
                                    reference_obj = bpy.data.objects[asset_name]
                                    slope = abs(Vector((0,0,1)).dot(ground_normal))
                                    #if ("as_asset" not in self.ray_data_list[0][1] or wm.asset_sketcher.canvas_all or j > 1) and slope >= self.asset_item.slope_threshold:
                                    if True:
                                        #place new asset
                                        if self.asset_item.stroke_orient:
                                            dir = self.stroke_direction#(self.projected_mouse - hit_position).normalized()
                                        else:
                                            dir = Vector((0,1,0))
                                             
                                        new_asset = self.instance_object(reference_obj,reference_obj,self.asset_item.name,self.asset_item.make_single_user)
                                        self.stroke_assets.append(new_asset)
                                        
                                        #self.transform_object(context,event,new_asset,custom_location=hit_position,custom_direction=dir*rot_mat,custom_ground_normal=ground_normal)
                                        if j == 0:
                                            #new_asset.color = [1,0,0,1]
                                            self.transform_object(context,event,new_asset,custom_location=hit_position,custom_direction=dir,custom_ground_normal=ground_normal)
                                            previous_asset = new_asset
                                            self.asset_transform_queue.append([new_asset,hit_position,ground_normal,Vector(self.projected_mouse_last),hit_position])
                                        else:
                                            self.transform_object(context,event,new_asset,custom_location=hit_position,custom_direction=dir,custom_ground_normal=ground_normal)
                                            
                                        self.projected_mouse_last = Vector(self.projected_mouse)
                                            
                        self.asset_count += 1                 
            
    
        
