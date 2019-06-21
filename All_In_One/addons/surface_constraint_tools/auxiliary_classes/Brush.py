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

from mathutils import Matrix, Vector

class Brush():
    def __init__(self):
        # Transform Attributes
        self.center = Vector()
        self.normal = Vector()
        self.radius = float()
        self.transformation_matrix = Matrix.Identity(4)

        # Influence Attributes
        self.indices = dict()
        self.falloff_map = dict()
        self.color_map = dict()

        # Relational Attribute
        self.is_on_mesh = False

    def reset_influence(self):
        self.indices = dict()
        self.falloff_map = dict()
        self.color_map = dict()