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
# Contributor: Florian Biermann

from .performtime import PerformTimeOperator
from .timingutils import TimingProps
from bpy_extras import view3d_utils
from math import floor
from mathutils import Vector
import bpy


class DragTimeOperator(PerformTimeOperator):
    '''Drag a feature along its motion path in the 3D view to navigate through time or retime an animation'''
    
    bl_idname = 'view3d.drag_time'
    bl_label = 'DragTime'
    area_type = 'VIEW_3D'
    
    
    def input_poll(self, context, event):
        
        if not PerformTimeOperator.input_poll(self, context, event):
            return False
        
        if self._target_path.arclength_3d < 0.001:
            return False
        
        target = self._target_path.target
        target_bone = self._target_path.target_bone
        
        if target_bone:
            
            bmode = self._target_path.props.bone_mode
            
            if bmode == 'head':
                target_3d = target.matrix_world * target_bone.head
            elif bmode == 'tail':
                target_3d = target.matrix_world * target_bone.tail
            elif bmode == "middle":
                target_3d = target.matrix_world * target_bone.tail.lerp(target_bone.head, 0.5)
        else:
            target_3d = target.matrix_world[3].to_3d()
        
        target_2d = view3d_utils.location_3d_to_region_2d(context.region, \
                                                          context.space_data.region_3d, \
                                                          target_3d)
        
        dist = (Vector((event.mouse_region_x, event.mouse_region_y)) - target_2d).length
        
        if dist < self.props.selection_radius:
            return True
        
        return False
    
    
    def timing_input(self, context, input_vector):
        
        # set attributes first time
        try:
            self._arc_current
        except:
            self._arc_current = self._target_path.arclength_from_time(self._t_target, projected=len(input_vector) == 2)
            #self._arc_last = self._arc_current
            self._arc_last = 0
        
        # get sample from input
        if self.props.timing.constrain_forward:
            arc_start = self._arc_current
        else:
            arc_start = 0
        sample = self._target_path.sample_from_point(input_vector, \
                                                     arc_current=self._arc_current, \
                                                     arc_last=self._arc_last, \
                                                     arc_start=arc_start, \
                                                     k_arc=self.props.k_arclength, \
                                                     k_dir=self.props.k_direction)
        
        # set attributes
        self._t_target = sample.time
        self._arc_last = self._arc_current
        if len(input_vector) == 2:
            self._arc_current = sample.arc_2d
        elif len(input_vector) == 3:
            self._arc_current = sample.arc_3d
        
        # write target and source time into map
        self._time_map.write(self._t_target, self._timer.current())
        
        # set scene time
        t_frame = int(floor(self._t_target))
        t_subframe = self._t_target - t_frame
        context.scene.frame_set(t_frame, t_subframe)
        
        # save range touched
        self.set_range_touched(self._t_target)
    
    
    def invoke(self, context, event):
        
        self._t_target = context.scene.frame_current + context.scene.frame_subframe
        self.props = context.window_manager.drag_time
        return PerformTimeOperator.invoke(self, context, event)


class DragTimePanel(bpy.types.Panel): 
    
    bl_label = "DragTime"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    
    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return(False)
        return(context.active_object.mode in ['OBJECT', 'POSE'])
    
    
    def draw(self, context):
        
        col = self.layout.column(align=True)
        col.operator("view3d.drag_time", text="DragTime")
        
        box = self.layout.box()
        box.prop(context.window_manager.drag_time.timing, "apply_mode", text="Timing")
        
        col = self.layout.column(align=True)
        col.prop(context.window_manager.drag_time, "k_arclength", "Arc-length Continuity")


class DragTimeProps(bpy.types.PropertyGroup):
    
    # timing settings
    timing = bpy.props.PointerProperty(type=TimingProps)
    
    # tool settings
    k_arclength = bpy.props.FloatProperty(name="Arclength Continuity Factor", \
        description="Favor continuity in terms of arc-length variation", \
        default=0.5, min=0.0)
    
    k_direction = bpy.props.FloatProperty(name="Directional Continuity Factor", \
        description="Favor variations that preserve the arc-length direction of motion", \
        default=1000.0, min=0.0)
    
    selection_radius = bpy.props.IntProperty(min=5, max=100, default=30)
