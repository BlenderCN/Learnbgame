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

import bmesh
import bpy
import mathutils
import math
from . import Utils
from . import GenUtils
from . import GenLayout


class ParamsPillar:
    # horizontal separator: bool which defines whether or not to include the horizontal separator in the pillar profile
    # offset_size - size of the offset
    # offset - position of the offset
    def __init__(self, pillar_width, pillar_depth, pillar_chamfer, pillar_offset_height,
                 pillar_offset_size, pillar_include_floor_separator, pillar_include_first_floor):
        self.pillar_width = pillar_width
        self.pillar_depth = pillar_depth
        self.pillar_chamfer = pillar_chamfer
        self.pillar_offset_height = pillar_offset_height
        self.pillar_offset_size = pillar_offset_size
        self.pillar_include_floor_separator = pillar_include_floor_separator
        self.pillar_include_first_floor = pillar_include_first_floor
    # end __init__

    @staticmethod
    def from_ui():
        properties = bpy.context.scene.PBGPropertyGroup
        params = ParamsPillar(
            properties.pillar_width,
            properties.pillar_depth,
            properties.pillar_chamfer,
            properties.pillar_offset_height,
            properties.pillar_offset_size,
            properties.pillar_include_floor_separator,
            properties.pillar_include_first_floor,
        )
        return params
    # end from_ui
# end ParamsPillar


class ParamsWalls:
    def __init__(self, wall_type, wall_mortar_size, wall_section_size, wall_row_count, wall_offset_size,
                 wall_offset_type, wall_offset_mortar_size, wall_offset_section_size, wall_offset_row_count):
        self.wall_type = wall_type
        self.wall_mortar_size = wall_mortar_size
        self.wall_section_size = wall_section_size
        self.wall_row_count = wall_row_count
        self.wall_offset_size = wall_offset_size
        self.wall_offset_type = wall_offset_type
        self.wall_offset_mortar_size = wall_offset_mortar_size
        self.wall_offset_section_size = wall_offset_section_size
        self.wall_offset_row_count = wall_offset_row_count
    # end init

    @staticmethod
    def from_ui():
        properties = bpy.context.scene.PBGPropertyGroup
        params = ParamsWalls(
            properties.wall_type,
            properties.wall_mortar_size,
            properties.wall_section_size,
            properties.wall_row_count,
            properties.wall_offset_size,
            properties.wall_offset_type,
            properties.wall_offset_mortar_size,
            properties.wall_offset_section_size,
            properties.wall_offset_row_count
        )
        return params
    # end from_ui
# end ParamsWalls


class ParamsWindowsUnder:
    def __init__(self, windows_under_type: str, windows_under_width: float, windows_under_height: float,
                 windows_under_depth: float, windows_under_inset_depth: float, windows_under_amplitude: float,
                 windows_under_period_count: int, windows_under_simple_width: float, windows_under_simple_depth: float,
                 windows_under_pillar_base_diameter: float, windows_under_pillar_base_height: float,
                 windows_under_pillar_min_diameter: float, windows_under_pillar_max_diameter: float):
        self.windows_under_type = windows_under_type
        self.windows_under_width = windows_under_width
        self.windows_under_height = windows_under_height
        self.windows_under_depth = windows_under_depth
        self.windows_under_inset_depth = windows_under_inset_depth
        self.windows_under_amplitude = windows_under_amplitude
        self.windows_under_period_count = windows_under_period_count
        self.windows_under_simple_width = windows_under_simple_width
        self.windows_under_simple_depth = windows_under_simple_depth
        self.windows_under_pillar_base_diameter = windows_under_pillar_base_diameter
        self.windows_under_pillar_base_height = windows_under_pillar_base_height
        self.windows_under_pillar_min_diameter = windows_under_pillar_min_diameter
        self.windows_under_pillar_max_diameter = windows_under_pillar_max_diameter
    # end __init__

    @staticmethod
    def from_ui():
        properties = bpy.context.scene.PBGPropertyGroup
        params = ParamsWindowsUnder(
            properties.windows_under_type,
            properties.windows_under_width,
            properties.windows_under_height,
            properties.windows_under_depth,
            properties.windows_under_inset_depth,
            properties.windows_under_amplitude,
            properties.windows_under_period_count,
            properties.windows_under_simple_width,
            properties.windows_under_simple_depth,
            properties.windows_under_pillar_base_diameter,
            properties.windows_under_pillar_base_height,
            properties.windows_under_pillar_min_diameter,
            properties.windows_under_pillar_max_diameter
        )
        return params
    # end from_ui
# end ParamsWindowsUnder


def gen_mesh_floor_separator(context: bpy.types.Context, footprint: list, section_mesh: bpy.types.Mesh) \
        -> bpy.types.Object:
    """
        Creates the floor separator object
        floor separator will be placed at the origin (0, 0, 0)
    Args:
        context: bpy.types.Context
        footprint: list(tuple(x,y,z)) - building footprint
        section_mesh: cross section/side profile of the separator
    Returns:
        bpy.types.Object - single separator object placed at origin
    """

    # extrude the section along the footprint to create the separator
    m = Utils.extrude_along_edges(section_mesh, footprint, True)

    # create a new object, link it to the scene and return it
    obj = bpy.data.objects.new("PBGFloorSeparator", m)
    context.scene.objects.link(obj)
    return obj
# end gen_mesh_floor_separator


def gen_mesh_pillar(context: bpy.types.Context, params_pillar: ParamsPillar, params_general: GenLayout.ParamsGeneral,
                    floor_separator_mesh) -> bpy.types.Object:
    """
        Creates the pillar object
        pillar will be placed ar the origin (0, 0, 0)
    Args:
        context: bpy.types.Context
        params_pillar: instance of the ParamsPillar class
        params_general: instance of the ParamsGeneral class
        floor_separator_mesh: cross section/side profile of the separator
    Returns:
        Pillar object
    """
    bm = bmesh.new()

    if params_pillar.pillar_include_floor_separator:
        # add separator section mesh to bmesh and move it to the appropriate place (up on Z)
        bm.from_mesh(floor_separator_mesh)
        vec_trans = (0.0, 0.0, params_general.floor_height - params_general.separator_height)
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.translate(bm, vec=vec_trans, verts=bm.verts, space=mat_loc)
    else:
        # we don't have a separator mesh, add a straight line
        m = bpy.data.meshes.new(name="PBGPillarSeparatorSection")
        verts = list()
        edges = list()
        verts.append((0.0, 0.0, params_general.floor_height - params_general.separator_height))
        verts.append((0.0, 0.0, params_general.floor_height))
        edges.append((0, 1))
        m.from_pydata(verts, edges, [])
        bm.from_mesh(m)
    # end if

    if params_pillar.pillar_offset_size > 0:
        # generate a pillar_section mesh
        pillar_offset_params = GenUtils.ParamsSectionFactory.horizontal_separator_params_large()
        pillar_offset_section = GenUtils.gen_section_element_list(pillar_offset_params)
        pillar_offset_mesh = GenUtils.gen_section_mesh(pillar_offset_section, params_pillar.pillar_offset_size,
                                                       params_pillar.pillar_offset_size)
        # add it to new bmesh
        bm_offset = bmesh.new()
        bm_offset.from_mesh(pillar_offset_mesh)

        # remove last vertex
        bm_offset.verts.ensure_lookup_table()
        last_vert = bm_offset.verts[len(bm_offset.verts) - 1]
        bm_offset.verts.remove(last_vert)

        # move up on Z, and on -Y for offset.
        vec_trans = (0.0, -params_pillar.pillar_offset_size, params_general.floor_height -
                     params_general.separator_height - params_pillar.pillar_offset_size)
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.translate(bm_offset, vec=vec_trans, verts=bm_offset.verts, space=mat_loc)

        # duplicate, flip and move down
        mat_loc = mathutils.Matrix.Translation((0.0, params_pillar.pillar_offset_size, - params_general.floor_height +
                                                params_general.separator_height +
                                                params_pillar.pillar_offset_size))
        geom_to_duplicate = bm_offset.verts[:] + bm_offset.edges[:] + bm_offset.faces[:]
        ret_dup = bmesh.ops.duplicate(bm_offset, geom=geom_to_duplicate)
        verts_to_transform = [ele for ele in ret_dup["geom"] if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.scale(bm_offset, vec=(1.0, 1.0, -1.0), space=mat_loc, verts=verts_to_transform)
        z_dist = (params_general.floor_height - params_general.separator_height -
                  params_pillar.pillar_offset_height - 2 * params_pillar.pillar_offset_size)
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.translate(bm_offset, vec=(0.0, 0.0, - z_dist), verts=verts_to_transform, space=mat_loc)

        # add filler between the two sections and below the lower section
        m_filler = bpy.data.meshes.new("PBGPillarFiller")
        m_filler_verts = list()
        m_filler_edges = list()
        m_filler_verts.append((0.0, 0.0, 0.0))
        m_filler_verts.append((0.0, 0.0, params_pillar.pillar_offset_height))
        m_filler_edges.append((0, 1))
        m_filler_verts.append((0.0, -params_pillar.pillar_offset_size,
                               params_pillar.pillar_offset_height + params_pillar.pillar_offset_size))
        m_filler_verts.append((0.0, -params_pillar.pillar_offset_size, params_general.floor_height -
                               params_general.separator_height - params_pillar.pillar_offset_size))
        m_filler_edges.append((2, 3))
        m_filler.from_pydata(m_filler_verts, m_filler_edges, [])

        # add the filler to bmesh
        bm_offset.from_mesh(m_filler)

        # bmesh to mesh and append to existing bmesh
        m_offset = bpy.data.meshes.new("PBGPillarMesh")
        bm_offset.to_mesh(m_offset)
        bm_offset.free()
        bm.from_mesh(m_offset)
    else:
        m = bpy.data.meshes.new("PBGPillarMesh")
        mesh_filler_verts = list()
        mesh_filler_edges = list()
        mesh_filler_verts.append((0.0, 0.0, 0.0))
        mesh_filler_verts.append((0.0, 0.0, params_general.floor_height - params_general.separator_height))
        mesh_filler_edges.append((0, 1))
        m.from_pydata(mesh_filler_verts, mesh_filler_edges, [])
        bm.from_mesh(m)
    # end if

    # remove doubles before extruding
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    # create the horizontal layout for extruding along
    layout = list()
    layout.append((-0.5 * params_pillar.pillar_width, 0.0, 0.0))
    if params_pillar.pillar_chamfer > 0:
        layout.append((-0.5 * params_pillar.pillar_width,
                       params_pillar.pillar_depth - params_pillar.pillar_chamfer, 0.0))
        layout.append((-0.5 * params_pillar.pillar_width + params_pillar.pillar_chamfer,
                       params_pillar.pillar_depth, 0.0))
        layout.append((0.5 * params_pillar.pillar_width - params_pillar.pillar_chamfer,
                       params_pillar.pillar_depth, 0.0))
        layout.append((0.5 * params_pillar.pillar_width,
                       params_pillar.pillar_depth - params_pillar.pillar_chamfer, 0.0))
    else:
        layout.append((-0.5 * params_pillar.pillar_width, params_pillar.pillar_depth, 0.0))
        layout.append((0.5 * params_pillar.pillar_width, params_pillar.pillar_depth, 0.0))
    # end if
    layout.append((0.5 * params_pillar.pillar_width, 0.0, 0.0))

    # convert to mesh, extrude along, free bmesh
    m = bpy.data.meshes.new("PBGPillarSection")
    bm.to_mesh(m)
    bm.free()
    m_pillar_extruded = Utils.extrude_along_edges(m, layout, False)

    # create object and link it to the scene, return the object
    obj = bpy.data.objects.get("PBGPillar")
    if obj is not None:
        context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    obj = bpy.data.objects.new("PBGPillar", m_pillar_extruded)
    context.scene.objects.link(obj)
    return obj
# end generate_pillars


def gen_mesh_wall(context: bpy.types.Context, wall_loops: list, section_mesh: bpy.types.Mesh) -> bpy.types.Object:
    """
    Creates the wall object
    All walls will be generated, and there is no need to duplicate/move them
    Args:
        context: bpy.types.Context
        wall_loops: list(list(tuple(x,y,z))) - list of wall loops, result of gen_layout.
        section_mesh: cross section/side profile of the wall
    Returns:
        The wall object
    """

    bm = bmesh.new()
    for loop in wall_loops:
        mesh = Utils.extrude_along_edges(section_mesh.copy(), loop, False)
        bm.from_mesh(mesh)
    # end for

    # check if the object for walls already exists
    obj = bpy.data.objects.get("PBGWalls")
    if obj is not None:
        context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    # end if

    m = bpy.data.meshes.new("PBGWall")
    bm.to_mesh(m)
    bm.free()

    # link the created object to the scene
    obj = bpy.data.objects.new("PBGWalls", m)
    context.scene.objects.link(obj)
    return obj
# end gen_mesh_walls


def gen_mesh_offset_wall(context: bpy.types.Context, footprint: list, params_general: GenLayout.ParamsGeneral,
                         params_walls: ParamsWalls) -> bpy.types.Object:
    """
    Generate Floor offset wall object
    Args:
        context: bpy.types.Context
        footprint: list(tuple(x,y,z)) - building footprint
        params_general: instance of GenLayout.ParamsGeneral class
        params_walls: instance of paramsWalls class
    Returns:
        the Floor offset wall object
    """
    # generate wall section mesh
    m_section = GenUtils.gen_wall_section_mesh(params_walls.wall_offset_type, params_general.floor_offset,
                                               params_walls.wall_offset_section_size,
                                               params_walls.wall_offset_mortar_size,
                                               params_walls.wall_offset_row_count)
    bm = bmesh.new()
    bm.from_mesh(m_section)

    # offset it on y axis
    vec_trans = mathutils.Vector((0.0, params_walls.wall_offset_size, 0.0))
    mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
    bmesh.ops.translate(bm, vec=vec_trans, verts=bm.verts, space=mat_loc)

    # append the top edge
    verts = list()
    edges = list()
    verts.append((0.0, 0.0, params_general.floor_offset))
    verts.append((0.0, params_walls.wall_offset_size, params_general.floor_offset))
    edges.append((0, 1))
    m_edge = bpy.data.meshes.new("PBGWallOffsetEdge")
    m_edge.from_pydata(verts, edges, [])
    bm.from_mesh(m_edge)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    # convert to mesh, extrude along
    m = bpy.data.meshes.new("PbgWallOffset")
    bm.to_mesh(m)
    bm.free()
    m_extruded = Utils.extrude_along_edges(m, footprint, True)

    # check if the object for walls already exists
    obj = bpy.data.objects.get("PBGOffset")
    if obj is not None:
        context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    # end if

    # link the created object to the scene
    obj = bpy.data.objects.new("PBGOffset", m_extruded)
    context.scene.objects.link(obj)
    return obj
# end gen_mesh_offset_wall


def gen_mesh_windows_under(context: bpy.types.Context, params_general: GenLayout.ParamsGeneral,
                           params_window_under: ParamsWindowsUnder, wall_section_mesh: bpy.types.Mesh):
    # generate the mesh, centered, lowest point at 0
    windows_under_bmesh = bmesh.new()
    if params_window_under.windows_under_type == "WALL":
        # start with the wall mesh
        windows_under_bmesh.from_mesh(wall_section_mesh)

        # bisect it on offset height, remove the outer geometry
        geom = windows_under_bmesh.verts[:] + windows_under_bmesh.edges[:] + windows_under_bmesh.faces[:]
        plane_co = (0.0, 0.0, params_general.window_offset)
        plane_no = (0.0, 0.0, 1.0)
        bmesh.ops.bisect_plane(windows_under_bmesh, geom=geom, clear_outer=True, plane_co=plane_co, plane_no=plane_no)

        # move it on x axis half the width
        vec_trans = (-0.5 * params_general.window_width, 0.0, 0.0)
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.translate(windows_under_bmesh, vec=vec_trans, verts=windows_under_bmesh.verts, space=mat_loc)

        # extrude on x axis, to fill width
        vec_ext = (params_general.window_width, 0.0, 0.0)
        ret_extrude = bmesh.ops.extrude_edge_only(windows_under_bmesh, edges=windows_under_bmesh.edges,
                                                  use_select_history=True)
        verts_to_translate = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.translate(windows_under_bmesh, verts=verts_to_translate, vec=vec_ext, space=mat_loc)
    else:
        # make the cube, it is same for all types (SINE, SIMPLE, PILLARS)
        # first loop, append to bmesh...
        verts = list()
        verts.append((-0.5*params_general.window_width, 0.0, 0.0))
        verts.append((-0.5*params_general.window_width, 0.0, params_general.window_offset))
        verts.append((0.5*params_general.window_width, 0.0, params_general.window_offset))
        verts.append((0.5*params_general.window_width, 0.0, 0.0))
        m = bpy.data.meshes.new("PBGWindowsUnderMesh")
        m.from_pydata(verts, [(0, 1), (1, 2), (2, 3), (3, 0)], [])
        windows_under_bmesh.from_mesh(m)

        # extrude on y forwards
        vec_ext = (0.0, params_window_under.windows_under_depth, 0.0)
        ret_extrude = bmesh.ops.extrude_edge_only(windows_under_bmesh, edges=windows_under_bmesh.edges,
                                                  use_select_history=True)
        verts_to_translate = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMVert)]
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.translate(windows_under_bmesh, verts=verts_to_translate, vec=vec_ext, space=mat_loc)

        # extrude, scale down so it fits the width and height
        scale_x = (params_general.window_width -
                   2*params_window_under.windows_under_width)/params_general.window_width
        scale_z = (params_general.window_offset -
                   2*params_window_under.windows_under_height)/params_general.window_offset
        edges_to_extrude = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMEdge)]
        ret_extrude = bmesh.ops.extrude_edge_only(windows_under_bmesh, edges=edges_to_extrude, use_select_history=True)
        verts_to_scale = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMVert)]
        mat_loc = mathutils.Matrix.Translation((0.0, -params_window_under.windows_under_depth,
                                                -0.5*params_general.window_offset))
        bmesh.ops.scale(windows_under_bmesh, space=mat_loc, verts=verts_to_scale, vec=(scale_x, 0, scale_z))

        # extrude inwards
        edges_to_extrude = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMEdge)]
        ret_extrude = bmesh.ops.extrude_edge_only(windows_under_bmesh, edges=edges_to_extrude, use_select_history=True)
        verts_to_translate = [ele for ele in ret_extrude["geom"] if isinstance(ele, bmesh.types.BMVert)]
        vec_ext = (0.0, -params_window_under.windows_under_inset_depth, 0.0)
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.translate(windows_under_bmesh, verts=verts_to_translate, vec=vec_ext, space=mat_loc)

        # make a face
        bmesh.ops.contextual_create(windows_under_bmesh, geom=ret_extrude["geom"])

        if params_window_under.windows_under_type in {"CYCLOID", "SINE"}:
            period_width = (params_general.window_width
                            - 2*params_window_under.windows_under_width)/params_window_under.windows_under_period_count
            bm = bmesh.new()
            # create a single vert, spin it to make half a circle
            if params_window_under.windows_under_type == "CYCLOID":
                v_co_x = -0.5*params_general.window_width + params_window_under.windows_under_width
                v_co_y = params_window_under.windows_under_depth
                v_co_z = params_window_under.windows_under_height
                bmesh.ops.create_vert(bm, co=(v_co_x, v_co_y, v_co_z))
                geom = bm.verts[:]
                bmesh.ops.spin(bm, geom=geom, angle=math.radians(180), steps=12, axis=(0.0, 0.0, 1.0),
                               cent=(v_co_x + period_width/2, v_co_y, v_co_z))
                sf = (params_window_under.windows_under_amplitude*2)/period_width
                mat_loc = mathutils.Matrix.Translation((0.0, -params_window_under.windows_under_depth, 0.0))
                bmesh.ops.scale(bm, vec=(1.0, sf, 1.0), space=mat_loc, verts=bm.verts)
            else:
                co_start_x = -0.5*params_general.window_width + params_window_under.windows_under_width
                co_y = params_window_under.windows_under_depth - 0.5*params_window_under.windows_under_amplitude
                verts = list()
                edges = list()
                n = 12
                for i in range(0, n+1):
                    v_co_x = co_start_x + period_width*(i/n)
                    v_co_y = co_y + math.sin(2*math.pi*(i/n))*params_window_under.windows_under_amplitude*0.5
                    verts.append((v_co_x, v_co_y, params_window_under.windows_under_height))
                    if i > 0:
                        edges.append((i-1, i))
                # end for
                m = bpy.data.meshes.new("PBGWindowsUnderMeshSine")
                m.from_pydata(verts, edges, [])
                bm.from_mesh(m)
            # end if
            # extrude on z
            ret_ext = bmesh.ops.extrude_edge_only(bm, edges=bm.edges, use_select_history=True)
            verts_to_translate = [ele for ele in ret_ext["geom"] if isinstance(ele, bmesh.types.BMVert)]
            vec_trans = (0.0, 0.0, params_general.window_offset - 2*params_window_under.windows_under_height)
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            bmesh.ops.translate(bm, verts=verts_to_translate, vec=vec_trans, space=mat_loc)

            # duplicate and move on x
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            for i in range(1, params_window_under.windows_under_period_count):
                ret_dup = bmesh.ops.duplicate(bm, geom=geom)
                verts_to_translate = [ele for ele in ret_dup["geom"] if isinstance(ele, bmesh.types.BMVert)]
                bmesh.ops.translate(bm, vec=(i*period_width, 0.0, 0.0), space=mat_loc, verts=verts_to_translate)

            # remove doubles
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

            # append to original bmesh
            sine_cycle_mesh = bpy.data.meshes.new("PBGWindowsUnderMeshSineCycle")
            bm.to_mesh(sine_cycle_mesh)
            bm.free()
            windows_under_bmesh.from_mesh(sine_cycle_mesh)
        elif params_window_under.windows_under_type == "PILLARS":
            # create a single pillar section(quite a lot of work here)
            params = GenUtils.ParamsSectionFactory.horizontal_separator_params_large()
            sequence = GenUtils.gen_section_element_list(params)
            mesh = GenUtils.gen_section_mesh(sequence, params_window_under.windows_under_pillar_base_height,
                                             0.5*params_window_under.windows_under_pillar_base_diameter
                                             - 0.5*params_window_under.windows_under_pillar_min_diameter)
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.verts.ensure_lookup_table()
            last_vert = bm.verts[len(bm.verts) - 1]
            bm.verts.remove(last_vert)

            # move, on y and z, so the middle is on the bottom and goes through the center.
            vec_trans = (0.0, 0.5 * params_window_under.windows_under_pillar_min_diameter,
                         params_general.window_offset - 2 * params_window_under.windows_under_height
                         - params_window_under.windows_under_pillar_base_height)
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            bmesh.ops.translate(bm, vec=vec_trans, space=mat_loc, verts=bm.verts)

            # generate pillar mesh
            verts = list()
            edges = list()
            start_y = vec_trans[1]
            start_z = vec_trans[2]
            end_z = 0.5*params_general.window_offset - params_window_under.windows_under_height
            end_y = 0.5*params_window_under.windows_under_pillar_max_diameter
            dist_z = start_z - end_z
            dist_y = end_y - start_y
            n = 5
            for i in range(0, n+1):
                v_co_z = start_z - (dist_z/n)*i
                v_co_y = start_y + math.sin((0.5*math.pi*i)/n)*dist_y
                verts.append((0.0, v_co_y, v_co_z))
                if i > 0:
                    edges.append((i-1, i))
            # end for
            # append to bmesh
            m = bpy.data.meshes.new("PBGWindowsUnderMeshPillar")
            m.from_pydata(verts, edges, [])
            bm.from_mesh(m)

            # duplicate and mirror
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            ret_dup = bmesh.ops.duplicate(bm, geom=geom)
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, -end_z))
            verts_to_scale = [ele for ele in ret_dup["geom"] if isinstance(ele, bmesh.types.BMVert)]
            bmesh.ops.scale(bm, verts=verts_to_scale, space=mat_loc, vec=(1.0, 1.0, -1.0))

            # remove doubles and spin
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
            geom_spin = bm.verts[:] + bm.edges[:]
            ret_spin = bmesh.ops.spin(bm, geom=geom_spin, angle=math.radians(360), steps=16, axis=(0.0, 0.0, 1.0),
                                      cent=(0.0, 0.0, 0.0))

            # calculate the pillar positions
            width = params_general.window_width - 2*params_window_under.windows_under_width
            pillar_count = int(width/params_window_under.windows_under_pillar_base_diameter)
            total_pillar_width = width/pillar_count

            # duplicate original geometry and translate
            geom_initial = bm.verts[:] + bm.edges[:] + bm.faces[:]
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            for i in range(0, pillar_count):
                v_co_x = -0.5*width + total_pillar_width*(i+0.5)
                ret_dup = bmesh.ops.duplicate(bm, geom=geom_initial)
                verts_to_translate = [ele for ele in ret_dup["geom"] if isinstance(ele, bmesh.types.BMVert)]
                # TODO: fix y coordinate of this trans vector
                v_co_y = 0.5*(params_window_under.windows_under_depth + (params_window_under.windows_under_depth
                                                                         - params_window_under.windows_under_inset_depth))
                vec_trans = (v_co_x, v_co_y, params_window_under.windows_under_height)
                bmesh.ops.translate(bm, vec=vec_trans, verts=verts_to_translate, space=mat_loc)

            # remove original geometry
            bmesh.ops.delete(bm, geom=geom_initial, context=1)

            # append to original bmesh
            pillar_mesh = bpy.data.meshes.new("PBGWindowsUnderMeshPillar")
            bm.to_mesh(pillar_mesh)
            bm.free()
            windows_under_bmesh.from_mesh(pillar_mesh)
        else:
            # create layout for extruding
            layout = list()
            size_x = params_general.window_width - 2*params_window_under.windows_under_width
            size_y = params_general.window_offset - 2*params_window_under.windows_under_height
            layout.append((0.5 * size_x, 0.5 * size_y, 0.0))
            layout.append((-0.5 * size_x, 0.5 * size_y, 0.0))
            layout.append((-0.5 * size_x, -0.5 * size_y, 0.0))
            layout.append((0.5 * size_x, -0.5 * size_y, 0.0))

            # create a section and extrude it in x-y plane
            params = GenUtils.ParamsSectionFactory.horizontal_separator_params_large()
            sequence = GenUtils.gen_section_element_list(params)
            mesh = GenUtils.gen_section_mesh(sequence, params_window_under.windows_under_simple_depth,
                                             params_window_under.windows_under_simple_width)
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.verts.ensure_lookup_table()
            last_vert = bm.verts[len(bm.verts) - 1]
            bm.verts.remove(last_vert)
            bm.to_mesh(mesh)
            extruded = Utils.extrude_along_edges(mesh, layout, True)
            simple_bmesh = bmesh.new()
            simple_bmesh.from_mesh(extruded)

            # create the filler face
            verts = list()
            v_co_x = 0.5 * size_x - params_window_under.windows_under_simple_width
            v_co_y = 0.5 * size_y - params_window_under.windows_under_simple_width
            verts.append((v_co_x, v_co_y, params_window_under.windows_under_simple_depth))
            verts.append((-v_co_x, v_co_y, params_window_under.windows_under_simple_depth))
            verts.append((-v_co_x, -v_co_y, params_window_under.windows_under_simple_depth))
            verts.append((v_co_x, -v_co_y, params_window_under.windows_under_simple_depth))
            m = bpy.data.meshes.new("PBGWindowsUnderMeshSimpleFillFace")
            m.from_pydata(verts, [(0, 1), (1, 2), (2, 3), (3, 0)], [(0, 1, 2, 3)])
            simple_bmesh.from_mesh(m)
            bmesh.ops.remove_doubles(simple_bmesh, verts=simple_bmesh.verts, dist=0.0001)

            # rotate, move and offset on y
            mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
            mat_rot = mathutils.Matrix.Rotation(math.radians(-90), 3, "X")

            # rotate it, move to the desired position, append to main bmesh
            bmesh.ops.rotate(simple_bmesh, cent=(0, 0, 0), matrix=mat_rot, verts=simple_bmesh.verts, space=mat_loc)
            vec_trans = (0.0, params_window_under.windows_under_depth, 0.5*params_general.window_offset)
            bmesh.ops.translate(simple_bmesh, vec=vec_trans, space=mat_loc, verts=simple_bmesh.verts)

            simple_mesh = bpy.data.meshes.new("PBGWindowsUnderMeshSimple")
            simple_bmesh.to_mesh(simple_mesh)
            simple_bmesh.free()
            windows_under_bmesh.from_mesh(simple_mesh)
    # end if

    # recalculate normals
    # TODO: normals are sometimes recalculated differently when height changes while using "WALL" type.
    bmesh.ops.recalc_face_normals(windows_under_bmesh, faces=windows_under_bmesh.faces)

    # convert to mesh and create object
    windows_under_mesh = bpy.data.meshes.new("PBGWindowsUnderMesh")
    windows_under_bmesh.to_mesh(windows_under_mesh)
    windows_under_bmesh.free()
    ob = bpy.data.objects.get("PBGWindowsUnder")
    if ob is not None:
        context.scene.objects.unlink(ob)
        bpy.data.objects.remove(ob)

    # link the created object to the scene
    new_obj = bpy.data.objects.new("PBGWindowsUnder", windows_under_mesh)
    context.scene.objects.link(new_obj)
    return new_obj
# end gen_mesh_windows_under
