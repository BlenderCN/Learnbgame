bl_info = {
    "name": "FWNormals",
    "description": "Weights normals based on face area, using the face vector for fine tuning.",
    "author": "Steven Raybell (popcornbag); Original Author: Simon Lusenc (50keda)",
    "version": (0, 2),
    "blender": (2, 79, 0),
    "location": "3D View > Quick Search > Weight Normals",
    "category": "Object",
    "support": "COMMUNITY"
}

import bpy, bmesh, array
from mathutils import *
from math import *


class FaceWeightedNormals(bpy.types.Operator):
    """Calculate weighted normals for active object."""
    bl_idname = "object.calculate_weighted_normals"
    bl_label = "Weight Normals"
    bl_options = set()

    @staticmethod
    def AngleBetweenVectors(v1: Vector, v2: Vector):
    
        arg1 = v1.normalized()
        arg2 = v2.normalized()
        
        angle = None
        try:
            angle = acos(arg1.dot(arg2))
        except:
            angle = 0
            
        return angle
    
    @staticmethod
    def calc_weighted_normal(bm, vert_index, edge_index):
        """
        calc_weighted_normal(bm, vert_index, edge_index)
        
        Calculates weighted normal for given combination of vertex and edge index.
        Need a check here to make sure that the vertex and edge are properly grouped.

        Parameters
        ----------
        bm : bmesh
        vert_index : int 
            index of the vertex to calculate normal for
        edge_index : int 
            index of the edge to use for calculation (vertex has to belong to this edge)
        
        Returns
        -------
        Vector
            A vector that represents the calculated normal for the specified vertex and edge index
        """
        normal_hash = str(vert_index) + ":" + str(edge_index)

        edge = bm.edges[edge_index]
        vert = bm.verts[vert_index]

        selected_faces = []

        for f in edge.link_faces:

            if not f.select:

                f.select = True
                selected_faces.append(f)

        # select linked faces of already selected edges
        # until every smooth face around current loop is selected
        more_selected = 1
        while more_selected > 0:

            more_selected = 0
            for edge1 in vert.link_edges:

                if edge1.smooth and edge1.select:

                    for f in edge1.link_faces:

                        if not f.select:

                            f.select = True
                            selected_faces.append(f)

                            more_selected += 1

        # calculate face areas
        areas = {}
        max_area = 0
        for i, f in enumerate(selected_faces):
            area = f.calc_area()
            areas[i] = area
            
            if area > max_area:
                max_area = area

        # calculate face angle
        faceangle = []
        for i, f in enumerate(selected_faces):
            v1 = Vector(f.verts[0].co)
            v2 = Vector(f.verts[1].co)
            v3 = Vector(f.verts[2].co)
                       
            # consider doing something more dynamic here to better support non-coplanar n-gons
            a1 = FaceWeightedNormals.AngleBetweenVectors((v2-v1), (v3-v1))
            a2 = FaceWeightedNormals.AngleBetweenVectors((v1-v2), (v3-v2))
            a3 = FaceWeightedNormals.AngleBetweenVectors((v1-v3), (v2-v3))
            
            faceangle.append([ a1, a2, a3 ])
            
        # calculate normal
        normal = Vector()
        for i, f in enumerate(selected_faces):
            f.normal_update()
            
            # iterate over each vertex angle and area mapped to the face, 
            # then use a percentage of the total face area as a final adjustment.
            for r in range(0, 3):
                normal += (f.normal * faceangle[i][r] * areas[i]) * (areas[i] / max_area)

            # deselect all the faces
            f.select = False

        n_normal = normal.normalized()

        return n_normal

    @classmethod
    def poll(cls, context):
        return context.object and context.object.mode == "OBJECT" and context.object.type == "MESH"

    def execute(self, context):

        mesh = context.object.data

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        # deselect everything first
        for v in bm.faces:
            v.select = False
            v.hide = False

        for v in bm.edges:
            v.select = False
            v.hide = False

        for v in bm.verts:
            v.select = False
            v.hide = False

        nor_list = [(0,)] * len(mesh.loops)
        for f in bm.faces:

            # map both edge indices into vertex (loop has info only about one edge)
            verts_edge_map = {}
            for e in f.edges:
                for v in e.verts:

                    v_i = v.index

                    if v_i not in verts_edge_map:
                        verts_edge_map[v_i] = {e.index: 1}
                    else:
                        verts_edge_map[v_i][e.index] = 1

            for curr_loop in f.loops:

                edge_keys = verts_edge_map[curr_loop.vert.index].keys()

                # if current loop vertex has at leas one sharp edge around calculate weighted normal
                for e_i in edge_keys:

                    if not mesh.edges[e_i].use_edge_sharp:

                        curr_n = FaceWeightedNormals.calc_weighted_normal(bm, curr_loop.vert.index, e_i)
                        nor_list[curr_loop.index] = curr_n

                        break

                else:

                    nor_list[curr_loop.index] = mesh.loops[curr_loop.index].normal

        bm.free()

        mesh.use_auto_smooth = True
        bpy.ops.mesh.customdata_custom_splitnormals_clear()

        bpy.ops.mesh.customdata_custom_splitnormals_add()
        mesh.normals_split_custom_set(nor_list)
        mesh.free_normals_split()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FaceWeightedNormals)


def unregister():
    bpy.utils.unregister_class(FaceWeightedNormals)


if __name__ == '__main__':
    register()
