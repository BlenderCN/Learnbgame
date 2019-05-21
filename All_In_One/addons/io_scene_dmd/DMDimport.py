#-------------------------------------------------------------------------------
#
#       Модуль импорта DMD-модели в Blender
#       (c) РГУПС, ВЖД 19/07/2018
#       Разработал: Притыкин Д.Е.
#
#-------------------------------------------------------------------------------
import bpy
import bmesh
import os
from .DMD import MultyMesh

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------
def getFileName(path):
    basename = os.path.basename(path)
    tmp = basename.split(".")
    return tmp[0]

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
class Importer:

    def __init__(self):
        self.dmd = MultyMesh()

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def setUVcoords(self, md, mesh):
        bm = bmesh.new()
        bm.from_mesh(md)

        uv_layer = bm.loops.layers.uv.new()

        # Перебираем все грани
        for i, f in enumerate(bm.faces):
            # Получаем список индексов текстурных вершин конкретной грани
            tex_face = mesh.parent.tex_faces[i]
            for v, l in zip(tex_face, f.loops):
                # Берем слой развертки для конкретной грани
                l_uv = l[uv_layer]
                try:
                    # читаем текстурные координаты для конкретной вершины в данном слое
                    tmp = mesh.parent.tex_vertices[v]
                    l_uv.uv[0] = tmp[0]
                    l_uv.uv[1] = tmp[1]
                except Exception as ex:
                    print(ex)
                    return

        bm.to_mesh(md)

    #---------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------
    def load(self, filepath):
        self.dmd.loadFromFile(filepath)

        for m_idx, m in enumerate(self.dmd.meshes):

            obj_name = getFileName(filepath)
            print("Process new model: ", obj_name)

            # Загружаем геометрию
            md = bpy.data.meshes.new(obj_name + "-" + str(m_idx))
            print("Mesh name: ", md.name)
            print("New mesh created...OK")
            md.from_pydata(m.vertices, [], m.faces)
            print("Loaded data to mesh...OK")
            md.update(calc_edges=True)
            print("Mesh update...OK")

            # Загружаем текстурные координаты
            self.setUVcoords(md, m)

            # Создаем новый объект на основе считанной геометрии
            obj = bpy.data.objects.new(md.name, md)
            print("New scene object creation...OK")
            # Присоединяем новый объект к сцене
            bpy.context.scene.objects.link(obj)
            print("Link object to scene...OK")


