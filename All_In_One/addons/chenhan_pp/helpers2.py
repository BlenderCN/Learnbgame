import bpy, bmesh, bgl, math, os, mathutils, sys;
import blf, time, datetime;
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
from bpy_extras import view3d_utils;

from bpy.props import StringProperty;
from bpy.props import FloatVectorProperty;
from mathutils import Vector, Matrix;
from mathutils.bvhtree import BVHTree;


BEVEL_DEPTH_FACTOR = 0.002941176;
MAX_ZOOM_DISTANCE = 100.0;
MIN_ZOOM_DISTANCE = 1.0;
FRIENDLY_ZOOM_DISTANCE = 3.5;
TEXT_SCALE_VALUE = 0.001;
TWOPI = math.pi * 2.0;

def areas_view3d(context):
    spaces = [];
    for area in context.window.screen.areas:
        if(area.type == 'VIEW_3D'):
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    spaces.append(space);
    
    return spaces;

def getQuadMesh(context, object):
    bm = getBMMesh(context, object);
    bpy.ops.mesh.select_all(action="SELECT");
    
    bpy.ops.mesh.tris_convert_to_quads(face_threshold=3.14 * 0.5, shape_threshold=3.14 * 0.5);
    
    bm.free();
    
    if(not context.mode == "OBJECT"):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False);
    
    return object;

def getDuplicatedObject(context, meshobject, meshname="Duplicated"):
    if(not context.mode == "OBJECT"):
        bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False);

    bpy.ops.object.select_all(action='DESELECT') #deselect all object
    
    hide_selection = meshobject.hide_select;
    hide_view = meshobject.hide;
    
    meshobject.hide_select = False;
    meshobject.hide = False;
    
    #The next step is to duplicate these objects and then apply fairing on them
    meshobject.select = True;
    context.scene.objects.active = meshobject;
    bpy.ops.object.duplicate_move();

    meshobject.select = False;

    duplicated = context.active_object;
    duplicated.location.x = 0;
    duplicated.location.y = 0;
    duplicated.location.z = 0;
    duplicated.name = meshname;
    duplicated.show_wire = True;
    duplicated.show_all_edges = True;
    duplicated.data.name = meshname;

    meshobject.hide_select = hide_selection;
    meshobject.hide = hide_view;

    return duplicated;

def getBMMesh(context, obj, useeditmode = True):
#     print('GETBMMESH ::: USEEDITMODE = ', useeditmode, " MESH NAME ::: ", obj.name);
    if(not useeditmode):
        if(context.mode == "OBJECT"):
            bm = bmesh.new();
            bm.from_mesh(obj.data);
        else:
            bm = bmesh.from_edit_mesh(obj.data);


            if context.mode != 'EDIT_MESH':
                bpy.ops.object.mode_set(mode = 'EDIT', toggle = False);

        return bm;

    else:
        if(context.mode != "OBJECT"):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False);

        bpy.ops.object.select_all(action='DESELECT') #deselect all object
        context.scene.objects.active = obj;
        obj.select = True;
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False);
        bm = bmesh.from_edit_mesh(obj.data);
        return bm;
    


def ensurelookuptable(bm):
    try:
        bm.verts.ensure_lookup_table();
        bm.edges.ensure_lookup_table();
        bm.faces.ensure_lookup_table();
    except:
        print('THIS IS AN OLD BLENDER VERSION, SO THIS CHECK NOT NEEDED');

#Can be of type, 1-VERT, 2-EDGE, 3-FACE, 4-FACEVERT (contains vertices co with face Index)
#5-EDGEVERT (contains vertices co with EDGE INDEX)
def buildKDTree(context, meshobject, type="VERT", points=[], use_bm =None):
#     print('BUILDING KDTREE FOR ', object.name);
    if(meshobject):
        mesh = meshobject.data;
        data = [];    
    if(type == "VERT"):
        size = len(mesh.vertices);
        kd = mathutils.kdtree.KDTree(size);
        for i, v in enumerate(mesh.vertices):
            kd.insert(v.co, v.index);
    elif(type =="EDGE"):
        size = len(mesh.edges);
        kd = mathutils.kdtree.KDTree(size);

        for i, e in enumerate(mesh.edges):
            v0 = mesh.vertices[e.vertices[0]].co;
            v1 = mesh.vertices[e.vertices[1]].co;
            vect = (v1 - v0);
            point = v0 + (vect * 0.5);
            kd.insert(point, e.index);
    
    elif(type =="FACE"):
        size = len(mesh.polygons);
        kd = mathutils.kdtree.KDTree(size);
        oneby3 = 1.0 / 3.0;
        loops = meshobject.data.loops;
        vertices = meshobject.data.vertices;
        
        for i, f in enumerate(mesh.polygons):
            kd.insert(f.center.copy(), f.index);
    
    elif(type == "FACEVERT"):
        size = len(mesh.polygons) * 3;
        kd = mathutils.kdtree.KDTree(size);

        for i, f in enumerate(mesh.polygons):
            if(len(f.loop_indices) > 3):
                print('GOTCHA :: THE BLACK SHEEP ::: ', object.name, f.index);
            for ind in f.loop_indices:
                l = mesh.loops[ind];
                v = mesh.vertices[l.vertex_index];
                kd.insert(v.co, f.index);            
    
    elif(type == "CUSTOM"):
        size = len(points);
        kd = mathutils.kdtree.KDTree(size);
        useDict = True;
        try:
            index = points[0]['index'];
        except KeyError:            
            useDict = False;
        except TypeError:
            useDict = False;
        except IndexError:
            useDict = False;
        
        for i, point in enumerate(points):
            if(useDict):
                index = point['index'];
                co = point['co'];
                kd.insert(co, index);
            else:
                kd.insert(point, i);          
                
    kd.balance();
#     print('BUILD KD TREE OF SIZE : ', size, ' FOR :: ', object.name, ' USING TYPE : ', type);
    return kd;

def getTriangleArea(p0, p1, p2):        
    a = (p1 - p0).length;
    b = (p2 - p1).length;
    c = (p0 - p2).length;
    #Using Herons formula
    A = 0.25 * ((a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c))**0.5;
    
    if(isinstance(A, complex)):
        A = cmath.phase(A);
    
    if (A < 0.0001):
        A = 0.0001;
    
    return A, A*2;

def getGeneralCartesianFromPolygonFace(weights, f, mesh):
    loops = mesh.data.loops;
    vertices = mesh.data.vertices;
    
    p = Vector((0,0,0));
    points = [];
    
    for lid in f.loop_indices:
        l = loops[lid];
        v = vertices[l.vertex_index]; 
        points.append(v.co.copy());
    
    for index, r in enumerate(weights):
        p = p + (points[index] * r);    
        
    return p;

def getGeneralCartesianFromBarycentre(weights, points):
    p = Vector((0.0,0.0,0.0));
    for index, r in enumerate(weights):
        p = p + (points[index] * r);    
    return p;

#Given the barycentric value as a mathutils.Vector (u=>x, v=>y, w=>z)
#And the three new points of the triangle again of the form mathutils.Vector
#Will give the new cartesian coordinate

def getCartesianFromBarycentre(ba, a, b, c):
    aa = a.copy();
    bb = b.copy();
    cc = c.copy();    
    
    p = ( aa * ba.x) + (bb * ba.y) + (cc * ba.z);
    
    return p;    

#Given the point and three coordinates of form mathutils.Vector
#Will return the barycentric ratios
def getBarycentricCoordinate(p, a, b, c, *, epsilon=0.0000001,snapping=True):
    
    v0 = b - a;
    v1 = c - a;
    v2 = p - a;
    
    d00 = v0.dot(v0);
    d01 = v0.dot(v1);
    d11 = v1.dot(v1);
    d20 = v2.dot(v0);
    d21 = v2.dot(v1);
    denom = (d00 * d11) - (d01 * d01);
    
    try:
        v = (d11 * d20 - d01 * d21) / denom;        
    except ZeroDivisionError:
        problems = True;
        v = 0.0;
    try:
        w = (d00 * d21 - d01 * d20) / denom;
    except ZeroDivisionError:
        problems = True;
        w = 0.0;
    
    if(v > 0.95 and snapping):
        return 0.0, 1.0, 0.0,1.0, True;
    if(w > 0.95 and snapping):
            return 0.0, 0.0, 1.0,1.0, True;
    
    u = 1.0 - v - w;
    
    if(u > 0.95 and snapping):
        return 1.0, 0.0, 0.0,1.0, True;
    
    if(u < 0.0 or v < 0.0 or w < 0.0):
        return u, v, w,(u+v+w), False;

    if(snapping):    
        residue = 0.0;
        divisor = 3.0;
         
        if(u < 1.0e-01 and u > 0.0):
            residue += u;
            divisor -= 1.0;
            u = 0.0;
                 
        if(v < 1.0e-01 and v > 0.0):
            residue += v;
            divisor -= 1.0;
            v = 0.0;
                 
        if(w < 1.0e-01 and w > 0.0):
            residue += w;
            divisor -= 1.0;
            w = 0.0;
         
        if(divisor > 0.0):
            real_residue = residue / divisor;
        else:
            real_residue = 0.0;
             
        u += min(u, real_residue);
        v += min(v, real_residue);
        w += min(w, real_residue);
    
    ratio = u + v + w;
    
    
    return u,v,w,ratio, (u >= 0.0 and v >=0.0 and u >=0.0 and ratio <=1.0);

# https://blender.stackexchange.com/questions/22963/viewport-position-and-direction
def getSceneViewVector(context, coord=None):
    space_data = context.space_data;
    view_vector = Vector((0,0,0));
    if(space_data.region_3d):
        r3d = space_data.region_3d;
        view_vector = (r3d.view_rotation * Vector((0.0,0.0,-1.0))).normalized();
    return view_vector;

def getScreenLookAxis(context, location=None):
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = region.width/2.0, region.height/2.0;
    if(location is not None):
        coord = view3d_utils.location_3d_to_region_2d(region, rv3d, location);
    
    if(not coord):
        return Vector((0.0,0.0,0.0)), 0;
#     depth = Vector((0.0, 0.0, 0.0));
#     origin = 0.0, 0.0;
#     down = 0.0, 1.0;
#     right = 1.0, 0.0;
    
#     o_vector = view3d_utils.region_2d_to_location_3d(region, rv3d, origin, depth_location=depth);
#     r_vector = view3d_utils.region_2d_to_location_3d(region, rv3d, right, depth_location=depth) - o_vector;
#     d_vector = view3d_utils.region_2d_to_location_3d(region, rv3d, down, depth_location=depth) - o_vector;
    
#     r_vector.normalize();
#     d_vector.normalize();
#     print('VIEW VECTOR ::: ', o_vector, r_vector, d_vector);
    base_view = Vector((0.0, 1.0, 0.0));
#     base_view = Vector((0.0, 0.0, 1.0));
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord);
    view_vector.normalize();

    axis = base_view.cross(view_vector);
    angle = base_view.angle(view_vector);
    
    axis.normalize();
    
    return axis, math.degrees(angle);

def drawHollowCircleBillBoard(context, location, radius, resolution=20):
    fl_resolution = float(resolution);
    #Marker Highlight    
    axis, angle = getScreenLookAxis(context, location);
    bgl.glPushMatrix();
    bgl.glTranslatef(location.x, location.y , location.z);
    bgl.glPushMatrix();
    bgl.glRotatef(angle+90.0, axis.x, axis.y, axis.z);
    bgl.glPushMatrix();
#     bgl.glBegin(bgl.GL_TRIANGLE_FAN);
    bgl.glLineWidth(5.0);  
    bgl.glBegin(bgl.GL_LINE_LOOP);
    x, y = 0.0, 0.0;
    for i in range(resolution):        
        factor = (float(i) / fl_resolution) * TWOPI;
        xpos = x + (radius * math.cos(factor));
        ypos = y + (radius * math.sin(factor));
        bgl.glVertex2f(xpos, ypos);
         
    bgl.glEnd();
    bgl.glPopMatrix();
    bgl.glPopMatrix();
    bgl.glPopMatrix();

def drawPoint(location, color, size=15.0, enable_depth=False):
    if(enable_depth):
        bgl.glEnable(bgl.GL_DEPTH_TEST);
    bgl.glColor4f(*color);
    bgl.glPointSize(size);
    bgl.glBegin(bgl.GL_POINTS);
    bgl.glVertex3f(*location);
    bgl.glEnd();        
    if(enable_depth):
        bgl.glDisable(bgl.GL_DEPTH_TEST);
    
def drawRegionOfPoints(regionofpoints, color, size = 3.0, enable_depth=True,ugly=False):
    if(enable_depth):
        bgl.glEnable(bgl.GL_DEPTH_TEST);
    bgl.glColor4f(*color);
    bgl.glPointSize(size);
    bgl.glBegin(bgl.GL_POINTS);
    for region in regionofpoints:
        if(ugly):
            points = region['borders'];
        else:
            points = region['points'];
        for co in points:            
            bgl.glVertex3f(*co);
    
    bgl.glEnd();
    if(enable_depth):
        bgl.glDisable(bgl.GL_DEPTH_TEST);

def drawText(context, text, location, text_scale_value=TEXT_SCALE_VALUE, *,enable_depth = False, constant_scale=False):
    if(enable_depth):
        bgl.glEnable(bgl.GL_DEPTH_TEST);
    v3d = context.space_data;
    rv3d = v3d.region_3d;
    text_scale = text_scale_value * ((max(min(MAX_ZOOM_DISTANCE, rv3d.view_distance), MIN_ZOOM_DISTANCE)) / FRIENDLY_ZOOM_DISTANCE);    
    
    font_id = 0;
    
    axis, angle = getScreenLookAxis(context, location);
    
    bgl.glPushMatrix();
    bgl.glTranslatef(location.x, location.y , location.z);
    
    bgl.glPushMatrix();
    bgl.glRotatef(angle, axis.x, axis.y, axis.z);
    
    bgl.glPushMatrix();
    if(not constant_scale):
        bgl.glScalef(text_scale,text_scale,text_scale);
    else:
        bgl.glScalef(text_scale_value,text_scale_value,text_scale_value);
    
    bgl.glPushMatrix();
    bgl.glRotatef(90.0, 1.0, 0.0, 0.0);
    
    blf.position(font_id, 0.0, 0.0 , 0.0);
    blf.size(font_id, 72, 72);
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0);
    blf.draw(0, text);
#     blf.rotation(0, 1.57);
    bgl.glPopMatrix();
    
    bgl.glPopMatrix();
    
    bgl.glPopMatrix();
    
    bgl.glPopMatrix();

    if(enable_depth):
        bgl.glDisable(bgl.GL_DEPTH_TEST);


def drawTriangle(triangle, linethickness, linecolor, fillcolor, drawpoints=False, pointcolor=None, *, enable_depth=False):
    if(enable_depth):
        bgl.glEnable(bgl.GL_DEPTH_TEST);
    bgl.glEnable(bgl.GL_BLEND);
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA);
    bgl.glEnable(bgl.GL_LINE_SMOOTH);
    bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST);
    
#     for co in triangle:
    bgl.glColor4f(*fillcolor);
    bgl.glBegin(bgl.GL_TRIANGLES);
    
    for coord in triangle:
        bgl.glVertex3f(*coord); 
    bgl.glEnd();
    
    bgl.glColor4f(*linecolor);
    bgl.glLineWidth(linethickness);
    bgl.glBegin(bgl.GL_LINE_STRIP);
    
    for coord in triangle:
        bgl.glVertex3f(*coord);    
    
    bgl.glVertex3f(*triangle[0]);
    
    bgl.glEnd();
        
    if(drawpoints):        
        bgl.glColor4f(*pointcolor);
        bgl.glPointSize(5.0);
        bgl.glBegin(bgl.GL_POINTS);
        
        for coord in triangle:
            bgl.glVertex3f(*coord);
            
        bgl.glEnd();
        
    if(enable_depth):
        bgl.glDisable(bgl.GL_DEPTH_TEST);
        
def drawLine(a, b,*, linethickness=5, linecolor=(1,0,0,1), enable_depth = False):
    if(enable_depth):
        bgl.glEnable(bgl.GL_DEPTH_TEST);
    
    bgl.glEnable(bgl.GL_BLEND);
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA);
    bgl.glEnable(bgl.GL_LINE_SMOOTH);
    bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST);
    
    bgl.glColor4f(*linecolor);
    bgl.glLineWidth(linethickness);
    bgl.glBegin(bgl.GL_LINE_STRIP);
    
    bgl.glVertex3f(*a);
    bgl.glVertex3f(*b);
    
    bgl.glEnd();
    
    if(enable_depth):
        bgl.glDisable(bgl.GL_DEPTH_TEST);
            
            
def createIsoContourMesh(context, meshobject, isocontours, isamappedcontour = False):
    iso_name = meshobject.name+"_isocontours_"+str(meshobject.iso_mesh_count);    
    try:
        existing = context.scene.objects[iso_name];
        existing.name = "READY_FOR_DELETE";
        bpy.ops.object.select_all(action="DESELECT");
        existing.select = True;
        context.scene.objects.active = existing;
        bpy.ops.object.delete();
    except KeyError:
        pass;
    
    meshobject.iso_mesh_count += 1;
    temp_iso_name = meshobject.name+"_isocontours_"+str(meshobject.iso_mesh_count);    
    iso_mesh = bpy.data.meshes.new(temp_iso_name);
    
    all_verts_tuples = [];
    
    for segment in isocontours:
        co_start = segment['start'];
        co_end = segment['end'];
        
        tup_start = (co_start.x, co_start.y, co_start.z);
        tup_end = (co_end.x, co_end.y, co_end.z)
        
        if(tup_start not in all_verts_tuples):
            all_verts_tuples.append((co_start.x, co_start.y, co_start.z));
        
        if(tup_end not in all_verts_tuples):
            all_verts_tuples.append((co_end.x, co_end.y, co_end.z));
    
#     verts = all_verts_tuples;#list(set(all_verts_tuples));
    verts = list(set(all_verts_tuples));
    edges = [];
    kd = buildKDTree(None, None, "CUSTOM", verts);
    
    for segment in isocontours:
        co_start = segment['start'];
        co_end = segment['end'];
        
        co, index1, dist = kd.find(co_start);
        co, index2, dist = kd.find(co_end);
        
        edges.append([index1, index2]);    
    
    # Create mesh from given verts, faces.
    iso_mesh.from_pydata(verts, edges, []);
    # Update mesh with new data
    iso_mesh.update();
    
    iso_mesh_obj = bpy.data.objects.new(temp_iso_name, iso_mesh);
    iso_mesh_obj.data = iso_mesh;    
    context.scene.objects.link(iso_mesh_obj);
             
#     iso_mesh_obj.location = meshobject.location.copy();
    iso_mesh_obj.parent = meshobject;
    
    for segment in isocontours:
        co_start = segment['start'];
        co_end = segment['end'];
        
        iso_point = iso_mesh_obj.isopoints.add();
        iso_index = iso_mesh_obj.isoindices.add();
        contour_index = iso_mesh_obj.contourindices.add();
        
        co, index, dist = kd.find(co_start);
        
        iso_point.x = co_start.x;
        iso_point.y = co_start.y;
        iso_point.z = co_start.z;
        
        iso_index.index = index;
        contour_index.index = segment['contour_index'];
         
        iso_point = iso_mesh_obj.isopoints.add();
        iso_index = iso_mesh_obj.isoindices.add();
        contour_index = iso_mesh_obj.contourindices.add();
        
        co, index, dist = kd.find(co_end);
        
        iso_point.x = co_end.x;
        iso_point.y = co_end.y;
        iso_point.z = co_end.z;
        
        iso_index.index = index;
        contour_index.index = segment['contour_index'];
    
    bpy.ops.object.select_all(action="DESELECT");
    iso_mesh_obj.select = True;
    context.scene.objects.active = iso_mesh_obj;
     
    bpy.ops.object.convert(target="CURVE");
    bpy.data.curves[iso_mesh_obj.name].fill_mode = "FULL";
    bpy.data.curves[iso_mesh_obj.name].bevel_resolution = 6;
    max_dim = max(iso_mesh_obj.dimensions.x, iso_mesh_obj.dimensions.y, iso_mesh_obj.dimensions.z);
    bpy.data.curves[iso_mesh_obj.name].bevel_depth = BEVEL_DEPTH_FACTOR * max_dim;
    
    print(bpy.data.curves[iso_mesh_obj.name].bevel_depth, BEVEL_DEPTH_FACTOR * max_dim);
     
    try:
        material = bpy.data.materials['IsoContourMaterial'];
    except:
        material = bpy.data.materials.new('IsoContourMaterial');
     
    material.diffuse_color = (0.003, 0.0, 0.8);
    material.alpha = 1;
    material.specular_color = (0.003, 0.0, 0.8);
     
    iso_mesh_obj.data.materials.clear();
    iso_mesh_obj.data.materials.append(material);
    
    bpy.ops.object.select_all(action="DESELECT");
    meshobject.select = True;
    context.scene.objects.active = meshobject;
    
    return iso_mesh_obj;

def ScreenPoint3D(context, event, mesh, *, ray_max=1000.0, position_mouse = True):
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y


    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)


    if rv3d.view_perspective == 'ORTHO':
        ray_max=100000.0
        # move ortho origin back
        ray_origin = ray_origin - (view_vector * (ray_max / 2.0));


    ray_target = ray_origin + (view_vector * ray_max)


    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""


        # get the ray relative to the object
        matrix_inv = matrix.inverted();
        ray_origin_obj = matrix_inv * ray_origin;
        ray_target_obj = matrix_inv * ray_target;
        
        if((2, 76, 0) >= bpy.app.version):
            # cast the ray
            location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj);
        else:
            hit, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj);
#        hit, normal, face_index, distance = bvhtree.ray_cast(ray_origin_obj, ray_target_obj);
        
        if face_index != -1:
            return location, normal, face_index;
        else:
            return None, None, None;


    # no need to loop through other objects since we are interested in the active object only
    obj = mesh;
    if(obj):
        matrix = obj.matrix_world.copy();
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj, matrix);
            if hit is not None:
                hit_world = matrix * hit;
                return hit_world, True, face_index, hit;
    return view_vector, False, None, None;


# ALL PROPERTIES UPDATE AND HELPER METHODS 

def fillMeshType(self, context):
    if(context.active_object.meshtype == "Source"):
        context.active_object.issourcemesh = True;
        context.active_object.istargetmesh = False;
        context.active_object.ishummaobject = True;
        
    
    if(context.active_object.meshtype == "Target"):
        context.active_object.issourcemesh = False;
        context.active_object.istargetmesh = True;
        context.active_object.ishummaobject = True;

def fillMappingMesh(self, context):
    if(context.active_object.issourcemesh):
        context.active_object.mappedtargetmeshname = context.active_object.selecttarget;
    if(context.active_object.istargetmesh):
        context.active_object.mappedsourcemeshname = context.active_object.selectsource;

def get_scene_meshes(self, context):
    templatenames = ["_marker","_joint","_bone","_lines","_cloud"];
#     if(context.active_object):
#         templatenames.append(context.active_object.name);
    return [(item.name, item.name, item.name) for item in bpy.data.objects if item.type == "MESH" and not any(word in item.name for word in templatenames)];

def updateIsoLinesCount(self, context):
    context.scene.isolinesupdated = False;


#Methods related to isolines transfer below


def getTriangleMappedPoints(subject, reference ,subject_face, subject_correspondencemap = None):
    if(not subject_correspondencemap):
        cmap = subject.correspondencemap;
    else:
        cmap = subject_correspondencemap;
        
    subject_loops = subject.data.loops;
    citem1 = cmap[subject_loops[subject_face.loop_indices[0]].vertex_index];
    citem2 = cmap[subject_loops[subject_face.loop_indices[1]].vertex_index];
    citem3 = cmap[subject_loops[subject_face.loop_indices[2]].vertex_index];
    
    co1 = getGeneralCartesianFromPolygonFace(citem1.mappedbaryratios, reference.data.polygons[citem1.mappedfaceid - 1], reference);
    co2 = getGeneralCartesianFromPolygonFace(citem2.mappedbaryratios, reference.data.polygons[citem2.mappedfaceid - 1], reference);
    co3 = getGeneralCartesianFromPolygonFace(citem3.mappedbaryratios, reference.data.polygons[citem3.mappedfaceid - 1], reference);
    
    return co1, co2, co3;
    
def getBarycentricValue(context, mesh, face, point):
    vertices = mesh.data.vertices;
    loops = mesh.data.loops;
    a = vertices[loops[face.loop_indices[0]].vertex_index];
    b = vertices[loops[face.loop_indices[1]].vertex_index];
    c = vertices[loops[face.loop_indices[2]].vertex_index];
    u,v,w,ratio,isinside = getBarycentricCoordinate(point, a.co, b.co, c.co,snapping=False);    
    return u, v, w;

def getMappedContourSegments(context, subject, reference, isocontours, reference_meshnames=[]):
    bvhtree = BVHTree.FromObject(subject, context.scene);
    
    mappedcontours = [];
    references = [];
    
    if(len(subject.multimaps)):
        for mname in reference_meshnames:
            mappedcontours.append([]);
            references.append(bpy.data.objects[mname]);
    else:
        mappedcontours.append([]);
    
        
    for segment in isocontours:
        co_start = segment['start'];
        co_end = segment['end'];
        
        if((2, 76, 0) < bpy.app.version):
            co_s, n, index1, distance = bvhtree.find(co_start);
            co_e, n, index2, distance = bvhtree.find(co_end);
        else:
            co_s, n, index1, distance = bvhtree.find_nearest(co_start);
            co_e, n, index2, distance = bvhtree.find_nearest(co_end);
        
        u1, v1, w1 = getBarycentricValue(context, subject, subject.data.polygons[index1], co_s);
        u2, v2, w2 = getBarycentricValue(context, subject, subject.data.polygons[index2], co_e);
        
        if(len(subject.multimaps)):
            for index, mmap in enumerate(subject.multimaps):
                reference = references[index];
                map_co_s_1, map_co_s_2, map_co_s_3 = getTriangleMappedPoints(subject, reference, subject.data.polygons[index1], mmap.map_items);
                map_co_e_1, map_co_e_2, map_co_e_3 = getTriangleMappedPoints(subject, reference, subject.data.polygons[index2], mmap.map_items);
                
                map_co_start = getGeneralCartesianFromBarycentre([u1, v1, w1], [map_co_s_1, map_co_s_2, map_co_s_3]);
                map_co_end = getGeneralCartesianFromBarycentre([u2, v2, w2], [map_co_e_1, map_co_e_2, map_co_e_3]);
                
                mapped_segment = {'start':map_co_start, 'end':map_co_end, 'contour_index':segment['contour_index']};
                mappedcontours[index].append(mapped_segment);                
        
        else:
            map_co_s_1, map_co_s_2, map_co_s_3 = getTriangleMappedPoints(subject, reference, subject.data.polygons[index1]);
            map_co_e_1, map_co_e_2, map_co_e_3 = getTriangleMappedPoints(subject, reference, subject.data.polygons[index2]);
            
            map_co_start = getGeneralCartesianFromBarycentre([u1, v1, w1], [map_co_s_1, map_co_s_2, map_co_s_3]);
            map_co_end = getGeneralCartesianFromBarycentre([u2, v2, w2], [map_co_e_1, map_co_e_2, map_co_e_3]);
            
            mapped_segment = {'start':map_co_start, 'end':map_co_end, 'contour_index':segment['contour_index']};
            mappedcontours[0].append(mapped_segment);
    
    return mappedcontours;

