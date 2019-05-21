#-------------------------------------------------------------------------------
#
#       Модуль экспорта DMD-модели в Blender
#       (c) РГУПС, ВЖД 06/12/2018
#       Разработал: Притыкин Д.Е.
#
#-------------------------------------------------------------------------------
import bpy
import bmesh
import os
from .DMD import MultyMesh

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class Exporter:

    def __init__(self):
        self.filepath = ""

    def exportModel(self, path):

        self.filepath = path

        dmd_model = MultyMesh()

        objs = bpy.context.selected_objects

        for obj in objs:

            if obj.type == 'MESH':

                from .DMD import Mesh

                print("Process object: " + obj.name)

                model = obj.data

                bm = bmesh.new()
                bm.from_mesh(model)
                bmesh.ops.triangulate(bm, faces=bm.faces)
                md = bpy.data.meshes.new("temporary")
                bm.to_mesh(md)
                bm.free()

                mesh = Mesh()

                vert_indices = []
                for vertex in md.vertices:
                    mesh.vertices.append(list(vertex.co))
                    mesh.vertex_count += 1
                    vert_indices.append(mesh.vertex_count)

                for face in md.polygons:
                    mesh.faces.append(list(face.vertices))
                    mesh.faces_count += 1

                dmd_model.meshes.append(mesh)

                if obj.material_slots:
                    mat = obj.material_slots[0].material

                    if mat.texture_slots:
                        dmd_model.texture_present = True

                        for poly in md.polygons:
                            print("Polygon: ", poly.index)
                            for li in poly.loop_indices:
                                vi = md.loops[li].vertex_index
                                uv = md.uv_layers.active.data[li].uv
                                print("   Loop index %i (Vertex %i) - UV %f %f" % (li, vi, uv.x, uv.y))

                        # Читаем текстурные вершины
                        for poly in md.polygons:
                            tex_face = []
                            for li in poly.loop_indices:
                                uv = md.uv_layers.active.data[li].uv
                                texel = [uv.x, 1 - uv.y, 0.0]
                                dmd_model.tex_vertices.append(texel)
                                dmd_model.tex_v_count += 1;
                                print(li)
                                tex_face.append(li)

                            dmd_model.tex_faces.append(tex_face)
                            dmd_model.tex_f_count += 1



        dmd_model.writeToFile(path, dmd_model)