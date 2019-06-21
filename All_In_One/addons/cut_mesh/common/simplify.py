'''
Created on Nov 10, 2018

@author: Patrick
'''

import math
from mathutils.geometry import intersect_point_line
from mathutils import Vector


def perp_vector_point_line(pt1, pt2, ptn):
    '''
    Vector bwettn pointn and line between point1
    and point2
    args:
        pt1, and pt1 are Vectors representing line segment
    
    return Vector
    
    pt1 ------------------- pt
            ^
            |
            |
            |<-----this vector
            |
            ptn
    '''
    pt_on_line = intersect_point_line(ptn.to_3d(), pt1.to_3d(), pt2.to_3d())[0]
    alt_vect = pt_on_line - ptn
    
    return alt_vect

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
    
# iterate through verts

def iterate_rdp(points, newVerts, error,method = 0):
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
            if method == 1:
                alti = perp_vector_point_line(points[newVerts[newIndex]], points[newVerts[newIndex+1]], point).length
            else:
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

def simplify_RDP(splineVerts, error, method = 0):
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
        new = iterate_rdp(splineVerts, newVerts, error, method = method)
        if new:
            newVerts += new
            newVerts.sort()
            
    return newVerts

def relax_vert_chain(verts, factor = .75, in_place = True):
    '''
    verts is a list of Vectors
    first and last vert will not be changes
    
    this should modify the list in place
    however I have it returning verts?
    '''
    
    L = len(verts)
    if L < 4:
        print('not enough verts to relax')
        return verts
    
    
    deltas = [Vector((0,0,0))] * L
    
    for i in range(1,L-1):
        
        d = .5 * (verts[i-1] + verts[i+1]) - verts[i]
        deltas[i] = factor * d
    
    if in_place:
        for i in range(1,L-1):
            verts[i] += deltas[i]
        
        return True
    else:
        new_verts = verts.copy()
        for i in range(1,L-1):
            new_verts[i] += deltas[i]     
        
        return new_verts
