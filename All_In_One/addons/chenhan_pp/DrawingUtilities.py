import bpy, bmesh, bgl, time, math, os, mathutils, sys;
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
from bpy_extras import view3d_utils;

def DrawGLLines(self, context, paths, temppaths, reflector_paths, reflected_temppaths, color, thickness, LINE_TYPE= "GL_LINE"):
    bgl.glEnable(bgl.GL_BLEND);
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA);
    bgl.glEnable(bgl.GL_LINE_SMOOTH);
    bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST);
#    bgl.glDisable(bgl.GL_DEPTH_TEST);

    bgl.glLineWidth(thickness);
    
    carr = context.scene.path_color;
    color = (carr[0],carr[1],carr[2],1.0);
    
    for path in paths:        
        bgl.glBegin(bgl.GL_LINE_STRIP);
        bgl.glColor4f(*color);
        
        for coord in path:
            bgl.glVertex3f(*coord);    
        
        bgl.glEnd();
    
    for path in reflector_paths:        
        bgl.glBegin(bgl.GL_LINE_STRIP);
        bgl.glColor4f(*color);
        
        for coord in path:
            bgl.glVertex3f(*coord);    
        
        bgl.glEnd();
    
    
    
    carr = context.scene.temp_path_color;
    color = (carr[0],carr[1],carr[2],1.0);
    for path in temppaths:
        bgl.glBegin(bgl.GL_LINE_STRIP);
        bgl.glColor4f(*color);
        
        for co in path:
            bgl.glVertex3f(*co);
            
        bgl.glEnd();
    
    
    for path in reflected_temppaths:
        bgl.glBegin(bgl.GL_LINE_STRIP);
        bgl.glColor4f(*color);
        
        for co in path:
            bgl.glVertex3f(*co);
            
        bgl.glEnd();

    # restore opengl defaults
    bgl.glLineWidth(1);
    bgl.glDisable(bgl.GL_BLEND);
#    bgl.glEnable(bgl.GL_DEPTH_TEST);
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def ScreenPoint3D(context, event, ray_max=1000.0):
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y


    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord);
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord);

    if bpy.app.version < (2, 77, 0):
        if rv3d.view_perspective == 'ORTHO':
            # move ortho origin back
#             ray_origin = ray_origin - (view_vector * (ray_max / 2.0));
            pass;
    
    else:
        ray_max = 1.0;
    
    ray_target = ray_origin + (view_vector * ray_max);


    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""
        # get the ray relative to the object
        matrix_inv = matrix.inverted();
        ray_origin_obj = matrix_inv * ray_origin;
        ray_target_obj = matrix_inv * ray_target;
        ray_direction_obj = ray_target_obj - ray_origin_obj;


        # cast the ray
        try:
            hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj);
        except ValueError:
            result, hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj);
#        hit, normal, face_index, distance = bvhtree.ray_cast(ray_origin_obj, ray_target_obj);
        
        if face_index != -1:
            return hit, normal, face_index;
        else:
            return None, None, None;


    # no need to loop through other objects since we are interested in the active object only
    obj = context.scene.objects.active;
    matrix = obj.matrix_world.copy();
    mousemarker = bpy.data.objects["GeodesicMarker"];
    
    if obj.type == 'MESH':
        hit, normal, face_index = obj_ray_cast(obj, matrix);
        if hit is not None:
            hit_world = matrix * hit;
            mousemarker.location = hit_world;
            return hit_world, True, face_index, hit;
        else:
            return view_vector, False, None, None;
