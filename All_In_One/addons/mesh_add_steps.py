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

bl_info = {
    "name": "Add Steps",
    "author": "Dealga McArdle",
    "version": (0, 1, 0),
    "blender": (2, 7, 3),
    "location": "View3D > Add > Mesh > Steps",
    "description": "Add a steps to tilted quad",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"
}

import bpy
from bpy.props import *
from math import sin, cos, pi, atan2
from mathutils import Vector, Euler, geometry
import bmesh


def force_lookups(bm):
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()


def make_steps(operator, context):
    obj = context.edit_object
    me = obj.data

    bm = bmesh.from_edit_mesh(me)
    verts = bm.verts
    faces = bm.faces

    selected = [v for v in verts if v.select]
    if not len(selected) == 4:
        return

    face = [f for f in faces if f.select]
    if not len(face) == 1:
        return

    face = face[0]
    fn = face.normal
    if fn.x == fn.y == 0.0:
        print('face must be at an angle')
        return

    # get two lowest and highest
    indices = [v.index for v in face.verts]
    print(indices)

    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

    _v1 = verts[indices[0]].co
    _v2 = verts[indices[1]].co
    _v3 = verts[indices[2]].co
    _v4 = verts[indices[3]].co

    '''
    At first you don't know how _v(1..4) relate to a,b,c,d.
    All we do know is that _v(1..4) is a sequence of joined verts.
    either: |a,b,c,d| or |b,c,d,a| or |c,d,a,b| or |d,a,b,c|

    a ----- b  You investigate which vertices share a z coordinate
    |       |  (or within epsilon distance). If the face is at an angle
    |       |  (like a normal stairs..not an Escher drawing), 2 verts will
    |       |  share the upper z and the other two verts will share the lower z.
    d ----- c  Once you know which indices are up and down you can overlay that
               information and get the coordinates of (a, b) and (d, c). From
               this point planning the stairs is easy.
    '''

    def are_similar_z(vertices):
        EPSILON = 1.0e-5
        return (Vector((0, 0, vertices[0].z)) - Vector((0, 0, vertices[1].z))).length < EPSILON

    if are_similar_z([_v1, _v2]) and are_similar_z([_v3, _v4]):
        if _v1.z > _v3.z:
            a, b, c, d = _v1, _v2, _v3, _v4  # abcd
        else:
            a, b, c, d = _v3, _v4, _v1, _v2  # cdab
    elif are_similar_z([_v4, _v1]) and are_similar_z([_v2, _v3]):
        if _v1.z > _v2.z:
            a, b, c, d = _v4, _v1, _v2, _v3  # dabc
        else:
            a, b, c, d = _v2, _v3, _v4, _v1  # bcda

    try:
        m = [a, b, c, d]
        print('a,b,c,d are assigned!')
    except:
        print('a,b,c,d not assigned.. ')
        print(_v1, _v2, _v3, _v4)
        return

    ''' At this point we now know (a, b) are high, and (c, d) are low

          a --------- b   grow from dc to ab
         /           /|   up and over.
        /           / |
       /           /  |
      /           /   |
     /           /    |
    d --------- c - - +

    '''
    force_lookups(bm)  # this one might be overkill..

    step_size = 1.0 / operator.num_steps
    zstep_size = (a.z - d.z) / operator.num_steps
    z_up = Vector((0, 0, zstep_size))

    left_side = []
    right_side = []

    for i in range(operator.num_steps):
        ratio = i * step_size
        vco1 = d.lerp(a, ratio)
        vco2 = c.lerp(b, ratio)

        v1 = bm.verts.new(vco1)
        v2 = bm.verts.new(vco2)
        v1a = bm.verts.new(vco1 + z_up)
        v2a = bm.verts.new(vco2 + z_up)

        left_side.extend([v1, v1a])
        right_side.extend([v2, v2a])

    va = bm.verts.new(a)
    vb = bm.verts.new(b)
    left_side.append(va)
    right_side.append(vb)

    force_lookups(bm)

    for idx in range(0, len(left_side)-1, 2):

        # do triangles.
        __v0 = right_side[idx]
        __v1 = right_side[idx+1]
        __v2 = right_side[idx+2]
        bm.faces.new([__v0, __v1, __v2])

        __V0 = left_side[idx]
        __V1 = left_side[idx+2]
        __V2 = left_side[idx+1]
        bm.faces.new([__V0, __V1, __V2])

        # do quads
        bm.faces.new([__V0, __V2, __v1, __v0])  # front
        bm.faces.new([__V2, __V1, __v2, __v1])  # flat

    bm.normal_update()
    bmesh.update_edit_mesh(me, True)


class AddStepsMesh(bpy.types.Operator):

    bl_idname = "mesh.steps_add"
    bl_label = "Add Steps"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    num_steps = IntProperty(
        name="num profile verts",
        description="how many verts in profile shape",
        default=8, min=2, max=30)

    def execute(self, context):
        make_steps(self, context)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator("mesh.steps_add", icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
