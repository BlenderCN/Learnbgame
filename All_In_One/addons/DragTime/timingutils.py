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

from math import floor
from time import time
import bpy

EPSILON = 0.001

class FrameTimer():
    
    def __init__(self, fps=24):
        self._fps = fps
        self._start_time = 0
        self.is_running = False
    
    def start(self):
        self._start_time = time() * self._fps
        self.is_running = True
    
    def stop(self):
        self.is_running = False
    
    def current(self):
        return time() * self._fps - self._start_time


class TimeMap():
    
    def __init__(self):
        
        self._samples = []
    
    
    def sort_source(self):
        '''Sorts map samples by source time.
        '''
        
        self._samples.sort(key=lambda sample: sample[1])
    
    
    def sort_target(self):
        '''Sorts map samples by target time.
        '''
        
        self._samples.sort(key=lambda sample: sample[0])
    
    
    def write(self, t_target, t_source):
        '''Writes a target/source time tuple into the map.
        '''
        
        self._samples.append((t_target, t_source))
    
    
    def get_source_time(self, t_target, option='AVERAGE'):
        '''Returns the source time for given target time.
           If more than one source time exists, options determines choice.
        '''
        
        # sanity check
        if option not in {'AVERAGE', 'FIRST', 'LAST'}:
            print("get_source_time received wrong option argument, defaulting to AVERAGE")
            option = 'AVERAGE'
        
        self.sort_target()
        
        # find tuples that t_target lies between and interpolate
        t_candidates = []
        for i in range(0, len(self._samples) - 1):
            
            t1 = self._samples[i]
            t2 = self._samples[i + 1]
            
            if t1[0] - EPSILON < t_target and t_target < t2[0] + EPSILON:
                t_target_dist = t2[0] - t1[0]
                if t_target_dist < EPSILON:
                    w = 0
                else:
                    w = (t_target - t1[0]) / t_target_dist
                t = t1[1] + w * (t2[1] - t1[1])
                t_candidates.append(t)
        
        # if more than one found, resolve dependent on options
        if len(t_candidates) == 0:
            return -1
        elif len(t_candidates) == 1:
            return t_candidates[0]
        elif option == 'FIRST':
            return t_candidates[0]
        elif option == 'LAST':
            return t_candidates[-1]
        elif option == 'AVERAGE':
            t_acc = 0
            for t in t_candidates:
                t_acc += t
            return t_acc / len(t_candidates)
    
    
    def get_target_time(self, t_source, option='AVERAGE'):
        '''Returns the target time for given source time.
           If more than one target time exists, options determines choice.
        '''
        
        # sanity check
        if option not in {'AVERAGE', 'FIRST', 'LAST'}:
            print("get_target_time received wrong option argument, defaulting to AVERAGE")
            option = 'AVERAGE'
        
        self.sort_source()
        
        # find tuples that t_target lies between and interpolate
        t_candidates = []
        for i in range(0, len(self._samples) - 1):
            
            t1 = self._samples[i]
            t2 = self._samples[i + 1]
            
            if t1[1] - EPSILON < t_source and t_source < t2[1] + EPSILON:
                t_source_dist = t2[1] - t1[1]
                if t_source_dist < EPSILON:
                    w = 0
                else:
                    w = (t_source - t1[1]) / t_source_dist
                t = t1[0] + w * (t2[0] - t1[0])
                t_candidates.append(t)
        
        # if more than one found, resolve dependent on options
        if len(t_candidates) == 0:
            return -1
        elif len(t_candidates) == 1:
            return t_candidates[0]
        elif option == 'FIRST':
            return t_candidates[0]
        elif option == 'LAST':
            return t_candidates[-1]
        elif option == 'AVERAGE':
            t_acc = 0
            for t in t_candidates:
                t_acc += t
            return t_acc / len(t_candidates)
    
    
    def extend_range_target(self, t_start, t_end):
        '''Extends the range of the map target time range to t_start, t_end.
        '''
        
        self.sort_target()
        
        # offset source times
        t_source_offset = self._samples[0][0]
        for i in range(0, len(self._samples)):
            t_target = self._samples[i][0]
            t_source = self._samples[i][1] + t_source_offset
            self._samples[i] = (t_target, t_source)
        
        # append sample at start
        if t_start < self._samples[0][0]:
            self._samples.insert(0, (t_start, t_start))
        
        # append sample at end
        if t_end > self._samples[-1][0]:
            
            t_source_offset = t_end - self._samples[-1][0]
            
            self._samples.append((t_end, self._samples[-1][1] + t_source_offset))
    
    
    @classmethod
    def from_path_match(cls, target_path, source_path):
        '''Creates a time map by matching a source path to a target path.
           Based on Terra & Metoyer 2004, 2007
        '''
        
        # segment target and source path at given features
        target_segs = target_path.segment_by_feature({'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'})
        source_segs = source_path.segment_by_feature({'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'})
        
        # check whether paths match
        if len(target_segs) != len(source_segs):
            print("Target path and source path do not match")
            return None
        
        # create time map by matching times via arc length per segment
        tm = TimeMap()
        for i in range(0, len(target_segs)):
            
            target_seg = target_segs[i]
            source_seg = source_segs[i]
            
            for target_sample in target_seg._samples:
                
                t_target = target_sample._time
                t_source = source_seg.time_from_arclength(target_sample._narcp, projected=True, normalized=True)
                tm.write(t_target, t_source)
        
        return tm


def apply_action(object, action_new, action_old=None):
    '''Creates new nla track from active action (or action_old) and sets action_new as active action.
    '''
    
    if not action_new:
        return
    
    # if action_old not given, use active
    if not action_old:
        action_old = object.animation_data.action
    
    # create nla track with action_old and mute 
    if action_old:
        nlatrack = object.animation_data.nla_tracks.new()
        nlatrack.strips.new(action_old.name, action_old.frame_range.x, action_old)
        object.animation_data.nla_tracks[-1].mute = True
    
    # set new active action
    object.animation_data.action = action_new


def retime_action(action_old, time_map, debug=False):
    '''Retimes action's keyframes as determined by time_map
    '''
    
    # setup new action
    action_new = action_old.copy()
    
    # go through all channels
    for i in range(0, len(action_new.fcurves)):
        
        fcu_old = action_old.fcurves[i]
        fcu_new = action_new.fcurves[i]
        kf_old_last = kf_new_last = None
        
        if debug: print("retiming channel", fcu_old.data_path, fcu_old.array_index, "keyframes in fcurve", len(fcu_old.keyframe_points))
        
        # go through all keyframe points in channel
        for j in range (0, len(fcu_old.keyframe_points)):
            
            # get old and new f-curve
            kf_old = fcu_old.keyframe_points[j]
            kf_new = fcu_new.keyframe_points[j]
            
            # lookup new time in map and set
            t_old = kf_old.co.x
            t_new = time_map.get_source_time(t_old)
            kf_new.co.x = t_new
            
            if debug: print("set timing of keyframe", j, "from", t_old, "to", t_new)
            
            # recalculate handles
            if kf_old_last:
                
                l_old = kf_old.co.x - kf_old_last.co.x
                l_new = kf_new.co.x - kf_new_last.co.x
                
                if l_new < EPSILON:
                    
                    if debug: print("keyframe distance too short, setting handles to 0")
                    kf_new_last.handle_right = kf_new_last.co.copy()
                    kf_new.handle_left = kf_new.co.copy()
                    continue
                
                ratio = l_new / l_old
                
                # right handle keyframe j - 1
                handle_right = kf_old_last.handle_right - kf_old_last.co
                handle_right.x *= ratio
                kf_new_last.handle_right_type = 'FREE'
                kf_new_last.handle_right = kf_new_last.co + handle_right
                
                # left handle keyframe j
                handle_left = kf_old.handle_left - kf_old.co
                handle_left.x *= ratio
                kf_new.handle_left_type = 'FREE'
                kf_new.handle_left = kf_new.co + handle_left
            
            kf_old_last = kf_old
            kf_new_last = kf_new
        
        # set first and last handle to old with offset
        if len(fcu_new.keyframe_points) > 0:
            fcu_new.keyframe_points[0].handle_left_type = 'FREE'
            fcu_new.keyframe_points[0].handle_left = fcu_new.keyframe_points[0].co + fcu_old.keyframe_points[0].handle_left - fcu_old.keyframe_points[0].co
            fcu_new.keyframe_points[-1].handle_right_type = 'FREE'
            fcu_new.keyframe_points[-1].handle_right = fcu_new.keyframe_points[-1].co + fcu_old.keyframe_points[-1].handle_right - fcu_old.keyframe_points[-1].co            
    
    return action_new


def resample_action(action_old, time_map):
    '''Creates a new action by sampling given action.
       Sample rate and range are determined by the time map.
    '''
    
    # make sure samples are sorted by source time
    time_map.sort_source()
    
    # note the sampled range
    range_start = time_map._samples[0][0]
    range_end = time_map._samples[-1][0]
    range_offset = range_start + time_map._samples[-1][1] - range_end
    
    # setup new action
    action_new = bpy.data.actions.new(name=action_old.name + "Resampled")
    
    # write fcurves
    for fcu_old in action_old.fcurves:
        
        # new fcurve with settings from old, catch fcurves that don't have group
        try:
            fcu_new = action_new.fcurves.new(fcu_old.data_path, fcu_old.array_index, fcu_old.group.name)
        except:
            fcu_new = action_new.fcurves.new(fcu_old.data_path, fcu_old.array_index)
        
        # write keyframe for each sample
        for sample in time_map._samples:
            fcu_new.keyframe_points.insert(range_start + sample[1], fcu_old.evaluate(sample[0]))
        
        # write old keyframes before and after sampled range
        for kf in fcu_old.keyframe_points:
            if kf.co.x < range_start:
                kf_new = fcu_new.keyframe_points.insert(kf.co.x, kf.co.y)
                kf_new.handle_left = kf.handle_left.copy()
                kf_new.handle_left_type = kf.handle_left_type
                kf_new.handle_right = kf.handle_right.copy()
                kf_new.handle_right_type = kf.handle_right_type
            if kf.co.x > range_end:
                kf_new = fcu_new.keyframe_points.insert(range_offset + kf.co.x, kf.co.y)
                kf_new.handle_left = kf_new.co + kf.handle_left - kf.co
                kf_new.handle_left_type = kf.handle_left_type
                kf_new.handle_right = kf_new.co + kf.handle_right - kf.co
                kf_new.handle_right_type = kf.handle_right_type
    
    return action_new


def has_motion(obj):
    '''Convenience method for checking for object animation data and action.
    '''
    
    return obj.animation_data and obj.animation_data.action


class TimingProps(bpy.types.PropertyGroup):
    
    def update(self, context):
        if self.apply_mode == 'retime':
            self.constrain_forward = True
        else:
            self.constrain_forward = False
    
    reset_time = bpy.props.EnumProperty(name="Reset Mode", \
        items=(("scene", "Scene", "Reset time to start of scene after retiming"), \
               ("touched", "Retimed Range", "Reset time to start of retimed frame range after retiming")), \
        default="touched")
    auto_playback = bpy.props.BoolProperty(name="Auto-Playback", \
        description="Automatically play back resulting timing", \
        default = True)
    apply_mode = bpy.props.EnumProperty(name="Apply Timing", \
        items=(("disabled", "Don't apply", "Interactive timing is not applied"), \
               ("retime", "Retime", "Interactive timing is used to retime existing keyframes"), \
               ("resample", "Resample", "Interactive timing generates new keyframes")), \
        description="Set how interactive timing is applied", \
        default="disabled", \
        update=update)
    iterate_parents = bpy.props.IntProperty(name="Iterate Parents", \
        description="Depth up to which object's parents are also retimed", \
        min=0, default=10)
    iterate_children = bpy.props.IntProperty(name="Iterate Children", \
        description="Depth up to which object's children are also retimed", \
        min=0, default=10)
    constrain_forward = bpy.props.BoolProperty(name="Constrain Forward", \
        description="Only move forward in time, not backward", \
        default=False)
