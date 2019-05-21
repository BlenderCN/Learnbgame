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

import mathutils
import bmesh
import math
import bpy


def vec_from_verts(vert_start, vert_end):
    """
    Generates a vector from given two points
    Args:
        vert_start: starting point in 3D space
        vert_end: ending point in 3D space
    Returns:
        mathutils.Vector
    """
    vec = mathutils.Vector((
        vert_end[0] - vert_start[0],
        vert_end[1] - vert_start[1],
        vert_end[2] - vert_start[2]
    ))
    return vec
# end vec_from_verts


def vert_check_intersect(vert, range_start, range_end) -> bool:
    """
    Checks whether a giver vert is located in a rectangle given by two other verts
    Checks in the x-y plane only.
    Order of verts is not important
    Args:
        vert: vert to check
        range_start: first vert that defines the rectangle
        range_end: second vert that defines the rectangle
    Returns:
        bool indicating if the vert intersects
    """
    if (((range_start[0] <= vert[0] <= range_end[0]) or (range_end[0] <= vert[0] <= range_start[0])) and
            ((range_start[1] <= vert[1] <= range_end[1]) or (range_end[1] <= vert[1] <= range_start[1]))):
        return True
    else:
        return False
    # end if
# end vert_check_range


def extrude_along_edges(section_mesh: bpy.types.Mesh, footprint: list, is_loop: bool) -> bpy.types.Mesh:
    """
    Takes a given mesh, and extrudes it along a given list of verts
    Args:
        section_mesh: mesh to be extruded along
        footprint: list of verts (must be ordered) along which the mesh will be extruded
        is_loop: bool, indicating whether to connect first and last vert.
    Returns:
        The extruded mesh.
    """
    # load the section mesh into bmesh
    bm = bmesh.new()
    bm.from_mesh(section_mesh)

    # set initial values
    angle_previous = 0
    scale_previous = 1
    vec_0 = mathutils.Vector((0.0, 1.0, 0.0))
    layout_vert_count = len(footprint)

    # this will get overridden during the first iteration, and it's not used in the first iteration
    geom_initial = bm.verts[:] + bm.edges[:]
    geom_last = bm.verts[:] + bm.edges[:]
    i = 0
    while i < layout_vert_count:
        # calculate the vectors needed to determine the normal vector, used for scaling and rotating the section loop
        if i == 0:
            if is_loop:
                vec_prev = vec_from_verts(footprint[i], footprint[layout_vert_count - 1])
                vec_next = vec_from_verts(footprint[i], footprint[i + 1])
            else:
                vec_next = vec_from_verts(footprint[i], footprint[i + 1])
                vec_prev = vec_from_verts(footprint[i + 1], footprint[i])
            # end if
        elif i == (layout_vert_count - 1):
            if is_loop:
                vec_prev = vec_from_verts(footprint[i], footprint[i-1])
                vec_next = vec_from_verts(footprint[i], footprint[0])
            else:
                vec_prev = vec_from_verts(footprint[i], footprint[i - 1])
                vec_next = vec_from_verts(footprint[i - 1], footprint[i])
            # end if
        else:
            vec_prev = vec_from_verts(footprint[i], footprint[i - 1])
            vec_next = vec_from_verts(footprint[i], footprint[i + 1])
        # end if

        # normalize the vectors
        vec_prev.normalize()
        vec_next.normalize()

        # calculate the angle to use in transformation
        vec_prev.negate()
        vec_next.negate()
        vec_sum = vec_prev + vec_next
        # TODO: this feels really hackish, but works. Should improve this...
        if vec_sum.length == 0:
            angle_desired = vec_0.xy.angle_signed(vec_next.xy) + 0.5*math.pi
        else:
            angle_desired = vec_0.xy.angle_signed(vec_sum.xy, 0)
        # end if

        if -math.pi < vec_next.xy.angle_signed(vec_prev.xy) < 0:
            angle_desired += math.pi
        # end if
        angle_to_transform = angle_previous - angle_desired

        # calculate the scale to use in transformation
        scale_desired = math.fabs(1/(math.cos(math.radians(90) - 0.5 * vec_next.xy.angle_signed(vec_prev.xy))))
        scale_to_transform = scale_desired / scale_previous

        # if it's the first iteration, move the mesh from the center to the first vert position
        # for all other iterations, extrude the mesh to the current vert position
        if i == 0:
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            verts_to_transform = bm.verts
            bmesh.ops.translate(bm, vec=footprint[i], verts=verts_to_transform, space=mat_loc)
        else:
            mat_loc = mathutils.Matrix.Translation((-footprint[i - 1][0], -footprint[i - 1][1],
                                                    -footprint[i - 1][2]))
            vec_extrude = vec_from_verts(footprint[i-1], footprint[i])
            edges_to_extrude = [ele for ele in geom_last if isinstance(ele, bmesh.types.BMEdge)]
            ret_extrude = bmesh.ops.extrude_edge_only(bm, edges=edges_to_extrude, use_select_history=True)
            verts_to_transform = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, verts=verts_to_transform, vec=vec_extrude, space=mat_loc)
            geom_last = ret_extrude["geom"]
        # end if

        # set up location/space matrix and rotation matrix
        mat_loc = mathutils.Matrix.Translation((-footprint[i][0], -footprint[i][1], -footprint[i][2]))
        mat_rot = mathutils.Matrix.Rotation(angle_to_transform, 3, "Z")

        # apply rotation, set the result of the operation as the last geometry to be used in next iteration
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=mat_rot, verts=verts_to_transform, space=mat_loc)

        # apply scale and rotation by chaining bmesh operations.
        bmesh.ops.scale(bm, vec=(scale_to_transform, scale_to_transform, 1), space=mat_loc,
                        verts=verts_to_transform)

        # if this is the last iteration, bridge the loop between first and last section loop
        if (i == layout_vert_count - 1) and is_loop:
            edges_initial = [ele for ele in geom_initial if isinstance(ele, bmesh.types.BMEdge)]
            edges_last = [ele for ele in geom_last if isinstance(ele, bmesh.types.BMEdge)]
            bmesh.ops.bridge_loops(bm, edges=edges_initial+edges_last)

        # set the previous scale and angle variables to be used in the next iteration
        angle_previous = angle_desired
        scale_previous = scale_desired

        # increment counter
        i += 1
    # end while

    # create the mesh and return it
    m = bpy.data.meshes.new("Mesh")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(m)
    bm.free()
    return m
# end generate_horizontal_separator
