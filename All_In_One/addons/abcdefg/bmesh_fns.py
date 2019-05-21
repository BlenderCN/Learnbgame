import bpy
import bmesh
from mathutils import Matrix, Vector, Color
import loops_tools
from mathutils.bvhtree import BVHTree


def find_face_loop(bme, ed, select = False):
    '''
    takes a bmedge, and walks perpendicular to it
    returns [face inds], [ed inds]
    '''
    #reality check
    if not len(ed.link_faces): return []
    
    def ed_to_vect(ed):
        vect = ed.verts[1].co - ed.verts[0].co
        vect.normalize()
        return vect
        
    def next_edge(cur_face, cur_ed):
        ledges = [ed for ed in cur_face.edges]
        n = ledges.index(cur_ed)
        j = (n+2) % 4
        return cur_face.edges[j]
    
    def next_face(cur_face, edge):
        if len(edge.link_faces) == 1: return None
        next_face = [f for f in edge.link_faces if f != cur_face][0]
        return next_face
    
    loop_eds = []
    loop_faces = []
    loop_revs = []

    for f in ed.link_faces:
        if len(f.edges) != 4: continue            
        eds = [ed.index]
        fs = [f.index]
        revs = [False]   
        
        f_next = True
        f_cur = f
        ed_cur = ed
        while f_next != f:
            if select:
                f_cur.select_set(True) 
                ed_cur.select_set(True)
            
            ed_next = next_edge(f_cur, ed_cur)
            eds += [ed_next.index]
            
            parallel = ed_to_vect(ed_next).dot(ed_to_vect(ed_cur)) > 0
            prev_rev = revs[-1]
            rever = parallel == prev_rev                
            revs += [rever]
            
            f_next = next_face(f_cur, ed_next)
            if not f_next: break
            
            fs += [f_next.index]
            if len(f_next.verts) != 4:
                break
            
            ed_cur = ed_next
            f_cur = f_next
            
        #if we looped
        if f_next == f:

            face_loop_fs = fs
            face_loop_eds = eds[:len(eds)-1]

            return face_loop_fs, face_loop_eds
        else:
            if len(fs):
                loop_faces.append(fs)
                loop_eds.append(eds)
                loop_revs.append(revs)
    
    if len(loop_faces) == 2:    
        loop_faces[0].reverse()    
        face_loop_fs = loop_faces[0] +  loop_faces[1]
        tip = loop_eds[0][1:]
        tip.reverse()
        face_loop_eds = tip + loop_eds[1]
        rev_tip = loop_revs[0][1:]
        rev_tip.reverse()

        
    elif len(loop_faces) == 1:
        face_loop_fs = loop_faces[0]
        face_loop_eds = loop_eds[0]

    else:
        face_loop_fs, face_loop_eds = [], []
        
    return  face_loop_fs, face_loop_eds

def edge_loops_from_bmedges(bmesh, bm_edges, ret = {'VERTS'}):
    """
    args:
       bmesh - a BMEsh
       bm_edges - an UNORDERED list of edge indices in the bmesh
       ret - a dictionary with {'VERTS', 'EDGES'}  which determines what data to return
    
    returns:
        a dictionary with keys 'VERTS' 'EDGES' containing lists of the corresponding data

    geom_dict['VERTS'] =   [ [1, 6, 7, 2], ...]

    closed loops have matching start and end vert indices
    closed loops will not have duplicate edge indices
    
    Notes:  This method is not "smart" in any way, and does not leverage BMesh
    connectivity data.  Therefore it could iterate  len(bm_edges)! (factorial) times
    There are better methods to use if your bm_edges are already in order  This is mostly
    used to sort non_man_edges = [ed.index for ed in bmesh.edges if not ed.is_manifold]
    There will be better methods regardless that utilize walking some day....
    """
    geom_dict = dict()
    geom_dict['VERTS'] = []
    geom_dict['EDGES'] = []
    edges = bm_edges.copy()
    
    while edges:
        current_edge = bmesh.edges[edges.pop()]
        
        vert_e, vert_st = current_edge.verts[:]
        vert_end, vert_start = vert_e.index, vert_st.index
        line_poly = [vert_start, vert_end]
        ed_loop = [current_edge.index]
        ok = True
        while ok:
            ok = False
            #for i, ed in enumerate(edges):
            i = len(edges)
            while i:
                i -= 1
                ed = bmesh.edges[edges[i]]
                v_1, v_2 = ed.verts
                v1, v2 = v_1.index, v_2.index
                if v1 == vert_end:
                    line_poly.append(v2)
                    ed_loop.append(ed.index)
                    vert_end = line_poly[-1]
                    ok = 1
                    del edges[i]
                    # break
                elif v2 == vert_end:
                    line_poly.append(v1)
                    ed_loop.append(ed.index)
                    vert_end = line_poly[-1]
                    ok = 1
                    del edges[i]
                    #break
                elif v1 == vert_start:
                    line_poly.insert(0, v2)
                    ed_loop.insert(0, ed.index)
                    vert_start = line_poly[0]
                    ok = 1
                    del edges[i]
                    # break
                elif v2 == vert_start:
                    line_poly.insert(0, v1)
                    ed_loop.insert(0, ed.index)
                    vert_start = line_poly[0]
                    ok = 1
                    del edges[i]#break
        
          
        if 'VERTS' in ret:            
            geom_dict['VERTS'] += [line_poly]
        if 'EDGES' in ret:
            print('adding edge loop to dict')
            geom_dict['EDGES'] += [ed_loop]

    return geom_dict

def edge_loop_neighbors(bme, edge_loop, strict = False, trim_tails = True, expansion = 'EDGES', quad_only = True):
    '''
    bme - the bmesh which the edges belongs to
    edge_loop - list of BMEdge indices.  Not necessarily in order, possibly multiple edge loops
    strict - Bool
           False , not strict, returns all loops regardless of topology
           True  ,  loops must be connected by quads only
                    Only returns  if the parallel loops are exactly the same length as original loop
        
    trim_tails - will trim p shaped loops or figure 8 loops
    
    expansion - 'EDGES'  - a single edge loop within a mesh will return 
                           2 parallel and equal length edge loops
                'VERTS'  - a single edge loop within a mesh will return
                           a single edge loop around the single loop
                           only use with strict = False
    
    quad_only  - Allow for generic edge loop expansion in triangle meshes if False
    
    returns a dictionary  with keys 'VERTS' 'EDGES' 'FACES'.  geom_dict
    
    the 'VERTS' and 'EDGES' lists are correlated.
    Eg geom_dict['VERTS'][0] and geom_dict['EDGES'][0] are corresponding vert and edge loops
    However geom_dict['FACES'][0] may correlate with geom_dict['EDGES'][1]
    
    
    '''
    
    
    ed_loops = edge_loops_from_bmedges(bme, edge_loop, ret = {'VERTS','EDGES'})
    
    geom_dict = dict()
    geom_dict['VERTS'] = []
    geom_dict['EDGES'] = []
    geom_dict['FACES'] = []
    
    for v_inds, ed_inds in zip(ed_loops['VERTS'],ed_loops['EDGES']):
        
        v0 = bme.verts[v_inds[0]]
        e0 = bme.edges[ed_inds[0]]
        v1 = e0.other_vert(v0)
        
        orig_eds = set(ed_inds)
        #find all the faces directly attached to this edge loop
        all_faces = set()
        
        if quad_only:
            if expansion == 'EDGES':
                for e_ind in ed_inds:
                    all_faces.update([f.index for f in bme.edges[e_ind].link_faces if len(f.verts) == 4])
                
            elif expansion == 'VERTS':
                for v_ind in v_inds:
                    all_faces.update([f.index for f in bme.verts[v_ind].link_faces if len(f.verts) == 4])
                
        else:
            for e_ind in ed_inds:
                for v in bme.edges[e_ind].verts:            
                    all_faces.update([f.index for f in v.link_faces])
        
        #find all the edges perpendicular to this edge loop
        perp_eds = set()
        for v_ind in v_inds:
            perp_eds.update([ed.index for ed in bme.verts[v_ind].link_edges if ed.index not in orig_eds])
        
        
        parallel_eds = []
        
        if quad_only:
            for f_ind in all_faces:
                parallel_eds += [ed.index for ed in bme.faces[f_ind].edges if 
                             ed.index not in perp_eds and ed.index not in orig_eds
                             and not (all([f.index in all_faces for f in ed.link_faces]) and trim_tails)]
        else:
            for f_ind in all_faces:
                parallel_eds += [ed.index for ed in bme.faces[f_ind].edges if
                                 ed.index not in orig_eds
                                 and not all([f.index in all_faces for f in ed.link_faces])]
        
            print('Triangle Problems ')
            print(parallel_eds)
        #sort them!    
        parallel_loops =  edge_loops_from_bmedges(bme, parallel_eds, ret = {'VERTS','EDGES'})   
        
        #get the face loops, a little differently, just walk from 2 perpendicular edges

        for ed in v1.link_edges:
            if ed.index not in perp_eds: continue
            f_inds, _e_inds = find_face_loop(bme, ed, select=False)
            #print(f_inds)
            #keep only the part of face loop direclty next door
            if strict:
                f_inds = [f for f in f_inds if f in all_faces]
            geom_dict['FACES'] += [f_inds]
        
        if strict:
            if all([len(e_loop) == len(ed_inds) for e_loop in parallel_loops['EDGES']]):
                for v_loop in parallel_loops['VERTS']:
                    geom_dict['VERTS'] += [v_loop]
                for e_loop in parallel_loops['EDGES']:
                    geom_dict['EDGES'] += [e_loop]
                
                
            elif any([len(e_loop) == len(ed_inds) for e_loop in parallel_loops['EDGES']]):

                for pvs, peds in zip(parallel_loops['VERTS'],parallel_loops['EDGES']):
                    if len(peds) == len(ed_inds):
                        geom_dict['VERTS'] += [pvs]
                        geom_dict['EDGES'] += [peds]
                

        else:
            for v_loop in parallel_loops['VERTS']:
                geom_dict['VERTS'] += [v_loop]
            for e_loop in parallel_loops['EDGES']:
                geom_dict['EDGES'] += [e_loop]
    
                      
    return geom_dict


def remove_undercuts(context, ob, view, world = True, smooth = True, epsilon = .000001):
    '''
    args:
      ob - mesh object
      view - Mathutils Vector
      
    return:
       Bmesh with Undercuts Removed?
       
    best to make sure normals are consistent beforehand
    best for manifold meshes, however non-man works
    noisy meshes can be compensated for with island threhold
    '''
    
        
    #careful, this can get expensive with multires
    me = ob.to_mesh(context.scene, True, 'RENDER')    
    bme = bmesh.new()
    bme.from_mesh(me)
    bme.normal_update()
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.faces.ensure_lookup_table()
    
    bvh = BVHTree.FromBMesh(bme)
    
    #keep track of the world matrix
    mx = ob.matrix_world
    
    if world:
        #meaning the vector is in world coords
        #we need to take it back into local
        i_mx = mx.inverted()
        view = i_mx.to_quaternion() * view
            
    face_directions = [[0]] * len(bme.faces)
    
    up_faces = set()
    overhang_faces = set()  #all faces pointing away from view
    #precalc all the face directions and store in dict
    for f in bme.faces:
        direction = f.normal.dot(view)
        
        if direction <= -epsilon:
            overhang_faces.add(f)
        else:
            up_faces.add(f)
            
        face_directions[f.index] = direction
    
    print('there are %i up_faces' % len(up_faces))
    print('there are %i down_faces' % len(overhang_faces))
    
    
    #for f in bme.faces:
    #    if f in overhangs:
    #        f.select_set(True)
    #    else:
    #        f.select_set(False)
            
    overhang_islands = [] #islands bigger than a certain threshold (by surface area?
    upfacing_islands = []
    def face_neighbors_up(bmface):
        neighbors = []
        for ed in bmface.edges:
            neighbors += [f for f in ed.link_faces if f != bmface and f in up_faces]
            
        return neighbors
    #remove smal islands from up_faces and add to overhangs
    max_iters = len(up_faces)
    iters_0 = 0
    islands_removed = 0
    
    up_faces_copy = up_faces.copy()
    while len(up_faces_copy) and iters_0 < max_iters:
        iters_0 += 1
        max_iters_1 = len(up_faces)
        seed = up_faces_copy.pop()
        new_faces = set(face_neighbors_up(seed))
        up_faces_copy -= new_faces
        
        island = set([seed])
        island |= new_faces
        
        iters_1 = 0
        while iters_1 < max_iters_1 and new_faces:
            iters_1 += 1
            new_candidates = set()
            for f in new_faces:
                new_candidates.update(face_neighbors_up(f))
            
            new_faces = new_candidates - island
        
            if new_faces:
                island |= new_faces    
                up_faces_copy -= new_faces
        if len(island) < 75: #small patch surrounded by overhang, add to overhang area
            islands_removed += 1
            overhang_faces |= island
        else:
            upfacing_islands += [island]
            
    print('%i upfacing islands removed' % islands_removed)
    print('there are now %i down faces' % len(overhang_faces))
    
    def face_neighbors_down(bmface):
        neighbors = []
        for ed in bmface.edges:
            neighbors += [f for f in ed.link_faces if f != bmface and f in overhang_faces]
            
        return neighbors
    overhang_faces_copy = overhang_faces.copy()
    
    while len(overhang_faces_copy):
        seed = overhang_faces_copy.pop()
        new_faces = set(face_neighbors_down(seed))
        island = set([seed])
        island |= new_faces
        overhang_faces_copy -= new_faces
        iters = 0
        while iters < 100000 and new_faces:
            iters += 1
            new_candidates = set()
            for f in new_faces:
                new_candidates.update(face_neighbors_down(f))
            
            new_faces = new_candidates - island
        
            if new_faces:
                island |= new_faces    
                overhang_faces_copy -= new_faces
        if len(island) > 75: #TODO, calc overhang factor.  Surface area dotted with direction
            overhang_islands += [island]
    
    for f in bme.faces:
        f.select_set(False)   
    for ed in bme.edges:
        ed.select_set(False)
    for v in bme.verts:
        v.select_set(False)
            
    island_loops = []
    island_verts = []
    del_faces = set()
    for isl in overhang_islands:
        loop_eds = []
        loop_verts = []
        del_faces |= isl
        for f in isl:
            for ed in f.edges:
                if len(ed.link_faces) == 1:
                    loop_eds += [ed]
                    loop_verts += [ed.verts[0], ed.verts[1]]
                elif (ed.link_faces[0] in isl) and (ed.link_faces[1] not in isl):
                    loop_eds += [ed]
                    loop_verts += [ed.verts[0], ed.verts[1]]
                elif (ed.link_faces[1] in isl) and (ed.link_faces[0] not in isl):
                    loop_eds += [ed]
                    loop_verts += [ed.verts[0], ed.verts[1]]
                    
            #f.select_set(True) 
        island_verts += [list(set(loop_verts))]
        island_loops += [loop_eds]
    
    bme.faces.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    
    loop_edges = []
    for ed_loop in island_loops:
        loop_edges += ed_loop
        for ed in ed_loop:
            ed.select_set(True)
    
    loops_tools.relax_loops_util(bme, loop_edges, 5)
    
    for ed in bme.edges:
        ed.select_set(False)
        
    exclude_vs = set()
    for vs in island_verts:
        exclude_vs.update(vs)
    
    smooth_verts = []    
    for v in exclude_vs:
        smooth_verts += [ed.other_vert(v) for ed in v.link_edges if ed.other_vert(v) not in exclude_vs]
            
    ret = bmesh.ops.extrude_edge_only(bme, edges = loop_edges)
    
    
    new_fs = [ele for ele in ret['geom'] if isinstance(ele, bmesh.types.BMFace)]                
    new_vs = [ele for ele in ret['geom'] if isinstance(ele, bmesh.types.BMVert)]
    
    #TODO, ray cast down to base plane?
    for v in new_vs:
        v.co -= 10*view
    
    for f in new_fs:
        f.select_set(True)
        
    bmesh.ops.delete(bme, geom = list(del_faces), context = 3)
    
    del_verts = []
    for v in bme.verts:
        if all([f in del_faces for f in v.link_faces]):
            del_verts += [v]        
    bmesh.ops.delete(bme, geom = del_verts, context = 1)
    
    
    del_edges = []
    for ed in bme.edges:
        if len(ed.link_faces) == 0:
            del_edges += [ed]
    print('deleting %i edges' % len(del_edges))
    bmesh.ops.delete(bme, geom = del_edges, context = 4) 
    bmesh.ops.recalc_face_normals(bme, faces = new_fs)
    
    bme.normal_update()
    
    new_me = bpy.data.meshes.new(ob.name + '_blockout')
    
    obj = bpy.data.objects.new(new_me.name, new_me)
    context.scene.objects.link(obj)
    
    obj.select = True
    context.scene.objects.active = obj
    
    bme.to_mesh(obj.data)
    # Get material
    mat = bpy.data.materials.get("Model Material")
    if mat is None:
        # create material
        print('creating model material')
        mat = bpy.data.materials.new(name="Model Material")
        #mat.diffuse_color = Color((0.8, .8, .8))
    
    # Assign it to object
    obj.data.materials.append(mat)
    print('Model material added')
    
    mat2 = bpy.data.materials.get("Undercut Material")
    if mat2 is None:
        # create material
        mat2 = bpy.data.materials.new(name="Undercut Material")
        mat2.diffuse_color = Color((0.8, .2, .2))
    

    obj.data.materials.append(mat2)
    mat_ind = obj.data.materials.find("Undercut Material")
    print('Undercut material is %i' % mat_ind)
    
    for f in new_faces:
        obj.data.polygons[f.index].material_index = mat_ind
            
    if world:
        obj.matrix_world = mx

    bme.free()
    del bvh
        
    return


def join_bmesh_map(source, target, src_trg_map = None, src_mx = None, trg_mx = None):
    '''
    
    '''
    
 
    L = len(target.verts)
    
    if not src_trg_map:
        src_trg_map = {-1:-1}
    l = len(src_trg_map)
    print('There are %i items in the vert map' % len(src_trg_map))
    if not src_mx:
        src_mx = Matrix.Identity(4)
    
    if not trg_mx:
        trg_mx = Matrix.Identity(4)
        i_trg_mx = Matrix.Identity(4)
    else:
        i_trg_mx = trg_mx.inverted()
        
        
    old_bmverts = [v for v in target.verts]  #this will store them in order
    new_bmverts = [] #these will be created in order
    
    source.verts.ensure_lookup_table()

    for v in source.verts:
        if v.index not in src_trg_map:
            new_ind = len(target.verts)
            new_bv = target.verts.new(i_trg_mx * src_mx * v.co)
            new_bmverts.append(new_bv)  #gross...append
            src_trg_map[v.index] = new_ind
            
        else:
            print('vert alread in the map %i' % v.index)
    
    lverts = old_bmverts + new_bmverts
    
    target.verts.index_update()
    target.verts.ensure_lookup_table()
    
    new_bmfaces = []
    for f in source.faces:
        v_inds = []
        for v in f.verts:
            new_ind = src_trg_map[v.index]
            v_inds.append(new_ind)
            
        if any([i > len(lverts)-1 for i in v_inds]):
            print('impending index error')
            print(len(lverts))
            print(v_inds)
            
        if target.faces.get(tuple(lverts[i] for i in v_inds)):
            print(v_inds)
            continue
        new_bmfaces += [target.faces.new(tuple(lverts[i] for i in v_inds))]
    
        target.faces.ensure_lookup_table()
    target.verts.ensure_lookup_table()

    new_L = len(target.verts)
    
    if src_trg_map:
        if new_L != L + len(source.verts) -l:
            print('seems some verts were left in that should not have been')
 
def join_bmesh(source, target, src_mx = None, trg_mx = None):

    src_trg_map = dict()
    L = len(target.verts)
    if not src_mx:
        src_mx = Matrix.Identity(4)
    
    if not trg_mx:
        trg_mx = Matrix.Identity(4)
        i_trg_mx = Matrix.Identity(4)
    else:
        i_trg_mx = trg_mx.inverted()
        
        
    new_bmverts = []
    source.verts.ensure_lookup_table()

    for v in source.verts:
        if v.index not in src_trg_map:
            new_ind = len(target.verts)
            new_bv = target.verts.new(i_trg_mx * src_mx * v.co)
            new_bmverts.append(new_bv)
            src_trg_map[v.index] = new_ind
    
    
    target.verts.index_update()
    target.verts.ensure_lookup_table()

    new_bmfaces = []
    for f in source.faces:
        v_inds = []
        for v in f.verts:
            new_ind = src_trg_map[v.index]
            v_inds.append(new_ind)
            
        new_bmfaces += [target.faces.new(tuple(target.verts[i] for i in v_inds))]
    
    target.faces.ensure_lookup_table()
    target.verts.ensure_lookup_table()
    target.verts.index_update()
    
   
    target.verts.index_update()        
    target.verts.ensure_lookup_table()
    target.faces.ensure_lookup_table()
    
    new_L = len(target.verts)
    

    if new_L != L + len(source.verts):
        print('seems some verts were left out')
            
           
def join_objects(obs, name = ''):
    '''
    uses BMesh to join objects.  Advantage is that it is context
    agnostic, so no editmoe or bpy.ops has to be used.
    
    Args:
        obs - list of Blender objects
    
    Returns:
        new object with name specified.  Otherwise '_joined' will
        be added to the name of the first object in the list
    '''
    target_bme = bmesh.new()
    target_bme.verts.ensure_lookup_table()
    target_bme.faces.ensure_lookup_table()
    trg_mx = obs[0].matrix_world
    
    if name == '':
        name = obs[0].name + '_joined'
    
    for ob in obs:
        src_mx = ob.matrix_world

        if ob.data.is_editmode:
            src_bme = bmesh.from_editmesh(ob.data)
        else:
            src_bme = bmesh.new()
            if ob.type == 'MESH':
                if len(ob.modifiers):
                    src_bme.from_object(ob, bpy.context.scene)
                else:
                    src_bme.from_mesh(ob.data)
            else:
                me = ob.to_mesh(bpy.context.scene, apply_modifiers = True, settings = 'PREVIEW')
                src_bme.from_mesh(me)
                bpy.data.meshes.remove(me)
        join_bmesh(src_bme, target_bme, src_mx, trg_mx)

        src_bme.free()
    
    new_me = bpy.data.meshes.new(name)    
    new_ob = bpy.data.objects.new(name, new_me)
    new_ob.matrix_world = trg_mx
    target_bme.to_mesh(new_me)
    target_bme.free()
    return new_ob
    