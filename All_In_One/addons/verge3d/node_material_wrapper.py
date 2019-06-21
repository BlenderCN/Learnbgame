# Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class NodeMaterialWrapper():
    """
    Wrapper for a node material, capable of overwriting the "node_tree" property.
    Doesn't correspond to the actual node material though.
    """

    def __init__(self, material):
        super().__setattr__('_material', material)
        self.node_tree = None

    def __getattr__(self, attr):
        return getattr(self._material, attr)

    def __setattr__(self, attr, value):
        if attr == 'node_tree':
            super().__setattr__(attr, value)
        else:
            setattr(self._material, attr, value)

    def __getitem__(self, key):
        return self._material[key]

    def __setitem__(self, key, value):
        if key == 'node_tree':
            super()[key] = value
        else:
            self._material[key] = value
