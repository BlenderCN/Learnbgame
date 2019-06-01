'''
Created on Oct 8, 2015

@author: Patrick
'''
#Python Imports
import time
from itertools import chain,combinations

#Blender/bpy/bmesh imports
import bpy
from mathutils import Vector, Matrix, Quaternion
from mathutils.geometry import intersect_line_plane, intersect_point_line, distance_point_to_plane, intersect_line_line_2d, intersect_line_line

#Cut Mesh imports
from .bmesh_fns import face_neighbors, flood_selection_faces, grow_selection_to_find_face, edge_loops_from_bmedges, walk_non_man_edge
from .common.blender import bversion

#basic utils
def list_shift(seq, n):
    n = n % len(seq)
    return seq[n:] + seq[:n]


def find_bmedges_crossing_plane(pt, no, edges, epsilon, sort = False):
    '''
    pt - pt on cutting plane: mathutils.Vector
    no - normal of cutting plane: mathutils.Vector
    edges - edges of BMFace:  bmesh.BMEdge
    epsilon - dist from plane < epsilon means coplanar
    
    returns a list of tupples (edge, intersection):  [(BMEdges, mathutils.Vector)]
    
    if there are more than two (indicating a concave NGon) edges will be returned
    ordered across the ngon (in an arbitrary direction) such that only 
    intersections (0,1), (2,3), (4,5) can make valid edges.
    
    this information is useful for special cases like E or pac-man shaped Ngons (dumb scenarios)
    see this image #TODO link
    
    also, for God's sake, the NGon better be planar
    '''
    
    coords = {}
    for edge in edges:
        v0,v1 = edge.verts
        if v0 not in coords: coords[v0] = no.dot(v0.co-pt)
        if v1 not in coords: coords[v1] = no.dot(v1.co-pt)
    #print(str(coords))
    
    i_edges = []
    intersects = []
    ds = [] 
    signed_ds = []
    
    for edge in edges:
        v0,v1 = edge.verts
        s0,s1 = coords[v0],coords[v1]
        if s0 > epsilon and s1 > epsilon: continue
        if s0 < -epsilon and s1 < -epsilon: continue
        #if not ((s0>epsilon and s1<-epsilon) or (s0<-epsilon and s1>epsilon)):      # edge cross plane?
        #    continue
        
        i = intersect_line_plane(v0.co, v1.co, pt, no)
        if not i: continue  
        d = (i - pt).length
        if d == 0.00:
            d = epsilon
        i_edges += [edge]
        intersects += [i]
        ds += [d]
    
    if len(i_edges) == 3:
        print('\n\nTHE THREE EDGE ERROR')
        print('3 edges crossing plane')
        sorted_edges = []
        sorted_is = []         
    elif len(i_edges) > 3:  #a concave ngon with 4,6,8.. crossings
        
        print('There are %i crossed edges' % len(i_edges))
        print('There are %i total edges' % len(edges))
        
        if len(i_edges) == 3:
            return 
        #all the crossings are colinear if ngon is planar, so sorting them is easy
        min_i = intersects[ds.index(min(ds))]
        min_ed = i_edges[ds.index(min(ds))]
        
        max_i = intersects[ds.index(max(ds))]
        direction = (max_i - min_i).normalized()
        
        signed_ds = []
        for j, ed in enumerate(i_edges):
            signed_ds += [(intersects[j] - min_i).dot(direction)]
            
        print('signed_ds')
        print(signed_ds)
        
        #[x for (y,x) in sorted(zip(Y,X))]  X sorted by Y
        sorted_edges = [ed for (d,ed) in sorted(zip(signed_ds,i_edges))]
        sorted_is = [i for (d,i) in sorted(zip(signed_ds, intersects))]
        n = sorted_edges.index(min_ed)
        
        if n % 2:
            print('shifting and reversing')
            sorted_edges = list(reversed(list_shift(sorted_edges, n + 1)))
            sorted_is = list(reversed(list_shift(sorted_is, n + 1)))
    
    elif len(i_edges) == 0:
        print('no edges crossing plane')
        sorted_edges = []
        sorted_is = [] 
    else:
        if sort:
            #[x for (y,x) in sorted(zip(Y,X))]  X sorted by Y
            sorted_edges = [ed for (d, ed) in sorted(zip(ds, i_edges))]
            sorted_is = [i for (d, i) in sorted(zip(ds, intersects))]
        else:
            sorted_edges = i_edges
            sorted_is = intersects
           
    return list(zip(sorted_edges,sorted_is))

def find_distant_bmedge_crossing_plane(pt, no, edges, epsilon, e_ind_from, co_from):
    '''
    returns the farthest edge that *crosses* plane and corresponding intersection point
    '''
    
    if(len(edges)==3):
        # shortcut (no need to find farthest... just find first)
        for edge in edges:
            if edge.index == e_ind_from: continue
            v0,v1 = edge.verts
            co0,co1 = v0.co,v1.co
            s0,s1 = no.dot(co0 - pt), no.dot(co1 - pt)
            no_cross = not ((s0>epsilon and s1<-epsilon) or (s0<-epsilon and s1>epsilon))
            if no_cross: continue
            i = intersect_line_plane(co0, co1, pt, no)
            return (edge,i)
    
    d_max,edge_max,i_max = -1.0,None,None
    for edge in edges:
        if edge.index == e_ind_from: continue
        
        v0,v1 = edge.verts
        co0,co1 = v0.co, v1.co
        s0,s1 = no.dot(co0 - pt), no.dot(co1 - pt)
        if s0 > epsilon and s1 > epsilon: continue
        if s0 < -epsilon and s1 < -epsilon: continue
        #if not ((s0>epsilon and s1<-epsilon) or (s0<-epsilon and s1>epsilon)):      # edge cross plane?
        #    continue
        
        i = intersect_line_plane(co0, co1, pt, no)
        d = (co_from - i).length
        if d > d_max: d_max,edge_max,i_max = d,edge,i
    return (edge_max,i_max)

def find_sorted_bmedges_crossing_plane(pt, no, edges, epsilon, e_ind_from, co_from):
    '''
    pt - point on cutting plane: mathutils.Vector
    no - normal of cutting plane: mathutils.Vector
    edges - edges of BMeshFace
    epsilon - error for coplanar verts: Float
    e_ind_from - index of the previous bmesh edge the walker just crossed
    co_from  - location where the cutting plane crosses the lats BMEdge (e_ind_from)
    #e_exclude - a dictionary of edges previulsy crossed. dictionary should return order in which edges were crossed.
    
    returns a list of bmedges that *cross* plane and corresponding intersection points
    
    If BMFace happens to be a convex NGon with > 2 crosses, the list will be sorted such that the 0th item is the only
    valid intersection which makes an edge in teh cross section with e_ind_from.
    
    '''
    if(len(edges)<=4):
        # shortcut (no need to find multiple... just find first)
        for edge in edges:
            if edge.index == e_ind_from: continue
            v0,v1 = edge.verts
            co0,co1 = v0.co,v1.co
            s0,s1 = no.dot(co0 - pt), no.dot(co1 - pt)
            no_cross = not ((s0>epsilon and s1<-epsilon) or (s0<-epsilon and s1>epsilon))
            if no_cross: continue
            i = intersect_line_plane(co0, co1, pt, no)
            return [(edge,i)]

    #http://stackoverflow.com/questions/6618515/sorting-list-based-on-values-from-another-list
    i_edges = []
    intersects = []
    ds = [] 
    coords = {} #cache these to prevent twice per vert calcing
    for edge in edges:
        v0,v1 = edge.verts
        if v0 not in coords: coords[v0] = no.dot(v0.co-pt)
        if v1 not in coords: coords[v1] = no.dot(v1.co-pt)
        
    for edge in edges:
        #if edge.index == e_ind_from: continue  #<--we do need the e_ind_from edge because it helps us sort
        #if edge.index in e_ind_exclude: continue  #<-maybe don't need this because of the ordering :-)
        v0,v1 = edge.verts
        s0,s1 = coords[v0],coords[v1]
        if s0 > epsilon and s1 > epsilon: continue
        if s0 < -epsilon and s1 < -epsilon: continue
        #if not ((s0>epsilon and s1<-epsilon) or (s0<-epsilon and s1>epsilon)):      # edge cross plane?
        #    continue
        
        i = intersect_line_plane(v0.co, v1.co, pt, no)
        d = (i - co_from).length
        
        i_edges += [edge]
        intersects += [i]
        ds += [d]
        
    
    if len(i_edges) == 2:
        ed = [e for e in i_edges if e.index != e_ind_from][0]
        return [(ed, intersects[i_edges.index(ed)])]
    
    elif len(i_edges) > 2:  #a concave ngon with 4,6,8.. crossings
        print('there are %i crossings' % len(i_edges))
        #all the crossings are colinear if ngon is planar, so sorting them is easy
        edge_from = [e for e in i_edges if e.index == e_ind_from][0]
        min_i = intersects[i_edges.index(edge_from)]
        
        max_i = intersects[ds.index(max(ds))]
        direction = (max_i - min_i).normalized()
        
        signed_ds = []
        for j, ed in enumerate(i_edges):
            signed_ds += [(intersects[j] - min_i).dot(direction)]
            
        #[x for (y,x) in sorted(zip(Y,X))]  X sorted by Y
        sorted_edges = [ed for (d,ed) in sorted(zip(signed_ds,i_edges))]
        sorted_is = [i for (d,i) in sorted(zip(signed_ds, intersects))]
        n = sorted_edges.index(edge_from)
        
        if n % 2 == 0:
            print('odd crossings, this is the problem or a bad face')
            sorted_edges = list(reversed(list_shift(sorted_edges, n + 2)))
            sorted_is = list(reversed(list_shift(sorted_is, n + 2)))
        
        else:
            sorted_edges = list_shift(sorted_edges, n - 1)
            sorted_is =list_shift(sorted_is, n - 1)
        print('came from this edge ' + str(e_ind_from))
        print('leaving to this edge' + str(sorted_edges[0].index))
        return list(zip(sorted_edges, sorted_is))
    
    else:
        print('no crossings perhaps')
        print([e.index for e in edges])
        print(pt)
        print(no)
        return []
    
def cross_section_walker_endpoints(bme, pt, no, f_ind_from, e_ind_from, co_from, f_ind_to, co_to, epsilon, limit_set = None, max_iters = 10000):
    '''
    bme -  bmesh
    pt  - a point on cutting plane: mathutils.Vector
    no  - the normal of the cutting plane: mathutils.Vector
    f_ind_from - index of face which we are walking from: Int
    e_ind_from - index of the edge which we are stepping over: Int
    co_from - location of intersectino of e_ind_from edge and cutting plane:  mathutils.Vector
    f_end_to - index of face which we are walking toward
    co_to  - location of end point, not necessarily and edge intersection, often a racy_cast result in middle of a face
    
    returns tuple (verts,ed_inds, looped, found) by walking around a bmesh near the given plane
    verts: List of intersections of edges and cutting plane (in order) mathutils.Vector  co_2 is excluded
    eds crossed:  lost of the edges which were intersected(in orter)  Int.  
    looped is bool indicating if walk wrapped around bmesh, only true if did not find other face
    found is a bool indicating if the walk was able to find face f_ind_to  at point co_to
    '''
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.faces.ensure_lookup_table()
    
    # returned values
    verts = [co_from]
    eds_crossed = [bme.edges[e_ind_from]]
    #faces_crossed = [bme.faces[f_ind_from]]  #don't record first face because we did not cross it?
    faces_crossed = []
    looped = False
    found = False
    error = None
    
    #verify that the points are coplanar to the cut plane
    d0 = distance_point_to_plane(co_from, pt, no)
    df = distance_point_to_plane(co_to, pt, no)
    
    if d0 > epsilon or df > epsilon:
        print('not coplanar by epsilons standdards')
        print((d0, df, epsilon))
        return ([co_from, co_to],[], [],False, False, 'EPSILON')
    
    # track what faces we've seen
    f_inds_dict = {f_ind_from: 0}
    #track what edges we've seen  (more important with Ngons, we may traverse a face multiple times)
    e_inds_dict = {e_ind_from: 0}
    
    # get blender version
    bver = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])
    if bver > '002.072.000':
        bme.edges.ensure_lookup_table();

    f_cur = next(f for f in bme.edges[e_ind_from].link_faces if f.index != f_ind_from) #There is occasionally error here
    find_current = f_cur.index
    faces_crossed += [f_cur]
    
    #find the edges we might cross at the end, make sure where we are headed is valid
    #co_end will be bweteen edges 0,1  2,3  3,4 even if f_end is a concve ngon sith 4,6,8... intersections
    valid_end = False
    f_end = bme.faces[f_ind_to]
    eds_is = find_bmedges_crossing_plane(pt, no, f_end.edges, epsilon)
    for i in range(0,int(len(eds_is)/2)):
        p0 = eds_is[2*i][1]
        p1 = eds_is[2*i + 1][1]
        
        line_loc, line_pct = intersect_point_line(co_to, p0, p1)
        if line_pct >= 0 and line_pct <= 1: #we have found the 2 edges which co_to lies between!
            end_edges_dict = {eds_is[2*i][0].index: 0}
            end_edges_dict[eds_is[2*i+1][0].index] = 1
            valid_end = True
    
    if not valid_end:
        print('co_to is not close to f_ind_to or not between 2 edge intersections of f_to and cut plane')
        return ([co_from, co_to],[], [], False, False, 'END_POINT')
    
    
    while True:
        # find edges in the face that cross the plane
        cross_eds = find_sorted_bmedges_crossing_plane(pt, no, f_cur.edges, epsilon, e_ind_from, co_from)
        edge, i = cross_eds[0]
        verts += [i]
        eds_crossed += [edge]
        
        if len(edge.link_faces) == 1: 
            error = 'NON_MANIFOLD'
            break  #end of non manifold mesh
        
        if edge.index in end_edges_dict:  #we found an edge in the ending face.
            #print('found an edge in the ending face')
            #verts += [co_to]  #tack on the final point?
            found = True
            error = None
            break
        
        # get next face, edge, co
        f_next = next(f for f in edge.link_faces if f.index != find_current)
        
        if f_next == f_end:
            print('we found the last face without end_edge_dict catching it')
        faces_crossed += [f_next]
        find_next = f_next.index
        eind_next = edge.index
        co_next   = i
        
        if find_next in f_inds_dict:   #we might have looped, ngons can be crossed multiple times
            print('we have seen the next face before')
            if len(bme.faces[find_next].edges) <= 4: #can only cross a quad or tri onces
                print('quad or tri, we have looped to where we started')
                looped = True
                if f_inds_dict[find_next] != 0:
                    # loop is P-shaped (loop with a tail)
                    print('p shaped loop len %i, clipping tail %i' % (len(verts), f_inds_dict[find_next]))
                    verts = verts[f_inds_dict[find_next]:]      # clip off tail
                    faces_crossed = faces_crossed[f_inds_dict[find_next]:]
                    eds_crossed = eds_crossed[f_inds_dict[find_next]:]
                    
                    error = 'P_LOOP'
                    
                    print('do we need to do more clipping')
                    print(len(verts))
                    print(len(faces_crossed))
                    print(len(eds_crossed))
                    break
            
            elif len(bme.faces[find_next].edges) > 4 and f_inds_dict[find_next] == 0:
                print('more than 4 edges, and the first face we started with')
                next_crosses = find_sorted_bmedges_crossing_plane(pt, no, f_next.edges, epsilon, eind_next, co_next)
                if all(e.index in e_inds_dict for e, i in next_crosses[1:]):  #all the other edges of the face have been seen, we have looped
                    print('looped, all the other edges in the ngon has been tested, and it was the first ngon we tested')
                    looped = True
                    error = 'NGON_SPECIAL'
                    break
            
            elif eind_next in e_inds_dict:
                print('looped when found an already crossed edge')
                looped = True
                verts.pop()
                error = 'NGON_SPECIAL'
                break
        
        elif limit_set and f_next not in limit_set:
            error = 'LIMIT_SET'
            break
            
        else:
            # leave breadcrumb if find_next not in the dict, we may cross the face mutliple
            #times so we don't want to add it repeatedly
            f_inds_dict[find_next] = len(f_inds_dict)
        

        #always record the tested edges, allows us to find out if we have looped on an arm
        #of an extruded E shaped NGon
        e_inds_dict[eind_next] = len(e_inds_dict)
        
        f_ind_from = find_current
        e_ind_from = eind_next
        co_from   = co_next
        f_cur = f_next
        find_current = find_next
    
    return (verts,eds_crossed, faces_crossed, looped, found, error)

def cross_section_walker_dynamic_endpoints(bme, f_ind_from, e_ind_from, co_from, f_ind_to, co_to, epsilon, limit_set = None, max_iters = 10000):
    '''
    bme -  bmesh
    f_ind_from - index of face which we are walking from: Int
    e_ind_from - index of the edge which we are stepping over: Int
    co_from - location of intersectino of e_ind_from edge and cutting plane:  mathutils.Vector
    f_ind_to - index of face which we are walking toward
    co_to  - location of end point, not necessarily and edge intersection, often a racy_cast result in middle of a face
    epsilon
    limit_set = None, or set(BMFaces).  Used to stop walking if new faces found are not in the limit set
    max_iters - Integer, number of steps used to prevent exscessive infinite loops
    
    returns tuple (verts,ed_inds, looped, found) by walking around a bmesh near the given plane
    verts: List of intersections of edges and cutting plane (in order) mathutils.Vector  co_2 is excluded
    eds crossed:  lost of the edges which were intersected(in orter)  Int.  
    looped is bool indicating if walk wrapped around bmesh, only true if did not find other face
    found is a bool indicating if the walk was able to find face f_ind_to  at point co_to
    '''
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.faces.ensure_lookup_table()
    
    vec = co_to - co_from
    vec.normalize()
    # returned values
    verts = [co_from]
    eds_crossed = [bme.edges[e_ind_from]]
    #faces_crossed = [bme.faces[f_ind_from]] #we do not want to use the seed face in this dict, we didn't "cross" that face
    
    faces_crossed  = []
    looped = False
    found = False
    
    # track what faces we've seen, and in what order we saw them
    f_inds_dict = {f_ind_from: 0}
    #track what edges we've seen  (more important with Ngons, we may traverse a face multiple times)
    e_inds_dict = {e_ind_from: 0}
    
    # get blender version
    bver = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])
    if bver > '002.072.000':
        bme.edges.ensure_lookup_table();

    if len(bme.edges[e_ind_from].link_faces) != 2:
        print('no manifold edge in this direction')
        return ([co_from, co_to],[],[], False, False, 'NON_MANIFOLD')
        return
        
        
    f_cur = next(f for f in bme.edges[e_ind_from].link_faces if f.index != f_ind_from)
    find_current = f_cur.index
    faces_crossed += [f_cur]
    
    #find the edges we might cross at the end, make sure where we are headed is valid
    #co_end will be bweteen edges 0,1  2,3  3,4 even if f_end is a concve ngon sith 4,6,8... intersections
    f_end = bme.faces[f_ind_to]
    eds_is = find_bmedges_crossing_plane(co_to, f_end.normal.cross(vec), f_end.edges, epsilon)
    valid_end = False
    for i in range(0,int(len(eds_is)/2)):
        p0 = eds_is[2*i][1]
        p1 = eds_is[2*i + 1][1]
        
        line_loc, line_pct = intersect_point_line(co_to, p0, p1)
        if line_pct >= 0 and line_pct <= 1: #we have found the 2 edges which co_to lies between!
            end_edges_dict = {eds_is[2*i][0].index: 0}
            end_edges_dict[eds_is[2*i+1][0].index] = 1
            valid_end = True
    
    if not valid_end:
        print('co_to is not close to f_ind_to or not between 2 edge intersections of f_to and cut plane')
        return ([co_from, co_to],[],[], False, False, 'BAD TARGET')
    
    
    while True:
        face_no = f_cur.normal
        if face_no.dot(vec) > .999:
            print('parallel face normal to direction we are traveling')
            #if plane no happens to be parallel to the line connecting
            #the 2 poitns, then use the previous edge to define a cut
            #plane
            ed = eds_crossed[-1]
            ed_v = ed.verts[0].co - ed.verts[1].co
            ed_v.normalize()
            z = ed_v.cross(vec)
            no = vec.cross(z)
        else:
            no = face_no.cross(vec)  #keeps us always cutting on the axis between the 2 end points
            
        
        # find edges in the face that cross the plane
        cross_eds = find_sorted_bmedges_crossing_plane(verts[-1], no, f_cur.edges, epsilon, e_ind_from, co_from)
        
        if not len(cross_eds):
            return verts,eds_crossed, faces_crossed, False, False, 'STOP_MID'
            
        edge, i = cross_eds[0]
        verts += [i]
        eds_crossed += [edge]
        
        if len(edge.link_faces) == 1: 
            print('end of non manifold mesh!')
            error = 'NON_MANIFOLD'
            break  #end of non manifold mesh
        
        if edge.index in end_edges_dict:  #we found an edge in the ending face.
            #print('found an edge in the ending face')
            #verts += [co_to]  #tack on the final point?
            error = None
            found = True
            break
        
        # get next face, edge, co
        f_next = next(f for f in edge.link_faces if f.index != find_current)
        
        if f_next == f_end:
            
            print('you somehow found f_end without end_edges_dict catching it')
            error = None
            found = True
            break
        
        
        #we tested to see if we met up with the final face 
        faces_crossed += [f_next]
        find_next = f_next.index
        eind_next = edge.index
        co_next   = i
        
        vec = co_to - i
        vec.normalize()
        if find_next in f_inds_dict:   #we might have looped, ngons can be crossed multiple times
            if len(bme.faces[find_next].edges) <= 4: #can only cross a quad or tri onces
                looped = True
                if f_inds_dict[find_next] != 0:
                    # loop is P-shaped (loop with a tail)
                    print('p shaped loop len %i, clipping tail %i' % (len(verts), f_inds_dict[find_next]))
                    verts = verts[f_inds_dict[find_next]:]      # clip off tail
                    faces_crossed = faces_crossed[f_inds_dict[find_next]:]
                    eds_crossed = eds_crossed[f_inds_dict[find_next]:]
                    error = 'P_LOOP'
                    
                    print('do we need to do more clipping')
                    print(len(verts))
                    print(len(faces_crossed))
                    print(len(eds_crossed))
                    
                    break
            
            elif len(bme.faces[find_next].edges) > 4 and f_inds_dict[find_next] == 0:
                print('more than 4 edges, and the first face we started with')
                next_crosses = find_sorted_bmedges_crossing_plane(verts[-1], no, f_next.edges, epsilon, eind_next, co_next)
                if all(e.index in e_inds_dict for e, i in next_crosses[1:]):  #all the other edges of the face have been seen, we have looped
                    print('looped, all the other edges in the ngon has been tested, and it was the first ngon we tested')
                    looped = True
                    error = 'NGON_SPECIAL'
                    break
            
            elif eind_next in e_inds_dict:
                print('looped when found an already crossed edge')
                looped = True
                error = 'EDGE_SPECIAL'
                verts.pop()
                break
        
        elif limit_set and f_next not in limit_set:
            
            if len(verts) > 3:
                print('ran out of the limiting face set boundaries but went a long way first')
                print(len(verts))
            error = 'LIMIT_SET'
            break
        else:
            # leave breadcrumb if find_next not in the dict, we may cross the face mutliple
            #times so we don't want to add it repeatedly
            f_inds_dict[find_next] = len(f_inds_dict)
        

        #always record the tested edges, allows us to find out if we have looped on an arm
        #of an extruded E shaped NGon
        e_inds_dict[eind_next] = len(e_inds_dict)
        
        f_ind_from = find_current
        e_ind_from = eind_next
        co_from   = co_next
        f_cur = f_next
        find_current = find_next
    
    return (verts,eds_crossed, faces_crossed, looped, found, error)

def path_between_2_points(bme, bvh, pt_a, pt_b, 
                          max_tests = 10000, debug = True, 
                          prev_face = None, use_limit = True):
    '''
    Takes a bmesh and associated 
    world matrix of the object 
    
    returns list of locations and edges
        
    Args:
        bme: Blender BMesh
        bvh:  BVH from Bmesh.  mathutils.bvhtree.BVHTree
        
        mx:   World matrix (type Mathutils.Matrix)
        pt_A: any point close to the  bmesh surface
        pt_b:  any point close to the bmesh surface
        
    '''
    # max distance a coplanar vertex can be from plane
    epsilon = 0.00001
    
    
    times = [time.time()]

    #snap and find nearest pt and face in local coords
    if bversion() < "002.077.000":
        loc_a, no_a, ind_a, d_a = bvh.find(pt_a)
        loc_b, no_b, ind_b, d_b = bvh.find(pt_b)
    
    else:
        loc_a, no_a, ind_a, d_a = bvh.find_nearest(pt_a)
        loc_b, no_b, ind_b, d_b = bvh.find_nearest(pt_b)
    
    
    if prev_face and (prev_face.index == ind_a or prev_face.index == ind_b):
        print('dumb rule!')
        prev_face = None
        
    if use_limit:
        #grow selection from A to B and from B to A this way we get good connectivity
        faces_a = grow_selection_to_find_face(bme, bme.faces[ind_a], bme.faces[ind_b])
        faces_b = grow_selection_to_find_face(bme, bme.faces[ind_b], bme.faces[ind_a])
        faces_set = faces_a & faces_b
        times.append(time.time())
        step = times[-1] - times[-2]
        #print('did connectivity growing in %f' % step) 
    else:
        faces_set = None
    


    verts = {}
    
    
    vec = loc_b - loc_a
    loc_tip = loc_a
    loc_tail = loc_b
    cut_no_a = no_a.cross(vec)
    cut_no_b = no_b.cross(vec)
    
    # find intersections of edges and cutting plane
    bmface = bme.faces[ind_a]
    bmedges = bmface.edges
    ei_init = find_bmedges_crossing_plane(loc_a, cut_no_a, bmedges, epsilon)
    
    if len(ei_init) < 2:
        print('warning: it should not reach here! len(ei_init) = %d' % len(ei_init))
        print('lengths = ' + str([(edge.verts[0].co-edge.verts[1].co).length for edge in bmedges]))
        return ([],[],[], False, 'NO_INTITIAL_CROSSES')
    elif len(ei_init) == 2:
        # simple case
        ei0_max, ei1_max = ei_init
    else:
        #complex case, no difference except we need to pull out the first 2
        ei0_max, ei1_max = ei_init[0], ei_init[1]
        
    # start walking one way around bmesh
    if (prev_face and prev_face not in ei0_max[0].link_faces) or not prev_face:
        verts0, crossed_eds0, crossed_faces0, looped0, found0, error0 = cross_section_walker_dynamic_endpoints(bme, ind_a, ei0_max[0].index, ei0_max[1], ind_b, loc_b, epsilon, limit_set = faces_set)
    else:
        print('prev face prevented walking in the Verts0 direction')
        verts0, crossed_eds0, crossed_faces0, looped0, found0, error0 = [], [], [], False, False, 'PREV_FACE'
        
    if (prev_face and prev_face not in ei1_max[0].link_faces) or not prev_face:
        verts1, crossed_eds1, crossed_faces1, looped1, found1, error1 = cross_section_walker_dynamic_endpoints(bme, ind_a, ei1_max[0].index, ei1_max[1], ind_b, loc_b, epsilon, limit_set = faces_set)
    else:
        print('prev face prevented walking in the Verts1 direction')
        verts1, crossed_eds1, crossed_faces1, looped1, found1, error1 = [], [], [], False, False, 'PREV_FACE'
        
    if found0 and found1:
        print('Found target both directions')
        print('Len of path0:   %i' % len(verts0))
        print('Len of path1:   %i' % len(verts1))
        #great!  return the shortest path (TODO  shortest by path length)
        if len(verts0) < len(verts1):
            nv = len(verts0)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts0, edges, crossed_eds0, crossed_faces0, 'BOTH_DIR')
        else:
            nv = len(verts1)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts1, edges, crossed_eds1, crossed_faces1, 'BOTH_DIR')
            
    elif found0 and not found1:
        #print('found other face only one direction verts0')
        nv = len(verts0)
        edges = [(i,i+1) for i in range(nv-1)]
        return (verts0, edges, crossed_eds0, crossed_faces0, None)
    
    
    elif found1 and not found0:
        #print('found other face only one direction verts1')
        nv = len(verts1)
        edges = [(i,i+1) for i in range(nv-1)]
        return (verts1, edges, crossed_eds1, crossed_faces1, None)
    
    else:
        if len(verts0) and error0 == 'P_LOOP':
            'P_LOOP usualy means poorly behaved mesh'
            nv = len(verts0)
            edges = [(i,i+1) for i in range(nv-1)]
            return ([], [], [], [], 'P_LOOP')
        
        elif len(verts1) and error1 == 'P_LOOP':
            'P_LOOP usualy means poorly behaved mesh'
            nv = len(verts1)
            edges = [(i,i+1) for i in range(nv-1)]
            return ([], [], [], [], 'P_LOOP')
        
        elif len(verts0) and len(verts1) and (error0 == 'LIMIT_SET' and error1 == 'LIMIT_SET'):
            if len(verts0) >= len(verts1):
                nv = len(verts0)
                edges = [(i,i+1) for i in range(nv-1)]
                return (verts0, edges, crossed_eds0, crossed_faces0, 'LIMIT_SET')
            else:
                nv = len(verts1)
                edges = [(i,i+1) for i in range(nv-1)]
                return (verts1, edges, crossed_eds1, crossed_faces1, 'LIMIT_SET')
        
        if error0 == 'EPSILON' or error1 == 'EPSILON':
            error = 'EPSILON'
        else:
            error = 'TOTAL'
            
        print('unable to walk at all')
        print('Error 0: ' + error0)
        print('Error 1: ' + error1)
        return([], [], [], [], error)
    


def path_between_2_points_clean(bme, loc_a, ind_a,
                                loc_b, ind_b,
                                max_tests = 10000, 
                                debug = True, 
                                prev_face = None, 
                                use_limit = True,
                                epsilon = 0.00001):
    '''
    Takes a bmesh and associated 
    world matrix of the object 
    
    returns list of locations and edges
        
    Args:
        bme: Blender BMesh
        bvh:  BVH from Bmesh.  mathutils.bvhtree.BVHTree
        
        mx:   World matrix (type Mathutils.Matrix)
        pt_A: any point close to the  bmesh surface
        pt_b:  any point close to the bmesh surface
        
    '''
    times = [time.time()]


    no_a = bme.faces[ind_a].normal
    no_b = bme.faces[ind_a].normal
    
    if prev_face and (prev_face.index == ind_a or prev_face.index == ind_b):
        print('dumb rule!')
        prev_face = None
        
    if use_limit:
        #grow selection from A to B and from B to A this way we get good connectivity
        faces_a = grow_selection_to_find_face(bme, bme.faces[ind_a], bme.faces[ind_b])
        faces_b = grow_selection_to_find_face(bme, bme.faces[ind_b], bme.faces[ind_a])
        faces_set = faces_a & faces_b
        times.append(time.time())
        step = times[-1] - times[-2]
        #print('did connectivity growing in %f' % step) 
    else:
        faces_set = None
    

    verts = {}
    
    vec = loc_b - loc_a
    loc_tip = loc_a
    loc_tail = loc_b
    cut_no_a = no_a.cross(vec)
    cut_no_b = no_b.cross(vec)
    
    # find intersections of edges and cutting plane
    bmface = bme.faces[ind_a]
    bmedges = bmface.edges
    ei_init = find_bmedges_crossing_plane(loc_a, cut_no_a, bmedges, epsilon)
    
    if len(ei_init) < 2:
        print('warning: it should not reach here! len(ei_init) = %d' % len(ei_init))
        print('lengths = ' + str([(edge.verts[0].co-edge.verts[1].co).length for edge in bmedges]))
        return ([],[],[], False, 'NO_INTITIAL_CROSSES')
    elif len(ei_init) == 2:
        # simple case
        ei0_max, ei1_max = ei_init
    else:
        #complex case, no difference except we need to pull out the first 2
        ei0_max, ei1_max = ei_init[0], ei_init[1]
        
    # start walking one way around bmesh
    if (prev_face and prev_face not in ei0_max[0].link_faces) or not prev_face:
        verts0, crossed_eds0, crossed_faces0, looped0, found0, error0 = cross_section_walker_dynamic_endpoints(bme, ind_a, ei0_max[0].index, ei0_max[1], ind_b, loc_b, epsilon, limit_set = faces_set)
    else:
        print('prev face prevented walking in the Verts0 direction')
        verts0, crossed_eds0, crossed_faces0, looped0, found0, error0 = [], [], [], False, False, 'PREV_FACE'
        
    if (prev_face and prev_face not in ei1_max[0].link_faces) or not prev_face:
        verts1, crossed_eds1, crossed_faces1, looped1, found1, error1 = cross_section_walker_dynamic_endpoints(bme, ind_a, ei1_max[0].index, ei1_max[1], ind_b, loc_b, epsilon, limit_set = faces_set)
    else:
        print('prev face prevented walking in the Verts1 direction')
        verts1, crossed_eds1, crossed_faces1, looped1, found1, error1 = [], [], [], False, False, 'PREV_FACE'
        
    if found0 and found1:
        print('Found target both directions')
        print('Len of path0:   %i' % len(verts0))
        print('Len of path1:   %i' % len(verts1))
        #great!  return the shortest path (TODO  shortest by path length)
        if len(verts0) < len(verts1):
            nv = len(verts0)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts0, edges, crossed_eds0, crossed_faces0, 'BOTH_DIR')
        else:
            nv = len(verts1)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts1, edges, crossed_eds1, crossed_faces1, 'BOTH_DIR')
            
    elif found0 and not found1:
        #print('found other face only one direction verts0')
        nv = len(verts0)
        edges = [(i,i+1) for i in range(nv-1)]
        return (verts0, edges, crossed_eds0, crossed_faces0, None)
    
    
    elif found1 and not found0:
        #print('found other face only one direction verts1')
        nv = len(verts1)
        edges = [(i,i+1) for i in range(nv-1)]
        return (verts1, edges, crossed_eds1, crossed_faces1, None)
    
    else:
        if len(verts0) and error0 == 'P_LOOP':
            'P_LOOP usualy means poorly behaved mesh'
            nv = len(verts0)
            edges = [(i,i+1) for i in range(nv-1)]
            return ([], [], [], [], 'P_LOOP')
        
        elif len(verts1) and error1 == 'P_LOOP':
            'P_LOOP usualy means poorly behaved mesh'
            nv = len(verts1)
            edges = [(i,i+1) for i in range(nv-1)]
            return ([], [], [], [], 'P_LOOP')
        
        elif len(verts0) and len(verts1) and (error0 == 'LIMIT_SET' and error1 == 'LIMIT_SET'):
            if len(verts0) >= len(verts1):
                nv = len(verts0)
                edges = [(i,i+1) for i in range(nv-1)]
                return (verts0, edges, crossed_eds0, crossed_faces0, 'LIMIT_SET')
            else:
                nv = len(verts1)
                edges = [(i,i+1) for i in range(nv-1)]
                return (verts1, edges, crossed_eds1, crossed_faces1, 'LIMIT_SET')
        
        if error0 == 'EPSILON' or error1 == 'EPSILON':
            error = 'EPSILON'
        else:
            error = 'TOTAL'
            
        print('unable to walk at all')
        print('Error 0: ' + error0)
        print('Error 1: ' + error1)
        return([], [], [], [], error)
    
    
    
def cross_section_2seeds_ver1(bme, point, normal, 
                       seed_index0, co_0,
                       seed_index1, co_1,
                       max_tests = 10000, 
                       debug = True, 
                       prev_face = None, 
                       epsilon = .0000001,
                       topo_limit = True):
    '''
    '''
    #convert plane defn (point and normal) into local coords
    #imx = mx.inverted()
    #pt  = imx * point
    #no  = (imx.to_3x3() * normal).normalized()
    no = normal
    pt = point
    # get blender version
    bver = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])

    if bver > '002.072.000':
        bme.faces.ensure_lookup_table();

    # make sure that plane crosses seed faces!
    lco0 = [v.co for v in bme.faces[seed_index0].verts]
    ld0 = [no.dot(co - pt) for co in lco0]
    
    if all(d > epsilon for d in ld0) or all(d < -epsilon for d in ld0):               # does face_0 cross plane?
        # shift pt so plane crosses face
        shift_dist = (min(ld0)+epsilon) if ld0[0] > epsilon else (max(ld0)-epsilon)
        pt += no * shift_dist
        print('>>> shifting for face 0')
        #print('>>> ' + str(ld0))
        #print('>>> ' + str(shift_dist))
        #print('>>> ' + str(no*shift_dist))
    #else:
    #    print('Face 0 crosses plane')
    
    lco1 = [v.co for v in bme.faces[seed_index1].verts]
    ld1 = [no.dot(co - pt) for co in lco1]

    if all(d > epsilon for d in ld1) or all(d < -epsilon for d in ld1):               # does face_1 cross plane?
        # shift pt so plane crosses face
        shift_dist = (min(ld1)+epsilon) if ld1[0] > epsilon else (max(ld1)-epsilon)
        pt += no * shift_dist
        print('>>> shifting for face 1')
        #print('>>> ' + str(ld1))
        #print('>>> ' + str(shift_dist))
        #print('>>> ' + str(no*shift_dist))
    #else:
    #    print('Face 1 crosses plane')
    
    start_face = bme.faces[seed_index0]
    stop_face = bme.faces[seed_index1]
    
    if topo_limit:
        #find selection between 2 faces to limit cutting
        flooded_sel0 = grow_selection_to_find_face(bme, start_face, stop_face, max_iters = 1000)
        flooded_sel1 = grow_selection_to_find_face(bme, stop_face, start_face, max_iters = 1000)
        flood_set = flooded_sel0 & flooded_sel1
    else:
        flood_set = None
    
    
    # find intersections of edges and cutting plane
    bmface = bme.faces[seed_index0]
    bmedges = bmface.edges
    ei_init = find_bmedges_crossing_plane(pt, no, bmedges, epsilon)
    
    if prev_face and (prev_face.index == seed_index0 or prev_face.index == seed_index1):
        print('dumb rule!')
        prev_face = None
    if len(ei_init) < 2:
        print('warning: it should not reach here! len(ei_init) = %d' % len(ei_init))
        print('lengths = ' + str([(edge.verts[0].co-edge.verts[1].co).length for edge in bmedges]))
        return ([],[],[], 'NO_INTITIAL_CROSSES')
    elif len(ei_init) == 2:
        # simple case
        ei0_max, ei1_max = ei_init
    else:
        #complex case, no difference except we need to pull out the first 2
        ei0_max, ei1_max = ei_init[0], ei_init[1]  #find_bmedges_crossing_plane returns closest pairs of edges to initial pt.
    
    # start walking one way around bmesh
    if (prev_face and prev_face not in ei0_max[0].link_faces) or not prev_face:
        verts0, crossed_eds0, crossed_faces0, looped0, found0, error0 = cross_section_walker_endpoints(bme, pt, no, 
                                                                               seed_index0, ei0_max[0].index, ei0_max[1], 
                                                                               seed_index1, co_1, epsilon,                                                                                limit_set=flood_set)
    else:
        print('prev face prevented walking in the Verts0 direction')
        verts0, crossed_eds0, crossed_faces0, looped0, found0, error0 = [], [], [], False, False, 'PREV_FACE'
        
    if (prev_face and prev_face not in ei1_max[0].link_faces) or not prev_face:
        verts1, crossed_eds1, crossed_faces1, looped1, found1, error1 = cross_section_walker_endpoints(bme, pt, no, 
                                                                               seed_index0, ei1_max[0].index, ei1_max[1], 
                                                                               seed_index1, co_1, epsilon, 
                                                                               limit_set=flood_set)
    else:
        print('prev face prevented walking in the Verts1 direction')
        verts1, crossed_eds1, crossed_faces1, looped1, found1, error1 = [], [], [], False, False, 'PREV_FACE'
        
    if found0 and found1:
        #print('Went both ways, awesome. Picking shortest path, Verts0 and Verts 1 have the following lengths')
        #print(len(verts0))
        #print(len(verts1))
        #great!  return the shortest path (TODO  shortest by path length)
        if len(verts0) < len(verts1):
            nv = len(verts0)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts0, edges, crossed_eds0, crossed_faces0, 'BOTH_DIR')
        else:
            nv = len(verts1)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts1, edges, crossed_eds1, crossed_faces1, 'BOTH_DIR')
            
    elif found0 and not found1:
        print('found other face only one direction verts0')
        nv = len(verts0)
        edges = [(i,i+1) for i in range(nv-1)]
        return (verts0, edges, crossed_eds0, crossed_faces0, None)
    
    
    elif found1 and not found0:
        print('found other face only one direction verts1')
        nv = len(verts1)
        edges = [(i,i+1) for i in range(nv-1)]
        return (verts1, edges, crossed_eds1, crossed_faces1, None)
    
    else:
        if len(verts0) and error0 == 'P_LOOP':
            nv = len(verts0)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts0, edges, crossed_eds0, crossed_faces0, 'P_LOOP')
        
        elif len(verts1) and error1 == 'P_LOOP':
            nv = len(verts1)
            edges = [(i,i+1) for i in range(nv-1)]
            return (verts1, edges, crossed_eds1, crossed_faces1, 'P_LOOP')
        
        elif len(verts0) and len(verts1) and (error0 == 'LIMIT_SET' and error0 == 'LIMIT_SET'):
            if len(verts0) >= len(verts1):
                nv = len(verts0)
                edges = [(i,i+1) for i in range(nv-1)]
                return (verts0, edges, crossed_eds0, crossed_faces0, 'LIMIT_SET')
            else:
                nv = len(verts1)
                edges = [(i,i+1) for i in range(nv-1)]
                return (verts1, edges, crossed_eds1, crossed_faces1, 'LIMIT_SET')
            

        if error0 == 'EPSILON' or error1 == 'EPSILON':
            error = 'EPSILON'
        else:
            error = 'TOTAL'
            
        print('unable to walk between faces')
        print('Error 0: ' + error0)
        print('Error 1: ' + error1)
        return([], [], [], [], error)
    

def cross_section_walker(bme, pt, no, find_from, eind_from, co_from, epsilon):
    '''
    returns tuple (verts,looped) by walking around a bmesh near the given plane
    verts is list of verts as the intersections of edges and cutting plane (in order)
    looped is bool indicating if walk wrapped around bmesh
    '''

    # returned values
    verts = [co_from]
    looped = False
    
    # track what we've seen
    finds_dict = {find_from: 0}

    # get blender version
    bver = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])

    if bver > '002.072.000':
        bme.edges.ensure_lookup_table();

    f_cur = next(f for f in bme.edges[eind_from].link_faces if f.index != find_from)
    find_current = f_cur.index
    
    while True:
        # find farthest point
        edge,i = find_distant_bmedge_crossing_plane(pt, no, f_cur.edges, epsilon, eind_from, co_from)
        verts += [i]
        if len(edge.link_faces) == 1: break                                     # hit end?
        
        # get next face, edge, co
        f_next = next(f for f in edge.link_faces if f.index != find_current)
        find_next = f_next.index
        eind_next = edge.index
        co_next   = i
        
        if find_next in finds_dict:                                             # looped
            looped = True
            if finds_dict[find_next] != 0:
                # loop is P-shaped (loop with a tail)
                verts = verts[finds_dict[find_next]:]      # clip off tail
            break
        
        # leave breadcrumb
        finds_dict[find_next] = len(finds_dict)
        
        find_from = find_current
        eind_from = eind_next
        co_from   = co_next
        
        f_cur = f_next
        find_current = find_next
    
    return (verts,looped)
    
