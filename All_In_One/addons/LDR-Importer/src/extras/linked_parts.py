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


__all__ = ("main")


def replace_parts(objects, part, material):
    """
    Replace identical meshes of part/color-combination with a linked version.

    @param {String} part - ID of LDraw part currently being processed.
    @param {String} color - Name of material the part uses.
    """
    mat = bpy.data.materials[material]
    mesh = None

    # For each imported object in the scene check
    # if it matches the given part name.
    for ob in objects:
        if ob.type == "MESH" and ob.name.split(".")[0] == part:
            for slot in ob.material_slots:
                if slot.material == mat:
                    # First occurrence of part, save in mesh.
                    if mesh is None:
                        mesh = ob.data
                    # Following occurrences of part, link to mesh.
                    else:
                        ob.data = mesh
                    ob.select = True
        else:
            ob.select = False

    # Change mesh name in combination of .dat-filename and material.
    if mesh is not None:
        mesh.name = "{0} {1}".format(part, material)


def main(objects):
    """Clean-up design by linking identical parts (mesh/color).

    @param {List} objects - A list of all models in the scene.
    """
    # Generate list of all materials
    colors = [color.name for color in bpy.data.materials]

    # List all unique meshes
    # For example 3002 and 3002.001 are considered equal.
    parts = []
    for part in objects:
        # Find all unique names of meshes, ignoring everything behind the "."
        # and create a list of these names, making sure no double enties occur.
        if part.type == "MESH" and part.name.split(".")[0] not in parts:
            parts.append(part.name.split(".")[0])

    # For each mesh/color combination create a link to a unique mesh.
    for part in parts:
        for color in colors:
            replace_parts(objects, part, color)
