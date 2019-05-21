'''
Created on Oct 8, 2015

@author: Patrick
'''
from mathutils import Vector, Matrix
import bmesh

def face_neighbors_by_edge(bmface):
    neighbors = []
    for ed in bmface.edges:
        neighbors += [f for f in ed.link_faces if f != bmface]
        
    return neighbors

def face_neighbors_by_vert(bmface):
    neighbors = []
    for v in bmface.verts:
        neighbors += [f for f in v.link_faces if f != bmface]
        
    return neighbors

def face_neighbors(bmface):
    neighbors = []
    for ed in bmface.edges:
        neighbors += [f for f in ed.link_faces if f != bmface]
        
    return neighbors

def face_neighbors_limit(bmface, limit = set()):
    neighbors = []
    for ed in bmface.edges:
        if ed in limit: continue
        neighbors += [f for f in ed.link_faces if f != bmface] 
    return neighbors

def face_neighbors_strict(bmface):
    neighbors = []
    for ed in bmface.edges:
        if not (ed.verts[0].is_manifold and ed.verts[1].is_manifold):
            if len(ed.link_faces) == 1:
                print('found an ed, with two non manifold verts')
            continue
        neighbors += [f for f in ed.link_faces if f != bmface]
        
    return neighbors


def vert_neighbors_manifold(bmvert):
    neighbors = [ed.other_vert(bmvert) for ed in bmvert.link_edges]
    return [v for v in neighbors if v.is_manifold]

def vert_neighbors(bmvert):
    neighbors = [ed.other_vert(bmvert) for ed in bmvert.link_edges]
    return neighbors


#https://blender.stackexchange.com/questions/92406/circular-order-of-edges-around-vertex
# Return edges around param vertex in counter-clockwise order
def connectedEdgesFromVertex_CCW(vertex):

    vertex.link_edges.index_update()
    first_edge = vertex.link_edges[0]

    edges_CCW_order = []

    edge = first_edge
    while edge not in edges_CCW_order:
        edges_CCW_order.append(edge)
        edge = rightEdgeForEdgeRegardToVertex(edge, vertex)

    return edges_CCW_order

# Return the right edge of param edge regard to param vertex
#https://blender.stackexchange.com/questions/92406/circular-order-of-edges-around-vertex
def rightEdgeForEdgeRegardToVertex(edge, vertex):
    right_loop = None

    for loop in edge.link_loops:
        if loop.vert == vertex:
            right_loop = loop
            break
    return loop.link_loop_prev.edge



def bmesh_loose_parts_faces(bme, selected_faces = None, max_iters = 100): 
    '''
    bme - BMesh
    selected_faces = list, set or None
    max_iters = maximum amount
    
    return - list of lists of BMFaces
    '''
    if selected_faces == None:
        total_faces = set(bme.faces[:])
    else:
        if isinstance(selected_faces, list):
            total_faces = set(selected_faces)
        elif isinstance(selected_faces, set):
            total_faces = selected_faces.copy()
            
        else:
            #raise exception
            return []
        
    islands = []
    iters = 0
    while len(total_faces) and iters < max_iters:
        iters += 1
        seed = total_faces.pop()
        island = flood_selection_faces(bme, {}, seed, max_iters = 10000)
        islands += [island]
        total_faces.difference_update(island)
    
    return islands

def bmesh_loose_parts_verts(bme, selected_verts, max_iters = 100): 
    '''
    bme - BMesh
    selected_verts = list, set or None of BMVert
    max_iters = maximum amount of loose parts to be found
    
    return - list of lists of BMVerts
    '''
    if selected_verts == None or len(selected_verts) == 0:
        total_verts = set(bme.verts[:])
       
    else:
        if isinstance(selected_verts, list):
            total_verts = set(selected_verts)
        elif isinstance(selected_verts, set):
            total_verts = selected_verts.copy()  #don't want to modify initial set

        else:
            #raise exception
            return []
    islands = []
    iters = 0
    while len(total_verts) and iters < max_iters:
        iters += 1
        seed = total_verts.pop()
        island = flood_island_within_selected_verts(bme, total_verts, seed, max_iters = 10000)
        islands += [island]
        total_verts.difference_update(island)
    
    return islands

def new_bmesh_from_bmelements(geom):
    
    out_bme = bmesh.new()
    out_bme.verts.ensure_lookup_table()
    out_bme.faces.ensure_lookup_table()
    
    faces = [ele for ele in geom if isinstance(ele, bmesh.types.BMFace)]
    verts = [ele for ele in geom if isinstance(ele, bmesh.types.BMVert)]
    
    vs = set(verts)
    for f in faces:
        vs.update(f.verts[:])
        
    src_trg_map = dict()
    new_bmverts = []
    for v in vs:
    
        new_ind = len(out_bme.verts)
        new_bv = out_bme.verts.new(v.co)
        new_bmverts.append(new_bv)
        src_trg_map[v.index] = new_ind
    
    out_bme.verts.ensure_lookup_table()
    out_bme.faces.ensure_lookup_table()
        
    new_bmfaces = []
    for f in faces:
        v_inds = []
        for v in f.verts:
            new_ind = src_trg_map[v.index]
            v_inds.append(new_ind)
            
        new_bmfaces += [out_bme.faces.new(tuple(out_bme.verts[i] for i in v_inds))]
        
    out_bme.faces.ensure_lookup_table()
    out_bme.verts.ensure_lookup_table()
    out_bme.verts.index_update()
    
   
    out_bme.verts.index_update()        
    out_bme.verts.ensure_lookup_table()
    out_bme.faces.ensure_lookup_table()
    
    return out_bme     

def flood_island_within_selected_verts(bme, selected_verts, seed_element, max_iters = 10000):
    '''
    final all connected verts to seed element that are witin selected_verts
    
    bme - bmesh

    selected_verts - list or set of BMVert
    
    if an empty set, selection will grow to non manifold boundaries
    seed_element - a vertex or face within/out perimeter verts loop
    max_iters - maximum recursions to select_neightbors
    
    return - set of verticies
    '''
    
    if isinstance(selected_verts, list):
        selected_verts = set(selected_verts)
    elif isinstance(selected_verts, set):
        selected_verts = selected_verts.copy()
    
    flood_selection = set()
    flood_selection.add(seed_element)
    new_verts = set([v for v in vert_neighbors(seed_element) if v in selected_verts])
    
    print('print there are %i new_verts at first iteration' % len(new_verts))   
    iters = 0
    while iters < max_iters and new_verts:
        iters += 1
        new_candidates = set()
        for v in new_verts:
            new_candidates.update(vert_neighbors(v))
            
        new_verts = new_candidates & selected_verts
        print('at iteration %i there are %i new_verts' % (iters, len(new_verts)))
        if new_verts:
            flood_selection |= new_verts 
            selected_verts -= new_verts   
    if iters == max_iters:
        print('max iterations reached') 
           
    return flood_selection
       
def flood_selection_vertex_perimeter(bme, perimeter_verts, seed_element, max_iters = 10000):
    '''
    bme - bmesh
    

    perimeter_verts - should create a closed edge loop to contain "flooded" selection.
    
    
    if an empty set, selection will grow to non manifold boundaries
    seed_element - a vertex or face within/out perimeter verts loop
    max_iters - maximum recursions to select_neightbors
    
    return - set of verticies
    '''
    
    flood_selection = set()
    if isinstance(seed_element, bmesh.types.BMVert):
        
        flood_selection.add(seed_element)
        new_verts = set(vert_neighbors(seed_element)) - perimeter_verts
        
    elif isinstance(seed_element, bmesh.types.BMFace):
        flood_selection.update(seed_element.verts[:])
        
        for v in seed_element.verts:
            new_verts = set()
            new_verts.update(set(vert_neighbors(v)) - perimeter_verts)
    
    
    flood_selection |= perimeter_verts
    
    iters = 0
    while iters < max_iters and new_verts:
        iters += 1
        new_candidates = set()
        for v in new_verts:
            new_candidates.update(vert_neighbors(v))
            
        new_verts = new_candidates - flood_selection
        
        if new_verts:
            flood_selection |= new_verts    
    if iters == max_iters:
        print('max iterations reached') 
           
    return flood_selection
      
def flood_selection_by_verts(bme, selected_faces, seed_face, max_iters = 1000):
    '''
    bme - bmesh
    selected_faces - should create a closed face loop to contain "flooded" selection
    if an empty set, selection willg grow to non manifold boundaries
    seed_face - a face within/out selected_faces loop
    max_iters - maximum recursions to select_neightbors
    
    return - set of faces
    '''
    total_selection = set([f for f in selected_faces])
    levy = set([f for f in selected_faces])  #it's funny because it stops the flood :-)

    new_faces = set(face_neighbors_strict(seed_face)) - levy
    iters = 0
    while iters < max_iters and new_faces:
        iters += 1
        new_candidates = set()
        for f in new_faces:
            new_candidates.update(face_neighbors_strict(f))
            
        new_faces = new_candidates - total_selection
        
        if new_faces:
            total_selection |= new_faces    
    if iters == max_iters:
        print('max iterations reached')    
    return total_selection

def flood_selection_faces(bme, selected_faces, seed_face, max_iters = 1000):
    '''
    bme - bmesh
    selected_faces - should create a closed face loop to contain "flooded" selection
    if an empty set, selection willg grow to non manifold boundaries
    seed_face - a face within/out selected_faces loop
    max_iters - maximum recursions to select_neightbors
    
    return - set of faces
    '''
    total_selection = set([f for f in selected_faces])
    levy = set([f for f in selected_faces])  #it's funny because it stops the flood :-)

    new_faces = set(face_neighbors(seed_face)) - levy
    iters = 0
    while iters < max_iters and new_faces:
        iters += 1
        new_candidates = set()
        for f in new_faces:
            new_candidates.update(face_neighbors(f))
            
        new_faces = new_candidates - total_selection
        
        if new_faces:
            total_selection |= new_faces    
    if iters == max_iters:
        print('max iterations reached')    
    return total_selection

def partition_faces_between_edge_boundaries(bme, input_faces, boundary_edges, max_iters = 1000):
    
    if len(input_faces) == 0:
        input_faces = set(bme.faces[:])
        
    
    iters = 0    
    islands = []
    while len(input_faces) and iters < max_iters:
        iters += 1
        
        seed_face = input_faces.pop()
        island = flood_selection_edge_loop(bme, boundary_edges, seed_face, max_iters = 10000)
        
        input_faces.difference_update(island)
    
        islands += [island]
        
    return islands

def flood_selection_edge_loop(bme, edge_loop, seed_face, max_iters = 1000):
    '''
    bme - bmesh
    edge_loop - should create a closed edge loop to contain "flooded" selection
    if an empty set, selection will grow to non manifold boundaries
    seed_face - a face within/out selected_faces loop
    max_iters - maximum recursions to select_neightbors
    
    return - set of faces
    '''
    
    edge_levy = set([e for e in edge_loop])
    def face_neighbors_by_edge(bmface):
        
        neighbors = []
        for ed in bmface.edges:
            neighbors += [f for f in ed.link_faces if f != bmface and ed not in edge_levy]
        
        return neighbors
        
        
    total_selection = set()
    total_selection.add(seed_face)
        
    new_faces = set(face_neighbors_by_edge(seed_face)) #- face_levy
    iters = 0
    while iters < max_iters and new_faces:
        iters += 1
        new_candidates = set()
        for f in new_faces:
            new_candidates.update(face_neighbors_by_edge(f))
            
        new_faces = (new_candidates - total_selection)
        #remove = set()
        #for f in new_faces:
        #    if any([e for e in f.edges if e in edge_levy]):
        #        remove.add(f)
                
        
        
        if new_faces:
            total_selection |= new_faces
            #new_faces -= face_levy    
    if iters == max_iters:
        print('max iterations reached')   
        

    return total_selection

def grow_selection(bme, start_faces, max_iters = 1000):
    '''
    a simple "select more" if oyu pass None for stop_face and
    max_iters = number of times to select more
    
    args:
        bme - BMesh
        start_faces = List or Set of BMFaces
        max_iters = Int, number of times to select more
        
    return
        set(BMFaces)
    '''

    print('there are %i start_faces' % len(start_faces))
    if isinstance(start_faces, list):
        total_selection = set(start_faces)
        new_faces = set()
        for f in start_faces:
            new_faces.update(face_neighbors_by_vert(f))
    
        print('there are %i new_faces' % len(new_faces))
        
    elif isinstance(start_faces, set):
        total_selection = set()
        total_selection.update(start_faces)
        
        new_faces = set()
        for f in start_faces:
            new_faces.update(face_neighbors_by_vert(f))
    
        print('there are %i new_faces' % len(new_faces))
    
    iters = 0
    while iters < max_iters and len(new_faces):
        iters += 1
        candidates = set()
        for f in new_faces:
            candidates.update(face_neighbors(f))
        
        new_faces = candidates - total_selection   
        if new_faces:
            total_selection |= new_faces
             
    if iters == max_iters:
        print('max iterations reached')
            
    return total_selection 

def grow_selection_to_find_face(bme, start_face, stop_face, max_iters = 1000):
    '''
    contemplating indexes vs faces themselves?  will try both ways for speed
    will grow selection iterartively with neighbors until stop face is
    reached.
    '''

    total_selection = set([start_face])
    new_faces = set(face_neighbors(start_face))
    
    if stop_face in new_faces:
        total_selection |= new_faces
        return total_selection
    
    iters = 0
    while iters < max_iters and stop_face not in new_faces:
        iters += 1
        candidates = set()
        for f in new_faces:
            candidates.update(face_neighbors(f))
        
        new_faces = candidates - total_selection   
        if new_faces:
            total_selection |= new_faces
             
    if iters == max_iters:
        print('max iterations reached')
            
    return total_selection

def decrease_vert_selection(bme, selected_verts, iterations = 1):
    '''
    remove outer layer of selection
    
    TODO, treat this as a region growing subtraction of the border
    rather than iterate the whole selection each time.  
    '''
    
    #make a copy instead of modify in place, in case
    #oritinal selection is important
    if isinstance(selected_verts, list):
        sel_verts = set(selected_verts)
    
    elif isinstance(selected_verts, set):
        sel_verts = selected_verts.copy()
    
    def is_boundary(v):
        return not all([ed.other_vert(v) in sel_verts for ed in v.link_edges])
        
    for i in range(iterations):
        
        border = [v for v in sel_verts if is_boundary(v)] #TODO...smarter way to find new border...connected to old border
        sel_verts.difference_update(border)
    
    return sel_verts
    
def increase_vert_selection(bme, selected_verts, iterations = 1):
    '''
    remove outer layer of selection
    
    TODO, treat this as a region growing subtraction of the border
    rather than iterate the whole selection each time.  
    '''
    
    #make a copy instead of modify in place, in case
    #oritinal selection is important
    if isinstance(selected_verts, list):
        sel_verts = set(selected_verts)
    
    elif isinstance(selected_verts, set):
        sel_verts = selected_verts.copy()
    
    #def is_boundary(v):
    #    return not all([ed.other_vert(v) in sel_verts for ed in v.link_edges])
    
    
    new_verts = set()
    for v in sel_verts:
        new_verts.update(vert_neighbors(v))    
        
    iters = 0
    while iters < iterations and new_verts:
        iters += 1
        new_candidates = set()
        for v in new_verts:
            new_candidates.update(vert_neighbors(v))
            
        new_verts = new_candidates - sel_verts
        
        if new_verts:
            sel_verts |= new_verts  
    
    return sel_verts
   
def grow_to_find_mesh_end(bme, start_face, max_iters = 20):
    '''
    will grow selection until a non manifold face is raeched.
    
    geom = dictionary
    
    geom['end'] = BMFace or None, the first non manifold face to be found
    geom['faces'] = list [BMFaces], all the faces encountered on the way
    
    '''

    geom = {}
    
    total_selection = set([start_face])
    new_faces = set(face_neighbors(start_face))
    
    def not_manifold(faces):
        for f in faces:
            if any([not ed.is_manifold for ed in f.edges]):
                return f
        return None
    
    iters = 0
    stop_face = not_manifold(new_faces)
    if stop_face:
        total_selection |= new_faces
        geom['end'] = stop_face
        geom['faces'] = total_selection
        return geom
    
    while new_faces and iters < max_iters and not stop_face:
        iters += 1
        candidates = set()
        for f in new_faces:
            candidates.update(face_neighbors(f))
        
        new_faces = candidates - total_selection   
        if new_faces:
            total_selection |= new_faces
            stop_face = not_manifold(new_faces)
            
    if iters == max_iters:
        print('max iterations reached')
        geom['end'] = None
        
    elif not stop_face:
        print('completely manifold mesh')
        geom['end'] = None
        
    else:
        geom['end'] = stop_face
     
    geom['faces'] = total_selection    
    return geom
    
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

def edge_loops_from_bmedges_old(bmesh, bm_edges):
    """
    Edge loops defined by edges (indices)

    Takes [mesh edge indices] or a list of edges and returns the edge loops

    return a list of vertex indices.
    [ [1, 6, 7, 2], ...]

    closed loops have matching start and end values.
    """
    line_polys = []
    edges = bm_edges.copy()

    while edges:
        current_edge = bmesh.edges[edges.pop()]
        vert_e, vert_st = current_edge.verts[:]
        vert_end, vert_start = vert_e.index, vert_st.index
        line_poly = [vert_start, vert_end]

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
                    vert_end = line_poly[-1]
                    ok = 1
                    del edges[i]
                    # break
                elif v2 == vert_end:
                    line_poly.append(v1)
                    vert_end = line_poly[-1]
                    ok = 1
                    del edges[i]
                    #break
                elif v1 == vert_start:
                    line_poly.insert(0, v2)
                    vert_start = line_poly[0]
                    ok = 1
                    del edges[i]
                    # break
                elif v2 == vert_start:
                    line_poly.insert(0, v1)
                    vert_start = line_poly[0]
                    ok = 1
                    del edges[i]
                    #break
        line_polys.append(line_poly)

    return line_polys

def walk_non_man_edge(bme, start_edge, stop, max_iters = 5000):
    '''
    bme = BMesh
    start_edge - BMEdge
    stop -  set of verts or edges to stop when reached
    
    return- list of edge loops
    '''
    
    #stop criteria
    # found element in stop set
    # found starting edge (completed loop)
    # found vert with 2 other non manifold edges
    
    def next_pair(prev_ed, prev_vert):
        v_next = prev_ed.other_vert(prev_vert)
        eds = [e for e in v_next.link_edges if not e.is_manifold and e != prev_ed]
        print(eds)
        if len(eds):
            return eds[0], v_next
        else:
            return None, None
    
    chains = []
    for v in start_edge.verts:
        edge_loop = []
        prev_v = start_edge.other_vert(v)
        prev_ed = start_edge
        next_ed, next_v = next_pair(prev_ed, prev_v)
        edge_loop += [next_ed]
        iters = 0
        while next_ed and next_v and not (next_ed in stop or next_v in stop) and iters < max_iters:
            iters += 1
            
            next_ed, next_v = next_pair(next_ed, next_v)
            if next_ed:
                edge_loop += [next_ed]
                
        chains += [edge_loop]
     
    return chains

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

def face_region_boundary_loops(bme, sel_faces):
    '''
    bme - BMesh object
    sel_faces:  list of face indices
    
    '''
    face_set = set(sel_faces)
    edges_raw = [ed.index for ed in bme.edges if ed.select and len([f.index for f in ed.link_faces if f.index in face_set]) == 1]
    
    geom_dict = edge_loops_from_bmedges(bme, edges_raw, ret={'VERTS','EDGES'})
    
    return geom_dict

def join_bmesh(source, target, src_trg_map, src_mx = None, trg_mx = None):
    '''
    
    '''
    L = len(target.verts)
    print('Target has %i verts' % L)
    
    print('Source has %i verts' % len(source.verts))
    l = len(src_trg_map)
    print('is the src_trg_map being sticky...%i' % l)
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
            #new_bv.index = new_ind
            src_trg_map[v.index] = new_ind
    
    #new_bmverts = [target.verts.new(i_trg_mx * src_mx * v.co) for v in source.verts]# if v.index not in src_trg_map]

    #def src_to_trg_ind(v):
    #    subbed = False
    #    if v.index in src_trg_map:

    #       new_ind = src_trg_map[v.index]
    #        subbed = True
    #    else:
    #        new_ind = v.index + L  #TODO, this takes the actual versts from sources, these verts are in target
            
    #    return new_ind, subbed
    
    #new_bmfaces = [target.faces.new(tuple(new_bmverts[v.index] for v in face.verts)) for face in source.faces]
    target.verts.index_update()
    #target.verts.sort()  #does this still work?
    target.verts.ensure_lookup_table()
    #print('new faces')
    #for f in source.faces:
        #print(tuple(src_to_trg_ind(v) for v in f.verts))
    
    #subbed = set()
    new_bmfaces = []
    for f in source.faces:
        v_inds = []
        for v in f.verts:
            new_ind = src_trg_map[v.index]
            v_inds.append(new_ind)
          
        new_bmfaces += [target.faces.new(tuple(target.verts[i] for i in v_inds))]
    
    #new_bmfaces = [target.faces.new(tuple(target.verts[src_to_trg_ind(v)] for v in face.verts)) for face in source.faces]
    target.faces.ensure_lookup_table()
    target.verts.ensure_lookup_table()
    target.verts.index_update()
    
    #throw away the loose verts...not very elegant with edges and what not
    #n_removed = 0
    #for vert in new_bmverts:
    #    if (vert.index - L) in src_trg_map: #these are verts that are not needed
    #        target.verts.remove(vert)
    #        n_removed += 1
    
    #bmesh.ops.delete(target, geom=del_verts, context=1)
            
    target.verts.index_update()        
    target.verts.ensure_lookup_table()
    target.faces.ensure_lookup_table()
    
    new_L = len(target.verts)
    
    if src_trg_map:
        if new_L != L + len(source.verts) -l:
            print('seems some verts were left in that should not have been')
            
    del src_trg_map


def ensure_lookup(bme):
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.faces.ensure_lookup_table()