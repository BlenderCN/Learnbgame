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
from .hyperpreset import ensure_scene_is_hyper
from .hypermeshpreferences import debug_message


class InsertHyperCubeOperator(bpy.types.Operator):
    bl_idname = "hyper.inserthypercube"
    bl_label = "Add hypercube"
    bl_options = {'REGISTER', 'UNDO'}

    radius = bpy.props.FloatProperty(name="Radius", default=1.0, subtype='DISTANCE')

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        debug_message("Adding hypercube")

        sc = bpy.context.scene
        ensure_scene_is_hyper(sc)

        me = bpy.data.meshes.new("Hypercube")
        me.hypersettings.hyper = True
        me["hypermesh-dirty"] = False
        me["hypermesh-justcleaned"] = True

        bm = bmesh.new()
        bm.from_mesh(me)
        layw = bm.verts.layers.float.new('hyperw')
        layx = bm.verts.layers.float.new('hyperx')
        layy = bm.verts.layers.float.new('hypery')
        layz = bm.verts.layers.float.new('hyperz')

        for i in range(16):
            v = bm.verts.new((0, 0, 0))
            v[layw] = self.radius * (((i & 0x01) << 1) - 1)
            v[layx] = self.radius * (((i & 0x02) << 0) - 1)
            v[layy] = self.radius * (((i & 0x04) >> 1) - 1)
            v[layz] = self.radius * (((i & 0x08) >> 2) - 1)

        bm.verts.ensure_lookup_table()

        bits = [0x01, 0x02, 0x04, 0x08]
        for i in range(16):
            for j in bits:
                k = i | j
                if k != i:
                    bm.edges.new((bm.verts[i], bm.verts[k]))

        for i in range(16):
            for j in range(4):
                for k in range(j+1, 4):
                    if (i & bits[j]) or (i & bits[k]):
                        continue
                    bm.faces.new((bm.verts[i], bm.verts[i | bits[j]],
                                  bm.verts[i | bits[j] | bits[k]],
                                  bm.verts[i | bits[k]]))

        bm.to_mesh(me)

        ob = bpy.data.objects.new("Hypercube", me)
        sc.objects.link(ob)
        sc.objects.active = ob
        ob.select = True

        # triggers a projection to 3D
        me.hypersettings.preset = sc.selectedpreset

        return {'FINISHED'}
