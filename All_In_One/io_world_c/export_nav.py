import bpy
import math

class NavEdge(object):
    def __init__(self):
        self.neighbor_index = -1
        self.vertices = []
        self.solid = False

    def __eq__(self, other):
        if self.vertices[0] == other.vertices[0] and self.vertices[1] == other.vertices[1]:
            return True
        else:
            return False

class NavPoly(object):
    def __init__(self):
        self.edge_start = 0
        self.edge_count = 0
        self.normal = []

class NavMesh(object):
    def __init__(self):
        self.vertices = []
        self.polys = []
        self.edges = []

    def extract(self, b_mesh):
        poly_edge_map = {ek: b_mesh.data.edges[i] for i, ek in enumerate(b_mesh.data.edge_keys)}

        for vert in b_mesh.data.vertices:
            self.vertices.append([e for e in vert.co])

        for poly in b_mesh.data.polygons:
            new_poly = NavPoly()
            new_poly.edge_start = len(self.edges)
            new_poly.edge_count = 0
            new_poly.normal = [e for e in poly.normal]

            for ek in poly.edge_keys:
                edge = poly_edge_map[ek]
                new_edge = NavEdge()
                new_edge.vertices = [e for e in edge.vertices]
                new_edge.solid = edge.use_seam
                self.edges.append(new_edge)
                new_poly.edge_count += 1

            self.polys.append(new_poly)

        for poly_index, poly in enumerate(self.polys):
            for other_poly_index, other_poly in enumerate(self.polys):
                if poly_index == other_poly_index:
                    continue

                for edge_index in range(poly.edge_start, poly.edge_start + poly.edge_count):
                    for other_edge_index in range(other_poly.edge_start, other_poly.edge_start + other_poly.edge_count):
                        if self.edges[edge_index] == self.edges[other_edge_index]:
                            self.edges[edge_index].neighbor_index = other_poly_index


def export(b_mesh, filepath):
    file_version = 2

    file = open(filepath, "w")

    mesh = NavMesh()
    mesh.extract(b_mesh)

    file.write("# World C - NavMesh\n")
    file.write("version: %i\n" % file_version)
    file.write("vertex_count: %i\n" % len(mesh.vertices))
    file.write("poly_count: %i\n" % len(mesh.polys))
    file.write("edge_count: %i\n" % len(mesh.edges))

    file.write("vertices: \n")
    for vert in mesh.vertices:
        file.write("%f, %f, %f\n" % (vert[0], vert[1], vert[2]))

    file.write("edges: \n")
    for edge in mesh.edges:
        file.write("%i, %i, %i, %i\n" % (edge.neighbor_index, edge.vertices[0], edge.vertices[1], edge.solid))

    file.write("polys: \n")
    for poly in mesh.polys:
        file.write("%i, %i\n" % (poly.edge_start, poly.edge_count))
        file.write("%f, %f, %f\n" % (poly.normal[0], poly.normal[1], poly.normal[2]))

    file.close()
