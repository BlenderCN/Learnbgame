import gc
import copy;
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import bpy, bmesh, bgl, math, os, mathutils, sys;
import blf, time, datetime;
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
from bpy_extras import view3d_utils;

import numpy as np;

from bpy.props import StringProperty;
from bpy.props import FloatVectorProperty, BoolProperty;
from mathutils import Vector, Matrix;
from mathutils.bvhtree import BVHTree;

from chenhan_pp.MeshData import RichModel
from chenhan_pp.GraphPaths import ChenhanGeodesics, isFastAlgorithmLoaded;

from chenhan_pp.CICHWithFurtherPriorityQueue import CICHWithFurtherPriorityQueue
from chenhan_pp.helpers import getBMMesh, ensurelookuptable, getBarycentricCoordinate, getCartesianFromBarycentre, getTriangleArea, getGeneralCartesianFromPolygonFace;
from chenhan_pp.helpers import buildKDTree, getDuplicatedObject, getQuadMesh;
from chenhan_pp.helpers import getScreenLookAxis, drawLine, drawText, drawTriangle, ScreenPoint3D, createIsoContourMesh;
from chenhan_pp.helpers import getTriangleMappedPoints, getBarycentricValue, getMappedContourSegments, GetIsoLines;
from chenhan_pp.GraphPaths import ChenhanGeodesics, AnisotropicGeodesics

__date__ ="$Mar 23, 2015 8:16:11 PM$"

def DrawGL(self, context):
    
#     bgl.glDisable(bgl.GL_DEPTH_TEST);
    bgl.glColor4f(*(1.0, 1.0, 0.0,1.0));
    bgl.glPointSize(15.0);
    bgl.glBegin(bgl.GL_POINTS);
    bgl.glVertex3f(*self.highlight_point);
    bgl.glEnd();
#     bgl.glEnable(bgl.GL_DEPTH_TEST);
    if(len(self.isolines)):            
        bgl.glColor4f(*(0.0, 1.0, 0.0,1.0));
        bgl.glPointSize(15.0);
        bgl.glBegin(bgl.GL_POINTS);
        bgl.glVertex3f(*self.isoorigin);
        bgl.glEnd();        
        drawText(context, "Iso Origin", self.isoorigin);
        
        for segment in self.isolines:
            drawLine(segment['start'], segment['end'], 1.0, (0.0, 1.0, 0.0,1.0));
#          
        bgl.glDisable(bgl.GL_DEPTH_TEST);
    
    # restore opengl defaults
    bgl.glLineWidth(1);
    bgl.glDisable(bgl.GL_BLEND);
    bgl.glEnable(bgl.GL_DEPTH_TEST);
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0);

class SpecifiedIsoContours(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "ashok.specifiedisocontours";
    bl_label = "Isolines Visualizer";
    bl_description = "Given a mesh show isolines"
    hit = FloatVectorProperty(name="hit", size=3);
    
    def getWorldFacePoint(self, context, mesh, face):
        arr = [];
        path = [mesh.data.vertices[vindex].co for vindex in face.vertices];
        for co in path:
            arr.append(mesh.matrix_world * co);
        
        return arr;            
    
    def modal(self, context, event):
        region = context.region;
        rv3d = context.region_data;
        obj = context.active_object;
        context.area.tag_redraw();
        
#         print(event.type, event.value);
        
        if(not context.scene.isolinesupdated and self.alg and len(self.vertex_distances)):
            dist_max = max(self.vertex_distances);
            n_count = max(self.subject.isolines_count, 1);
            print('DISTANCE MAX ::: ', dist_max);
            isolines = GetIsoLines(n_count, self.subject, self.richmodel, self.vertex_distances, useDistance=self.subject.specific_distance_ratio*dist_max);
            self.constant_points[self.vertex_index] = copy.deepcopy(isolines);
            
            for segment in isolines:
                segment['start'] = self.subject.matrix_world * segment['start'];
                segment['end'] = self.subject.matrix_world * segment['end'];
            
            self.constant_points_transformed[self.vertex_index] = isolines;
            
            self.isolines.clear();
            for key_vindex in self.constant_points_transformed:            
                self.isolines.extend(self.constant_points_transformed[key_vindex]);
                
            print('LEN OF ISOLINES: %s'%(len(self.isolines)));
#             createIsoContourMesh(context, self.subject, self.isolines);   
            
            context.scene.isolinesupdated = True;
        
        
        if event.type in {'ESC'}:       
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW'); 
            if(self.bm):
                self.bm.free();
                
            return {'CANCELLED'}
        
        if(event.type == 'I' and event.value == 'PRESS'):
            diffkey = time.time() - self.lastkeypress;
            if(diffkey > 3):
                self.lastkeypress = time.time();
                if(event.type == "I"):
                    self.hit, onMesh, face_index, hitpoint = ScreenPoint3D(context, event, self.subject, position_mouse = False);
                    if(self.richmodel or isFastAlgorithmLoaded):
                        vco, vindex, dist = self.kd.find(hitpoint);                        
                        self.alg.addSeedIndex(vindex);        
                        self.vertex_distances = self.alg.getVertexDistances(vindex);
                        self.max_godesic_distance = np.amax(self.vertex_distances);
                        self.isoorigin = self.subject.matrix_world * self.subject.data.vertices[vindex].co;
                        self.constant_points[vindex] = [];
                        self.vertex_index = vindex;                 
                        context.scene.isolinesupdated = False;
                        return {'RUNNING_MODAL'};
        
        elif event.type in {'F'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW');
            if(self.bm):
                self.bm.free();            
            self.isolines.clear();
            for key_vindex in self.constant_points:            
                self.isolines.extend(self.constant_points[key_vindex]);                
            createIsoContourMesh(context, self.subject, self.isolines);
            
            return {'FINISHED'};
        
        elif(event.type == 'UP_ARROW' and event.value == 'PRESS'):
            diffkey = time.time() - self.lastkeypress;
            if(diffkey > 0.2):
                self.lastkeypress = time.time();
                self.subject.specific_distance_ratio = min(1.0, self.subject.specific_distance_ratio+0.01);
                return {'RUNNING_MODAL'};
                
        elif(event.type == 'DOWN_ARROW' and event.value == 'PRESS'):
            diffkey = time.time() - self.lastkeypress;
            if(diffkey > 0.2):
                self.lastkeypress = time.time();
                self.subject.specific_distance_ratio = max(0.01, self.subject.specific_distance_ratio-0.01);
                return {'RUNNING_MODAL'};
        
        elif(event.type == 'MOUSEMOVE'):
            self.hit, onMesh, face_index, hitpoint = ScreenPoint3D(context, event, self.subject, position_mouse = False);
            if(onMesh):
                if(face_index):
                    vco, vindex, dist = self.kd.find(hitpoint);
                    self.highlight_point = self.subject.matrix_world * self.subject.data.vertices[vindex].co;        
        
        context.area.header_text_set("Maximum Geodesic Distance: %f"%(self.max_godesic_distance));
         
        return {'PASS_THROUGH'};
        
    def invoke(self, context, event):
        if(context.active_object):
            self.subject = context.active_object;            
            self.bm = getBMMesh(context, self.subject, False);
            
            self.richmodel = None;            
            if(not isFastAlgorithmLoaded):
                try:
                    self.richmodel = RichModel(self.bm, self.subject);
                    self.richmodel.Preprocess();
                except: 
                    print('CANNOT CREATE RICH MODEL');
                    self.richmodel = None;
            
            
            self.vertex_distances = [];
            self.max_godesic_distance = 0.0;
            self.alg = ChenhanGeodesics(context, self.subject, self.bm, self.richmodel);
            self.isolines = [];
            self.constant_points = {};
            self.constant_points_transformed = {};
            self.vertex_index = 0;
            
            self.isoorigin = ();
            self.highlight_point = (0,0,0);
            self.kd = buildKDTree(context, self.subject, type="VERT");
            self.lastkeypress = time.time();
            
            context.scene.objects.active = self.subject;
            self.subject.select = True;
            
            args = (self, context); 
            self._handle = bpy.types.SpaceView3D.draw_handler_add(DrawGL, args, 'WINDOW', 'POST_VIEW');
            context.window_manager.modal_handler_add(self);
        return {'RUNNING_MODAL'}

class IsoContours(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "ashok.isocontours";
    bl_label = "Isolines Visualizer";
    bl_description = "Given a mesh show isolines"
    hit = FloatVectorProperty(name="hit", size=3);
    
    def getWorldFacePoint(self, context, mesh, face):
        arr = [];
        path = [mesh.data.vertices[vindex].co for vindex in face.vertices];
        for co in path:
            arr.append(mesh.matrix_world * co);
        
        return arr;    
    
#     def saveIsoContoursMesh(self, context):
        
    
    def modal(self, context, event):
        region = context.region;
        rv3d = context.region_data;
        obj = context.active_object;
        context.area.tag_redraw();
        
        if(not context.scene.isolinesupdated and self.alg and len(self.vertex_distances)):
            self.isolines = GetIsoLines(self.subject.isolines_count+1, self.subject, self.richmodel, self.vertex_distances);
#             self.isolines = self.alg.GetIsoLines(self.subject.isolines_count+1);
            createIsoContourMesh(context, self.subject, self.isolines);   
            
            for segment in self.isolines:
                segment['start'] = self.subject.matrix_world * segment['start'];
                segment['end'] = self.subject.matrix_world * segment['end'];
            
            context.scene.isolinesupdated = True;
        
        
        if event.type in {'ESC'}:       
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW'); 
            if(self.bm):
                self.bm.free();
                
            return {'CANCELLED'}
        
        elif(event.type == 'I' and event.value == 'PRESS'):
            diffkey = time.time() - self.lastkeypress;
            if(diffkey > 3):
                self.lastkeypress = time.time();
                if(event.type == "I"):
                    self.hit, onMesh, face_index, hitpoint = ScreenPoint3D(context, event, self.subject, position_mouse = False);
                    if(self.richmodel or isFastAlgorithmLoaded):
                        vco, vindex, dist = self.kd.find(hitpoint);                        
                        self.alg.addSeedIndex(vindex);        
                        self.vertex_distances = self.alg.getVertexDistances(vindex);     
                        self.isoorigin = self.subject.matrix_world * self.subject.data.vertices[vindex].co;
                        context.scene.isolinesupdated = False;
                        return {'RUNNING_MODAL'};
        
        elif(event.type == 'MOUSEMOVE'):
            self.hit, onMesh, face_index, hitpoint = ScreenPoint3D(context, event, self.subject, position_mouse = False);
            if(onMesh):
                if(face_index):
                    vco, vindex, dist = self.kd.find(hitpoint);
                    self.highlight_point = self.subject.matrix_world * self.subject.data.vertices[vindex].co;        
                    
        return {'PASS_THROUGH'};
        
    def invoke(self, context, event):
        if(context.active_object):
            self.subject = context.active_object;            
            self.bm = getBMMesh(context, self.subject, False);
            
            self.richmodel = None;
            if(not isFastAlgorithmLoaded):
                try:
                    self.richmodel = RichModel(self.bm, self.subject);
                    self.richmodel.Preprocess();
                except: 
                    print('CANNOT CREATE RICH MODEL');
                    self.richmodel = None;
                                
            self.vertex_distances = [];
            self.alg = ChenhanGeodesics(context, self.subject, self.bm, self.richmodel);
            self.isolines = [];
            self.isoorigin = ();
            self.highlight_point = (0,0,0);
            self.kd = buildKDTree(context, self.subject, type="VERT");
            self.lastkeypress = time.time();
            
            context.scene.objects.active = self.subject;
            self.subject.select = True;
            
            args = (self, context); 
            self._handle = bpy.types.SpaceView3D.draw_handler_add(DrawGL, args, 'WINDOW', 'POST_VIEW');
            context.window_manager.modal_handler_add(self);
        return {'RUNNING_MODAL'}