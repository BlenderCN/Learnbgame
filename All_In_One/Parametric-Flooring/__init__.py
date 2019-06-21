# -*- coding:utf-8 -*-

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

# <pep8 compliant>

# ----------------------------------------------------------
# Blender Parametric object skeleton
# Author: Stephen Leger (s-leger)
# ----------------------------------------------------------

bl_info = {
    'name': 'Floor',
    'description': 'Floor parametric object',
    'author': 's-leger, Jacob Morris',
    'license': 'GPL',
    'version': (1, 0, 0),
    'blender': (2, 7, 8),
    'location': 'View3D > Tools > Sample',
    'warning': '',
    'wiki_url': 'https://github.com/BlendingJake/Parametric-Flooring-for-Blender-3D/wiki',
    'tracker_url': 'https://github.com/BlendingJake/Parametric-Flooring-for-Blender-3D/issues',
    'link': 'hhttps://github.com/BlendingJake/Parametric-Flooring-for-Blender-3D',
    'support': 'COMMUNITY',
    "category": "Learnbgame",
    }


import bpy
from bpy.types import Operator, PropertyGroup, Mesh, Panel
from bpy.props import FloatProperty, CollectionProperty, BoolProperty, IntProperty, EnumProperty
from mathutils import Vector
from random import uniform
from math import radians, cos, sin, atan
from .bmesh_utils import BmeshEdit as BmeshHelper
from .simple_manipulator import Manipulable
import bmesh

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

FOOT = 0.3048  # 1 foot in meters
INCH = 0.0254  # 1 inch in meters
EQUAL, NOT_EQUAL, LESS_EQUAL, GREATER_EQUAL, LESS, GREATER = [i for i in range(6)]
SLOP = 0.001  # amount of wiggle room in rough_comp

# ------------------------------------------------------------------
# Define property class to store object parameters and update mesh
# ------------------------------------------------------------------


def update(self, context):
    if self.auto_update:
        self.update(context)


class archipack_floor(Manipulable, PropertyGroup):
    # keep track of data
    vs, fs = [], []  # vertices and faces
    ms, us = [], []  # mat ids and uvs
    uv_factor = 1  # uv scale factor

    auto_update = BoolProperty(
        name="Auto Update Mesh", default=True, update=update,
        description="Automatically update the mesh whenever a parameter is changed"
    )

    # pattern
    pattern = EnumProperty(
        name='Floor Pattern', items=(("boards", "Boards", ""), ("square_parquet", "Square Parquet", ""),
                                     ("herringbone_parquet", "Herringbone Parquet", ""),
                                     ("herringbone", "Herringbone", ""), ("regular_tile", "Regular Tile", ""),
                                     ("hopscotch", "Hopscotch", ""), ("stepping_stone", "Stepping Stone", ""),
                                     ("hexagon", "Hexagon", ""), ("windmill", "Windmill", "")),
        default="boards", update=update
    )

    # overall length and width
    width = FloatProperty(  # x
        name='Width',
        min=2*FOOT, soft_max=100*FOOT,
        default=20*FOOT, precision=2,
        description='Width', update=update,
        subtype="DISTANCE"
    )
    length = FloatProperty(  # y
        name='Length',
        min=2*FOOT, soft_max=100*FOOT,
        default=8*FOOT, precision=2,
        description='Length', update=update,
        subtype="DISTANCE"
    )

    # generic spacing
    spacing = FloatProperty(
        name='Spacing', unit='LENGTH', min=0, soft_max=1 * INCH,
        default=0.125 * INCH, precision=2, update=update,
        description='The amount of space between boards or tiles in both directions'
    )

    # general thickness
    thickness = FloatProperty(  # z
        name='Thickness',
        min=0.25*INCH, soft_max=2*INCH,
        default=1*INCH, precision=2,
        description='Thickness', update=update,
        subtype="DISTANCE"
    )
    vary_thickness = BoolProperty(
        name='Vary Thickness', update=update, default=False,
        description='Vary board thickness?'
    )
    thickness_variance = FloatProperty(
        name='Thickness Variance', min=0, max=100, subtype='PERCENTAGE',
        default=25, update=update, precision=2,
        description='How much board thickness can vary by'
    )

    # board width, variance, and spacing
    board_width = FloatProperty(
        name='Board Width', unit='LENGTH', min=2*INCH,
        soft_max=2*FOOT, default=6*INCH, update=update,
        description='The width of the boards', precision=2
    )
    vary_width = BoolProperty(
        name='Vary Width', default=False,
        description='Vary board width?', update=update
    )
    width_variance = FloatProperty(
        name='Width Variance', subtype='PERCENTAGE',
        min=1, max=100, default=50, description='How much board width can vary by',
        precision=2, update=update
    )
    width_spacing = FloatProperty(
        name='Width Spacing', unit='LENGTH', min=0, soft_max=1*INCH,
        default=0.125*INCH, precision=2, update=update,
        description='The amount of space between boards in the width direction'
    )

    # board length
    board_length = FloatProperty(
        name='Board Length', unit='LENGTH', min=2*FOOT,
        soft_max=100*FOOT, default=8*FOOT, update=update,
        description='The length of the boards', precision=2
    )
    short_board_length = FloatProperty(
        name='Board Length', unit='LENGTH', min=6*INCH,
        soft_max=4*FOOT, default=2*FOOT, update=update,
        description='The length of the boards', precision=2
    )
    vary_length = BoolProperty(
        name='Vary Length', default=False,
        description='Vary board length?', update=update
    )
    length_variance = FloatProperty(
        name='Length Variance', subtype='PERCENTAGE',
        min=1, max=100, default=50, description='How much board length can vary by',
        precision=2, update=update
    )
    max_boards = IntProperty(
        name='Max Boards', min=1, soft_max=10, default=2,
        update=update, description='Max number of boards in one row'
    )
    length_spacing = FloatProperty(
        name='Length Spacing', unit='LENGTH', min=0, soft_max=1*INCH,
        default=0.125*INCH, precision=2, update=update,
        description='The amount of space between boards in the length direction'
    )

    # parquet specific
    boards_in_group = IntProperty(
        name='Boards in Group', min=1, soft_max=10, default=4,
        update=update, description='Number of boards in a group'
    )

    # tile specific
    tile_width = FloatProperty(
        name='Tile Width', min=2*INCH, soft_max=2*FOOT, default=1*FOOT,
        update=update, precision=2, description='Width of the tiles', unit='LENGTH',
    )
    tile_length = FloatProperty(
        name='Tile Length', min=2*INCH, soft_max=2*FOOT, default=8*INCH,
        update=update, precision=2, description='Length of the tiles', unit='LENGTH',
    )

    # grout
    add_grout = BoolProperty(
        name='Add Grout', default=False, description='Add grout', update=update
    )
    mortar_depth = FloatProperty(
        name='Mortar Depth', min=0, soft_max=1*INCH, default=0.25*INCH,
        update=update, precision=2, unit='LENGTH', step=0.005,
        description='The depth of the mortar from the surface of the tile'
    )

    # regular tile
    random_offset = BoolProperty(
        name='Random Offset', update=update, default=False,
        description='Random amount of offset for each row of tiles'
    )
    offset = FloatProperty(
        name='Offset', update=update, min=0, max=100, default=0,
        precision=2, description='How much to offset each row of tiles'
    )
    offset_variance = FloatProperty(
        name='Offset Variance', update=update, min=0.001, max=100, default=50,
        precision=2, description='How much to vary the offset each row of tiles'
    )

    # UV stuff
    random_uvs = BoolProperty(
        name='Random UV\'s', update=update, default=True, description='Random UV positions for the faces'
    )

    # bevel
    bevel = BoolProperty(
        name='Bevel', update=update, default=False, description='Bevel upper faces'
    )
    bevel_amount = FloatProperty(
        name='Bevel Amount', update=update, unit='LENGTH', min=0.0001, max=0.005, default=0.001,
        description='Bevel amount', precision=2, step=0.0005
    )

    @staticmethod
    def append_all(v_list, add):
        for i in add:
            v_list.append(i)

    @staticmethod
    def create_uv_seams(bm):
        handled = set()
        for edge in bm.edges:
            if edge.verts[0].co.z == 0 and edge.verts[1].co.z == 0:  # bottom
                # make sure both vertices on the edge haven't been handled, this forces one edge to not be made a seam
                # leaving the bottom face still attached
                if not (edge.verts[0].index in handled and edge.verts[1].index in handled):
                    edge.seam = True
                    handled.add(edge.verts[0].index)
                    handled.add(edge.verts[1].index)
            elif edge.verts[0].co.z != edge.verts[1].co.z:  # not horizontal, so they are vertical seams
                edge.seam = True

    @staticmethod
    def rotate_point(point, pivot, angle, units="DEGREES"):
        if units == "DEGREES":
            angle = radians(angle)

        x, y = point[0] - pivot[0], point[1] - pivot[1]
        new_x = (x * cos(angle)) - (y * sin(angle))
        new_y = (x * sin(angle)) - (y * cos(angle))

        return new_x + pivot[0], new_y + pivot[1]

    # ---------------------------------------------------
    # Patterns
    # ---------------------------------------------------

    def regular_tile(self):
        """
         ____  ____  ____
        |    ||    ||    | Regular tile, rows can be offset, either manually or randomly
        |____||____||____|
           ____  ____  ____
          |    ||    ||    |
          |____||____||____| 
        """
        off = False
        o = 1 / (100 / self.offset) if self.offset != 0 else 0
        cur_y = 0.0

        while cur_y < self.length:
            cur_x = 0.0
            tl2 = self.tile_length
            if cur_y < self.length < cur_y + self.tile_length:
                tl2 = self.length - cur_y

            while cur_x < self.width:
                tw2 = self.tile_width

                if cur_x < self.width < cur_x + self.tile_width:
                    tw2 = self.width - cur_x
                elif cur_x == 0.0 and off and not self.random_offset:
                    tw2 = self.tile_width * o
                elif cur_x == 0.0 and self.random_offset:
                    v = self.tile_width * self.offset_variance * 0.0049
                    tw2 = uniform((self.tile_width / 2) - v, (self.tile_width / 2) + v)

                self.add_plane(cur_x, cur_y, tw2, tl2)
                cur_x += tw2 + self.spacing

            cur_y += tl2 + self.spacing
            off = not off

    def hopscotch(self):
        """
         ____  _  Large tile, plus small one on top right corner
        |    ||_|
        |____| ____  _  But shifted up so next large one is right below previous small one
              |    ||_|
              |____| 
        """
        cur_y = 0
        sp = self.spacing

        # movement variables
        row = 0

        tw = self.tile_width
        tl = self.tile_length
        s_tw = (tw - sp) / 2  # small tile width
        s_tl = (tl - sp) / 2  # small tile length

        pre_y = cur_y
        while cur_y < self.length or (row == 2 and cur_y - s_tl - sp < self.length):
            cur_x = 0
            step_back = True

            if row == 1:  # row start indented slightly
                cur_x = s_tw + sp

            while cur_x < self.width:
                if row == 0 or row == 1:
                    # adjust for if there is a need to cut off the bottom of the tile
                    if cur_y < 0:
                        self.add_plane(cur_x, 0, tw, tl + cur_y)  # large one
                    else:
                        self.add_plane(cur_x, cur_y, tw, tl)  # large one

                    self.add_plane(cur_x + tw + sp, cur_y + s_tl + sp, s_tw, s_tl)  # small one

                    if step_back:
                        cur_x += tw + sp
                        cur_y -= s_tl + sp
                    else:
                        cur_x += tw + s_tw + 2*sp
                        cur_y += s_tl + sp

                    step_back = not step_back
                else:
                    if cur_x == 0:  # half width for starting position
                        self.add_plane(cur_x, cur_y, s_tw, tl)  # large one
                        # small one on right
                        self.add_plane(cur_x + s_tw + sp, cur_y + s_tl + sp, s_tw, s_tl)
                        # small one on bottom
                        self.add_plane(cur_x, cur_y - sp - s_tl, s_tw, s_tl)
                        cur_x += (2 * s_tw) + tw + (3 * sp)
                    else:
                        self.add_plane(cur_x, cur_y, tw, tl)  # large one
                        # small one on right
                        self.add_plane(cur_x + tw + sp, cur_y + s_tl + sp, s_tw, s_tl)
                        cur_x += (2 * tw) + (3*sp) + s_tw

            if row == 0 or row == 2:
                cur_y = pre_y + tl + sp
            else:
                cur_y = pre_y + s_tl + sp
            pre_y = cur_y

            row = (row + 1) % 3  # keep wrapping rows

    def stepping_stone(self):
        """
         ____  __  ____
        |    ||__||    | Row of large one, then two small ones stacked beside it
        |    | __ |    |
        |____||__||____|
         __  __  __  __
        |__||__||__||__| Row of smalls
        """
        sp = self.spacing
        cur_y = 0.0
        row = 0

        tw = self.tile_width
        tl = self.tile_length
        s_tw = (tw - sp) / 2
        s_tl = (tl - sp) / 2

        while cur_y < self.length:
            cur_x = 0

            while cur_x < self.width:
                if row == 0:  # large one then two small ones stacked beside it
                    self.add_plane(cur_x, cur_y, tw, tl)
                    self.add_plane(cur_x + tw + sp, cur_y, s_tw, s_tl,)
                    self.add_plane(cur_x + tw + sp, cur_y + s_tl + sp, s_tw, s_tl)
                    cur_x += tw + s_tw + (2 * sp)
                else:  # row of small ones
                    self.add_plane(cur_x, cur_y, s_tw, s_tl)
                    self.add_plane(cur_x + s_tw + sp, cur_y, s_tw, s_tl)
                    cur_x += tw + sp

            if row == 0:
                cur_y += tl + sp
            else:
                cur_y += s_tl + sp

            row = (row + 1) % 2

    def hexagon(self):
        """
          __  Hexagon tiles
        /   \
        \___/ 
        """
        sp = self.spacing
        width = self.tile_width
        dia = (width / 2) / cos(radians(30))
        #               top of current, half way up next,    vertical spacing component
        vertical_spacing = dia * (1 + sin(radians(30))) + (sp * sin(radians(60)))  # center of one row to next row
        base_points = [self.rotate_point((dia, 0), (0, 0), ang + 30) for ang in range(0, 360, 60)]

        cur_y = 0
        offset = False
        while cur_y - width / 2 < self.length:  # place tile as long as bottom is still within bounds
            if offset:
                cur_x = width / 2
            else:
                cur_x = -sp / 2

            while cur_x - width / 2 < self.width:  # place tile as long as left is still within bounds
                p = len(self.vs)
                for pt in base_points:
                    self.vs.append((pt[0] + cur_x, pt[1] + cur_y, 0))
                self.fs.append([p] + [i for i in range(len(self.vs) - 1, p, -1)])

                cur_x += width + sp

            cur_y += vertical_spacing
            offset = not offset

    def windmill(self):
        """
         __  ____
        |  ||____| This also has a square one in the middle, totaling 5 tiles per pattern
        |__|   __
         ____ |  |
        |____||__|  
        """
        sp = self.spacing

        tw = self.tile_width
        tl = self.tile_length
        s_tw = (tw - sp) / 2
        s_tl = (tl - sp) / 2

        cur_y = 0
        while cur_y < self.length:
            cur_x = 0

            while cur_x < self.width:
                self.add_plane(cur_x, cur_y, tw, s_tl)  # bottom
                self.add_plane(cur_x + tw + sp, cur_y, s_tw, tl)  # right
                self.add_plane(cur_x + s_tw + sp, cur_y + tl + sp, tw, s_tl)  # top
                self.add_plane(cur_x, cur_y + s_tl + sp, s_tw, tl)  # left
                self.add_plane(cur_x + s_tw + sp, cur_y + s_tl + sp, s_tw, s_tl)  # center

                cur_x += tw + s_tw + (2*sp)
            cur_y += tl + s_tl + (2*sp)

    def boards(self):
        """
        ||| Typical wood boards
        |||
        """
        cur_x = 0.0
        bw, bl = self.board_width, self.board_length

        while cur_x < self.width:
            if self.vary_width:
                v = bw * (self.width_variance / 100) * 0.99
                bw2 = uniform(bw - v, bw + v)
            else:
                bw2 = bw

            if bw2 + cur_x > self.width:
                bw2 = self.width - cur_x
            cur_y = 0.0

            counter = 1
            while cur_y < self.length:
                bl2 = bl
                if self.vary_length:
                    v = bl * (self.length_variance / 100) * 0.99
                    bl2 = uniform(bl - v, bl + v)
                if (counter >= self.max_boards and self.vary_length) or cur_y + bl2 > self.length:
                    bl2 = self.length - cur_y

                self.add_plane(cur_x, cur_y, bw2, bl2)
                cur_y += bl2 + self.length_spacing
                counter += 1

            cur_x += bw2 + self.width_spacing

    def square_parquet(self):
        """
        ||--||-- Alternating groups oriented either horizontally, or forwards and backwards.
        ||--||-- self.spacing is used because it is the same spacing for width and length
        --||--|| Board width is calculated using number of boards and the length.
        --||--||
        """
        cur_x = 0.0
        start_orient_length = True

        # figure board width
        bl = self.short_board_length
        bw = (bl - (self.boards_in_group - 1) * self.spacing) / self.boards_in_group
        while cur_x < self.width:
            cur_y = 0.0
            orient_length = start_orient_length
            while cur_y < self.length:

                if orient_length:
                    start_x = cur_x

                    for i in range(self.boards_in_group):
                        if cur_x < self.width and cur_y < self.length:
                            self.add_plane(cur_x, cur_y, bw, bl)
                            cur_x += bw + self.spacing

                    cur_x = start_x
                    cur_y += bl + self.spacing

                else:
                    for i in range(self.boards_in_group):
                        if cur_x < self.width and cur_y < self.length:
                            self.add_plane(cur_x, cur_y, bl, bw)
                            cur_y += bw + self.spacing

                orient_length = not orient_length

            start_orient_length = not start_orient_length
            cur_x += bl + self.spacing

    def herringbone(self):
        """
        Boards are at 45 degree angle, in chevron pattern, ends are angled 
        """
        width_dif = self.board_width / cos(radians(45))
        x_dif = self.short_board_length * cos(radians(45))
        y_dif = self.short_board_length * sin(radians(45))
        total_y_dif = width_dif + y_dif
        sp_dif = self.spacing / cos(radians(45))

        cur_y = -y_dif
        while cur_y < self.length:
            cur_x = 0

            while cur_x < self.width:
                # left side
                p = len(self.vs)
                self.append_all(
                    self.vs,
                    [(cur_x, cur_y, 0), (cur_x + x_dif, cur_y + y_dif, 0),
                     (cur_x + x_dif, cur_y + total_y_dif, 0), (cur_x, cur_y + width_dif, 0)]
                )
                self.fs.append([p + 3, p + 2, p + 1, p])
                cur_x += x_dif + self.spacing

                # right side
                if cur_x < self.width:
                    p = len(self.vs)
                    self.append_all(
                        self.vs,
                        [(cur_x, cur_y + y_dif, 0), (cur_x + x_dif, cur_y, 0),
                         (cur_x + x_dif, cur_y + width_dif, 0), (cur_x, cur_y + total_y_dif, 0)]
                    )
                    self.fs.append([p + 3, p + 2, p + 1, p])
                    cur_x += x_dif + self.spacing

            cur_y += width_dif + sp_dif  # adjust spacing amount for 45 degree angle

    def herringbone_parquet(self):
        """
        Boards are at 45 degree angle, in chevron pattern, ends are square, not angled
        """
        x_dif = self.short_board_length * cos(radians(45))
        y_dif = self.short_board_length * sin(radians(45))
        y_dif_45 = self.board_width * cos(radians(45))
        x_dif_45 = self.board_width * sin(radians(45))
        total_y_dif = y_dif + y_dif_45

        sp_dif = (self.spacing / cos(radians(45))) / 2  # divide by two since it is used for both x and y
        width_dif = self.board_width / cos(radians(45))

        cur_y = -y_dif
        while cur_y - y_dif_45 < self.length:  # continue as long as bottom left corner is still good
            cur_x = 0
            pre_y = cur_y

            while cur_x - x_dif_45 < self.width:  # continue as long as top left corner is still good
                # left side
                p = len(self.vs)
                self.append_all(
                    self.vs,
                    [(cur_x, cur_y, 0), (cur_x + x_dif, cur_y + y_dif, 0),
                     (cur_x + x_dif - x_dif_45, cur_y + total_y_dif, 0), (cur_x - x_dif_45, cur_y + y_dif_45, 0)]
                )
                self.fs.append([p + 3, p + 2, p + 1, p])
                cur_x += x_dif - x_dif_45 + sp_dif
                cur_y += y_dif - y_dif_45 - sp_dif

                if cur_x < self.width:
                    p = len(self.vs)
                    self.append_all(
                        self.vs,
                        [(cur_x, cur_y, 0), (cur_x + x_dif, cur_y - y_dif, 0),
                         (cur_x + x_dif + x_dif_45, cur_y - y_dif + y_dif_45, 0),
                         (cur_x + x_dif_45, cur_y + y_dif_45, 0)]
                    )
                    self.fs.append([p + 3, p + 2, p + 1, p])
                    cur_x += x_dif + x_dif_45 + sp_dif
                    cur_y -= y_dif - y_dif_45 - sp_dif
                else:  # we didn't place the right board, so step ahead far enough the the while loop for x breaks
                    cur_x = self.width + x_dif_45

            cur_y = pre_y + width_dif + (2*sp_dif)

    # --------------------------------------------------
    # Non-pattern functions
    # --------------------------------------------------

    def add_plane(self, x, y, w, l, clip=True):
        """
        Adds vertices and faces for a place, clip to outer boundaries if clip is True
        :param x: start x position
        :param y: start y position
        :param w: width (in x direction)
        :param l: length (in y direction)
        :param clip: trim back plane to be within length and width  
        """
        # if starting point is greater than bounds, don't even bother
        if clip and (x >= self.width or y >= self.length):
            return

        if clip and x + w > self.width:
            w = self.width - x
        if clip and y + l > self.length:
            l = self.length - y

        p = len(self.vs)
        self.append_all(self.vs, [(x, y, 0), (x + w, y, 0), (x + w, y + l, 0), (x, y + l, 0)])
        self.fs.append([p + 3, p + 2, p + 1, p])

    def add_manipulator(self, name, pt1, pt2, pt3):
        m = self.manipulators.add()
        m.prop1_name = name
        m.set_pts([pt1, pt2, pt3])

    def confirm_materials(self, obj):
        mats = len(obj.data.materials)

        if mats == 0:  # add main material
            mat = bpy.data.materials.new(obj.name + "_floor")
            obj.data.materials.append(mat)
        if (mats == 0 or mats == 1) and self.add_grout:  # add grout
            mat = bpy.data.materials.new(obj.name + "_grout")
            obj.data.materials.append(mat)
        if mats == 2 and not self.add_grout:  # remove grout
            obj.data.materials.pop(1, update_data=True)

    def generate_pattern(self):
        # clear data before refreshing it
        self.vs, self.fs, self.ms, self.us = [], [], [], []
        self.uv_factor = 1 / max(self.width, self.length)  # automatically scale to keep within reasonable bounds

        if self.pattern == "boards":
            self.boards()
        elif self.pattern == "square_parquet":
            self.square_parquet()
        elif self.pattern == "herringbone":
            self.herringbone()
        elif self.pattern == "herringbone_parquet":
            self.herringbone_parquet()
        elif self.pattern == "regular_tile":
            self.regular_tile()
        elif self.pattern == "hopscotch":
            self.hopscotch()
        elif self.pattern == "stepping_stone":
            self.stepping_stone()
        elif self.pattern == "hexagon":
            self.hexagon()
        elif self.pattern == "windmill":
            self.windmill()

    def update_manipulators(self):
        self.manipulators.clear()  # clear every time, add new ones
        self.add_manipulator("length", (0, 0, 0), (0, self.length, 0), (-0.4, 0, 0))
        self.add_manipulator("width", (0, 0, 0), (self.width, 0, 0), (0.4, 0, 0))

        z = self.thickness

        if self.pattern == "boards":
            self.add_manipulator("board_length", (0, 0, z), (0, self.board_length, z), (0.1, 0, z))
            self.add_manipulator("board_width", (0, 0, z), (self.board_width, 0, z), (-0.2, 0, z))
        elif self.pattern == "square_parquet":
            self.add_manipulator("short_board_length", (0, 0, z), (0, self.short_board_length, z), (-0.2, 0, z))
        elif self.pattern in ("herringbone", "herringbone_parquet"):
            dia = self.short_board_length * cos(radians(45))
            dia2 = self.board_width * cos(radians(45))
            self.add_manipulator("short_board_length", (0, 0, z), (dia, dia, z), (0, 0, z))
            self.add_manipulator("board_width", (dia, 0, z), (dia - dia2, dia2, z), (0, 0, z))
        else:
            tl = self.tile_length
            tw = self.tile_width

            if self.pattern in ("regular_tile", "hopscotch", "stepping_stone"):
                self.add_manipulator("tile_width", (0, tl, z), (tw, tl, z), (0, 0, z))
                self.add_manipulator("tile_length", (0, 0, z), (0, tl, z), (0, 0, z))
            elif self.pattern == "hexagon":
                self.add_manipulator("tile_width", (tw / 2 + self.spacing, 0, z), (tw * 1.5 + self.spacing, 0, z),
                                     (0, 0, 0))
            elif self.pattern == "windmill":
                self.add_manipulator("tile_width", (0, 0, z), (tw, 0, 0), (0, 0, z))
                self.add_manipulator("tile_length", (0, tl / 2 + self.spacing, z), (0, tl * 1.5 + self.spacing, z),
                                     (0, 0, z))

    @property
    def verts(self):
        return self.vs

    @property
    def faces(self):
        return self.fs

    @property
    def uvs(self):
        return self.us

    @property
    def matids(self):
        return self.ms

    def update(self, context):

        old = context.active_object

        o, props = ARCHIPACK_PT_floor.params(old)
        if props != self:
            return

        o.select = True
        context.scene.objects.active = o

        self.generate_pattern()  # update vertices and faces
        self.confirm_materials(o)  # update materials
        BmeshHelper.buildmesh(context, o, self.verts, self.faces)

        # needs bisected?
        bisect = self.pattern in ('hexagon', 'herringbone', 'herringbone_parquet')
        for mod in o.modifiers:
            if mod.type == 'BOOLEAN':
                bisect = False

        if bisect:
            BmeshHelper.bissect(context, o, Vector((0, 0, 0)), Vector((0, -1, 0)))  # bottom
            BmeshHelper.bissect(context, o, Vector((0, self.length, 0)), Vector((0, 1, 0)))  # top
            BmeshHelper.bissect(context, o, Vector((0, 0, 0)), Vector((-1, 0, 0)))  # left
            BmeshHelper.bissect(context, o, Vector((self.width, 0, 0)), Vector((1, 0, 0)))  # right

        # create bmesh to edit
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.verts.ensure_lookup_table()

        # extrude
        bmesh.ops.solidify(bm, geom=bm.faces, thickness=1)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # thickness
        faces = []
        for face in bm.faces:
            if face.verts[0].co.z > 0.9:  # the thickness above is one, allow for some rounding error
                # calculate thickness
                if self.vary_thickness:
                    off = 1 / (100 / self.thickness_variance) if self.thickness_variance != 0 else 0
                    v = off * self.thickness
                    z = uniform(self.thickness - v, self.thickness + v)
                else:
                    z = self.thickness

                # apply thickness to every vertex in the face
                for vertex in face.verts:
                    bm.verts[vertex.index].co.z = z

                faces.append(face)

        # bevel if needed
        if self.bevel:
            geometry = []
            for face in faces:
                self.append_all(geometry, face.edges)
                self.append_all(geometry, face.verts)

            bmesh.ops.bevel(bm, geom=geometry, offset=self.bevel_amount, segments=1, profile=0.5)

        # add material id's before adding grout
        for face in bm.faces:
            face.material_index = 0

        # grout
        if self.add_grout:
            # add cube then adjust vertex positions
            grout_geometry = bmesh.ops.create_cube(bm, size=1.0)
            z = self.thickness - self.mortar_depth

            for vertex in grout_geometry['verts']:
                # x
                if vertex.co.x > 0:
                    vertex.co.x = self.width
                elif vertex.co.x < 0:
                    vertex.co.x = 0
                # y
                if vertex.co.y > 0:
                    vertex.co.y = self.length
                elif vertex.co.y < 0:
                    vertex.co.y = 0
                # z
                if vertex.co.z > 0:
                    vertex.co.z = z
                elif vertex.co.z < 0:
                    vertex.co.z = 0

                # material id for grout
                for face in vertex.link_faces:
                    face.material_index = 1

        # create seams
        self.create_uv_seams(bm)

        # free bmesh
        bm.to_mesh(o.data)
        bm.free()

        # unwrap since mesh has now been updated
        if context.mode != "EDIT_MESH":
            bpy.ops.object.editmode_toggle()

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap()
        bpy.ops.mesh.select_all(action='DESELECT')

        if context.mode == "EDIT_MESH":
            bpy.ops.object.editmode_toggle()

        # update manipulators
        self.update_manipulators()

        # restore context
        old.select = True
        context.scene.objects.active = old

# ------------------------------------------------------------------
# Define panel class to show object parameters in ui panel (N)
# ------------------------------------------------------------------


class ARCHIPACK_PT_floor(Panel):
    bl_idname = "ARCHIPACK_PT_floor"
    bl_label = "Floor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Floor'

    def draw(self, context):
        layout = self.layout
        o = context.object

        o, props = ARCHIPACK_PT_floor.params(o)
        if props is None:
            return

        # manipulate
        layout.operator("archipack.floor_manipulate")
        layout.separator()

        layout.prop(props, 'pattern')
        layout.separator()

        # overall measurements
        layout.prop(props, 'width')
        layout.prop(props, 'length')

        # thickness
        layout.separator()
        layout.prop(props, 'thickness')
        layout.prop(props, 'vary_thickness', icon='RNDCURVE')
        if props.vary_thickness:
            layout.prop(props, 'thickness_variance')
        layout.separator()

        if props.pattern == 'boards':
            layout.prop(props, 'board_length')
            layout.prop(props, 'vary_length', icon='RNDCURVE')
            if props.vary_length:
                layout.prop(props, 'length_variance')
                layout.prop(props, 'max_boards')
            layout.separator()

            # width
            layout.prop(props, 'board_width')
            # vary width
            layout.prop(props, 'vary_width', icon='RNDCURVE')
            if props.vary_width:
                layout.prop(props, 'width_variance')
            layout.separator()

            layout.prop(props, 'length_spacing')
            layout.prop(props, 'width_spacing')
            layout.separator()
        elif props.pattern in ('square_parquet', 'herringbone_parquet', 'herringbone'):
            layout.prop(props, 'short_board_length')

            if props.pattern != "square_parquet":
                layout.prop(props, "board_width")
            layout.prop(props, "spacing")

            if props.pattern == 'square_parquet':
                layout.prop(props, 'boards_in_group')
        elif props.pattern in ('regular_tile', 'hopscotch', 'stepping_stone', 'hexagon', 'windmill'):
            # width and length and mortar
            if props.pattern != "hexagon":
                layout.prop(props, "tile_length")
            layout.prop(props, "tile_width")
            layout.prop(props, "mortar_depth")
            layout.separator()

            if props.pattern == "regular":
                layout.prop(props, "random_offset", icon="RNDCURVE")
                if props.random_offset:
                    layout.prop(props, "offset_variance")
                else:
                    layout.prop(props, "offset")

        # grout
        layout.separator()
        layout.prop(props, 'add_grout', icon='MESH_GRID')
        if props.add_grout:
            layout.prop(props, 'mortar_depth')

        # bevel
        layout.separator()
        layout.prop(props, 'bevel', icon='MOD_BEVEL')
        if props.bevel:
            layout.prop(props, 'bevel_amount')

        # uv

        # updating
        layout.separator()
        layout.prop(props, 'auto_update', icon='FILE_REFRESH')
        if not props.auto_update:
            layout.operator('archipack.floor_update')

    @classmethod
    def params(cls, o):
        if cls.filter(o):
            if 'archipack_floor' in o.data:
                return o, o.data.archipack_floor[0]
        return o, None

    @classmethod
    def filter(cls, o):
        try:
            return o.data is not None and bool('archipack_floor' in o.data)
        except:
            return False

    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        return cls.filter(o)

# ------------------------------------------------------------------
# Define operator class to create object
# ------------------------------------------------------------------


class ARCHIPACK_OT_floor(Operator):
    bl_idname = "archipack.floor"
    bl_label = "Floor"
    bl_description = "Floor"
    bl_category = 'Sample'
    bl_options = {'REGISTER', 'UNDO'}

    def create(self, context):
        """
            expose only basic params in operator
            use object property for other params
        """
        m = bpy.data.meshes.new("Floor")
        o = bpy.data.objects.new("Floor", m)

        # attach parametric datablock
        d = m.archipack_floor.add()

        context.scene.objects.link(o)
        # make newly created object active
        o.select = True
        context.scene.objects.active = o
        # create mesh data
        d.update(context)
        return o

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.select_all(action="DESELECT")
            o = self.create(context)
            o.location = context.scene.cursor_location
            # activate manipulators at creation time
            o.select = True
            context.scene.objects.active = o
            bpy.ops.archipack.floor_manipulate()
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Option only valid in Object mode")
            return {'CANCELLED'}

# ------------------------------------------------------------------
# Define operator for manually updating mesh
# ------------------------------------------------------------------


class ARCHIPACK_OT_floor_update(Operator):
    bl_idname = "archipack.floor_update"
    bl_label = "Update Floor"
    bl_description = "Manually update floor"
    bl_category = 'Sample'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return ARCHIPACK_PT_floor.filter(context.active_object)

    def execute(self, context):
        if context.mode == "OBJECT":
            o, props = ARCHIPACK_PT_floor.params(context.object)
            if props is None:
                return

            props.update(context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Option only valid in Object mode")
            return {'CANCELLED'}

# ------------------------------------------------------------------
# Define operator class to manipulate object
# ------------------------------------------------------------------


class ARCHIPACK_OT_floor_manipulate(Operator):
    bl_idname = "archipack.floor_manipulate"
    bl_label = "Manipulate"
    bl_description = "Manipulate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return ARCHIPACK_PT_floor.filter(context.active_object)

    def modal(self, context, event):
        return self.d.manipulable_modal(context, event)

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            o = context.active_object
            self.d = o.data.archipack_floor[0]
            self.d.manipulable_invoke(context)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

# ------------------------------------------------------------------
# Define a panel class to add button on Create panel under regular primitives
# ------------------------------------------------------------------


class TOOLS_PT_parametric_object(Panel):
    bl_label = "ParametricObject"
    bl_idname = "TOOLS_PT_parametric_object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        box = row.box()
        box.label("Objects")
        row = box.row(align=True)
        row.operator("archipack.floor")


def register():
    bpy.utils.register_class(archipack_floor)
    bpy.utils.register_class(ARCHIPACK_OT_floor_manipulate)
    bpy.utils.register_class(ARCHIPACK_OT_floor_update)
    bpy.utils.register_class(ARCHIPACK_OT_floor)
    bpy.utils.register_class(ARCHIPACK_PT_floor)
    bpy.utils.register_class(TOOLS_PT_parametric_object)
    Mesh.archipack_floor = CollectionProperty(type=archipack_floor)


def unregister():
    bpy.utils.unregister_class(archipack_floor)
    bpy.utils.unregister_class(ARCHIPACK_OT_floor_manipulate)
    bpy.utils.unregister_class(ARCHIPACK_OT_floor_update)
    bpy.utils.unregister_class(ARCHIPACK_OT_floor)
    bpy.utils.unregister_class(ARCHIPACK_PT_floor)
    bpy.utils.unregister_class(TOOLS_PT_parametric_object)
    del Mesh.archipack_floor


if __name__ == "__main__":
    register()
