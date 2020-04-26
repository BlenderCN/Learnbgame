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
import bmesh
import math

# Blender imports
import bpy
from mathutils import Vector

# Addon imports
from .common import *


def generateLattice(vertDist:Vector, scale:Vector, offset:Vector=Vector((0, 0, 0)), visualize:bool=False):
    """ return lattice coordinate matrix surrounding object of size 'scale'

    Keyword arguments:
    vertDist  -- distance between lattice verts in 3D space
    scale     -- lattice scale in 3D space
    offset    -- offset lattice center from origin
    visualize -- draw lattice coordinates in 3D space

    """

    # shift offset to ensure lattice surrounds object
    offset = offset - vec_remainder(offset, vertDist)
    # calculate res of lattice
    res = Vector((scale.x / vertDist.x,
                  scale.y / vertDist.y,
                  scale.z / vertDist.z))
    # round up lattice res
    res = Vector(round_up(round(val), 2) for val in res)
    h_res = res / 2
    # populate coord matrix
    nx, ny, nz = int(res.x) + 2, int(res.y) + 2, int(res.z) + 2
    create_coord = lambda v: vec_mult(v - h_res, vertDist) + offset
    coordMatrix = [[[create_coord(Vector((x, y, z))) for z in range(nz)] for y in range(ny)] for x in range(nx)]

    if visualize:
        # create bmesh
        bme = bmesh.new()
        vertMatrix = np.zeros((len(coordMatrix), len(coordMatrix[0]), len(coordMatrix[0][0]))).tolist()
        # add vertex for each coordinate
        for x in range(len(coordMatrix)):
            for y in range(len(coordMatrix[0])):
                for z in range(len(coordMatrix[0][0])):
                    vertMatrix[x][y][z] = bme.verts.new(coordMatrix[x][y][z])
                    # create new edges from vert
                    if x != 0: bme.edges.new((vertMatrix[x][y][z], vertMatrix[x-1][y][z]))
                    if y != 0: bme.edges.new((vertMatrix[x][y][z], vertMatrix[x][y-1][z]))
                    if z != 0: bme.edges.new((vertMatrix[x][y][z], vertMatrix[x][y][z-1]))
        # draw bmesh verts in 3D space
        drawBMesh(bme)

    return coordMatrix
