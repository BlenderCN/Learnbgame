bl_info = {
    "name": "CityGML Import Basic",
    "author": "",
    "version": (0, 1),
    "blender": (2, 7, 6),
    "category": "Import-Export"
}

import os
from xml.etree import ElementTree as et

import bpy
from bpy_extras.io_utils import ExportHelper


def main(filename):

    def unflatten(coords, s=0.002):
        return [(coords[i] * s, coords[i + 1] * s, coords[i + 2] * s) for i in range(0, len(coords), 3)]

    tree = et.parse(filename)
    polygons = tree.findall('.//{http://www.opengis.net/gml}Polygon')

    master_verts = []
    master_faces = []
    extend_verts = master_verts.extend
    append_faces = master_faces.append

    for i, p in enumerate(polygons):
        # print(p.keys())   $ gets ID
        # the ID is of a polygon is something like 80182bd5-e999-445c-a2d5-6dc690c928a4

        # app:ParameterizedTexture
        # app:imageURI
        # app:mimeType
        # app:target    <app:target uri="#ID">    # this ID refers to the polygon ID.
        # app:textureCoordinates

        poslist = p.find('.//{http://www.opengis.net/gml}posList')
        text = poslist.text

        coords = [float(i) for i in text.split(' ')]
        verts = unflatten(coords)

        start_idx = len(master_verts)
        end_idx = start_idx + len(verts)
        extend_verts(verts)
        append_faces([i for i in range(start_idx, end_idx)])

    mesh = bpy.data.meshes.new("mesh_name")
    mesh.from_pydata(master_verts, [], master_faces)
    mesh.update()

    obj = bpy.data.objects.new("obj_name", mesh)

    scene = bpy.context.scene
    scene.objects.link(obj)


# pick folder and import from... maybe this is a bad name.
class CityGMLDirectorySelector(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.citygml_folder_selector"
    bl_label = "pick an xml file"

    filename_ext = ".xml"
    use_filter_folder = True

    def execute(self, context):
        fdir = self.properties.filepath
        main(fdir)
        return{'FINISHED'}


def menu_import(self, context):
    self.layout.operator(CityGMLDirectorySelector.bl_idname, text="cityGML (.xml)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.utils.unregister_module(__name__)
