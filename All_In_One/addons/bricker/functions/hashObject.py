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

# Blender imports
import bpy
from mathutils import Vector


# from CG Cookie's retopoflow plugin
def hash_object(obj:bpy.types.Object):
    if obj is None:
        return None
    assert type(obj) is bpy.types.Object, "Only call hash_object on mesh objects!"
    assert type(obj.data) is bpy.types.Mesh, "Only call hash_object on mesh objects!"
    # get object data to act as a hash
    me = obj.data
    counts = (len(me.vertices), len(me.edges), len(me.polygons), len(obj.modifiers))
    if me.vertices:
        bbox = (tuple(min(v.co for v in me.vertices)), tuple(max(v.co for v in me.vertices)))
    else:
        bbox = (None, None)
    vsum   = tuple(sum((v.co for v in me.vertices), Vector((0, 0, 0))))
    xform  = tuple(e for l in obj.matrix_world for e in l)
    hashed = (counts, bbox, vsum, xform, hash(obj))  # ob.name???
    return hashed


# from CG Cookie's retopoflow plugin
def hash_bmesh(bme:bmesh.types.BMesh):
    if bme is None:
        return None
    assert type(bme) is bmesh.types.BMesh, 'Only call hash_bmesh on BMesh objects!'
    counts = (len(bme.verts), len(bme.edges), len(bme.faces))
    bbox   = BBox(from_bmverts=self.bme.verts)
    vsum   = tuple(sum((v.co for v in bme.verts), Vector((0, 0, 0))))
    hashed = (counts, tuple(bbox.min), tuple(bbox.max), vsum)
    return hashed
