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

import math
import bpy
import random
import bmesh
import mathutils
from . import Constants


class ParamsSection:
    """
    Params for generate_section() function.

    Note:
        Each attribute is treated as a percentage in range [0,1].
        Limit values indicate the cutoff points[0,1] for generating a certain element

    Attributes:
        s_min_size (float): min size of small element.
        s_max_size (float): max size of small element.
        m_min_size (float): min size of medium element.
        m_max_size (float): max size of medium element.
        l_min_size (float): min size of large element.
        l_max_size (float): max size of large element.
        ss_limit (float): cutoff value for generating a small square element.
        sc_limit (float): cutoff value for generating a small round element. Must be greater than ss_limit.
        ms_limit (float): cutoff value for generating a medium square element. Must be greater than sc_limit.
        mc_limit (float): cutoff value for generating a medium round element. Must be greater than ms_limit.
        ls_limit (float): cutoff value for generating a large square element. Must be equal to 1.
    """

    def __init__(self, s_min_size, s_max_size, m_min_size, m_max_size, l_min_size, l_max_size, ss_limit, sc_limit,
                 ms_limit, mc_limit):
        self.s_min_size = s_min_size
        self.s_max_size = s_max_size
        self.m_min_size = m_min_size
        self.m_max_size = m_max_size
        self.l_min_size = l_min_size
        self.l_max_size = l_max_size
        self.ss_limit = ss_limit
        self.sc_limit = sc_limit
        self.ms_limit = ms_limit
        self.mc_limit = mc_limit
        self.ls_limit = 1
    # end __init__

    # TODO: load params from ui here...
    # TODO: def from_ui(self):
# end GenerateSectionParams


class SectionElement:
    """
    Element of a Section.

    Note:
        Section element holds type of the element(square or circle) and the size as a percentage[0,1]

    Attributes:
        element_type (string in {"round", "square"): type of the element
        width (float): width of the element
        height (float): height of the element
    """
    def __init__(self, element_type: str, width: float, height: float):
        self.element_type = element_type
        self.width = width
        self.height = height
    # end __init__
# end SectionElement


class ParamsSectionFactory:
    # TODO: docstring
    # possibly remove this class and move the generating methods somewhere else?

    @staticmethod
    def horizontal_separator_params():
        params = ParamsSection(
            s_min_size=0.05,
            s_max_size=0.1,
            m_min_size=0.2,
            m_max_size=0.3,
            l_min_size=0.4,
            l_max_size=0.6,
            ss_limit=0.55,
            sc_limit=0.62,
            ms_limit=0.69,
            mc_limit=0.87
        )
        return params
    # end horizontal_separator_params

    @staticmethod
    def horizontal_separator_params_normalized():
        params = ParamsSection(
            s_min_size=0.05,
            s_max_size=0.1,
            m_min_size=0.2,
            m_max_size=0.3,
            l_min_size=0.4,
            l_max_size=0.6,
            ss_limit=0.2,
            sc_limit=0.4,
            ms_limit=0.6,
            mc_limit=0.8
        )
        return params
    # end horizontal_separator_params_normalized

    @staticmethod
    def horizontal_separator_params_large():
        params = ParamsSection(
            s_min_size=0.05,
            s_max_size=0.1,
            m_min_size=0.2,
            m_max_size=0.3,
            l_min_size=0.4,
            l_max_size=0.6,
            ss_limit=0.05,
            sc_limit=0.1,
            ms_limit=0.4,
            mc_limit=0.7
        )
        return params
# GenerateSectionParamsFactory


def gen_section_mesh(sequence: list, height: float, width: float) -> bpy.types.Mesh:
    """
    Generates a mesh from the given list of sectionElements.

    Args:
         sequence (list of SectionElement): a list of SectionElements, to be used for generating the mesh. Likely the
             result of calling the generate_section function.
         height (float): height of the section
         width (float): width of the section

    Returns, bpy.types.Mesh:
        A mesh following the sequence, in Y-Z plane, starting in (0,0,0), with width and height of 1 blender unit.
    """

    verts = list()
    verts.append([0, 0, 0])
    for element in sequence:
        if element.element_type == "square":
            verts.append([0, verts[-1][1]+element.width, verts[-1][2]])
            verts.append([0, verts[-1][1], verts[-1][2]+element.height])
        else:
            # this is where the fun begins
            i = 1
            angle_step = (math.pi/2)/Constants.PROFILE_CIRCLE_PRECISION
            angle = -math.pi/2
            center_y = verts[-1][1]
            center_z = verts[-1][2]+element.height
            while i <= Constants.PROFILE_CIRCLE_PRECISION+1:
                verts.append([0, center_y + element.width*math.cos(angle), center_z + element.height*math.sin(angle)])
                i += 1
                angle += angle_step
            # end while
        # end if
    # end for

    verts.append([0, 0, verts[-1][2]])

    edges = list()
    i = 0
    while i < len(verts)-1:
        edges.append([i, i+1]),
        i += 1
    # end while

    m = bpy.data.meshes.new(name="PBGSection")
    m.from_pydata(verts, edges, [])
    m.update()
    bm = bmesh.new()
    bm.from_mesh(m)

    # scale the mesh so it has the desired width and height.
    mat_loc = mathutils.Matrix.Translation((0, 0, 0))
    bmesh.ops.scale(bm, vec=(1.0, width, height), space=mat_loc, verts=bm.verts)

    bm.to_mesh(m)
    bm.free()
    return m
# end generate_section_mesh


def gen_section_element_list(params_section: ParamsSection) -> list:
    """
    Generates a list of SectionElements based on the supplied params.

    Args:
        params_section (ParamsSection): object containing the parameters

    Returns, list of SectionElement:
        A list of SectionElement objects.
    """
    remaining_width = 1
    remaining_height = 1
    sequence = list()

    # generate first element
    e_width = random.uniform(params_section.s_min_size, params_section.s_max_size)
    e_height = random.uniform(params_section.s_min_size, params_section.s_max_size)
    element = SectionElement("square", e_width, e_height)
    remaining_width -= e_width
    remaining_height -= e_height
    sequence.append(element)

    # generate last element
    e_width = random.uniform(params_section.s_min_size, params_section.s_max_size)
    e_height = random.uniform(params_section.s_min_size, params_section.s_max_size)
    element = SectionElement("square", e_width, e_height)
    remaining_width -= e_width
    remaining_height -= e_height
    sequence.append(element)

    # generate elements until width or height become limiting factor
    # once the generated element can fill either range, it is scaled up to fill that range
    # no matter if the circle element would become distorted as a result.
    while remaining_height > 0 and remaining_width > 0:
        # pick a pseudo-random element while making sure we do not get an element which would be too big
        if remaining_height > params_section.l_min_size:
            rand = random.uniform(0, 1)
        elif remaining_height > params_section.m_min_size:
            rand = random.uniform(0, params_section.mc_limit)
        else:
            rand = random.uniform(0, params_section.sc_limit)
        # end if

        # generate correct element
        if rand < params_section.sc_limit:
            if params_section.s_max_size >= remaining_height or params_section.s_max_size >= remaining_width:
                e_width = remaining_width
                e_height = remaining_height
            else:
                e_width = random.uniform(params_section.s_min_size, params_section.s_max_size)
                e_height = random.uniform(params_section.s_min_size, params_section.s_max_size)
            # end if

            if rand < params_section.ss_limit:
                element = SectionElement("square", e_width, e_height)
            else:
                element = SectionElement("circle", e_width, e_height)
            # end if
        elif rand < params_section.mc_limit:
            if params_section.m_max_size >= remaining_height or params_section.m_max_size >= remaining_width:
                e_width = remaining_width
                e_height = remaining_height
            else:
                e_width = random.uniform(params_section.m_min_size, params_section.m_max_size)
                e_height = random.uniform(params_section.m_min_size, params_section.m_max_size)
            # end if

            if rand < params_section.ms_limit:
                element = SectionElement("square", e_width, e_height)
            else:
                element = SectionElement("circle", e_width, e_height)
            # end if
        else:
            if params_section.l_max_size >= remaining_height or params_section.l_max_size >= remaining_width:
                e_width = remaining_width
                e_height = remaining_height
            else:
                e_width = random.uniform(params_section.l_min_size, params_section.l_max_size)
                e_height = random.uniform(params_section.l_min_size, params_section.l_max_size)
            # end if

            element = SectionElement("square", e_width, e_height)
        # end if

        # update the remaining width and height
        remaining_width -= e_width
        remaining_height -= e_height

        # push the element into the list
        sequence.insert(len(sequence)-1, element)
    # end while
    return sequence
# end generate_section_element_list


def gen_wall_section_mesh(wall_type: str, wall_section_height: float, wall_section_size: float, wall_mortar_size: float,
                          wall_row_count: float) -> bpy.types.Mesh:
    # TODO: docstring
    if wall_type == "FLAT":
        verts = list()
        edges = list()
        verts.append((0.0, 0.0, 0.0))
        verts.append((0.0, 0.0, wall_section_height))
        edges.append((0, 1))
        wall_section_mesh = bpy.data.meshes.new(name="PBGWallSectionMesh")
        wall_section_mesh.from_pydata(verts, edges, [])
    else:
        # generate mesh
        wall_offset_params = ParamsSectionFactory.horizontal_separator_params_large()
        wall_offset_section = gen_section_element_list(wall_offset_params)
        wall_offset_mesh = gen_section_mesh(wall_offset_section, wall_section_size, wall_section_size)
        # append it to new bmesh
        bm = bmesh.new()
        bm.from_mesh(wall_offset_mesh)
        # remove last vert
        bm.verts.ensure_lookup_table()
        last_vert = bm.verts[len(bm.verts) - 1]
        bm.verts.remove(last_vert)
        # move up on Z axis
        vec_trans = (0.0, 0.0, wall_mortar_size)
        bmesh.ops.translate(bm, vec=vec_trans, verts=bm.verts)
        # duplicate, flip and move up on Z
        mat_loc = mathutils.Matrix.Translation((0.0, 0.0, -wall_mortar_size))
        geom_to_duplicate = bm.verts[:] + bm.edges[:] + bm.faces[:]
        ret_dup = bmesh.ops.duplicate(bm, geom=geom_to_duplicate)
        verts_to_transform = [ele for ele in ret_dup["geom"] if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.scale(bm, vec=(1.0, 1.0, -1.0), space=mat_loc, verts=verts_to_transform)
        row_height = wall_section_height / wall_row_count
        vec_trans = (0.0, 0.0, row_height - 2 * wall_mortar_size)
        bmesh.ops.translate(bm, vec=vec_trans, verts=verts_to_transform)

        # create a mesh that fills the gaps...
        verts = list()
        edges = list()
        verts.append((0.0, 0.0, 0.0))
        verts.append((0.0, 0.0, wall_mortar_size))
        edges.append((0, 1))
        verts.append((0.0, 0.0, row_height - wall_mortar_size))
        verts.append((0.0, 0.0, row_height))
        edges.append((2, 3))
        verts.append((0.0, wall_section_size, wall_section_size + wall_mortar_size))
        verts.append((0.0, wall_section_size, row_height - wall_section_size - wall_mortar_size))
        edges.append((4, 5))
        filler_mesh = bpy.data.meshes.new(name="PBGWallSectionMeshFiller")
        filler_mesh.from_pydata(verts, edges, [])
        bm.from_mesh(filler_mesh)

        # duplicate bmesh geometry so it fills the whole floor.
        i = 1
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        while i < wall_row_count:
            ret_dup = bmesh.ops.duplicate(bm, geom=geom)
            verts_to_translate = [ele for ele in ret_dup["geom"] if isinstance(ele, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, verts=verts_to_translate, vec=(0.0, 0.0, row_height))
            geom = ret_dup["geom"]
            i += 1
        # end while

        # remove doubles before converting
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        # convert bmesh geometry to mesh
        wall_section_mesh = bpy.data.meshes.new(name="PBGWallSectionMesh")
        bm.to_mesh(wall_section_mesh)
        bm.free()
    # end if
    return wall_section_mesh
# end gen_wall_section_mesh
