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

from .mpathutils import MotionPathProps
from .performtime import PerformTimeOperator
from .timingutils import TimingProps
from math import floor, ceil
from mathutils import Color
import bgl
import blf
import bpy

DEBUG = True

class ScrubTimeOperator(PerformTimeOperator):
    '''Retime via scrubbing in the timeline window.'''
    
    bl_idname = "time.scrub_time"    
    bl_label = "ScrubTime"
    area_type = 'TIMELINE'
    
    
    def timing_input_end(self, context):
        
        # reset "real" frame marker colour and frame indicator
        context.user_preferences.themes[0].timeline.frame_current = self._marker_color_old
        context.space_data.show_frame_indicator = self._show_frame_indicator
        
        # remove draw callback 
        context.region.callback_remove(self._draw_handle)
        
        PerformTimeOperator.timing_input_end(self, context)
    
    
    def timing_input_start(self, context):
        
        # standardise framerange display
        bpy.ops.time.view_all()
        
        # calculate margin and pixel per frame
        self._margin = ceil(context.region.width * 0.01)
        self._ppf = (context.region.width - self._margin * 2) / (context.scene.frame_end - context.scene.frame_start)
        
        # draw existing timeline marker in a less prominent colour
        self._marker_color_old = context.user_preferences.themes[0].timeline.frame_current.copy()
        context.user_preferences.themes[0].timeline.frame_current = Color((0.5, 0.5, 0.5))
        
        # deactivate frame indicator
        self._show_frame_indicator = context.space_data.show_frame_indicator
        context.space_data.show_frame_indicator = False
        
        # register draw handle
        self._draw_handle = context.region.callback_add(draw_callback, (self, context), 'POST_PIXEL')
        
        PerformTimeOperator.timing_input_start(self, context)
    
    
    def timing_input(self, context, input_vector):
        
        # determine time from input
        t_target_new = context.scene.frame_start + (input_vector.x - self._margin) / self._ppf
        t_target_new = max(t_target_new, float(context.scene.frame_start))
        t_target_new = min(t_target_new, float(context.scene.frame_end))
        if self.props.timing.constrain_forward:
            self._t_target = max(self._t_target, t_target_new)
        else:
            self._t_target = t_target_new
        
        # write target and source time into map
        self._time_map.write(self._t_target, self._timer.current())
        
        # set scene time
        t_frame = int(floor(self._t_target))
        t_subframe = self._t_target - t_frame
        context.scene.frame_set(t_frame, t_subframe)
        
        # save range touched
        self.set_range_touched(self._t_target)
        
        # redraw area
        context.area.tag_redraw()
    
    
    def invoke(self, context, event):
        
        self._t_target = -1000000
        self.props = context.window_manager.scrub_time
        return PerformTimeOperator.invoke(self, context, event)


def draw_callback(self, context):
    
    scene = context.scene
    x = int(round(context.region.width * 0.01 + (self._t_target - scene.frame_start) * self._ppf))
    string = str(self._t_target)
    string = string[0 : string.index('.') + 3]
    font_id = 0  # XXX, need to find out how best to get this.
    
    # draw marker
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1, 0, 0, 1)
    bgl.glLineWidth(2)

    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2i(x, 17)
    bgl.glVertex2i(x, context.region.height)
    bgl.glEnd()
    
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    
    # draw frame number
    if self._show_frame_indicator:
        blf.position(font_id, x + 5, 21, 0)
        blf.size(font_id, 12, 72)
        blf.draw(font_id, string)


class ScrubTimeProps(bpy.types.PropertyGroup):
        
    # timing settings
    timing = bpy.props.PointerProperty(type=TimingProps)
    
    # tool settings
