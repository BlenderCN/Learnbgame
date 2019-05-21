# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2011: Benjamin Walther-Franks, bwf@tzi.de

from .mpathutils import MotionPath, MotionPathProps
from .performtime import PerformTimeOperator
from .timingutils import FrameTimer, TimeMap, TimingProps
from math import floor
from mathutils import Vector, Color
import bpy


THRESH_FEATURE_DETECT = 1
THRESH_FEATURE_CLEAN = 30 

g_tgt_path = None
g_src_path = None


class SketchTime(PerformTimeOperator):
    '''Sketch a timing path'''
    
    bl_idname = "view3d.sketch_time"
    bl_label = "SketchTime"
    area_type = 'VIEW_3D'
    
    
    def timing_input_end(self, context):
        
        global g_tgt_path, g_src_path
        
        # make sure arclengths are set
        self._source_path.calculate_arclength()
        
        # filter any too short paths
        if self._source_path.arclength_2d > self.props.min_path_length:
            
            if g_src_path:
                del g_src_path
            
            g_src_path = self._source_path
            
            # feature detection
            if g_tgt_path._is_2d and g_src_path._is_2d:
                
                g_tgt_path.features_minmax(threshold = THRESH_FEATURE_DETECT, projection = True)
                tgt_num_features = g_tgt_path.features_clean(THRESH_FEATURE_CLEAN)
                g_src_path.features_minmax(threshold = THRESH_FEATURE_DETECT, projection = True)
                src_num_features = g_src_path.features_clean(THRESH_FEATURE_CLEAN)
                
                # color paths for visual feedback
                if tgt_num_features != src_num_features:
                    g_src_path.props.color = Color((1.0, 0.3, 0.3))
                else:
                    g_src_path.props.color = Color((0.3, 1.0, 0.3))
            
        else:
            self._source_path.draw_end(context)
            del self._source_path
            if g_src_path:
                g_src_path.draw_begin(context) 
        
        context.area.tag_redraw()
    
    
    def invoke(self, context, event):
        
        if context.area.type == 'VIEW_3D':
            
            if not context.active_object:
                self.report({'WARNING'}, "Nothing to time")
                return {'CANCELLED'}
            
            self.props = context.window_manager.sketch_time
            
            # source path
            global g_src_path
            if g_src_path:
                g_src_path.draw_end(context)
            
            src_path_props = self.props.path
            src_path_props.color = Color((0.7, 0.7, 0.7))
            src_path_props.features_shape = 'cross'
            self._source_path = MotionPath(src_path_props)
            self._source_path._is_2d = True
            self._source_path.draw_begin(context)
            
            ret_val = PerformTimeOperator.invoke(self, context, event)
            
            # target path
            global g_tgt_path
            g_tgt_path = self._target_path
            if not g_tgt_path.visible:
                g_tgt_path.draw_begin(context)
            
            return ret_val
        else:
            self.report({'WARNING'}, "View3D not found, cannot run SketchTime")
            return {'CANCELLED'}
    
    
    def timing_input(self, context, input_vector):
        
        self._source_path.write_sample(input_vector, self._timer.current())
        context.area.tag_redraw()


class SketchTimeEdit(PerformTimeOperator):
    '''Edit a sketched timing path'''

    bl_idname = "view3d.sketch_time_edit"
    bl_label = "SketchTime Edit"
    
    
    def invoke(self, context, event):
                
        if context.area.type == 'VIEW_3D':
            
            self.props = context.window_manager.sketch_time
            
            global g_src_path
            if not g_src_path:
                self.report({'WARNING'}, "No source path sketched")
                return {'CANCELLED'}
            
            retval = self.modal(context, event)
            if retval == {'FINISHED'}:
                return {'FINISHED'}
            
            context.window_manager.modal_handler_add(self)                    
            return {'RUNNING_MODAL'}
        
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
    
    
    def modal(self, context, event):
        
        if (event.type == 'LEFTMOUSE' or event.type == 'RIGHTMOUSE') and event.value == 'PRESS':
            
            global g_src_path
            sample = g_src_path.sample_from_point(point = Vector((event.mouse_region_x, event.mouse_region_y)), \
                                                  threshold=self.props.edit_threshold_squared, \
                                                  priority_threshold=self.props.edit_priority_threshold_squared, \
                                                  priority_flags = {'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'})
            
            if sample:
                if sample._flag in {'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'}:
                    sample._flag = 'NONE'
                elif sample._flag in {'NONE', 'CLEANED'}:
                    sample._flag = 'MINMAX_XY'
                
                # color paths for visual feedback
                props = context.window_manager.sketch_time
                if g_tgt_path.num_features != g_src_path.num_features:
                    g_src_path.props.color = Color((1.0, 0.3, 0.3))
                else:
                    g_src_path.props.color = Color((0.3, 1.0, 0.3))
                
                context.area.tag_redraw()
            
            return {'FINISHED'}
        
        elif event.type == 'ESC':
            
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}


class SketchTimeClear(PerformTimeOperator):
    '''Clear sketched timing path'''
    
    bl_idname = "view3d.sketch_time_clear"
    bl_label = "SketchTime Clear"
    
    
    def invoke(self, context, event):
        
        global g_tgt_path, g_src_path
        
        # clear source path
        try:
            g_src_path.draw_end(context)
            del g_src_path
        except:
            pass
        g_src_path = None
        
        # clear target path
        try:
            g_tgt_path.features_clear()
        except:
            pass
        g_tgt_path = None
        
        if context.area:
            context.area.tag_redraw()
        
        return {'FINISHED'}


class SketchTimeApply(PerformTimeOperator):
    '''Apply a sketched timing path'''
    
    bl_idname = "view3d.sketch_time_apply"
    bl_label = "SketchTime Apply"
    
    
    def invoke(self, context, event):
        
        global g_tgt_path, g_src_path
        if not g_src_path:
            self.report({'WARNING'}, "No source path sketched")
            return {'CANCELLED'}
        
        # split paths into segments given by features
        tgt_segs = g_tgt_path.segment_by_feature({'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'})
        src_segs = g_src_path.segment_by_feature({'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'})
        
        # check whether paths match
        if len(tgt_segs) != len(src_segs):
            self.report({'WARNING'}, "Target path and source path do not match")
            return {'CANCELLED'}
        
        # setup properties needed for applying timing
        self.props = context.window_manager.sketch_time
        self.props.timing.apply_mode = 'retime'
        self._time_map = TimeMap.from_path_match(g_tgt_path, g_src_path)
        self._target_path = g_tgt_path
        
        # apply recorded timing
        self.apply(context)
        
        # clear paths
        bpy.ops.view3d.sketch_time_clear('INVOKE_DEFAULT')
        
        # reset time according to settings if retimed
        if self.props.timing.reset_time == "scene":
            context.scene.frame_set(context.scene.frame_start)
        if self.props.timing.reset_time == "touched":
            context.scene.frame_set(floor(self._target_path.start_time))
        
        # animation playback
        if self.props.timing.auto_playback:
            bpy.ops.screen.animation_play()        
        
        return {'FINISHED'}


class SketchTimePanel(bpy.types.Panel):
    
    bl_label = "SketchTime"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    
    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return(False)
        return(context.active_object.mode in ['OBJECT', 'POSE'])
    
    
    def draw(self, context):
        
        col = self.layout.column(align=True)
        col.operator("view3d.sketch_time", text="Sketch")
        col.operator("view3d.sketch_time_edit", text="Edit")
        col.operator("view3d.sketch_time_clear", text="Clear")
        col.operator("view3d.sketch_time_apply", text="Apply")


class SketchTimeProps(bpy.types.PropertyGroup):
    
    def update(self, context):
        
        self.edit_priority_threshold_squared = self.edit_priority_threshold * self.edit_priority_threshold 
        self.edit_threshold_squared = self.edit_threshold * self.edit_threshold
    
    # source path settings
    path = bpy.props.PointerProperty(type=MotionPathProps)
    
    # timing settings
    timing = bpy.props.PointerProperty(type=TimingProps)
    
    # tool settings
    edit_priority_threshold = bpy.props.IntProperty(name="Priority Threshold", \
        default=15, description="Feature editing priority threshold in pixels.", \
        update=update)
    edit_priority_threshold_squared = bpy.props.IntProperty(default=15*15)
    edit_threshold = bpy.props.IntProperty(name="Selection Threshold", \
        default=25, description="Feature editing threshold in pixels.", \
        update=update)
    edit_threshold_squared = bpy.props.IntProperty(default=25*25)
    min_path_length = bpy.props.IntProperty(name="Minimum Path Arclength", \
        default=100, description='Minimum arclength in pixels sketched path must have, otherwise sketch is ignored.', \
        min=0)
