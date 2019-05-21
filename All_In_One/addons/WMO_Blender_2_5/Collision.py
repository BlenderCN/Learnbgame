

import mathutils
from mathutils import *

# return true if projections of 2 polygons are overlapping
def ProjOverlap(poly1_min, poly1_max, poly2_min, poly2_max):
    if(poly1_max < poly2_min):
        return False
    if(poly2_max < poly1_min):
        return False
    return True

# return min coordinate and max coordinate of a vertex list in a tuple
def GetMinMax(vertList):
    min = Vector(vertList[0])
    max = Vector(vertList[0])
    for v in vertList:
        if(v.x < min.x):
            min.x = v.x
        elif(v.x > max.x):
            max.x = v.x
        if(v.y < min.y):
            min.y = v.y
        elif(v.y > max.y):
            max.y = v.y
        if(v.z < min.z):
            min.z = v.z
        elif(v.z > max.z):
            max.z = v.z
    return (min, max)

# return projection of point with given direction vector
def ProjectPoint(pt, v):
    proj = Vector()
    # project on X
    if(v.y == 0):
        l = 0
    else:
        l = - pt.y / v.y
    proj.z = pt.x + l * v.x
    # project on Y
    if(v.z == 0):
        l = 0
    else:
        l = - pt.z / v.z
    proj.y = pt.x + l * v.x
    # project on Z
    proj.x = pt.y + l * v.y
    return proj

def PlaneBoxOverlap(normal, vert, box):
    vmin = Vector()
    vmax = Vector()
    for q in range(0, 3):
        v = vert[q]
        if(normal[q] > 0.0):
            vmin[q] = box[0][q] - v
            vmax[q] = box[1][q] - v
        else:
            vmin[q] = box[1][q] - v
            vmax[q] = box[0][q] - v
    if(normal.dot(vmin) > 0.0):
        return False
    if(normal.dot(vmax) >= 0.0):
        return True
    return False
"""
def ColTest():
    box_vertices = []
    for v in box_me.vertices:
        box_vertices.append(v.co)
    tri_vertices = []
    for v in tri_me.vertices:
        tri_vertices.append(v.co)
    bb = CalculateBoundingBox(None, box_vertices)
    print(CollideBoxTri(bb, tri_vertices))
    """
# return True if AABB and triangle overlap
def CollideBoxTri(box, triangle):
    triangleMinMax = GetMinMax(triangle)
    # check if overlap on box axis
    if(not ProjOverlap(box[0].x, box[1].x, triangleMinMax[0].x, triangleMinMax[1].x)):
       return False
    if(not ProjOverlap(box[0].y, box[1].y, triangleMinMax[0].y, triangleMinMax[1].y)):
       return False
    if(not ProjOverlap(box[0].z, box[1].z, triangleMinMax[0].z, triangleMinMax[1].z)):
       return False
    pt_box = []
    pt_box.append(Vector(box[0].xyz))
    pt_box.append(Vector((box[0].x, box[1].y, box[0].z)))
    pt_box.append(Vector((box[1].x, box[1].y, box[0].z)))
    pt_box.append(Vector((box[1].x, box[0].y, box[0].z)))
    pt_box.append(Vector(box[1].xyz))
    pt_box.append(Vector((box[0].x, box[1].y, box[1].z)))
    pt_box.append(Vector((box[1].x, box[1].y, box[1].z)))
    pt_box.append(Vector((box[1].x, box[0].y, box[1].z)))
    # project on edge 1 axis
    E0 = triangle[1] - triangle[0]
    pt_box_projected = []
    pt_triangle_projected = []
    for pt in pt_box:
        pt_box_projected.append(ProjectPoint(pt, E0))
    for pt in triangle:
        pt_triangle_projected.append(ProjectPoint(pt, E0))
    projected_box_MinMax = GetMinMax(pt_box_projected)
    projected_triangle_MinMax = GetMinMax(pt_triangle_projected)
    if(not ProjOverlap(projected_box_MinMax[0].x, projected_box_MinMax[1].x, projected_triangle_MinMax[0].x, projected_triangle_MinMax[1].x)):
       return False
    if(not ProjOverlap(projected_box_MinMax[0].y, projected_box_MinMax[1].y, projected_triangle_MinMax[0].y, projected_triangle_MinMax[1].y)):
       return False
    if(not ProjOverlap(projected_box_MinMax[0].z, projected_box_MinMax[1].z, projected_triangle_MinMax[0].z, projected_triangle_MinMax[1].z)):
       return False
    # project on edge 2 axis
    E1 = triangle[2] - triangle[1]
    pt_box_projected = []
    pt_triangle_projected = []
    for pt in pt_box:
        pt_box_projected.append(ProjectPoint(pt, E1))
    for pt in triangle:
        pt_triangle_projected.append(ProjectPoint(pt, E1))
    projected_box_MinMax = GetMinMax(pt_box_projected)
    projected_triangle_MinMax = GetMinMax(pt_triangle_projected)
    if(not ProjOverlap(projected_box_MinMax[0].x, projected_box_MinMax[1].x, projected_triangle_MinMax[0].x, projected_triangle_MinMax[1].x)):
       return False
    if(not ProjOverlap(projected_box_MinMax[0].y, projected_box_MinMax[1].y, projected_triangle_MinMax[0].y, projected_triangle_MinMax[1].y)):
       return False
    if(not ProjOverlap(projected_box_MinMax[0].z, projected_box_MinMax[1].z, projected_triangle_MinMax[0].z, projected_triangle_MinMax[1].z)):
       return False
   # project on edge 3 axis
    E2 = triangle[0] - triangle[2]
    pt_box_projected = []
    pt_triangle_projected = []
    for pt in pt_box:
        pt_box_projected.append(ProjectPoint(pt, E2))
    for pt in triangle:
        pt_triangle_projected.append(ProjectPoint(pt, E2))
    projected_box_MinMax = GetMinMax(pt_box_projected)
    projected_triangle_MinMax = GetMinMax(pt_triangle_projected)
    if(not ProjOverlap(projected_box_MinMax[0].x, projected_box_MinMax[1].x, projected_triangle_MinMax[0].x, projected_triangle_MinMax[1].x)):
       return False
    if(not ProjOverlap(projected_box_MinMax[0].y, projected_box_MinMax[1].y, projected_triangle_MinMax[0].y, projected_triangle_MinMax[1].y)):
       return False
    if(not ProjOverlap(projected_box_MinMax[0].z, projected_box_MinMax[1].z, projected_triangle_MinMax[0].z, projected_triangle_MinMax[1].z)):
       return False
    if(not PlaneBoxOverlap(E0.cross(E1), triangle[0], box)):
        return False
    return True



def CalculateBoundingBox(vertices):
    corner1 = Vector(vertices[0])
    corner2 = Vector(vertices[0])
    for v in vertices:
        if(v[0] < corner1[0]):
            corner1[0] = v[0]
        elif(v[0] > corner2[0]):
            corner2[0] = v[0]
        if(v[1] < corner1[1]):
            corner1[1] = v[1]
        elif(v[1] > corner2[1]):
            corner2[1] = v[1]
        if(v[2] < corner1[2]):
            corner1[2] = v[2]
        elif(v[2] > corner2[2]):
            corner2[2] = v[2]
    return (corner1, corner2)