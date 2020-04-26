# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Procedural building generator
#  Copyright (C) 2019 Luka Simic
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . import GenLayout
from . import GenMesh
from . import GenUtils
import time


class Generator(bpy.types.Operator):
    # TODO: docstring

    bl_idname = "pbg.generate_building"
    bl_label = "Generate Building"

    def invoke(self, context, event):
        # generate stuff needed for other functions that generate geometry
        time_start = time.time()
        params_general = GenLayout.ParamsGeneral.from_ui()
        params_section = GenUtils.ParamsSectionFactory.horizontal_separator_params_large()
        params_pillar = GenMesh.ParamsPillar.from_ui()
        params_walls = GenMesh.ParamsWalls.from_ui()
        params_windows_under = GenMesh.ParamsWindowsUnder.from_ui()
        params_footprint = GenLayout.ParamsFootprint.from_ui()
        door_position = ((0.0, 0.5*params_footprint.building_depth+params_footprint.building_wedge_depth,
                          params_general.floor_offset), 0)

        footprint = GenLayout.gen_footprint(params_footprint)
        layout = GenLayout.gen_layout(params_general, footprint, door_position)
        section_element_list = GenUtils.gen_section_element_list(params_section)
        section_mesh = GenUtils.gen_section_mesh(section_element_list, params_general.separator_height,
                                                 params_general.separator_width)
        if params_general.generate_separator == True:
            wall_section_height = params_general.floor_height - params_general.separator_height
        else:
            wall_section_height = params_general.floor_height
        # end if
        wall_section_mesh = GenUtils.gen_wall_section_mesh(params_walls.wall_type, wall_section_height,
                                                           params_walls.wall_section_size,
                                                           params_walls.wall_mortar_size,
                                                           params_walls.wall_row_count)

        # generate geometry
        if params_general.generate_separator == True:
            obj_separator = GenMesh.gen_mesh_floor_separator(context, footprint, section_mesh.copy())
            separator_positions = list()
            for i in range(0, params_general.floor_count+1):
                separator_positions.append(((0, 0, params_general.floor_offset + wall_section_height +
                                            i*params_general.floor_height), 0))
            apply_positions(obj_separator, separator_positions)
            bpy.data.objects.remove(obj_separator, do_unlink=True)
        # end if
        GenMesh.gen_mesh_wall(context, layout["wall_loops"], wall_section_mesh.copy())
        GenMesh.gen_mesh_offset_wall(context, footprint, params_general, params_walls)
        obj_window_under = GenMesh.gen_mesh_windows_under(context, params_general, params_windows_under, wall_section_mesh)
        apply_positions(obj_window_under, layout["window_positions"])
        bpy.data.objects.remove(obj_window_under, do_unlink=True)

        if params_general.generate_pillar == True:
            obj_pillar = GenMesh.gen_mesh_pillar(context, params_pillar, params_general, section_mesh.copy())
            apply_positions(obj_pillar, layout["pillar_positions"])
            bpy.data.objects.remove(obj_pillar, do_unlink=True)
        # end if
        time_end = time.time()
        print(time_end - time_start)
        return {"FINISHED"}
    # end invoke
# end Generator


def apply_positions(obj: bpy.types.Object, positions: list):
    """
        Duplicates (linked duplicate) the given object onto the given positions
        applies the given rotation
    Args:
        obj: object to duplicate, origin should be in (0, 0, 0)
        positions: list(tuple(tuple(x,y,z), rot)) - object positions and rotations
    Returns:

    """
    for position in positions:
        dup = obj.copy()
        # move it
        dup.location.x = position[0][0]
        dup.location.y = position[0][1]
        dup.location.z = position[0][2]
        # rotate it
        dup.rotation_euler.z = position[1]
        # link it to the scene
        bpy.context.scene.objects.link(dup)
# end apply_positions
