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

import bpy
from mathutils import Matrix, Vector
from .OctreeNode import OctreeNode

class Octree():
    def __init__(self, root_center = Vector(),
                 root_half_size = 0, max_indices_per_leaf = 1):
        OctreeNode.max_indices_per_leaf = max_indices_per_leaf
        self.root =\
            OctreeNode(center = root_center, half_size = root_half_size)

        # Create a catalog that maps each index to its respective node in the
        # octree.
        self.catalog = dict()

        # The octree stores indices.  A map is needed to determine their
        # coordinates.
        self.coordinate_map = dict()

    def contract_root(self):
        # Recursively contract the root node if only a single child node
        # exists.
        child_map = self.root.child_map
        if len(child_map) == 1:
            key, self.root = child_map.popitem()
            self.root.parent = None
            self.contract_root()

    def expand_root(self, co):
        old_root = self.root
        old_root_center = old_root.center
        old_root_half_size = old_root.half_size

        # The current root node will become a child of the new root node.  Find
        # the octant key of this child.
        if co.x >= old_root_center.x:
            if co.y >= old_root_center.y:
                if co.z >= old_root_center.z:
                    key = '---'
                else:
                    key = '--+'
            else:
                if co.z >= old_root_center.z:
                    key = '-+-'
                else:
                    key = '-++'
        else:
            if co.y >= old_root_center.y:
                if co.z >= old_root_center.z:
                    key = '+--'
                else:
                    key = '+-+'
            else:
                if co.z >= old_root_center.z:
                    key = '++-'
                else:
                    key = '+++'

        # Create the new root node.
        octant_offset = old_root_half_size * old_root.offset_map[key]
        self.root = OctreeNode(
            center = old_root_center - octant_offset,
            half_size = 2 * old_root_half_size,
        )
        root = self.root

        # Make the old root node a child of the new root node.
        root.child_map[key] = old_root
        old_root.parent = root

        # Recursively expand the root node until it encompasses the specified
        # coordinates.
        root_half_size = root.half_size
        offset = co - root.center
        if (
            abs(offset.x) > root_half_size or
            abs(offset.y) > root_half_size or
            abs(offset.z) > root_half_size
        ):
            self.expand_root(co)

    def get_indices_in_box(self, center, half_size):
        indices_in_box = list()
        self.root.query_indices_in_box(
            center, half_size, self.coordinate_map, indices_in_box
        )
        return indices_in_box

    def insert_indices(self, indices):
        catalog = self.catalog
        coordinate_map = self.coordinate_map

        # Duplicate indices should not exist in the octree.  Remove from the
        # octree all existing indices that are in common with the specified
        # indices.
        common_indices = set(indices).intersection(catalog.keys())
        self.remove_indices(common_indices)

        # Each node has an insert method to recursively add an index to the
        # tree.  However, when adding data to the root, it is necessary to
        # determine if the coordinates exist outside of the root node and
        # adjust the size of it accordingly.
        for index in indices:
            co = coordinate_map[index]
            root = self.root

            # If the coordinates are found to be outside of the root node,
            # adjust the size of it accordingly.
            root_half_size = root.half_size
            offset = co - root.center
            if (
                abs(offset.x) > root_half_size or
                abs(offset.y) > root_half_size or
                abs(offset.z) > root_half_size
            ): 
                # An empty root node can be replaced.
                if not (root.child_map or root.indices):
                    minimum_half_size = max(
                        abs(offset.x), abs(offset.y), abs(offset.z)
                    )
                    self.root = OctreeNode(
                        center = root.center, half_size = minimum_half_size
                    )
                    root = self.root

                # A root node with data or children must become the child of
                # a new root node.
                else:
                    self.expand_root(co)

            # Insert the index into the root node.
            root.insert_index(index, coordinate_map, catalog)

    def insert_object(self, mesh_object, space = 'WORLD'):
        # Only mesh objects can be inserted into the octree.
        if mesh_object.type != 'MESH':
            raise Exception(
                "Only mesh objects can be inserted into the octree."
            )

        # Ensure that a valid coordinate system is specified.
        if space not in {'OBJECT', 'WORLD'}:
            raise Exception((
                    "Invalid space argument '{0}' not found in " +
                    "('OBJECT', 'WORLD')"
                ).format(space)
            )

        # Write Edit mode's data to the mesh object, if necessary.
        if mesh_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Generate the coordinate map.
        vertices = mesh_object.data.vertices
        if space == 'OBJECT':
            coordinate_map = {
                vertex.index : vertex.co.copy()
                for vertex in vertices
            }
        else:
            matrix_world = mesh_object.matrix_world
            coordinate_map = {
                vertex.index : matrix_world * vertex.co
                for vertex in vertices
            }

        # Derive the sequence of indices from the coordinate map.
        indices = coordinate_map.keys()

        # Assign the coordinate map to the octree, merging it with an existing
        # map, if necessary.
        if self.coordinate_map:
            self.coordinate_map.update(coordinate_map)
        else:
            self.coordinate_map = coordinate_map

        # If the root node is empty, modify it, and insert the object's vertex
        # indices.
        root = self.root
        if not (root.child_map or root.indices):
            # Set the octree root node's center to that of the object's
            # bounding box.
            bbox = mesh_object.bound_box
            root.center = Vector(0.125 * sum(t) for t in zip(*bbox))
            if space == 'WORLD':
                root.center = matrix_world * root.center

            # Set the octree root node's half size to slightly more than the
            # largest dimension of the bounding box.  This ensures that the
            # root is large enough to encompass the entire object.
            if space == 'OBJECT':
                shared_corner = Vector(bbox[0])
                root.half_size = 1.1 * max(
                    (Vector(bbox[1]) - shared_corner).length,
                    (Vector(bbox[3]) - shared_corner).length,
                    (Vector(bbox[4]) - shared_corner).length
                )
            else:
                root.half_size = 1.1 * max(tuple(mesh_object.dimensions))

            # All indices are known to be encompassed by the root node.  As
            # such, insert the indices directly into the root node to
            # circumvent unnecessary bounds checks.
            catalog = self.catalog
            for index in indices:
                root.insert_index(index, coordinate_map, catalog)

        # Otherwise, the root node is not empty.  Insert the indices into the
        # octree.
        else:
            self.insert_indices(indices)

    def remove_indices(self, indices):
        # Remove indices from their corresponding nodes in the octree,
        # discarding empty leaf nodes and contracting the root node when
        # possible.
        catalog = self.catalog
        for index in indices:
            leaf = catalog[index]
            del catalog[index]
            leaf.indices.remove(index)
            if not leaf.indices:
                leaf.remove()
        self.contract_root()

    def reset(self):
        self.__init__(max_indices_per_leaf = self.root.max_indices_per_leaf)