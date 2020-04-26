'''
Copyright (C) 2018 CG Cookie
https://github.com/CGCookie/retopoflow
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

import inspect

import bpy
import gpu
import mathutils
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_line_sphere


class CookieCutter_FSM:
    '''- register finite state machine state callbacks with the CookieCutter.FSM_State(state) function decorator
        - state can be any string that is a state in your FSM
        - Must provide at least a 'main' state
        - return values of each FSM_State decorated function tell FSM which state to switch into
            - None, '', or no return: stay in same state'''
    class FSM_State:
        @staticmethod
        def get_state(state, substate):
            return '%s__%s' % (str(state), str(substate))

        def __init__(self, state, substate='main'):
            self.state = state
            self.substate = substate

        def __call__(self, fn):
            self.fn = fn
            self.fnname = fn.__name__

            def run(*args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print('Caught exception in function "%s" ("%s", "%s")' % (
                        self.fnname, self.state, self.substate
                    ))
                    print (e)
                    return
            run.fnname = self.fnname
            run.fsmstate = CookieCutter_FSM.FSM_State.get_state(self.state, self.substate)
            return run

    def find_fns(self, key):
        c = type(self)
        objs = [getattr(c,k) for k in dir(c)]
        fns = [fn for fn in objs if inspect.isfunction(fn)]
        return [(getattr(fn,key),fn) for fn in fns if hasattr(fn,key)]

    def fsm_init(self):
        self._state_next = 'main'
        self._state = None
        self._fsm_states = {}
        for (m, fn) in self.find_fns('fsmstate'):
            assert m not in self._fsm_states, 'Duplicate states registered!'
            self._fsm_states[m] = fn

    def _fsm_call(self, state, substate='main', fail_if_not_exist=False):
        s = CookieCutter_FSM.FSM_State.get_state(state, substate)
        if s not in self._fsm_states:
            assert not fail_if_not_exist
            return
        try:
            return self._fsm_states[s](self)
        except Exception as e:
            print('Caught exception in state ("%s")' % (s))
            print(e)
            return

    def fsm_update(self):
        if self._state_next is not None and self._state_next != self._state:
            if self._fsm_call(self._state, substate='can exit') == False:
                # print('Cannot exit %s' % str(self._state))
                self._state_next = None
                return
            if self._fsm_call(self._state_next, substate='can enter') == False:
                # print('Cannot enter %s' % str(self._state_next))
                self._state_next = None
                return
            # print('%s -> %s' % (str(self._state), str(self._state_next)))
            self._fsm_call(self._state, substate='exit')
            self._state = self._state_next
            self._fsm_call(self._state, substate='enter')
        self._state_next = self._fsm_call(self._state, fail_if_not_exist=True)


class ModalCommon:
    """Common Operator methods for garment editing are defined here"""

    _handle_draw_verts = None
    _handle_draw_text = None

    patter_segments_cache = {}
    garment_index = 0
    event = None
    context = None
    allow_nav = False
    done = False

    @staticmethod
    def draw_text(self, context):
        '''Cos self is passed by handler'''
        pass

    @staticmethod
    def draw_px(self, context):
        '''Cos self is passed by handler'''
        pass

    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

    @staticmethod
    def visible_objects_and_duplis(context):
        """Loop over (object, matrix) pairs (mesh only)"""
        for obj in context.visible_objects:
            if obj.type == 'CURVE':
                yield (obj)

    @staticmethod
    def scene_objects_and_duplis(context):
        """Loop over (object, matrix) pairs (mesh only)"""
        for obj in context.scene.objects:
            if obj.type == 'CURVE':
                yield (obj)

    @staticmethod
    def get_segments_len(segments_points):
        '''Return segments  points len '''
        out_segments_lens = []
        for points in segments_points:
            previous_point = points[0]
            segment_len = 0
            for point in points:
                point_diff_vec = point - previous_point
                segment_len += point_diff_vec.length
                previous_point = point
            out_segments_lens.append(segment_len)
        return out_segments_lens

    @staticmethod
    def curve_resample(curve_obj, resolution):
        '''Return list of points for each 2D curve segment. Assume curve obj, has segment count dict assigned '''
        spline = curve_obj.data.splines[0]
        points_count = len(spline.bezier_points)
        output_points = []
        for i in range(points_count):
            knot1 = spline.bezier_points[i].co
            handle1 = spline.bezier_points[i].handle_right
            knot2 = spline.bezier_points[(i+1) % points_count].co
            handle2 = spline.bezier_points[(i+1) % points_count].handle_left
            interpolated = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, resolution)
            output_points.append([curve_obj.matrix_world @ point for point in interpolated])
        return output_points

    def obj_ray_cast(self, obj, ray_origin, ray_target):
        """Wrapper for ray casting that moves the ray into object space"""
        # get the ray relative to the object
        ray_direction = ray_target - ray_origin
        sourceTri_BVHT = self.construct_pattern_BVHTree(obj)  # [0,1,2] - polygon == vert indices list
        # location, normal, index, dist =
        return sourceTri_BVHT.ray_cast(ray_origin, ray_direction, 600)

    def curve_ray_cast(self, obj, ray_origin, ray_target):
        """Wrapper for ray casting that moves the ray into object space"""
        # get the ray relative to the object
        ray_direction = ray_target - ray_origin
        resampled_curve_segments = self.patter_segments_cache[obj.name]
        segments_points_flat = []
        for segment in resampled_curve_segments:  # add cloth sillayette
            segments_points_flat.extend(segment[:-1])
        # cast the ray
        sourceTri_BVHT = BVHTree.FromPolygons(segments_points_flat, [tuple(i for i in range(len(
            segments_points_flat)))], all_triangles=False)  # [0,1,2] - polygon == vert indices list
        # location, normal, index, dist =
        return sourceTri_BVHT.ray_cast(ray_origin, ray_direction, 600)

    def construct_pattern_BVHTree(self, obj):
        # give world space points ( multiplied by obj.mat_world)
        resampled_curve_segments = self.patter_segments_cache[obj.name]
        segments_points_flat = []
        for segment in resampled_curve_segments:  # add cloth sillayette
            segments_points_flat.extend(segment[:-1])

        # cast the ray
        sourceTri_BVHT = BVHTree.FromPolygons(segments_points_flat, [tuple(i for i in range(len(
            segments_points_flat)))], all_triangles=False)  # [0,1,2] - polygon == vert indices list
        return sourceTri_BVHT

    def find_curve_under_cursor(self, context, event):
        """Run this function on left mouse, execute the ray cast"""
        # get the context arguments
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        # get the ray from the viewport and mouse
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = ray_origin + view_vector

        # cast rays and find the closest object
        best_length_squared = -1.0
        best_obj = None

        for obj in self.visible_objects_and_duplis(context):
            if obj.type == 'CURVE':
                hit_world, normal, face_index, dist = self.obj_ray_cast(obj, ray_origin, ray_target)
                if hit_world is not None:
                    length_squared = (hit_world - ray_origin).length_squared
                    if best_obj is None or length_squared < best_length_squared:
                        best_length_squared = length_squared
                        best_obj = obj

        # now we have the object under the mouse cursor,
        return best_obj

    def hit_obj_pos(self, context, hit_obj):
        ''' Return index of pin closest to mouse'''
        """Run this function on left mouse, execute the ray cast"""
        region = context.region
        rv3d = context.region_data
        coord = self.event.mouse_region_x, self.event.mouse_region_y

        # get the ray from the viewport and mouse
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        ray_target = ray_origin + view_vector
        # cast rays and find the closest object
        hit_world, normal, face_index, dist = self.obj_ray_cast(hit_obj, ray_origin, ray_target)
        hit_local = hit_obj.matrix_world.inverted() @ hit_world if hit_world else None
        if hit_local is not None:
            hit_local.z = 0  # cos it is flat
        return hit_local

    def assign_target_obj_to_garment(self,  target_obj):
        for pattern in self.garment.sewing_patterns:
            if pattern.pattern_obj == target_obj:
                return
        self.garment.sewing_patterns.add()
        self.garment.sewing_patterns[-1].pattern_obj = target_obj

    # @CookieCutter_FSM.FSM_State('main')
    # def modal_main(self):
    #     pass

    def end_cancel(self):
        self.disable_handlers()
        bpy.ops.ed.undo()
        bpy.ops.garment.cleanup(garment_index=self.garment_index)
        self.done = 'CANCELLED'

    def end_commit(self):
        self.disable_handlers()
        bpy.ops.garment.cleanup(garment_index=self.garment_index)
        self.done = 'FINISHED'

    def disable_handlers(self):
        if self._handle_draw_verts:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw_verts, 'WINDOW')
        if self._handle_draw_text:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_draw_text, 'WINDOW')



    def invoke_common(self, context, event):
        bpy.ops.garment.cleanup(garment_index=self.garment_index)
        bpy.ops.ed.undo_push()
        for obj in context.view_layer.objects:
            obj.select_set(False)

        self.event = event
        self.context = context
        self.allow_nav = False
        self.done = False

        self.garment = context.scene.cloth_garment_data[self.garment_index]
        self.patter_segments_cache.clear()

        #maybe do this on pocket picking? But we need it for hover before
        for obj in self.visible_objects_and_duplis(context):
            if obj.type == 'CURVE':
                resampled_curve_segments = self.curve_resample(obj, 8)
                segment_len = self.get_segments_len(resampled_curve_segments)
                self.patter_segments_cache[obj.name] = resampled_curve_segments
                self.patter_segments_cache[obj.name+'_len'] = segment_len

        args = (self, context)
        if not self._handle_draw_verts:
            self._handle_draw_verts = bpy.types.SpaceView3D.draw_handler_add(self.draw_px, args, 'WINDOW', 'POST_VIEW')
        if not self._handle_draw_text:
            self._handle_draw_text = bpy.types.SpaceView3D.draw_handler_add(self.draw_text, args, 'WINDOW', 'POST_PIXEL')



