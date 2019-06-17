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

from datetime import datetime, timedelta

def hours_float_to_str(rendertime): 
    hours_int = int(rendertime)    
        
    left_mins = (rendertime - hours_int)*60
    if left_mins > 0:
        return "%d:%02d" % (hours_int,left_mins)
    else:
        return hours_int
 

def estimate_render_animation_time(self, context):
    layout = self.layout
    scene = context.scene
        
    total_frames = scene.frame_end - scene.frame_start
    
    avg = scene.average_rendertime 
    estimated_rendertime = total_frames * avg/60

    rendertime_in_hours = hours_float_to_str(estimated_rendertime)
    
    estimated_finish_time = datetime.now() + timedelta(hours=estimated_rendertime)
    formatted_finish_time = '{:%a, %d %b @ %H:%M}'.format(estimated_finish_time)

    row = layout.row()
    split =layout.split()
    split.label("Average render time: ")
    
    split.prop(scene,"average_rendertime", text="mins")

    row = layout.row()
    row = row.label("Expected rendertime for %s frames is:"  % total_frames)
    row = layout.row()
    row = row.label("%s hours (ETA %s)"  % (rendertime_in_hours,formatted_finish_time))
# // FEATURE: Estimate Time to Render an Animation
