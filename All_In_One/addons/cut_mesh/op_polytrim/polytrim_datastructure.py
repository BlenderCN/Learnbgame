'''
Created on Oct 8, 2015

@author: Patrick,  

#TODO Micah Needs to add email and stuff in here
License, copyright all that
This code has an ineresting peidgree
Inspired by contours Patrick Moore for CGCookie
Improved by using some PolyStrips concepts Jon Denning @CGCookie and Taylor University
refreshed again as part of summer practicum by Micah Stewart Summer 2018, Taylor University + Impulse Dental Technologies LLC
reworked again by Patrick Moore, Micah Stewart and Jon Denning Fall 2018 
'''
import time
import math
import random

import bpy
import bmesh
import bgl

from collections import defaultdict
from mathutils import Vector, Matrix, Color, kdtree
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line, intersect_line_plane
from bpy_extras import view3d_utils

from ..bmesh_fns import grow_selection_to_find_face, flood_selection_faces, edge_loops_from_bmedges_old, edge_loops_from_bmedges, flood_selection_by_verts, flood_selection_edge_loop, ensure_lookup
from ..bmesh_fns import face_region_boundary_loops, bmesh_loose_parts_faces
from ..cut_algorithms import cross_section_2seeds_ver1, path_between_2_points, path_between_2_points_clean, find_bmedges_crossing_plane
from ..geodesic import GeoPath, geodesic_walk, continue_geodesic_walk, gradient_descent
from .. import common_drawing
from ..common.rays import get_view_ray_data, ray_cast
from ..common.blender import bversion
from ..common.colors import get_random_color
from ..common.utils import get_matrices
from ..common.bezier import CubicBezier, CubicBezierSpline, CompositeSmoothCubicBezierSpline
from ..common.shaders import circleShader
from ..common.simplify import simplify_RDP, relax_vert_chain
from ..common.profiler import profiler

from concurrent.futures.thread import ThreadPoolExecutor

#helper function to split a face
def split_face_by_verts(bme, f, ed_enter, ed_exit, bmvert_chain):
    '''
    bme - BMesh
    f - f in bme to be split
    ed_enter - the BMEdge that bmvert_chain[0] corresponds to
    ed_exit - the BMEdge that bmvert_chain[-1] corresponds to
    bmvert_chain - list of BMVerts that define the path that f is split on. len() >= 2
    
    
    returns f1 and f2 the newly split faces
    '''

    if ed_enter not in f.edges:
        print('ed_enter not in f.edges')
        if not ed_enter.is_valid:
            print('this edge has been removed')
            
        return None, None
    
    if ed_exit not in f.edges:
        print('ed_exit not in f.edges')
        if not ed_exit.is_valid:
            print('this edge has been removed')
            
        return None, None
    
    if len(ed_enter.link_loops) < 1:
        print('we have no link loops; problem')
        
        print(f)
        print([f.edges[:]])
        
        print(ed_enter)
        print(ed_enter.link_faces[:])
        
        print('there are %i link loops' % len(ed_enter.link_loops))
        return None, None
    
    
    if ed_enter.link_loops[0].face == f:
        l_loop = ed_enter.link_loops[0]
    else:
        
        if len(ed_enter.link_loops) < 2:
            print('we not enough link loops; problem')
        
            print(f)
            print([f.edges[:]])
            
            print(ed_enter)
            print(ed_enter.link_faces[:])
            
            print('there are %i link loops' % len(ed_enter.link_loops))
            return None, None    
        l_loop = ed_enter.link_loops[1]
        
    if ed_enter == None:
        #Error....needs to be an edge
        print('NONE EDGE ENTER')
        return None, None
    if ed_exit == None:
        #Error...needs to be an edg 
        print('NONE EDGE EXIT')
        return None, None
     
    if ed_enter == ed_exit:
        print('ed enter and ed exit the same!')
        
        #determine direction/order of bmvert chain that makes sense
        #by testing distance of bmvert_chain[0].co to link_loop.vert.co
        
        d0 = (bmvert_chain[0].co - l_loop.vert.co).length
        d1 = (bmvert_chain[-1].co - l_loop.vert.co).length
        
        verts = []
        start_loop = l_loop
        l_loop = l_loop.link_loop_next
        iters = 0
        while l_loop != start_loop and iters < 100:
            verts += [l_loop.vert]
            l_loop = l_loop.link_loop_next
            iters += 1
        
        verts += [start_loop.vert]
            
        if iters >= 99:
            
            print('iteration problem')
            
            print(f, ed_enter, ed_exit)
            return None, None
        if d0 < d1:
            f1 = bme.faces.new(verts + bmvert_chain)
            f2 = bme.faces.new(bmvert_chain[::-1])
            
        else:
            f1 = bme.faces.new(verts + bmvert_chain[::-1])
            f2 = bme.faces.new(bmvert_chain)
        
        return f1, f2
    else:
        iters = 0
        verts = []  #the link_loop.vert will be behind the intersection so we don't need to include it
        while l_loop.edge != ed_exit and iters < 100:
            iters += 1
            verts += [l_loop.link_loop_next.vert]
            l_loop = l_loop.link_loop_next
        
        if iters >= 99:
            print('iteration problem')
            print(f, ed_enter, ed_exit)
            return None, None

        f1verts = verts + bmvert_chain[::-1]
        #keep going around
        verts = []
        iters = 0
        while l_loop.edge != ed_enter and iters < 100:
            verts += [l_loop.link_loop_next.vert]
            l_loop = l_loop.link_loop_next
            iters += 1
            
        if iters >= 99:
            print('iteration problem')
            print(f, ed_enter, ed_exit)
            return None, None
        
        
        f1 = bme.faces.new(f1verts)
        f2 = bme.faces.new(verts + bmvert_chain)
        return f1, f2
    

class BMFacePatch(object):
    '''
    Data Structure for managing patches on BMeshes meant to help
    in segmentation of surface patches
    '''
    def __init__(self, bmface, local_loc, world_loc, vcol_layer, color = (1.0, .7, 0)):
        self.seed_face = bmface
        self.local_loc = local_loc
        self.world_loc = world_loc
        
        self.patch_faces = set()  #will find these
        self.boundary_edges = set() #set of BMEdges will be calculated
        self.color = Color(color)
        self.color_layer = vcol_layer
        
        #mapping to DiscreteNetwork
        self.input_net_segments = []
        self.ip_points = []
        
        #mapping to SplineNetwork
        self.spline_net_segments = []
        self.curve_nodes = []
        
        #depricated
        self.perimeter_path = []
        self.bez_data = []
        
        self.paint_modified = False  #flag for when boundary needs to be updated when re-entering stroke modes
        
    def set_color(self, color): 
        self.color = Color(color)
           
    
    def validate_seed(self):
        if len(self.patch_faces) == 0: return False
        
        if self.seed_face not in self.patch_faces:
            #choose an arbitray element from set
            for s in self.patch_faces:
                break
            self.seed_face = s
            self.local_loc = s.calc_center_bounds()
            return True
            
            
    def grow_seed(self, bme, boundary_edges):
        #if we are re-growing our seed,
        if len(self.patch_faces)  != 0:
            self.un_color_patch()
        island = flood_selection_edge_loop(bme, boundary_edges, self.seed_face, max_iters = 10000)
        self.patch_faces = island
        
    def grow_seed_faces(self, bme, boundary_faces):
        if len(self.patch_faces)  != 0:
            self.un_color_patch()
        island = flood_selection_faces(bme, boundary_faces, self.seed_face)
        island -= boundary_faces  #because boundary_faces are between all segments
        self.patch_faces = island
    
        self.boundary_edges.clear()  #no longer valid
        
    def adjacent_faces(self):
        '''
        the set of the one ring neighbors of this patch
        used for adjacency testing
        TODO, cache and use for later, know when to update
        '''
        def face_neighbors_by_vert(bmface):
            neighbors = []
            for v in bmface.verts:
                neighbors += [f for f in v.link_faces if f != bmface]
        
            return neighbors
        
        expanded_faces = set()
        if len(self.boundary_edges) == 0:
            print('using faces method')
            for f in self.patch_faces:
                expanded_faces.update(face_neighbors_by_vert(f))
        else:
            print('using boundary edges method')
            for ed in self.boundary_edges:
                for v in ed.verts:
                    expanded_faces.update([f for f in v.link_faces])
                    
        expanded_faces.difference_update(self.patch_faces)
        
        return expanded_faces
            
            
    def color_patch(self, color_layer = None):
        
        if color_layer == None:
            color_layer = self.color_layer
            
        for f in self.patch_faces:
            for loop in f.loops:
                loop[color_layer] = self.color

    def un_color_patch(self, color_layer = None):
        color = Color((1,1,1))
        if color_layer == None:
            color_layer = self.color_layer
            
        for f in self.patch_faces:
            if not f.is_valid: continue
            for loop in f.loops:
                loop[color_layer] = color
                
    def find_boundary_edges(self, bme):
        #TODO refactor bmesh_fns to not use indices
        #for now, only biggest patch
        if len(self.patch_faces) == 0: return
        
        islands = bmesh_loose_parts_faces(bme, self.patch_faces)
        self.perimeter_path = []
        self.boundary_edges.clear()
        if len(islands) > 1:
            mainland = max(islands, key = len)
            geom = face_region_boundary_loops(bme, [f.idnex for f in mainland])
        
            for island in islands:
                if island == mainland: continue
                self.patch_faces.difference_update(island)
        else:
            geom = face_region_boundary_loops(bme, [f.index for f in self.patch_faces])
        
        #TODO, face patch could have interior lakes
        loop = geom['EDGES'][0]
        for ind in loop:
            self.boundary_edges.add(bme.edges[ind])
        
        loop = geom['VERTS'][0]
        for ind in loop:
            self.perimeter_path += [bme.verts[ind].co.copy()]
    
    def find_all_boundary_edges(self):
        '''
        this does not need loops, will find all MANIFOLD boundary edges
        
        '''
        if len(self.patch_faces) == 0: return set()
        
        all_edges = set()
        for f in self.patch_faces:
            all_edges.update([ed for ed in f.edges])
        
        print('there are %i edges in this patch' % len(all_edges))   
        keep_edges = set()
        for ed in all_edges:
            if len(ed.link_faces) != 2: continue #non manifold
            
            if len([f for f in ed.link_faces if f in self.patch_faces]) == 1:
                keep_edges.add(ed)
        
        return keep_edges    
            
        
#Input Net Topolocy Functons to help
def next_segment(ip, current_seg): #TODO Code golf this
    if len(ip.link_segments) != 2: return None  #TODO, the the segment to right
    return [seg for seg in ip.link_segments if seg != current_seg][0]

#TODO def next_segment_to_right(ip, current_segment):
    #if len(ip.link_sgements) > 2:  find the winding
    #if len(ip.link_segments == 2: normal
    #if len(ip.link_segments_ == 1:  return None            
class NetworkCutter(object):
    ''' Manages cuts in the InputNetwork '''

    def __init__(self, input_net, net_ui_context):
        #this is all the basic data that is needed
        self.input_net = input_net
        self.net_ui_context = net_ui_context

        #this is fancy "que" of things to be processed
        self.executor = ThreadPoolExecutor()  
        self.executor_tasks = {}
        
        
        self.new_bmverts = set()
        
        #TODO consider packaging this up into some structure
        self.cut_data = {}  #a dictionary of cut data
        self.ip_bmvert_map = {} #dictionary of new bm verts to InputPoints  in input_net 
        self.reprocessed_edge_map = {}
        self.completed_segments = set()
        
        self.original_indices_map = {}
        self.new_to_old_face_map = {}
        self.old_to_new_face_map = {}
        self.completed_input_points = set()
        
        #have to store all these beacuse we are about to alter the bme
        self.old_face_indices = {}
        for f in self.input_net.bme.faces:
            self.old_face_indices[f.index] = f
          
        
        #list of BMFacePatch 
        self.face_patches = []
        self.active_patch = None  #used when painting
            
        #this is used to create coars boudaries from the input segments
        self.boundary_faces = set()
        
        self.knife_complete = False
        self.boundary_edges = set()  #this is a list of the newly created cut edges (the seams)
        self.the_bad_segment = None
        self.seg_enter = None
        self.seg_exit = None
        self.active_ip = None
        self.ip_chain = []
        self.ip_set = set()
        
        #temporary stuff to draw
        self.simple_paths = []
    
    
    ###########################################
    ####### Pre Cut Commit Functions  #########
    ###########################################
        
    def update_segments(self):
        for seg in self.input_net.segments:
            if seg.needs_calculation and not seg.calculation_complete:
                self.precompute_cut(seg)
                
        return
    
    def update_segments_async(self):
        
        self.validate_cdata()
        
        for seg in self.input_net.segments:
            
            if seg.needs_calculation and not seg.calculation_complete:
                seg.needs_calculation = False #this will prevent it from submitting it again before it's done
                                
                #TODO check for existing task
                #TODO if still computing, cancel it
                #start a new task
                future = self.executor.submit(self.precompute_cut, (seg))
                
                self.executor_tasks[seg] = future  
        return
    
    def validate_cdata(self):
        old_cdata = []
        for seg, cdata in self.cut_data.items():
            if seg not in self.input_net.segments:
                old_cdata.append(seg)
        
        print('deleting %i old seg cut data' % len(old_cdata))
        for seg in old_cdata:
            self.cut_data.pop(seg, None)
                        
    def compute_cut_normal(self, seg):
        surf_no = self.net_ui_context.imx.to_3x3() * seg.ip0.view.lerp(seg.ip1.view, 0.5)  #must be a better way.
        e_vec = seg.ip1.local_loc - seg.ip0.local_loc
        #define
        cut_no = e_vec.cross(surf_no)
        
        return cut_no              
    def precompute_cut(self, seg):

        print('precomputing cut!')
        #TODO  shuld only take bmesh, input faces and locations.  Should not take BVH or matrix as inputs
        self.face_chain = []

        # * return either bad segment or other important data.
        f0 = self.net_ui_context.bme.faces[seg.ip0.face_index]  #<<--- Current BMFace #TODO use actual BMFace reference
        f1 = self.net_ui_context.bme.faces[seg.ip1.face_index] #<<--- Next BMFace #TODO use actual BMFace reference

        if f0 == f1:
            seg.path = [seg.ip0.world_loc, seg.ip1.world_loc]
            seg.bad_segment = False  #perhaps a dict self.bad_segments[seg] = True
            seg.needs_calculation = False
            seg.calculation_complete = True
            seg.cut_method = 'SAME_FACE'
            return

        ###########################
        ## Define the cutting plane for this segment#
        ############################

        
        if seg.ip1.view.dot(seg.ip0.view) < 0:
            surf_no = self.net_ui_context.imx.to_3x3() * seg.ip0.view.lerp(-1 * seg.ip1.view, 0.5)
        else:
            surf_no = self.net_ui_context.imx.to_3x3() * seg.ip0.view.lerp(seg.ip1.view, 0.5)  #must be a better way.
        
        
        e_vec = seg.ip1.local_loc - seg.ip0.local_loc  #edge vector
        #define
        cut_no = e_vec.cross(surf_no)
        #cut_pt = .5*self.cut_pts[ind_p1] + 0.5*self.cut_pts[ind]
        cut_pt = .5 * seg.ip0.local_loc + 0.5 * seg.ip1.local_loc

        #find the shared edge,, check for adjacent faces for this cut segment
        cross_ed = None
        for ed in f0.edges:
            if f1 in ed.link_faces:
                print('this face is adjacent to the next face')
                cut_data = {} 
                cut_data['face_crosses'] = []
                cut_data['face_set'] = set()
                cut_data['edge_crosses'] = [ed]
                cross = intersect_line_plane(ed.verts[0].co, ed.verts[1].co, cut_pt, cut_no)
                cut_data['verts'] = [cross]
                self.cut_data[seg] = cut_data
                

                #print(seg.ip0.local_loc, seg.ip1.local_loc)
                print(seg.ip0.view, seg.ip1.view)
                print(surf_no)
                print(cut_no)
                print(cross)
                
                print(f1.index, f0.index)
                print(ed.index)
                
                
                if cross == None:
                    print('No CROSS PRODUCT')
                    seg.path= [self.net_ui_context.mx * v for v in [seg.ip0.local_loc, seg.ip1.local_loc]]
                else:    
                    seg.path = [self.net_ui_context.mx * v for v in [seg.ip0.local_loc, cross, seg.ip1.local_loc]] #TODO
                cross_ed = ed
                seg.needs_calculation = False
                seg.calculation_complete = True
                seg.bad_segment = False
                seg.cut_method = 'ADJACENT_FACE'
                break

        #if no shared edge, need to cut across to the next face
        if not cross_ed:
            p_face = None

            vs = []
            epp = .0000000001
            use_limit = True
            attempts = 0
            seg.cut_method = 'PATH_2_POINTS'
            while epp < .0001 and not len(vs) and attempts <= 5:
                attempts += 1
                vs, eds, eds_crossed, faces_crossed, error = path_between_2_points_clean(self.net_ui_context.bme,
                    seg.ip0.local_loc, seg.ip0.face_index,
                    seg.ip1.local_loc, seg.ip1.face_index,
                    max_tests = 5000, debug = True,
                    prev_face = p_face,
                    use_limit = use_limit,
                    epsilon = epp)
                if len(vs) and error == 'LIMIT_SET':
                    vs = []
                    use_limit = False
                    print('Limit was too limiting, relaxing that consideration')

                elif len(vs) == 0 and error == 'EPSILON':
                    print('Epsilon was too small, relaxing epsilon')
                    epp *= 10
                elif len(vs) == 0 and error:
                    print('too bad, could not adjust due to ' + error)
                    print(p_face)
                    print(f0)
                    break

            if not len(vs):
                print('\n')
                print('CUTTING METHOD 2seeds ver1')
                seg.cut_method = 'CROSS_SECTION_2_SEEDS'
                vs = []
                epp = .00000001
                use_limit = True
                attempts = 0
                while epp < .0001 and not len(vs) and attempts <= 10:
                    attempts += 1
                    vs, eds, eds_crossed, faces_crossed, error = cross_section_2seeds_ver1(
                        self.net_ui_context.bme,
                        cut_pt, cut_no,
                        f0.index,seg.ip0.local_loc,
                        #f1.index, self.cut_pts[ind_p1],
                        f1.index, seg.ip1.local_loc,
                        max_tests = 10000, debug = True, prev_face = p_face,
                        epsilon = epp)
                    if len(vs) and error == 'LIMIT_SET':
                        vs = []
                        use_limit = False
                    elif len(vs) == 0 and error == 'EPSILON':
                        epp *= 10
                    elif len(vs) == 0 and error:
                        print('too bad, couldnt adjust due to ' + error)
                        print(p_face)
                        print(f0)
                        break

            if len(vs):
                print('crossed %i faces' % len(faces_crossed))
                seg.face_chain = faces_crossed
                seg.path = [self.net_ui_context.mx * v for v in vs]
                seg.bad_segment = False
                seg.needs_calculation = False
                seg.calculation_complete = True

                cut_data = {} 
                cut_data['face_crosses'] = faces_crossed
                cut_data['face_set'] = set(faces_crossed)
                cut_data['edge_crosses'] = eds_crossed
                cut_data['verts'] = vs
                
                old_cdata = []
                self.cut_data[seg] = cut_data
                for other_seg, cdata in self.cut_data.items():
                    if other_seg == seg: continue
                    if other_seg not in self.input_net.segments:
                        print('old seg data in self.cut_data')
                        continue
                    
                    if not cut_data['face_set'].isdisjoint(cdata['face_set']):
                        bad_seg = False
                
                        print("\n Found self intersection on this segment")
                        print("\n")
                        
                        overlap = cut_data['face_set'].intersection(cdata['face_set'])
                        
                        middle_overlap = overlap - set([cdata['face_crosses'][0], cdata['face_crosses'][-1]])
                        
                        if len(middle_overlap):
                            print('there is a middle self intersection')
                            bad_seg = True
                        #if overlap includes faces other than tip and tail
                        
                        #check that it does not touch any InputPoint faces
                        ipfaces = set(ip.bmface for ip in self.input_net.points)
                        if not cut_data['face_set'].isdisjoint(ipfaces):
                            print('crossed an IP Face, needs to not do that')
                            bad_seg = True
                        
                        if bad_seg:
                            seg.bad_segment = True #intersection
                            if seg in self.cut_data:
                                print('\n')
                                print('removing cut data for this segment')
                                print('\n')
                                print(seg)
                                print(seg.ip0.bmface)
                                print(seg.ip1.bmface)
                                self.cut_data.pop(seg, None)
                        
                            print('\n')
                            #only return if there is a forbidden self intersection
                            return  #found a self intersection, for now forbidden
                    
                
                
            else:  #we failed to find the next face in the face group
                seg.bad_segment = True
                seg.needs_calculation = False
                seg.calculation_complete = True
                seg.path = [seg.ip0.world_loc, seg.ip1.world_loc]
                print('cut failure!!!')
                
        return
    
    
    def pre_vis_geo(self, seg, bme, bvh, mx):

        geo = GeoPath(bme, bvh, mx)
        geo.seed = bme.faces[seg.ip0.face_index]
        geo.seed_loc = seg.ip0.local_loc
        geo.target = bme.faces[seg.ip1.face_index]
        geo.target_loc =  seg.ip0.local_loc
            
        geo.calculate_walk()
        
        self.geodesic = geo
        
        if geo.found_target():
            geo.gradient_descend()
            seg.path = [mx * v for v in geo.path]

    def preview_bad_segments_geodesic(self):
        for seg in self.input_net.segments:
            if seg.bad_segment:
                self.pre_vis_geo(seg, self.input_net.bme, self.net_ui_context.bvh, self.net_ui_context.mx)   


    def find_boundary_faces_cycles(self):
        self.boundary_faces = set()
        #find network cycles
        #this prevents open cycles from messing up things
        ip_cycles, seg_cycles = self.input_net.find_network_cycles()
        for seg_cyc in seg_cycles:
            for seg in seg_cyc:
                if seg not in self.cut_data: continue
                self.boundary_faces.update(self.cut_data[seg]['face_crosses'])
        for ip_cyc in ip_cycles:
            for ip in ip_cyc:
                self.boundary_faces.add(ip.bmface)   

    
    
    def validate_face_patch_spline_data(self, patch, spline_net): 
        '''
        after SplineNet or InputNet have had elements destroyed when painting
        those elements need to be de-referenced from the Patch Level
        maybe they should be del element at time or removal from the
        SplineNet or Input Net, but since I'm unsure on that, this needs to
        happen so we don't have stale references laying around
        '''
        
        ip_remove = []
        for ip in patch.ip_points:
            if ip not in self.input_net.points:
                ip_remove += [ip]
        
        seg_remove = []
        for seg in patch.input_net_segments:
            if seg not in self.input_net.segments:
                seg_remove += [seg]
                
        node_remove = []
        for node in patch.curve_nodes:
            if node not in spline_net.points:
                node_remove += [node]
                
        spline_remove = []
        for spline in patch.spline_net_segments:
            if spline not in spline_net.segments:
                spline_remove += [spline] 
                
                
        print('removed %i InputPoint references' % len(ip_remove))
        print('removed %i InputSegment references' % len(seg_remove))
        
        print('removed %i CurveNode references' % len(node_remove))
        print('removed %i SplineSegment references' % len(spline_remove))
        
        #TODO shoudl these be sets and do some difference_update
        for ip in ip_remove: 
            patch.ip_points.remove(ip)
        for seg in seg_remove:
            patch.input_net_segments.remove(seg)
        for node in node_remove:
            patch.curve_nodes.remove(node)
        for spline in spline_remove:
            patch.spline_net_segments.remove(spline)
        
                
    def create_spline_network_from_face_patches(self, spline_net):  #maybe this should be a tool instead of datastructure
        '''
        This only creates noew spline data from face patches that
        were initiated in paint mode, but have not had boundaries
        defined yet
        '''
        if len(self.face_patches) == 0:
            print('no face patches yet')
            return
        
        
        for patch in self.face_patches:
            if not patch.paint_modified: continue
            
            self.validate_face_patch_spline_data(patch, spline_net)
            
            if len(patch.curve_nodes) > 0: 
                print('patch still has nodes')
                continue
            if len(patch.ip_points) > 0:
                print('patch still has input_points')
                continue
            if len(patch.spline_net_segments) > 0:
                print('patch still has spline segments')
                continue
            if len(patch.input_net_segments) > 0:
                print('patch still has input segments')
                continue
            
            #TODO patch.is_inet_dirty?
            #TODO how to handle patches on non manifold boundary
            #TODO how to ensure non-tangentional patches (patches with a border)
            patch.find_boundary_edges(self.input_net.bme)
            raw_boundary = patch.perimeter_path
            
            #relaxed_boundary = relax_vert_chain(raw_boundary, in_place = False)
            #simple_path_inds = simplify_RDP(relaxed_boundary, .25)
            feature_inds = simplify_RDP(raw_boundary, .35)
            simple_path = [self.net_ui_context.mx * raw_boundary[i] for i in feature_inds]
            
            
            new_points = []
            new_segs = []
            prev_pnt = None
            
            for pt in simple_path[0:len(simple_path)-1]:
                delta = Vector((random.random(), random.random(), random.random()))
                delta.normalize()
                loc, no, face_ind, d =  self.net_ui_context.bvh.find_nearest(self.net_ui_context.imx * (pt + .1 * delta))
                if face_ind == None: continue
                #TODO store a view dictionary from the brush
                new_pnt = spline_net.create_point(self.net_ui_context.mx * loc, loc, self.net_ui_context.mx_norm * no, face_ind)
                #patch.ip_points.append(new_pnt)
                #new_pnt = self.spline_net.create_point(loc3d, loc, view_vector, face_ind)
                new_points += [new_pnt]
                if prev_pnt:
                    seg = SplineSegment(prev_pnt,new_pnt)
                    spline_net.segments.append(seg)
                    new_segs += [seg]
                #self.network_cutter.precompute_cut(seg)
                #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)
                prev_pnt = new_pnt
            
            #TODO non manifold boundaries
            #Close the loop
            seg = SplineSegment(prev_pnt,new_points[0])
            spline_net.segments.append(seg)  
            new_segs += [seg]
            
            
            patch.curve_nodes = new_points
            patch.spline_net_segments = new_segs
            patch.paint_modified = False  #we have now corrected paint modification
            
            for p in new_points:
                p.calc_handles()
            for seg in new_segs:
                seg.calc_bezier()
                seg.tessellate()
                seg.tessellate_IP_error(.1)
        
        #This happens OUTSIDE of this function at the UITools level...so the patch
        #does not know about it's DiscreteNetwork/InputNetwork elements yet
        #self.spline_net.push_to_input_net(self.net_ui_context, self.input_net)    
        #self.update_segments_async()   
    
    def update_painted_face_patches_splines(self, spline_net): 
        '''
        for any patch that had it's boundaries modified
        need to find the new boundary and fit splines to it
        '''
        
        
        inet_boundary_faces = set()
        #TODO, if we have fidelity in FacePatch references to input segments
        #thene we don't need to iterate over ALL of them
        #remove all existing boundary faces from the neighbors
        for seg in self.input_net.segments:
            seg_faces = self.cut_data[seg]['face_set']
            inet_boundary_faces.update(seg_faces)
        
        for ip in self.input_net.points:
            inet_boundary_faces.add(ip.bmface)
                    
        
        for patch in self.face_patches:
            #TODO, Only Affect Patches that have been painted and have existing spline data
            if not patch.paint_modified: continue
            #if len(patch.ip_points) == 0: continue  #we have not established this fidelity yet
            if len(patch.spline_net_segments) == 0: continue
            
            
            #get the patch one ring neighbors
            adjacent_faces = patch.adjacent_faces()
            
            adjacent_faces.difference_update(inet_boundary_faces)
            #color the non-affected boundary faces
            #cl = patch.color_layer
            #for f in adjacent_faces:
            #    for loop in f.loops:
            #        loop[cl]  = Color((.1,.1,.1))   
            
            
            b_edges = patch.find_all_boundary_edges()
            print('there are %i free boundary edges' % len(b_edges))
            
            
            #keep only the ones touching the....adjacent_faces
            #TODO
            unbounded_edges = set()
            for ed in b_edges:
                if len([f for f in ed.link_faces if f in adjacent_faces]) == 1:
                    unbounded_edges.add(ed)
            
            
            b_eds_inds = [ed.index for ed in unbounded_edges] #TODO, this is stupid
            geom = edge_loops_from_bmedges(self.input_net.bme, b_eds_inds)
            loops = geom['VERTS']
            
            spline_endpoints = [node for node in patch.curve_nodes if node.is_endpoint]
            
            def spline_dist(node, pt):
                return (node.world_loc - pt).length
            
            for v_loop in loops:
                print('there are %i verts in this loop' % len(v_loop))
                path = [self.input_net.bme.verts[ind].co.copy() for ind in v_loop]
                path_inds = simplify_RDP(path, .35)
                
                simple_path = [self.net_ui_context.mx * path[i] for i in path_inds]
                
                start_node = min(spline_endpoints, key = lambda x: spline_dist(x, simple_path[0]))
                end_node = min(spline_endpoints, key = lambda x: spline_dist(x, simple_path[-1]))
                
                new_points = []
                new_segs = []
                prev_pnt = start_node
                end_pnt = end_node
                
                if len(simple_path) == 2:
                    seg = SplineSegment(prev_pnt,end_pnt)
                    spline_net.segments.append(seg)  
                    new_segs += [seg]
                    
                    start_node.calc_handles()
                    end_pnt.calc_handles()
                    seg.calc_bezier()
                    seg.tessellate()
                    seg.tessellate_IP_error(.1)
                else:
                    for pt in simple_path[1:len(simple_path)-1]:
                        delta = Vector((random.random(), random.random(), random.random()))
                        delta.normalize()
                        loc, no, face_ind, d =  self.net_ui_context.bvh.find_nearest(self.net_ui_context.imx * (pt + .1 * delta))
                        if face_ind == None: continue
                        #TODO store a view dictionary from the brush
                        new_pnt = spline_net.create_point(self.net_ui_context.mx * loc, loc, self.net_ui_context.mx_norm * no, face_ind)
                        #patch.ip_points.append(new_pnt)
                        #new_pnt = self.spline_net.create_point(loc3d, loc, view_vector, face_ind)
                        new_points += [new_pnt]
                        if prev_pnt:
                            seg = SplineSegment(prev_pnt,new_pnt)
                            spline_net.segments.append(seg)
                            new_segs += [seg]
                        #self.network_cutter.precompute_cut(seg)
                        #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)
                        prev_pnt = new_pnt
                
                    
                    #connect to the endpoint
                    seg = SplineSegment(prev_pnt,end_pnt)
                    spline_net.segments.append(seg)  
                    new_segs += [seg]
                
                
                    patch.curve_nodes += new_points
                    patch.spline_net_segments += new_segs
                
                
                    for p in new_points:
                        p.calc_handles()
                    for seg in new_segs:
                        seg.calc_bezier()
                        seg.tessellate()
                        seg.tessellate_IP_error(.1)
                
                
                
            patch.paint_modified = False  #we have now corrected paint modification
            
            
                
            #get all the patch adjacent edges that are also adjacent to 1 ring neighbors
            #But not in the existing boundary edges
            
            continue


    def update_spline_edited_patches(self, spline_net): 
        '''
        for any patch that had it's boundaries modified by spline
        editing, needs to make sure patch data is correct
        
        this will be part of region_enter
        
        This is a brute force techqnique that can be avoided if we 
        use careful management of spline editings and if splines have
        link_patches mapping to adjacent patches
        '''
        
        
        #TODO, if we have fidelity in FacePatch references to input segments
        #thene we don't need to iterate over ALL of them
        #remove all existing boundary faces from the neighbors
        
    
        for patch in self.face_patches:
            #TODO, Only Affect Patches that have been spline_edits
            #TODO if not patch.spline_dirty: continue
            
    
            #get the patch one ring neighbors
            adjacent_faces = patch.adjacent_faces()
            
            
            boundary_splines = set()
            boundary_nodes = set()
            boundary_segs = set()
            boundary_points = set()
            
            #might be smarter...to just iterate over the ponts, and then do link_segments
            for node in spline_net.points:
                if node.bmface in adjacent_faces:
                    boundary_nodes.add(node)
            
            for node in boundary_nodes:
                for spline in node.link_segments:
                    if spline.n0 in boundary_nodes and spline.n1 in boundary_nodes:
                        boundary_splines.add(spline)
                        
                        
            for spline in boundary_splines:
                #add all the children
                boundary_segs.update(spline.input_segments)
            
            for seg in boundary_segs:
                boundary_points.update([seg.ip0, seg.ip1])   
                
            
            patch.ip_points = list(boundary_points)
            patch.input_net_segments = list(boundary_segs)
            patch.spline_net_segments = list(boundary_splines)
            patch.curve_nodes = list(boundary_nodes)
            
            print("patch has %i points" % len(patch.ip_points))  
            print("patch has %i nodes" % len(patch.curve_nodes))  
            print("patch has %i segments" % len(patch.input_net_segments))  
            print("patch has %i splines" % len(patch.spline_net_segments))  
           
    def create_network_from_face_patches(self):
        #TODO UNTESTED, SHOULD NOT EB USED
        #ACTUALLY SHOULD NEVER BE USED BECAUSE PAINT -> DIRECT EDIT is unnecessary
        if len(self.face_patches) == 0:
            print('no face patches yet')
            return
        
        for patch in self.face_patches:
            if not patch.paint_modified: continue
            
            patch.find_boundary_edges(self.input_net.bme)
            raw_boundary = patch.perimeter_path
        
            simple_path_inds = simplify_RDP(raw_boundary, .4)
            simple_path = [self.net_ui_context.mx * raw_boundary[i] for i in simple_path_inds]
            
     
            #self.simple_paths += [simple_path]
            patch.paint_modified = False
            patch.input_net_segments = []
            patch.ip_points = []
            new_points = []
            new_segs = []
            prev_pnt = None
            for ind in range(0, len(simple_path) -1):
                pt = simple_path[ind]
                #intersects that ray with the geometry
                delta = Vector((random.random(), random.random(), random.random()))
                delta.normalize()
                
                loc, no, face_ind, d =  self.net_ui_context.bvh.find_nearest(self.net_ui_context.imx * (pt + .1 * delta))
                if face_ind != None:
                    new_pnt = self.input_net.create_point(self.net_ui_context.mx * loc, loc, self.net_ui_context.mx_norm * no, face_ind)
                    patch.ip_points.append(new_pnt)
                if face_ind == None: continue
                #TODO store a view dictionary from the brush
                new_pnt = self.input_net.create_point(self.net_ui_context.mx * loc, loc, self.net_ui_context.mx_norm * no, face_ind)
                #patch.ip_points.append(new_pnt)
                #new_pnt = self.spline_net.create_point(loc3d, loc, view_vector, face_ind)
                new_points += [new_pnt]
                if prev_pnt:
                    print(prev_pnt)
                    seg = InputSegment(prev_pnt,new_pnt)
                    self.input_net.segments.append(seg)
                    patch.input_net_segments.append(seg)
                    
                    new_segs += [seg]
                #self.network_cutter.precompute_cut(seg)
                #seg.make_path(self.net_ui_context.bme, self.input_net.bvh, self.net_ui_context.mx, self.net_ui_context.imx)
                prev_pnt = new_pnt
             
             
            #seal the tail
            seg = InputSegment(prev_pnt,patch.ip_points[0])
            self.input_net.segments.append(seg)
            patch.input_net_segments.append(seg)
    
        self.update_segments_async()
    
    
    #########################################################
    #### Helper Functions for committing cut to BMesh #######
    #########################################################
    
    def find_old_face(self, new_f, max_iters = 5):
        '''
        iteratively drill down to find source face of new_f
        TODO return a list in order of inheritance?
        '''
        iters = 0
        old_f = None
        while iters < max_iters:
            iters += 1
            if new_f not in self.new_to_old_face_map: break
            old_f = self.new_to_old_face_map[new_f]
            new_f = old_f
            
        return old_f
        
    def find_new_faces(self, old_f, max_iters = 5):
        '''
        TODO, may want to only find NEWEST
        faces
        '''    
        if old_f not in self.old_to_new_face_map: return []
        
        iters = 0
        new_fs = []
        
        child_fs = self.old_to_new_face_map[old_f]
        new_fs += child_fs
        while iters < max_iters and len(child_fs):
            iters += 1
            next_gen = []
            for f in child_fs:
                if f in self.old_to_new_face_map:
                    next_gen += self.old_to_new_face_map[f] #this is always a pair
            
            new_fs += next_gen
            child_fs = next_gen

        #new_fs = old_to_new_face_map[old_f]
            
        return new_fs
            
    def find_newest_faces(self,old_f, max_iters = 5):
        '''
        '''    
        if old_f not in self.old_to_new_face_map: return []
        
        iters = 0
        child_fs = self.old_to_new_face_map[old_f]
        newest_faces = []
        
        if not any([f in self.old_to_new_face_map for f in child_fs]):
            return child_fs
        
        while iters < max_iters and any([f in self.old_to_new_face_map for f in child_fs]):
            iters += 1
            next_gen = []
            for f in child_fs:
                if f in self.old_to_new_face_map:
                    next_gen += self.old_to_new_face_map[f]
            
                else:
                    newest_faces += [f]
                    
                print(f)
            print(next_gen)
            child_fs = next_gen

        return newest_faces  
    
    def remap_input_point(self, ip):

        if ip.bmface not in self.old_to_new_face_map: return
        newest_faces = self.find_newest_faces(ip.bmface)
        found = False
        for new_f in newest_faces:
            if bmesh.geometry.intersect_face_point(new_f, ip.local_loc):
                #print('found the new face that corresponds')
                f = new_f
                found = True
                ip.bmface = f
                break
            
        return found
            
        
        #identify closed loops in the input
        #we might need to recompute cycles if we are creating new segments   
        
    def find_ip_chain_edgepoint(self,ip):
        '''
        will find all the Input Points that are connected
        to and on the same face as ip
        '''
        #TODO, split this off, thanks
        ip_chain =[ip]
        current_seg = ip.link_segments[0]  #edge poitns only have 1 seg
        ip_next = current_seg.other_point(ip)

        if not ip_next.bmface.is_valid: #no remapping yet
            self.remap_input_point(ip_next)
            
        while ip_next and ip_next.bmface == ip.bmface:
            
            #if ip_next in ip_set:
            #    ip_set.remove(ip_next)  #TODO, remove the whole chain from ip_set
                
            ip_chain += [ip_next]
            
            next_seg = next_segment(ip_next, current_seg)
            if next_seg == None: 
                print('there is no next seg')
                break
        
            ip_next = next_seg.other_point(ip_next)
            if not ip_next.bmface.is_valid:
                self.remap_input_point(ip_next)
            
            if ip_next.is_edgepoint(): 
                #ip_set.remove(ip_next)
                ip_chain += [ip_next]
                break
            current_seg = next_seg
            
            #implied if ip_next.bmface != ip.bmface...we have stepped off of this face
        
        seg_enter = None
        seg_exit = current_seg

        return ip_chain, seg_enter, seg_exit
        
    def find_ip_chain_facepoint(self,ip):
        '''
        this is the more generic which finds the chain
        in both directions along an InputPoint
        '''
                
        ip_chain = []
        
        #walk forward and back
        chain_0 = []
        seg_enter = None
        
        chain_1 = []
        seg_exit = None
        
        for seg in ip.link_segments:
            
            if seg == ip.link_segments[0]:
                chain = chain_0
            else:
                chain = chain_1

            current_seg = seg
            ip_next = current_seg.other_point(ip)
        
            if not ip_next.bmface.is_valid:
                self.remap_input_point(ip_next)

            while ip_next and ip_next.bmface == ip.bmface:  #walk along the input segments as long as the next input point is on the same face
                #if ip_next in ip_set:  #we remove it here only if its on the same face
                #    ip_set.remove(ip_next)
        
                chain += [ip_next]
                next_seg = next_segment(ip_next, current_seg)
                if next_seg == None: 
                    print('there is no next seg we are on an open loop')
                    break
        
                ip_next = next_seg.other_point(ip_next)
                if not ip_next.bmface.is_valid:
                    self.remap_input_point(ip_next)
                if ip_next.is_edgepoint(): 
                    
                    if ip_next.bmface == ip.bmface:
                        chain += [ip_next]  #if the edgepoint is on the same face we need to keep it
                    current_seg = next_seg
                    print('we broke on an endpoint')
                    #ip_set.remove(ip_next)
                    break
                current_seg = next_seg
            
            if seg==ip.link_segments[0]:
                seg_enter = current_seg
            else:
                seg_exit = current_seg
                
        chain_0.reverse()
        
        #if len(chain_0) and len(chain_1):
            #print(chain_0 + [ip] + chain_1)
            
        return chain_0 + [ip] + chain_1, seg_enter, seg_exit   
   
    def detect_ed_enter_exit(self):
        '''
        '''
        
        def ed_from_seg(ip, seg):   
            if ip == seg.ip0:
                ed = self.cut_data[seg]['edge_crosses'][0]
            else:
                ed = self.cut_data[seg]['edge_crosses'][-1]
            
            return ed
        
        #we know all the BMVerts from the IP points will be in the chain
        bmv_chain = [self.ip_bmvert_map[ipc] for ipc in self.ip_chain]
        
        if len(self.ip_chain) == 1:
            ip = self.ip_chain[0]
            if ip.is_edgepoint():
                ed_enter = ip.seed_geom
                ed_exit = ed_from_seg(ip, ip.link_segments[0])
                bmv_exit = self.cut_data[self.seg_exit]['bmedge_to_new_bmv'][ed_exit]
                bmv_chain += [bmv_exit]
            else:
                ed_enter = ed_from_seg(ip, ip.link_segments[0])
                bmv_enter = self.cut_data[self.seg_enter]['bmedge_to_new_bmv'][ed_enter]
                bmv_chain = [bmv_enter] + bmv_chain
                
                ed_exit = ed_from_seg(ip, ip.link_segments[1])
                bmv_exit = self.cut_data[self.seg_exit]['bmedge_to_new_bmv'][ed_exit]
                bmv_chain += [bmv_exit]
        else:
            ip_enter = self.ip_chain[0]
            ip_exit = self.ip_chain[-1]
        
            if ip_enter.is_edgepoint():
                ed_enter = ip_enter.seed_geom
                
            else:
                ed_enter = ed_from_seg(ip_enter, self.seg_enter)
                bmv_enter = self.cut_data[self.seg_enter]['bmedge_to_new_bmv'][ed_enter]
                bmv_chain = [bmv_enter] + bmv_chain
                
            if ip_exit.is_edgepoint():
                ed_exit = ip_exit.seed_geom
                
            else:
                ed_exit = ed_from_seg(ip_exit, self.seg_exit)
                bmv_exit = self.cut_data[self.seg_exit]['bmedge_to_new_bmv'][ed_exit]
                bmv_chain = bmv_chain + [bmv_exit]
                
        if not ed_enter.is_valid:
            print('ed enter is not valid')
        if not ed_exit.is_valid:
            print('ed exit is not valid')
            
        return ed_enter, ed_exit, bmv_chain
                
    def process_segment(self, seg):
        if seg not in self.cut_data:  #check for pre-processed cut data
            print('no cut data for this segment, must need to precompute or perhaps its internal to a face')
            
            print(seg.ip0.bmface)
            print(seg.ip1.bmface)
            
            print(seg.cut_method)
            seg.ip0.bmface.select_set(True)
            seg.ip1.bmface.select_set(True)
            
            print('PROCESS SEGMENT')
            
            return False
        
        if not all([f.is_valid for f in self.cut_data[seg]['face_crosses']]):  #check the validity of the pre-processed data
            print('segment out of date')
            self.recompute_segment(seg)
            return False
        
        if seg not in self.cut_data: #dumb check after recompute, #TODO, kick us back out into modal
            print('there is no cut data for this segment')
            return False
        
        if seg in self.completed_segments:  #don't attempt to cut it again.  TODO, delete InputSegment?  Return some flag for completed?
            print('segment already completed')
            return False
        
        start = time.time()
        
        cdata = self.cut_data[seg]
        if 'bmedge_to_new_bmv' not in cdata:
            bmedge_to_new_vert_map = {}
            cdata['bmedge_to_new_bmv'] = bmedge_to_new_vert_map  #yes, keep a map on the per segment level and on the whole network level
        else:
            bmedge_to_new_vert_map = cdata['bmedge_to_new_bmv']
            
        #create all verts on this segment
        for i, co in enumerate(cdata['verts']):
            bmedge = cdata['edge_crosses'][i]
            bmv = self.input_net.bme.verts.new(co)
            bmedge_to_new_vert_map[bmedge] = bmv
            self.new_bmverts.add(bmv)
        #now process all the faces crossed
        #for a face to be crossed 2 edges of the face must be crossed
        for f in cdata['face_crosses']:
            ed_enter = None
            ed_exit = None
            bmvs = []
            for ed in f.edges:
                if ed in cdata['bmedge_to_new_bmv']:
                    bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                    if ed_enter == None:
                        ed_enter = ed
                    else:
                        ed_exit = ed
                        
                elif ed in self.reprocessed_edge_map:
                    print('Found reprocessed edge')
                    re_ed = self.reprocessed_edge_map[ed]
                    if re_ed in cdata['bmedge_to_new_bmv']:
                        bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                        if ed_enter == None:
                            ed_enter = ed
                        else:
                            ed_exit = ed    
            
            if ed_enter == None:
                print('No ed enter')
                f.select_set(True)
                print(f)
                continue
            if ed_exit == None:
                print('no ed exit')
                f.select_set(True)
                print(f)
                continue
            
            if len(bmvs) != 2:
                print('bmvs not 2')
                continue
            
            #print(ed_enter, ed_exit, bmvs)
            f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvs)   
            if f1 == None or f2 == None:
                print('could not split faces in process segment')
                #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                return
                #continue 
            self.new_to_old_face_map[f1] = f
            self.new_to_old_face_map[f2] = f
            
            if f not in self.new_to_old_face_map:  #maybe not a good idea, if cutting twice and
                self.original_indices_map[f.index] = f
                    
            self.old_to_new_face_map[f] = [f1, f2]
            
        finish = time.time()
        #print('finished adding new faces in %f seconds' % (finish - start))
        
        
        #delete all old faces and edges from bmesh
        #but references remain in InputNetwork elements like InputPoint!
        #perhaps instead of deleting them on the fly, collect them and then delete them
        face_delete_start = time.time()
        #bmesh.ops.delete(self.input_net.bme, geom = cdata['face_crosses'], context = 3)
        
        #try and remove manually
        for bmf in cdata['face_crosses']:
            self.input_net.bme.faces.remove(bmf)
            
        face_delete_finish = time.time()
        #print('deleted old faces in %f seconds' % (face_delete_finish - face_delete_start))
        
        
        edge_delete_start = time.time()
        del_edges = [ed for ed in cdata['edge_crosses'] if len(ed.link_faces) == 0]
        del_edges = list(set(del_edges))
        #bmesh.ops.delete(self.input_net.bme, geom = del_edges, context = 4)
        for ed in del_edges:
            self.input_net.bme.edges.remove(ed)
        edge_delete_finish = time.time()
        #print('deleted old edges in %f seconds' % (edge_delete_finish - edge_delete_start))
        self.completed_segments.add(seg)
        #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
        
        return
     
    def recompute_segment(self, seg):
            
        '''
        recomputation most often needs to happen with the first or last face is crossed by
        2 segments.  It also happens when the user draws self intersecting cuts which
        is less common is handled by this
        '''
        if seg not in self.cut_data:  #check for pre-processed cut data
            print('no cut data for this segment, must need to precompute or perhaps its internal to a face')
            
            print(seg.ip0.bmface)
            print(seg.ip1.bmface)
            
            seg.ip0.bmface.select_set(True)
            seg.ip1.bmface.select_set(True)
            
            print("NOT RECOMPUTING?")
            print(seg.cut_method)
            return False
        
        start = time.time()
        cdata = self.cut_data[seg]
        bmedge_to_new_vert_map = {}
        cdata['bmedge_to_new_bmv'] = bmedge_to_new_vert_map
        
        bad_fs = [f for f in cdata['face_crosses'] if not f.is_valid]
        tip_bad = cdata['face_crosses'][0].is_valid == False
        tail_bad = cdata['face_crosses'][-1].is_valid == False

        #check for self intersections in the middle
        #if tip_bad and not tail_bad and len(bad_fs) > 1:
        #    print('bad tip, and bad middle not handled')
        #    return False
        
        #if tail_bad and not tip_bad and len(bad_fs) > 1:
        #    print('bad tail, and bad middle not handled')
        #    return False
        
        #if tip_bad and tail_bad and len(bad_fs) > 2:
        #    print('bad tip, tail and, middle not handled')
        #    return False
        
        #if not tip_bad and not tail_bad and len(bad_fs) >= 1:
        #    print('just a bad middle, not handled')
        #    return False
        
        #print('there are %i bad faces' % len(bad_fs))
        
        
        tip_bad, tail_bad = False, False
        
        f0 = seg.ip0.bmface  #TODO check validity in case rare cutting on IPFaces
        f1 = seg.ip1.bmface  #TDOO check validity in case rare cutting on IPFaces
        
        no = self.compute_cut_normal(seg)
        if len(cdata['edge_crosses']) == 2 and len(cdata['face_crosses']) == 1:
            tip_bad = True
            tail_bad = True
            co0 = cdata['verts'][0]
            co1 = cdata['verts'][0]  #wait shouldn't this be verts [1]
            new_fs = self.find_new_faces(cdata['face_crosses'][0])
            
            #fix the tip
            #find the new edge in new_faces that matches old ed_crosses[0]
            fixed_tip, fixed_tail = False, False
            for f in new_fs:
                ed_inters = find_bmedges_crossing_plane(co0, no, f.edges[:], .000001, sort = True)
                if len(ed_inters):
                    ed, loc = ed_inters[0]
                    
                    print('reality check, distance co to loc %f' % (co0 - loc).length)
                    
                    #create the new tip vertex
                    bmv = self.input_net.bme.verts.new(co0)
                    self.new_bmverts.add(bmv)
                    
                    #map the new edge and the old edge to that vertex
                    cdata['bmedge_to_new_bmv'][ed] = bmv
                    cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][0]] = bmv
                    
                    #map new edge to old edge
                    self.reprocessed_edge_map[ed] = cdata['edge_crosses'][0]
                    #replace old edge  ed_crosses[0] with the new edge for
                    cdata['edge_crosses'][0] = ed
                    cdata['face_crosses'][0] = f
                    
                    print('this edge should be the edge we find in the tail ')
                    print(ed_inters[1])
                    
                    break
            #fix the tail
            for f in new_fs:
                ed_inters = find_bmedges_crossing_plane(co1, no, f.edges[:], .000001, sort = True)
                if len(ed_inters):
                    ed, loc = ed_inters[0]
                    
                    print('reality check, distance co to loc %f' % (co1 - loc).length)
                    
                    #create the new tip vertex
                    bmv = self.input_net.bme.verts.new(co1)
                    self.new_bmverts.add(bmv)
                    #map the new edge and the old eget to that vertex
                    cdata['bmedge_to_new_bmv'][ed] = bmv
                    cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][1]] = bmv
                    #map old edge to new edge
                    self.reprocessed_edge_map[ed] = cdata['edge_crosses'][1]
                    #replace ed_crosses[0] with the new edge for
                    cdata['edge_crosses'][1] = ed
                    
                    print('does this edge match?')
                    print(ed)
                    
                    #there is only one face so we already did that
            
            return
        
        elif len(cdata['edge_crosses']) > 2 and len(cdata['face_crosses']) > 1:
            tip_bad = cdata['face_crosses'][0].is_valid == False
            tail_bad = cdata['face_crosses'][-1].is_valid == False
            
            
            co0 = cdata['verts'][0]
            co1 = cdata['verts'][-1]
            
            new_fs = self.find_new_faces(cdata['face_crosses'][0])
            #fix the tip
            #find the new edge in new_faces that matches old ed_crosses[0]
            fixed_tip, fixed_tail = False, False
            for f in new_fs:
                ed_inters = find_bmedges_crossing_plane(co0, no, f.edges[:], .000001, sort = True)
                if len(ed_inters):
                    ed, loc = ed_inters[0]
                    ed1, loc1 = ed_inters[1]
                    
                    print('reality check, distance co to loc %f' % (co0 - loc).length)
                    
                    #create the new tip vertex
                    bmv = self.input_net.bme.verts.new(co0)
                    self.new_bmverts.add(bmv)
                    #map the new edge and the old eget to that vertex
                    cdata['bmedge_to_new_bmv'][ed] = bmv
                    cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][0]] = bmv
                    #map the new edge to the old edge
                    self.reprocessed_edge_map[ed] = cdata['edge_crosses'][0]
                    #replace ed_crosses[0] with the new edge for
                    cdata['edge_crosses'][0] = ed
                    cdata['face_crosses'][0] = f
                    
                    #now....will the exit edge be the same?
                    cdata['edge_crosses'][1] = ed1
                    
                    #cdata['verts'].pop(0) #prevent a double vert creation
                    #cdata['edge_crosses'].pop(0)
                    
                    print('link faces of redge one')
                    print([f for f in ed1.link_faces])
                    
                    break
            
            #fix the tail
            print('fixnig a bad tail on segment')
            new_fs = self.find_new_faces(cdata['face_crosses'][-1])
            for f in new_fs:
                ed_inters = find_bmedges_crossing_plane(co1, no, f.edges[:], .000001, sort = True)
                if len(ed_inters):
                    ed, loc = ed_inters[0]
                    ed1, loc1 = ed_inters[1]
                    print('reality check, distance co to loc %f' % (co1 - loc).length)
                    #create the new tip vertex
                    bmv = self.input_net.bme.verts.new(co1)
                    self.new_bmverts.add(bmv)
                    #map the new edge and the old edge to the new BMVert
                    cdata['bmedge_to_new_bmv'][ed] = bmv
                    cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][-1]] = bmv
                    
                    #map the new edge to the old edge
                    self.reprocessed_edge_map[ed] = cdata['edge_crosses'][-1]
                    #replace old edge ed_crosses[-1] with the new edge for
                    cdata['edge_crosses'][-1] = ed
                    cdata['face_crosses'][-1] = f
                    cdata['edge_crosses'][-2] = ed1
                    
                    #cdata['verts'].pop() #prevent a double vert creation
                    #cdata['edge_crosses'].pop()
                    
                    print('link faces of edge one')
                    print([f for f in ed1.link_faces])
                    break        
        
        if tip_bad or tail_bad:
            print('fixed tip and tail , process again')
            
            #create all verts on this segment
            for i, co in enumerate(cdata['verts']):
                if tip_bad and i == 0: continue
                if tail_bad and i == len(cdata['verts']) - 1: continue
                bmedge = cdata['edge_crosses'][i]
                bmv = self.input_net.bme.verts.new(co)
                bmedge_to_new_vert_map[bmedge] = bmv
                self.new_bmverts.add(bmv)
        
            #now process all the faces crossed
            #for a face to be crossed 2 edges of the face must be crossed
            for f in cdata['face_crosses']:
                ed_enter = None
                ed_exit = None
                bmvs = []
                for ed in f.edges:
                    if ed in cdata['bmedge_to_new_bmv']:
                        bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                        if ed_enter == None:
                            ed_enter = ed
                        else:
                            ed_exit = ed
                            
                    elif ed in self.reprocessed_edge_map:
                        print('Found reprocessed edge')
                        re_ed = self.reprocessed_edge_map[ed]
                        if re_ed in cdata['bmedge_to_new_bmv']:
                            bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                            if ed_enter == None:
                                ed_enter = ed
                            else:
                                ed_exit = ed    
                
                if ed_enter == None:
                    print('No ed enter')
                    f.select_set(True)
                    print(f)
                    continue
                if ed_exit == None:
                    print('no ed exit')
                    f.select_set(True)
                    print(f)
                    continue
                if len(bmvs) != 2:
                    print('bmvs not 2')
                    continue
                
                #print(ed_enter, ed_exit, bmvs)
                f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvs)   
                if f1 == None or f2 == None:
                    print('could not split faces in process segment')
                    #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                    return
                    #continue 
                self.new_to_old_face_map[f1] = f
                self.new_to_old_face_map[f2] = f
                
                #if this is an original face, store it's index because bvh is going to report original mesh indices
                if f not in self.new_to_old_face_map:
                    self.original_indices_map[f.index] = f
                    
                self.old_to_new_face_map[f] = [f1, f2]
                
        
        finish = time.time()
        #print('Made new faces in %f seconds' % (finish - start))
            
        #delete all old faces and edges from bmesh
        #but references remain in InputNetwork elements like InputPoint!
        delete_face_start = time.time()
        #bmesh.ops.delete(self.input_net.bme, geom = cdata['face_crosses'], context = 3)
        for f in cdata['face_crosses']:
            self.input_net.bme.faces.remove(f)
        delete_face_finish = time.time()
        #print('Deleted old faces in %f seconds' % (delete_face_finish - delete_face_start))   
        
        delete_edges_start = time.time()    
        del_edges = [ed for ed in cdata['edge_crosses'] if len(ed.link_faces) == 0]
        del_edges = list(set(del_edges))
        #bmesh.ops.delete(self.input_net.bme, geom = del_edges, context = 4)
        for ed in del_edges:
            self.input_net.bme.edges.remove(ed)
        delete_edges_finish = time.time()
        #print('Deleted old edges in %f seconds' % (delete_edges_finish - delete_edges_start))
        start = finish
        
        
        self.completed_segments.add(seg)
        #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
            
              
        return False  
    
    def find_perimeter_edges(self):
        perim_edges = set()    
        for ed in self.input_net.bme.edges: #TODO, is there a faster way to collect these edges from the strokes? Yes
            if ed.verts[0] in self.new_bmverts and ed.verts[1] in self.new_bmverts:
                perim_edges.add(ed)

        high_genus_verts = set()    
        for v in self.input_net.bme.verts: 
            if v in self.new_bmverts: 
                if len([ed for ed in v.link_edges if ed in perim_edges]) >2:
                    high_genus_verts.add(v)
                    
        print('there aer %i high genus verts' % len(high_genus_verts))  #this method will fail in the case of a diamond on 4 adjacent quads.   
        for v in high_genus_verts:
            for ed in v.link_edges:
                if ed.other_vert(v) in high_genus_verts:
                    if ed in perim_edges:
                        perim_edges.remove(ed)

        self.boundary_edges = perim_edges    
        
    
       
    def knife_gometry_stepper_prepare(self):
        
        self.validate_cdata()  #there could be a lot of old cdata
        
        self.new_bmverts = set()
        for ip in self.input_net.points:
            bmv = self.input_net.bme.verts.new(ip.local_loc)
            self.ip_bmvert_map[ip] = bmv
            self.new_bmverts.add(bmv)
        
        self.input_net.bme.verts.ensure_lookup_table()
        self.input_net.bme.edges.ensure_lookup_table()
        self.input_net.bme.faces.ensure_lookup_table()
        
        ip_cycles, seg_cycles = self.input_net.find_network_cycles()
        
        for ip_cyc in ip_cycles:
            print(ip_cyc)
        #create a set of input points that we will pull from
        self.ip_set = set()
        
        for ip_cyc in ip_cycles:
            self.ip_set.update(ip_cyc)
        
        #pick an active IP
        self.active_ip = self.input_net.points[0]
        
        if self.active_ip.is_edgepoint():
            self.ip_chain, self.seg_enter, self.seg_exit = self.find_ip_chain_edgepoint(self.active_ip)
        else:
            self.ip_chain, self.seg_enter, self.seg_exit = self.find_ip_chain_facepoint(self.active_ip)
        
        
        
    def knife_geometry_step(self):
        
        #ensure we have prepared
        if len(self.ip_set) == 0: return
        
        #pick any one to start
        self.active_ip = self.ip_set.pop()
        
        #find all connected IP on the same face
        #as well as the segments which enter/exit the face (cross a face edge)
        if self.active_ip.is_edgepoint():
            self.ip_chain, self.seg_enter, self.seg_exit = self.find_ip_chain_edgepoint(self.active_ip)
        else:
            self.ip_chain, self.seg_enter, self.seg_exit = self.find_ip_chain_facepoint(self.active_ip)
    
        print(len(self.ip_chain))
        self.ip_set.difference_update(self.ip_chain)
        
        
        #commit the entrance and exit segments to BMesh if not already
        if self.seg_enter and self.seg_enter not in self.completed_segments:
            self.process_segment(self.seg_enter)     
        if self.seg_exit and self.seg_exit not in self.completed_segments:
            self.process_segment(self.seg_exit)
        
        #Detect the entrance and exit edges for this face
        ed_enter, ed_exit, bmvert_chain = self.detect_ed_enter_exit()
        
        #check for reprocessing
        if ed_enter in self.reprocessed_edge_map:
            ed_enter = self.reprocessed_edge_map[ed_enter]
        if ed_exit in self.reprocessed_edge_map:
            ed_exit = self.reprocessed_edge_map[ed_exit]
               
        #actually split the face
        f = self.active_ip.bmface
        f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvert_chain)
        
        #clean up the old geom, and do some book_keeping/mapping
        if f1 != None and f2 != None:
            self.new_to_old_face_map[f1] = f
            self.new_to_old_face_map[f2] = f
            self.old_to_new_face_map[f] = [f1, f2]
            self.input_net.bme.faces.remove(f)
            
            del_eds = [ed for ed in [ed_enter, ed_exit] if len(ed.link_faces) == 0]
            del_eds = list(set(del_eds))
            for ed in del_eds:
                self.input_net.bme.edges.remove(ed)
            
        else:
            #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
            print('f1 or f2 is none why')
            return            
                    
     
    
    def knife_geometry4(self):
        self.knife_gometry_stepper_prepare()
        
        while len(self.ip_set):
            self.knife_geometry_step()
        
        self.seg_enter = None
        self.seg_exit = None
        self.active_ip = None
        self.knife_complete = True
        
        if len(self.face_patches):
            self.active_patch = self.face_patches[0]
        self.input_net.bme.faces.ensure_lookup_table()
        self.input_net.bme.edges.ensure_lookup_table()
        self.input_net.bme.verts.ensure_lookup_table()   
        return
        
        
    def knife_geometry3(self):
        #check all deferred calculations
        knife_sart = time.time()
        for seg in self.input_net.segments:
            if (seg.needs_calculation == True) or (seg.calculation_complete == False):
                print('segments still computing')
                return
            
            if seg.is_bad:
                print('bad_segment')  #TODO raise error message #TODO put this in a can_start/can_enter kind of check
                return
        #ensure no bad segments
        
        
        #dictionaries to map newly created faces to their original faces and vice versa
        original_face_indices = self.original_indices_map
        new_to_old_face_map = self.new_to_old_face_map
        old_to_new_face_map = self.old_to_new_face_map
        completed_segments = self.completed_segments
        completed_input_points = self.completed_input_points
        ip_bmvert_map = self.ip_bmvert_map
    
        new_bmverts = set()
        
       
        
        #helper function to walk along input point chains
        def next_segment(ip, current_seg): #TODO Code golf this
            if len(ip.link_segments) != 2: return None  #TODO, the the segment to right
            return [seg for seg in ip.link_segments if seg != current_seg][0]
        
        def find_old_face(new_f, max_iters = 5):
            '''
            iteratively drill down to find source face of new_f
            TODO return a list in order of inheritance?
            '''
            iters = 0
            old_f = None
            while iters < max_iters:
                iters += 1
                if new_f not in new_to_old_face_map: break
                old_f = new_to_old_face_map[new_f]
                new_f = old_f
                
            return old_f
        
        def find_new_faces(old_f, max_iters = 5):
            '''
            TODO, may want to only find NEWEST
            faces
            '''    
            if old_f not in old_to_new_face_map: return []
            
            iters = 0
            new_fs = []
            
            child_fs = old_to_new_face_map[old_f]
            new_fs += child_fs
            while iters < max_iters and len(child_fs):
                iters += 1
                next_gen = []
                for f in child_fs:
                    if f in old_to_new_face_map:
                        next_gen += old_to_new_face_map[f] #this is always a pair
                
                new_fs += next_gen
                child_fs = next_gen
    
            #new_fs = old_to_new_face_map[old_f]
                
            return new_fs
            
        def find_newest_faces(old_f, max_iters = 5):
            '''
            '''    
            if old_f not in old_to_new_face_map: return []
            
            iters = 0
            child_fs = old_to_new_face_map[old_f]
            newest_faces = []
            
            if not any([f in old_to_new_face_map for f in child_fs]):
                return child_fs
            
            while iters < max_iters and any([f in old_to_new_face_map for f in child_fs]):
                iters += 1
                next_gen = []
                for f in child_fs:
                    if f in old_to_new_face_map:
                        next_gen += old_to_new_face_map[f]
                
                    else:
                        newest_faces += [f]
                        
                    print(f)
                print(next_gen)
                child_fs = next_gen

            return newest_faces     
        
        def recompute_segment(seg):
            
            '''
            recomputation most often needs to happen with the first or last face is crossed by
            2 segments.  It also happens when the user draws self intersecting cuts which
            is less common is handled by this
            '''
            if seg not in self.cut_data:  #check for pre-processed cut data
                print('no cut data for this segment, must need to precompute or perhaps its internal to a face')
                
                print(seg.ip0.bmface)
                print(seg.ip1.bmface)
                
                seg.ip0.bmface.select_set(True)
                seg.ip1.bmface.select_set(True)
                
                print("NOT RECOMPUTING?")
                print(seg.cut_method)
                return False
            
            start = time.time()
            cdata = self.cut_data[seg]
            bmedge_to_new_vert_map = {}
            cdata['bmedge_to_new_bmv'] = bmedge_to_new_vert_map
            
            bad_fs = [f for f in cdata['face_crosses'] if not f.is_valid]
            tip_bad = cdata['face_crosses'][0].is_valid == False
            tail_bad = cdata['face_crosses'][-1].is_valid == False
    
            #check for self intersections in the middle
            #if tip_bad and not tail_bad and len(bad_fs) > 1:
            #    print('bad tip, and bad middle not handled')
            #    return False
            
            #if tail_bad and not tip_bad and len(bad_fs) > 1:
            #    print('bad tail, and bad middle not handled')
            #    return False
            
            #if tip_bad and tail_bad and len(bad_fs) > 2:
            #    print('bad tip, tail and, middle not handled')
            #    return False
            
            #if not tip_bad and not tail_bad and len(bad_fs) >= 1:
            #    print('just a bad middle, not handled')
            #    return False
            
            #print('there are %i bad faces' % len(bad_fs))
            
            
            tip_bad, tail_bad = False, False
            
            f0 = seg.ip0.bmface  #TODO check validity in case rare cutting on IPFaces
            f1 = seg.ip1.bmface  #TDOO check validity in case rare cutting on IPFaces
            
            no = self.compute_cut_normal(seg)
            if len(cdata['edge_crosses']) == 2 and len(cdata['face_crosses']) == 1:
                tip_bad = True
                tail_bad = True
                co0 = cdata['verts'][0]
                co1 = cdata['verts'][0]  #wait shouldn't this be verts [1]
                new_fs = find_new_faces(cdata['face_crosses'][0])
                
                #fix the tip
                #find the new edge in new_faces that matches old ed_crosses[0]
                fixed_tip, fixed_tail = False, False
                for f in new_fs:
                    ed_inters = find_bmedges_crossing_plane(co0, no, f.edges[:], .000001, sort = True)
                    if len(ed_inters):
                        ed, loc = ed_inters[0]
                        
                        print('reality check, distance co to loc %f' % (co0 - loc).length)
                        
                        #create the new tip vertex
                        bmv = self.input_net.bme.verts.new(co0)
                        new_bmverts.add(bmv)
                        
                        #map the new edge and the old edge to that vertex
                        cdata['bmedge_to_new_bmv'][ed] = bmv
                        cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][0]] = bmv
                        
                        #map new edge to old edge
                        self.reprocessed_edge_map[ed] = cdata['edge_crosses'][0]
                        #replace old edge  ed_crosses[0] with the new edge for
                        cdata['edge_crosses'][0] = ed
                        cdata['face_crosses'][0] = f
                        
                        print('this edge should be the edge we find in the tail ')
                        print(ed_inters[1])
                        
                        break
                #fix the tail
                for f in new_fs:
                    ed_inters = find_bmedges_crossing_plane(co1, no, f.edges[:], .000001, sort = True)
                    if len(ed_inters):
                        ed, loc = ed_inters[0]
                        
                        print('reality check, distance co to loc %f' % (co1 - loc).length)
                        
                        #create the new tip vertex
                        bmv = self.input_net.bme.verts.new(co1)
                        new_bmverts.add(bmv)
                        #map the new edge and the old eget to that vertex
                        cdata['bmedge_to_new_bmv'][ed] = bmv
                        cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][1]] = bmv
                        #map old edge to new edge
                        self.reprocessed_edge_map[ed] = cdata['edge_crosses'][1]
                        #replace ed_crosses[0] with the new edge for
                        cdata['edge_crosses'][1] = ed
                        
                        print('does this edge match?')
                        print(ed)
                        
                        #there is only one face so we already did that
                
                return
            
            elif len(cdata['edge_crosses']) > 2 and len(cdata['face_crosses']) > 1:
                tip_bad = cdata['face_crosses'][0].is_valid == False
                tail_bad = cdata['face_crosses'][-1].is_valid == False
                
                
                co0 = cdata['verts'][0]
                co1 = cdata['verts'][-1]
                
                new_fs = find_new_faces(cdata['face_crosses'][0])
                #fix the tip
                #find the new edge in new_faces that matches old ed_crosses[0]
                fixed_tip, fixed_tail = False, False
                for f in new_fs:
                    ed_inters = find_bmedges_crossing_plane(co0, no, f.edges[:], .000001, sort = True)
                    if len(ed_inters):
                        ed, loc = ed_inters[0]
                        ed1, loc1 = ed_inters[1]
                        
                        print('reality check, distance co to loc %f' % (co0 - loc).length)
                        
                        #create the new tip vertex
                        bmv = self.input_net.bme.verts.new(co0)
                        new_bmverts.add(bmv)
                        #map the new edge and the old eget to that vertex
                        cdata['bmedge_to_new_bmv'][ed] = bmv
                        cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][0]] = bmv
                        #map the new edge to the old edge
                        self.reprocessed_edge_map[ed] = cdata['edge_crosses'][0]
                        #replace ed_crosses[0] with the new edge for
                        cdata['edge_crosses'][0] = ed
                        cdata['face_crosses'][0] = f
                        
                        #now....will the exit edge be the same?
                        cdata['edge_crosses'][1] = ed1
                        
                        #cdata['verts'].pop(0) #prevent a double vert creation
                        #cdata['edge_crosses'].pop(0)
                        
                        print('link faces of redge one')
                        print([f for f in ed1.link_faces])
                        
                        break
                
                #fix the tail
                print('fixnig a bad tail on segment')
                new_fs = find_new_faces(cdata['face_crosses'][-1])
                for f in new_fs:
                    ed_inters = find_bmedges_crossing_plane(co1, no, f.edges[:], .000001, sort = True)
                    if len(ed_inters):
                        ed, loc = ed_inters[0]
                        ed1, loc1 = ed_inters[1]
                        print('reality check, distance co to loc %f' % (co1 - loc).length)
                        #create the new tip vertex
                        bmv = self.input_net.bme.verts.new(co1)
                        new_bmverts.add(bmv)
                        #map the new edge and the old edge to the new BMVert
                        cdata['bmedge_to_new_bmv'][ed] = bmv
                        cdata['bmedge_to_new_bmv'][cdata['edge_crosses'][-1]] = bmv
                        
                        #map the new edge to the old edge
                        self.reprocessed_edge_map[ed] = cdata['edge_crosses'][-1]
                        #replace old edge ed_crosses[-1] with the new edge for
                        cdata['edge_crosses'][-1] = ed
                        cdata['face_crosses'][-1] = f
                        cdata['edge_crosses'][-2] = ed1
                        
                        #cdata['verts'].pop() #prevent a double vert creation
                        #cdata['edge_crosses'].pop()
                        
                        print('link faces of edge one')
                        print([f for f in ed1.link_faces])
                        break        
            
            if tip_bad or tail_bad:
                print('fixed tip and tail , process again')
                
                #create all verts on this segment
                for i, co in enumerate(cdata['verts']):
                    if tip_bad and i == 0: continue
                    if tail_bad and i == len(cdata['verts']) - 1: continue
                    bmedge = cdata['edge_crosses'][i]
                    bmv = self.input_net.bme.verts.new(co)
                    bmedge_to_new_vert_map[bmedge] = bmv
                    new_bmverts.add(bmv)
            
                #now process all the faces crossed
                #for a face to be crossed 2 edges of the face must be crossed
                for f in cdata['face_crosses']:
                    ed_enter = None
                    ed_exit = None
                    bmvs = []
                    for ed in f.edges:
                        if ed in cdata['bmedge_to_new_bmv']:
                            bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                            if ed_enter == None:
                                ed_enter = ed
                            else:
                                ed_exit = ed
                                
                        elif ed in self.reprocessed_edge_map:
                            print('Found reprocessed edge')
                            re_ed = self.reprocessed_edge_map[ed]
                            if re_ed in cdata['bmedge_to_new_bmv']:
                                bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                                if ed_enter == None:
                                    ed_enter = ed
                                else:
                                    ed_exit = ed    
                    
                    if ed_enter == None:
                        print('No ed enter')
                        f.select_set(True)
                        print(f)
                        continue
                    if ed_exit == None:
                        print('no ed exit')
                        f.select_set(True)
                        print(f)
                        continue
                    if len(bmvs) != 2:
                        print('bmvs not 2')
                        continue
                    
                    #print(ed_enter, ed_exit, bmvs)
                    f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvs)   
                    if f1 == None or f2 == None:
                        print('could not split faces in process segment')
                        #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                        return
                        #continue 
                    new_to_old_face_map[f1] = f
                    new_to_old_face_map[f2] = f
                    
                    #if this is an original face, store it's index because bvh is going to report original mesh indices
                    if f not in new_to_old_face_map:
                        original_face_indices[f.index] = f
                        
                    old_to_new_face_map[f] = [f1, f2]
                    
            
            finish = time.time()
            print('Made new faces in %f seconds' % (finish - start))
                
            #delete all old faces and edges from bmesh
            #but references remain in InputNetwork elements like InputPoint!
            delete_face_start = time.time()
            #bmesh.ops.delete(self.input_net.bme, geom = cdata['face_crosses'], context = 3)
            for f in cdata['face_crosses']:
                self.input_net.bme.faces.remove(f)
            delete_face_finish = time.time()
            print('Deleted old faces in %f seconds' % (delete_face_finish - delete_face_start))   
            
            delete_edges_start = time.time()    
            del_edges = [ed for ed in cdata['edge_crosses'] if len(ed.link_faces) == 0]
            del_edges = list(set(del_edges))
            #bmesh.ops.delete(self.input_net.bme, geom = del_edges, context = 4)
            for ed in del_edges:
                self.input_net.bme.edges.remove(ed)
            delete_edges_finish = time.time()
            print('Deleted old edges in %f seconds' % (delete_edges_finish - delete_edges_start))
            start = finish
            
            
            completed_segments.add(seg)
            #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                
                  
            return False
                    
        def process_segment(seg):
            if seg not in self.cut_data:  #check for pre-processed cut data
                print('no cut data for this segment, must need to precompute or perhaps its internal to a face')
                
                print(seg.ip0.bmface)
                print(seg.ip1.bmface)
                
                print(seg.cut_method)
                seg.ip0.bmface.select_set(True)
                seg.ip1.bmface.select_set(True)
                
                print('PROCESS SEGMENT')
                
                return False
            
            if not all([f.is_valid for f in self.cut_data[seg]['face_crosses']]):  #check the validity of the pre-processed data
                print('segment out of date')
                recompute_segment(seg)
                return False
            
            if seg not in self.cut_data: #dumb check after recompute, #TODO, kick us back out into modal
                print('there is no cut data for this segment')
                return False
            
            if seg in completed_segments:  #don't attempt to cut it again.  TODO, delete InputSegment?  Return some flag for completed?
                print('segment already completed')
                return False
            
            start = time.time()
            
            cdata = self.cut_data[seg]
            if 'bmedge_to_new_bmv' not in cdata:
                bmedge_to_new_vert_map = {}
                cdata['bmedge_to_new_bmv'] = bmedge_to_new_vert_map  #yes, keep a map on the per segment level and on the whole network level
            else:
                bmedge_to_new_vert_map = cdata['bmedge_to_new_bmv']
                
            #create all verts on this segment
            for i, co in enumerate(cdata['verts']):
                bmedge = cdata['edge_crosses'][i]
                bmv = self.input_net.bme.verts.new(co)
                bmedge_to_new_vert_map[bmedge] = bmv
                new_bmverts.add(bmv)
            #now process all the faces crossed
            #for a face to be crossed 2 edges of the face must be crossed
            for f in cdata['face_crosses']:
                ed_enter = None
                ed_exit = None
                bmvs = []
                for ed in f.edges:
                    if ed in cdata['bmedge_to_new_bmv']:
                        bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                        if ed_enter == None:
                            ed_enter = ed
                        else:
                            ed_exit = ed
                            
                    elif ed in self.reprocessed_edge_map:
                        print('Found reprocessed edge')
                        re_ed = self.reprocessed_edge_map[ed]
                        if re_ed in cdata['bmedge_to_new_bmv']:
                            bmvs.append(cdata['bmedge_to_new_bmv'][ed])
                            if ed_enter == None:
                                ed_enter = ed
                            else:
                                ed_exit = ed    
                
                if ed_enter == None:
                    print('No ed enter')
                    f.select_set(True)
                    print(f)
                    continue
                if ed_exit == None:
                    print('no ed exit')
                    f.select_set(True)
                    print(f)
                    continue
                
                if len(bmvs) != 2:
                    print('bmvs not 2')
                    continue
                
                #print(ed_enter, ed_exit, bmvs)
                f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvs)   
                if f1 == None or f2 == None:
                    print('could not split faces in process segment')
                    #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                    return
                    #continue 
                new_to_old_face_map[f1] = f
                new_to_old_face_map[f2] = f
                
                if f not in new_to_old_face_map:
                    original_face_indices[f.index] = f
                        
                old_to_new_face_map[f] = [f1, f2]
                
            finish = time.time()
            print('finished adding new faces in %f seconds' % (finish - start))
            
            
            #delete all old faces and edges from bmesh
            #but references remain in InputNetwork elements like InputPoint!
            #perhaps instead of deleting them on the fly, collect them and then delete them
            face_delete_start = time.time()
            #bmesh.ops.delete(self.input_net.bme, geom = cdata['face_crosses'], context = 3)
            
            #try and remove manually
            for bmf in cdata['face_crosses']:
                self.input_net.bme.faces.remove(bmf)
                
            face_delete_finish = time.time()
            print('deleted old faces in %f seconds' % (face_delete_finish - face_delete_start))
            
            
            edge_delete_start = time.time()
            del_edges = [ed for ed in cdata['edge_crosses'] if len(ed.link_faces) == 0]
            del_edges = list(set(del_edges))
            #bmesh.ops.delete(self.input_net.bme, geom = del_edges, context = 4)
            for ed in del_edges:
                self.input_net.bme.edges.remove(ed)
            edge_delete_finish = time.time()
            print('deleted old edges in %f seconds' % (edge_delete_finish - edge_delete_start))
            completed_segments.add(seg)
            #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
            
            return
        
        #first, we wil attempt to process every segment
        
        #all input points get a BMVert
        
        def remap_input_point(ip):

            if ip.bmface not in old_to_new_face_map: return
            newest_faces = find_newest_faces(ip.bmface)
            found = False
            for new_f in newest_faces:
                if bmesh.geometry.intersect_face_point(new_f, ip.local_loc):
                    print('found the new face that corresponds')
                    f = new_f
                    found = True
                    ip.bmface = f
                    break
                
            return found
            
        
        #identify closed loops in the input
        #we might need to recompute cycles if we are creating new segments   
        
        def find_ip_chain_edgepoint(ip):
            '''
            will find all the Input Points that are connected
            to and on the same face as ip
            '''
            #TODO, split this off, thanks
            ip_chain =[ip]
            current_seg = ip.link_segments[0]  #edge poitns only have 1 seg
            ip_next = current_seg.other_point(ip)

            if not ip_next.bmface.is_valid:
                remap_input_point(ip_next)
                
            while ip_next and ip_next.bmface == ip.bmface:
                
                #if ip_next in ip_set:
                #    ip_set.remove(ip_next)  #TODO, remove the whole chain from ip_set
                    
                ip_chain += [ip_next]
                
                next_seg = next_segment(ip_next, current_seg)
                if next_seg == None: 
                    print('there is no next seg')
                    break
            
                ip_next = next_seg.other_point(ip_next)
                if not ip_next.bmface.is_valid:
                    remap_input_point(ip_next)
                
                if ip_next.is_edgepoint(): 
                    #ip_set.remove(ip_next)
                    ip_chain += [ip_next]
                    break
                current_seg = next_seg
                
                #implied if ip_next.bmface != ip.bmface...we have stepped off of this face
            

            return ip_chain
        
        def find_ip_chain_facepoint(ip):
            '''
            this is the more generic which finds the chain
            in both directions along an InputPoint
            '''
                    
            ip_chain = []
            
            #wak forward and back
            chain_0 = []
            chain_1 = []
            for seg in ip.link_segments:
                
                if seg == ip.link_segments[0]:
                    chain = chain_0
                else:
                    chain = chain_1
                
                current_seg = seg
                ip_next = current_seg.other_point(ip)
            
                if not ip_next.bmface.is_valid:
                    remap_input_point(ip_next)

                while ip_next and ip_next.bmface == ip.bmface:  #walk along the input segments as long as the next input point is on the same face
                    #if ip_next in ip_set:  #we remove it here only if its on the same face
                    #    ip_set.remove(ip_next)
            
                    chain += [ip_next]
                    next_seg = next_segment(ip_next, current_seg)
                    if next_seg == None: 
                        print('there is no next seg we are on an open loop')
                        break
            
                    ip_next = next_seg.other_point(ip_next)
                    if not ip_next.bmface.is_valid:
                        remap_input_point(ip_next)
                    if ip_next.is_edgepoint(): 
                        print('we broke on an endpoint')
                        #ip_set.remove(ip_next)
                        break
                    current_seg = next_seg
                
            chain_0.reverse()
            
            if len(chain_0)  and len(chain_1):
                print(chain_0 + [ip] + chain_1)
                
            return chain_0 + [ip] + chain_1

        def split_ip_face_edgepoint(ip):
            
            ip_chain = find_ip_chain_edgepoint(ip)
            
            ed_enter = ip_chain[0].seed_geom # this is the entrance edge
            
            if len(ip_chain) > 1 and ip_chain[-1].is_edgepoint():  #cut across a single face from edge to tedge
                bmvert_chain  = [self.ip_bmvert_map[ipc] for ipc in ip_chain]           
                ed_exit = ip_chain[-1].seed_geom
            else:
                if current_seg not in completed_segments:
                    result = process_segment(current_seg)
                    #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                    #return
            
                if current_seg.ip0 == ip_next:  #test the direction of the segment
                    ed_exit = self.cut_data[current_seg]['edge_crosses'][-1]
                else:
                    ed_exit = self.cut_data[current_seg]['edge_crosses'][0]
                
                bmvert_chain  = [self.ip_bmvert_map[ipc] for ipc in ip_chain] + \
                            [self.cut_data[current_seg]['bmedge_to_new_bmv'][ed_exit]]
            

            self.input_net.bme.verts.ensure_lookup_table()
            self.input_net.bme.edges.ensure_lookup_table()
            self.input_net.bme.faces.ensure_lookup_table()  
                
            f = ip.bmface
            f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvert_chain)
            
            if f1 != None and f2 != None:
                new_to_old_face_map[f1] = f
                new_to_old_face_map[f2] = f
                old_to_new_face_map[f] = [f1, f2]
                
                if f not in new_to_old_face_map:
                    original_face_indices[f.index] = f
                
                self.input_net.bme.faces.remove(f)
                #bmesh.ops.delete(self.input_net.bme, geom = [f], context = 3)
                
                del_eds = [ed for ed in [ed_enter, ed_exit] if len(ed.link_faces) == 0]
                del_eds = list(set(del_eds))
                
                for ded in del_eds:
                    self.input_net.bme.edges.remove(ded)
                #bmesh.ops.delete(self.input_net.bme, geom = del_eds, context = 4)
            
            else:
                #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                print('f1 or f2 is none why')
                return
######################################################################
################33 ORIGINAL FUNCTION  ################################            
        ip_cycles, seg_cycles = self.input_net.find_network_cycles()
        
                
        for ip in self.input_net.points:
            bmv = self.input_net.bme.verts.new(ip.local_loc)
            self.ip_bmvert_map[ip] = bmv
            new_bmverts.add(bmv)
        
        
        for ip_cyc in ip_cycles:
            ip_set = set(ip_cyc)
            
            for i, ip in enumerate(ip_cyc):
                print('\n')
                print('attempting ip %i' % i)
                start = time.time()
                if ip not in ip_set: 
                    print('Already seen this IP %i' % i)
                    #print(ip)
                    continue #already handled this one

                if not ip.bmface.is_valid:
                    remap_input_point(ip)
                #print(ip)
                if ip.is_edgepoint(): #we have to treat edge points differently
                    print('cutting starting at boundary edge point')
                    #TODO, split this off, thanks
                    ip_chain =[ip]
                    current_seg = ip.link_segments[0]  #edge poitns only have 1 seg
                    ip_next = current_seg.other_point(ip)
    
                    if not ip_next.bmface.is_valid:
                        remap_input_point(ip_next)
                        
                    while ip_next and ip_next.bmface == ip.bmface:
                        
                        if ip_next in ip_set:
                            ip_set.remove(ip_next)
                            
                        ip_chain += [ip_next]
                        
                        next_seg = next_segment(ip_next, current_seg)
                        if next_seg == None: 
                            print('there is no next seg')
                            break
                    
                        ip_next = next_seg.other_point(ip_next)
                        if not ip_next.bmface.is_valid:
                            remap_input_point(ip_next)
                        
                        if ip_next.is_edgepoint(): 
                            ip_set.remove(ip_next)
                            break
                        current_seg = next_seg
                    

                    ed_enter = ip_chain[0].seed_geom # this is the entrance edge
                    
                    if ip_next.is_edgepoint():
                        bmvert_chain  = [self.ip_bmvert_map[ipc] for ipc in ip_chain] + \
                                    [self.ip_bmvert_map[ip_next]]
                                    
                        ed_exit = ip_next.seed_geom
                    else:
                        
                        if current_seg not in completed_segments:
                            result = process_segment(current_seg)
                            #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                            #return
                    
                        if current_seg.ip0 == ip_next:  #test the direction of the segment
                            ed_exit = self.cut_data[current_seg]['edge_crosses'][-1]
                        else:
                            ed_exit = self.cut_data[current_seg]['edge_crosses'][0]
                        
                        bmvert_chain  = [self.ip_bmvert_map[ipc] for ipc in ip_chain] + \
                                    [self.cut_data[current_seg]['bmedge_to_new_bmv'][ed_exit]]
                    
                    interval_start = time.time()
                    #this is dumb, expensive?
                    self.input_net.bme.verts.ensure_lookup_table()
                    self.input_net.bme.edges.ensure_lookup_table()
                    self.input_net.bme.faces.ensure_lookup_table()  
                    
                    finish = time.time()
                    print('updated lookup tables in %f' % (finish - interval_start))
                    interval_start = time.time()
                    
                    f = ip.bmface
                    f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvert_chain)
                    
                    finish = time.time()
                    print('split face in %f' % (finish - interval_start))
                    interval_start = time.time()
                    
                    
                    if f1 != None and f2 != None:
                        new_to_old_face_map[f1] = f
                        new_to_old_face_map[f2] = f
                        old_to_new_face_map[f] = [f1, f2]
                        
                        if f not in new_to_old_face_map:
                            original_face_indices[f.index] = f
                        
                        bmesh.ops.delete(self.input_net.bme, geom = [f], context = 3)
                        
                        del_eds = [ed for ed in [ed_enter, ed_exit] if len(ed.link_faces) == 0]
                        del_eds = list(set(del_eds))
                        bmesh.ops.delete(self.input_net.bme, geom = del_eds, context = 4)
                    
                        finish = time.time()
                        print('deleted split face in %f' % (finish - interval_start))
                        interval_start = time.time()
                    
                    else:
                        #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                        print('f1 or f2 is none why')
                        return
                           
                else: #TODO
                    print('starting at a input point within in face')
                    #TODO, split this off, thanks
                    #TODO, generalize to the CCW cycle finding, not assuming 2 link segments
                    ip_chains = []
                    
                    interval_start = time.time()
                    
                    for seg in ip.link_segments:  #go each direction from Input Point on both of it's segments
                        current_seg = seg
                        chain = []
                        ip_next = current_seg.other_point(ip)
                        
                        if not ip_next.bmface.is_valid:
                            remap_input_point(ip_next)
        
                        seg_chain_start = time.time()
                        while ip_next and ip_next.bmface == ip.bmface:  #walk along the input segments as long as the next input point is on the same face
                            if ip_next in ip_set:  #we remove it here only if its on the same face
                                ip_set.remove(ip_next)
                        
                            chain += [ip_next]
                            
                            next_seg_start  = time.time()
                            next_seg = next_segment(ip_next, current_seg)
                            
                            next_seg_finish = time.time()
                            print('next segment %f' % (next_seg_finish - next_seg_start))
                            
                            if next_seg == None: 
                                print('there is no next seg we ended on edge of mesh?')
                                break
                        
                            ip_next = next_seg.other_point(ip_next)
                            if not ip_next.bmface.is_valid:
                                remap_input_point(ip_next)
                            
                            if ip_next.is_edgepoint(): 
                                print('we broke on an endpoint')
                                ip_set.remove(ip_next)
                                break
                            current_seg = next_seg

                        seg_chain_finish = time.time()
                        print('found segment chain in %f seconds' % (seg_chain_finish-seg_chain_start))
                        ip_chains += [chain]
                        

                        if current_seg not in completed_segments:  #here is some time, process as we go
                            process_start = time.time()
                            result = process_segment(current_seg)
                            process_finish = time.time()
                            print('processed a new segment in %f seconds' % (process_finish-process_start))
                        elif current_seg not in self.cut_data:
                            print('Current segment is not in cut data')
                            current_seg.bad_segment = True
                            return
                            
                        if current_seg in self.cut_data:
                            cdata = self.cut_data[current_seg]
                        else:
                            print('there is no cdata for this')
                            cdata = None
                            
                        #if this is first segment, we define that as the entrance segment   
                        if seg == ip.link_segments[0]:
                            if ip_next.is_edgepoint() and cdata == None:
                                bmv_enter = self.ip_bmvert_map[ip_next]
                                ed_enter = ip_next.seed_geom #TODO, make this seed_edge, seed_vert or seed_face
                            else:
                                if current_seg.ip0 == ip_next: #meaning ip_current == ip1  #test the direction of the segment
                                    if current_seg not in self.cut_data:
                                        print('ABOUT TO BE AN ERROR!')
                                        self.the_bad_segment = current_seg
                                        return
                                    
                                    ed_enter = self.cut_data[current_seg]['edge_crosses'][-1]  #TODO error here some time
                                    print('IP_1 of he input segment entering the face')
                                    if ed_enter in self.reprocessed_edge_map:
                                        ed_enter = self.reprocessed_edge_map[ed_enter]
                                        print('a reprocessed edge')
                                        #print(ed_enter)
                                else:
                                    ed_enter = self.cut_data[current_seg]['edge_crosses'][0]
                                    print('IP_0 of the input segment entering the face')
                                    if ed_enter in self.reprocessed_edge_map:
                                        ed_enter = self.reprocessed_edge_map[ed_enter]
                                        print('a reprocessed edge')
                                        #print(ed_enter)
                                bmv_enter = self.cut_data[current_seg]['bmedge_to_new_bmv'][ed_enter]
                        

                        #the other direction, will find the exit segment.
                        else:
                            if ip_next.is_edgepoint() and cdata == None:
                                print('getting the edgepoint IP bmvert')
                                bmv_exit = self.ip_bmvert_map[ip_next]
                                ed_exit = ip_next.seed_geom
                            else:
                                if current_seg.ip0 == ip_next:  #test the direction of the segment
                                    #ed_exit = self.cut_data[current_seg]['edge_crosses'][0]
                                    ed_exit = self.cut_data[current_seg]['edge_crosses'][-1]
                                    if ed_exit in self.reprocessed_edge_map:
                                        ed_exit = self.reprocessed_edge_map[ed_exit]
                                        print('a reprocessed edge')
                                        #print(ed_exit)
                                        
                                    print('IP_1 of the input segment exiting the face')
                                else:
                                    #ed_exit = self.cut_data[current_seg]['edge_crosses'][-1]
                                    if current_seg not in self.cut_data:
                                        print('ABOUT TO BE AN ERROR!')
                                        self.the_bad_segment = current_seg
                                        return
                                    
                                    ed_exit = self.cut_data[current_seg]['edge_crosses'][0] #TODO AGAIN SOMETIMES HERE AN ERROR
                                    
                                    if ed_exit in self.reprocessed_edge_map:
                                        ed_exit = self.reprocessed_edge_map[ed_exit]
                                        print('a reprocessed edge')
                                        #print(ed_exit)
                                    print('IP_0 of the input segment exiting the face')   
                            
                                bmv_exit = self.cut_data[current_seg]['bmedge_to_new_bmv'][ed_exit]
                            
                    ip_chains[0].reverse()
                    total_chain = ip_chains[0] + [ip] + ip_chains[1]
                    
                    bmvert_chain  = [bmv_enter] + [self.ip_bmvert_map[ipc] for ipc in total_chain] + [bmv_exit]

                    finish = time.time()
                    print('found the IPsegment loop %f seconds' % (finish - interval_start))
                    interval_start = time.time()
                    
                    
                    #print(ed_enter, ed_exit)
                    
                    interval_start = time.time()
                    if len(bmvert_chain) != len(set(bmvert_chain)):
                        print('we have duplicates')
                        print(bmvert_chain)
                    else: 
                        interval_start = time.time()   
                        self.input_net.bme.verts.ensure_lookup_table()
                        self.input_net.bme.edges.ensure_lookup_table()
                        self.input_net.bme.faces.ensure_lookup_table()  

                        finish = time.time()
                        print('updated lookup tables %f' % (finish-interval_start))
                        interval_start = time.time()
                        
                        f = ip.bmface
                        f1, f2 = split_face_by_verts(self.input_net.bme, f, ed_enter, ed_exit, bmvert_chain)
                        
                        finish = time.time()
                        print('split the face %f' % (finish-interval_start))
                        interval_start = time.time()
                        
                        if f1 == None or f2 == None:
                            #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
                            return
                            #continue 
                        new_to_old_face_map[f1] = f
                        new_to_old_face_map[f2] = f
                        old_to_new_face_map[f] = [f1, f2]
                        if f not in new_to_old_face_map:
                            original_face_indices[f.index] = f
                        
                        geom_clean_start = time.time()
                        #bmesh.ops.delete(self.input_net.bme, geom = [f], context = 3)
                        self.input_net.bme.faces.remove(f)
                        
                        del_eds = [ed for ed in [ed_enter, ed_exit] if len(ed.link_faces) == 0]
                        del_eds = list(set(del_eds))
                        #bmesh.ops.delete(self.input_net.bme, geom = del_eds, context = 4)
                        for ed in del_eds:
                            self.input_net.bme.edges.remove(ed)
                        geom_clean_finish = time.time()
                        print('delete old face and edges in %f seconds' % (geom_clean_finish - geom_clean_start))
                    finish = time.time()
                    print('split IP face in %f seconds' % (finish - start)) 
        
        
        #now collect all the newly created edges which represent the cycle boundaries
        perim_edges = set()    
        for ed in self.input_net.bme.edges: #TODO, is there a faster way to collect these edges from the strokes? Yes
            if ed.verts[0] in new_bmverts and ed.verts[1] in new_bmverts:
                perim_edges.add(ed)

        high_genus_verts = set()    
        for v in self.input_net.bme.verts: 
            if v in new_bmverts: 
                if len([ed for ed in v.link_edges if ed in perim_edges]) >2:
                    high_genus_verts.add(v)
                    
        print('there aer %i high genus verts' % len(high_genus_verts))  #this method will fail in the case of a diamond on 4 adjacent quads.   
        for v in high_genus_verts:
            for ed in v.link_edges:
                if ed.other_vert(v) in high_genus_verts:
                    if ed in perim_edges:
                        perim_edges.remove(ed)

        self.boundary_edges = perim_edges             
        #self.input_net.bme.verts.ensure_lookup_table()
        #self.input_net.bme.edges.ensure_lookup_table()
        #self.input_net.bme.faces.ensure_lookup_table()    
        #self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
        knife_finish = time.time()
        print('\n')
        print('Executed the cut in %f seconds' % (knife_finish - knife_sart))
        return    
        
    
    

            
    def find_patch_post_cut(self, face_ind, world_loc, local_loc):
        '''
        selects a FacePatch based on "hovered mesh" data
        '''
        #dictionaries to map newly created faces to their original faces and vice versa
        old_to_new_face_map = self.old_to_new_face_map
             
        def find_newest_faces(old_f, max_iters = 5):
            '''
            '''    
            if old_f not in old_to_new_face_map: return []
            
            iters = 0
            child_fs = old_to_new_face_map[old_f]
            newest_faces = []
            
            if not any([f in old_to_new_face_map for f in child_fs]):
                return child_fs
            
            while iters < max_iters and any([f in old_to_new_face_map for f in child_fs]):
                iters += 1
                next_gen = []
                for f in child_fs:
                    if f in old_to_new_face_map:
                        next_gen += old_to_new_face_map[f]
                
                    else:
                        newest_faces += [f]
                        
                    print(f)
                print(next_gen)
                child_fs = next_gen
                
            #new_fs = old_to_new_face_map[old_f]
                
            return newest_faces  
        
        def find_new_faces(old_f, max_iters = 5):
            '''
            TODO, may want to only find NEWEST
            faces
            '''    
            if old_f not in old_to_new_face_map: return []
            
            iters = 0
            new_fs = []
            
            child_fs = old_to_new_face_map[old_f]
            new_fs += child_fs
            while iters < max_iters and len(child_fs):
                iters += 1
                next_gen = []
                for f in child_fs:
                    if f in old_to_new_face_map:
                        next_gen += old_to_new_face_map[f] #this is always a pair
                
                new_fs += next_gen
                child_fs = next_gen
                
            
            #new_fs = old_to_new_face_map[old_f]
                
            return new_fs    
        
        #print(self.original_indices_map)
        
        #first, BVH gives us a face index, but we have deleted all the faces and created new ones
        
        f = None
        if face_ind in self.original_indices_map:
            print('found an old face that was split')
            old_f = self.original_indices_map[face_ind]
            fs_new = find_newest_faces(old_f, max_iters = 5)
            for new_f in fs_new:
                if bmesh.geometry.intersect_face_point(new_f, local_loc):
                    print('found the new face that corresponds')
                    f = new_f
                
        else:
            self.input_net.bme.faces.ensure_lookup_table()
            self.input_net.bme.verts.ensure_lookup_table()
            self.input_net.bme.edges.ensure_lookup_table()
            
            f = self.old_face_indices[face_ind]
            #f = self.input_net.bme.faces[face_ind]
            
        if f == None:
            print('failed to find the new face')
            return None
        
        for patch in self.face_patches:
            if f in patch.patch_faces:  #just change the color but don't add a duplicate
                return patch
                            
        return None
      
    
    
        
    def add_seed(self, face_ind, world_loc, local_loc):
        
        if self.knife_complete:
            self.add_seed_post_cut(face_ind, world_loc, local_loc)
        else:
            self.add_seed_pre_cut(face_ind, world_loc, local_loc)
            
            
    def add_seed_post_cut(self, face_ind, world_loc, local_loc):
        #dictionaries to map newly created faces to their original faces and vice versa
        old_to_new_face_map = self.old_to_new_face_map
        
    
        if "patches" not in self.input_net.bme.loops.layers.color:
            vcol_layer = self.input_net.bme.loops.layers.color.new("patches")
        else:
            vcol_layer = self.input_net.bme.loops.layers.color["patches"]
            
            
        def find_newest_faces(old_f, max_iters = 5):
            '''
            '''    
            if old_f not in old_to_new_face_map: return []
            
            iters = 0
            child_fs = old_to_new_face_map[old_f]
            newest_faces = []
            
            if not any([f in old_to_new_face_map for f in child_fs]):
                return child_fs
            
            while iters < max_iters and any([f in old_to_new_face_map for f in child_fs]):
                iters += 1
                next_gen = []
                for f in child_fs:
                    if f in old_to_new_face_map:
                        next_gen += old_to_new_face_map[f]
                
                    else:
                        newest_faces += [f]
                        
                    print(f)
                print(next_gen)
                child_fs = next_gen
                
            #new_fs = old_to_new_face_map[old_f]
                
            return newest_faces  
        
        def find_new_faces(old_f, max_iters = 5):
            '''
            TODO, may want to only find NEWEST
            faces
            '''    
            if old_f not in old_to_new_face_map: return []
            
            iters = 0
            new_fs = []
            
            child_fs = old_to_new_face_map[old_f]
            new_fs += child_fs
            while iters < max_iters and len(child_fs):
                iters += 1
                next_gen = []
                for f in child_fs:
                    if f in old_to_new_face_map:
                        next_gen += old_to_new_face_map[f] #this is always a pair
                
                new_fs += next_gen
                child_fs = next_gen
                
            
            #new_fs = old_to_new_face_map[old_f]
                
            return new_fs    
        
        #print(self.original_indices_map)
        
        #first, BVH gives us a face index, but we have deleted all the faces and created new ones
        f = None
        if face_ind in self.original_indices_map:
            print('found an old face that was split')
            old_f = self.original_indices_map[face_ind]
            fs_new = find_newest_faces(old_f, max_iters = 5)
            for new_f in fs_new:
                if bmesh.geometry.intersect_face_point(new_f, local_loc):
                    print('found the new face that corresponds')
                    f = new_f
                
        else:
            self.input_net.bme.faces.ensure_lookup_table()
            self.input_net.bme.verts.ensure_lookup_table()
            self.input_net.bme.edges.ensure_lookup_table()
            
            f = self.old_face_indices[face_ind]
            #f = self.input_net.bme.faces[face_ind]
            
        if f == None:
            print('failed to find the new face')
            return
        
        
        for patch in self.face_patches:
            if f in patch.patch_faces:  #just change the color but don't add a duplicate
                patch.set_color(get_random_color())
                patch.color_patch()
                return
                            
        new_patch = BMFacePatch(f, local_loc, world_loc, vcol_layer, get_random_color())
        new_patch.grow_seed(self.input_net.bme, self.boundary_edges)
        new_patch.color_patch()
        self.face_patches += [new_patch]
        
        #self.update_spline_edited_patches(self.spline_net)
        
        print(new_patch.spline_net_segments)
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)


    def add_seed_pre_cut(self, face_ind, world_loc, local_loc):
        '''
        to be used when painting/corse patches before
        knife_geometry has committed geometry chagnes to BMesh
        '''
    
        if "patches" not in self.input_net.bme.loops.layers.color:
            vcol_layer = self.input_net.bme.loops.layers.color.new("patches")
        else:
            vcol_layer = self.input_net.bme.loops.layers.color["patches"]
            
            
        f= self.net_ui_context.bme.faces[face_ind]  
        
        for patch in self.face_patches:
            if f in patch.patch_faces:  #just change the color but don't add a duplicate
                patch.set_color(get_random_color())
                patch.color_patch()
                return
                            
        new_patch = BMFacePatch(f, local_loc, world_loc, vcol_layer, get_random_color())
        new_patch.grow_seed_faces(self.input_net.bme, self.boundary_faces)
        new_patch.color_patch()
        self.face_patches += [new_patch]
        
        
        self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
    
    
    def add_patch_start_paint(self, face_ind, world_loc, local_loc):
        if "patches" not in self.input_net.bme.loops.layers.color:
            vcol_layer = self.input_net.bme.loops.layers.color.new("patches")
        else:
            vcol_layer = self.input_net.bme.loops.layers.color["patches"]
            
            
        f= self.net_ui_context.bme.faces[face_ind]                   
        new_patch = BMFacePatch(f, local_loc, world_loc, vcol_layer, get_random_color())
        self.face_patches += [new_patch]
        self.active_patch = new_patch
                 
class InputPoint(object):  # NetworkNode
    '''
    Representation of an input point
    '''
    def __init__(self, world, local, view, face_ind, seed_geom = None, bmface = None, bmedge = None, bmvert = None):
        self.world_loc = world
        self.local_loc = local
        self.view = view
        self.face_index = face_ind
        self.link_segments = []

        #Mapping to source BMesh Geometry
        self.seed_geom = seed_geom #UNUSED, but will be needed if input point exists on an EDGE or VERT in the source mesh

        self.bmface = bmface
        self.bmedge = bmedge
        self.bmvert = bmvert
        
        #Mapping to Curve Network?
        self.spline = None  #Type SplineSegment, will not be none if IP was generated by Spline tessellation
        self.node = None #Type InputNode  Will exist if is equivalent to InputNode
        
    def is_endpoint(self):
        if self.seed_geom and self.num_linked_segs > 0: return False  #TODO, better system to delinate edge of mesh
        if self.num_linked_segs < 2: return True # What if self.linked_segs == 2 ??

    def is_edgepoint(self):
        '''
        defines whether this InputPoint lies on the non_manifold edge 
        of the source mesh
        '''
        if isinstance(self.seed_geom, bmesh.types.BMEdge):
            return True
        else:
            return False

    def num_linked_segs(self): return len(self.link_segments)

    is_endpoint = property(is_endpoint)

    num_linked_segs = property(num_linked_segs)

    def set_world_loc(self, loc): self.world_loc = loc
    def set_local_loc(self, loc): self.local_loc = loc
    def set_view(self, view): self.view = view
    def set_face_ind(self, face_ind): self.face_index = face_ind

    def set_values(self, world, local, view, face_ind):
        self.world_loc = world
        self.local_loc = local
        self.view = view
        self.face_index = face_ind

    def set_data(self, data):
        for key in data:
            if hasattr(self, key):
                setattr(self, key, data[key])
             
    #note, does not duplicate connectivity data
    def duplicate(self): return InputPoint(self.world_loc, self.local_loc, self.view, self.face_index)

    def duplicate_data(self):
        data = {}
        data["world_loc"] = self.world_loc
        data["local_loc"] = self.local_loc
        data["view"] = self.view
        data["face_index"] = self.face_index
        data["seed_geom"] = self.seed_geom
        data["bmface"] = self.bmface
        data["bmedge"] = self.bmedge
        data["bmvert"] = self.bmvert
        
        return data
    
    def are_connected(self, point):
        '''
        takes another input point, and returns InputSegment if they are connected
        returns False if they are not connected
        '''
        for seg in self.link_segments:
            if seg.other_point(self) == point:
                return seg
            
        return False

    def print_data(self): # for debugging
        print('\n', "POINT DATA", '\n')
        print("world location:", self.world_loc, '\n')
        print("local location:", self.local_loc, '\n')
        print("view direction:", self.view, '\n')
        print("face index:", self.face_index, '\n')
        
    def validate_bme_references(self):
        
        if self.bmvert and self.bmvert.is_valid:
            bmvalid = True
        elif self.bmvert == None:
            bmvalid = True   
        else:
            bmvalid = False
            
        if self.bmedge and self.bmedge.is_valid:
            bmedvalid = True
        elif self.bmedge == None:
            bmedvalid = True   
        else:
            bmedvalid = False
            
        if self.bmvert and self.bmvert.is_valid:
            bmvalid = True
        elif self.bmver == None:
            bmvalid = True   
        else:
            bmvalid = False    

##########################################
#Input Segment ToDos
#TODO - method to clean segments with unused Input Points

##########################################
class InputSegment(object): #NetworkSegment
    '''
    Representation of a cut between 2 input points
    Equivalent to an "edge" in a mesh connecting to verts
    '''
    def __init__(self, ip0, ip1):
        self.ip0 = ip0
        self.ip1 = ip1
        self.points = [ip0, ip1]
        self.path = []  #list of 3d points for previsualization
        self.bad_segment = False
        ip0.link_segments.append(self)
        ip1.link_segments.append(self)

        self.face_chain = []   #TODO, get a better structure within Network Cutter

        #Network Cutter Flags
        self.calculation_complete = False #this is a NetworkCutter Flag
        self.needs_calculation = True
        self.cut_method = 'NONE'
        
        
        #SplineNetwork References
        self.parent_spline = None #will be a SplineSegment if set
        
    def is_bad(self): return self.bad_segment
    is_bad = property(is_bad)

    def other_point(self, p):
        if p not in self.points: return None
        return self.ip0 if p == self.ip1 else self.ip1

    def detach(self):
        #TODO safety?  Check if in ip0.link_sgements?
        self.ip0.link_segments.remove(self)
        self.ip1.link_segments.remove(self)
    
class InputNetwork(object): #InputNetwork
    '''
    Data structure that stores a set of InputPoints that are
    connected with InputSegments.

    InputPoints store a mapping to the source mesh.
    InputPoints and Input segments, analogous to Verts and Edges

    Collection of all InputPoints and Input Segments
    '''
    def __init__(self, net_ui_context, ui_type="DENSE_POLY"):
        self.net_ui_context = net_ui_context
        self.net_ui_context.set_network(self)
        #self.bvh = self.net_ui_context.bvh   #this should go into net context.  DONE
        self.bme = self.net_ui_context.bme  #the network exists on the BMesh, it is fundamental
        self.points = []
        self.segments = []  #order not important, but maintain order in this list for indexing?

    def is_empty(self): return (not(self.points or self.segments))
    def num_points(self): return len(self.points)
    def num_segs(self): return len(self.segments)
    is_empty = property(is_empty)
    num_points = property(num_points)
    num_segs = property(num_segs)

    def point_world_locs(self): return [p.world_loc for p in self.points]
    def point_local_locs(self): return [p.local_loc for p in self.points]
    def point_views(self): return [p.view for p in self.points]
    def point_face_indices(self): return [p.face_index for p in self.points]
    point_world_locs = property(point_world_locs)
    point_local_locs = property(point_local_locs)
    point_views = property(point_views)
    point_face_indices = property(point_face_indices)

    def create_point(self, world_loc, local_loc, view, face_ind):
        ''' create an InputPoint '''
        self.points.append(InputPoint(world_loc, local_loc, view, face_ind, bmface = self.bme.faces[face_ind]))
        return self.points[-1]

    def connect_points(self, p1, p2, make_path=True):
        ''' connect 2 points with a segment '''
        seg = InputSegment(p1, p2)
        self.segments.append(seg)
        return seg
    
    def disconnect_points(self, p1, p2):
        seg = self.are_connected(p1, p2)
        if seg:
            self.segments.remove(seg)
            p1.link_segments.remove(seg)
            p2.link_segments.remove(seg)

    def remove_segment(self, seg):
        if seg in self.segments:
            self.segments.remove(seg)
        
        #remove references in the IPs
        #occasionally has been removed if adjacent point already gone
        if seg in seg.ip0.link_segments:
            seg.ip0.link_segments.remove(seg)
        if seg in seg.ip1.link_segments:
            seg.ip1.link_segments.remove(seg)
        
        
    def are_connected(self, p1, p2): #TODO: Needs to be in InputPoint 
        ''' Sees if 2 points are connected, returns connecting segment if True '''
        for seg in p1.link_segments:
            if seg.other_point(p1) == p2:
                return seg
        return False

    def connected_points(self, p):
        return [seg.other_point(p) for seg in p.link_segments]

    def insert_point(self, new_p, seg):
        p1 = seg.ip0
        p2 = seg.ip1
        self.disconnect_points(p1,p2)
        self.connect_points(p1, new_p)
        self.connect_points(p2, new_p)

    def remove_point(self, point, disconnect = False):
        connected_points = self.connected_points(point)
        for cp in connected_points:
            self.disconnect_points(cp, point)

        if len(connected_points) == 2 and not disconnect:
            self.connect_points(connected_points[0], connected_points[1])

        self.points.remove(point)

    def duplicate(self):
        new = InputNetwork(self.source_ob)
        new.points = self.points
        new.segments = self.segments
        return new

    def get_endpoints(self):
        #maybe later...be smart and carefully add/remove endpoints
        #as they are inserted/created/removed etc
        #probably not necessary
        endpoints = [ip for ip in self.points if ip.is_endpoint] #TODO self.endpoints?
        
        return endpoints
    
    
    def get_edgepoints(self):
        
        edge_points = [ip for ip in self.points if ip.is_edgepoint()]
        
        return edge_points
     
    def find_network_cycles(self):  #TODO
        #this is the equivalent of "edge_loops"
        #TODO, mirror the get_cycle method from polystrips
        #right now ther eare no T or X junctions, only cuts across mesh or loops within mesh
        #will need to implement "IputNode.get_segment_to_right(InputSegment) to take care this
        
        print('INPUT NETWORK CYCLES')
        ip_set = set(self.points)
        endpoints = set(self.get_endpoints())
        
        closed_edgepoints = set(self.get_edgepoints()) - endpoints
        
        
        print('There are %i endpoints' % len(endpoints))
        print('there are %i input points' % len(ip_set))
        print('there are %i closed edge_points' % len(closed_edgepoints))
        
        unclosed_ip_cycles = []
        unclosed_seg_cycles = []
        
        def next_segment(ip, current_seg): #TODO Code golf this
            if len(ip.link_segments) != 2: return None  #TODO, the the segment to right
            return [seg for seg in ip.link_segments if seg != current_seg][0]
              
        while len(endpoints):
            current_ip = endpoints.pop()
            ip_start = current_ip
            ip_set.remove(current_ip)
            
            node_cycle = [current_ip]
            if len(current_ip.link_segments) == 0: continue #Lonely Input Point, ingore it
            
            current_seg = current_ip.link_segments[0]
            seg_cycle = [current_seg]
            
            while current_seg:
                next_ip = current_seg.other_point(current_ip)  #always true
                
                if next_ip == ip_start: break  #we have found the end, no need to get the next segment
                
                #take care of sets
                if next_ip in ip_set: ip_set.remove(next_ip)
                if next_ip in endpoints: endpoints.remove(next_ip)
                node_cycle += [next_ip]
                
                #find next segment
                next_seg = next_segment(next_ip, current_seg)
                if not next_seg:  break  #we have found an endpoint
                seg_cycle += [next_seg]
               
                #reset variable for next iteration
                current_ip = next_ip
                current_seg = next_seg
                
            unclosed_ip_cycles += [node_cycle] 
            unclosed_seg_cycles += [seg_cycle] 
         
            
        print('there are %i unclosed cycles' % len(unclosed_ip_cycles))
        print('there are %i ip points in ip set' % len(ip_set))
        for i, cyc in enumerate(unclosed_ip_cycles):
            print('There are %i nodes in %i unclosed cycle' % (len(cyc), i))
        
        ip_cycles = []
        seg_cycles = []   #<<this basicaly becomes a PolyLineKine
        while len(ip_set):
            
            if len(closed_edgepoints):  #this makes sure we start with a closed edge point
                current_ip = closed_edgepoints.pop()
                ip_set.remove(current_ip)
            else:
                current_ip = ip_set.pop()
            
            ip_start = current_ip
                
            node_cycle = [current_ip]
            if len(current_ip.link_segments) == 0: continue #Lonely Input Point, ingore it
            
            current_seg = current_ip.link_segments[0]
            seg_cycle = [current_seg]
            
            while current_seg:
                next_ip = current_seg.other_point(current_ip)  #always true
                
                if next_ip == ip_start: break  #we have found the end, no need to get the next segment
                
                #take care of sets
                if next_ip in ip_set: ip_set.remove(next_ip)  #<-- i what circumstance would this not be true?
                if next_ip in closed_edgepoints: closed_edgepoints.remove(next_ip)
                node_cycle += [next_ip]
                
                #find next segment
                next_seg = next_segment(next_ip, current_seg)
                if not next_seg:  break  #we have found an endpoint
                seg_cycle += [next_seg]
               
                #reset variable for next iteration
                current_ip = next_ip
                current_seg = next_seg
                
            ip_cycles += [node_cycle] 
            seg_cycles += [seg_cycle] 
        
        
        print('there are %i closed seg cycles' % len(seg_cycles))
        for i, cyc in enumerate(ip_cycles):
            print('There are %i nodes in %i closed cycle' % (len(cyc), i))
        
        return ip_cycles, seg_cycles
    
    
class CurveNode(object):  # CurveNetworkNode, basically identical to InputPoint
    '''
    Representation of an input point
    '''
    def __init__(self, world, local, view, face_ind, seed_geom = None, bmface = None, bmedge = None, bmvert = None):
        self.world_loc = world
        self.local_loc = local
        self.view = view
        self.face_index = face_ind
        self.link_segments = []
        self.input_point = None
    
        #dictionary mapping handle to link_segments
        self.handles = {}
        
        #SETTING UP FOR MORE COMPLEX MESH CUTTING    ## SHould this exist in InputPoint??
        self.seed_geom = seed_geom #UNUSED, but will be needed if input point exists on an EDGE or VERT in the source mesh

        self.bmface = bmface
        self.bmedge = bmedge
        self.bmvert = bmvert
        
    def spawn_input_point(self, input_network):
        if self.input_point and self.input_point in input_network.points: return  #don't duplicate
        
        ip = InputPoint(self.world_loc, 
                        self.local_loc, 
                        self.view, 
                        self.face_index, 
                        self.seed_geom, 
                        bmface = self.bmface,
                        bmedge = self.bmedge,
                        bmvert = self.bmvert)
        
        input_network.points.append(ip)
        self.input_point = ip
        
    
    def update_input_point(self, input_network):
        if self.input_point == None:
            self.spawn_input_point(input_network)
            
        self.input_point.set_data(self.duplicate_data())    
    
    def clear_input_net_references(self, input_network):
        if self.input_point in input_network.points:
            input_network.remove_point(self.input_point, disconnect = True)
        
                
    def is_endpoint(self):
        if self.is_edgepoint() and self.num_linked_segs > 0: return False
        if self.num_linked_segs < 2: return True # What if self.linked_segs == 2 ??

    def is_edgepoint(self):
        '''
        defines whether this InputPoint lies on the non_manifold edge 
        of the source mesh
        '''
        if isinstance(self.seed_geom, bmesh.types.BMEdge):
            return True
        else:
            return False

    def num_linked_segs(self): return len(self.link_segments)

    is_endpoint = property(is_endpoint)

    num_linked_segs = property(num_linked_segs)

    def set_world_loc(self, loc): self.world_loc = loc
    def set_local_loc(self, loc): self.local_loc = loc
    def set_view(self, view): self.view = view
    def set_face_ind(self, face_ind): self.face_index = face_ind

    def set_values(self, world, local, view, face_ind):
        self.world_loc = world
        self.local_loc = local
        self.view = view
        self.face_index = face_ind

    def set_data(self, data):
        for key in data:
            if hasattr(self, key):
                setattr(self, key, data[key])
                
    def calc_handles(self):
        #TODO, consider plane fit to all connecting points?
        if len(self.link_segments) != 2:
            for seg in self.link_segments:
                other = seg.other_point(self)
                v = other.world_loc - self.world_loc
                self.handles[seg] = self.world_loc + 1/3 * v  #TODO coefficient for this?
        else:
            seg0, seg1 =  self.link_segments[0],  self.link_segments[1]
            n0, n1 = seg0.other_point(self), seg1.other_point(self)
            
            r0 = (n0.world_loc - self.world_loc).length
            r1 = (n1.world_loc - self.world_loc).length

            tangent = n1.world_loc - n0.world_loc
            tangent.normalize()
            
            self.handles[seg0] = self.world_loc - r0/3 * tangent
            self.handles[seg1] = self.world_loc + r1/3 * tangent
            
        #TODO if self.handles == 4  #Hold this code until we have more compelex structure
            #calc handles 0/2 as smooth (tangent)
            #calc handles 1/3 as smooth (tangent)
            #ASSUMES SEGMENTS SORTED CCW AROUND
            #seg0, seg1, seg2, seg3 =  self.segments_ccw()
            
            #n0, n2 = seg0.other_poitn(self), seg2.other_point(self)
            
            #r0 = (n0.world_loc - self.world_loc).length
            #r2 = (n2.world_loc - self.world_loc).length

            #tangent = n1.world_loc - n0.world_loc
            #tangent.normalize()
            
            #self.handles[seg0] = self.world_loc + r0/3 * tangent
            #self.handles[seg2] = self.world_loc + r2/3 * tangent
            
            
            #n1, n3 = seg1.other_poitn(self), seg3.other_point(self)
            
            #r1 = (n1.world_loc - self.world_loc).length
            #r3 = (n3.world_loc - self.world_loc).length

            #tangent = n3.world_loc - n1.world_loc #tangent points 1 to 3
            #tangent.normalize()
            
            #self.handles[seg1] = self.world_loc - r1/3 * tangent
            #self.handles[seg3] = self.world_loc + r3/3 * tangent
    
    def calc_handles_vector(self):
        '''
        handle pointing directly at next node
        '''
        for seg in self.link_segments:
            other = seg.other_point(self)
            v = other.world_loc - self.world_loc
            self.handles[seg] = self.world_loc + 1/3 * v
               
    def update_splines(self):
        for seg in self.link_segments:
            seg.calc_bezier()
            seg.tessellate()
            seg.tessellate_IP_error(.1)
            seg.is_inet_dirty = True
              
    #note, does not duplicate connectivity data
    def duplicate(self): return InputPoint(self.world_loc, self.local_loc, self.view, self.face_index)

    def duplicate_data(self):
        data = {}
        data["world_loc"] = self.world_loc
        data["local_loc"] = self.local_loc
        data["view"] = self.view
        data["face_index"] = self.face_index
        data["seed_geom"] = self.seed_geom
        data["bmface"] = self.bmface
        data["bmedge"] = self.bmedge
        data["bmvert"] = self.bmvert
        
        return data
    
    def are_connected(self, point):
        '''
        takes another input point, and returns InputSegment if they are connected
        returns False if they are not connected
        '''
        for seg in self.link_segments:
            if seg.other_point(self) == point:
                return seg
            
        return False

    def print_data(self): # for debugging
        print('\n', "POINT DATA", '\n')
        print("world location:", self.world_loc, '\n')
        print("local location:", self.local_loc, '\n')
        print("view direction:", self.view, '\n')
        print("face index:", self.face_index, '\n')
        
    def validate_bme_references(self):
        
        if self.bmvert and self.bmvert.is_valid:
            bmvalid = True
        elif self.bmvert == None:
            bmvalid = True   
        else:
            bmvalid = False
            
        if self.bmedge and self.bmedge.is_valid:
            bmedvalid = True
        elif self.bmedge == None:
            bmedvalid = True   
        else:
            bmedvalid = False
            
        if self.bmvert and self.bmvert.is_valid:
            bmvalid = True
        elif self.bmver == None:
            bmvalid = True   
        else:
            bmvalid = False    

##########################################
#Input Segment ToDos
#TODO - method to clean segments with unused Input Points

##########################################
class SplineSegment(object): #NetworkSegment
    '''
    Representation of a connection between 2 curve nodes
    Interpolated by a Cubic Bezier Spline
    '''
    def __init__(self, n0, n1):
        self.n0 = n0
        self.n1 = n1
        self.points = [n0, n1]
        self.path = []  #list of 3d points for previsualization
        self.bad_segment = False
        n0.link_segments.append(self)
        n1.link_segments.append(self)


        self.cb = None #CubicBezier
        #Calculation, Tessellation and update flags here

        self.input_points = []  #mapping to the tesselated InputPoints
        self.input_segments = []  #mapping to the tesselated InputSegments
        self.is_inet_dirty = False  #flag when needs to be re-tesslated and
        
        self.draw_tessellation = []  #higher res tesselation for draw and for furthe use
        self.ip_tesselation = []  #error based or length based tesselation to create InputPoints
        self.ip_views = []  #interpolated view_direction from n0 to n1
        
    def is_bad(self): return self.bad_segment
    is_bad = property(is_bad)

    def other_point(self, p):
        if p not in self.points: return None
        return self.n0 if p == self.n1 else self.n1

    def detach(self):
        #TODO safety?  Check if in ip0.link_sgements?
        self.ip0.link_segments.remove(self)
        self.ip1.link_segments.remove(self)
    
    def calc_bezier(self):
        if self not in self.n0.handles:
            self.n0.calc_handles()
        if self not in self.n1.handles:
            self.n1.calc_handles()
        p0 = self.n0.world_loc
        p1 = self.n0.handles[self]
        p2 = self.n1.handles[self]
        p3 = self.n1.world_loc
        
        self.cb = CubicBezier(p0, p1, p2, p3)
    
    def tessellate(self):
        
        if self.cb == None: return
        
        self.cb.tessellate_uniform(lambda p,q:(p-q).length, split=30)  #INITIAL TESSELATION
        #L = cbs.approximate_totlength_tessellation()
        #n = L/2  #2mm spacing long strokes?
        self.draw_tessellation = [pt.as_vector() for i,pt,d in self.cb.tessellation]
        #print('there are %i points in draw_tesselation' % len(self.draw_tessellation))
    
    def tessellate_IP_error(self, error):
        '''
        Used RDP simplification on the draw_tess
        '''
        if len(self.draw_tessellation) == 0:
            self.tessellate()
            
        
        feature_inds = simplify_RDP(self.draw_tessellation, error)
        
        self.ip_tesselation = []
        self.ip_views = []
        
        for ind in feature_inds:
            self.ip_tesselation += [self.draw_tessellation[ind]]
            blend = ind/(len(self.draw_tessellation) - 1)
            self.ip_views += [self.n0.view.lerp(self.n1.view, blend)]
    
        self.is_inet_dirty = True
        
    def clear_input_net_references(self, input_network):
        for seg in self.input_segments:
            input_network.remove_segment(seg)
            #for ip in seg.points:  #THIS IS THE CULPRIT BECUASE OPEN ENDED SEGMENTS GOT ENDPOINTS REMOVED
                #if len(ip.link_segments) == 0 and ip in input_network.points:
                #    input_network.remove_point(ip)
               
        for ip in self.input_points:
            if ip in input_network.points:
                input_network.remove_point(ip, disconnect = True)
                        
    def convert_tessellation_to_network(self, net_ui_context, input_network):
        """
        The reason SplineNet does not have a self reference to InputNet
        is because SplineNet is a more generic Class, that could be used
        independently of an InputNetwork.  I'm also not convinced this method
        shoould be here, vs a function in a higher level manager.  but the
        parent/child references are fundamental to how the overall system works.
        For now, this is stashed here.
        """
       
        #first clear out any existing tessellation
        self.clear_input_net_references(input_network)
        
        #get the CurveNodes and corresponding InputPoints
        if self.n0.input_point == None:
            self.n0.spawn_input_point(input_network)
        if self.n1.input_point == None:
            self.n1.spawn_input_point(input_network)
        
        self.input_points = []
        self.input_segments = []
        
        #now create new tesseation
        ip0 = self.n0.input_point
        ip1 = self.n1.input_point
        
        if len(self.ip_tesselation) <= 2:
            if not ip0.are_connected(ip1):
                seg = input_network.connect_points(ip0, ip1)
                self.input_segments += [seg]
                seg.parent_spline = self
            
            self.is_inet_dirty = False    
            return
        prev_pnt = ip0
        end_pnt = ip1
        mx = net_ui_context.mx
        imx = net_ui_context.imx
        for ind in range(1,len(self.ip_tesselation)-1):
            pt = self.ip_tesselation[ind]
            view = self.ip_views[ind]
            loc, no, face_ind, d = net_ui_context.bvh.find_nearest(imx * pt)
            f = input_network.bme.faces[face_ind]
            new_pnt = InputPoint(mx * loc, loc, view, face_ind, seed_geom = f, bmface = f)
            input_network.points.append(new_pnt)
            self.input_points += [new_pnt]
            
            #create segment, link the child/parent relationship and insert into network
            seg = InputSegment(prev_pnt,new_pnt)
            self.input_segments += [seg]
            seg.parent_spline = self
            input_network.segments.append(seg)
            
            prev_pnt = new_pnt
        
        seg = InputSegment(prev_pnt,end_pnt)
        seg.parent_spline = self
        self.input_segments += [seg]
        input_network.segments.append(seg)    
        self.is_inet_dirty = False
    
         
class SplineNetwork(object): #InputNetwork
    '''
    Data structure that stores a set of CurveNodes that are
    connected with SplineSegments.

    Curve Nodes have Equivalent InputPoints store a mapping to the source mesh.
    InputPoints and Input segments, analogous to Verts and Edges

    Collection of all InputPoints and Input Segments
    '''
    def __init__(self, net_ui_context, ui_type="DENSE_POLY"):
        self.net_ui_context = net_ui_context
        self.net_ui_context.set_network(self)
        #self.bvh = self.net_ui_context.bvh   #this should go into net context.  DONE
        self.bme = self.net_ui_context.bme  #the network exists on the BMesh, it is fundamental
        self.points = []
        self.segments = []  #order not important, but maintain order in this list for indexing?

    def is_empty(self): return (not(self.points or self.segments))
    def num_points(self): return len(self.points)
    def num_segs(self): return len(self.segments)
    is_empty = property(is_empty)
    num_points = property(num_points)
    num_segs = property(num_segs)

    def point_world_locs(self): return [p.world_loc for p in self.points]
    def point_local_locs(self): return [p.local_loc for p in self.points]
    def point_views(self): return [p.view for p in self.points]
    def point_face_indices(self): return [p.face_index for p in self.points]
    point_world_locs = property(point_world_locs)
    point_local_locs = property(point_local_locs)
    point_views = property(point_views)
    point_face_indices = property(point_face_indices)


    def push_to_input_net(self, net_ui_context, input_net, all_segs = False):
        
        for seg in self.segments:
            if seg.is_inet_dirty or all_segs:
                seg.convert_tessellation_to_network(net_ui_context, input_net)
        
    def create_point(self, world_loc, local_loc, view, face_ind):
        ''' create an InputPoint '''
        self.points.append(CurveNode(world_loc, local_loc, view, face_ind, bmface = self.bme.faces[face_ind]))
        return self.points[-1]

    def connect_points(self, p1, p2, make_path=True):
        ''' connect 2 points with a segment '''
        new_seg = SplineSegment(p1, p2)
        self.segments.append(new_seg)
        return new_seg
        #TODO  need to update auto handles for all affected adjacent splines
        
    def disconnect_points(self, p1, p2):
        seg = self.are_connected(p1, p2)
        if seg: 
            self.segments.remove(seg)
            p1.link_segments.remove(seg)
            p2.link_segments.remove(seg)

    def remove_segment(self, seg):
        '''
        delete segment but leave nodes
        '''
        if seg in self.segments:
            self.segments.remove(seg)
        
        #remove references in the IPs
        if seg in seg.n0.link_segments:
            seg.n0.link_segments.remove(seg)
            if len(seg.n0.link_segments) == 0 and seg.n0 in self.points:
                self.points.remove(seg.n0)
        if seg in seg.n1.link_segments:
            seg.n1.link_segments.remove(seg)
            if len(seg.n1.link_segments) == 0 and seg.n1 in self.points:
                self.points.remove(seg.n1)
        
        
    def are_connected(self, p1, p2): #TODO: Needs to be in InputPoint 
        ''' Sees if 2 points are connected, returns connecting segment if True '''
        for seg in p1.link_segments:
            if seg.other_point(p1) == p2:
                return seg
        return False

    def connected_points(self, p):
        return [seg.other_point(p) for seg in p.link_segments]

    def insert_point(self, new_p, seg):
        p1 = seg.n0
        p2 = seg.n1
        self.disconnect_points(p1,p2)
        self.connect_points(p1, new_p)
        self.connect_points(p2, new_p)


    def remove_point(self, point, disconnect = False):
        
        connected_points = self.connected_points(point)
        for cp in connected_points:
            self.disconnect_points(cp, point)

        if point in self.points:
            self.points.remove(point)
        
        if len(connected_points) == 2 and not disconnect:
            new_seg = self.connect_points(connected_points[0], connected_points[1])
        
        return connected_points
        
        
    #def duplicate(self):
    #    new = InputNetwork(self.source_ob)
    #    new.points = self.points
    #    new.segments = self.segments
    #    return new

    def get_endpoints(self):
        #maybe later...be smart and carefully add/remove endpoints
        #as they are inserted/created/removed etc
        #probably not necessary
        endpoints = [ip for ip in self.points if ip.is_endpoint] #TODO self.endpoints?
        return endpoints
    
    
    def get_edgepoints(self):
        
        edge_points = [ip for ip in self.points if ip.is_edgepoint()]
        return edge_points
     
    def find_network_cycles(self):  #TODO
        #this is the equivalent of "edge_loops"
        #TODO, mirror the get_cycle method from polystrips
        #right now ther eare no T or X junctions, only cuts across mesh or loops within mesh
        #will need to implement "IputNode.get_segment_to_right(InputSegment) to take care this
        
        print('SPLINE NETWORK CYCLES')
        
        ip_set = set(self.points)
        endpoints = set(self.get_endpoints())
        
        closed_edgepoints = set(self.get_edgepoints()) - endpoints
        
        
        print('There are %i endpoints' % len(endpoints))
        print('there are %i input points' % len(ip_set))
        print('there are %i closed edge_points' % len(closed_edgepoints))
        
        unclosed_ip_cycles = []
        unclosed_seg_cycles = []
        
        def next_segment(ip, current_seg): #TODO Code golf this
            if len(ip.link_segments) != 2: return None  #TODO, the the segment to right
            return [seg for seg in ip.link_segments if seg != current_seg][0]
              
        while len(endpoints):
            current_ip = endpoints.pop()
            ip_start = current_ip
            ip_set.remove(current_ip)
            
            node_cycle = [current_ip]
            if len(current_ip.link_segments) == 0: continue #Lonely Input Point, ingore it
            
            current_seg = current_ip.link_segments[0]
            seg_cycle = [current_seg]
            
            while current_seg:
                next_ip = current_seg.other_point(current_ip)  #always true
                
                if next_ip == ip_start: break  #we have found the end, no need to get the next segment
                
                #take care of sets
                if next_ip in ip_set: ip_set.remove(next_ip)
                if next_ip in endpoints: endpoints.remove(next_ip)
                node_cycle += [next_ip]
                
                #find next segment
                next_seg = next_segment(next_ip, current_seg)
                if not next_seg:  break  #we have found an endpoint
                seg_cycle += [next_seg]
               
                #reset variable for next iteration
                current_ip = next_ip
                current_seg = next_seg
                
            unclosed_ip_cycles += [node_cycle] 
            unclosed_seg_cycles += [seg_cycle] 
         
            
        print('there are %i unclosed cycles' % len(unclosed_ip_cycles))
        print('there are %i ip points in ip set' % len(ip_set))
        for i, cyc in enumerate(unclosed_ip_cycles):
            print('There are %i nodes in %i unclosed cycle' % (len(cyc), i))
        
        ip_cycles = []
        seg_cycles = []   #<<this basicaly becomes a PolyLineKine
        while len(ip_set):
            
            if len(closed_edgepoints):  #this makes sure we start with a closed edge point
                current_ip = closed_edgepoints.pop()
                ip_set.remove(current_ip)
            else:
                current_ip = ip_set.pop()
            
            ip_start = current_ip
                
            node_cycle = [current_ip]
            if len(current_ip.link_segments) == 0: continue #Lonely Input Point, ingore it
            
            current_seg = current_ip.link_segments[0]
            seg_cycle = [current_seg]
            
            while current_seg:
                next_ip = current_seg.other_point(current_ip)  #always true
                
                if next_ip == ip_start: break  #we have found the end, no need to get the next segment
                
                #take care of sets
                if next_ip in ip_set: ip_set.remove(next_ip)  #<-- i what circumstance would this not be true?
                if next_ip in closed_edgepoints: closed_edgepoints.remove(next_ip)
                node_cycle += [next_ip]
                
                #find next segment
                next_seg = next_segment(next_ip, current_seg)
                if not next_seg:  break  #we have found an endpoint
                seg_cycle += [next_seg]
               
                #reset variable for next iteration
                current_ip = next_ip
                current_seg = next_seg
                
            ip_cycles += [node_cycle] 
            seg_cycles += [seg_cycle] 
        
        
        print('there are %i closed seg cycles' % len(seg_cycles))
        for i, cyc in enumerate(ip_cycles):
            print('There are %i nodes in %i closed cycle' % (len(cyc), i))
        
        return ip_cycles, seg_cycles