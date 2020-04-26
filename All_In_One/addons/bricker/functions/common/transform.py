# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import math

# Blender imports
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
from bpy.types import Object

# Module imports
from .blender import *
from .maths import mathutils_mult
from .python_utils import confirmIter


def apply_transform(obj:Object, location:bool=True, rotation:bool=True, scale:bool=True):
    """ apply object transformation to mesh """
    loc, rot, scale = obj.matrix_world.decompose()
    obj.matrix_world = Matrix.Identity(4)
    m = obj.data
    s_mat_x = Matrix.Scale(scale.x, 4, Vector((1, 0, 0)))
    s_mat_y = Matrix.Scale(scale.y, 4, Vector((0, 1, 0)))
    s_mat_z = Matrix.Scale(scale.z, 4, Vector((0, 0, 1)))
    if scale:    m.transform(mathutils_mult(s_mat_x, s_mat_y, s_mat_z))
    else:        obj.scale = scale
    if rotation: m.transform(rot.to_matrix().to_4x4())
    else:        obj.rotation_euler = rot.to_euler()
    if location: m.transform(Matrix.Translation(loc))
    else:        obj.location = loc


def parent_clear(objs, apply_transform:bool=True):
    """ efficiently clear parent """
    # select(objs, active=True, only=True)
    # bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    objs = confirmIter(objs)
    if apply_transform:
        for obj in objs:
            last_mx = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = last_mx
    else:
        for obj in objs:
            obj.parent = None


def getBoundsBF(obj:Object):
    """ brute force method for obtaining object bounding box """
    # initialize min and max
    min = Vector((math.inf, math.inf, math.inf))
    max = Vector((-math.inf, -math.inf, -math.inf))
    # calculate min and max verts
    for v in obj.data.vertices:
        if v.co.x > max.x:
            max.x = v.co.x
        elif v.co.x < min.x:
            min.x = v.co.x
        if v.co.y > max.y:
            max.y = v.co.y
        elif v.co.y < min.y:
            min.y = v.co.y
        if v.co.z > max.z:
            max.z = v.co.z
        elif v.co.z < min.z:
            min.z = v.co.z
    # set up bounding box list of coord lists
    bound_box = [list(min),
                 [min.x, min.y, min.z],
                 [min.x, min.y, max.z],
                 [min.x, max.y, max.z],
                 [min.x, max.y, min.z],
                 [max.x, min.y, min.z],
                 [max.y, min.y, max.z],
                 list(max),
                 [max.x, max.y, min.z]]
    return bound_box


def bounds(obj:Object, local:bool=False, use_adaptive_domain:bool=True):
    """
    returns object details with the following subattribute Vectors:

    .max : maximum value of object
    .min : minimum value of object
    .mid : midpoint value of object
    .dist: distance min to max

    """

    local_coords = getBoundsBF(obj) if is_smoke(obj) and is_adaptive(obj) and not use_adaptive_domain else obj.bound_box[:]
    om = obj.matrix_world

    if not local:
        worldify = lambda p: mathutils_mult(om, Vector(p[:]))
        coords = [worldify(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])
    getMax = lambda i: max([co[i] for co in coords])
    getMin = lambda i: min([co[i] for co in coords])

    info = lambda: None
    info.max = Vector((getMax(0), getMax(1), getMax(2)))
    info.min = Vector((getMin(0), getMin(1), getMin(2)))
    info.mid = (info.min + info.max) / 2
    info.dist = info.max - info.min

    return info


def setObjOrigin(obj:Object, loc:Vector):
    """ set object origin """
    l, r, s = obj.matrix_world.decompose()
    r_mat = r.to_matrix().to_4x4()
    s_mat_x = Matrix.Scale(s.x, 4, Vector((1, 0, 0)))
    s_mat_y = Matrix.Scale(s.y, 4, Vector((0, 1, 0)))
    s_mat_z = Matrix.Scale(s.z, 4, Vector((0, 0, 1)))
    s_mat = mathutils_mult(s_mat_x, s_mat_y, s_mat_z)
    mx = mathutils_mult((obj.matrix_world.translation-loc), r_mat, s_mat.inverted())
    obj.data.transform(Matrix.Translation(mx))
    obj.matrix_world.translation = loc


def transformToWorld(vec:Vector, mat:Matrix, junk_bme:bmesh=None):
    """ transfrom vector to world space from 'mat' matrix local space """
    # decompose matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    scale = mat.to_scale()[0]
    # apply rotation
    if rot != Euler((0, 0, 0), "XYZ"):
        junk_bme = bmesh.new() if junk_bme is None else junk_bme
        v1 = junk_bme.verts.new(vec)
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.x, 3, 'X'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.y, 3, 'Y'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.z, 3, 'Z'))
        vec = v1.co
    # apply scale
    vec = vec * scale
    # apply translation
    vec += loc
    return vec


def transformToLocal(vec:Vector, mat:Matrix, junk_bme:bmesh=None):
    """ transfrom vector to local space of 'mat' matrix """
    # decompose matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    scale = mat.to_scale()[0]
    # apply scale
    vec = vec / scale
    # apply rotation
    if rot != Euler((0, 0, 0), "XYZ"):
        junk_bme = bmesh.new() if junk_bme is None else junk_bme
        v1 = junk_bme.verts.new(vec)
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.z, 3, 'Z'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.y, 3, 'Y'))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.x, 3, 'X'))
        vec = v1.co
    return vec
