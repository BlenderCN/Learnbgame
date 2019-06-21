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

# <pep8-80 compliant>

import bmesh
import bpy

class VertexProperties():
    def __init__(self):
        self.mesh_object = None

        # Properties
        self.boundary_indices = set()
        self.manifold_indices = set()
        self.hidden_indices = set()
        self.selected_indices = set()

    def determine_indices(self, properties):
        invalid_properties =\
            properties.difference(
                {'BOUNDARY', 'MANIFOLD', 'HIDDEN', 'SELECTED'}
            )
        if invalid_properties:
            raise Exception((
                    "Invalid vertex property set {0}.  Parameter " +
                    "\"properties\" expects a subset of " +
                    "('BOUNDARY', 'MANIFOLD', 'HIDDEN', 'SELECTED')."
                ).format(invalid_properties)
            )

        mesh_object = self.mesh_object
        mesh = mesh_object.data

        # Create the bmesh object.
        if mesh_object.mode == 'EDIT':
            bmesh_object = bmesh.from_edit_mesh(mesh)
        else:
            bmesh_object = bmesh.new()
            bmesh_object.from_mesh(mesh)

        # Determine the specified property states of all vertex indices.
        bmesh_verts = bmesh_object.verts
        if 'BOUNDARY' in properties:
            self.boundary_indices =\
                {vert.index for vert in bmesh_verts if vert.is_boundary}
        if 'MANIFOLD' in properties:
            self.manifold_indices =\
                {vert.index for vert in bmesh_verts if vert.is_manifold}
        if 'HIDDEN' in properties:
            self.hidden_indices =\
                {vert.index for vert in bmesh_verts if vert.hide}
        if 'SELECTED' in properties:
            self.selected_indices =\
                {vert.index for vert in bmesh_verts if vert.select}

    def reset(self):
        self.__init__()
