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

from ..bmesh_fns import grow_selection_to_find_face, flood_selection_faces
from ..cut_algorithms import cross_section_2seeds_ver1, path_between_2_points
from ..geodesic import geodesic_walk, continue_geodesic_walk, gradient_descent
from .. import common_drawing
from ..common.blender import bversion

class GeoPath(object):
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
        
        
        non_tris = [f for f in self.bme.faces if len(f.verts) > 3]
        bmesh.ops.triangulate(self.bme, faces = non_tris, quad_method = 0, ngon_method = 0)
        self.bvh = BVHTree.FromBMesh(self.bme)
        
        
        self.seed = None
        self.seed_loc = None
        
        self.target = None
        self.target_loc = None
        
        self.geo_data = [dict(), set(), set(), set()]  #geos, fixed, close, far
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
            if face_ind == -1:        
                self.grab_cancel()
                return
        else:
            res, loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        
            if not res:
                self.grab_cancel()
                return
        
        #check if first or end point and it's a non man edge!   
        geos, fixed, close, far = self.geo_data
        
        self.target = self.bme.faces[face_ind]
        self.target_loc = loc
        
        if all([v in fixed for v in self.target.verts]):
            
            path_elements, self.path = gradient_descent(self.bme, geos, 
                                self.target, self.target_loc, epsilon = .0000001)
            print('great we have already waked the geodesic this far')
            
        else:
            print('continue geo walk until we find it, then get it')
            continue_geodesic_walk(self.bme, self.seed, self.seed_loc, 
                           geos, fixed, close, far,
                           targets =[self.bme.faces[face_ind]], subset = None, max_iters = 100000, min_dist = None)
            
            path_elements, self.path = gradient_descent(self.bme, geos, 
                                self.target, self.target_loc, epsilon = .0000001)
            
        
        
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
            if face_ind == -1: 
                self.selected = -1
                return
        else:
            res, loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
        
            if not res:
                self.selected = -1
                return
        self.bme.faces.ensure_lookup_table() #how does this get outdated?
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
            if face_ind == -1: return   
        else:
            res, loc, no, face_ind = self.cut_ob.ray_cast(imx * ray_origin, imx * ray_target - imx * ray_origin)
            if not res: return
                         
        self.target = self.bme.faces[face_ind]
        self.target_loc = loc
        
        
        geos, fixed, close, far = geodesic_walk(self.bme, self.seed, self.seed_loc, 
                                                targets = [self.target], subset = None, max_iters = 100000,
                                                min_dist = None)
        
        path_elements, self.path  = gradient_descent(self.bme, geos, 
                                self.target, self.target_loc, epsilon = .0000001)
        
        self.geo_data = [geos, fixed, close, far]
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
        
    
        
        
        
        