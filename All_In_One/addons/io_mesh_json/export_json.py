# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

# <pep8-80 compliant>

"""
This script exports a Mesh to a JSON geometry format file.

The exported data is a JSON formatted array of polygons defined by a list of vertices.

Usage:
Execute this script from the "File->Export" menu.

"""

import bpy


def faceValues(face, mesh, matrix):
    fv = []
    for verti in face.vertices:
        fv.append((matrix * mesh.vertices[verti].co)[:])
    return fv

def faceToLine(face):
    return ", ".join([("[%.6f,%.6f,%.6f]" % v) for v in face])

def write(filepath):

    scene = bpy.context.scene

    faces = []
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            try:
                me = obj.to_mesh(scene, True, "PREVIEW")
            except:
                me = None
            is_tmp_mesh = True
        else:
            me = obj.data
            if not me.tessfaces and me.polygons:
                me.calc_tessface()
            is_tmp_mesh = False

        if me is not None:
            matrix = obj.matrix_world.copy()
            for face in me.tessfaces:
                fv = faceValues(face, me, matrix)
                faces.append(fv)

            if is_tmp_mesh:
                bpy.data.meshes.remove(me)

    # write the faces to a file
    file = open(filepath, "w")
    file.write('{\n    \"raw\":[\n')

    fl = []
    for face in faces:
        fl.append('[' + faceToLine(face) + ']\n')

    file.write(",".join(fl))

    file.write('    ]\n}\n')
    file.close()
