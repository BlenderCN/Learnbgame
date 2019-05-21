# This file is part of Hypermesh.
#
# Hypermesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hypermesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hypermesh.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
from .projections import map4to4
from mathutils import Vector
from .hypermeshpreferences import debug_message


def clean_mesh(me):
    debug_message("Cleaning mesh " + me.name)

    h = bpy.context.scene.hyperpresets[me.hypersettings.preset]
    if me.is_editmode:
        bm = bmesh.from_edit_mesh(me)
    else:
        bm = bmesh.new()
        bm.from_mesh(me)
    layw = bm.verts.layers.float['hyperw']
    layx = bm.verts.layers.float['hyperx']
    layy = bm.verts.layers.float['hypery']
    layz = bm.verts.layers.float['hyperz']
    for v in bm.verts:
        old = Vector([v[layw], v[layx], v[layy], v[layz]])
        newco = map4to4(h, v.co, old)
        v[layw] = newco[0]
        v[layx] = newco[1]
        v[layy] = newco[2]
        v[layz] = newco[3]
    if me.is_editmode:
        bmesh.update_edit_mesh(me)
    else:
        bm.to_mesh(me)


class UpdateHyperPositions(bpy.types.Operator):
    bl_idname = "hyper.update4"
    bl_label = "Update hypercoordinates"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        if context.active_object.type != 'MESH':
            return False
        me = context.active_object.data
        if not me.hypersettings.hyper:
            return False
        return True

    def execute(self, context):
        me = context.active_object.data
        clean_mesh(me)
        return {'FINISHED'}
