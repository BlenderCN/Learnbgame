'''
Created on Oct 8, 2015

@author: Patrick
'''
import time

import bpy
import bmesh
from mathutils import Vector, Matrix, kdtree
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line, intersect_line_plane
from bpy_extras import view3d_utils

from ..bmesh_fns import grow_selection_to_find_face, flood_selection_faces, edge_loops_from_bmedges
from ..cut_algorithms import cross_section_2seeds_ver1, path_between_2_points
from ..common.blender import bversion
from ..geodesic import geodesic_walk, continue_geodesic_walk, gradient_descent
from .. import common_drawing

class Slice(object):
    '''
    A class which manages user placed points on an object to create a
    piecewise path of geodesics, adapted to the objects surface.
    '''
    def __init__(self,context, cut_object):   
        
        self.cut_ob = cut_object
        self.bme = bmesh.new()
        self.bme.from_mesh(cut_object.data)
        self.bme.verts.ensure_lookup_table()
        self.bme.edges.ensure_lookup_table()
        self.bme.faces.ensure_lookup_table()
        
        
        #non_tris = [f for f in self.bme.faces if len(f.verts) > 3]
        #bmesh.ops.triangulate(self.bme, faces = non_tris, quad_method = 0, ngon_method = 0)
        
        #non_tris = [f for f in self.bme.faces if len(f.verts) > 3]
        #if len(non_tris):
            #geom = bmesh.ops.connect_verts_concave(self.bme, non_tris)
        
        self.bme.verts.ensure_lookup_table()
        self.bme.edges.ensure_lookup_table()
        self.bme.faces.ensure_lookup_table()
        
        self.bvh = BVHTree.FromBMesh(self.bme)
        
        
        self.seed = None
        self.seed_loc = None
        
        self.target = None
        self.target_loc = None
        
        self.path = []
    
    def reset_vars(self):
        '''
        '''

        self.seed = None
        self.seed_loc = None
        
        self.target = None
        self.target_loc = None
        self.geo_data = [dict(), set(), set(), set()]  #geos, fixed, close, far
        self.path = []
        
        
    def grab_initiate(self):
        if self.target != None :
            self.grab_undo_loc = self.target_loc
            self.target_undo = self.target
            self.path_undo = self.path
            return True
        else:
            return False
       
    def grab_mouse_move(self,context,x,y):
        region = context.region
        rv3d = context.region_data
        coord = x, y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)

        mx = self.cut_ob.matrix_world
        imx = mx.inverted()
        
        if bversion() < '002.077.000':
            loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target)
        else:
            res, loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        
        loc2, no2, face_ind2, d = self.bvh.ray_cast(imx * ray_origin, view_vector)
        
        
        
        if loc != None and loc2 != None:
            print((loc - loc2).length)
        
            
        if face_ind == -1:        
            self.grab_cancel()
            return
        
        
        self.target = self.bme.faces[face_ind]
        self.target_loc = loc
        

        vrts, eds, ed_cross, f_cross, error = path_between_2_points(self.bme, self.bvh, mx,mx* self.seed_loc,mx*self.target_loc, 
                                                                    max_tests = 10000, debug = True, 
                                                                    prev_face = None, use_limit = True)
            
        if not error:
            self.path = vrts
        #else:
            #self.path = []
            
            
    def grab_cancel(self):
        self.target_loc = self.grab_undo_loc
        self.target = self.target_undo
        self.path = self.path_undo
        return
    
    def grab_confirm(self):
        self.grab_undo_loc = None
        self.target_undo = None
        self.path_undo = []
        
        return
               
    def click_add_seed(self,context,x,y):
        '''
        x,y = event.mouse_region_x, event.mouse_region_y
        
        this will add a point into the bezier curve or
        close the curve into a cyclic curve
        '''
        region = context.region
        rv3d = context.region_data
        coord = x, y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)
        mx = self.cut_ob.matrix_world
        imx = mx.inverted()
        
        if bversion() < '002.077.000':
            loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target)
        else:
            res, loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        
        if face_ind == -1: 
            self.selected = -1
            return
        
        self.seed = self.bme.faces[face_ind]
        self.seed_loc = loc
        
        self.geo_data = [dict(), set(), set(), set()]
    
    
        
    def click_add_target(self, context, x, y):
        
        region = context.region
        rv3d = context.region_data
        coord = x, y
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        ray_target = ray_origin + (view_vector * 1000)
        mx = self.cut_ob.matrix_world
        imx = mx.inverted()
        
        if bversion() < '002.077.000':
            loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target)
        else:
            res, loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        if face_ind == -1: return
            
            
        self.target = self.bme.faces[face_ind]
        self.target_loc = loc
        
        
        vrts, eds, ed_cross, f_cross, error = path_between_2_points(self.bme, self.bvh, mx,mx* self.seed_loc,mx*self.target_loc, 
                                                                    max_tests = 10000, debug = True, 
                                                                    prev_face = None, use_limit = True)
            
        if not error:
            self.path = vrts
        else:
            self.path = []
        return
                
    def draw(self,context):
        if len(self.path):
            mx = self.cut_ob.matrix_world
            pts = [mx * v for v in self.path]
            common_drawing.draw_polyline_from_3dpoints(context, pts, (.2,.1,.8,1), 3, 'GL_LINE')

        if self.seed_loc != None:
            mx = self.cut_ob.matrix_world
            
            common_drawing.draw_3d_points(context, [mx * self.seed_loc], 8, color = (1,0,0,1))

        if self.target_loc != None:
            mx = self.cut_ob.matrix_world
            common_drawing.draw_3d_points(context, [mx * self.target_loc], 8, color = (0,1,0,1))
class PolyCutPoint(object):
    
    def __init__(self,co):
        self.co = co
        
        self.no = None
        self.face = None
        self.face_region = set()
        
    def find_closest_non_manifold(self):
        return None
    
class NonManifoldEndpoint(object):
    
    def __init__(self,co, ed):
        if len(ed.link_faces) != 1:
            return None
        
        self.co = co
        self.ed = ed
        self.face = ed.link_faces[0]
        
    
        
        
        
        