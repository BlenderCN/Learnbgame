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

# Script copyright (C) Li Jun (AKA oyster @blenderartists.org, @blendercn.org)
# Contributors: Li Jun

# <pep8-80 compliant>

"""
This script exports LDraw DAT File format files from Blender. LDraw is an open
standard for LEGO CAD programs, which can be found on http://www.ldraw.org/

Usage:
Execute this script from the "File->Export" menu and choose a DAT file to
save.

Notes:
You can choose
whether export all objects or only selected objects
"""

import bpy

def rgb2legocolor(rgb):
    rgbCurrent=['%02X' % (i*255) for i in rgb]
    return '0x2%s' %(''.join(rgbCurrent))

def writeface(face):
    for v in face:
        pass

def faceToTriangles(face):
    triangles = []
    if len(face) == 4:
        triangles.append([face[0], face[1], face[2]])
        triangles.append([face[2], face[3], face[0]])
    else:
        triangles.append(face)

    return triangles


def faceValues(face, mesh, matrix):
    fv = []
    for verti in face.vertices:
        fv.append((matrix * mesh.vertices[verti].co)[:])
    return fv

def faceToLine(face):
    return " ".join([("%.6f %.6f %.6f" % v) for v in face] + ["\n"])

def write(filepath,
          onlyVisible=True,
          use_selection=False,
          ):

    # write the faces to a file
    file = open(filepath, "w")

    scene = bpy.context.scene

    if use_selection:
        objects = (ob for ob in scene.objects if ob.select)
    else:
        objects = (ob for ob in scene.objects)

    if onlyVisible:
        obj=(ob for ob in objects if ob.is_visible(scene))

    faces = []
    for obj in objects:#bpy.context.selected_objects:
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

                try:
##                    print('face.material_index=', face.material_index)
##                    print('me.materials', me.materials)

                    facecolor=me.materials[face.material_index].diffuse_color
##                    print('facecolor', facecolor)
                    facecolor=rgb2legocolor(facecolor)
                except:
                    #default Blender color
                    facecolor='0x2CCCCCC'

##                print ('facecolor=%s' % facecolor)
##
##                print('fv')
##                print(fv)
##                print(len(fv))
##                print(faceToLine(fv))

                file.write('%i %s %s' %(len(fv), facecolor, faceToLine(fv)))

            if is_tmp_mesh:
                bpy.data.meshes.remove(me)


    file.close()

if __name__=='__main__':
	filepath=r'e:\my_project\blender\io\lego\test.dat'
	write(filepath)
