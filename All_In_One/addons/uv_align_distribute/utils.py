# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
"""Utils function.

Most functions here will be deprecated"""

import math

import bmesh
import bpy
import mathutils

from . import geometry, global_def


def InitBMesh():
    """Init global bmesh."""
    global_def.bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
    global_def.bm.faces.ensure_lookup_table()
    # uvlayer = bm.loops.layers.uv.active

    global_def.uvlayer = global_def.bm.loops.layers.uv.verify()
    global_def.bm.faces.layers.tex.verify()


def update():
    """Update mesh rappresentation in blender."""
    bmesh.update_edit_mesh(bpy.context.edit_object.data, False, False)
    # bm.to_mesh(bpy.context.object.data)
    # bm.free()


def GBBox(islands):
    """Return the bounding box of all islands."""
    minX = minY = 1000
    maxX = maxY = -1000
    for _island in islands:
        for face_id in _island.faceList:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                u, v = loop[global_def.uvlayer].uv
                minX = min(u, minX)
                minY = min(v, minY)
                maxX = max(u, maxX)
                maxY = max(v, maxY)

    return rectangle.Rectangle(mathutils.Vector((minX, minY)),
                               mathutils.Vector((maxX, maxY)))


def vectorDistance(vector1, vector2):
    """Return the distance between vectors."""
    return math.sqrt(
        math.pow((vector2.x - vector1.x), 2) +
        math.pow((vector2.y - vector1.y), 2))


def _sortCenter(pointList):

    scambio = True
    n = len(pointList)
    while scambio:
        scambio = False
        for i in range(0, n-1):
            pointA = pointList[i][0]
            pointB = pointList[i+1][0]

            if (pointA.x <= pointB.x) and (pointA.y > pointB.y):
                pointList[i], pointList[i+1] = pointList[i+1], pointList[i]
                scambio = True

    return pointList


def _sortVertex(vertexList, BBCenter):

    anglesList = []
    for v in vertexList:
        # atan2(P[i].y - M.y, P[i].x - M.x)
        angle = math.atan2(v.uv.y - BBCenter.y, v.uv.x - BBCenter.x)
        anglesList.append((v, angle))

    vertsAngle = sorted(anglesList, key=lambda coords: coords[0].uv)
    # vertsAngle = sorted(anglesList, key=lambda angle: angle[1])
    newList = []
    for i in vertsAngle:
        newList.append(i[0])

    return newList


def getTargetPoint(context, islands):
    """Return the target of uv operations."""
    if context.scene.relativeItems == 'UV_SPACE':
        return mathutils.Vector((0.0, 0.0)), mathutils.Vector((1.0, 1.0))
    elif context.scene.relativeItems == 'ACTIVE':
        activeIsland = islands.activeIsland()
        if not activeIsland:
            return None
        else:
            return activeIsland.BBox()
    elif context.scene.relativeItems == 'CURSOR':
        value = bpy.context.space_data.uv_editor.show_normalized_coords
        bpy.context.space_data.uv_editor.show_normalized_coords = value or True
        coords = context.space_data.cursor_location
        bpy.context.space_data.uv_editor.show_normalized_coords = value
        return coords


# deprecated:
# def IslandSpatialSortX(islands):
#     spatialSort = []
#     for _island in islands:
#         spatialSort.append((island.BBox().center().x, island))
#     spatialSort.sort()
#     return spatialSort


# def IslandSpatialSortY(islands):
#     spatialSort = []
#     for _island in islands:
#         spatialSort.append((_island.BBox().center().y, island))
#     spatialSort.sort()
#     return spatialSort


# todo: to rework
def averageIslandDist(islands):
    """Return the average distance between islands."""
    distX = 0
    distY = 0
    counter = 0

    for i in range(len(islands)):
        elem1 = islands[i].BBox().bottomRight()
        try:            # island
            elem2 = islands[i + 1].BBox().topLeft()
            counter += 1
        except:
            break

        distX += elem2.x - elem1.x
        distY += elem2.y - elem1.y

    avgDistX = distX / counter
    avgDistY = distY / counter
    return mathutils.Vector((avgDistX, avgDistY))
