#!/bin/usr/env python

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


"""
This module tries to reconstruct tessellated faces
"""


def sorted_edge(edge):
    """
    This function returns sorted edge; e.g.: (4, 1) -> (1, 4).
    """
    return (edge[0], edge[1]) if edge[0] < edge[1] else (edge[1], edge[0])


def extend_polygon(polygon, face, inner_edge):
    """
    This function extend polygon by unique vertices from face that
    are not part of shared inner edge
    """
    polygon.extend([vert for vert in face if vert not in inner_edge])


class EdgeLooper(object):
    """
    Iterator of Face edges
    """

    def __init__(self, face):
        """
        Constructor of EdgeLooper
        """
        self.face = face
        self.edge_index = 0

    def __iter__(self):
        """
        This method returns iterator
        """
        return self

    def __getitem__(self, index):
        """
        This method returns edge at given index
        """
        if index < 0 or index >= len(self.face):
            raise IndexError
        else:
            return (self.face[index], self.face[index + 1]) \
                if (index + 1) < len(self.face) else \
                (self.face[index], self.face[0])

    def __next__(self):
        """
        This method returns next face of face
        """
        try: 
            edge = self[self.edge_index]
        except IndexError:
            raise StopIteration
        else:
            self.edge_index += 1
            return sorted_edge(edge)

    def next(self):
        """
        Backward compatibility for Python 2.x
        """
        return self.__next__()


class Mesh(object):
    """
    Class representing Mesh
    """

    def __init__(self):
        """
        Constructor
        """
        self.vertices = {}
        self.edges = []
        self.polygons = []
        self.tess_faces = {}

    def add_vertices(self, verts):
        """
        This method adds vertices to mesh
        """
        for index, vert in enumerate(verts):
            self.vertices[index] = vert

    def add_edges(self, edges):
        """
        This method adds edges to the mesh
        """
        self.edges.extend([sorted_edge(edge) for edge in edges])

    def add_tess_face(self, face):
        """
        This method adds tessellated face to mesh
        """
        # Create iterator of all face edges
        edge_looper = EdgeLooper(face)
        # Create list of inner edges of polygon from face
        inner_edges = [edge for edge in edge_looper if edge not in self.edges]
        # Add tesselated face to list of faces
        for inner_edge in inner_edges:
            # When there is already tesselated face with same inner edge, then
            # extend this tesselated face with unique vertices from current face
            if inner_edge in self.tess_faces.keys():
                polygon = self.tess_faces[inner_edge]
                extend_polygon(polygon, face, inner_edge)
                # The inner_edge is no longer inner edge, then pop this
                # key from dictionary
                self.tess_faces.pop(inner_edge)
                # When polygon is not included in dictionary of tesselated faces,
                # then it means, that polygon doesn't contain any inner edges.
                # The polygon is complete and can be added to the list of polygons.
                if polygon not in self.tess_faces.values():
                    self.polygons.append(polygon)
            else:
                self.tess_faces[inner_edge] = list(face)


def main():
    """
    Main function for testing
    """
    mesh = Mesh()
    mesh.add_vertices(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)))
    mesh.add_edges(((0, 1), (1, 2), (2, 3), (3, 0)))
    mesh.add_tess_face((0, 1, 2))
    mesh.add_tess_face((0, 2, 3))
    print(mesh.vertices)
    print(mesh.edges)
    print(mesh.tess_faces)
    print(mesh.polygons)


if __name__ == '__main__':
    main()
