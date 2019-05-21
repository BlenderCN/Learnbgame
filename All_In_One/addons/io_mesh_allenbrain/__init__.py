# Plugin for loading Allen brain .msh format compartment structures into Blender

bl_info = {
    'name': 'Load Allen brain mesh',
    'author': 'Christopher M. Bruns',
    'version': (1, 0, 0),
    'blender': (2, 76, 0),
    'location': 'File > Import > Allen Brain Mesh',
    'description': 'Import Allen Brain Compartment Mesh',
    'license': 'MIT',
    'category': 'Import'
}

__author__ = bl_info['author']
__license__ = bl_info['license']
__version__ = ".".join([str(s) for s in bl_info['version']])


import os
import math
import struct # Python library for reading/writing binary numbers

import numpy
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty


class AllenMeshPoint:
    "One XYZ point and its associated unit normal direction"
    def __init__(self, point, normal):
        self.point = point
        self.normal = normal


class AllenMesh:
    "Brain compartment surface mesh from Allen Brain Institute format"
    def __init__(self):
        self.points = list()
        self.strips = list()
        self.triangles = list()

    def load_msh(self, file_):
        # Read count of points/normals
        num_points = struct.unpack('I', file_.read(4))[0]
        print (num_points, "points found")
        # Read alternating normals and points
        for i in range(num_points):
            normal = struct.unpack('3f', file_.read(4*3))
            # print normals[ip]
            point = struct.unpack('3f', file_.read(4*3))
            self.points.append(AllenMeshPoint(point, normal))
        # Read count of triangle strips
        num_strips = struct.unpack('I', file_.read(4))[0]
        # print num_strips, "triangle strips found"
        # Load triangle strips
        num_tris = 0
        for i in range(num_strips):
            num_strip_points = struct.unpack('H', file_.read(2))[0]
            num_tris += num_strip_points - 2
            # print "strip %d contains %d points" % (i, num_strip_points)
            strip = struct.unpack('%dI' % num_strip_points, file_.read(4*num_strip_points))
            self.strips.append(strip)
        # Populate triangle indices
        for strip in self.strips:
            for i in range(len(strip) - 2):
                if i % 2 == 0: # Even number
                    self.triangles.append(tuple([strip[i], strip[i+1], strip[i+2]]))
                else: # Odd number
                    self.triangles.append(tuple([strip[i], strip[i+2], strip[i+1]]))
        assert(len(self.triangles) == num_tris)


class AllenBrainMeshImporter(bpy.types.Operator, ImportHelper):
    "Loads Allen brain compartment meshes"

    bl_label = 'Import Allen brain compartment'
    bl_idname = 'import_mesh.allenbrain'
    filename_ext = '.msh'
    filter_glob = StringProperty(
            default="*.msh",
            options={'HIDDEN'})
    
    def execute(self, context):
        "Load the mesh file the user already specified, and display the geometry in the current scene"
        allen_mesh = AllenMesh()
        with open(self.filepath, "rb") as fh:
            allen_mesh.load_msh(fh)
        name = os.path.splitext(os.path.basename(self.filepath))[0]
        bpy_mesh = bpy.data.meshes.new(name)
        vertices = list()
        normals = list()
        scale = 0.001
        for p in allen_mesh.points:
            vertices.append(scale * numpy.array(p.point, 'f'))
            # print(p.point)
            normals.append(p.normal)
        faces = list()
        for t in allen_mesh.triangles:
            faces.append(list(t))
            # print(t)
        bpy_mesh.from_pydata(vertices, [], faces)
        for i,v in enumerate(bpy_mesh.vertices):
            v.normal = normals[i]
        bpy_object = bpy.data.objects.new(name, bpy_mesh)
        bpy.context.scene.objects.link(bpy_object)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AllenBrainMeshImporter)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(AllenBrainMeshImporter)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

def menu_func_import(self, context):
    self.layout.operator(AllenBrainMeshImporter.bl_idname, text="Allen brain compartment mesh (.msh)")

if __name__ == "__main__":
    register()
