import bpy
import math
import struct

class Mesh(object):
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.colors = []
        self.uv_channels = []

    def extract(self, b_mesh):

        for uv_layer in b_mesh.data.uv_layers:
            self.uv_channels.append([])

        for poly in b_mesh.data.polygons:
            for loop_index in poly.loop_indices:
                loop = b_mesh.data.loops[loop_index]

                self.normals.append(loop.normal)
                vert = b_mesh.data.vertices[loop.vertex_index]

                pos = b_mesh.matrix_world * vert.co
                self.vertices.append(pos)

                for channel, uv_layer in enumerate(b_mesh.data.uv_layers):
                    self.uv_channels[channel].append([uv_layer.data[loop_index].uv[0], uv_layer.data[loop_index].uv[1]])


def export(b_mesh, filename):
    file_version = 1

    b_mesh.data.calc_tangents()

    mesh = Mesh()
    mesh.extract(b_mesh)

    file = open(filename, "w")
    file.write("# World C - StaticMesh\n")

    file.write("version: %i\n" % file_version)
    file.write("vertex_count: %i\n" % len(mesh.vertices))
    file.write("uv_channel_count: %i\n" % len(mesh.uv_channels))

    file.write("vertices: \n")
    for vert in mesh.vertices:
        file.write("%f, %f, %f\n" % (vert[0], vert[1], vert[2]))

    file.write("normals: \n")
    for normal in mesh.normals:
        file.write("%f, %f, %f\n" % (normal[0], normal[1], normal[2]))

    for i, uv_channel in enumerate(mesh.uv_channels):
        file.write("uv %i: \n" % i)
        for uv in uv_channel:
            file.write("%f, %f\n" % (uv[0], uv[1]))
    file.close()

def export_binary(b_mesh, filename):
    file_version = 1

    b_mesh.data.calc_tangents()

    mesh = Mesh()
    mesh.extract(b_mesh)

    file = open(filename, "wb")
    file.write(struct.pack('<i', file_version))
    file.write(struct.pack('<i', len(mesh.vertices)))
    file.write(struct.pack('<i', len(mesh.uv_channels)))

    for i in range(len(mesh.vertices)):
        vert = mesh.vertices[i]
        file.write(struct.pack('<fff', vert[0], vert[1], vert[2]))
        normal = mesh.normals[i]
        file.write(struct.pack('<fff', normal[0], normal[1], normal[2]))
        for uv_channel in mesh.uv_channels:
            uv_coord = uv_channel[i]
            file.write(struct.pack('<ff', uv_coord[0], uv_coord[1]))

    file.close()
