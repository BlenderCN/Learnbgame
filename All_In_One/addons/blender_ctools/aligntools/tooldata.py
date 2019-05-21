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


from mathutils import Matrix

from .localutils.memoize import Memoize

from .va import vamath as vam


class ToolData:
    def __init__(self):
        self.vecs = []
        self.verts = []
        self.plane = vam.PlaneVector()
        self.axis = vam.PlaneVector()
        # self.manipulator_matrix = None
        # """:type: vamanipul.ManipulatorMatrix"""

        self.matrix_a = Matrix.Identity(4)
        self.matrix_b = Matrix.Identity(4)

        self.cache = {}  # ナニカ
        self.memoize = Memoize()

        self.operator = None


tool_data = ToolData()
