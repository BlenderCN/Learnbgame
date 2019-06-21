# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2011: Benjamin Walther-Franks, bwf@tzi.de

from .mpathutils import MotionPath
from .timingutils import FrameTimer, TimeMap, apply_action, retime_action, resample_action
from math import floor, ceil
from mathutils import Vector
import bpy
import time


class PerformTimeOperator(bpy.types.Operator):
    '''
       Performance Timing Tools Base Class
    '''
    
    bl_idname = ""
    bl_label = "PerformTime"
    bl_options = {'UNDO'}
    area_type = None
    props = None
    debug = False
    
    
    def __str__(self):
        return self.bl_label
    
    
    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return(False)
        return(context.active_object.mode in ['OBJECT', 'POSE'])
    
    
    def init(self, context):
        '''Initialise Operator.
        '''
        
        try:
            self._target_path = context.window_manager.active_motion_path
        except:
            bpy.ops.view3d.motion_path_draw('INVOKE_DEFAULT', visible=False)
            self._target_path = context.window_manager.active_motion_path
        
        self._active = False
        self._t_range_touched = Vector((1000000, -1000000))
        self._timer = FrameTimer()
        self._time_map = TimeMap()
    
    
    def exit(self, context):
        '''Cleanup.
        '''
        
        pass
    
    
    def timing_input_start(self, context):
        ''' Initialises timing input.
        '''
        
        self._is_animation_playing = context.screen.is_animation_playing
        if self._is_animation_playing:
            bpy.ops.screen.animation_play()
        
        self._timer.start()
        
        self._init_frame = context.scene.frame_current
        self._init_subframe = context.scene.frame_subframe
    
    
    def timing_input_end(self, context):
        '''Ends timing input.
        '''
        
        # apply timing
        reset = self.apply(context)
        
        # reset time according to settings if retimed
        if reset:
            if self.props.timing.reset_time == "scene":
                context.scene.frame_set(context.scene.frame_start)
            elif self.props.timing.reset_time == "touched":
                context.scene.frame_set(floor(self._t_range_touched.x))
        
        # animation playback
        if self._is_animation_playing or (reset and self.props.timing.auto_playback):
            bpy.ops.screen.animation_play()
    
    
    def set_range_touched(self, t):
        '''Expands the time range touched if t not in current time range.
        '''
        
        if t < self._t_range_touched.x:
            self._t_range_touched.x = t
        if t > self._t_range_touched.y:
            self._t_range_touched.y = t
    
    
    def apply(self, context):
        '''Applies the recorded timing dependent on options.
        '''
        
        applied = False
        object = self._target_path.target
        
        # secure that time map spans whole frame range
        if self.props.timing.apply_mode == 'retime':
            motion_range = MotionPath.get_motion_range(object)
            self._time_map.extend_range_target(min(context.scene.frame_start, floor(motion_range.x)), \
                                               max(context.scene.frame_end, ceil(motion_range.y)))
        
        # apply timing to target
        if object.animation_data and object.animation_data.action:
            
            action_old = object.animation_data.action
            action_new = None
            
            if self.props.timing.apply_mode == 'retime':
                action_new = retime_action(action_old, self._time_map)
            elif self.props.timing.apply_mode == 'resample':
                action_new = resample_action(action_old, self._time_map)
            
            apply_action(object, action_new)
            applied = action_new is not None
        
        # apply timing to children (children don't affect path)
        self.apply_children(object, self.props.timing.iterate_children)
        
        # apply timing to parents
        applied = self.apply_parents(object, self.props.timing.iterate_parents) or applied
        
        # recalculate target path
        if self._target_path.props.auto_recalc:
            
            self._target_path.recalculate()
            self._target_path.calculate_projection(MotionPath.get_area(context, 'VIEW_3D'))
            self._target_path.calculate_arclength()
        
        return applied
    
    
    def apply_children(self, object, depth):
        '''Recursively retimes object's children up to depth.
        '''
        
        if object is None or depth == 0:
            return False
        
        applied = False
        
        for child in object.children:
            
            if child.animation_data and child.animation_data.action:
                
                action_old = child.animation_data.action
                action_new = None
                
                if self.props.timing.apply_mode == 'retime':
                    action_new = retime_action(action_old, self._time_map)
                elif self.props.timing.apply_mode == 'resample':
                    action_new = resample_action(action_old, self._time_map)
                
                apply_action(child, action_new)
                applied = action_new is not None
            
            applied = self.apply_children(child, depth - 1) or applied
        
        return applied
    
    
    def apply_parents(self, object, depth):
        '''Recursively retimes object's parent chain up to depth.
        '''
        
        if object is None or depth == 0:
            return False
        
        applied = False
        
        if object.parent:
            
            if object.parent.animation_data and object.parent.animation_data.action:
                
                action_old = object.parent.animation_data.action
                action_new = None
                
                if self.props.timing.apply_mode == 'retime':
                    action_new = retime_action(action_old, self._time_map)
                elif self.props.timing.apply_mode == 'resample':
                    action_new = resample_action(action_old, self._time_map)
                
                apply_action(object.parent, action_new)
                applied = action_new is not None
            
            applied = self.apply_parents(object.parent, depth - 1) or applied
        
        return applied
    
    
    def input_poll(self, context, event):
        '''Implement in subclasses For additional execution conditions.
        '''
        
        return (self._target_path.target is not None)
    
    
    def invoke(self, context, event):
        
        if not context.area.type == self.area_type:
            self.report({'WARNING'}, self.area_type + " not found, cannot run " + self.bl_label)
            return {'CANCELLED'}
        
        # initialise
        self.init(context)
        
        # run modal once
        self.modal(context, event)
        
        # register modal handler
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    
    def modal(self, context, event):
        
        if self.debug: t_comp = time.time()
        
        # handle events
        if event.type in ('LEFTMOUSE', 'EVT_TWEAK_L'):
            
            if (event.value == 'PRESS' or event.type == 'EVT_TWEAK_L') and self.input_poll(context, event):
                
                self._active = True
                self.timing_input_start(context)
                self.timing_input(context, Vector((event.mouse_region_x, event.mouse_region_y)))
                return {'RUNNING_MODAL'}
            
            elif event.value == 'RELEASE':
                
                if self._active:
                    self.timing_input_end(context)
                
                self.exit(context)
                return {'FINISHED'}
        
        elif event.type == 'MOUSEMOVE' and self._active:
            
            self.timing_input(context, Vector((event.mouse_region_x, event.mouse_region_y)))
            return {'RUNNING_MODAL'}
        
        if self.debug:
            t_comp = time.time() - t_comp
            print('%s computation time: %s' % (self, str(t_comp)))
        
        return {'PASS_THROUGH'}
