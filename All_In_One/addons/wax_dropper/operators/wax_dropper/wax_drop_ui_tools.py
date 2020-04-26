# Copyright (C) 2018 Patrick Moore
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import time
import math
import numpy

# Blender imports
import bpy
import bmesh
import bgl
from bpy_extras import view3d_utils
from mathutils import Vector, kdtree, Color, Matrix
from mathutils.geometry import intersect_point_line
from mathutils.bvhtree import BVHTree

# Addon imports
from .wax_drop_datastructure import InputNetwork, InputPoint, InputSegment, SplineSegment, CurveNode
from ...functions import *
from ...addon_common.common.utils import get_matrices
from ...addon_common.common.maths import Point, Direction, XForm, space_evenly_on_path, get_path_length
from ...addon_common.common.bezier import CubicBezierSpline

class WaxDrop_UI_Tools():
    '''
    Functions/classes helpful with user interactions in polytrim
    '''

    class SketchManager():
        '''
        UI tool for managing sketches made by user.
        * Intermediary between polytrim_states and Network
        '''
        def __init__(self, input_net, spline_net, net_ui_context, network_cutter):
            self.sketch = []
            self.input_net = input_net
            self.spline_net = spline_net
            self.network_cutter = network_cutter
            self.net_ui_context = net_ui_context
            self.stroke_smoothing = 0.75  # 0: no smoothing. 1: no change
            self.sketch_curpos = (0, 0)
            self.bez_data = []

        def has_locs(self): return len(self.sketch) > 0
        has_locs = property(has_locs)

        def get_locs(self): return self.sketch

        def reset(self): self.sketch = []

        def add_loc(self, x, y):
            ''' Add's a screen location to the sketch list '''
            self.sketch.append((x,y))

        def smart_add_loc(self, x, y):
            ''' Add's a screen location to the sketch list based on smart stuff '''
            (lx, ly) = self.sketch[-1]
            ss0,ss1 = self.stroke_smoothing ,1-self.stroke_smoothing  #First data manipulation
            self.sketch += [(lx*ss0+x*ss1, ly*ss0+y*ss1)]

        def is_good(self):
            ''' Returns whether the sketch attempt should/shouldn't be added to the InputNetwork '''
            # checking to see if sketch functionality shouldn't happen
            if len(self.sketch) < 5 and self.net_ui_context.ui_type == 'DENSE_POLY': return False
            return True

        def finalize_uniform(self, context, net_ui_context, shift_func, step_size:float=0.5, error_threshold:float=0.25):
            """ finalizes sketch data uniformly """
            # get 3d points on mesh from screen-space sketch
            start = time.time()

            sketch_3d = []
            for pt in self.sketch:
                view_vector, ray_origin, ray_target = get_view_ray_data(context, pt)  # location and direction in WORLD coordinates
                loc, norm, face_idx = ray_cast_bvh(net_ui_context.bvh, net_ui_context.imx, ray_origin, ray_target, None)
                if face_idx != None:
                    new_loc = net_ui_context.mx * shift_func(loc, norm)
                    sketch_3d.append(new_loc)

            finish = time.time()
            # print('ray cast in %f' % (finish-start))
            start = finish
            # slice over sketch_3d to get simplified points
            #TODO error threshold should be related to particle size.  Eg .1 # self.blob_size
            important_idxs = simplify_RDP(sketch_3d, error_threshold)

            finish = time.time()
            # print('found important verts in %f' % (finish-start))
            start = finish

            # get important locations from important indices in sketch_3d
            locs = [loc for i,loc in enumerate(sketch_3d) if i in important_idxs]  # TODO: make this list initialization more efficient

            # get evenly spaced group of points along path of important locations
            #TODO step size should be related to particle size to "overpack" them into creating tubes
            new_locs = space_evenly_on_path(locs, segments=int(get_path_length(locs)/step_size))

            finish = time.time()
            # print('spaced evenly on path in %f' % (finish-start))
            start = finish

            # returns evenly spaced locs along sketch
            return new_locs

        def finalize(self, context, start_pnt, end_pnt=None):
            ''' takes sketch data and adds it into the data structures '''

            print('Finalizing sketching', start_pnt, end_pnt)
            if not isinstance(end_pnt, InputPoint) or isinstance(end_pnt, CurveNode):
                end_pnt = None
            if not isinstance(start_pnt, InputPoint) or isinstance(start_pnt, CurveNode):
                prev_pnt = None
            else:
                prev_pnt = start_pnt

            #FINALIZE INPUT NET MODE
            if isinstance(start_pnt, InputPoint):
                for ind in range(0, len(self.sketch) , 5):
                    if not prev_pnt:
                        if self.input_net.num_points == 1: new_pnt = self.input_net.points[0]
                        else: new_pnt = start_pnt
                    else:
                        pt_screen_loc = self.sketch[ind]  #in screen space
                        view_vector, ray_origin, ray_target = get_view_ray_data(context, pt_screen_loc)  #a location and direction in WORLD coordinates
                        #loc, no, face_ind =  ray_cast(self.net_ui_context.ob,self.net_ui_context.imx, ray_origin, ray_target, None)  #intersects that ray with the geometry
                        loc, no, face_ind =  ray_cast_bvh(self.net_ui_context.bvh,self.net_ui_context.imx, ray_origin, ray_target, None)
                        if face_ind != None:
                            new_pnt = self.input_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)
                    if prev_pnt:
                        print(prev_pnt)
                        seg = InputSegment(prev_pnt,new_pnt)
                        self.input_net.segments.append(seg)

                        #self.network_cutter.precompute_cut(seg)
                        #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)
                    prev_pnt = new_pnt
                if end_pnt:
                    seg = InputSegment(prev_pnt,end_pnt)
                    self.input_net.segments.append(seg)

            #FINALIZE CURVE NETWORK MODE
            else:
                sketch_3d = []
                other_data = []
                for pt in self.sketch:
                    view_vector, ray_origin, ray_target = get_view_ray_data(context, pt)  #a location and direction in WORLD coordinates
                    # loc, no, face_ind =  ray_cast(self.net_ui_context.ob,self.net_ui_context.imx, ray_origin, ray_target, None)  #intersects that ray with the geometry
                    loc, no, face_ind =  ray_cast_bvh(self.net_ui_context.bvh,self.net_ui_context.imx, ray_origin, ray_target, None)
                    if face_ind != None:
                            sketch_3d += [self.net_ui_context.mx * loc]
                            other_data += [(loc, view_vector, face_ind)]

                # slice over sketch_3d to get simplified points
                feature_inds = simplify_RDP(sketch_3d, .25)  #TODO, 0.25 sketch threshold as parameter

                new_points = []
                new_segs = []
                for ind in feature_inds:
                    if not prev_pnt:
                        if self.spline_net.num_points == 1: new_pnt = self.spline_net.points[0]
                        else: new_pnt = start_pnt
                    else:
                        loc3d = sketch_3d[ind]
                        loc, view_vector, face_ind = other_data[ind]
                        new_pnt = self.spline_net.create_point(loc3d, loc, view_vector, face_ind)
                        new_points += [new_pnt]
                    if prev_pnt:
                        print(prev_pnt)
                        seg = SplineSegment(prev_pnt,new_pnt)
                        self.spline_net.segments.append(seg)
                        new_segs += [seg]
                        # self.network_cutter.precompute_cut(seg)
                        # seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)
                    prev_pnt = new_pnt
                if end_pnt:
                    seg = SplineSegment(prev_pnt,end_pnt)
                    self.spline_net.segments.append(seg)
                    new_segs += [seg]
                for p in new_points:
                    p.calc_handles()
                for seg in new_segs:
                    seg.calc_bezier()
                    seg.tessellate()
                    seg.tessellate_IP_error(.1)


        def finalize_bezier(self, context):

            stroke3d = []
            for ind in range(0, len(self.sketch) , 5):
                pt_screen_loc = self.sketch[ind]  #in screen space
                view_vector, ray_origin, ray_target = get_view_ray_data(context, pt_screen_loc)  #a location and direction in WORLD coordinates
                    #loc, no, face_ind =  ray_cast(self.net_ui_context.ob,self.net_ui_context.imx, ray_origin, ray_target, None)  #intersects that ray with the geometry
                loc, no, face_ind =  ray_cast_bvh(self.net_ui_context.bvh,self.net_ui_context.imx, ray_origin, ray_target, None)
                if face_ind != None:
                    stroke3d += [self.net_ui_context.mx * loc]

            #print(stroke3d)
            cbs = CubicBezierSpline.create_from_points([stroke3d], .05)
            cbs.tessellate_uniform(lambda p,q:(p-q).length, split=20)
            L = cbs.approximate_totlength_tessellation()
            n = L/2  #2mm spacing long strokes?
            #print(cbs.tessellation)

            self.bez_data = []
            for btess in cbs.tessellation:
                self.bez_data += [pt.as_vector() for i,pt,d in btess]


    class PaintBrush():  #TODO replace with widget, this is a coars placeholder
        #active patch?  meaning we are updating a selection
        def __init__(self, net_ui_context, radius=1.5, color=(0.8, 0.1, 0.3)):
            self.net_ui_context = net_ui_context
            self.xform = XForm(self.net_ui_context.ob.matrix_world)
            self.radius = radius
            self.brush_color = Color(color)
            #self.brush_rad_pixel = 40
            self.geom_accum = set()  #FACES

            #TODO....figure out if we need a dual color layer?
            if "patches" not in self.net_ui_context.bme.loops.layers.color:
                vcol_layer = self.net_ui_context.bme.loops.layers.color.new("patches")
            else:
                vcol_layer = self.net_ui_context.bme.loops.layers.color["patches"]

            self.vcol = vcol_layer
            self.points = [(math.cos(math.radians(t)), math.sin(math.radians(t))) for t in range(0,361,10)]
            self.spiral_points = []


        def calc_npoints(self, density):
            '''
            density in points/mm^2
            '''

            area = math.pi * self.radius**2
            npoints = round(area*density)
            npoints = max(min(1000, npoints), 16)

            return npoints

        def generate_spiral_points(self, npoints):

            n = npoints


            golden_angle = math.pi * (3 - math.sqrt(5))

            points = []
            for i in range(n):
                theta = i * golden_angle
                r = math.sqrt(i) / math.sqrt(n)
                points.append((r * math.cos(theta), r * math.sin(theta)))

            #Using numpy, one can use vector operations like this
            #radius = numpy.sqrt(numpy.arange(n) / float(n))
            #golden_angle = numpy.pi * (3 - numpy.sqrt(5))
            #theta = golden_angle * numpy.arange(n)
            #points = numpy.zeros((n, 2))
            #points[:,0] = numpy.cos(theta)
            #points[:,1] = numpy.sin(theta)
            #points *= radius.reshape((n, 1))

            self.spiral_points = points

        def spiral_points_to_3d(self, loc, norm):
            # convert to 3d locations
            norm = self.xform.l2w_normal(norm)
            tr = Vector((0,0,1)) if abs(norm.z) < 0.9 else Vector((1,0,0))
            tx = Direction(norm.cross(tr))
            ty = Direction(norm.cross(tx))
            spiral_points_3d = list()
            for mx, my in self.spiral_points:  #spiral cluster
                p = loc + (tx * mx + ty * my) * self.radius
                spiral_points_3d.append(p)
            return spiral_points_3d

        def ray_hit(self, pt_screen, context):
            view_vector, ray_origin, ray_target = get_view_ray_data(context, pt_screen)  #a location and direction in WORLD coordinates
            return ray_cast_bvh(self.net_ui_context.bvh, self.net_ui_context.imx, ray_origin, ray_target, None)

        def absorb_geom(self, context, pt_screen_loc):
            loc, no, face_ind = self.ray_hit(pt_screen_loc, context)
            if not loc: return

            close_geom = self.net_ui_context.bvh.find_nearest_range(loc, self.radius)
            fs = [self.net_ui_context.bme.faces[ind] for  _,_,ind,_ in close_geom]
            self.color_geom(fs)
            self.geom_accum.update(fs)

        def absorb_geom_geodesic(self, context, pt_screen_loc):
            loc, no, face_ind = self.ray_hit(pt_screen_loc, context)
            if not loc: return

            #can do old mapping if bme has been altered
            seed = self.net_ui_context.bme.faces[face_ind]
            geos, fixed_vs, close, far = geodesic_walk(self.net_ui_context.bme, seed, loc, min_dist=self.radius)
            fs_in = set()
            fs_out = set()
            for v in fixed_vs:
                for f in v.link_faces:
                    if f in fs_in or f in fs_out: continue
                    if all([v in fixed_vs for v in f.verts]):
                        fs_in.add(f)
                    else:
                        fs_out.add(f)

            self.color_geom(fs_in)
            self.geom_accum.update(fs_in)

        def color_geom(self, faces):
            for f in faces:
                for loop in f.loops:
                    loop[self.vcol] = self.brush_color

        def color_all_geom(self):
            self.color_geom(self.geom_accum)

        def draw_postview(self, context, pt_screen):
            loc,no,_ = self.ray_hit(pt_screen, context)
            if not loc: return
            loc = self.xform.l2w_point(loc)
            no = self.xform.l2w_normal(no)
            tr = Vector((0,0,1)) if abs(no.z) < 0.9 else Vector((1,0,0))
            tx = Direction(no.cross(tr))
            ty = Direction(no.cross(tx))
            cr,cg,cb = self.brush_color

            bgl.glDepthRange(0, 0.99999)    # squeeze depth just a bit
            bgl.glDepthMask(bgl.GL_FALSE)   # do not overwrite depth
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            bgl.glLineWidth(2.0) # self.drawing.line_width(2.0)
            bgl.glPointSize(3.0) # self.drawing.point_size(3.0)

            ######################################
            # draw in front of geometry

            bgl.glDepthFunc(bgl.GL_LEQUAL)

            bgl.glColor4f(cr, cg, cb, 1.0)       # outer ring
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for mx,my in self.points:
                p = loc + (tx * mx + ty * my) * self.radius
                bgl.glVertex3f(*p)
            bgl.glEnd()

            bgl.glColor4f(cr, cg, cb, 0.1)     # inner ring
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for mx,my in self.points:
                p = loc + (tx * mx + ty * my) * (self.radius * 0.5)
                bgl.glVertex3f(*p)
            bgl.glEnd()

            bgl.glColor4f(1, 1, 1, 0.25)    # center point
            bgl.glBegin(bgl.GL_POINTS)
            bgl.glVertex3f(*loc)


            for mx, my in self.spiral_points:  #spiral cluster
                p = loc + (tx * mx + ty * my) * self.radius
                bgl.glVertex3f(*p)

            bgl.glEnd()

            ######################################
            # draw behind geometry (hidden below)

            bgl.glDepthFunc(bgl.GL_GREATER)

            bgl.glColor4f(cr, cg, cb, 0.05)    # outer ring
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for mx,my in self.points:
                p = loc + (tx * mx + ty * my) * self.radius
                bgl.glVertex3f(*p)
            bgl.glEnd()

            bgl.glColor4f(cr, cg, cb, 0.01)   # inner ring
            bgl.glBegin(bgl.GL_LINE_STRIP)
            for mx,my in self.points:
                p = loc + (tx * mx + ty * my) * (self.radius * 0.5)
                bgl.glVertex3f(*p)
            bgl.glEnd()

            ######################################
            # reset to defaults

            bgl.glDepthFunc(bgl.GL_LEQUAL)
            bgl.glDepthMask(bgl.GL_TRUE)
            bgl.glDepthRange(0, 1)

    # TODO: Clean this up
    def click_add_point(self, context, mouse_loc, connect=True):
        '''
        this will add a point into the trim line
        close the curve into a cyclic curve

        NOTE: Need to get smarter about closing the loop
        '''
        def none_selected(): self.net_ui_context.selected = None # TODO: Change this weird function in function shizz

        view_vector, ray_origin, ray_target= get_view_ray_data(context,mouse_loc)
        #loc, no, face_ind = ray_cast(self.net_ui_context.ob, self.net_ui_context.imx, ray_origin, ray_target, none_selected)
        loc, no, face_ind = ray_cast_bvh(self.net_ui_context.bvh, self.net_ui_context.imx, ray_origin, ray_target, none_selected)

        if loc == None:
            print("Here")
            return

        if self.net_ui_context.hovered_near[0] and 'NON_MAN' in self.net_ui_context.hovered_near[0]:
            bmed, wrld_loc = self.net_ui_context.hovered_near[1] # hovered_near[1] is tuple (BMesh Element, location?)
            ip1 = self.closest_endpoint(wrld_loc)

            self.net_ui_context.selected = self.input_net.create_point(wrld_loc, self.net_ui_context.imx * wrld_loc, view_vector, bmed.link_faces[0].index)
            self.net_ui_context.selected.seed_geom = bmed
            self.net_ui_context.selected.bmedge = bmed  #UNUSED BUT PREPARING FOR FUTURE

            if ip1:
                seg = InputSegment(self.net_ui_context.selected, ip1)
                self.input_net.segments.append(seg)
                self.network_cutter.precompute_cut(seg)
                #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)

        #Add a New Point at end
        elif (self.net_ui_context.hovered_near[0] == None) and (self.net_ui_context.snap_element == None):  #adding in a new point at end, may need to specify closest unlinked vs append and do some previs
            print("Here 11")
            closest_endpoint = self.closest_endpoint(self.net_ui_context.mx * loc)
            self.net_ui_context.selected = self.input_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)
            print('create new point')

            if len(self.spline_net.points):
                last_node = self.spline_net.points[-1]
                new_node = self.spline_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)
                self.spline_net.connect_points(new_node, last_node)
                new_node.update_splines()
                last_node.update_splines()  #this is going to update the spline twice?
            else:
                new_node = self.spline_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)

            if closest_endpoint and connect:
                self.input_net.connect_points(self.net_ui_context.selected, closest_endpoint)
                self.network_cutter.precompute_cut(self.input_net.segments[-1])  #<  Hmm...not very clean.

        elif self.net_ui_context.hovered_near[0] == None and self.net_ui_context.snap_element != None:  #adding in a new point at end, may need to specify closest unlinked vs append and do some previs
            print("Here 2")
            closest_endpoints = self.closest_endpoints(self.net_ui_context.snap_element.world_loc, 2)

            if closest_endpoints == None:
                #we are not quite hovered_near but in snap territory
                return

            if len(closest_endpoints) < 2:
                return

            seg = InputSegment(closest_endpoints[0], closest_endpoints[1])
            self.input_net.segments.append(seg)
            self.network_cutter.precompute_cut(seg)
            #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)

        elif self.net_ui_context.hovered_near[0] == 'POINT':
            self.net_ui_context.selected = self.net_ui_context.hovered_near[1]

        elif self.net_ui_context.hovered_near[0] == 'EDGE':  #TODO, actually make InputSegment as hovered_near
            point = self.input_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)
            old_seg = self.net_ui_context.hovered_near[1]
            self.input_net.insert_point(point, old_seg)
            self.net_ui_context.selected = point
            self.network_cutter.update_segments()


    def add_spline(self, endpoint0, endpoint1):
        assert endpoint0.is_endpoint and endpoint1.is_endpoint
        seg = SplineSegment(endpoint0, endpoint1)
        self.spline_net.segments.append(seg)

        endpoint0.calc_handles()
        endpoint1.calc_handles()

        endpoint0.update_splines()
        endpoint1.update_splines()


        self.spline_net.push_to_input_net(self.net_ui_context, self.input_net)
        self.network_cutter.update_segments_async()
        return seg

    def add_point(self, p2d):
        mx = self.net_ui_context.mx
        imx = self.net_ui_context.imx
        loc, no, face_ind = self.ray_cast_source(p2d, in_world=False)
        if not loc: return None
        view_vector, ray_origin, ray_target = get_view_ray_data(self.context, p2d)

        #add an input node on non manifold edge of mesh
        if self.net_ui_context.hovered_near[0] and 'NON_MAN' in self.net_ui_context.hovered_near[0]:
            bmed, wrld_loc = self.net_ui_context.hovered_near[1]
            p = self.spline_net.create_point(wrld_loc,imx * wrld_loc, view_vector, bmed.link_faces[0].index)
            p.seed_geom = bmed
            p.bmedge = bmed #UNUSED, but preparing for future
        else:
            p = self.spline_net.create_point(mx * loc, loc, view_vector, face_ind)

        return p


    def insert_spline_point(self, p2d):
        mx = self.net_ui_context.mx
        imx = self.net_ui_context.imx
        loc, no, face_ind = self.ray_cast_source(p2d, in_world=False)
        if not loc: return None
        view_vector, ray_origin, ray_target = get_view_ray_data(self.context, p2d)


        p = self.spline_net.create_point(mx * loc, loc, view_vector, face_ind)

        #place holder for later hovering the tessellated line segments
        #old_discrete_seg = self.net_ui_context.hovered_near[1]
        #old_spline_seg = old_discrete_seg.parent_spline
        seg = self.net_ui_context.hovered_near[1]
        n0, n1 = seg.n0, seg.n1
        self.spline_net.insert_point(p, seg)
        seg.clear_input_net_references(self.input_net)
        for node in [n0, p, n1]:
            node.calc_handles()

        #n00 ----- n0 ------ p ------ n1-----n11
        for node in [n0, n1]:  #because n0 and n1 connect to p,  this updates 4 splines
            node.update_splines()

        self.spline_net.push_to_input_net(self.net_ui_context, self.input_net)
        self.network_cutter.update_segments_async()
        self.network_cutter.validate_cdata()
        return p

    def ray_cast_source(self, p2d, in_world=True):
        context = self.context
        view_vector, ray_origin, ray_target = get_view_ray_data(context, p2d)
        mx,imx = self.net_ui_context.mx,self.net_ui_context.imx
        itmx = imx.transposed()
        loc, no, face_ind = ray_cast_bvh(self.net_ui_context.bvh, imx, ray_origin, ray_target)
        return (mx * loc if loc and in_world else loc, itmx * no if no and in_world else no, face_ind)

    def ray_cast_source_hit(self, p2d):
        return self.ray_cast_source(p2d, in_world=False)[0] != None

    def click_add_spline_point(self, context, mouse_loc, connect=True):
        '''
        this will add a point into the trim line
        close the curve into a cyclic curve

        #Need to get smarter about closing the loop
        '''
        def none_selected(): self.net_ui_context.selected = None # TODO: Change this weird function in function shizz

        view_vector, ray_origin, ray_target= get_view_ray_data(context,mouse_loc)
        #loc, no, face_ind = ray_cast(self.net_ui_context.ob, self.net_ui_context.imx, ray_origin, ray_target, none_selected)
        loc, no, face_ind = ray_cast_bvh(self.net_ui_context.bvh, self.net_ui_context.imx, ray_origin, ray_target, none_selected)

        if not loc: return

        #Add a new edge_point?
        if self.net_ui_context.hovered_near[0] and 'NON_MAN' in self.net_ui_context.hovered_near[0]:
            bmed, wrld_loc = self.net_ui_context.hovered_near[1] # hovered_near[1] is tuple (BMesh Element, location?)
            ip1 = self.closest_spline_endpoint(wrld_loc)

            self.net_ui_context.selected = self.spline_net.create_point(wrld_loc, self.net_ui_context.imx * wrld_loc, view_vector, bmed.link_faces[0].index)
            self.net_ui_context.selected.seed_geom = bmed
            self.net_ui_context.selected.bmedge = bmed  #UNUSED, but preparing for future

            self.net_ui_context.selected.update_splines()

            if ip1:
                seg = SplineSegment(self.net_ui_context.selected, ip1)
                self.spline_net.segments.append(seg)
                ip1.update_splines()
                #self.network_cutter.precompute_cut(seg)
                #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)

        #Add a New Point at end free chains
        elif (self.net_ui_context.hovered_near[0] == None) and (self.net_ui_context.snap_element == None):  #adding in a new point at end, may need to specify closest unlinked vs append and do some previs

            closest_endpoint = self.closest_spline_endpoint(self.net_ui_context.mx * loc)
            self.net_ui_context.selected = self.spline_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)
            print('create new point')

            if closest_endpoint and connect:
                self.spline_net.connect_points(self.net_ui_context.selected, closest_endpoint)
                self.net_ui_context.selected.update_splines()
                closest_endpoint.update_splines()

        elif self.net_ui_context.hovered_near[0] == 'POINT CONNECT' and self.net_ui_context.snap_element != None:  #adding in a new point at end, may need to specify closest unlinked vs append and do some previs
            print("Here 2")
            closest_endpoints = self.closest_spline_endpoints(self.net_ui_context.snap_element.world_loc, 2)
            # bail if we did not find at least two nearby endpoints
            if len(closest_endpoints) < 2: return
            seg = SplineSegment(closest_endpoints[0], closest_endpoints[1])
            self.spline_net.segments.append(seg)
            closest_endpoints[0].update_splines()
            closest_endpoints[1].update_splines()

            #self.network_cutter.precompute_cut(seg)
            #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)

        elif self.net_ui_context.hovered_near[0] == 'POINT':
            self.net_ui_context.selected = self.net_ui_context.hovered_near[1]

        elif self.net_ui_context.hovered_near[0] == 'EDGE':  #TODO, actually make InputSegment as hovered_near
            point = self.spline_net.create_point(self.net_ui_context.mx * loc, loc, view_vector, face_ind)
            old_seg = self.net_ui_context.hovered_near[1]
            self.spline_net.insert_point(point, old_seg)
            old_seg.clear_input_net_references(self.input_net)
            self.net_ui_context.selected = point

            point.update_splines()
            for node in old_seg.points:
                node.update_splines()


        self.spline_net.push_to_input_net(self.net_ui_context, self.input_net, all_segs = True)
        self.network_cutter.update_segments_async()

    def inspect_things(self):
        '''
        container for random stuff to help debug
        '''
        print(self.net_ui_context.selected)

        if isinstance(self.net_ui_context.selected, CurveNode):
            cn = self.net_ui_context.selected
            print(cn.link_segments)
            print(cn.bmface)

    # TODO: Clean this up
    def click_delete_point(self, mode = 'mouse', disconnect=False):
        '''
        removes point from the trim line
        '''
        if mode == 'mouse':
            if self.net_ui_context.hovered_near[0] != 'POINT': return

            self.input_net.remove_point(self.net_ui_context.hovered_near[1], disconnect)
            self.network_cutter.update_segments()

            if self.input_net.is_empty or self.net_ui_context.selected == self.net_ui_context.hovered_near[1]:
                self.net_ui_context.selected = None

        else: #hard delete with x key
            if not self.net_ui_context.selected: return
            self.input_net.remove(self.net_ui_context.selected, disconnect= True)

    def click_delete_spline_point(self, mode = 'mouse', disconnect=False):
        '''
        removes point from the trim line
        '''
        if mode == 'mouse':
            if self.net_ui_context.hovered_near[0] != 'POINT': return
            curve_point = self.net_ui_context.hovered_near[1]  #CurveNode

            #Clear the CurveNode to InputNetwork mappings and delete corresponding
            #elements
            for seg in curve_point.link_segments:
                seg.clear_input_net_references(self.input_net)
            if curve_point.input_point in self.input_net.points:
                self.input_net.remove_point(curve_point.input_point, disconnect)
            #Remove CurveNode from SplineNetwork
            connected_points = self.spline_net.remove_point(curve_point, disconnect)  #returns the new points on either side, connected or not
            print('there are %i connected points')
            for node in connected_points:  #need all point handles updated first, becuae of how auto handles use neighboring points
                node.calc_handles()
            for node in connected_points:  #this actually doubly updaes the middle segment, but it's just bez interp, no cutting
                node.update_splines()

            self.spline_net.push_to_input_net(self.net_ui_context, self.input_net, all_segs = False)
            self.network_cutter.update_segments_async()
            self.network_cutter.validate_cdata()
            if self.spline_net.is_empty or self.net_ui_context.selected == self.net_ui_context.hovered_near[1]:
                self.net_ui_context.selected = None

        #Let's avoid hotkeys for now
        # else: #hard delete with x key
        #     if not self.net_ui_context.selected: return
        #     self.spline_net.remove(self.net_ui_context.selected, disconnect= True)

    def click_add_seed(self):

        if self.net_ui_context.hovered_mesh == {}: return

        face_ind = self.net_ui_context.hovered_mesh['face index']
        world_loc = self.net_ui_context.hovered_mesh['world loc']
        local_loc = self.net_ui_context.hovered_mesh['local loc']
        self.network_cutter.add_seed(face_ind, world_loc, local_loc)

    def click_enter_paint(self, delete = False):

        if self.net_ui_context.hovered_mesh == {}: return

        face_ind = self.net_ui_context.hovered_mesh['face index']
        world_loc = self.net_ui_context.hovered_mesh['world loc']
        local_loc = self.net_ui_context.hovered_mesh['local loc']

        f= self.net_ui_context.bme.faces[face_ind]

        self.network_cutter.active_patch = None  #TODO, this should already be none..should we enforce it?
        for patch in self.network_cutter.face_patches:
            if f in patch.patch_faces:  #just change the color but don't add a duplicate
                self.network_cutter.active_patch = patch
                self.brush.brush_color = patch.color
                print('found the active patch')

        if delete:
            self.brush.brush_color = Color((1,1,1))
        if self.network_cutter.active_patch == None and not delete:
            self.network_cutter.add_patch_start_paint(face_ind, world_loc, local_loc)

    def paint_confirm_greedy(self):
        '''
        destroy all Iput elements touched by brush
        add brush accum geometry to active patch
        remove brush accumg geometry from other patches
        '''


        print('paint confirm')

        self.network_cutter.validate_cdata()

        #First, remove geom accum from other patches
        remove_patches = []
        for patch in self.network_cutter.face_patches:
            if patch == self.network_cutter.active_patch:continue

            if not patch.patch_faces.isdisjoint(self.brush.geom_accum):
                patch.paint_modified = True
            patch.patch_faces.difference_update(self.brush.geom_accum)
            if len(patch.patch_faces) == 0:
                remove_patches += [patch]
            patch.validate_seed()

        for patch in remove_patches:
            self.network_cutter.face_patches.remove(patch)

        #Destroy all Discrete Network Elements touched by brush
        remove_points = []
        for ip in self.input_net.points:
            if ip.bmface in self.brush.geom_accum:
                remove_points += [ip]

        print('removing %i input points' % len(remove_points))
        for ip in remove_points:
            self.input_net.remove_point(ip, disconnect = True)

        remove_segs = []
        for seg in self.input_net.segments:
            if seg not in self.network_cutter.cut_data: continue #uh oh
            if not self.brush.geom_accum.isdisjoint(self.network_cutter.cut_data[seg]['face_set']):
                remove_segs += [seg]

        for seg in remove_segs:
            self.input_net.remove_segment(seg)

        print('removing %i input segments' % len(remove_segs))

        #Destroy all Spline Network Elements touched by brush
        remove_nodes = []
        for node in self.spline_net.points:
            if node.bmface in self.brush.geom_accum:
                #self.spline_net.remove_point(node, disconnect = True)
                remove_nodes += [node]

        for node in remove_nodes:
            #the seg is about to get deleted because it's node is gone
            #so we will loose the opportuity to clear out the children
            #segments
            for seg in node.link_segments:
                seg.clear_input_net_references(self.input_net)
            #actually delete the node
            self.spline_net.remove_point(node, disconnect = True)
            node.clear_input_net_references(self.input_net)  #Should  not be any

        remove_splines = set()
        for spline in self.spline_net.segments:
            for ip_seg in spline.input_segments:
                if ip_seg not in self.input_net.segments:
                    #remove the associated SPLINE segment  #TODO get smarter later
                    remove_splines.add(spline)

        for spline in remove_splines:
            self.spline_net.remove_segment(spline)
            spline.clear_input_net_references(self.input_net) #if the spline parent is gone, we take all children away from the border too....#TRUMP?

        #loose_nodes = []
        #for node in self.spline_net.points:
        #    if len(node.link_segments) == 0:
        #        loose_nodes += [node]

        #print('deleting %i loose nodes' % len(loose_nodes))
        #for node in loose_nodes:
        #    self.spline_net.remove_point(node)

        self.network_cutter.active_patch.patch_faces |= self.brush.geom_accum
        self.network_cutter.active_patch.paint_modified = True


        #TODO, remove the destroyed elements from the patch references

        self.network_cutter.active_patch.color_patch()
        self.network_cutter.validate_cdata()


        return

    def paint_confirm_mergey(self):
        '''
        destroy all Iput elements touched by brush
        add brush accum geometry to active patch
        merge any patches touched into active patch
        this prevents adjacnet patches until we have the cutting mechancis
        to support it
        '''


        print('paint confirm')

        if len(self.brush.geom_accum) == 0: return  #that was easy

        self.network_cutter.validate_cdata()

        AP = self.network_cutter.active_patch

        #First, identify touched patches
        merge_patches = []

        for patch in self.network_cutter.face_patches:
            if patch == AP: continue
            if not patch.patch_faces.isdisjoint(self.brush.geom_accum):
                merge_patches += [patch]

        #merge them all together
        for patch in merge_patches:
            AP.patch_faces.update(patch.patch_faces)
            AP.input_net_segments += patch.input_net_segments
            AP.ip_points += patch.ip_points
            AP.spline_net_segments += patch.spline_net_segments
            AP.curve_nodes += patch.curve_nodes
            self.network_cutter.face_patches.remove(patch)

        #Destroy all Discrete Network Elements touched by brush
        remove_points = []
        for ip in self.input_net.points:
            if ip.bmface in self.brush.geom_accum:
                remove_points += [ip]

        print('removing %i input points' % len(remove_points))
        for ip in remove_points:
            self.input_net.remove_point(ip, disconnect = True)

        remove_segs = []
        for seg in self.input_net.segments:
            if seg not in self.network_cutter.cut_data: continue #uh oh
            if not self.brush.geom_accum.isdisjoint(self.network_cutter.cut_data[seg]['face_set']):
                remove_segs += [seg]

        for seg in remove_segs:
            self.input_net.remove_segment(seg)

        print('removing %i input segments' % len(remove_segs))

        #Destroy all Spline Network Elements touched by brush
        remove_nodes = []
        for node in self.spline_net.points:
            if node.bmface in self.brush.geom_accum:
                #self.spline_net.remove_point(node, disconnect = True)
                remove_nodes += [node]

        for node in remove_nodes:
            #the seg is about to get deleted because it's node is gone
            #so we will loose the opportuity to clear out the children
            #segments
            for seg in node.link_segments:
                seg.clear_input_net_references(self.input_net)
            #actually delete the node
            self.spline_net.remove_point(node, disconnect = True)
            node.clear_input_net_references(self.input_net)  #Should  not be any

        remove_splines = set()
        for spline in self.spline_net.segments:
            for ip_seg in spline.input_segments:
                if ip_seg not in self.input_net.segments:
                    #remove the associated SPLINE segment  #TODO get smarter later
                    remove_splines.add(spline)

        for spline in remove_splines:
            self.spline_net.remove_segment(spline)
            spline.clear_input_net_references(self.input_net) #if the spline parent is gone, we take all children away from the border too....#TRUMP?

        #join the brush geom!
        self.network_cutter.active_patch.patch_faces |= self.brush.geom_accum
        self.network_cutter.active_patch.paint_modified = True

        #ensure no 0 face paches
        remove_patches = []
        for patch in self.network_cutter.face_patches:
            if len(patch.patch_faces) == 0:
                remove_patches += [patch]

        for patch in remove_patches:
            self.network_cutter.face_patches.remove(patch)

        #TODO, remove the destroyed elements from the patch references
        self.network_cutter.active_patch.color_patch()
        self.network_cutter.validate_cdata()  #we have just removed a bunch of input network elements

        return

    def paint_confirm_subtract(self):
        '''
        destroy all Input elements touched by brush
        remove brush accum geometry from all patches
        '''


        print('paint confirm subtract')

        if len(self.brush.geom_accum) == 0: return  #that was easy

        self.network_cutter.validate_cdata()

        #First, identify touched patches
        for patch in self.network_cutter.face_patches:
            if not patch.patch_faces.isdisjoint(self.brush.geom_accum):
                print('removing brush geom from patch')
                patch.patch_faces.difference_update(self.brush.geom_accum)
                if patch.validate_seed():
                    patch.world_loc = self.net_ui_context.mx * patch.local_loc
                patch.paint_modified = True
                patch.un_color_patch()
                patch.color_patch()

        #ensure no 0 face paches
        remove_patches = []
        for patch in self.network_cutter.face_patches:
            if len(patch.patch_faces) == 0:
                remove_patches += [patch]

        for patch in remove_patches:
            self.network_cutter.face_patches.remove(patch)

        #Destroy all Discrete Network Elements touched by brush
        remove_points = []
        for ip in self.input_net.points:
            if ip.bmface in self.brush.geom_accum:
                remove_points += [ip]

        for ip in remove_points:
            self.input_net.remove_point(ip, disconnect = True)

        remove_segs = []
        for seg in self.input_net.segments:
            if seg not in self.network_cutter.cut_data: continue #uh oh
            if not self.brush.geom_accum.isdisjoint(self.network_cutter.cut_data[seg]['face_set']):
                remove_segs += [seg]

        for seg in remove_segs:
            self.input_net.remove_segment(seg)

        #Destroy all Spline Network Elements touched by brush
        remove_nodes = []
        for node in self.spline_net.points:
            if node.bmface in self.brush.geom_accum:
                #self.spline_net.remove_point(node, disconnect = True)
                remove_nodes += [node]

        for node in remove_nodes:
            #the seg is about to get deleted because it's node is gone
            #so we will loose the opportuity to clear out the children
            #segments
            for seg in node.link_segments:
                seg.clear_input_net_references(self.input_net)
            #actually delete the node
            self.spline_net.remove_point(node, disconnect = True)
            node.clear_input_net_references(self.input_net)  #Should  not be any

        remove_splines = set()
        for spline in self.spline_net.segments:
            for ip_seg in spline.input_segments:
                if ip_seg not in self.input_net.segments:
                    #remove the associated SPLINE segment  #TODO get smarter later
                    remove_splines.add(spline)

        for spline in remove_splines:
            self.spline_net.remove_segment(spline)
            spline.clear_input_net_references(self.input_net) #if the spline parent is gone, we take all children away from the border too....#TRUMP?


        self.network_cutter.validate_cdata()  #we have just removed a bunch of input network elements

        return

    def paint_exit(self):
        print('paint exit')

        #create new splines around newly created patches
        self.network_cutter.create_spline_network_from_face_patches(self.spline_net)

        #fit splines to modified boundaries of existing patches
        self.network_cutter.update_painted_face_patches_splines(self.spline_net)

        #now push all the splines back to input net and preview the cuts
        self.spline_net.push_to_input_net(self.net_ui_context, self.input_net)
        self.network_cutter.update_segments_async()

        #Do this for now
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)

    # TODO: Make this a NetworkUIContext function

    def delete_active_patch(self):


        if self.network_cutter.active_patch == None: return
        if self._state != 'segmentation': return
        #for now, use an active patch input style
        #if self.net_ui_context.hovered_mesh == {}: return
        #face_ind = self.net_ui_context.hovered_mesh['face index']
        #world_loc = self.net_ui_context.hovered_mesh['world loc']
        #local_loc = self.net_ui_context.hovered_mesh['local loc']
        #patch = self.network_cutter.find_patch_post_cut(face_ind, world_loc, local_loc)

        #verts = set()
        #edges = set()
        #for f in patch.faces:
            #verts.update(f.verts)
            #edges.update(ed.verts)

        patch = self.network_cutter.active_patch
        del_vs = [v for v in self.net_ui_context.bme.verts if all([f in patch.patch_faces for f in v.link_faces])]
        del_eds = [ed for ed in self.net_ui_context.bme.edges if all([f in patch.patch_faces for f in ed.link_faces])]

        bme = self.net_ui_context.bme

        for f in patch.patch_faces:
            bme.faces.remove(f)

        for ed in del_eds:
            bme.edges.remove(ed)

        for v in del_vs:
            bme.verts.remove(v)

        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()

        self.network_cutter.active_patch = None
        self.network_cutter.face_patches.remove(patch)
        bme.to_mesh(self.net_ui_context.ob.data)

        #update BVH?  hmmmm....

    def active_patch_to_vgroup(self):


        if self.network_cutter.active_patch == None: return
        if self._state != 'segmentation': return
        #for now, use an active patch input style
        #if self.net_ui_context.hovered_mesh == {}: return
        #face_ind = self.net_ui_context.hovered_mesh['face index']
        #world_loc = self.net_ui_context.hovered_mesh['world loc']
        #local_loc = self.net_ui_context.hovered_mesh['local loc']
        #patch = self.network_cutter.find_patch_post_cut(face_ind, world_loc, local_loc)

        #verts = set()
        #edges = set()
        #for f in patch.faces:
            #verts.update(f.verts)
            #edges.update(ed.verts)

        patch = self.network_cutter.active_patch
        bme = self.net_ui_context.bme

        group_vs = [v for v in bme.verts if all([f in patch.patch_faces for f in v.link_faces])]

        ob = self.net_ui_context.ob
        vg = ob.vertex_groups.new('segmentation')

        vg.add([v.index for v in group_vs], 1, type = 'REPLACE')
        self.network_cutter.active_patch = None
        self.network_cutter.face_patches.remove(patch)
        bme.to_mesh(self.net_ui_context.ob.data)

    def split_active_patch(self):


        if self.network_cutter.active_patch == None: return
        #for now, use an active patch input style
        #if self.net_ui_context.hovered_mesh == {}: return
        #face_ind = self.net_ui_context.hovered_mesh['face index']
        #world_loc = self.net_ui_context.hovered_mesh['world loc']
        #local_loc = self.net_ui_context.hovered_mesh['local loc']
        #patch = self.network_cutter.find_patch_post_cut(face_ind, world_loc, local_loc)

        #verts = set()
        #edges = set()
        #for f in patch.faces:
            #verts.update(f.verts)
            #edges.update(ed.verts)

        patch = self.newtork_cutter.active_patch

        patch.find_boundary_edges()  #this should probbaly happen at regino growing time anyway

        bme = self.net_ui_context.bme
        eds = patch.find_all_boundary_edges()
        bmesh.ops.split_edges(bme, eges = list(eds))

        self.newtork_cutter.active_patch = None
        self.network_cutter.face_patches.remove(patch)
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)


    def separate_active_patch(self):


        if self.network_cutter.active_patch == None: return
        #for now, use an active patch input style
        #if self.net_ui_context.hovered_mesh == {}: return
        #face_ind = self.net_ui_context.hovered_mesh['face index']
        #world_loc = self.net_ui_context.hovered_mesh['world loc']
        #local_loc = self.net_ui_context.hovered_mesh['local loc']
        #patch = self.network_cutter.find_patch_post_cut(face_ind, world_loc, local_loc)

        #verts = set()
        #edges = set()
        #for f in patch.faces:
            #verts.update(f.verts)
            #edges.update(ed.verts)

        patch = self.network_cutter.active_patch

        new_bme = new_bmesh_from_bmelements(patch.patch_faces)
        name = self.net_ui_context.ob.name + "_patch"
        new_me = bpy.data.meshes.new(name)
        new_ob = bpy.data.objects.new(name, new_me)
        new_ob.matrix_world = self.net_ui_context.mx
        new_bme.to_mesh(new_me)
        new_bme.free()
        bpy.context.scene.objects.link(new_ob)

        bme = self.net_ui_context.bme

        del_vs = [v for v in bme.verts if all([f in patch.patch_faces for f in v.link_faces])]
        del_eds = [ed for ed in bme.edges if all([f in patch.patch_faces for f in ed.link_faces])]
        bme = self.net_ui_context.bme
        for f in patch.patch_faces:
            bme.faces.remove(f)

        for ed in del_eds:
            bme.edges.remove(ed)

        for v in del_vs:
            bme.verts.remove(v)

        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()

        self.network_cutter.active_patch = None
        self.network_cutter.face_patches.remove(patch)
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)

    def duplicate_active_patch(self):

        if self.network_cutter.active_patch == None: return
        patch = self.network_cutter.active_patch
        patch.un_color_patch()

        new_bme = new_bmesh_from_bmelements(patch.patch_faces)
        name = self.net_ui_context.ob.name + "_patch"
        new_me = bpy.data.meshes.new(name)
        new_ob = bpy.data.objects.new(name, new_me)
        new_ob.matrix_world = self.net_ui_context.mx
        new_bme.to_mesh(new_me)
        new_bme.free()
        bpy.context.scene.objects.link(new_ob)

        self.network_cutter.active_patch = None
        self.network_cutter.face_patches.remove(patch)
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)

    def closest_endpoint(self, pt3d):
        def dist3d(point):
            return (point.world_loc - pt3d).length

        endpoints = [ip for ip in self.input_net.points if ip.is_endpoint]
        if len(endpoints) == 0: return None

        return min(endpoints, key = dist3d)

    # TODO: Make this a NetworkUIContext function
    def closest_spline_endpoint(self, pt3d):
        def dist3d(point):
            return (point.world_loc - pt3d).length

        endpoints = [ip for ip in self.spline_net.points if ip.is_endpoint]
        if len(endpoints) == 0: return None

        return min(endpoints, key = dist3d)

    # TODO: Also NetworkUIContext function
    def closest_endpoints(self, pt3d, n_points):
        #in our application, at most there will be 100 endpoints?
        #no need for accel structure here
        n_points = max(0, n_points)

        endpoints = [ip for ip in self.input_net.points if ip.is_endpoint] #TODO self.endpoints?

        if len(endpoints) == 0: return None
        n_points = min(n_points, len(endpoints))

        def dist3d(point):
            return (point.world_loc - pt3d).length

        endpoints.sort(key = dist3d)

        return endpoints[0:n_points+1]

    def closest_spline_endpoints(self, pt3d, n_points):
        #in our application, at most there will be 100 endpoints?
        #no need for accel structure here
        n_points = max(0, n_points)

        endpoints = [ip for ip in self.spline_net.points if ip.is_endpoint] #TODO self.endpoints?
        if len(endpoints) == 0: return []
        n_points = min(n_points, len(endpoints))

        def dist3d(point): return (point.world_loc - pt3d).length

        endpoints.sort(key = dist3d)
        return endpoints[0:n_points+1]

    # TODO: NetworkUIContext??
    def closest_point_3d_linear(self, seg, pt3d):
        '''
        will return the closest point on a straigh line segment
        drawn between the two input points

        If the 3D point is not within the infinite cylinder defined
        by 2 infinite disks placed at each input point and orthogonal
        to the vector between them, will return None



        A_pt3d              B_pt3d
          .                    .
          |                    |
          |                    |
          |                    |
          |       ip0._________x_________.ip1


         A_pt3d will return None, None.  B_pt3d will return 3d location at orthogonal intersection and the distance

         else, will return a tupple (location of intersection, %along line from ip0 to ip1

         happens in the world coordinates

        '''

        if isinstance(seg, SplineSegment):
            intersect3d = intersect_point_line(pt3d, seg.n0.world_loc, seg.n1.world_loc)
        else:
            intersect3d = intersect_point_line(pt3d, seg.ip0.world_loc, seg.ip1.world_loc)

        if intersect3d == None: return (None, None)

        dist3d = (intersect3d[0] - pt3d).length

        if  (intersect3d[1] < 1) and (intersect3d[1] > 0):
            return (intersect3d[0], dist3d)

        return (None, None)

    def enter_poly_mode(self):
        if self._state == 'sketch wait': return

        if self._state == 'paint wait':
            del self.brush
            self.brush = None
            self.paint_exit()
            self.fsm_change('sketch wait')

        elif self._state == 'seed':
            self.fsm_change('sketch wait')


    def enter_paint_mode(self):
        self.fsm_change('paint entering')

    def find_network_cycles_button(self):
        self.input_net.find_network_cycles()

    def knife_stepwise_prepare_button(self):
        self.network_cutter.knife_gometry_stepper_prepare()

    def knife_step_button(self):
        self.network_cutter.knife_geometry_step()
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)

    def compute_cut_button(self):
        self.network_cutter.knife_geometry4()

        self.network_cutter.find_perimeter_edges()
        for patch in self.network_cutter.face_patches:
            patch.grow_seed(self.input_net.bme, self.network_cutter.boundary_edges)
            patch.color_patch()
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)

        self._sate_next = 'segmentation'

    def enter_seed_select_button(self):
        self.fsm_change('seed')
        self.cursor_modal_set('EYEDROPPER')
        return


    def hover(self, select_radius = 12, snap_radius = 24): #TDOD, these radii are pixels? Shoudl they be settings?
        '''
        finds points/edges/etc that are near ,mouse
         * hovering happens in mixed 3d and screen space, 20 pixels thresh for points, 30 for edges 40 for non_man
        '''

        # TODO: update self.hover to use Accel2D?
        mouse = self.actions.mouse
        context = self.context

        mx, imx = get_matrices(self.net_ui_context.ob)
        loc3d_reg2D = view3d_utils.location_3d_to_region_2d
        # ray tracing
        view_vector, ray_origin, ray_target = get_view_ray_data(context, mouse)
        #loc, no, face_ind = ray_cast(self.net_ui_context.ob, imx, ray_origin, ray_target, None)
        loc, no, face_ind = ray_cast_bvh(self.net_ui_context.bvh, imx, ray_origin, ray_target, None)
        self.net_ui_context.snap_element = None
        self.net_ui_context.connect_element = None

        if self.input_net.is_empty:
            self.net_ui_context.hovered_near = [None, -1]
            self.net_ui_context.nearest_non_man_loc()
            return

        if face_ind == -1 or face_ind == None:
            self.net_ui_context.closest_ep = None
            return
        else: self.net_ui_context.closest_ep = self.closest_endpoint(mx * loc)

        #find length between vertex and mouse
        def dist(v):
            if v == None:
                print('v off screen')
                return 100000000
            diff = v - Vector(mouse)
            return diff.length

        #find length between 2 3d points
        def dist3d(v3):
            if v3 == None:
                return 100000000
            delt = v3 - self.net_ui_context.ob.matrix_world * loc
            return delt.length

        #closest_3d_loc = min(self.input_net.world_locs, key = dist3d)
        closest_ip = min(self.input_net.points, key = lambda x: dist3d(x.world_loc))
        pixel_dist = dist(loc3d_reg2D(context.region, context.space_data.region_3d, closest_ip.world_loc))

        if pixel_dist  < select_radius:
            #print('point is hovered_near')
            #print(pixel_dist)
            self.net_ui_context.hovered_near = ['POINT', closest_ip]  #TODO, probably just store the actual InputPoint as the 2nd value?
            self.net_ui_context.snap_element = None
            return

        elif pixel_dist >= select_radius and pixel_dist < snap_radius:
            #print('point is within snap radius')
            #print(pixel_dist)
            if closest_ip.is_endpoint:
                self.net_ui_context.snap_element = closest_ip

                #print('This is the close loop scenario')
                closest_endpoints = self.closest_endpoints(self.net_ui_context.snap_element.world_loc, 2)

                #print('these are the 2 closest endpoints, one should be snap element itself')
                #print(closest_endpoints)
                if closest_endpoints == None:
                    #we are not quite hovered_near but in snap territory
                    return

                if len(closest_endpoints) < 2:
                    #print('len of closest endpoints not 2')
                    return

                self.net_ui_context.connect_element = closest_endpoints[1]

            return


        if self.input_net.num_points == 1:  #why did we do this? Oh because there are no segments.
            self.net_ui_context.hovered_near = [None, -1]
            self.net_ui_context.snap_element = None
            return

        ##Check distance between ray_cast point, and segments
        distance_map = {}
        for seg in self.input_net.segments:  #TODO, may need to decide some better naming and better heirarchy

            close_loc, close_d = self.closest_point_3d_linear(seg, self.net_ui_context.ob.matrix_world * loc)
            if close_loc  == None:
                distance_map[seg] = 10000000
                continue

            distance_map[seg] = close_d

        if self.input_net.segments:
            closest_seg = min(self.input_net.segments, key = lambda x: distance_map[x])

            a = loc3d_reg2D(context.region, context.space_data.region_3d, closest_seg.ip0.world_loc)
            b = loc3d_reg2D(context.region, context.space_data.region_3d, closest_seg.ip1.world_loc)

            if a and b:  #if points are not on the screen, a or b will be None
                intersect = intersect_point_line(Vector(mouse).to_3d(), a.to_3d(),b.to_3d())
                dist = (intersect[0].to_2d() - Vector(mouse)).length_squared
                bound = intersect[1]
                if (dist < select_radius**2) and (bound < 1) and (bound > 0):
                    self.net_ui_context.hovered_near = ['EDGE', closest_seg]
                    return

        ## Multiple points, but not hovering over edge or point.
        self.net_ui_context.hovered_near = [None, -1]

        self.net_ui_context.nearest_non_man_loc()


    def hover_spline(self, select_radius=12, snap_radius=24): #TODO, these radii are pixels? Should they be settings?
        '''
        finds points/edges/etc that are near ,mouse
         * hovering happens in mixed 3d and screen space, 20 pixels thresh for points, 30 for edges 40 for non_man
        '''

        self.net_ui_context.snap_element    = None
        self.net_ui_context.connect_element = None
        self.net_ui_context.hovered_near    = [None, -1]
        self.net_ui_context.hovered_dist2D  = float('inf')
        self.net_ui_context.closest_ep      = None

        # TODO: update self.hover to use Accel2D?
        mouse = self.actions.mouse
        mouse_vec = Vector(mouse)
        context = self.context
        mx, imx = get_matrices(self.net_ui_context.ob)
        loc3d_reg2D = view3d_utils.location_3d_to_region_2d

        if self.spline_net.is_empty:
            # no points to be near
            self.net_ui_context.nearest_non_man_loc()
            return

        # ray tracing
        view_vector, ray_origin, ray_target = get_view_ray_data(context, mouse)
        #loc, no, face_ind = ray_cast(self.net_ui_context.ob, imx, ray_origin, ray_target, None)
        loc,_,face_ind = ray_cast_bvh(self.net_ui_context.bvh, imx, ray_origin, ray_target, None)

        # bail if we did not hit the source
        if face_ind == -1 or face_ind == None: return

        loc = mx * loc      # transform loc to world
        self.net_ui_context.closest_ep = self.closest_spline_endpoint(loc)

        # find length between vertex and mouse
        def dist(v): return (v - mouse_vec).length if v else float('inf')
        # find length between 2 3d points
        def dist3d(v3): return (v3 - loc).length if v3 else float('inf')

        #closest_3d_loc = min(self.spline_net.world_locs, key = dist3d)
        closest_ip = min(self.spline_net.points, key = lambda x: dist3d(x.world_loc))
        pixel_dist = dist(loc3d_reg2D(context.region, context.space_data.region_3d, closest_ip.world_loc))

        if pixel_dist < select_radius:
            # the mouse is hovering over a point
            self.net_ui_context.hovered_near = ['POINT', closest_ip]  #TODO, probably just store the actual InputPoint as the 2nd value?
            self.net_ui_context.hovered_dist2D = pixel_dist
            return

        if select_radius <= pixel_dist < snap_radius:
            # the mouse is near a point (just outside of hovering)
            if closest_ip.is_endpoint:
                # only care about endpoints at this moment
                self.net_ui_context.snap_element = closest_ip
                self.net_ui_context.hovered_dist2D = pixel_dist
                #print('This is the close loop scenario')
                closest_endpoints = self.closest_spline_endpoints(self.net_ui_context.snap_element.world_loc, 2)
                # bail if we did not find at least two nearby endpoints
                if len(closest_endpoints) < 2: return
                self.net_ui_context.hovered_near = ['POINT CONNECT', closest_ip]
                self.net_ui_context.connect_element = closest_endpoints[1]
            return

        # bail if there are only one num_points (no segments)
        if self.spline_net.num_points == 1: return

        ##Check distance between ray_cast point, and segments
        distance_map = {}
        #notice InputNet not SplineNet!  We could also check against BMFaceMap for the cut data
        for seg in self.input_net.segments:  #TODO, may need to decide some better naming and better hierarchy
            close_loc, close_d = self.closest_point_3d_linear(seg, loc)
            distance_map[seg] = close_d if close_loc else float('inf')

        if self.input_net.segments:
            closest_seg = min(self.input_net.segments, key = lambda x: distance_map[x])

            a = loc3d_reg2D(context.region, context.space_data.region_3d, closest_seg.ip0.world_loc)
            b = loc3d_reg2D(context.region, context.space_data.region_3d, closest_seg.ip1.world_loc)

            if a and b:  #if points are not on the screen, a or b will be None
                intersect = intersect_point_line(mouse_vec.to_3d(), a.to_3d(),b.to_3d())
                dist = (intersect[0].to_2d() - mouse_vec).length_squared
                bound = intersect[1]
                if (dist < select_radius**2) and (bound < 1) and (bound > 0):
                    spline_seg = closest_seg.parent_spline
                    self.net_ui_context.hovered_near = ['EDGE', spline_seg]
                    return
        ## Multiple points, but not hovering over edge or point.

        self.net_ui_context.nearest_non_man_loc()


    def hover_patches(self): #TODO, these radii are pixels? Should they be settings?
        '''
        finds the patch associated under the mouse
        '''


        # TODO: update self.hover to use Accel2D?
        mouse = self.actions.mouse
        mouse_vec = Vector(mouse)
        context = self.context
        mx, imx = get_matrices(self.net_ui_context.ob)
        loc3d_reg2D = view3d_utils.location_3d_to_region_2d

        if len(self.network_cutter.face_patches) == 0:
            self.net_ui_context.hovered_near = [None, None]
            return

        # ray tracing
        view_vector, ray_origin, ray_target = get_view_ray_data(context, mouse)
        #loc, no, face_ind = ray_cast(self.net_ui_context.ob, imx, ray_origin, ray_target, None)
        loc,_,face_ind = ray_cast_bvh(self.net_ui_context.bvh, imx, ray_origin, ray_target, None)

        # bail if we did not hit the source
        if face_ind == -1 or face_ind == None:
            self.net_ui_context.hovered_near = [None, None]
            return

        #find if we hit a patch
        patch = self.network_cutter.find_patch_post_cut(face_ind, mx * loc, loc)

        if patch != None:
            self.net_ui_context.hovered_near = ['PATCH', patch]
        else:
            self.net_ui_context.hovered_near = [None, None]


    def end_commit(self):
        print('end commit')
        if self.net_ui_context.geometry_mode == 'DESTRUCTIVE':
            bpy.data.meshes.remove(self.net_ui_context.backup_data)

        else:
            del_data = self.net_ui_context.ob.data
            self.net_ui_context.ob.data = self.net_ui_context.backup_data
            bpy.data.meshes.remove(del_data)

        self.net_ui_context.bme.free() #and other cleanup?

    def end_cancel(self):
        print('end cancel')
        del_data = self.net_ui_context.ob.data  #remember we swapped the data at the init
        self.net_ui_context.ob.data = self.net_ui_context.backup_data
        bpy.data.meshes.remove(del_data)

        self.net_ui_context.bme.free()
