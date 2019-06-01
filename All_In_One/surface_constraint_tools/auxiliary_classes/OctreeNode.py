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

from mathutils import Vector

class OctreeNode():
    max_indices_per_leaf = 1
    offset_map = {
        '+++' : Vector((1, 1, 1)), '---' : Vector((-1, -1, -1)),
        '++-' : Vector((1, 1, -1)), '--+' : Vector((-1, -1, 1)),
        '+-+' : Vector((1, -1, 1)), '-+-' : Vector((-1, 1, -1)),
        '+--' : Vector((1, -1, -1)), '-++' : Vector((-1, 1, 1))
    }

    def __init__(self, center = Vector(), half_size = 0, parent = None):
        self.center = center
        self.child_map = dict()
        self.half_size = half_size
        self.indices = set()
        self.parent = parent

    def insert_index(self, index, coordinate_map, catalog):
        # If the node is on the interior of the octree, determine the child
        # node to which the index belongs, and insert it recursively.
        if self.child_map:
            center = self.center
            child_map = self.child_map
            co = coordinate_map[index]

            # Determine the octant to which the index belongs.
            if co.x < center.x:
                if co.y < center.y:
                    if co.z < center.z:
                        key = '---'
                    else:
                        key = '--+'
                else:
                    if co.z < center.z:
                        key = '-+-'
                    else:
                        key = '-++'
            else:
                if co.y < center.y:
                    if co.z < center.z:
                        key = '+--'
                    else:
                        key = '+-+'
                else:
                    if co.z < center.z:
                        key = '++-'
                    else:
                        key = '+++'

            # Ensure that the child node exists.
            if not key in child_map:
                child_half_size = self.half_size / 2
                octant_offset = child_half_size * self.offset_map[key]
                child_map[key] = OctreeNode(
                    center = center + octant_offset,
                    half_size = child_half_size, parent = self
                )

            # Recursively insert the index into the child node.
            child_map[key].insert_index(index, coordinate_map, catalog)

        # The node is a leaf.
        else:
            # Add the index to the leaf if it is not full, and update the
            # catalog.
            if len(self.indices) < self.max_indices_per_leaf:
                self.indices.add(index)
                catalog[index] = self

            # In the case that a node is full, remove the indices from the node
            # and make a recursive call to insert each index into its
            # respective child node.
            else:
                indices = self.indices
                self.indices = set()
                indices.add(index)
                for index in indices:
                    if index in catalog:
                        del catalog[index]
                    center = self.center
                    child_map = self.child_map
                    co = coordinate_map[index]

                    # Determine the octant to which the index belongs.
                    if co.x < center.x:
                        if co.y < center.y:
                            if co.z < center.z:
                                key = '---'
                            else:
                                key = '--+'
                        else:
                            if co.z < center.z:
                                key = '-+-'
                            else:
                                key = '-++'
                    else:
                        if co.y < center.y:
                            if co.z < center.z:
                                key = '+--'
                            else:
                                key = '+-+'
                        else:
                            if co.z < center.z:
                                key = '++-'
                            else:
                                key = '+++'

                    # Ensure that the child node exists.
                    if not key in child_map:
                        child_half_size = self.half_size / 2
                        octant_offset = child_half_size * self.offset_map[key]
                        child_map[key] = OctreeNode(
                            center = center + octant_offset,
                            half_size = child_half_size, parent = self
                        )

                    # Recursively insert the index into the child node.
                    child_map[key].insert_index(index, coordinate_map, catalog)

    def query_indices_in_box(self, center, half_size,
                             coordinate_map, query_result):
        node_half_size = self.half_size
        offset = self.center - center
        offset_x = abs(offset.x)
        offset_y = abs(offset.y)
        offset_z = abs(offset.z)

        # Only proceed if the query box intersects with the node.
        intersection_distance = half_size + node_half_size
        if (
            offset_x > intersection_distance or
            offset_y > intersection_distance or
            offset_z > intersection_distance
        ):
            return

        # No additional intersection tests are required for nodes that are
        # fully contained within the query box.
        containment_distance = half_size - node_half_size
        if (half_size > node_half_size) and not (
            offset_x > containment_distance or
            offset_y > containment_distance or
            offset_z > containment_distance
        ):
            # Find all indices that are contained within this node.
            self.query_indices_in_node(query_result)

        # The node partially intersects with the query box.
        else: 
            # If the partially intersecting node is internal, recursively query
            # its child nodes for indices that are within the box.
            child_map = self.child_map
            if child_map:
                for key in child_map:
                    child_map[key].query_indices_in_box(
                        center, half_size, coordinate_map, query_result
                    )

            # Not all of the indices in a partially intersecting leaf node are
            # necessary inside of the query box.
            else:
                for index in self.indices:
                    co = coordinate_map[index]
                    offset = co - center
                    if not (
                        abs(offset.x) > half_size or
                        abs(offset.y) > half_size or
                        abs(offset.z) > half_size
                    ):
                        query_result.append(index)

    def query_indices_in_node(self, query_result):
        # Recursively determine the indices that are contained within the node.
        child_map = self.child_map
        if child_map:
            for key in child_map:
                child_map[key].query_indices_in_node(query_result)
        else:
            query_result.extend(self.indices)

    def remove(self):
        # Recursively remove this node and any non-root parent nodes that
        # become empty (childless) as a consequence of this operation.
        parent = self.parent
        if parent:
            child_map = parent.child_map
            for key, child in child_map.items():
                if child is self:
                    break
            del child_map[key]
            if not child_map:
                parent.remove()