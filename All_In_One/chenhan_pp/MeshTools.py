import bpy, bmesh, mathutils;
from mathutils import Vector;

def getBMMesh(context, obj, useeditmode = True):
#     print('GETBMMESH ::: USEEDITMODE = ', useeditmode, " MESH NAME ::: ", obj.name);
    if(not useeditmode):
        if(context.mode == "OBJECT"):
            bm = bmesh.new();
            bm.from_mesh(obj.data);
        else:
            bm = bmesh.from_edit_mesh(obj.data);


            if not obj.mode == 'EDIT':
                bpy.ops.object.mode_set(mode = 'EDIT', toggle = False);

        return bm;

    else:
        if(not context.mode == "OBJECT"):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False);

        bpy.ops.object.select_all(action='DESELECT') #deselect all object
        context.scene.objects.active = obj;
        obj.select = True;

        if not obj.mode == 'EDIT':
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
        for i, f in enumerate(mesh.polygons):
            v0 = mesh.vertices[f.vertices[0]].co;
            v1 = mesh.vertices[f.vertices[1]].co;
            v2 = mesh.vertices[f.vertices[2]].co;
            
            point = (v0 * oneby3) + (v1 * oneby3) + (v2 * oneby3);
            kd.insert(point, f.index);
    
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

        for i, co in enumerate(points):
            kd.insert(co, i);          
                
    kd.balance();
#     print('BUILD KD TREE OF SIZE : ', size, ' FOR :: ', object.name, ' USING TYPE : ', type);
    return kd;


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


