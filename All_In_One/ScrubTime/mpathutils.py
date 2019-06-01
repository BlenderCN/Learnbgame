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
# Contributor: Florian Biermann

from bpy_extras import view3d_utils
from mathutils import Vector
import bgl
import blf
import bpy
import math

EPSILON = 0.0001

class MotionPathVert():
    
    def __init__(self, vec, time):
        
        self._time = time
                
        # 3D
        self._loc = None
        self._arc = -1
        self._narc = -1
        
        # 2D
        self._proj = None
        self._arcp = -1
        self._narcp = -1
        
        dim = len(vec.to_tuple())
        
        if dim == 2:
            self._proj = vec.copy()
        elif dim == 3:
            self._loc = vec.copy()
        
        self._flag = 'NONE'
    
    # Equality functions 
    def __eq__(self, q):
        return self._loc == q._loc and self._time == q._time
    
    def __neq__(self, q):
        return self._loc != q._loc or self._time != q._time
    
    # Functions for sorting, based on time value.
    def __gt__(self, q):
        return self._time.__gt__(q._time)
    
    def __ge__(self, q):
        return self._time.__ge__(q._time)
        
    def __lt__(self, q):
        return self._time.__lt__(q._time)
    
    def __le__(self, q):
        return self._time.__le__(q._time)
    
    @property
    def time(self):
        return self._time
    
    @property
    def arc_2d(self):
        return self._arcp
    
    @property
    def arc_3d(self):
        return self._arc


class MotionPath():
    """A 2D and 3D Motion Path representation.
    """
    
    def __init__(self, props, obj=None, t_start=-1000000, t_end=1000000, debug=False):
        
        self._debug = debug
        
        if self._debug: print("created MotionPath")
        
        self._samples = []
        self._is_2d = False
        self._is_3d = False
        
        self.visible = False
        self.props = props
        
        # for more efficient iterative calculation
        self._arc_index = -1
        self._arcp_index = -1
        self._proj_index = -1
        
        self._proj_scale = 1
        
        self._feature = None
        self._feature_bone = None
        
        if obj is not None:
            if self.props.res_mode == 'spatial':
                self.from_object_spatial(obj, self.props.res_spatial, self.props.bone_mode, t_start, t_end)
            elif self.props.res_mode == 'temporal':
                self.from_object_temporal(obj, self.props.res_temporal, self.props.bone_mode, t_start, t_end)
    
    
    def __del__(self):
        try:
            self.draw_end(bpy.context)
        except:
            pass
        if self._debug: print("deleted MotionPath")
    
    
    @property
    def num_features(self):
        num_features = 0
        for sample in self._samples:
            if sample._flag in {'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'}:
                num_features += 1
        return num_features
    
    
    @property
    def start_time(self):
        """Get time of first sample.
        """
        if len(self._samples) > 0:
            self._samples.sort()
            return self._samples[0]._time
        return -1
    
    
    @property
    def end_time(self):
        """Get time of last sample.
        """
        if len(self._samples) > 0:
            self._samples.sort()
            return self._samples[-1]._time
        return -1
    
    
    @property
    def target(self):
        """Get the motion path target.
        """
        return self._feature
    
    
    @property
    def target_bone(self):
        """Get the motion path target bone.
        """
        return self._feature_bone
    
    
    @property
    def arclength_2d(self):
        """Get the 2d path arc length.
        """
        if len(self._samples) > 0 and self._is_2d:
            self._samples.sort()
            return self._samples[-1]._arcp
        return 0
    
    
    @property
    def arclength_3d(self):
        """Get the 3d path arc length.
        """
        if len(self._samples) > 0 and self._is_3d:
            self._samples.sort()
            return self._samples[-1]._arc
        return 0
    
    
    @property
    def center_3d(self):
        """Get the 2d center of the path.
        """
        avg = Vector()
        for sample in self._samples:
            avg += sample._proj
        return avg / len(self._samples)
    
    
    @property
    def center_2d(self):
        """Get the 3d center of the path.
        """
        avg = Vector()
        for sample in self._samples:
            avg += sample._loc        
        return avg / len(self._samples)
    
    
    def clear(self):
        self.__init__(self.props)
    
    
    def recalculate(self, obj=None):
        """Calculates a path from the current settings.
        """
        if obj is None:
            obj = self._feature
        self.__init__(props=self.props, obj=obj, debug=self._debug)
    
    
    def copy_samples(self, start = 0, end = 1000000000):
        """Creates a deep copy of the samples list.
           Careful: if start, end not equal to original values, arclengths need to be recalculated
        """
        
        samples_copy = []
        start = max(0, start)
        end = min(end, len(self._samples))
        
        for vert in self._samples[start : end]:
            if self._is_3d:
                vert_copy = MotionPathVert(vert._loc.copy(), vert._time)
                if self._is_2d:
                    vert_copy._proj = vert._proj.copy()
            elif self._is_2d:
                vert_copy = MotionPathVert(vert._proj.copy(), vert._time)
            samples_copy.append(vert_copy)
        
        return samples_copy
    
    
    def from_object_spatial(self, obj, s_res = 0.25, bone_mode='head', t_start=-1000000000, t_end=1000000000):
        """Samples object motion based on a spatial resolution
        """
        
        if obj is None:
            return
        
        self.clear()
        self._feature = obj
        self._feature_bone = bpy.context.active_pose_bone # TODO: make this a parameter
        
        def resample(self, arclen, path):
            t = path.time_from_arclength(arclen)
            p = path.point_from_time(t)
            self.write_sample(p, t)
        
        def subdivide(self, left, right, path, res):
            if (right - left <= res):
                return
            
            median = left + (right - left)/2
            subdivide(self, left, median, path, res)
            resample(self, median, path)
            subdivide(self, median, right, path, res)
        
        # Aux path
        t_path = MotionPath(self.props)
        t_path._debug = False
        t_path.from_object_temporal(obj, 0.5, bone_mode, t_start, t_end)
        t_path.calculate_arclength()
        
        # Get max arclength
        arclen = t_path.arclength_3d
        
        resample(self, 0, t_path) # TODO: instead, we could also copy first sample of t_path
        subdivide(self, 0, arclen, t_path, s_res)
        resample(self, arclen, t_path) # TODO: instead, we could also copy last sample of t_path
        
        del t_path
    
    
    def write_sample_from_feature(self, obj, bone, bone_mode, t):
        """Writes a feature's world position as a sample at time t.
        """
        
        frame = int(math.floor(t))
        subframe = t - frame
        bpy.context.scene.frame_set(frame, subframe)
        
        if obj.mode == 'POSE':
            if bone_mode == 'head':
                self.write_sample(obj.matrix_world * bone.head, t)
            elif bone_mode == 'tail':
                self.write_sample(obj.matrix_world * bone.tail, t)
            elif bone_mode == 'middle':
                self.write_sample(obj.matrix_world * bone.tail.lerp(bone.head, 0.5), t)
        else:
            self.write_sample(obj.matrix_world[3].to_3d(), t)
    
    
    def from_object_temporal(self, obj, t_res=1, bone_mode='head', t_start=-1000000000, t_end=1000000000):
        """Samples object motion based on a temporal resolution
        """
        
        if obj is None:
            return
        
        self.clear()
        self._feature = obj
        self._feature_bone = bpy.context.active_pose_bone # TODO: make this a parameter
        
        scene = bpy.context.scene #@UndefinedVariable
        
        frame_init = scene.frame_current
        subframe_init = scene.frame_subframe
        
        motion_range = MotionPath.get_motion_range(self._feature)
        t_start = max(t_start, motion_range.x)
        t_end = min(t_end, motion_range.y)
        
        t = t_start
        
        while t <= t_end:
            
            self.write_sample_from_feature(self._feature, self._feature_bone, bone_mode, t)
            t += t_res
        
        scene.frame_set(frame_init, subframe_init)
    
    
    @classmethod
    def get_motion_range(cls, obj):
        """Returns a range vector giving the frame range in which the object has motion
        """
        
        range = Vector((1000000, -1000000))
        
        while obj:
            
            if obj.animation_data and obj.animation_data.action:
                range.x = min(range.x, obj.animation_data.action.frame_range[0])
                range.y = max(range.y, obj.animation_data.action.frame_range[1])
            
            obj = obj.parent
        
        return range
    
    
    def to_curve(self):
        """Creates a polyline spline curve object for the motion path.
        """
        
        curve = bpy.data.curves.new("MotionPathCurve", type = 'CURVE') #@UndefinedVariable
        spline = curve.splines.new('POLY')
        spline.points.add(int(len(self._samples) - 1))
        
        for i in range(0, int(len(self._samples))):
            loc = self._samples[i]._loc
            spline.points[i].co = loc.x, loc.y, loc.z, 0
            
        obj = bpy.data.objects.new("MotionPath", curve) #@UndefinedVariable
        bpy.context.scene.objects.link(obj) #@UndefinedVariable
        
        return obj
    
    
    def features_minmax(self, threshold = 1, projection = True):
        """Determines path local x, y, (z) minima and maxima based on Terra & Metoyer 2004, 2007.
        """
        
        self._samples[0]._flag = 'START'
        self._samples[-1]._flag = 'END'
        
        if projection:
            for i in range(1, len(self._samples) - 2):
                
                p1 = self._samples[i - 1]
                p2 = self._samples[i]
                p3 = self._samples[i + 1]
                
                d1 = p2._proj - p1._proj
                d2 = p3._proj - p2._proj
                
                p2._flag = 'NONE'
                
                if (d1.x == 0 and d2.x != 0) or (d1.x != 0 and d2.x == 0) or (d1.x * d2.x < 0):
                    if self._debug: print("x dirchange detected at", i)
                    
                    if abs(d1.x) + abs(d2.x) > threshold:
                        if self._debug: print("x min/max feature set at", i)
                        p2._flag = 'MINMAX_X'
                
                if (d1.y == 0 and d2.y != 0) or (d1.y != 0 and d2.y == 0) or (d1.y * d2.y < 0):
                    if self._debug: print("y dirchange detected at", i)
                    
                    if abs(d1.y) + abs(d2.y) > threshold:
                        if self._debug: print("y min/max feature set at", i)
                        if p2._flag == 'MINMAX_X':
                            p2._flag = 'MINMAX_XY'
                        else:
                            p2._flag = 'MINMAX_Y'
                            
        else:
            for i in range(1, len(self._samples) - 2):
                
                p1 = self._samples[i - 1]
                p2 = self._samples[i]
                p3 = self._samples[i + 1]
                
                d1 = p2._loc - p1._loc
                d2 = p3._loc - p2._loc
                
                p2._flag = 'NONE'
                
                if (d1.x == 0 and d2.x != 0) or (d1.x != 0 and d2.x == 0) or (d1.x * d2.x < 0):
                    if self._debug: print("x dirchange detected at", i)
                    
                    if abs(d1.x) + abs(d2.x) > threshold:
                        if self._debug: print("x min/max feature set at", i)
                        p2._flag = 'MINMAX_X'
                
                if (d1.y == 0 and d2.y != 0) or (d1.y != 0 and d2.y == 0) or (d1.y * d2.y < 0):
                    if self._debug: print("y dirchange detected at", i)
                    
                    if abs(d1.y) + abs(d2.y) > threshold:
                        if self._debug: print("y min/max feature set at", i)
                        if p2._flag == 'MINMAX_X':
                            p2._flag = 'MINMAX_XY'
                        else:
                            p2._flag = 'MINMAX_Y'
                
                if (d1.z == 0 and d2.z != 0) or (d1.z != 0 and d2.z == 0) or (d1.z * d2.z < 0):
                    if self._debug: print("z dirchange detected at", i)
                    
                    if abs(d1.z) + abs(d2.z) > threshold:
                        if self._debug: print("z min/max feature set at", i)
                        if p2._flag == 'MINMAX_X':
                            p2._flag = 'MINMAX_XZ'
                        elif p2._flag == 'MINMAX_Y':
                            p2._flag = 'MINMAX_YZ'
                        elif p2._flag == 'MINMAX_XY':
                            p2._flag = 'MINMAX_XYZ'
    
    
    def features_clean(self, threshold = 30, projection = True):
        """Cleans path features that have features within threshold in a forward direction.
           Currently only implemented for 2D (projection).
        """
        
        num_features = 2
        
        for i in range(1, len(self._samples) - 2):
            
            if self._samples[i]._flag in {'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'}:
                
                num_features += 1
                
                # search backwards
                for j in range(i - 1, -1, -1):
                    
                    dist = self._samples[i]._arcp - self._samples[j]._arcp
                    
                    if dist > threshold:
                        break
                    
                    if self._samples[j]._flag in {'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'}:
                        self._samples[i]._flag = 'CLEANED'
                        num_features -= 1
                        break
                
                if self._samples[i]._flag == 'CLEANED':
                    continue
                
                # search forwards
                for j in range(i + 1, len(self._samples)):
                    
                    dist = self._samples[j]._arcp - self._samples[i]._arcp
                    
                    if dist > threshold:
                        break
                    
                    if self._samples[j]._flag in {'START', 'END', 'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY'}:
                        self._samples[i]._flag = 'CLEANED'
                        num_features -= 1
                        break
        
        return num_features
    
    
    def features_clear(self):
        """Sets all flags to 'NONE'.
        """
        
        for sample in self._samples:
            sample._flag = 'NONE'
    
    
    def segment_by_feature(self, feature_set):
        """Segments a path at samples that are flagged as element in feature_set.
           Returns a list of segments as new motion paths
        """
        
        segments = []
        i = 0
        for j in range(1, len(self._samples)):
            if self._samples[j]._flag in feature_set:
                seg_path = MotionPath(self.props)
                seg_path._samples = self.copy_samples(i, j + 1)
                seg_path._is_2d = self._is_2d
                seg_path._is_3d = self._is_3d
                seg_path.calculate_arclength()
                segments.append(seg_path)
                i = j
        
        return segments
    
                    
    def write_sample(self, loc, time):
        """ Writes a sample into the MotionPath
            if it is not yet part of it.
        """
        vert = MotionPathVert(loc, time)
        if True:#not vert in self._samples:
            if self._debug: print("writing sample", loc, "at time", time)
            self._samples.append(vert)
            self._is_2d = vert._proj is not None
            self._is_3d = vert._loc is not None
    
    
    def calculate_arclength(self):
        """Calculates the 3D arclength for each MotionPathVertex.
        """
        
        if self._debug: print("calculating arclength...")
        
        if len(self._samples) == 0:
            if self._debug: print("no samples to calculate arclength for")
            return
            
        self._samples.sort()
        if self._is_3d == True:
            if self._arc_index < 0:
                self._arc_index = 0
                self._samples[0]._arc = 0.0
            
            # Samples are now sorted by time.
            while self._arc_index < len(self._samples) - 1:
                s1 = self._samples[self._arc_index]
                self._arc_index += 1
                s2 = self._samples[self._arc_index]            
                s2._arc = s1._arc + (s2._loc - s1._loc).length
            
            if self._samples[-1]._arc > EPSILON:
                for sample in self._samples:
                    sample._narc = sample._arc / self._samples[-1]._arc
            else:
                for sample in self._samples:
                    sample._narc = 0
            
            if self._debug: print("calculated 3D arclength")        
        else:
            if self._debug: print("could not calculate 3D arc")
        
        if self._is_2d == True:
            if self._arcp_index < 0:
                self._arcp_index = 0
                self._samples[0]._arcp = 0.0
               
            while self._arcp_index < len(self._samples) - 1:
                s1 = self._samples[self._arcp_index]
                self._arcp_index += 1
                s2 = self._samples[self._arcp_index]
                s2._arcp = s1._arcp + (s2._proj - s1._proj).length
            
            if self._samples[-1]._arcp > EPSILON:
                for sample in self._samples:
                    sample._narcp = sample._arcp / self._samples[-1]._arcp
            else:
                for sample in self._samples:
                    sample._narcp = 0
            
            if self._debug: print("calculated 2D arclength")   
        else:
            if self._debug: print("could not calculate 2D arc")
    
    
    def calculate_projection(self, area):
        """Calculates 2D projection for given 3D view.
        """
        
        if self._debug: print("calculating 2D projection")
        
        if area.type != 'VIEW_3D':
            raise Exception("wrong area type, no 3d view info for projection")
        
        if not self._is_3d:
            return
        
        region = space = None
        for region in area.regions:
            if region.type == 'WINDOW':
                break
        space = area.spaces[0]
        
        for sample in self._samples[self._proj_index + 1: ]:
            sample._proj = view3d_utils.location_3d_to_region_2d(region, 
                                                                 space.region_3d,
                                                                 sample._loc * self._proj_scale)
        
        self._proj_index = len(self._samples) - 1
        self._is_2d = True
        
    
    def set_scale_projection(self, scale):
        self._proj_scale = scale
    
    
    def point_from_arclength(self, a, projected = False, normalized = False):
        """ Interpolates points linearly from closest two path samples
            determined by given a with respect to arclength.
        """
        
        if self._debug: print("evaluating point at arclength", a)
        
        if normalized:
            a = max(a, 0.0)
            a = min(a, 1.0)
        
        # extend path for negative arclength by first location
        if not normalized:
            if projected and a <= self._samples[0]._arcp:
                return self._samples[0]._proj
            elif a <= self._samples[0]._arc:
                return self._samples[0]._loc
            
        
        for i in range(0, len(self._samples) - 1):
        
            s1 = self._samples[i]
            s2 = self._samples[i + 1]
            
            # interpolate time linearly based on arclength
            if projected:
                if normalized:
                    if a >= s1._narcp and a < s2._narcp:
                        w = (a - s1._narcp) / (s2._narcp - s1._narcp)
                        return s1._proj + w * (s2._proj - s1._proj)                        
                else:
                    if a >= s1._arcp and a < s2._arcp:
                        w = (a - s1._arcp) / (s2._arcp - s1._arcp)
                        return s1._proj + w * (s2._proj - s1._proj)
            else:
                if normalized:
                    if a >= s1._narc and a < s2._narc:
                        w = (a - s1._narc) / (s2._narc - s1._narc)
                        return s1._loc + w * (s2._loc - s1._loc)
                else:
                    if a >= s1._arc and a < s2._arc:
                        w = (a - s1._arc) / (s2._arc - s1._arc)
                        return s1._loc + w * (s2._loc - s1._loc)
        
        return self._samples[-1]._loc
    
    
    def point_from_time(self, t, projected = False):
        """Returns a point for time.
        """
        
        if self._debug: print("evaluating point for time ", t)
        
        for i in range(len(self._samples) - 1):
        
            s1 = self._samples[i]
            s2 = self._samples[i + 1]
            
            if t > s1._time - EPSILON and t < s2._time + EPSILON:
                
                # interpolate arclength linearly based on time
                if projected:
                    diff = s2._proj - s1._proj
                else:
                    diff = s2._loc - s1._loc
                    
                tdiff = s2._time - s1._time
                
                if tdiff == 0:
                    tdiff = 1
                
                w = (t - s1._time) / tdiff
                
                if projected:
                    return s1._proj + w * diff
                else:
                    return s1._loc + w * diff
        
        if t < self.start_time:
            if projected:
                return self._samples[0]._proj
            else:
                return self._samples[0]._loc
        elif t > self.end_time:
            if projected:
                return self._samples[-1]._proj
            else:
                return self._samples[-1]._loc
        return None
    
    
    def sample_from_point(self, point, arc_current=0, arc_last=0, arc_start=0, k_arc=0, k_dir=0, threshold=1000000, priority_threshold=1000000, priority_flags={}):
        """Returns sample closest to point
        """
        
        dim = len(point.to_tuple())
        dist = threshold
        closest = None
        dir = arc_current - arc_last
        
        if dim == 2:
            for sample in self._samples:
                
                if sample._arcp < arc_start:
                    continue
                
                # distance including arclength continuity
                arcdiff = sample._arcp - arc_current
                d = (point - sample._proj).length_squared + arcdiff * arcdiff * k_arc
                
                # directional continuity factor
                if arcdiff * dir < -EPSILON:
                    d += k_dir
                
                # save closest
                if d < dist:
                    dist = d
                    closest = sample
                
                # give priority
                if d < priority_threshold and sample._flag in priority_flags:
                    return sample
        
        elif dim == 3:
            for sample in self._samples:
                
                if sample._arc < arc_start:
                    continue
                
                # distance including arclength continuity factor
                arcdiff = sample._arc - arc_current
                d = (point - sample._loc).length_squared + arcdiff * arcdiff * k_arc
                
                # directional continuity factor
                if arcdiff * dir < -EPSILON:
                    d += k_dir
                
                # save closest
                if d < dist:
                    dist = d
                    closest = sample
                
                # give priority
                if d < priority_threshold and sample._flag in priority_flags:
                    return sample
        
        return closest
    
    
    def time_from_arclength(self, a, projected = False, normalized = False):
        """ Interpolates time linearly from closest two path samples
            determined by given a with respect to arclength.
        """
        
        if self._debug: print("evaluating time at arclength", a)
        
        if normalized:
            a = max(a, 0.0)
            a = min(a, 1.0)
        
        for i in range(0, len(self._samples) - 1):
        
            s1 = self._samples[i]
            s2 = self._samples[i + 1]
            
            # interpolate time linearly based on arclength
            if projected:
                if normalized:
                    if a >= s1._narcp and a < s2._narcp:
                        w = (a - s1._narcp) / (s2._narcp - s1._narcp)
                        return s1._time + w * (s2._time - s1._time)                        
                else:
                    if a >= s1._arcp and a < s2._arcp:
                        w = (a - s1._arcp) / (s2._arcp - s1._arcp)
                        return s1._time + w * (s2._time - s1._time)
            else:
                if normalized:
                    if a >= s1._narc and a < s2._narc:
                        w = (a - s1._narc) / (s2._narc - s1._narc)
                        return s1._time + w * (s2._time - s1._time)
                else:
                    if a >= s1._arc and a < s2._arc:
                        w = (a - s1._arc) / (s2._arc - s1._arc)
                        return s1._time + w * (s2._time - s1._time)
        
        return self._samples[-1]._time
    
    
    def arclength_from_time(self, t, projected = False, normalized = False):
        """Interpolates arclength linearly from closest two path samples determined by given t with respect to time.
        """
        
        if self._debug: print("evaluating arclength for time", t)
        
        # cap top and bottom
        t = max(t, self.start_time)
        t = min(t, self.end_time)
        
        for i in range(0, len(self._samples) - 1):
        
            s1 = self._samples[i]
            s2 = self._samples[i + 1]
            
            if t >= s1._time and t < s2._time:
                
                # interpolate arclength linearly based on time
                if projected:
                    if normalized:
                        adiff = s2._narcp - s1._narcp
                    else:
                        adiff = s2._arcp - s1._arcp
                    tdiff = s2._time - s1._time
                else:
                    if normalized:
                        adiff = s2._narc - s1._narc
                    else:
                        adiff = s2._arc - s1._arc
                    tdiff = s2._time - s1._time
                
                w = (t - s1._time) / tdiff
                
                if projected:
                    if normalized:
                        return s1._narcp + w * adiff
                    else:
                        return s1._arcp + w * adiff
                else:
                    if normalized:
                        return s1._narc + w * adiff
                    else:
                        return s1._arc + w * adiff 
        
        if projected:
            if normalized:
                return self._samples[len(self._samples) - 1]._narcp
            else:
                return self._samples[len(self._samples) - 1]._arcp
        else:
            if normalized:
                return self._samples[len(self._samples) - 1]._narc
            else:
                return self._samples[len(self._samples) - 1]._arc
    
    
    @classmethod
    def get_area(cls, context, type):
        
        if context.area and context.area.type == type:
            return context.area
        else:
            for area in context.screen.areas:
                if area.type == type:
                    return area
        
        return None
    
    @classmethod
    def get_region(cls, area, type):
        
        if area:
            for region in area.regions:
                if region.type == type:
                    return region
        
        return None
    
    
    def draw_begin(self, context):
        """Adds calc and draw callbacks to an arbitrary 3D_VIEW area WINDOW region on the current screen. 
           Blender seems to add the callbacks to all 3D_VIEW regions of type WINDOW...
        """
        
        area = self.get_area(context, 'VIEW_3D')
        region = self.get_region(area, 'WINDOW')
        
        if region:
            
            # causes segfault with startup scripts!
#            if context.mode == "POSE":
#                bpy.ops.pose.paths_clear()
#            elif context.mode == "OBJECT":
#                bpy.ops.object.paths_clear()
            
            # this seems to add a callback to all 3D_VIEW regions of type WINDOW!
            self._calc_handle = region.callback_add(self.calc_callback, (context,), 'POST_VIEW')
            self._draw_handle = region.callback_add(self.draw_callback, (context,), 'POST_PIXEL')
            area.tag_redraw()
            
            self.visible = True
    
    
    def draw_end(self, context):
        """Removes calc and draw callbacks from an arbitrary 3D_VIEW area WINDOW region on the the current screen.
           Blender seems to remove the callbacks from all 3D_VIEW regions of type WINDOW...
        """
        
        area = self.get_area(context, 'VIEW_3D')
        region = self.get_region(area, 'WINDOW')
        
        if region:
            try:
                
                # this seems to remove callback from all 3D_VIEW regions of type WINDOW!
                region.callback_remove(self._calc_handle)
                region.callback_remove(self._draw_handle)
                
                # update all 3D view areas
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                
                self.visible = False
                
            except:
                pass
    
    
    def draw_callback(self, context):
        
        if context.mode not in ['OBJECT', 'POSE']:
            return
        
        area = MotionPath.get_area(context, 'VIEW_3D')
        
        if not self._is_2d or not area:
            return
        
        LINE_WIDTH = 1
        POINT_SIZE = 1
        STAR_SIZE = 10
        CROSS_SIZE = 7.07106781186547
                
        # draw line
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor3f(self.props.color.r, self.props.color.g, self.props.color.b)
        bgl.glLineWidth(LINE_WIDTH)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for sample in self._samples:
            if sample._proj is not None:
                bgl.glVertex2i(int(sample._proj.x), int(sample._proj.y))
        bgl.glEnd()
        
        feature_count = 1
        
        # draw points
        bgl.glPointSize(POINT_SIZE)
        for sample in self._samples:
            
            if sample._proj is None:
                continue
            
            x = sample._proj.x
            y = sample._proj.y
            
#            if self._features_type_color:
#                if sample._flag == 'MINMAX_X':
#                    bgl.glColor3f(0, 1, 0)
#                elif sample._flag == 'MINMAX_Y':
#                    bgl.glColor3f(1, 1, 0)
#                elif sample._flag == 'MINMAX_XY':
#                    bgl.glColor3f(1, 0, 0)
#                elif sample._flag == 'CLEANED':
#                    bgl.glColor3f(0, 0, 1)
#                elif sample._flag in {'START', 'END'}:
#                    bgl.glColor3f(1, 0, 1)
            
            if sample._flag in {'MINMAX_X', 'MINMAX_Y', 'MINMAX_XY', 'START', 'END'}:
                # shape
                if self.props.features_shape == 'star':
                    bgl.glBegin(bgl.GL_LINES)
                    bgl.glVertex2i(int(x - STAR_SIZE), int(y))
                    bgl.glVertex2i(int(x + STAR_SIZE + 1), int(y))
                    bgl.glVertex2i(int(x), int(y - STAR_SIZE))
                    bgl.glVertex2i(int(x), int(y + STAR_SIZE + 1))
                    bgl.glEnd()
                    
                    blf.position(0, int(x) + 15, int(y) - 5, 0)
                    blf.size(0, 14, 72)
                    blf.draw(0, str(feature_count))
                    
                elif self.props.features_shape == 'cross':
                    bgl.glBegin(bgl.GL_LINES)
                    bgl.glVertex2i(int(x - CROSS_SIZE), int(y - CROSS_SIZE))
                    bgl.glVertex2i(int(x + CROSS_SIZE + 1), int(y + CROSS_SIZE + 1))
                    bgl.glVertex2i(int(x - CROSS_SIZE), int(y + CROSS_SIZE))
                    bgl.glVertex2i(int(x + CROSS_SIZE + 1), int(y - CROSS_SIZE - 1))
                    bgl.glEnd()
                    
                    blf.position(0, int(x) + 15, int(y) - 5, 0)
                    blf.size(0, 14, 72)
                    blf.draw(0, str(feature_count))
                
                feature_count += 1
                
            else:
                # point
                bgl.glBegin(bgl.GL_POINTS)
                bgl.glVertex2i(int(x), int(y))
                bgl.glEnd()
        
        area.tag_redraw()
    
    
    def calc_callback(self, context):
        
        self._proj_index = -1
        self.calculate_projection(context.area)
    
    
    @classmethod
    def object_has_motion(cls, object):
        
        has_motion = False
        
        while object is not None:
            has_motion = (object.animation_data is not None) or has_motion
            object = object.parent
        
        return has_motion


class MotionPathDrawOperator(bpy.types.Operator):
    '''Calculates a motion path for the active object'''
    
    bl_idname = 'view3d.motion_path_draw'
    bl_label = 'Motion Path Draw'
    
    visible = bpy.props.BoolProperty(default=True)
    
    
    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return(False)
        return(context.active_object.mode in ['OBJECT', 'POSE'])
    
    
    def invoke(self, context, event):
        
        path = None
        area = MotionPath.get_area(context, 'VIEW_3D')
        props = context.window_manager.motion_path
        
        # calculate path if not already calculated
        try:
            path = context.window_manager.active_motion_path
        except:
            pass
        
        if not path:
            path = MotionPath(props, context.active_object)
            bpy.types.WindowManager.active_motion_path = path
        
        path.calculate_projection(area)
        path.calculate_arclength()
        
        # draw path
        if self.visible and not path.visible:
            path.draw_begin(context)
        
        # register modal handler
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    
    def modal(self, context, event):
        
        # check whether active path still exists
        try:
            path = context.window_manager.active_motion_path
        except:
            return {'FINISHED'}
        
        # check whether active object has changed
        if path.target != context.active_object or path.target_bone != context.active_pose_bone:
            path.recalculate(context.active_object)
            path.calculate_projection(MotionPath.get_area(context, 'VIEW_3D'))
            path.calculate_arclength()
        
        return {'PASS_THROUGH'}


class MotionPathClearOperator(bpy.types.Operator):
    '''Clears motion path'''
    
    bl_idname = 'view3d.motion_path_clear'
    bl_label = 'Motion Path Clear'
    
    
    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return(False)
        return(context.active_object.mode in ['OBJECT', 'POSE'])
    
    
    def execute(self, context):
        
        try:
            context.window_manager.active_motion_path.draw_end(context)
            del bpy.types.WindowManager.active_motion_path
        except:
            pass
        
        return {'FINISHED'}


class MotionPathPanel(bpy.types.Panel):
    
    bl_label = "Motion Path"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    
    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return(False)
        return(context.active_object.mode in ['OBJECT', 'POSE'])
    
    
    def draw(self, context):
        
        props = context.window_manager.motion_path
        
        col = self.layout.column(align=True)
        col.operator("view3d.motion_path_draw", text="Calculate Path")
        col.operator("view3d.motion_path_clear", text="Clear Path")
                
        box = self.layout.box()
        box.prop(props, "res_mode", text="Resolution")
        if props.res_mode == "spatial":
            box.prop(props, "res_spatial", text="Units")
        elif props.res_mode == "temporal":
            box.prop(props, "res_temporal", text="Frames")
        
        if context.active_object.mode == 'POSE':
            box = self.layout.box()    
            box.prop(props, "bone_mode", text="Bone")


class MotionPathProps(bpy.types.PropertyGroup):
    
    def update(self, context):
        path = None
        try:
            path = context.window_manager.active_motion_path
        except:
            pass
        if path and self.auto_recalc:
            if self.res_mode == 'spatial':
                path.from_object_spatial(context.active_object, s_res=self.res_spatial, bone_mode=self.bone_mode)
            elif self.res_mode == 'temporal':
                path.from_object_temporal(context.active_object, t_res=self.res_temporal, bone_mode=self.bone_mode)
            path.calculate_projection(context.area)
            path.calculate_arclength()
    
    
    res_mode = bpy.props.EnumProperty(name="Resolution Mode", \
        description="Sample motion path based on time or on arclength", \
        items=(("temporal", "Temporal", "Determine path resolution based on time"), \
               ("spatial", "Spatial", "Determine path resolution based on arclength")), \
        default="spatial",
        update=update)
    res_spatial = bpy.props.FloatProperty(name="Spatial Resolution", \
        description="Spatial sampling resolution in Blender units", \
        default=0.5, min=0.01, max=1.0, update=update)
    res_temporal = bpy.props.FloatProperty(name="Temporal Resolution", \
        description="Temporal sampling resolution in frames", \
        default=1.0, min=0.1, max=1.0, update=update)
    bone_mode = bpy.props.EnumProperty(name="Bone Mode", \
        items=(("head", "Head", "Use bone head position when calculating motion path"), \
               ("tail", "Tail", "Use bone tail position when calculating motion path"), \
               ("middle", "Middle", "Use position halfway between bone head and tail when calculating motion path")), \
        default="tail", \
        update=update)
    auto_recalc = bpy.props.BoolProperty(name="Auto-recalculate", \
        description="Automatically recalculate path on changes.", \
        default=True)
    color = bpy.props.FloatVectorProperty(name="Color", default=(0.95, 0.58, 0), \
        min=0.0, max=1.0, precision=2, subtype='COLOR', size=3)
    features_shape = bpy.props.EnumProperty(name="Feature Shape", \
        items=(("star", "Star", "Draw features in star shape."), \
               ("cross", "Cross", "Draw features in cross shape.")), \
        default="star")
