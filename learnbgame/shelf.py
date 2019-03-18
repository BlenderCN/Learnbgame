# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================
import bpy
from mathutils import Vector, Matrix

from math import cos, tan, radians, sin
import random

from .book import Book


class Shelf:
    origin = Vector((0, 0, 0))
    direction = Vector((1, 0, 0))
    width = 3.0
    parameters = {}

    def __init__(self, origin, direction, width, parameters):
        self.origin = origin
        self.direction = direction
        self.width = width
        self.parameters = parameters

    def add_book(self, first,
                 align_offset,
                 book_height,
                 cover_thickness,
                 book_depth,
                 textblock_height,
                 textblock_depth,
                 textblock_thickness,
                 spline_curl,
                 hinge_inset,
                 hinge_width,
                 spacing,
                 book_width,
                 lean,
                 lean_angle
                 ):

        book = Book(book_height,
                    cover_thickness,
                    book_depth,
                    textblock_height,
                    textblock_depth,
                    textblock_thickness,
                    spline_curl,
                    hinge_inset,
                    hinge_width,
                    unwrap=self.parameters["unwrap"]).b_object

        book.select_set(True)

        if(self.parameters["subsurf"]):
            book.modifiers.new("subd", type='SUBSURF')
            book.modifiers['subd'].levels = 1
        if(self.parameters["smooth"]):
            bpy.ops.object.shade_smooth()

        # book alignment
        offset_dir = -1 if self.parameters["alignment"] == "1" else 1

        if(not first and not self.parameters["alignment"] == "2"):
            # location alignment
            book.location += Vector((0, offset_dir * (book_depth / 2 - align_offset), 0))

        book.location += Vector((0, 0, book_height / 2))

        # leaning
        if lean_angle < 0:
                book.location += Vector((book_width / 2, 0, 0))
        else:
            book.location += Vector((-book_width / 2, 0, 0))

        book.location = Matrix.Rotation(lean_angle, 3, 'Y') @ book.location

        book.rotation_euler[1] = lean_angle

        if lean_angle < 0:
            pass
            # book.location += Vector((-book_width/2, 0,0 ))
        else:
            pass
            # book.location += Vector((book_width/2, 0,0))

        # distribution
        book.location += Vector((self.cur_offset, 0, 0))
        book.location = Matrix.Rotation(self.direction, 3, 'Z') @ book.location

        book.rotation_euler[2] = self.direction

        book.location += self.origin

        return (book_width, lean_angle if lean else 0, book_height)

    def fill(self):
        self.cur_width = 0
        self.cur_offset = 0

        random.seed(self.parameters["seed"])

        first = False
        params = self.apply_parameters()

        align_offset = params["book_depth"] / 2

        print("=============================")

        old_lean_angle = 0.0
        old_corner_height = 0.0
        corner_height = 0.0

        while(self.cur_width + params["book_width"] < self.width * self.parameters["scale"]):

            print("lean old: " + str(old_lean_angle))
            print("lean    : " + str(params["lean_angle"]))

            print("height old: " + str(old_corner_height))
            print("height    : " + str(corner_height))

            old_width, old_lean_angle, old_height = self.add_book(first, align_offset, **params)
            params = self.apply_parameters()

            self.cur_width += old_width + params["book_width"]

            old_corner_height = old_height * cos(old_lean_angle)

            corner_height = cos(params["lean_angle"]) * (params["book_height"] + params["book_width"] / tan(radians(90) - params["lean_angle"]))

            if(old_corner_height <= corner_height and old_lean_angle >= params["lean_angle"]):
                print("case 1 ")
                self.cur_offset += sin(old_lean_angle) * old_height - cos(old_lean_angle) * old_height / (tan(radians(90) - params["lean_angle"])) + params["book_width"] / cos(params["lean_angle"])
            elif(old_lean_angle < params["lean_angle"]):
                print("case 2")
                self.cur_offset += cos(params["lean_angle"]) * params["book_width"] + sin(params["lean_angle"]) * params["book_width"] / tan(radians(90) - old_lean_angle)
            elif(old_corner_height > corner_height and old_lean_angle >= params["lean_angle"]):
                print("case 3")
                self.cur_offset += (cos(params["lean_angle"]) * params["book_height"] + sin(params["lean_angle"]) * params["book_width"]) / tan(radians(90) - old_lean_angle) + params["book_width"] / cos(params["lean_angle"]) - sin(params["lean_angle"]) * (params["book_height"] + params["book_width"] / tan(radians(90) - params["lean_angle"]))
            else:
                print("doesn't fit a designed case")

            first = False

    def apply_parameters(self):
        """Return book parameters with all randomization applied"""

        p = self.parameters

        rndm_book_height = (random.random() * 0.4 - 0.2) * p["rndm_book_height_factor"]
        rndm_book_width = (random.random() * 0.4 - 0.2) * p["rndm_book_width_factor"]
        rndm_book_depth = (random.random() * 0.4 - 0.2) * p["rndm_book_depth_factor"]

        rndm_textblock_offset = (random.random() * 0.4 - 0.2) * p["rndm_textblock_offset_factor"]

        rndm_cover_thickness = (random.random() * 0.4 - 0.2) * p["rndm_cover_thickness_factor"]

        rndm_spline_curl = (random.random() * 0.4 - 0.2) * p["rndm_spline_curl_factor"]

        rndm_hinge_inset = (random.random() * 0.4 - 0.2) * p["rndm_hinge_inset_factor"]
        rndm_hinge_width = (random.random() * 0.4 - 0.2) * p["rndm_hinge_width_factor"]

        rndm_spacing = random.random() * p["rndm_spacing_factor"]

        rndm_lean_angle = (random.random() * 0.8 - 0.4) * p["rndm_lean_angle_factor"]

        book_height = p["scale"] * p["book_height"] * (1 + rndm_book_height)
        book_width = p["scale"] * p["book_width"] * (1 + rndm_book_width)
        book_depth = p["scale"] * p["book_depth"] * (1 + rndm_book_depth)

        cover_thickness = p["scale"] * p["cover_thickness"] * (1 + rndm_cover_thickness)

        textblock_height = book_height - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_depth = book_depth - p["scale"] * p["textblock_offset"] * (1 + rndm_textblock_offset)
        textblock_thickness = book_width - 2 * cover_thickness

        spline_curl = p["scale"] * p["spline_curl"] * (1 + rndm_spline_curl)

        hinge_inset = p["scale"] * p["hinge_inset"] * (1 + rndm_hinge_inset)
        hinge_width = p["scale"] * p["hinge_width"] * (1 + rndm_hinge_width)

        spacing = p["scale"] * p["spacing"] * (1 + rndm_spacing)

        lean = p["lean_amount"] > random.random()

        lean_dir_factor = 1 if random.random() > (.5 - p["lean_direction"] / 2) else -1

        lean_angle = p["lean_angle"] * (1 + rndm_lean_angle) * lean_dir_factor if lean else 0

        return {"book_height": book_height,
                "cover_thickness": cover_thickness,
                "book_depth": book_depth,
                "textblock_height": textblock_height,
                "textblock_depth": textblock_depth,
                "textblock_thickness": textblock_thickness,
                "spline_curl": spline_curl,
                "hinge_inset": hinge_inset,
                "hinge_width": hinge_width,
                "spacing": spacing,
                "book_width": book_width,
                "lean": lean,
                "lean_angle": lean_angle}
