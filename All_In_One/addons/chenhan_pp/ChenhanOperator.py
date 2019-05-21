import gc
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import bpy, time;

from bpy.props import FloatVectorProperty;
from mathutils import Vector;

# from basics.mathtoolbox import getBMMesh, ensurelookuptable;
# from basics.MeshToolBox import buildKDTree, getDuplicatedObject;

from chenhan_pp.MeshTools import getBMMesh, ensurelookuptable, buildKDTree, getDuplicatedObject

from bpy.props import StringProperty;

# import chenhan.Constants as Constants;
# from chenhan.meshstructures import RichModel

import chenhan_pp.Constants as Constants;
from chenhan_pp.MeshData import RichModel

from chenhan_pp.DrawingUtilities import ScreenPoint3D, DrawGLLines
from chenhan_pp.GraphPaths import ChenhanGeodesics, AnisotropicGeodesics, isFastAlgorithmLoaded;
from chenhan_pp.helpers import createGeodesicPathMesh;


__author__="ashok"
__date__ ="$Mar 23, 2015 8:16:11 PM$"

class ChenhanGeodesicsOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "ashok.geodesics_chenhan";
    bl_label = "Geodesics using ChenHan's algorithm";
    hit = FloatVectorProperty(name="hit", size=3);
    algorithm_counter = 0;
    
    def applyMarkerColor(self, object):
        try:
            material = bpy.data.materials[object.name+'_MouseMarkerMaterial'];
        except:
            material = bpy.data.materials.new(object.name+'_MouseMarkerMaterial');
        
        material.diffuse_color = (1.0, 0.0, 0.0);
        material.alpha = 1;
        material.specular_color = (1.0, 0.0, 0.0);
        
        object.data.materials.clear();
        object.data.materials.append(material);
    
    def getSequencedShortestPath(self, v1, v2, local_path = False):
        path = None;
        reflected_path = None;
        if(v1 != v2):
            path, reflected_path = self.chenhan.path_between(v1, v2, local_path = local_path);
        return path, reflected_path;
    
    
    def endOperator(self, context):
        context.area.header_text_set();
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW');            
        if(self.bm):
            self.bm.free();
        
        
    def modal(self, context, event):
        region = context.region;
        rv3d = context.region_data;
        obj = context.active_object;
        context.area.tag_redraw();
        
        #=======================================================================
#         print('EVENT ::: ', event.type, event.value);
        #=======================================================================
        
        if event.type in {'ESC'}:
            print('INDICES :: ', self.chenhan.m_seed_indices);
            
            self.endOperator(context);
                
            return {'CANCELLED'};
        
        elif (event.value == 'PRESS' and event.type == 'A'):
            diffmouse = time.time() - self.lastmousepress;
            if(diffmouse > Constants.TIME_INTERVAL_MOUSE_PRESS):
                self.lastmousepress = time.time();
            else:
                return {'RUNNING_MODAL'};
            
            if(len(self.reflected_paths)):
                createGeodesicPathMesh(context, self.mesh, self.for_reflected_paths_as_mesh, suffix='reflectedpaths' );
            if(len(self.paths)):
                createGeodesicPathMesh(context, self.mesh, self.for_paths_as_mesh, suffix='geodesicpaths');
                self.endOperator(context);                
                return {'FINISHED'};1
            
            return {'RUNNING_MODAL'};
            
        elif (event.value == "PRESS" and event.type == "LEFTMOUSE"):
            
            if(self.pausedrawing):
                return {'PASS_THROUGH'};
            
            self.hit, onMesh, face_index, hitpoint = ScreenPoint3D(context, event);
            if(onMesh):
                diffmouse = time.time() - self.lastmousepress;
                
                if(diffmouse > Constants.TIME_INTERVAL_MOUSE_PRESS):
                        self.lastmousepress = time.time();
                else:
                    return {'RUNNING_MODAL'};
            
                find_co, index, dist = self.kdtree.find(hitpoint);  
                
                if(len(self.chenhan.getSeedIndices()) > 0):
                    if(self.chenhan.getSeedIndices()[-1] == index):
                        return {'PASS_THROUGH'};                
                
                self.chenhan.addSeedIndex(index);
                print('ADDED SEED INDEX ', index);
                self.currentseed = index;
                stable_paths = [{'start':-1, 'end':-1, 'points':None}];
                
                if(len(self.chenhan.getSeedIndices()) > 1):
                    p_indices = self.chenhan.getSeedIndices();
                    
                    stable_paths, stable_reflected_paths = self.getSequencedShortestPath(p_indices[-2], p_indices[-1]);
                    if(stable_paths):
                        stable_paths_for_mesh, stable_reflected_paths_for_mesh = self.getSequencedShortestPath(p_indices[-2], p_indices[-1], local_path=True);
                        
                        self.paths.append(stable_paths);
                        self.for_paths_as_mesh.append(stable_paths_for_mesh);
                        
                        if(len(stable_reflected_paths)):
                            self.reflected_paths.append(stable_reflected_paths);
                            self.for_reflected_paths_as_mesh.append(stable_reflected_paths_for_mesh);
                
                return {'PASS_THROUGH'};
        
        elif event.type == 'MOUSEMOVE':            
            if(self.pausedrawing):
                return {'PASS_THROUGH'}
            self.hit, onMesh, face_index, hitpoint = ScreenPoint3D(context, event);
            if(onMesh):
                find_co, index, dist = self.kdtree.find(hitpoint);
                
                if(len(self.chenhan.getSeedIndices()) > 0):
                    obj = self.mesh;
                    
                    p_indices = self.chenhan.getSeedIndices();
                    currentseed = index;
                    
                    temp_paths, temp_reflected_paths = self.getSequencedShortestPath(p_indices[-1], currentseed);
                    try:
                        del self.temppath3d[0];
                        del self.reflected_temppath3d[0];
                    except IndexError:
                        pass;
                    if(temp_paths):
                        self.temppath3d.append(temp_paths);
                        self.reflected_temppath3d.append(temp_reflected_paths);
                    
            context.area.header_text_set("hit: %.4f %.4f %.4f" % tuple(self.hit));
                
            return {'PASS_THROUGH'};

        return {'PASS_THROUGH'} 
    
    def startModalOperations(self, context):
        self.pausedrawing = False;
        self.lastkeypress = time.time();
        self.lastmousepress = time.time();
        self.mesh = context.active_object;
        
        self.bm = getBMMesh(context, self.mesh, False);
        
        maxsize = max(self.mesh.dimensions.x, self.mesh.dimensions.y, self.mesh.dimensions.z);
        markersize = maxsize * 0.01;
        tempmarkersource = "GeodesicMarker";
        
        try:
            tempmarker = bpy.data.objects[tempmarkersource];
        except KeyError:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count = 36);
            tempmarker = context.object;
            tempmarker.name = "GeodesicMarker";
        
        tempmarker.dimensions = (markersize,markersize,markersize);
#         self.mousepointer = getDuplicatedObject(context, tempmarker, "MouseMarker");
        self.mousepointer = tempmarker;
        
        self.applyMarkerColor(self.mousepointer);
        
#         self.mousepointer = getDuplicatedObject(context, tempmarker, "MouseMarker");
        self.mousepointer.hide = False;
        self.mousepointer.hide_select = False;
        self.mousepointer.show_wire = False;
        self.mousepointer.show_all_edges = False;
        
        bpy.ops.object.select_all(action="DESELECT");
        self.mesh.select = False;
        context.scene.objects.active = self.mesh;
        
        self.richmodel = None;
        
        self.reflectormesh = None;
        if(not isFastAlgorithmLoaded):
            self.richmodel = RichModel(self.bm, context.active_object);
            self.richmodel.Preprocess();
        
        if(self.mesh.reflectormesh != 'None'):
            temp_reflectormesh = context.scene.objects[self.mesh.reflectormesh];
            r_verts = temp_reflectormesh.data.vertices;
            r_faces = temp_reflectormesh.data.polygons;
            r_edges = temp_reflectormesh.data.edges;
            m_verts = self.mesh.data.vertices;
            m_faces = self.mesh.data.polygons;
            m_edges = self.mesh.data.edges;
            
            if(len(r_verts) == len(m_verts) and len(r_faces) == len(m_faces) and len(r_edges) == len(m_edges)):            
                self.reflectormesh = context.scene.objects[self.mesh.reflectormesh];
        
        print('REFLECTOR MESH :::: ', self.mesh.reflectormesh, self.mesh.reflectormesh is None);
            
        #self.chenhan = ChenhanGeodesics(context, context.active_object, self.bm, self.richmodel);
        self.chenhan = AnisotropicGeodesics(context, context.active_object, self.bm, self.richmodel,self.reflectormesh);
        
        if(isFastAlgorithmLoaded()):
            self.richmodel = self.chenhan.getRichModel();
        
        self.paths = [];
        self.reflected_paths = [];
        
        self.for_paths_as_mesh = [];
        self.for_reflected_paths_as_mesh = [];
        
        self.prev = {};
        self.temppath3d = [];
        self.reflected_temppath3d = [];
        self.seeds = [];        
        self.currentseed = 0;
        self.currentseed_quad = 0;
        self.kdtree = buildKDTree(context, self.mesh);
        args = (self, context, self.paths, self.temppath3d, self.reflected_paths, self.reflected_temppath3d, (0.0,1.0,0.0,1.0), 5.0);
        self._handle = bpy.types.SpaceView3D.draw_handler_add(DrawGLLines, args, 'WINDOW', 'POST_VIEW');
        context.window_manager.modal_handler_add(self);
        return {'RUNNING_MODAL'}
        
    
    def invoke(self, context, event):
        print('INVOKE MODALITY')
        return self.startModalOperations(context);
    
    def execute(self, context):
        print('EXECUTE MODALITY')
        return self.startModalOperations(context);


def register():
    bpy.utils.register_module(__name__);
 
 
def unregister():
    bpy.utils.register_module(__name__);
 
 
if __name__ == "__main__":
    register();
