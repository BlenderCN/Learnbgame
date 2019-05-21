# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
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
"""Template for blender operators."""

import bpy


class UvOperatorTemplate(bpy.types.Operator):
    """Operator template for uv.

    this class serve as base class for most UV blender operator
    """

    bl_label = "Class Template"

    @classmethod
    def poll(cls, context):
        """Check if 'context' is correct."""
        return not (context.scene.tool_settings.use_uv_select_sync)
