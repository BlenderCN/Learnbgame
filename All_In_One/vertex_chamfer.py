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

bl_info = {
    "name": "Vertex Chamfer",
    "author": "Andrew Hale (TrumanBlending)",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "location": "Spacebar Menu",
    "description": "Chamfer vertex",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import bmesh


class VertexChamfer(bpy.types.Operator):
    bl_idname = "mesh.vertex_chamfer"
    bl_label = "Chamfer Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    factor = bpy.props.FloatProperty(name="Factor",
                                     default=0.1,
                                     min=0.0,
                                     soft_max=1.0)
    relative = bpy.props.BoolProperty(name="Relative", default=False)
    dissolve = bpy.props.BoolProperty(name="Remove", default=True)
    displace = bpy.props.FloatProperty(name="Displace",
                                       soft_min=-5.0,
                                       soft_max=5.0)

    @classmethod
    def poll(self, context):
        return (context.active_object.type == 'MESH' and
                context.mode == 'EDIT_MESH')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "factor", text="Fac" if self.relative else "Dist")
        sub = layout.row()
        sub.prop(self, "relative")
        sub.prop(self, "dissolve")
        if not self.dissolve:
            layout.prop(self, "displace")

    def execute(self, context):
        ob = context.active_object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)

        fac = self.factor
        rel = self.relative
        dissolve = self.dissolve
        displace = self.displace

        # Store the original edge lengths for all edges
        elens = bm.edges.layers.float.new("edge_lengths_chamfer")
        for e in bm.edges:
            e[elens] = e.calc_length()

        # Get the selected verts
        verts = [v for v in bm.verts if v.select]

        # Loop over all verts
        for v in verts:
            # Loop over the edges that contain this vert
            for e in v.link_edges[:]:
                # Determine the distance down the edge the new vert is created
                if rel:
                    if e.other_vert(v).select:
                        val = fac * e[elens] / e.calc_length()
                        if e[elens] == e.calc_length():
                            val = min(val, 0.5)
                    else:
                        val = fac
                else:
                    val = fac / e.calc_length()
                    if e.other_vert(v).select and e[elens] == e.calc_length():
                        val = min(val, 0.5)
                # Cut the edge
                ne, nv = bmesh.utils.edge_split(e, v, val)
                # Assign the edge length from the orginal length
                ne[elens] = e[elens]
            # Loop over all the loops of the vert
            for l in v.link_loops:
                # Split the face
                bmesh.utils.face_split(l.face,
                                       l.link_loop_next.vert,
                                       l.link_loop_prev.vert)
            # Remove the vert or displace otherwise
            if dissolve:
                success = bmesh.utils.vert_dissolve(l.vert)
                # Sometimes dissolve doesn't remove the vert, so just delete
                if not success:
                    bm.verts.remove()
            else:
                v.co += displace * v.normal
        # Remove the customdata layer and calc the tessfaces
        bm.edges.layers.float.remove(elens)
        me.calc_tessface()

        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()