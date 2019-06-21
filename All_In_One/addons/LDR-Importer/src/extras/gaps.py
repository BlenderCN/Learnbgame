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


def main(cur_obj, scale_val):
    """Add small, uniform gaps between parts.

    @param {Mesh} cur_obj - The individual model to process.
    @param {Number} scale_val - The amount a model should be scaled up or down.
    """
    bpy.ops.object.select_all(action="DESELECT")
    cur_obj.select = True
    bpy.context.scene.objects.active = cur_obj

    # Compute the scale factor
    gap_width = 0.007
    obj_scale = cur_obj.scale * scale_val
    dim = cur_obj.dimensions

    # Checks whether the object isn't flat in a certain direction
    # to avoid division by zero.
    # Else, the scale factor is set proportional to the inverse of
    # the dimension so that the mesh shrinks a fixed distance
    # (determined by the gap_width and the scale of the object)
    # in every direction, creating a uniform gap.
    scale_fac = {"x": 1, "y": 1, "z": 1}

    if dim.x != 0:
        scale_fac["x"] = 1 - 2 * gap_width * abs(obj_scale.x) / dim.x
    if dim.y != 0:
        scale_fac["y"] = 1 - 2 * gap_width * abs(obj_scale.y) / dim.y
    if dim.z != 0:
        scale_fac["z"] = 1 - 2 * gap_width * abs(obj_scale.z) / dim.z

    bpy.context.object.scale[0] *= scale_fac["x"]
    bpy.context.object.scale[1] *= scale_fac["y"]
    bpy.context.object.scale[2] *= scale_fac["z"]

    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.select_all(action="DESELECT")
