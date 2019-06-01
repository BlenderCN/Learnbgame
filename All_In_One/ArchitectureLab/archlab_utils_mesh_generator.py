# ##### BEGIN MIT LICENSE BLOCK #####
# MIT License
# 
# Copyright (c) 2018 Insma Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ##### END MIT LICENSE BLOCK #####

# ----------------------------------------------------------
# Author: Maciej Klemarczyk (mklemarczyk)
# ----------------------------------------------------------

import bpy
from math import sin, cos, radians
from mathutils import Vector, Matrix
from .archlab_utils import *


# ------------------------------------------------------------------------------
# Creates circle filled with ngon mesh data.
# ------------------------------------------------------------------------------
def generate_circle_ngonfill_mesh_data(radius, vertices, trunc_val):
    deltaAngle = 360 / vertices
    myvertices = []
    myfaces = [list(range(vertices))]
    for t in range(vertices):
        v1 = rotate_point2d(radius, 0.0, t * deltaAngle)
        myvertices.append((v1[0], v1[1], 0.0))
    if trunc_val > 0.0:
        (myvertices, myfaces) = truncate_circle_mesh(myvertices, myfaces, trunc_val)
    return myvertices, [], myfaces

# ------------------------------------------------------------------------------
# Creates circle witout filling mesh data.
# ------------------------------------------------------------------------------
def generate_circle_nofill_mesh_data(radius, vertices):
    deltaAngle = 360 / vertices
    myvertices = []
    myedges = []
    for t in range(vertices):
        v1 = rotate_point2d(radius, 0.0, t * deltaAngle)
        myvertices.append((v1[0], v1[1], 0.0))
        myedges.append((t, ((t+1) % vertices)))
    return myvertices, myedges, []

# ------------------------------------------------------------------------------
# Creates circle filled with triangle fan mesh data.
# ------------------------------------------------------------------------------
def generate_circle_tfanfill_mesh_data(radius, vertices):
    deltaAngle = 360 / vertices
    myvertices = []
    myfaces = []
    myvertices.append((0.0, 0.0, 0.0))
    for t in range(vertices):
        v1 = rotate_point2d(radius, 0.0, t * deltaAngle)
        myvertices.append((v1[0], v1[1], 0.0))
        myfaces.append((0, t+1, ((t+1) % vertices) +1))
    return myvertices, [], myfaces

# ------------------------------------------------------------------------------
# Creates cube mesh data.
# ------------------------------------------------------------------------------
def generate_cube_mesh_data(width, height, depth):
    posx = width /2
    posy = depth /2
    posz = height /2
    myvertices = [(-posx, -posy, -posz), (posx, -posy, -posz),
                (-posx, posy, -posz), (posx, posy, -posz),
                (-posx, -posy, posz), (posx, -posy, posz),
                (-posx, posy, posz), (posx, posy, posz)]
    myfaces = [(0, 1, 3, 2),
                (0, 1, 5, 4),
                (0, 4, 6, 2),
                (1, 5, 7, 3),
                (2, 3, 7, 6),
                (4, 5, 7, 6)]
    return myvertices, [], myfaces

# ------------------------------------------------------------------------------
# Creates plane mesh data.
# ------------------------------------------------------------------------------
def generate_plane_mesh_data(width, height):
    posx = width /2
    posy = height /2
    myvertices = [(-posx, -posy, 0.0), (posx, -posy, 0.0),
                (-posx, posy, 0.0), (posx, posy, 0.0)]
    myfaces = [(0, 1, 3, 2)]
    return myvertices, [], myfaces

# ------------------------------------------------------------------------------
# Creates ico sphere mesh data.
# ------------------------------------------------------------------------------
def generate_sphere_ico_mesh_data(radius, subdivisions):
    myvertices = []
    myfaces = []
    segments = 5
    topv = range(1, segments + 1)
    botv = range(segments + 1, segments * 2 + 1)
    sDeltaAngle = 360 /segments
    p1 = (0.2764 * radius, 0.8506 * radius, 0.4472 * radius)
    p2 = (0.7236 * radius, 0.5257 * radius, -0.4472 * radius)
    myvertices.append((0.0000, 0.0000, radius))
    lastv = topv[-1]
    for ts in topv:
        v1 = rotate_point3d(p1, anglez=(ts * sDeltaAngle))
        myvertices.append(v1)
        myfaces.append((0, lastv, ts))
        myfaces.append((lastv, ts, ts + segments))
        lastv = ts
    lastv = botv[-1]
    for ts in botv:
        v1 = rotate_point3d(p2, anglez=(ts * sDeltaAngle))
        myvertices.append(v1)
        myfaces.append((lastv, ts, lastv - segments))
        myfaces.append((11, lastv, ts))
        lastv = ts
    myvertices.append((0.0000, 0.0000, -radius))
    for ts in range(1, subdivisions):
        (myvertices, myfaces) = subdivide_icosphere_mesh(myvertices, myfaces, radius)
    return myvertices, [], myfaces

# ------------------------------------------------------------------------------
# Creates uv sphere mesh data.
# ------------------------------------------------------------------------------
def generate_sphere_uv_mesh_data(radius, segments, rings):
    myvertices = []
    myfaces = []
    segv = range(segments)
    sDeltaAngle = 360 /segments
    rDeltaAngle = 180 /rings
    p = (0.0, 0.0, radius)
    lastr = 0
    for tr in range(rings +1):
        lastv = segv[-1]
        for ts in segv:
            p1 = rotate_point3d(p, anglex=(tr * rDeltaAngle), anglez=(ts * sDeltaAngle))
            myvertices.append(p1)
            if tr > 0:
                myfaces.append((
                    lastr * segments + lastv,
                    lastr * segments + ts,
                    tr * segments + ts,
                    tr * segments + lastv
                ))
                lastv = ts
        lastr = tr
    return myvertices, [], myfaces

# --------------------------------------------------------------------
# Creates mesh based on meshes library data
# size - vector defines size in 3 axes
# segments - amount of segments to create circular mesh
# --------------------------------------------------------------------
def generate_mesh_from_library(meshname, size=(1.0, 1.0, 1.0), segments=32):
    meshdata = load_mesh_data_from_library(meshname)
    if meshdata is not None:
        mlsize = meshdata['RealSize']
        mlvertices = meshdata['Vertices']
        myedges = meshdata['Edges']
        myfaces = meshdata['Faces']
        myvertices = []
        for mlv in mlvertices:
            myvertices.append((
                mlv[0] * size[0] / mlsize[0],
                mlv[1] * size[1] / mlsize[1],
                mlv[2] * size[2] / mlsize[2]
            ))
        if meshdata['ConstructMethod'] == 'SoR_D':
            myvertices, myedges, myfaces = generate_sord_mesh(myvertices, myedges, segments)
            return myvertices, myedges, myfaces
        if meshdata['ConstructMethod'] == 'SoR_C':
            return [], [], []
        if meshdata['ConstructMethod'] == 'Math':
            return [], [], []
        return myvertices, myedges, myfaces
    return None

# --------------------------------------------------------------------
# Creates Solid of Revolution mesh based on meshes library data
# sordvertices - mesh profile vertices
# sordedges - mesh profile edges
# segments - amount of segments to create circular mesh base
# --------------------------------------------------------------------
def generate_sord_profile_mesh(sordvertices, sordedges, segments):
    return sordvertices, sordedges, []

# --------------------------------------------------------------------
# Creates Solid of Revolution mesh based on meshes library data
# sordvertices - mesh profile vertices
# sordedges - mesh profile edges
# segments - amount of segments to create circular mesh base
# --------------------------------------------------------------------
def generate_sord_mesh(sordvertices, sordedges, segments, close_top=True, close_bottom=True):
    myvertices = []
    myedges = []
    myfaces = []
    segv = range(segments)
    segh = len(sordvertices)
    sDeltaAngle = 360 /segments
    for ts in segv:
        for tv in sordvertices:
            p1 = rotate_point3d(tv, anglez=(ts * sDeltaAngle))
            myvertices.append(p1)
    lasts = segv[-1]
    for ts in segv:
        for te in sordedges:
            myfaces.append((
                te[0] + (lasts * segh),
                te[1] + (lasts * segh),
                te[1] + (ts * segh),
                te[0] + (ts * segh),
            ))
        lasts = ts
    if close_top or close_bottom:
        ends = set()
        for te in sordedges:
            if te[0] not in ends:
                ends.add(te[0])
            else:
                ends.remove(te[0])
            if te[1] not in ends:
                ends.add(te[1])
            else:
                ends.remove(te[1])
        topv = ends.pop()
        bottomv = ends.pop()
        if myvertices[topv][2] < myvertices[bottomv][2]:
            (topv, bottomv) = (bottomv, topv)
        topf = []
        bottomf = []
        for ts in segv:
            topf.append(ts * segh + topv)
            bottomf.append(ts * segh + bottomv)
        if close_top:
            myfaces.append(topf)
        if close_bottom:
            myfaces.append(bottomf)
    return myvertices, myedges, myfaces
