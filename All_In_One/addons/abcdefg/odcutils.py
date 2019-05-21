#----------------------------------------------------------
# File utils.py
#----------------------------------------------------------
'''
Created on Nov 20, 2012
#test commit tracker
This module has all the little extra tasks I need to keep the other code cleanish.
Things like 3d math, matrix math, selections, mundane bookkeeping, contextual management etc.

Some License might be in the source directory. Summary: don't be an asshole, but do whatever you want with this code
Author: Patrick Moore:  patrick.moore.bu@gmail.com
'''
import os
import bpy
import addon_utils
import time
import math
import random
import bmesh

import mesh_cut
from mesh_cut import edge_loops_from_bmedges
from mathutils import Vector, Matrix, Quaternion
from bpy_extras.mesh_utils import edge_loops_from_edges
from mathutils.geometry import intersect_point_line
from common_utilities import bversion

#Borrowed from retopoflow @CGCookie, Jonathan Wiliamson, Jon Denning, Patrick Moore
def get_settings():
    if not get_settings.cached_settings:
        addons = bpy.context.user_preferences.addons
        #frame = inspect.currentframe()
        #frame.f_code.co_filename
        folderpath = os.path.dirname(os.path.abspath(__file__))
        while folderpath:
            folderpath,foldername = os.path.split(folderpath)
            if foldername in {'lib','addons'}: continue
            if foldername in addons: break
        else:
            assert False, 'Could not find non-"lib" folder'
        
        get_settings.cached_settings = addons[foldername].preferences
   
    return get_settings.cached_settings

get_settings.cached_settings = None

#global universal_intntl
universal_intntl = {}
#global intntl_universal
intntl_universal = {}
international = [18,17,16,15,14,13,12,11,
                 21,22,23,24,25,26,27,28,
                 38,37,36,35,34,33,32,31,
                 41,42,43,44,45,46,47,48]
for i in range(1,33):
    intntl_universal[international[i-1]] = i
    universal_intntl[i] = international[i-1]

def unvi_to_intntl(a):
    b = universal_intntl(a)
    return b
    
#initial function for testing importing etc
def util_func(a,b,c):
    print("the util function %f and %d and %f" %(a,b,c))

def list_shift(seq, n):
    n = n % len(seq)
    return seq[n:] + seq[:n]
   
def running_sum(a):
    tot = 0
    for item in a:
        tot += item
    return tot
    
def project_report(scene):
    if scene.odc_props:
        for pair in scene.odc_props.items():
            print(pair)
    if scene.odc_teeth:
        for tooth in scene.odc_teeth:
            print(tooth.name)
            for pair in tooth.items():
                print(pair)
                
    if scene.odc_implants:
        for tooth in scene.odc_implants:
            print(tooth.name)
            for pair in tooth.items():
                print(pair)
                
    if scene.odc_bridges:
        for tooth in scene.odc_bridges:
            print(tooth.name)
            for pair in tooth.items():
                print(pair)
                
    if scene.odc_splints:
        for tooth in scene.odc_splints:
            print(tooth.name)
            for pair in tooth.items():
                print(pair)

#TODO: Layers get messed up if in another layer when object added.  make sure layer management forces other layers off....
#TODO: Using layers may cause data access problems...may have to manage this in scene preservation/reconstruction
def scene_preserv(context, objects = True, tools = True, space = True, debug = False):
    '''
    #TODO: write this docstring
    basically collects a lot of settings so you can mess with them
    in an operator and then put everytying back like you found it.
    '''
    if debug:
        start = time.time()
    ret_list = []
    
    if objects:
        objects_dict = {}
        for setting in ["object","selected_objects","mode"]:
            objects_dict[setting] = getattr(context, setting)
        
        hidden_obs = [ob for ob in bpy.data.objects if ob.hide]
        objects_dict["hidden"] = hidden_obs
        ret_list.append(objects_dict)
        
    if tools:
        tools_dict = {}
        for setting in ["vertex_group_weight", "mesh_select_mode","use_proportional_edit_objects", "proportional_edit", "proportional_edit_falloff","proportional_size","use_snap","snap_element"]:
            tools_dict[setting] = getattr(context.tool_settings, setting)
        ret_list.append(tools_dict)
    
    if space:   
        space_dict = {}
        for setting in ["pivot_point","transform_orientation","use_pivot_point_align","use_occlude_geometry","show_manipulator"]:
            space_dict[setting] = getattr(context.space_data, setting)
        
        ret_list.append(space_dict)
    
    if debug:    
        print('preserved the scene in %f seconds' % (time.time() - start))
    elif debug > 1:
        for key in objects_dict.keys():
            print("%s : %s" % (key, objects_dict[key]))
    
    return ret_list

def scene_reconstruct(context, obj_dict = {}, tools_dict = {}, space_dict = {}, debug = False):
    '''
    #TODO: write this docstring
    basically collects a lot of settings so you can mess with them
    in an operator and then put everytying back like you found it.
    '''
    if debug:
        start = time.time()
    
    if obj_dict:
        context.scene.objects.active = obj_dict["object"]
        for ob in bpy.data.objects:
            if ob in obj_dict["selected_objects"]:
                ob.select = True
            else:
                ob.select = False
            if ob in obj_dict["hidden"]:
                ob.hide = True
            else:
                ob.hide = False
                
        if context.mode != obj_dict["mode"]:
            if 'EDIT' in obj_dict["mode"]:
                bpy.ops.object.mode_set(mode='EDIT')
            else:
                bpy.ops.object.mode_set(mode=obj_dict["mode"])
        
    if tools_dict:
        for setting in tools_dict.keys():
            setattr(context.tool_settings, setting, tools_dict[setting])
        
    
    if space_dict:   
        for setting in space_dict.keys():
            setattr(context.space_data, setting,space_dict[setting])

    
    if debug:    
        print('reconstructed the scene in %f seconds' % (time.time() - start))
        
    return None
    
def get_all_addons(display=False):
    """
    Prints the addon state based on the user preferences.
    """
    import sys
    # RELEASE SCRIPTS: official scripts distributed in Blender releases
    paths_list = addon_utils.paths()
    addon_list = []
    for path in paths_list:
        bpy.utils._sys_path_ensure(path)
        for mod_name, mod_path in bpy.path.module_names(path):
            is_enabled, is_loaded = addon_utils.check(mod_name)
            addon_list.append(mod_name)
            if display:  #for example
                print("%s default:%s loaded:%s"%(mod_name,is_enabled,is_loaded))
            
    return(addon_list)

def get_com(me,verts,mx):
    '''
    args:
        me - the Blender Mesh data
        verts- a list of indices to be included in the calc
        mx- thw world matrix of the object, if empty assumes unity
        
    '''
    if not mx:
        mx = Matrix()
    COM = Vector((0,0,0))
    l = len(verts)
    for v in verts:
        COM = COM + me.vertices[v].co  
    COM = mx  * (COM/l)

    return COM

def get_com_bme(bme,vert_inds,mx):
    '''
    args:
        me - the Blender Mesh data
        verts- a list of indices to be included in the calc
        mx- thw world matrix of the object, if empty assumes unity
        
    '''
    if not mx:
        mx = Matrix()
    COM = Vector((0,0,0))
    l = len(vert_inds)
    for v in vert_inds:
        COM = COM + bme.verts[v].co  
    COM = mx  * (COM/l)

    return COM

def primitive_flattened_cylinder(R, r, N, H):
    #http://mathworld.wolfram.com/Circle-LineIntersection.html
    if r >= R:
        #make a primitive cylinder and return it
        bm = bmesh.new()
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=N, diameter1=R, diameter2=R, depth=H)
        for vert in bm.verts:
            vert.co[2] += H/2
            
        return bm
    
    xr = (R*R - r*r)**0.5
    xs = []
    ys = []
    inserts = []
    
    toggle = True
    for i in range(0,N):
        x = R * math.cos(i * 2 * math.pi / N)
        y = R * math.sin(i * 2 * math.pi / N)
        
        if abs(x) <= xr:
            if toggle == True:
                toggle = False
                inserts.append(i)    
            
            if y < 0:
                ys.append(-r)
            else:
                ys.append(r)
            
        else:
            if toggle == False:
                toggle = True
                inserts.append(i)
                   
            ys.append(y)
        
        xs.append(x)
        
    xs.insert(inserts[0],xr)
    xs.insert(inserts[1]+1,-xr)
    xs.insert(inserts[2]+2,-xr)
    xs.insert(inserts[3]+3,xr)
        
    ys.insert(inserts[0],r)
    ys.insert(inserts[1]+1,r)
    ys.insert(inserts[2]+2,-r)
    ys.insert(inserts[3]+3,-r)
    
    print(xs)
    print(ys)
    print(inserts)
    print(xr)
    
    bm = bmesh.new()
    bmverts = []
    for i in range(0,len(xs)):
        
        bmverts.append(bm.verts.new((xs[i], ys[i], 0)))
        bmverts.append(bm.verts.new((xs[i], ys[i], H)))
        
            
    for i in range(0,N+3):
        new_face = bm.faces.new((
                                 bmverts[2*i+2],
                                 bmverts[2*i+3],
                                 bmverts[2*i+1],
                                 bmverts[2*i], 
                                 ))
    new_face = bm.faces.new((
                                 bmverts[0],
                                 bmverts[1],
                                 bmverts[2*(N+4)-1],
                                 bmverts[2*(N+4)-2] 
                                 ))
    
    top_verts = [bmverts[2*i] for i in range(0,N+4)]
    bottom_verts = [bmverts[2*i+1] for i in range(0,N+4)]
    top_verts.reverse()
    
    end_cap = bm.faces.new(tuple(top_verts))
    end_cap = bm.faces.new(tuple(bottom_verts))  
    return bm

def primitive_wedge_cylinder(R, pct, N, H):
    '''
    not precise, will round to nearest integer vert.
    Radius
    pct: fraction of circle to make.  between 0 and 1
    N: Resolution of circle
    H: Height of cylinder
    '''

    if pct >= .99 or pct < .1:
        #error, bad input...
        bm = bmesh.new() 
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=N, diameter1=R, diameter2=R, depth=H)
        for vert in bm.verts:
            vert.co[2] += H/2
            
        return bm
        
    #start out with a 0 vert
    xs = [0]
    ys = [0]
    Nmax = round(pct*N) + 1
    for i in range(0,Nmax):
        x = R * math.cos(i * 2 * math.pi / N)
        y = R * math.sin(i * 2 * math.pi / N)
        
        xs.append(x)
        ys.append(y)
    
    bm = bmesh.new()
    bmverts = []
    for i in range(0,len(xs)):
        
        bmverts.append(bm.verts.new((xs[i], ys[i], 0)))
        bmverts.append(bm.verts.new((xs[i], ys[i], H)))
        
            
    for i in range(0,Nmax):
        new_face = bm.faces.new((
                                 bmverts[2*i], 
                                 bmverts[2*i+2], 
                                 bmverts[2*i+3], 
                                 bmverts[2*i+1]))
    new_face = bm.faces.new((
                             bmverts[0], 
                             bmverts[1],
                             bmverts[2*(Nmax+1)-1], 
                             bmverts[2*(Nmax+1)-2]))
    
    top_verts = [bmverts[2*i+1] for i in range(0,Nmax+1)]
    bottom_verts = [bmverts[2*i] for i in range(0,Nmax+1)]
    bottom_verts.reverse()
    
    top = bm.faces.new(tuple(top_verts))
    bottom = bm.faces.new(tuple(bottom_verts))  
    return bm
        
def get_bbox_center(ob, world = True):
    
    if world:
        mx = ob.matrix_world
    else:
        mx = Matrix.Identity(3)
        
    box = Vector((0,0,0))
    for v in ob.bound_box:
        box += mx * Vector(v)
    box *= 1/8
    
    return box

def bbox_to_lattice(scene, ob):
    
    mx = ob.matrix_world
    loc = get_bbox_center(ob, world=True)
    size = Vector((ob.dimensions[0], ob.dimensions[1], ob.dimensions[2]))
    
    lat_data = bpy.data.lattices.new(ob.name[0:2] + "_control")
    
    
    lat = bpy.data.objects.new(lat_data.name, lat_data)
    
    
    lat.location = loc
    lat.scale = 1.05*size
    lat.layers[1] = True
    lat.layers[0] = True
    
    
    if lat.rotation_mode != 'QUATERNION':
        lat.rotation_mode = 'QUATERNION'
        
    
    lat.rotation_quaternion = mx.to_quaternion()
    
    lat.update_tag()
    scene.objects.link(lat)
    
    scene.update()
    lat.data.points_u = 3
    lat.data.points_v = 3
    lat.data.points_w = 3
    
    
    lat_mod = ob.modifiers.new('Lattice','LATTICE')
    
    lat_mod.object = lat
    return lat  #in case you want to delete it after youe apply it.

def box_feature_locations(ob, specify):
    '''
    returns the location on the bounding box in global coords
    args:
      ob - blender object
      specify - vector of type Mathutils Vector specifying location eg.. which corner, edge or face
    examples:
      vector = ((0,0,1)) :: middle of top face
      vector = ((-1,-1,0)) :: left, back, edge midpoint
      vector = ((1,-1,1))  :: right, back, top corner
    '''    
    #construct the correct matrix
    xyz = Matrix()
    xyz = xyz.to_3x3()
    
    for i in range(0,3):
        for j in range(0,3):
            if i == j:
                xyz[j][i] = specify[i]
    
    dim = ob.dimensions    
    #calc bbox_center
    b_cent = get_bbox_center(ob, world=True)
    location = b_cent + ob.matrix_world.to_quaternion() * (xyz * dim/2)
    
    return location
        
def get_linear_density(me, edges, mx = None, debug = False):
    '''
    args:
        me - the Blender Mesh data
        edges - the mesh edges to be calculated
        mx- the world matrix of the object, if empty assumes unity and will return local value
    
    return: average vert spacing of edges    
    '''
    if debug:
        start = time.time()
        
    if not mx:
        mx = Matrix.Identity(3)
    
    N_edges = len(edges)
    sum_edge_length = 0
    for e in edges:
        v0= mx * me.vertices[e.vertices[0]].co
        v1= mx * me.vertices[e.vertices[1]].co
        V = Vector(v1 - v0)
        sum_edge_length += pow((V.length*V.length),.5)
    
    linear_density = sum_edge_length/N_edges
    
    if debug:
        time_taken = time.time() - start
        print("calced the linear density of %d edges in %f seconds" % (N_edges, time_taken))
        
    return linear_density

def edge_loop_curvature(me, edges, neighbors = 3, mx = None, debug = False, assume_even = True):
    '''
    args:
        me - the Blender Mesh data
        edges - the mesh edges to be calculated
        mx- the world matrix of the object, if empty assumes unity and will return local values
    
    return: a dict of curvature values and vertex indices
    '''
    if debug:
        start = time.time()
        
    if not mx:
        mx = Matrix.Identity(3)
    
    if assume_even:
        s_len = get_linear_density(me, edges, mx, debug = False)
        
    loops = edge_loops_from_edges(me, edges)
    if len(loops)>1:
        longest_loop_index = 0
        biggest_len = 0
        for i, loop in enumerate(loops):
            if len(loop) > biggest_len:
                biggest_len = len(loop)
                longest_loop_index = i
    
    #later add support to return as many lists as there are loops            
    verts_indx_order = loops[longest_loop_index]
    
    #test if cyclic or not (edge_loops_from_edges will repeat first index at end of list if closed loop)
    linear = verts_indx_order[0] != verts_indx_order[-1]
    if not linear:
        verts_indx_order.pop()
    
    #one less vertex than indices in the list if cyclic
    N_verts = len(verts_indx_order)
    
    verts =  [me.vertices[i] for i in verts_indx_order]
    
    #forward vector representation of all the edges
    ed_vecs = [verts[i+1].co - verts[i].co for i in range(0,len(verts)-2)]
    if not linear:
        ed_vecs.append(verts[0].co - verts[-1].co)

    curvatures = [0]*N_verts - neighbors * 2 * linear
    indices = [0]*N_verts - neighbors * 2 * linear
    
    
    
    #linear indexing starts 0 +neigbors to len(verts) -1 - neighbors
    #cyclic indexing starts 0 - neighbors to len(verts) -1 - neighbors
    for i in range(neighbors, N_verts -1 - neighbors):
        d_thetas = [0]*neighbors
        curve = 0
        
        if not assume_even:
            s_len = 0
            
        for n in range(0,neighbors):
            d_thetas = ed_vecs[i-1-n].angle(ed_vecs[i+n])
            if not assume_even:
                s_len += ed_vecs[i-1-n].length + ed_vecs[i+n].length
            
            #this results in a 1/n weighted average
            curve += 1/(2 * neighbors) * (neighbors - n) * (1/((2 * (n + 1) * s_len)))
        
        curvatures[i - neighbors] = curve
        indices = verts_indx_order[i]
        
    if debug:
        time_taken = time.time() - start
        print("calced discrete curvature of %d verts in %f seconds" % (N_verts,time_taken))
        
    return curvatures     

def active_tooth_from_index(scene):
    j = scene.odc_tooth_index
    tooth = scene.odc_teeth[j]
    return tooth

def parent_in_place(child,parent):
    '''
    context, selection, hidden etc insensitive parenting
    args: child and parent are blender objects
    Return: finished? nothing?
    '''
    current_matrix = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = current_matrix
       
def active_odc_item_candidate(items, ob, exclude, debug = False):
    '''
    items: ToothRestoration, Bridge Restoration or Implant Restoration in scene.odc_teeth (collection of ToothRestorations)
    objects: list of blender objects
    exclude: properties to exclude for guessing which tooth is being workied on...eg, mesial, distal
    
    return: ODC Tooth object wich has this Blender Object as one of it's property values
    
    iteartes through the props in a property group and tests the object's name agains it
    '''
    candidate = None
    for tooth in items:
        prop_keys = tooth.keys()
        prop_vals = tooth.values()
        
        if ob.name in prop_vals:
            n = prop_vals.index(ob.name)
            this_key = prop_keys[n]
            if debug:
                print("found the object named %s as the property value: %s" %(ob.name, this_key))
            if this_key and (this_key not in exclude):
                candidate = tooth
                
    return candidate

def splint_selction(context):
    '''
    looks at addon preferences
    returns a list,
    '''
    sce = context.scene
    splint = None
    settings = get_settings()
    b = settings.behavior
    behave_mode = settings.behavior_modes[int(b)]
    
    if behave_mode == 'LIST':
        #choose just one tooth in the list
        splint = sce.odc_splints[sce.odc_splint_index]
        
        
    elif behave_mode == 'ACTIVE':
        #test the active object, if nothing...default to item_list
        if context.object:
            ob = context.object
            tooth = active_odc_item_candidate(sce.odc_splints, ob,[])
            if tooth:
                splint = tooth
    
    if splint == None:
        splint = sce.odc_splints[sce.odc_splint_index]
                    
    return [splint]

def tooth_selection(context):
    '''
    looks at addon preferences and selected objects in scene
    returns a list or selected units
    '''
    sce = context.scene
    selected_items = []

    if not hasattr(sce, "odc_props"):
        print('addon may be broken')
        return selected_items
    settings = get_settings()
    b = settings.behavior
    behave_mode = settings.behavior_modes[int(b)]
    
    if behave_mode == 'LIST' and len(context.scene.odc_teeth):
        #choose just one tooth in the list
        tooth = sce.odc_teeth[sce.odc_tooth_index]
        selected_items.append(tooth)
        
    elif behave_mode == 'ACTIVE':
        #test the active object, if nothing...default to item_list
        if context.object and context.object.select == True:
            ob = context.object
            tooth = active_odc_item_candidate(sce.odc_teeth, ob,[])
            if tooth:
                selected_items.append(tooth)
                #sce.odc_tooth_index = sce.odc_teeth.find(tooth.name) #force the active tooth index..seems like a good idea?

    elif behave_mode == 'ACTIVE_SELECTED':
        #test active object and selected objects
        if context.object and context.object.select == True:
            #test the active object
            ob = context.object
            tooth = active_odc_item_candidate(sce.odc_teeth, ob,[])
            if tooth and tooth not in selected_items:
                selected_items.append(tooth)
        
        if context.selected_editable_objects and context.object:
            obs = [ob for ob in context.selected_editable_objects if ob.name != context.object.name]
            for ob in obs:
                tooth = active_odc_item_candidate(sce.odc_teeth, ob,[])
                if tooth and tooth not in selected_items:
                    selected_items.append(tooth)
    
    if len(selected_items) == 0 and len(context.scene.odc_teeth): #meaning previous method found nothing
        tooth = sce.odc_teeth[sce.odc_tooth_index]
        selected_items.append(tooth)                
    
    return selected_items
            
def implant_selection(context):
    '''
    looks at addon preferences
    returns a list,
    '''
    
    sce = context.scene
    implants = []
    if not hasattr(sce, 'odc_props'): return implants
    if len(context.scene.odc_implants) == 0: return implants
    
    settings = get_settings()
    b = settings.behavior
    behave_mode = settings.behavior_modes[int(b)]
    
    if len(context.scene.odc_implants) == 0:
        return implants
    
    if behave_mode == 'LIST'and len(context.scene.odc_implants):
        #choose just one tooth in the list
        implant = sce.odc_implants[sce.odc_implant_index]
        implants.append(implant)
        
    elif behave_mode == 'ACTIVE':
        #test the active object, if nothing...default to item_list
        if context.object:
            ob = context.object
            implant = active_odc_item_candidate(sce.odc_implants, ob,[])
            if implant:
                implants.append(implant)
                #sce.odc_tooth_index = sce.odc_teeth.find(tooth.name) #force the active tooth index..seems like a good idea?
    elif behave_mode == 'ACTIVE_SELECTED':
        #test active object and selected objects
        if context.object:
            #test the active object, if nothing...default to item_list
            ob = context.object
            implant = active_odc_item_candidate(sce.odc_implants, ob,[])
            if implant and implant not in implants:
                implants.append(implant)
        
        if context.selected_editable_objects and context.object:
            obs = [ob for ob in context.selected_editable_objects if ob.name != context.object.name]
            for ob in obs:
                implant = active_odc_item_candidate(sce.odc_implants, ob,[])
                if implant and implant not in implants:
                    implants.append(implant)

    if len(implants) == 0 and len(context.scene.odc_implants): #meaning previous method found nothing
        implant = sce.odc_implants[sce.odc_implant_index]
        implants.append(implant) 
                           
    return implants

    '''    
    if context.object:
        tooth_candidates = active_odc_item_candidate(sce.odc_teeth, [context.selected_editable_objects],[])
        if tooth_candidates:
            tooth = sce.odc_teeth[tooth_candidates[0]]
            sce.odc_tooth_index = sce.odc_teeth.find(tooth.name) #force the active tooth index..seems like a good idea?
    if not tooth:
        self.report({'WARNING'},"I'm not sure which tooth you want, guessing based on active tooth in list")
        tooth = sce.odc_teeth[sce.odc_tooth_index]
    return tooth 
    '''

def add_proximity_mod(ob1, ob2, min_d, max_d, group_name = None, n = None, over = 0):
    '''
    args:
        ob1 - object to have mod added to
        ob2 - target object for modifier calc
        group - NAME of vertex group for modifier to affect, if None, will make a new one.
        min_d - minimum distance
        max_d - max distance to color
        n - place in mod stack.  None goes to end.
        over = value to overwrite the Proximity vertex group with first.  None to leave group as is
        
    '''
    #pre-op setting code
    
    #make sure ob1 is how it needs to be
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = ob1
    ob1.select = True
    
    #take care of vertex group business
    group = None
    if group_name:
        group = ob1.vertex_groups.get(group_name)
    if not group:
        group = ob1.vertex_groups.get("Proximity")
        if not group:
            n=len(ob1.vertex_groups)
            bpy.ops.object.vertex_group_add()
            ob1.vertex_groups[n].name = "Proximity"
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.context.tool_settings.vertex_group_weight = 1
            bpy.context.tool_settings.mesh_select_mode = [True,False,False]
            bpy.ops.object.vertex_group_set_active(group = 'Proximity')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode='OBJECT')
            group = ob1.vertex_groups[n]
    
    i=len(ob1.modifiers)
    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_PROXIMITY')
    mod = ob1.modifiers[i]
    mod.target=ob2
    mod.proximity_mode = 'GEOMETRY'
    mod.proximity_geometry = {'EDGE','VERTEX','FACE'}
    mod.min_dist = min_d
    mod.max_dist = max_d
    mod.vertex_group=group.name
    
    return mod

def scale_vec_mult(a,b):
    '''
    performs item wise multiplication return Vec(a0*b0,a1*b1,a2*b2)
    args:
    a - vector of type mathutils.Vector
    b - vector of type mathutils.Vector
    '''
    out = Vector((a[0]*b[0],a[1]*b[1],a[2]*b[2]))
    return out

def extrude_edges_in(me, edges, mx, axis, res, debug = False):

    '''
    takes a CLOSED LOOP of edges and moves them in
    eg..take a  loop and turn it into a railroad track
    
    sorry for the naming convetion...doesn't actually extrude them, just moves them.
    you should extrude them first
    
    needs an axis to move perpendicular too...typically 3d view direction
    args:
        me - Blender Mesh Data
        edges - edges (not indices of edges) that form a closed loop
        mx  - world matrix of object
        z - the world axis which to extrude perpendicular to type Vector...probably the insertion axis
        res - distance step for each extrusion...world size
    '''
    if debug:
        start = time.time() #monitor performance
    
    #take the appropriate steps to go to local coords
    imx = mx.copy()
    imx.invert()
    irot = imx.to_quaternion()
    iscl = imx.to_scale() 
    z = irot*axis
    
    verts_in_order = edge_loops_from_edges(me,edges)
    verts_in_order = verts_in_order[0]
       
    verts_in_order.append(verts_in_order[1]) #the first (n=0) element of the list already repeated, adding the 2nd to the end as well.
    l = len(verts_in_order)    
    verts_alone = verts_in_order[0:l-2]
    
    
    lerps = [Vector((0,0,0))]*(l-2)
    vcoords = [me.vertices[index].co for index in verts_in_order]
    curl = 0
    
    for n in range(0,l-2):

        #Vec representation of the two edges
        V0 = (vcoords[n+1] - vcoords[n])
        V1 = (vcoords[n+2] - vcoords[n+1])
        
        ##XY projection
        T0 = V0 - V0.project(z)
        T1 = V1 - V1.project(z)
        
        cross = T0.cross(T1)        
        sign = 1
        if cross.dot(z) < 0:
            sign = -1
        
        rot = T0.rotation_difference(T1)  
        ang = rot.angle
        curl = curl + ang*sign
        lerps[n] = V0.lerp(V1,.5)
        
    clockwise = 1

    if curl < 0:
        clockwise = -1
    
    if debug:
        print(curl)
        print('you can double check the curl/CCW by examining first 10 vertex indices')
        print(verts_in_order[0:10])
        
    for n in range(0,l-2):
   
        index = verts_in_order[n+1]
        v = me.vertices[index]
        
        V = lerps[n]
        trans = z.cross(V)*clockwise
        trans.normalize()
        delta = scale_vec_mult(trans, iscl)
        delta *= res       
        v.co += delta       
    if debug:
        print("moved %d verts in %f seconds" %(l-2,time.time()-start))
    '''
    ob = bpy.context.object
    me = ob.data
    mx = ob.matrix_world
    axis = Vector((0,0,1))
    edges = [e for e in me.edges if e.select]
    res = 0.5
    
    utils.extrude_edges_in(me, edges, mx, axis, res):
    '''

def offset_bmesh_edge_loop(bme, bmedges, axis, res, debug = False):

    '''
    takes a CLOSED LOOP of bmesh edges and moves them in
    eg..take a  loop and turn it into a railroad track
    
    needs an axis to move perpendicular too...typically 3d view direction
    args:
        bme - Blender BMesh Data
        bmedges - indices of edges that form a closed loop
        axis - the local axis which to extrude perpendicular to type Vector...probably the insertion axis
        res - distance step for each extrusion...world size
    '''
    if debug:
        start = time.time() #monitor performance
    
    z = axis
    bme.edges.ensure_lookup_table()
    bme.verts.ensure_lookup_table()
    loops = edge_loops_from_bmedges(bme, bmedges)
    verts_in_order = loops[0]
       
    verts_in_order.append(verts_in_order[1]) #the first (n=0) element of the list already repeated, adding the 2nd to the end as well.
    l = len(verts_in_order)    
    verts_alone = verts_in_order[0:l-2]
    
    
    lerps = [Vector((0,0,0))]*(l-2)
    vcoords = [bme.verts[index].co for index in verts_in_order]
    curl = 0
    
    for n in range(0,l-2):

        #Vec representation of the two edges
        V0 = (vcoords[n+1] - vcoords[n])
        V1 = (vcoords[n+2] - vcoords[n+1])
        
        ##XY projection
        T0 = V0 - V0.project(z)
        T1 = V1 - V1.project(z)
        
        cross = T0.cross(T1)        
        sign = 1
        if cross.dot(z) < 0:
            sign = -1
        
        rot = T0.rotation_difference(T1)  
        ang = rot.angle
        curl = curl + ang*sign
        lerps[n] = V0.lerp(V1,.5)
        
    clockwise = 1

    if curl < 0:
        clockwise = -1
    
    if debug:
        print(curl)
        print('you can double check the curl/CCW by examining first 10 vertex indices')
        print(verts_in_order[0:10])
        
    for n in range(0,l-2):
   
        index = verts_in_order[n+1]
        v = bme.verts[index]
        
        V = lerps[n]
        trans = z.cross(V)*clockwise
        trans.normalize()
        #delta = scale_vec_mult(trans, iscl)
        #delta *= res 
        delta = res * trans      
        v.co += delta       
    if debug:
        print("moved %d verts in %f seconds" %(l-2,time.time()-start))
    '''
    ob = bpy.context.object
    me = ob.data
    mx = ob.matrix_world
    axis = Vector((0,0,1))
    edges = [e for e in me.edges if e.select]
    res = 0.5
    
    utils.extrude_edges_in(me, edges, mx, axis, res):
    '''        

def material_management(context, odc_items, force = False, debug = False):
    '''
    goes through all the items in project
    checks them for a material slot
    if none, adds the apporpriate material fom the material library, linking if necesary
    It will not change an existing material slot in case the user wants to modify colors unless force = True
    '''
    material_dictionary = {"prep_model":"prep",
                    "opposing":"opposing",
                    "bubble":"opposing",
                    "restoration":"restoration",
                    "contour":"restoration",
                    "coping":"restoration",
                    "acoping":"restoration",
                    "intaglio":"connector",
                    "outer":"aligner",
                    "inner":"collision",
                    "tissue":"tissue",
                    "splint":"splint",
                    "model":"prep",
                    "master":"master"}
    if debug:
        starttime = time.time()
    
    if context.user_preferences.filepaths.use_relative_paths:
        print('user settings -> file -> uncheck Relative Paths')
        return
    
    settings = get_settings()
    fname = settings.mat_lib
    if not os.path.isfile(fname):
        print(fname)
        print('cant find material dictionary, please see user preferences')
        return
                       
    #here comes the worst if, then, for if, loops logic statement EVER
    #this iterates through each tooth, implant etc
    for item in odc_items:  
        keys = item.keys()  #this will give the property names..eg, "prep_model" or "contour" or "inside"
        if debug > 1:
            print(keys)
        if keys:  #make sure we have started working on the tooth.
            values = item.values()
            if debug > 1:
                print(values)
            for n in range(0,len(keys)):
                if keys[n] in material_dictionary.keys() and keys[n] != "":  #make sure we have mapped this property to a material.
                    if debug > 1:
                        print(values[n])
                        
                    ob = bpy.data.objects.get(item.get(keys[n]))
                    if ob and not len(ob.material_slots):
                        if not bpy.data.materials.get(material_dictionary[keys[n]]):
                            mat_from_lib(settings.mat_lib, material_dictionary[keys[n]])
                        context.scene.objects.active = ob
                        was_hidden = ob.hide
                        if was_hidden:
                            ob.hide = False
                        bpy.ops.object.material_slot_add()
                        ob.material_slots[0].material = bpy.data.materials[material_dictionary[keys[n]]]
                        if was_hidden:
                            ob.hide = True
                        
    if debug:
        print("managed materials in %f" % (time.time()-starttime))
    return

def scene_verification(scene, debug = False):
    if debug:
        start = time.time()
    #remember the props we dont watnt to test
    exclusion_props = ['','name','log','in_bridge','rest_type','teeth','implants','connectors',"tooth_string","implant_string"]
    #splint_props = ['']
    #bridge_props_exclude=['']
    
    teeth = scene.odc_teeth
    imps = scene.odc_implants
    bridges = scene.odc_bridges
    splints = scene.odc_splints
    
    for collect in [teeth, imps, bridges,splints]:
        if len(collect):
            for item in collect:
                keys = item.keys()
                if debug > 2:
                    print(keys)
                if keys:
                    values = item.values()
                    if debug > 2:
                        print(values)
                    for n in range(0,len(keys)):
                        if keys[n] not in exclusion_props and values[n] not in bpy.data.objects:
                            if debug:
                                print('cant find %s = %s in blender data, removing prop' % (keys[n], values[n]))
                            setattr(item, keys[n], '')
                
    if debug:
        print("verified scene in %f seconds" % (start-time.time()))
    
    return
    
def layer_management(odc_items, debug = False):
    '''
    odc_items = Collection of type ToothRestoration...eg context.scene.odc_teeth or one ToothRestoration
    puts items in different layers to help with organization
    
    There are 20 layers in a scene
    Implant layers will mirror crown/bridge layers +10
    0. Everything
    1. preps, restorations
    11. implants, abutments
    2. Insertion Axes
    12. Abutment Axes
    3.Master Model + Opposing
    13. Teeth + Bone + etc
    4. Margins, Bubble, Pmargin, intaglio
    14. Occlusal Plane, Stent Outline
    5. Bridge, 
    15. Bars, 
    16. Solid restoration
    
    
    Garbage Collection
    9. Most C&B things...prep, mesial, distals, final restorations
    19. Most Implant things...imaplnt,all the hardware, etc.
    10: Guide, Stent, OccGuards,Custon Tray, DentureBase
    '''
    #Check for a master model
    sce = bpy.context.scene
    if sce.odc_props.master in bpy.data.objects:
        ob = bpy.data.objects[sce.odc_props.master]
        ob.layers[0] = True
        ob.layers[3] = True
        
    if sce.odc_props.opposing in bpy.data.objects:
        ob = bpy.data.objects[sce.odc_props.opposing]
        ob.layers[0] = True
        ob.layers[3] = True
        
    if sce.odc_props.bone in bpy.data.objects:
        ob = bpy.data.objects[sce.odc_props.bone]
        ob.layers[0] = True
        ob.layers[13] = True 
        
    if debug:
        starttime = time.time()
    layer_dictionary = {"axis":[0,2],
                         "mesial":[0,9],
                         "distal":[0,9],
                         "prep_model":[0,1,9],
                         "margin":[0,4],
                         "pmargin":[0,4],
                         "bubble":[0,4],
                         "restoration":[0,1,9],
                         "contour":[0,1],
                         "coping":[0,1],
                         "acoping":[0,1],
                         "intaglio":[0,4],
                         "implant":[0,11,19],
                         "outer":[0,19],
                         "sleeve":[0,19],
                         "drill":[0,19],
                         "inner":[0,9],
                         "cutout":[0,9],
                         "bone":[0,13],
                         "abut_axis":[0,12],
                         "tissue":[0,11,19],
                         "splint":[0,10],
                         "plane":[0,14],
                         "cut":[0,14],
                         "refractory":[0,14],
                         "bridge":[0,5],
                         "solid":[0,16]}
                         
    #here comes the worst if, then, for if, loops logic statement EVER
    for item in odc_items:
        keys = item.keys()
        print(keys)
        if keys:
            values = item.values()
            print(values)
            for n in range(0,len(keys)):
                if keys[n] in layer_dictionary.keys():
                    print(values[n])
                    ob = bpy.data.objects.get(item.get(keys[n]))
                    if ob:
                        odc_layers = layer_dictionary[keys[n]]
                        for i, L in enumerate(ob.layers):
                            if i in odc_layers:
                                ob.layers[i] = True
                            else:
                                ob.layers[i] = False
                    else:
                        print('couldnt find the obejct perhaps scene verify is not working')
    if debug:
        print("managed layers in %f" % (time.time()-starttime))

def transform_management(item,scene,space_data,val="axis"):
    '''
    item: usually class ToothRestortion, Bridge etc
    scene: bpy.data.type.Scene
    val: optional...rarely, val = "abut_axis" or something tricky if there are two orientations pertinent to a single type of restoration
    '''
    current_transform = space_data.transform_orientation
    #This can only be used within an operator in the 3d view
    #unless we want to override conetxt to pass to the operator in next line
    bpy.ops.transform.create_orientation(name = "ODC Transform",overwrite=True)
    trans = scene.orientations["ODC Transform"]
    ob = bpy.data.objects[item.get(val)]
    mx = ob.matrix_world.to_3x3()
    trans.matrix = mx
    
    return current_transform
            
def extrude_edges_out_view(me, edges, mx, res, debug = False):
    '''
    convenience wrapper of extrude_edges_in which grabs
    the currrent view orientation.
    args:
        me - Blender Mesh Data
        edges - edges (not indices of edges) that form a loop
        mx  - world matrix
        res - distance step for each extrusion
    '''
    
    space = bpy.context.space_data
    region = space.region_3d        
    vrot = region.view_rotation
    align = vrot.inverted()   
    z = vrot * Vector((0,0,1))
    
    extrude_edges_in(me, edges, mx, z, -1*res, debug)
   
def fill_bmesh_loop_scale(bme, bmedges, res, debug = False):
    '''
    fills a hole by recursively extruding, scaling toward median
    point, and then collapsing small edges.
    
    Will result in triangles and quads.  Not good for complex or concave
    holes.
    
    args:
        bme - BMesh
        bmedges - indices of edges which constitute the loop
        res - appprox size of step (optional)
    
    return:
        filled_verts - list of BMVerts
    '''
    if debug:
        start = time.time()
    
    
    def get_com_bmverts(lverts):
        COM = Vector((0,0,0))
        for v in lverts:
            COM += v.co
        COM *= 1/n_verts
        return COM
    
    def avg_radii(lverts, COM):
        Rs = [(v.co - COM).length for v in lverts]
        R_mean = sum(Rs)/len(Rs)
        return Rs, R_mean
    
    def relax_bmverts(lverts, factor = .2):
        deltas = {}
        
        for v in lverts:
            eds = [ed for ed in v.link_edges if not ed.is_manifold]
            if not len(eds): continue
            #longest edge
            ed_max = max(eds, key=lambda ed: ed.calc_length())
            
            total_len = sum([ed.calc_length() for ed in eds])
            mean_len = total_len/len(eds)
            correction = total_len - mean_len
            
            vec = (ed_max.other_vert(v).co - v.co).normalized()
            deltas[v] = factor * correction * vec
            
        for v in deltas.keys():
            v.co += deltas[v]
    
    prev_loop = [bme.edges[i] for i in bmedges]      
    orig_edges = set(bme.edges)
    orig_vs = set(bme.verts)
    
    print('There are %i original verts' % len(bme.verts))
    
    vert_inds = edge_loops_from_bmedges(bme, bmedges)[0]
    vert_inds.pop() #closed loop
    real_vs = [bme.verts[i] for i in vert_inds]
    n_verts = len(vert_inds)
    
    #choose smallest edge as the step resolution    
    if not res:
        res = min(prev_loop, key=lambda ed: ed.calc_length())
            
    COM = get_com_bmverts(real_vs)
    Rs, Rmean = avg_radii(real_vs, COM)
    step = math.ceil(Rmean/res)
    print('the step is %i ' % step)
    scl = 1
    
    filled_verts = set()
    finished = False
    for i in range(1,step):  #step
        
        if len(prev_loop) == 2:
            finished = True
            print('len prev loop == 2 which is quite strange')
            bme.verts.ensure_lookup_table()
            bme.edges.ensure_lookup_table()
            bme.faces.ensure_lookup_table()
            
            #TODO, report some errors
            break
        
        if len(prev_loop) < 5:
            vert_inds = edge_loops_from_bmedges(bme, [ed.index for ed in prev_loop])[0]
            vs = [bme.verts[i] for i in vert_inds[:-1]]
            bme.faces.new(tuple(vs))
            print('new face < 5 verts') 
            
            bme.verts.ensure_lookup_table()
            bme.edges.ensure_lookup_table()
            bme.faces.ensure_lookup_table()
        
            finished = True
            
        scl = (1 - 1/step*i)/scl
        print('the scl is %f' % scl)
        
        ret = bmesh.ops.extrude_edge_only(bme, edges = prev_loop)
        geom_extrude = ret['geom']
        prev_loop = [ele for ele in geom_extrude if isinstance(ele, bmesh.types.BMEdge)]
        verts_extrude = [ele for ele in geom_extrude if isinstance(ele, bmesh.types.BMVert)]
        
        #COM = get_com_bmverts(verts_extrude)
        Rs, Rmean = avg_radii(verts_extrude, COM)
        
        
        for i,v in enumerate(verts_extrude):
            
            vec = COM - v.co
            vec.normalize()
            factor = Rs[i]/Rmean
            v.co += factor * res * vec  #move the vert closer to the center of mass
            
            
        relax_bmverts(verts_extrude, factor = .2)
        
        print('there are %i eds in the loop before doubles' % len(prev_loop))
        bmesh.ops.remove_doubles(bme, verts = verts_extrude, dist = .5*res)    
    
        prev_loop = [ed for ed in bme.edges if not ed.is_manifold and ed not in orig_edges]
        
        if len(prev_loop) == 0 and len(verts_extrude) != 0:
            print('this is the scenario where last remove doubles meses something up')
            for v in bme.verts:
                if (v not in orig_vs) and (v not in filled_verts):
                    print('found the lone vert')
                    filled_verts.add(v)
        vs = set()
        for ed in prev_loop:
            vs.update([ed.verts[0], ed.verts[1]]) 
        filled_verts |= vs
        
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()

    if not finished:
        vert_inds = edge_loops_from_bmedges(bme, [ed.index for ed in prev_loop])
        
        if len(vert_inds) == 0:
            print('zero vert_inds, merged into one?')
            fv_inds = list(filled_verts)    
            return fv_inds
        
        vs = [bme.verts[i] for i in vert_inds[0][:-1]]
        f = bme.faces.new(tuple(vs))      
        
        if len(vs) > 4:
            bmesh.ops.triangulate(bme, faces = [f])
        
    
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()
        
    if debug:
        print("filled loop of %d verts in %f seconds" %(n_verts, start - time.time()))
    
    fv_inds = list(filled_verts)
    print('%i verts were filled in to clsoe hole' % len(fv_inds))    
    return fv_inds

def fill_loop_scale(ob, edges, res, debug = False):
    '''
    args:
        ob - Blender Object (must be mesh)
        edges - edges which constitute the loop (not indices of edges)
        mx  - world matrix
        res - appprox size of step (optional)
    
    '''
    if debug:
        start = time.time()
        
    if not ob:
        ob = bpy.context.object  #weird, why did I do this?
    
    me = ob.data
    mx = ob.matrix_world
        
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    
    ob.hide = False
    ob.select = True
    bpy.context.scene.objects.active = ob
    
    
    verts = edge_loops_from_edges(me,edges)
    verts = verts[0]
    verts.pop()
    n_verts = len(verts)
    
    n=len(ob.vertex_groups)
    bpy.ops.object.vertex_group_add()
    bpy.context.object.vertex_groups[n].name='filled_hole'
    
    
    n=len(ob.vertex_groups)
    bpy.context.tool_settings.vertex_group_weight = 1
    bpy.ops.object.vertex_group_add()
    bpy.context.object.vertex_groups[n].name='original_verts'
    
    
    #notice now that ob.vertex_groups[n-1] is original_verts
    #and ob.vertex_groups[n-2] = filled_hole
    
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.object.vertex_group_assign()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for v in verts:
        me.vertices[v].select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    #### Now we are ready to actually do something  ###
    
    #find COM of selected verts
    COM = get_com(me,verts,mx)
    if debug:
        print('global COM is %s' % str(COM))
    
    #calc the average "radius" of the loop
    
    R=0
    L = len(verts)
    for v in verts:
        r = mx * me.vertices[v].co - COM     
        R = R + r.length

    R = R/L
    if debug:
        print('the average radius is %f' % R)
        
    
    if not res:
        lengths=[]
        vert_loop = verts[:]
        vert_loop.append(verts[0])
        
        l = len(vert_loop)
        for i in range(0,l-1):
            a = vert_loop[i]
            b = vert_loop[i+1]
            v0=mx * me.vertices[a].co
            v1=mx * me.vertices[b].co
            V=v1-v0
          
            lengths.append(V.length)
    
        res=min(lengths)
        if debug:
            print('taking min edge length as res: %f' % res)
            

    step = math.ceil(R/res)
    print(step)
    
    bpy.ops.object.vertex_group_set_active(group = 'filled_hole')
    scl = 1

    for i in range(1,step):
    
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
    
        me = ob.data
        sverts=len([v for v in me.vertices if v.select])
    
        if sverts > 4:
            if debug:
                print('extruding again at iteration %d' % i)
            bpy.ops.mesh.extrude_edges_move()
            bpy.ops.object.vertex_group_assign()
            scl = (1 - 1/step*i)/scl
   
    
            bpy.ops.transform.resize(value = (scl, scl, scl))    
            bpy.ops.mesh.remove_doubles(threshold=.85*res)    
            bpy.ops.mesh.looptools_relax(input='selected', interpolation='cubic', iterations='3', regular=True)
        
        
        if sverts < 3:
            if debug:
                print('break at <3')
            break
                
        if (sverts <= 4 and sverts > 2) or i == step -1:
            if debug:
                print('break at 3 and fill remainder')
            bpy.ops.mesh.fill()
            bpy.ops.mesh.vertices_smooth(repeat =3)
            bpy.ops.object.vertex_group_assign()
            break
        
    bpy.ops.object.vertex_group_select()
    bpy.ops.object.vertex_group_set_active(group = 'original_verts')
    bpy.ops.object.vertex_group_remove_from()
        
    if debug:
        print("filled loop of %d verts in %f seconds" %(n_verts, start - time.time()))
        
            
def align_to_view(context, obj):
    '''
    aligns an objects z axis with the 3d view
    by rotating the object
    '''
    
    space = bpy.context.space_data
    region = space.region_3d        
    vrot = region.view_rotation
    
    if obj.rotation_mode != 'QUATERNION':
        obj.rotation_mode = 'QUATERNION'
 
    obj.rotation_quaternion = vrot
    
    
#Data Linkig from External Library
#Adapted form  Mackracke's Material Library   
def obj_from_lib(libpath, name, link = False, rel = False):
    '''
    links or appends an object from another blend file by object name
    obpath = libpath + '\\Object\\'
    bpy.ops.wm.link_append(directory = obpath, filename = name, link = True, relative_path = True )
    '''
    with bpy.data.libraries.load(libpath, link, rel) as (data_from, data_to):
        ind = data_from.objects.index(name)
        data_to.objects = [data_from.objects[ind]]
        
        #if len(data_to.objects[0].children):
            #print('found a child')
    for ob in data_to.objects:
        #attributes = dir(ob)
        #print(attributes)
        if hasattr(ob, 'children'):
            if len(getattr(ob, 'children')):
                print(ob.children)
            else:
               print('has no children')
        else:
            print('has no children')
           
    if link:
        print(name + " linked.")
    else:
        print(name + " appended.")
          
def obj_list_from_lib(libpath, include = None, exclude = None, debug = False):
    '''
    get's a list of object names from a lend file
    for later use with obj_from_lib
    
    args:
        libpath: filepath of library to investigate (string)
        include:  object name must include this string  eg '.'
        exclude: filter character to exclude based on object name  eg '_'
        debug: Bool or Int  controls how much is printed to console
    '''
    obj_list = []
    
    with bpy.data.libraries.load(libpath) as (data_from, data_to):
        #remember that data_From.objects is actually a list of stirngs
        #of the object names not the actual object data.
        for obj in data_from.objects:
            if not exclude and not include:
                obj_list.append(obj)
            
            elif exclude and not include:
                if exclude not in obj:
                    obj_list.append(obj)
                    
            elif include and not exclude:
                if include in obj:
                    obj_list.append(obj)
                    
            elif exclude and include:
                if exclude not in obj and include in obj: 
                    obj_list.append(obj)
            
            
            if debug > 2:
                print(obj)

    if debug:
        print(obj_list)
    return obj_list

def mat_list_from_lib(libpath):
    mat_list = []
    with bpy.data.libraries.load(libpath) as (data_from, data_to):
        for mat in data_from.materials:
            mat_list.append(mat)

    return list
    
def mat_from_lib(libpath, name, link = False, rel = False):    
    with bpy.data.libraries.load(libpath, link, rel) as (data_from, data_to):
        data_to.materials = [name]
        if link:
            print(name + " linked.")
        else:
            print(name + " appended.")


def max_alt(verts):
    '''
    args:
    verts - list of vectors in order
    return:
    the index of the vertex with the highest altitude
    the magnitude of the altitude
    the vector representing the max alt point and the line
    '''
    
    pt1 = verts[0]
    pt2 = verts[-1]
    n_verts = len(verts)
    
    alts = [0]*n_verts
    
    for i in range(1,n_verts-1):
        alts[i] = altitude(pt1, pt2,verts[i])
        
    max_alt = max(alts)
    max_indx = alts.index(max_alt)
    
    alt_vect = altitude_vector(pt1, pt2, verts[max_indx])
    return (max_alt, alt_vect, max_indx)
    
    
def simplypoly(splineVerts, order): #options
    # main vars
    newVerts = [] # list of vertindices to keep
    points = splineVerts # list of 3dVectors
    pointCurva = [] # table with curvatures
    curvatures = [] # averaged curvatures per vert
    for p in points:
        pointCurva.append([])
    #order = 5 # order of sliding beziercurves
    #k_thresh = options[2] # curvature threshold
    #dis_error = options[6] # additional distance error

    # get curvatures per vert
    for i, point in enumerate(points[:-(order-1)]):
        BVerts = points[i:i+order]
        for b, BVert in enumerate(BVerts[1:-1]):
            deriv1 = getDerivative(BVerts, 1/(order-1), order-1)
            deriv2 = getDerivative(BVerts, 1/(order-1), order-2)
            curva = getCurvature(deriv1, deriv2)
            pointCurva[i+b+1].append(curva)

    # average the curvatures
    for i in range(len(points)):
        avgCurva = sum(pointCurva[i]) / (order-1)
        curvatures.append(avgCurva)

    max_curv = max(curvatures)
    # get distancevalues per vert - same as Ramer-Douglas-Peucker
    # but for every vert
    '''
    distances = [0.0] #first vert is always kept
    for i, point in enumerate(points[1:-1]):
        dist = altitude(points[i], points[i+2], points[i+1])
        distances.append(dist)
    distances.append(0.0) # last vert is always kept
    '''
    
    '''
    # generate list of vertindices to keep
    # tested against averaged curvatures and distances of neighbour verts
    newVerts.append(0) # first vert is always kept
    for i, curv in enumerate(curvatures):
        if (curv >= k_thresh*0.01
        or distances[i] >= dis_error*0.1):
            newVerts.append(i)
    newVerts.append(len(curvatures)-1) # last vert is always kept
    '''
    
    return curvatures #max_curv #newVerts
#########################################
#### Ramer-Douglas-Peucker algorithm ####
#########################################
# get altitude of vert
def altitude(point1, point2, pointn):
    edge1 = point2 - point1
    edge2 = pointn - point1
    if edge2.length == 0:
        altitude = 0
        return altitude
    if edge1.length == 0:
        altitude = edge2.length
        return altitude
    alpha = edge1.angle(edge2)
    altitude = math.sin(alpha) * edge2.length
    
    return altitude

def altitude_vector(point1, point2, pointn):
    pt_on_line = intersect_point_line(pointn, point1, point2)[0]
    alt_vect = pt_on_line - pointn
    
    return alt_vect
    
def vert_group_inds_get(context, ob, vgroup, debug = False):
    '''
    args:
      ob - Blender Mesh Object
      vgroup - String representing vertex group name
    return:
      inds - a List of Integers representing the list of indices in the group
      
    notes, this will select and unhide the object, as well as deselect everything else
    if you need it to not distrupt your scene, use scene preservation and reconstruct
    '''
    if debug:
        start = time.time()
         
    if context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True
    ob.hide = False
    context.scene.objects.active = ob
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.vertex_group_set_active(group=vgroup)
    bpy.ops.object.vertex_group_select()
    bpy.ops.object.mode_set(mode='OBJECT')
    inds = [v.index for v in ob.data.vertices if v.select]
    
    if debug:
        print('got vgroup indices in %f seconds' % time.time() - start)
    return inds

    #do the scene reconstruc thing
# iterate through verts
def iterate(points, newVerts, error):
    '''
    args:
    points - list of vectors in order representing locations on a curve
    newVerts - list of indices? (mapping to arg: points) of aready identified "new" verts
    error - distance obove/below chord which makes vert considered a feature
    
    return:
    new -  list of vertex indicies (mappint to arg points) representing identified feature points
    or
    false - no new feature points identified...algorithm is finished.
    '''
    new = []
    for newIndex in range(len(newVerts)-1):
        bigVert = 0
        alti_store = 0
        for i, point in enumerate(points[newVerts[newIndex]+1:newVerts[newIndex+1]]):
            alti = altitude(points[newVerts[newIndex]], points[newVerts[newIndex+1]], point)
            if alti > alti_store:
                alti_store = alti
                if alti_store >= error:
                    bigVert = i+1+newVerts[newIndex]
        if bigVert:
            new.append(bigVert)
    if new == []:
        return False
    return new

#### get SplineVertIndices to keep
def simplify_RDP(splineVerts, error):
    '''
    Reduces a curve or polyline based on altitude changes globally and w.r.t. neighbors
    args:
    splineVerts - list of vectors representing locations along the spline/line path
    error - altitude above global/neighbors which allows point to be considered a feature
    return:
    newVerts - a list of indicies of the simplified representation of the curve (in order, mapping to arg-splineVerts)
    '''

    # set first and last vert
    newVerts = [0, len(splineVerts)-1]

    # iterate through the points
    new = 1
    while new != False:
        new = iterate(splineVerts, newVerts, error)
        if new:
            newVerts += new
            newVerts.sort()
    return newVerts


# get binomial coefficient
def binom(n, m):
    b = [0] * (n+1)
    b[0] = 1
    for i in range(1, n+1):
        b[i] = 1
        j = i-1
        while j > 0:
            b[j] += b[j-1]
            j-= 1
    return b[m]

# get nth derivative of order(len(verts)) bezier curve
def getDerivative(verts, t, nth):
    order = len(verts) - 1 - nth
    QVerts = []

    if nth:
        for i in range(nth):
            if QVerts:
                verts = QVerts
            derivVerts = []
            for i in range(len(verts)-1):
                derivVerts.append(verts[i+1] - verts[i])
            QVerts = derivVerts
    else:
        QVerts = verts

    if len(verts[0]) == 3:
        point = Vector((0, 0, 0))
    if len(verts[0]) == 2:
        point = Vector((0, 0))

    for i, vert in enumerate(QVerts):
        point += binom(order, i) * math.pow(t, i) * math.pow(1-t, order-i) * vert
    deriv = point

    return deriv

# get curvature from first, second derivative
def getCurvature(deriv1, deriv2):
    if deriv1.length == 0: # in case of points in straight line
        curvature = 0
        return curvature
    curvature = (deriv1.cross(deriv2)).length / math.pow(deriv1.length, 3)
    return curvature


#TODO:, this may go in margin methods....TBA
def tracer_mesh_add(rad, loc, spokes, res, target):
    '''
    args
    radius: radius of circle
    location
    spokes: number of spokes (resolution)
    res: distance between points
    target:  object
    '''
    
    current_obs = list(bpy.data.objects)
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.ops.object.add(type='MESH', location = loc)
    #bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.primitive_circle_add(vertices = spokes*2, radius = rad, fill_type = "TRIFAN")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.mesh.delete(type="EDGE_FACE")
    bpy.ops.mesh.select_all(action="SELECT")
    
    n_subs = math.ceil(math.log(rad/res)/math.log(2))
    for i in range(n_subs):
        bpy.ops.mesh.subdivide(number_cuts = 1)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    
    for obj in bpy.data.objects:
        if obj not in current_obs:
            Tracer = obj
            
    Tracer.rotation_mode = "QUATERNION"
        
    bpy.ops.object.modifier_add(type="SHRINKWRAP")
    mod = Tracer.modifiers["Shrinkwrap"]
    mod.wrap_method = 'NEAREST_SURFACEPOINT'
    mod.use_project_x = False
    mod.use_project_y = False
    mod.use_project_z = True
    mod.target = target
    
    return Tracer
    
    
def rot_between_vecs(v1,v2):
    '''
    args:
    v1 - Vector
    v2 - Vector
    
    returns the quaternion representing rotation between v1 to v2
    
    notes: doesn't test for parallel vecs
    '''
    v1.normalize()
    v2.normalize()
    angle = v1.angle(v2)
    axis = v1.cross(v2)
    axis.normalize()
    sin = math.sin(angle/2)
    cos = math.cos(angle/2)
    
    quat = Quaternion((cos, sin*axis[0], sin*axis[1], sin*axis[2]))
    
    return quat

        
# calculate a best-fit plane to the given vertices
#modified from looptoos script
def calculate_plane(locs, itermax = 500, debug = False):
    '''
    args: 
    vertex_locs - a list of type Vector
    return:
    normal of best fit plane
    '''
    if debug:
        start = time.time()
        n_verts = len(locs)
    
    # calculating the center of masss
    com = Vector()
    for loc in locs:
        com += loc
    com /= len(locs)
    x, y, z = com
    
    # creating the covariance matrix
    mat = Matrix(((0.0, 0.0, 0.0),
                  (0.0, 0.0, 0.0),
                  (0.0, 0.0, 0.0),
                   ))
    for loc in locs:
        mat[0][0] += (loc[0]-x)**2
        mat[1][0] += (loc[0]-x)*(loc[1]-y)
        mat[2][0] += (loc[0]-x)*(loc[2]-z)
        mat[0][1] += (loc[1]-y)*(loc[0]-x)
        mat[1][1] += (loc[1]-y)**2
        mat[2][1] += (loc[1]-y)*(loc[2]-z)
        mat[0][2] += (loc[2]-z)*(loc[0]-x)
        mat[1][2] += (loc[2]-z)*(loc[1]-y)
        mat[2][2] += (loc[2]-z)**2
    
    # calculating the normal to the plane
    normal = False
    try:
        mat.invert()
    except:
        if sum(mat[0]) == 0.0:
            normal = Vector((1.0, 0.0, 0.0))
        elif sum(mat[1]) == 0.0:
            normal = Vector((0.0, 1.0, 0.0))
        elif sum(mat[2]) == 0.0:
            normal = Vector((0.0, 0.0, 1.0))
    if not normal:
        # warning! this is different from .normalize()
        iters = 0
        vec = Vector((1.0, 1.0, 1.0))
        vec2 = (mat * vec)/(mat * vec).length
        while vec != vec2 and iters < itermax:
            iters+=1
            vec = vec2
            vec2 = mat * vec
            if vec2.length != 0:
                vec2 /= vec2.length
        if vec2.length == 0:
            vec2 = Vector((1.0, 1.0, 1.0))
        normal = vec2


    if debug:
        if iters == itermax:
            print("looks like we maxed out our iterations")
        print("found plane normal for %d verts in %f seconds" % (n_verts, time.time() - start))
    
    return normal       

def  tracer_settle(tracer, settling_treshold = .1, epsilon = .2, max_settles=10, debug = False, guess_on_flat = True):
    '''
    trace is a blender mesh object, generated by generate_trace, shrinkwrapped to another objcect
    settling_threshold: if distance moved on a settling iteration is < settling_threshold we are considered finished
    '''
    if debug:
        start = time.time()
        print('_______Start______')
        
    #code for autocomplete, comment before compile/save
    #tracer = bpy.types.Object
    
    #figure out where we are
    previous_location = tracer.location.copy()
    
    #get the modifier_applied mesh (notice this does NOT apply loc/rot/scale
    #I typically use me short for mesh...not for me like self.
    #we will have to do this on every settle to update modifier changes
    me = tracer.to_mesh(bpy.context.scene,True,'PREVIEW')
    
    #this we will do once, since shrinkwrap  wont change vertex locations
    #tracer is shaped like a starfish or wheel spokes
    spokes = edge_loops_from_edges(me,me.edges)
    n_spokes = len(spokes)
    
    tips = [0]*n_spokes*2
    for i in range(0,n_spokes):
        tips[2*i] = spokes[i][0]
        tips[2*i+1] = spokes[i][-1]
        
    if debug:
        print("there are %d spokes" % n_spokes)
        print("there are %d verts per spoke" % len(spokes[0]))
    
    
    
    best_features = [0]*n_spokes  #quantitative assemsment of features, indexed by spoke #
    best_feature_mesh_vertex_inds = [0]*n_spokes #indexed by spoke # mapped to the vertex index in the tracer
    
    
    
    n_settles = 0
    
    while n_settles < max_settles:
        
        #find the deepest crevice point
        for j, loop in enumerate(spokes):
            
            #get a list of vectors for the spoke
            #note the transform to worl coords....ob.to_mesh() gives deformed mesh 
            #in local coord.  I'm to chicken to do the calc in local and then
            #back it out later :-/
            vecs = [tracer.matrix_world * me.vertices[i].co for i in loop]
            
            #pass those vectors to the RDP algorigth
            simplified_points_inds = simplify_RDP(vecs, epsilon)
            if debug:
                print("simplified points for stroke %d" % j)
                print(simplified_points_inds)
            
            #count the number of feature points:
            n_features = len(simplified_points_inds)
            
            #one chance to improve the outcome..this could be more dynamic later.
            #if too few features (smooth on this distance scale), shrink epsilon by 10%
            #if too many features (noisy on this distance scale), grow epsilon by 10%
            if n_features < 3:
                simplified_points_inds = simplify_RDP(vecs, .9 * epsilon)
                n_features = len(simplified_points_inds)
            elif n_features > 5:
                simplified_points_inds = simplify_RDP(vecs, 1.1 * epsilon)
                n_features = len(simplified_points_inds)
            
            if n_features < 3:
                best_features[j] = 0
                best_feature_mesh_vertex_inds[j] = loop[simplified_points_inds[0]]  #just pick one index...the  line is flat as far as we are concerned anyway.
                if debug:
                    print("found a flat feature after epsilon correction at spoke %d" % j)
            else:    
                #simplified_pooints_inds are in order
                print('there are %d features at spoke %f' % (n_features,j))
                qualities = [0]*(n_features-2)
                for i in range(1,n_features-1):
                    point1 = vecs[simplified_points_inds[i-1]] #previos neighbor
                    point2 = vecs[simplified_points_inds[i+1]] #other neightbor
                    pointn = vecs[simplified_points_inds[i]]   #feature point
                    
                    depth = altitude_vector(point1, point2, pointn) #depth between features
                    
                    #we will asses depth as it's parallelness (word?) to the local normal
                    #which is stored in our tracer world z direction.
                    qualities[i-1] = depth.dot(tracer.rotation_quaternion * Vector((0,0,1)))
                
                #save the best feature from this spoe
                best_features[j] = max(qualities)
                
                #map it's index in the qualities list (which is 2 shorter than features on each end
                best_index = qualities.index(best_features[j])
                best_feature_mesh_vertex_inds[j] = loop[simplified_points_inds[best_index+1]]  #the plus one is for the endpoint
        
        greatest_feature = max(best_features)
        best_candidate_index = None       
        if greatest_feature <= 0:
            if min(best_features) == 0:
                print("problem...surface is flat wrt +/- %10 of epsilon")
                if guess_on_flat:
                    best_candidate_index = tips[math.floor(random.random() * 2 *n_spokes)]
            else:
                print("surface curvature is opposite in all direction..stopping in failure")
                return 0
        
        else:
            #map the greatest feature wrt to spoke to the index of the spoke
            greatest_feature_index = best_features.index(greatest_feature)
            #get the best vertex index wrt to mesh from the spoke
            best_candidate_index = best_feature_mesh_vertex_inds[greatest_feature_index]
        
        if debug:
            print("best_candidate_index was found to be %d with feature quality %f" % (best_candidate_index, greatest_feature))  
        #move the trace to the best feature identified in world coords
        #we could also grab this directly from the list of vectors supplied originally
        #except that we only held onto one spokes worth of vertex coords at a time per iteration
        new_loc = tracer.matrix_world * me.vertices[best_candidate_index].co.copy()
        
            
        #measure our movement and move tracer
        delta = new_loc - previous_location
        
        if debug:
            print("moving mesh by %f" % delta.length)        
        previous_location = new_loc.copy()
        tracer.location = new_loc
        
        #update mesh after move
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        me = tracer.to_mesh(bpy.context.scene,True,'PREVIEW')
        
        #re_orient it to plane of best fit to spoke ends
        #this is dependent on the spoke ends being  numbered like the were when it was created
        vert_locs = [tracer.matrix_world * me.vertices[tip].co for tip in tips]
        norm = calculate_plane(vert_locs, itermax = 500, debug = False)
        
        #compare plane normal with existing tracer z direction...
        #shouldn't deviate by more than a little.
        flip = norm.dot(tracer.rotation_quaternion * Vector((0,0,1))) < 0
        if flip:
            norm *= -1
            if debug:
                print("flipped best fit plane to keep tracer oriented")
            
            
        #make sure we don't rotate it if the best fit pane is perpendicular to current direction
        #which happens sometimes if the spokes don't overlap the edge of the crease enough (folded starfish)
        do_plane_re_orient = norm.dot(tracer.rotation_quaternion * Vector((0,0,1))) > .4
        
        if not do_plane_re_orient and debug:
            print("didnt reorient tracer because dot priduct was %f" % norm.dot(tracer.rotation_quaternion * Vector((0,0,1))))
        
        if do_plane_re_orient:
            new_quat = rot_between_vecs(Vector((0,0,1)),norm)
            tracer.rotation_quaternion = new_quat
        
        
        if delta.length < settling_treshold:
            #update mesh for next iteration and move the tracer
            tracer.location = new_loc
            me = tracer.to_mesh(bpy.context.scene,True,'PREVIEW')
            if debug:
                print("settled trace in %d iterations with last delta: %f in %f seconds" % (n_settles, delta.length, time.time() - start))
            return me
        
        #update mesh for next iteration
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        me = tracer.to_mesh(bpy.context.scene,True,'RENDER')

        n_settles += 1
        

    if debug:
        print("settled trace in %d iterations with last delta: %f in %f seconds" % (n_settles, delta.length, time.time() - start))
    return me
    
def index_update():
    bpy.ops.ed.undo_push(message = "changed active tooth")

def center_objects(context, obs, set_origins = False, bbox = True):
    sce = context.scene
    if set_origins:
        bpy.ops.object.select_all(action='DESELECT')
        for ob in obs:
            sce.objects.active = ob
            ob.hide = False
            ob.select = True
            bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center = 'BOUNDS')
            ob.select = False
            
    
    #calculate the median point of all the objects
    Med = Vector((0,0,0))
    for ob in obs:
        if bbox:
            Med += get_bbox_center(ob, world=True)
        else:
            Med += ob.location
        
    Med = 1/len(obs)*Med
    
    #this should handle everything well for parenting?
    for ob in obs:
        for i in range(0,3):
            ob.matrix_world[i][3] -= Med[i]   
        
def determine_trace_propogate_direction(tracer, me, bias, epsilon = .2, bias_type = "ENDPOINT", debug = True, guess_on_flat = False):
    
    if bias_type not in ["ENDPOINT","INITIAL_CONDITION"]:
        print("bias type myst be either 'ENDPOINT' or 'INITIAL_CONDITION'")
        return None
    
    spokes = edge_loops_from_edges(me,me.edges)
    n_spokes = len(spokes)
    
    tips = [0]*n_spokes*2
    for i in range(0,n_spokes):
        tips[2*i] = spokes[i][0]
        tips[2*i+1] = spokes[i][-1]
        
    best_features = [0]*n_spokes  #quantitative assemsment of features, indexed by spoke #
    best_feature_mesh_vertex_inds = [0]*n_spokes #indexed by spoke # mapped to the vertex index in the tracer
        
    #find the deepest crevice point
    for j, loop in enumerate(spokes):
        
        #get a list of vectors for the spoke
        #note the transform to worl coords....ob.to_mesh() gives deformed mesh 
        #in local coord.  I'm to chicken to do the calc in local and then
        #back it out later :-/
        vecs = [tracer.matrix_world * me.vertices[i].co for i in loop]
        
        #pass those vectors to the RDP algorigth
        simplified_points_inds = simplify_RDP(vecs, epsilon)
        
        #count the number of feature points:
        n_features = len(simplified_points_inds)
        
        #one chance to improve the outcome..this could be more dynamic later.
        #if too few features (smooth on this distance scale), shrink epsilon by 10%
        #if too many features (noisy on this distance scale), grow epsilon by 10%
        if n_features < 3:
            simplified_points_inds = simplify_RDP(vecs, .9 * epsilon)
            n_features = len(simplified_points_inds)
        elif n_features > 5:
            simplified_points_inds = simplify_RDP(vecs, 1.1 * epsilon)
            n_features = len(simplified_points_inds)
        
        if n_features < 3:
            best_features[j] = 0
            best_feature_mesh_vertex_inds[j] = loop[simplified_points_inds[0]]  #just pick one index...the  line is flat as far as we are concerned anyway.
            if debug:
                print("found a flat feature after epsilon correction at spoke %d" % j)
        else:    
            #simplified_pooints_inds are in order
            qualities = [0]*(n_features-2)
            for i in range(1,n_features-1):
                point1 = vecs[simplified_points_inds[i-1]] #previos neighbor
                point2 = vecs[simplified_points_inds[i+1]] #other neightbor
                pointn = vecs[simplified_points_inds[i]]   #feature point
                
                depth = altitude_vector(point1, point2, pointn) #depth between features
                
                #we will asses depth as it's parallelness (word?) to the local normal
                #which is stored in our tracer world z direction.
                qualities[i-1] = depth.dot(tracer.rotation_quaternion * Vector((0,0,1)))
            
            best_features[j] = max(qualities)**2  #squared to get the magnitude...now we just want flatness
            best_feature_mesh_vertex_inds[j] = loop[simplified_points_inds[qualities.index(max(qualities))+1]] #the plus one is for the endpoint
        
    #find the flattest line
    flattest_feature = min(best_features)
    flattest_spoke_index = best_features.index(flattest_feature)
    
    #if debug:
        #print('flattest feature had quatlity %f with spoke index #d' % (flattest_feature,flattest_spoke_index))
        #print('the tip vertices of the spoke are %d, %d' % (spokes[flattest_spoke_index][0],spokes[flattest_spoke_index][-1]))      
    
    #find direction
    v1 = me.vertices[spokes[flattest_spoke_index][0]].co
    v2 = me.vertices[spokes[flattest_spoke_index][-1]].co
    dir_vec = tracer.matrix_world.to_3x3()*(v2-v1)
    
    #flip it if we need to go the other dir
    if bias_type == "ENDPOINT":
        orig = .5 * (v1 + v2)
        if dir_vec.dot(bias-orig) < 0:
            dir_vec *= -1  
    else:
        if dir_vec.dot(bias) < 0:
            dir_vec *= -1
    dir_vec.normalize()    
    return dir_vec
    
def obj_ray_cast(obj, matrix, ray_origin, ray_target):
    """Wrapper for ray casting that moves the ray into object space"""

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv * ray_origin
    ray_target_obj = matrix_inv * ray_target

    # cast the ray
    if bversion() < '002.077.000':
        hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj)
    else:
        ok, hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj-ray_origin_obj)
        
    if face_index != -1:
        return hit, normal, face_index
    else:
        return None, None, None

def reorient_object(ob, orientation):
    '''
    This function resest's an objects local coordinates to align with whatever orientation is provided
    -Only affects rotation, not scale and 
    args:
    ob - Blender object
    orientation - frame of reference which to align local coordinates with type: mathutils Matrix or Quaternion
    '''
    sce = bpy.context.scene
    #cosntraint?
    
    mx = ob.matrix_world.copy()
    loc = ob.location.copy()
    loc2 = mx.to_translation()
    
    print('are these the same?')
    print(loc)
    print(loc2)
    print('is it because of constraints')
    print(len(ob.constraints))
    
    #should we clear the constraint too?
    
    #clear parent and keep transformation
    if ob.parent:
        Parent = ob.parent
        ob.parent = None
        ob.matrix_world = mx
        reparent = True
    else:
        reparent = False
        
    #make sure we are consistent in our inputs    
    if type(orientation) == Matrix:
        new_mx = orientation.to_3x3()
        
    elif type(orientation) == Quaternion:
        new_mx = orientation.to_matrix()
        #new_mx.resize()
        
    new_imx = new_mx.inverted()
    
    if ob.type == 'MESH':
        print('Meshes supported')
        #apply the objects current rotation
        ob.data.transform(mx.to_3x3().to_4x4())
        ob.data.transform(new_imx.to_4x4())
        ob.matrix_world = new_mx.to_4x4()
        ob.location = loc
        
    else:
        print('non Mesh Object, support not guaranteed')
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:        
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'object':ob,'window': window, 'screen': screen, 'area': area, 'region': region,'scene':sce, 'active_object':ob, 'selected_editable_objects':[ob]}
                            #bpy.ops.screen.screen_full_area(override)# Works!
                            #bpy.ops.screen.back_to_previous(override)# Works!
                            #bpy.ops.view3d.view_orbit(override)# Works!
                            #bpy.ops.view3d.view_pan(override)# Now works!
                            #bpy.ops.view3d.zoom(override, delta=5, mx=0, my=0)# Now works!
                            break
                        
        ob.rotation_mode = 'QUATERNION'
       
        bpy.ops.object.transform_apply(override,rotation = True)
    
        ob.rotation_quaternion = new_imx.to_quaternion()
        sce.update()
        
        bpy.ops.object.transform_apply(override, rotation = True)
        ob.rotation_quaternion = new_mx.to_quaternion()
    
    #ob.matrix_world = Matrix.identity(4)
    #ob.data.update()
    #ob.update_tag()
    #sce.update()

    if reparent:
        ob.update_tag()
        sce.update()
        parent_in_place(ob, Parent)
        
def silouette_brute_force(context, ob, view, world = True, smooth = True, debug = False):
    '''
    args:
      ob - mesh object
      view - Mathutils Vector
      
    return:
       new mesh of type Mesh (not BMesh)
    '''
    if debug:
        start = time.time()
        
    #careful, this can get expensive with multires
    me = ob.to_mesh(context.scene, True, 'RENDER')    
    bme = bmesh.new()
    bme.from_mesh(me)
    bme.normal_update()
    
    #keep track of the world matrix
    mx = ob.matrix_world
    
    if world:
        #meaning the vector is in world coords
        #we need to take it back into local
        i_mx = mx.inverted()
        view = i_mx.to_quaternion() * view
    
    if debug:
        face_time = time.time()
        print("took %f to initialze the bmesh" % (face_time - start))
        
    face_directions = [[0]] * len(bme.faces)
    
    for f in bme.faces:
        if debug > 1:
            print(f.normal)
        
        face_directions[f.index] = f.normal.dot(view)
    
    
    if debug:
        edge_time = time.time()
        print("%f seconds to test the faces" % (edge_time - face_time))
        
        if debug > 2:
            print(face_directions)
            
    delete_edges = []
    keep_verts = set()
    
    for ed in bme.edges:
        if len(ed.link_faces) == 2:
            silhouette = face_directions[ed.link_faces[0].index] * face_directions[ed.link_faces[1].index]
            if silhouette < 0:
                keep_verts.add(ed.verts[0])
                keep_verts.add(ed.verts[1])
            else:
                delete_edges.append(ed)
    if debug > 1:
        print("%i edges to be delted" % len(delete_edges))
        print("%i verts to be deleted" % (len(bme.verts) - len(keep_verts)))
    if debug:
        delete_time = time.time()
        print("%f seconds to test the edges" % (delete_time - edge_time))
        
    delete_verts = set(bme.verts) - keep_verts
    delete_verts = list(delete_verts)
    
    
    #https://svn.blender.org/svnroot/bf-blender/trunk/blender/source/blender/bmesh/intern/bmesh_operator_api.h
    bmesh.ops.delete(bme, geom = bme.faces, context = 3)
    bmesh.ops.delete(bme, geom = delete_verts, context = 1)
    #bmesh.ops.delete(bme, geom = delete_edges, context = 2)  #presuming the delte enum is 0 = verts, 1 = edges, 2 = faces?  who knows.
    
    new_me = bpy.data.meshes.new(ob.name + '_silhouette')
    bme.to_mesh(new_me)
    bme.free()
    
    obj = bpy.data.objects.new(new_me.name, new_me)
    context.scene.objects.link(obj)
    
    obj.select = True
    context.scene.objects.active = obj
    
    if world:
        obj.matrix_world = mx
        
    if smooth:
        mod = obj.modifiers.new('Smooth', 'SMOOTH')
        mod.iterations = 10
    
        mod2 = obj.modifiers.new('Wrap','SHRINKWRAP')
        mod2.target = ob
    
    if debug:
        print("finished in %f seconds" % (time.time() - start))
    
    return

    '''
    for i in range(0,res):
        
        
        angle = 2 * math.pi/res * (i + 1)
        sin = math.sin(angle/2)
        cos = math.cos(angle/2)
    
        quat = Quaternion((cos, sin*axis[0], sin*axis[1], sin*axis[2]))
        
        ob.rotation_quaternion = ob.rotation_quaternion * 
        
    '''

def bezier_to_mesh(crv_obj,  name, n_points = 200):
    C = bpy.context
    me = crv_obj.to_mesh(C.scene, True, 'PREVIEW')
    verts = [v.co for v in me.vertices]
    edges = [(0,1)]
    if crv_obj.data.splines[0].use_cyclic_u:
        edges += [(1,0)]
    
    vs, eds = mesh_cut.space_evenly_on_path(verts, edges, n_points)
    
    bme = bmesh.new()
    bmverts = []
    for v in vs:
        bmverts.append(bme.verts.new(v))
    
    for i in range(0, len(vs)-1):
        bme.edges.new((bmverts[i],bmverts[i+1])) 
    if crv_obj.data.splines[0].use_cyclic_u:
        bme.edges.new((bmverts[n_points-1],bmverts[0])) 
        
    new_me = bpy.data.meshes.new(name)
    bme.to_mesh(new_me)
    return new_me

def extrude_bmesh_loop(bme, bmedges, mx, axis, res, move_only = False):

    '''
    args:
        bme - Blender Mesh Data
        bmedges - edges (not indices of edges)
        mx  - world matrix of object
        z - the world axis which to extrude perpendicular to type Vector...probably the insertion axis
        res - distance step for each extrusion...world size
        move_only - will only translate, not extrude edges
    '''
    start = time.time() #monitor performance
    
    #take the appropriate steps to go to local coords
    imx = mx.copy()
    imx.invert()
    irot = imx.to_quaternion()
    iscl = imx.to_scale() 
    z = irot*axis
    
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    vert_inds = mesh_cut.edge_loops_from_bmedges(bme, [ed.index for ed in bmedges])[0]
    
    if vert_inds[0] != vert_inds[-1]:
        print('Not a closed loop, get out of here!')
        return bme
    
    if not move_only:
        ret = bmesh.ops.extrude_edge_only(bme, edges = bmedges)
        geom_extrude = ret['geom']
        edges_extrude = [ele for ele in geom_extrude if isinstance(ele, bmesh.types.BMEdge)]
    
        #ensure lookup table?
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        vert_inds = mesh_cut.edge_loops_from_bmedges(bme, [ed.index for ed in edges_extrude])[0]
    
    verts = [bme.verts[i] for i in vert_inds]
    verts.pop()  #no need to duplicate the end vert
    vcoords = [vert.co for vert in verts]
    curl = 0
    N = len(verts)
    lerps = []

    for n, v in enumerate(vcoords):
        
        np1 = (n + 1) % N
        nm1 = (n-1) % N
        #Vec representation of the two edges
        V0 = v - vcoords[nm1]
        V1 = vcoords[np1] - v
        
        ##XY projection
        T0 = V0 - V0.project(z)
        T1 = V1 - V1.project(z)
        
        cross = T0.cross(T1)        
        sign = 1
        if cross.dot(z) < 0:
            sign = -1
        
        rot = T0.rotation_difference(T1)  
        ang = rot.angle
        curl = curl + ang*sign
        lerps.append(V0.lerp(V1,.5))

    clockwise = 1

    if curl < 0:
        clockwise = -1
    print('The curl is %f' % curl)
    
        
    for n, v in enumerate(verts):
   
        V = lerps[n]
        trans = z.cross(V)*clockwise
        trans.normalize()
        delta = scale_vec_mult(trans, iscl)
        delta *= res       
        v.co +=  delta       

    print("moved verts in %f seconds" % (time.time()-start))
                    
def register():
    pass

def unregister():
    pass
            
if __name__ == "__main__":
    register()
    print('do something here?')