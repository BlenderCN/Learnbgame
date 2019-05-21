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
Module with unit tests for tess_face module
"""

import tess_faces as tf

VERTICES = ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0))
EDGES = ((0, 1), (1, 2), (2, 3), (3, 0))
TESS_FACES = ((0, 1, 2), (0, 2, 3))
POLYGONS = ((0, 1, 2, 3),)
INNER_EDGES = ((0, 2),)


def test_mesh_constructor():
    """
    Test creating new mesh
    """
    mesh = tf.Mesh()
    assert len(mesh.vertices) == 0
    assert len(mesh.edges) == 0
    assert len(mesh.polygons) == 0
    assert len(mesh.tess_faces) == 0


def test_add_vertices():
    """
    Test adding vertices to the mesh
    """
    mesh = tf.Mesh()
    mesh.add_vertices(VERTICES)
    assert list(VERTICES) == list(mesh.vertices.values())


def test_add_edges():
    """
    Test adding edges to the mesh
    """
    mesh = tf.Mesh()
    mesh.add_vertices(VERTICES)
    mesh.add_edges(EDGES)
    edges = [tuple(sorted(edge)) for edge in EDGES]
    assert edges == mesh.edges


def test_add_tess_face():
    """
    Test adding tessellated edges
    """
    mesh = tf.Mesh()
    mesh.add_vertices(VERTICES)
    mesh.add_edges(EDGES)
    for tess_face in TESS_FACES:
        mesh.add_tess_face(tess_face)
        for inner_edge in mesh.tess_faces.keys():
            assert inner_edge in INNER_EDGES
    for polygon in mesh.polygons:
        assert tuple(polygon) in POLYGONS
