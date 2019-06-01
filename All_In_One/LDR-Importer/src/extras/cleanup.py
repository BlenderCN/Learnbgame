# -*- coding: utf-8 -*-
"""LDR Importer GPLv2 license.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""

import bpy


def main(cur_obj, link_parts):
    """Perform basic model cleanup procedures.

    Actions performed include:
    * Remove doubles
    * Recalculate normals
    * Set part origin
    * Set smooth shading
    * Add 30deg edge split modifier

    @param {Mesh} cur_obj - The individual model to process.
    @param {Boolean} link_parts - True if Linked Parts option is enabled.
    """
    cur_obj.select = True
    bpy.context.scene.objects.active = cur_obj

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Remove doubles and recalculate the normals
        bpy.ops.mesh.remove_doubles(threshold=0.01)
        bpy.ops.mesh.normals_make_consistent()

        # When not linking parts, keep the original origin point
        bpy.ops.object.mode_set(mode='OBJECT')
        if not link_parts:  # noqa
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        # Set smooth shading
        bpy.ops.object.shade_smooth()

    # Add 30 degree edge split modifier to all bricks
    edges = cur_obj.modifiers.new(
        "Edge Split", type='EDGE_SPLIT')
    edges.split_angle = 0.523599
