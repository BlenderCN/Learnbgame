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
import bmesh


class Book:
    b_object = None
    height = 0.0
    width = 0.0

    def __init__(self, cover_height, cover_thickness, cover_depth, page_height, page_depth, page_thickness, spline_curl, hinge_inset, hinge_width, unwrap=False):
            self.height = cover_height
            self.width = page_thickness + 2 * cover_thickness

            """ The following section does not conform to PEP8 (whitespaces) in an attempt to improve readabilty. (Don't know if it's working though ;) ) """

            verts = [
                # cover right side
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                 cover_height / 2],
                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                 cover_height / 2],
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                -cover_height / 2],
                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                -cover_height / 2],

                    [ page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2],
                    [ page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2],
                    [ page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2],
                    [ page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2],

                # cover left side
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                 cover_height / 2],
                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                 cover_height / 2],
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                -cover_height / 2],
                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                -cover_height / 2],

                    [-page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2],
                    [-page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2],
                    [-page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2],
                    [-page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2],

                # pages
                    [ page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2],
                    [ page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2],
                    [ page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2],
                    [ page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2],

                    [-page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2],
                    [-page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2],
                    [-page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2],
                    [-page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2],

                # hinge right
                    [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
                    [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],

                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2],
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2],
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2],

                # hinge left
                    [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
                    [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],

                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2],
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2],
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2],

                # spline right
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2],

                # spline left
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2],

                # spline center
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,   cover_height / 2],
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                     cover_height / 2],
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,  -cover_height / 2],
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                    -cover_height / 2]
            ]

            verts_proximity = [
                # pages proximity loops
                    [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2],
                    [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2],
                    [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2],
                    [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2],

                    [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2],
                    [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2],
                    [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2],
                    [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2],

                    [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2],
                    [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                 -page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                 -page_height / 2],

                    [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                  page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                  page_height / 2],
                    [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                  page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                  page_height / 2],

                    [-page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2 - page_height / 100],
                    [ page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2 - page_height / 100],
                    [-page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2 - page_height / 100],
                    [ page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2 - page_height / 100],

                    [-page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
                    [ page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
                    [-page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2 + page_height / 100],
                    [ page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2 + page_height / 100],

                # cover proximity loops
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

                    [ page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
                    [ page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

                    [-page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
                    [-page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

                    [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],

                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],
                    [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],

                    [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],

                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],
                    [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],

                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2 + cover_height / 100],

                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2 + cover_height / 100],

                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,   cover_height / 2 - cover_height / 100],
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                     cover_height / 2 - cover_height / 100],
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,  -cover_height / 2 + cover_height / 100],
                    [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                    -cover_height / 2 + cover_height / 100],

                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],
                    [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
                    [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],

                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],
                    [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
                    [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],

                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],
                    [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
                    [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],

                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],
                    [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
                    [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],

                # additional proximity loops pages
                    [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2 + page_depth / 100,                               page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2 + page_depth / 100,                               page_height / 2],
                    [-page_thickness / 2 + page_thickness / 100,            page_depth / 2 - page_depth / 100,                               page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,            page_depth / 2 - page_depth / 100,                               page_height / 2],

                    [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2 + page_depth / 100,                              -page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2 + page_depth / 100,                              -page_height / 2],
                    [-page_thickness / 2 + page_thickness / 100,            page_depth / 2 - page_depth / 100,                              -page_height / 2],
                    [ page_thickness / 2 - page_thickness / 100,            page_depth / 2 - page_depth / 100,                              -page_height / 2],

                    [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
                    [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
                    [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                 -page_height / 2 + page_height / 100],
                    [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                 -page_height / 2 + page_height / 100],

                    [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                  page_height / 2 - page_height / 100],
                    [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                  page_height / 2 - page_height / 100],
                    [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                  page_height / 2 - page_height / 100],
                    [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                  page_height / 2 - page_height / 100],

                    [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2 - page_height / 100],
                    [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2 - page_height / 100],
                    [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2 - page_height / 100],
                    [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2 - page_height / 100],

                    [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2 + page_height / 100],
                    [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2 + page_height / 100],
                    [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2 + page_height / 100],
                    [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2 + page_height / 100],
            ]

            """ NON PEP8 ends here """

            faces = [
                # right cover
                [5, 77, 126, 118],
                [116, 1, 73, 124],
                [1, 5, 77, 73],
                [116, 118, 5, 1],
                [0, 4, 118, 116],
                [0, 116, 124, 72],
                [118, 4, 76, 126],
                [124, 73, 75, 125],
                [125, 75, 3, 117],
                [75, 79, 7, 3],
                [79, 127, 119, 7],
                [73, 77, 79, 75],
                [72, 124, 125, 74],
                [77, 126, 127, 79],
                [74, 125, 117, 2],
                [127, 78, 6, 119],
                [126, 76, 78, 127],
                [2, 117, 119, 6],
                [117, 3, 7, 119],

                # right hinge
                [24, 0, 72, 88],
                [25, 4, 0, 24],
                [4, 25, 89, 76],
                [76, 89, 91, 78],
                [78, 91, 27, 6],
                [6, 27, 26, 2],
                [88, 72, 74, 90],
                [90, 74, 2, 26],
                [95, 90, 26, 31],
                [29, 24, 88, 93],
                [93, 88, 90, 95],
                [28, 25, 24, 29],
                [25, 28, 92, 89],
                [89, 92, 94, 91],
                [91, 94, 30, 27],
                [30, 27, 26, 31],

                # spline
                [40, 28, 29],
                [105, 95, 31, 41],
                [41, 30, 31],
                [104, 93, 95, 105],
                [40, 29, 93, 104],
                [44, 40, 104, 108],
                [108, 104, 105, 110],
                [110, 105, 41, 46],
                [28, 45, 109, 92],
                [92, 109, 111, 94],
                [94, 111, 47, 30],
                [30, 47, 46, 41],
                [45, 28, 40, 44],
                [45, 44, 42, 36],
                [45, 36, 100, 109],
                [109, 100, 102, 111],
                [111, 102, 38, 47],
                [47, 38, 43, 46],
                [107, 110, 46, 43],
                [42, 44, 108, 106],
                [106, 108, 110, 107],
                [37, 36, 42],
                [37, 42, 106, 101],
                [101, 106, 107, 103],
                [103, 107, 43, 39],
                [38, 39, 43],

                # hinge left
                [33, 36, 37, 32],
                [36, 33, 97, 100],
                [100, 97, 99, 102],
                [102, 99, 35, 38],
                [38, 35, 34, 39],
                [12, 33, 32, 8],
                [32, 37, 101, 96],
                [96, 101, 103, 98],
                [98, 103, 39, 34],

                # cover left
                [82, 98, 34, 10],
                [80, 96, 98, 82],
                [8, 32, 96, 80],
                [33, 12, 84, 97],
                [97, 84, 86, 99],
                [99, 86, 14, 35],
                [35, 14, 10, 34],
                [112, 8, 80, 120],
                [9, 112, 120, 81],
                [13, 9, 81, 85],
                [114, 112, 9, 13],
                [114, 13, 85, 122],
                [12, 114, 122, 84],
                [84, 122, 123, 86],
                [86, 123, 115, 14],
                [12, 8, 112, 114],
                [120, 80, 82, 121],
                [121, 82, 10, 113],
                [83, 121, 113, 11],
                [87, 83, 11, 15],
                [123, 87, 15, 115],
                [81, 120, 121, 83],
                [85, 81, 83, 87],
                [122, 85, 87, 123],
                [115, 15, 11, 113],
                [14, 115, 113, 10],

                # pages
                [16, 49, 145, 65],
                [61, 16, 65, 141],
                [129, 49, 16, 61],
                [65, 145, 149, 69],
                [69, 149, 53, 18],
                [137, 69, 18, 57],
                [57, 18, 53, 133],
                [136, 137, 57, 56],
                [140, 141, 137, 136],
                [68, 136, 56, 22],
                [148, 68, 22, 52],
                [52, 22, 56, 132],
                [60, 61, 141, 140],
                [144, 64, 68, 148],
                [48, 20, 64, 144],
                [141, 65, 69, 137],
                [145, 147, 151, 149],
                [49, 51, 147, 145],
                [149, 151, 55, 53],
                [51, 17, 67, 147],
                [131, 63, 17, 51],
                [147, 67, 71, 151],
                [151, 71, 19, 55],
                [71, 139, 59, 19],
                [19, 59, 135, 55],
                [67, 143, 139, 71],
                [139, 138, 58, 59],
                [17, 63, 143, 67],
                [63, 62, 142, 143],
                [143, 142, 138, 139],
                [62, 21, 66, 142],
                [21, 50, 146, 66],
                [62, 130, 50, 21],
                [50, 48, 144, 146],
                [146, 144, 148, 150],
                [20, 60, 140, 64],
                [64, 140, 136, 68],
                [66, 146, 150, 70],
                [138, 70, 23, 58],
                [58, 23, 54, 134],
                [70, 150, 54, 23],
                [150, 148, 52, 54],
                [56, 57, 133, 132],
                [132, 133, 135, 134],
                [128, 60, 20, 48],
                [129, 61, 60, 128],
                [129, 131, 51, 49],
                [130, 131, 129, 128],
                [130, 62, 63, 131],
                [128, 48, 50, 130],
                [142, 66, 70, 138],
                [134, 54, 52, 132],
                [135, 59, 58, 134],
                [55, 135, 133, 53]
            ]

            seams = [
                (4, 25),
                (15, 87),
                (16, 65),
                (36, 45),
                (27, 30),
                (21, 62),
                (58, 59),
                (17, 63),
                (6, 27),
                (56, 57),
                (67, 71),
                (30, 47),
                (77, 79),
                (7, 119),
                (19, 59),
                (12, 33),
                (18, 69),
                (25, 28),
                (6, 119),
                (20, 60),
                (28, 45),
                (65, 69),
                (19, 55),
                (5, 118),
                (18, 53),
                (19, 71),
                (18, 57),
                (35, 38),
                (15, 115),
                (17, 67),
                (7, 79),
                (12, 114),
                (33, 36),
                (85, 87),
                (5, 77),
                (53, 55),
                (13, 85),
                (23, 58),
                (13, 114),
                (22, 56),
                (14, 115),
                (60, 61),
                (16, 61),
                (38, 47),
                (14, 35),
                (62, 63),
                (4, 118)
            ]

            def index_to_vert(face):
                lst = []
                for i in face:
                    lst.append(vert_ob[i])
                return tuple(lst)

            mesh = bpy.data.meshes.new("book")

            self.b_object = bpy.data.objects.new("book", mesh)

            verts = verts + verts_proximity

            bpy.context.scene.collection.objects.link(self.b_object)

            bm = bmesh.new()
            bm.from_mesh(mesh)
            vert_ob = []
            for vert in verts:
                vert_ob.append(bm.verts.new(vert))

            bm.verts.index_update()

            try:
                bm.verts.ensure_lookup_table()
            except(AttributeError):
                pass

            if(unwrap):
                for seam in seams:
                    edge = bm.edges.new((bm.verts[seam[0]], bm.verts[seam[1]]))
                    edge.seam = True

            for face in faces:
                bm.faces.new(index_to_vert(face))

            bm.faces.index_update()

            try:
                bm.edges.ensure_lookup_table()
            except(AttributeError):
                pass

            bm.to_mesh(mesh)
            bm.free()

            # recalculate normals
            bpy.context.view_layer.objects.active = self.b_object
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()

            if(unwrap):
                bpy.context.view_layer.objects.active = self.b_object
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.05)
                bpy.ops.object.editmode_toggle()
