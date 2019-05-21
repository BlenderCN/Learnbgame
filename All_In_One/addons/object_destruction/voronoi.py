import platform
from time import clock
#from concurrent.futures import ThreadPoolExecutor, wait
#import threading
import math

if platform.architecture()[0] == "64bit":
    if platform.architecture()[1] == "ELF":
        from object_destruction.libvoro.linux64 import voronoi
    elif platform.architecture()[1] == "WindowsPE":
        from object_destruction.libvoro.win64 import voronoi
    else:
        from object_destruction.libvoro.osx64 import voronoi
elif platform.architecture()[0] == "32bit":
    if platform.architecture()[1] == "ELF":
        from object_destruction.libvoro.linux32 import voronoi
    elif platform.architecture()[1] == "WindowsPE":
        from object_destruction.libvoro.win32 import voronoi
    else:
        from object_destruction.libvoro.osx32 import voronoi

#from object_destruction.libvoro import voronoi
import random
from mathutils import Vector
import bpy
from bpy import ops
import bmesh

from . import destruction_data as dd

#start = 0

selected = {}
#

def bracketPair(line, lastIndex):
    opening = line.index("(", lastIndex)
    closing = line.index(")", opening)
    
   # print(opening, closing)
    values = line[opening+1:closing]
    vals = values.split(",")
    return vals, closing
    
def parseFile(name):
#    read array from file
     file = open(name)
     records = []
     for line in file:
         verts = []
         faces = []
         areas = []
    #    #have a big string, need to parse ( and ), then split by ,
         #vertex part
         next = None
         lastIndex = 0
         while next != 'v':
            vals, closing = bracketPair(line, lastIndex)
            x = float(vals[0])
            y = float(vals[1])
            z = float(vals[2])
            verts.append((x,y,z))
            lastIndex = closing
            next = line[closing+2]
        
         while True:
            facetuple = []
          #  print(lastIndex, len(line), next)
            try:
                vals, closing = bracketPair(line, lastIndex)
                for f in vals:
                    facetuple.append(int(f))
                faces.append(facetuple)
                lastIndex = closing
            except ValueError:
                break
        
       #  print("VERTSFACES:", verts, faces) 
         records.append({"v": verts, "f": faces})
     return records    

def buildCell(cell, name, walls, diff, mat_index, re_unwrap, smart_angle, dissolve_angle):
 # for each face
    #global start
    
    verts = []
    faces = []
    edges = []
    
    for i in range(0, len(cell["f"])):
        v = []
        #get corresponding vertices
        for index in cell["f"][i]:
          #  print(index)
            vert = cell["v"][index]
            v.append(vert)
            if vert not in verts:
                verts.append(vert)
                    
        for j in range(1, len(v)-1):
            index = verts.index(v[0])
            index1 = verts.index(v[j])
            index2 = verts.index(v[j+1]) 
            
            if (index == index1) or (index == index2) or \
            (index2 == index1):
                continue
            else: 
                faces.append([index, index1, index2])
            #assert(len(set(faces[-1])) == 3)
            
  #  lock.acquire()
     
    nmesh = bpy.data.meshes.new(name = name)
    nmesh.from_pydata(verts, edges, faces)
    
    ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = name
    orig = bpy.context.scene.objects[name]
    obj.parent = orig.parent
   
    obj.data = None
    #nmesh.update(calc_edges=True) 
    #nmesh.validate()    
    obj.data = nmesh
    obj.select = True
    ops.object.origin_set(type='ORIGIN_GEOMETRY')
    #ops.object.material_slot_copy()
    
    mesh_src = orig.data
    for mat in mesh_src.materials:
        obj.data.materials.append(mat)
    obj.select = False
    
    ops.object.mode_set(mode = 'EDIT')
    ops.mesh.select_all(action = 'SELECT')
    ops.mesh.remove_doubles(threshold = 0.0001)
    ops.mesh.normals_make_consistent(inside=False)
    
    #if walls:
    ops.mesh.dissolve_limited(angle_limit = dissolve_angle)
        
    ops.object.mode_set(mode = 'OBJECT')
    
    if not walls:
       fixNonManifolds(obj)
       
       #simply assign inner material to all faces
       if mat_index != 0:
           for p in obj.data.polygons:
                p.material_index = mat_index
       
       if re_unwrap:
           bpy.context.scene.objects.active = obj
           ops.object.mode_set(mode = 'EDIT')
           ops.mesh.select_all(action = 'SELECT')
           ops.mesh.mark_seam()
           ops.uv.smart_project(angle_limit = smart_angle)
           ops.object.mode_set(mode = 'OBJECT')
               
       #let boolean handle the material assignment !      
       booleanIntersect(bpy.context, obj, orig, diff, dissolve_angle)
       
#    lock.release()
    return obj
    
   
    
    #print("Object assignment Time ", clock() - start)
   # start = clock()
    
         
def buildCellMesh(cells, name, walls, diff, mat_index, re_unwrap, smart_angle, dissolve_angle):      
    

#     lock = threading.Lock()     
#     threads = [threading.Thread(target=buildCell, args=(cell, name, walls, lock)) for cell in cells]
#
#     print("Starting threads...")
#        
#     for t in threads:
#        t.start()
#        
#     print("Waiting for threads to finish...")
#        
#     for t in threads:
#        t.join()       
    objs = []   
    for cell in cells: 
        objs.append(buildCell(cell, name, walls, diff, mat_index, re_unwrap, smart_angle, dissolve_angle))
        
        ob = bpy.context.scene.objects[name] 
        if ob.destruction.use_debug_redraw:
            bpy.context.scene.update()
            ob.destruction._redraw_yasiamevil()
        
    #    prog = round(float(cells.index(cell)+1) / float(len(cells)), 2)
        
     #   if walls:
     #       prog = prog * 100
    #    else:
    #        prog = prog * 50   #because there comes the boolean step too 
    #    
       # ob.destruction.fracture_progress(str(prog))
        
        
    return objs
        

def corners(obj, impactLoc = Vector((0,0,0))):
    
    bbox = obj.bound_box.data 
    dims = bbox.dimensions
    loc = bbox.location.copy()
    loc += impactLoc
    print("corners impact:", impactLoc)
    
    lowCorner = (loc[0] - dims[0] / 2, loc[1] - dims[1] / 2, loc[2] - dims[2] / 2)
    xmin = lowCorner[0]
    xmax = lowCorner[0] + dims[0]
    ymin = lowCorner[1]
    ymax = lowCorner[1] + dims[1]
    zmin = lowCorner[2]
    zmax = lowCorner[2] + dims[2]
    
    return xmin, xmax, ymin, ymax, zmin, zmax 

def deselect(obj):
    selected[obj] = obj.select
    obj.select = False

def select(obj):
    if obj in selected.keys():
        obj.select = selected[obj]    

def fixNonManifolds(obj):
    
    bpy.context.scene.objects.active = obj
    try:
        ops.object.mode_set(mode = 'EDIT')
        ops.mesh.select_all(action = 'SELECT')
        ops.mesh.remove_doubles(threshold = 0.0001)
        ops.mesh.select_all(action = 'DESELECT')
        ops.mesh.select_non_manifold()
        #ops.mesh.edge_collapse()
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v for v in bm.verts if len(v.link_edges) < 3 and v.select]
        for v in verts:
            print(len(v.link_edges))
            bm.verts.remove(v)
        
        ops.mesh.select_all(action = 'DESELECT')
        ops.mesh.select_non_manifold()
        ops.mesh.edge_collapse()   
        ops.object.mode_set(mode = 'OBJECT')
    except RuntimeError:
        print("fixManifold operator error")
    
def voronoiCube(context, obj, parts, vol, walls, mat_index):
    
    re_unwrap = obj.destruction.re_unwrap
    smart_angle = obj.destruction.smart_angle
    dissolve_angle = obj.destruction.dissolve_angle
    
    #applyscale before
   # global start
    start = clock()
    loc = Vector(obj.location)
    obj.destruction.origLoc = loc
    
    if vol != None and vol != "":
        print("USING VOL")
        volobj = context.scene.objects[vol]
        volobj.select = True
        #ops.object.origin_set(type='ORIGIN_GEOMETRY')
        ops.object.transform_apply(scale=True, rotation = True)
        volobj.select = False
        
        print("I: ", dd.DataStore.impactLocation)
        vxmin, vxmax, vymin, vymax, vzmin, vzmax = corners(volobj, dd.DataStore.impactLocation - loc)
        vxmin += loc[0]
        vxmax += loc[0]
        vymin += loc[1]
        vymax += loc[1]
        vzmin += loc[2]
        vzmax += loc[2] 
        
    
    [deselect(o) for o in bpy.data.objects]
      
    context.scene.objects.active = obj    
    obj.select = True
    mesh_center = Vector((0, 0, 0))
    diff = Vector((0, 0, 0))
    oldCur = context.scene.cursor_location.copy()
    if not walls:
        
        #memorize old origin and mesh_center(bounds)
        area = None
        for a in context.screen.areas:
            if a.type == 'VIEW_3D':
                area = a
        ctx = context.copy()
        ctx["area"] = area
        
        #ops.object.mode_set(mode = 'EDIT')
        #ctx["edit_object"] = obj
        #ops.mesh.select_all(action = 'SELECT')
        ops.view3d.snap_cursor_to_selected(ctx)
        old_orig = context.scene.cursor_location.copy()
        ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        ops.view3d.snap_cursor_to_selected(ctx)
        mesh_center = context.scene.cursor_location.copy()
        #ops.mesh.select_all(action = 'DESELECT')
        #   ops.object.mode_set(mode = 'OBJECT')
        diff = old_orig - mesh_center
        print(mesh_center, old_orig, diff)
        
        obj.destruction.tempLoc = diff
        
        context.scene.cursor_location = old_orig
        ops.object.origin_set(type='ORIGIN_CURSOR')
        ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
    else:
        context.scene.cursor_location = (0, 0, 0)
        ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
    ops.object.transform_apply(scale=True, location = True, rotation=True)
    
    [select(o) for o in context.scene.objects]
  
    xmin, xmax, ymin, ymax, zmin, zmax = corners(obj)
          
    xmin += loc[0]
    xmax += loc[0]
    ymin += loc[1]
    ymax += loc[1]
    zmin += loc[2]
    zmax += loc[2] 
     
    nx = 12
    ny = 12
    nz = 12
    particles = parts

    print(xmin, xmax, ymin, ymax, zmin, zmax)
    
    if vol != None and vol != "" and context.object.destruction.voro_exact_shape:
        volobj = context.scene.objects[vol]
        particles = len(volobj.data.vertices)
    
    partsystem = None    
    if context.object.destruction.voro_particles != "":
        partsystemname = context.object.destruction.voro_particles
        volobj = context.scene.objects[vol]
        partsystem = volobj.particle_systems[partsystemname]
        particles = len(partsystem.particles)
    
    #enlarge container a bit, so parts near the border wont be cut off
    theta = 0.5
    if walls:
        theta = 10
    con = voronoi.domain(xmin-theta,xmax+theta,ymin-theta,ymax+theta,zmin-theta,zmax+theta,nx,ny,nz,False, False, False, particles)
    
    if vol != None and vol != "":
        xmin = vxmin
        xmax = vxmax
        ymin = vymin
        ymax = vymax
        zmin = vzmin
        zmax = vzmax
        print("VOL: ", xmin, xmax, ymin, ymax, zmin, zmax)
        
    
    bm = obj.data
    
    if walls:
        colist = []
        i = 0
        for poly in bm.polygons:
           # n = p.calc_center_median()
            n = poly.normal
            v = bm.vertices[poly.vertices[0]].co
            d = n.dot(v)
           # print("Displacement: ", d)
            colist.append([n[0], n[1], n[2], d, i])
            i = i+1
        
        #add a wall object per face    
        con.add_wall(colist)
    
    values = []
    
    if vol != None and vol != "" and context.object.destruction.voro_exact_shape and partsystem == None:
        volobj = context.scene.objects[vol]
        #context.scene.objects.active = volobj
        
        #volobj.select = True
       # ops.object.transform_apply(scale=True, location = True, rotation = True)
        #volobj.select = False
        
        # impact location comes from game engine, is 0 by default
        # in game engine is location of volobj 0 by default, so this expression should be correct.        
        for v in volobj.data.vertices:
            values.append((v.co[0] + dd.DataStore.impactLocation[0] + volobj.location[0], 
                           v.co[1] + dd.DataStore.impactLocation[1] + volobj.location[1], 
                           v.co[2] + dd.DataStore.impactLocation[2] + volobj.location[2]))
        #print("VER", values)
            
    elif partsystem != None:
        for p in partsystem.particles:
            values.append((p.location[0] + dd.DataStore.impactLocation[0], 
                           p.location[1] + dd.DataStore.impactLocation[1], 
                           p.location[2] + dd.DataStore.impactLocation[2]))    
    else:    
        for i in range(0, particles):
            
            print (xmin, xmax, ymin, ymax, zmin, zmax)
            randX = random.uniform(xmin, xmax)
            randY = random.uniform(ymin, ymax)
            randZ = random.uniform(zmin, zmax)
            values.append((randX, randY, randZ))
  
    for i in range(0, particles):
        x = values[i][0]
        y = values[i][1]
        z = values[i][2]
        #if con.point_inside(x, y, z):
        print("Inserting", x, y, z)
        con.put(i, x, y, z)
    
  #  d.add_wall(colist)
        
    name = obj.destruction.voro_path
    con.print_custom("%P v %t", name )
    
    del con
    
    #oldnames = [o.name for o in context.scene.objects]
   
    print("Library Time ", clock() - start)
    start = clock()
    
    records = parseFile(name)
    print("Parsing Time ", clock() - start)
    start = clock()
    
    #do a remesh here if desired and try to fix non-manifolds
    context.scene.objects.active = obj
    
    if not walls:
         
        if obj.destruction.remesh_depth > 0:
            rem = obj.modifiers.new("Remesh", 'REMESH')
            rem.mode = 'SHARP'
            rem.octree_depth = obj.destruction.remesh_depth
            rem.scale = 0.9
            rem.sharpness = 1.0
            rem.remove_disconnected_pieces = False
            #  rem.threshold = 1.0
       
            #context.scene.objects.active = obj
            ctx = context.copy()
            ctx["object"] = obj
            ctx["modifier"] = rem
            ops.object.modifier_apply(ctx, apply_as='DATA', modifier = rem.name)
        
        #[deselect(o) for o in context.scene.objects]
        
        #try to fix non-manifolds...
        #fixNonManifolds(obj)
        
    objs = buildCellMesh(records, obj.name, walls, diff, mat_index, re_unwrap, smart_angle, dissolve_angle)
    
    print("Mesh Construction Time ", clock() - start)
    
    context.scene.cursor_location = oldCur
    
    return objs
    
    
def booleanIntersect(context, o, obj, diff, dissolve_angle):  
            
    bool = o.modifiers.new("Boolean", 'BOOLEAN')
    #use the original boolean object always, otherwise boolean op errors occur...
    bool.object = obj
 #    bool.object = bpy.data.objects[obj.destruction.boolean_original]
    bool.operation = 'INTERSECT'
    
    ctx = context.copy()
    ctx["object"] = o
    ctx["modifier"] = bool
    ops.object.modifier_apply(ctx, apply_as='DATA', modifier = bool.name)
    
    ops.object.mode_set(mode = 'EDIT')
    ops.mesh.select_all(action = 'SELECT')
    ops.mesh.dissolve_limited(angle_limit = dissolve_angle)
    ops.object.mode_set(mode = 'OBJECT')
    
   # newnames = []
    #for ob in context.scene.objects:
    #   if ob.name not in oldnames and ob.name != o.name:
    #       newnames.append(ob.name)
    obj.select = False
    
    oldSel = o.select
    o.select = True
    ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    if o.parent == None:
        o.location -= diff
    o.select = oldSel
    
    ops.object.mode_set(mode = 'EDIT')    
    ops.mesh.separate(type = 'LOOSE')
    ops.object.mode_set(mode = 'OBJECT')
    
    if len(o.data.vertices) == 0:
        context.scene.objects.unlink(o)
        
    #return newnames    
   