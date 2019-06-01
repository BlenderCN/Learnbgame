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
from mathutils import Vector
from math import pi, sin, cos
from .hypermeshpreferences import debug_message


class AddFlatTorusOperator(bpy.types.Operator):
    bl_idname = "hyper.addflattorus"
    bl_label = "Add flat torus"
    bl_options = {'REGISTER', 'UNDO'}

    orientation = bpy.props.EnumProperty(
            items=[("decompose_wx_yz", "(WX)x(YZ)", "Decompose as (WX)-plane times (YZ)-plane"),
                   ("decompose_wy_xz", "(WY)x(XZ)", "Decompose as (WY)-plane times (XZ)-plane"),
                   ("decompose_wz_xy", "(WZ)x(XY)", "Decompose as (WZ)-plane times (XY)-plane")],
            name="Orientation",
            description="How to decompose 4-space as a product of planes to define the flat torus",
            default="decompose_wx_yz")
    radius1 = bpy.props.FloatProperty(
        name="Radius 1", default=1.0, subtype='DISTANCE',
        description="Radius for the circle in the first plane of the decomposition")
    radius2 = bpy.props.FloatProperty(
        name="Radius 2", default=1.0, subtype='DISTANCE',
        description="Radius for the circle in the second plane of the decomposition")
    segmentcount1 = bpy.props.IntProperty(
        name="Vertices 1", default=32, min=3,
        description="Number of vertices along circle in first plane")
    segmentcount2 = bpy.props.IntProperty(
        name="Vertices 2", default=32, min=3,
        description="Number of vertices along circle in second plane")

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        debug_message("Adding flat torus")

        sc = bpy.context.scene
        ensure_scene_is_hyper(sc)

        me = bpy.data.meshes.new("Flat torus")
        me.hypersettings.hyper = True
        me["hypermesh-dirty"] = False
        me["hypermesh-justcleaned"] = True

        bm = bmesh.new()
        bm.from_mesh(me)
        layw = bm.verts.layers.float.new('hyperw')
        layx = bm.verts.layers.float.new('hyperx')
        layy = bm.verts.layers.float.new('hypery')
        layz = bm.verts.layers.float.new('hyperz')

        if self.orientation == "decompose_wx_yz":
            plane1 = (Vector([1, 0, 0, 0]), Vector([0, 1, 0, 0]))
            plane2 = (Vector([0, 0, 1, 0]), Vector([0, 0, 0, 1]))
        elif self.orientation == "decompose_wy_xz":
            plane1 = (Vector([1, 0, 0, 0]), Vector([0, 0, 1, 0]))
            plane2 = (Vector([0, 1, 0, 0]), Vector([0, 0, 0, 1]))
        else:
            plane1 = (Vector([1, 0, 0, 0]), Vector([0, 0, 0, 1]))
            plane2 = (Vector([0, 1, 0, 0]), Vector([0, 0, 1, 0]))

        for i in range(self.segmentcount1):
            for j in range(self.segmentcount2):
                v = bm.verts.new((0, 0, 0))

                theta = i * 2 * pi / self.segmentcount1
                phi = j * 2 * pi / self.segmentcount2

                position = self.radius1 * cos(theta) * plane1[0] +\
                    self.radius1 * sin(theta) * plane1[1] +\
                    self.radius2 * cos(phi) * plane2[0] +\
                    self.radius2 * sin(phi) * plane2[1]

                v[layw] = position[0]
                v[layx] = position[1]
                v[layy] = position[2]
                v[layz] = position[3]

        bm.verts.ensure_lookup_table()

        for i in range(self.segmentcount1):
            for j in range(self.segmentcount2):
                a = ((i+1) % self.segmentcount1)
                b = ((j+1) % self.segmentcount2)
                bm.edges.new((bm.verts[i * self.segmentcount2 + j],
                              bm.verts[i * self.segmentcount2 + b]))
                bm.edges.new((bm.verts[i * self.segmentcount2 + j],
                              bm.verts[a * self.segmentcount2 + j]))

        bm.edges.ensure_lookup_table()

        for i in range(self.segmentcount1):
            for j in range(self.segmentcount2):
                a = ((i+1) % self.segmentcount1)
                b = ((j+1) % self.segmentcount2)
                bm.faces.new((bm.verts[i * self.segmentcount2 + j],
                              bm.verts[a * self.segmentcount2 + j],
                              bm.verts[a * self.segmentcount2 + b],
                              bm.verts[i * self.segmentcount2 + b]))

        bm.to_mesh(me)

        ob = bpy.data.objects.new("Flat torus", me)
        sc.objects.link(ob)
        sc.objects.active = ob
        ob.select = True

        # triggers a projection to 3D
        me.hypersettings.preset = sc.selectedpreset

        return {'FINISHED'}
