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

# <pep8 compliant>

import bpy


class MeshRasterizer(bpy.types.Operator):
    '''rasterizes all vertices of the selected mesh object'''
    bl_idname = "object.mesh_rasterize"
    bl_label = "Rasterize Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    bits = bpy.props.IntProperty(name="Bits", default=8, min=1, max=64,
        soft_min=1, soft_max=64)

    @classmethod
    def poll(cls, context):
        return context.active_object != None and \
            context.active_object.type == 'MESH'

    def execute(self, context):
        if context.active_object.type != 'MESH':
            return {'CANCELLED'}
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()

        mesh = context.active_object

        # apply modifiers
        for m in mesh.modifiers:
            bpy.ops.object.modifier_apply(modifier=m.name)
        bb = mesh.bound_box
        boundMin = [bb[0][0], bb[0][1], bb[0][2]]
        boundMax = [bb[7][0], bb[7][1], bb[7][2]]
        # find absolute min and max
        for bVert in mesh.bound_box:
            for dim in range(3):
                if bVert[dim] < boundMin[dim]:
                    boundMin[dim] = bVert[dim]
                elif bVert[dim] > boundMax[dim]:
                    boundMax[dim] = bVert[dim]
        # calculate number of segments
        segs = pow(2, self.bits) - 1
        # we don't have a true center so need to adjust by half a seg
        adjust = 0.5 / (segs + 1)
        segmentLength = [
            (boundMax[0] - boundMin[0]) / segs,
            (boundMax[1] - boundMin[1]) / segs,
            (boundMax[2] - boundMin[2]) / segs]

        # rasterize every vertex of the mesh
        for vert in mesh.data.vertices:
            # calculate the rasterized value for each dimension x,y,z
            for dim in range(3):
                if segmentLength[dim] > 0:
                    offset = (abs(boundMin[dim]) + \
                        vert.co[dim]) % segmentLength[dim]
                    if (adjust + offset) > segmentLength[dim] / 2.0:
                        vert.co[dim] = vert.co[dim] + \
                            segmentLength[dim] - offset
                    else:
                        vert.co[dim] = vert.co[dim] - offset

        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.active_object.type != 'MESH':
            return {'CANCELLED'}
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()
        # only a copy will be rasterized, original is hidden
        orig = context.active_object
        bpy.ops.object.duplicate_move()
        orig.hide = True
        return self.execute(context)
