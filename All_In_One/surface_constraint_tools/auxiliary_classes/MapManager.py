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

class MapManager():
    def __init__(self):
        # The map is an association between a domain of vertex indices and the
        # corresponding range of arbitrary values.
        self.map_ = dict() 

    def clip_domain(self, vertex_indices, action):
        # Truncate the map to include only the vertex indices in its domain
        # that intersect with the sequence of supplied vertex indices.
        map_ = self.map_ 
        if action == 'RETAIN':
            vertex_indices = set(self.map_.keys()).difference(vertex_indices)
        elif action != 'DISCARD':
            return None
        for index in vertex_indices:
            if index in map_:
                del map_[index]

    def get_submap(self, vertex_indices, copy = False):
        # Return a portion of the map, the keys of which intersect with the
        # supplied collection of vertex indices.
        map_ = self.map_
        if copy:
            return {
                index : map_[index].copy()
                for index in vertex_indices
                if index in map_
            }
        else:
            return {
                index : map_[index]
                for index in vertex_indices
                if index in map_
            } 

    def update(self, submap):
        # Update the items in the map with the items in the supplied submap
        # over the common domain of the two.
        map_ = self.map_
        for index in submap:
            if index in map_:
                map_[index] = submap[index]

    def reset(self):
        self.__init__() 
