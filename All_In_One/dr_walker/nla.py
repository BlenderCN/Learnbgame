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

# <pep8-80 compliant>
# Copyright 2015 Bassam Kurdali 

if "bpy" in locals():
    import importlib
    importlib.reload(path)
    importlib.reload(utils)
else:
    from . import path
    from . import utils
import bpy

strip_settings = ('frame_start', 'frame_end', 'blend_in', 'blend_out')


def get_nla_active(context):
    """ return active strip and it's object"""
    # must be a poll for context.area.type == 'NLA_EDITOR'
    if context.space_data.dopesheet.show_only_selected:
        obs = context.selected_objects
    else:
        obs = context.scene.objects
    for ob in obs:
        anim = ob.animation_data
        if anim and anim.nla_tracks and anim.nla_tracks.active:
            for strip in anim.nla_tracks.active.strips:
                if strip.active:
                    return (strip, ob)


def get_nla_selected(context):
    """ returns selected strips for active object only """
    ob = context.active_object
    anim = ob.animation_data
    strips = []
    if anim and anim.nla_tracks:
        for track in anim.nla_tracks:
            for strip in track.strips:
                if strip.select:
                    strips.append(strip)
    return (strips, ob)


def replace_strip_action(strip, new_action, match_action = True):
    """ replace original action with new improved one """
    settings = {prop: getattr(strip, prop) for prop in strip_settings}
    strip.use_sync_length = False
    strip.action = new_action
    strip.scale = 1
    # strip.name = new_action.name

    if match_action:
        for i in range(3):
            strip.action_frame_start = strip.frame_start = settings['frame_start']
            strip.action_frame_end = strip.frame_end = settings['frame_end']
            strip.scale = strip.repeat = 1
    else:
        strip.action_frame_start = new_action.frame_range[0]
        strip.action_frame_end = new_action.frame_range[1]    
    # bpy.ops.nla.tweakmode_enter()
    # bpy.ops.nla.tweakmode_exit()
    for setting in settings:
        setattr(strip, setting, settings[setting])
    # set action limits
    

def eval_curve_from_steps(ob, track, strip, cycle_frames, curve_path):
    """ use strip evaluation time to match Elephants Dream speeds """
    data_path =\
        'animation_data.nla_tracks["{}"].strips["{}"].strip_time'.format(
        track.name, strip.name)
    strip.use_animated_time = True
    strip_limits = (strip.frame_start, strip.frame_end)
    action_limits = (strip.action_frame_start, strip.action_frame_end)
    eval_time_curve = path.get_path_eval_curve(curve_path)
    ob.keyframe_insert(data_path, -1, 0)
    fcurve = [
        cu for cu in ob.animation_data.action.fcurves if cu.data_path == data_path][0]
    fcurve.keyframe_points[0].co[1] = 0
    fcurve.keyframe_points[0].interpolation = 'LINEAR'
    duration = curve_path.data.path_duration
    for idx, frame in enumerate(cycle_frames):
        utils.insert_keyframe_curve(fcurve, frame, frame, 'LINEAR')
        try:
            next_frame = cycle_frames[idx + 1]
        except:
            break
        limits = (eval_time_curve.evaluate(frame) / duration, eval_time_curve.evaluate(next_frame) / duration)
        offset = frame - limits[0]
        scale = (next_frame - frame) / (limits[1] - limits[0])
        for subframe in range(int(frame) + 1, int(next_frame)):
            dif = eval_time_curve.evaluate(subframe)/duration - limits[0]
            utils.insert_keyframe_curve(fcurve, subframe, offset + scale * dif, 'LINEAR')
            
        
        
    
    # step 1 insert non changing keyframes for limits, steps
    # step 2 use the curve evalatuion to figure out 
    
       
    
    
    
