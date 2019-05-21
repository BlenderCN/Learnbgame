# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import bpy

# Blender imports
# NONE!

# Addon imports
from ...functions import *

legalBricks = {
    1:{ "PLATE":         [{"s":[1, 1], "pt":"3024"},
                          {"s":[1, 2], "pt":"3023"},
                          {"s":[1, 3], "pt":"3623"},
                          {"s":[1, 4], "pt":"3710"},
                          {"s":[1, 6], "pt":"3666"},
                          {"s":[1, 8], "pt":"3460"},
                          {"s":[1, 10], "pt":"4477"},
                          {"s":[1, 12], "pt":"60479"},
                          {"s":[2, 2], "pt":"3022"},
                          {"s":[2, 3], "pt":"3021"},
                          {"s":[2, 4], "pt":"3020"},
                          {"s":[2, 6], "pt":"3795"},
                          {"s":[2, 8], "pt":"3034"},
                          {"s":[2, 10], "pt":"3832"},
                          {"s":[2, 12], "pt":"2455"},
                          {"s":[2, 14], "pt":"91988"},
                          {"s":[2, 16], "pt":"4282"},
                          {"s":[3, 3], "pt":"11212"},
                          {"s":[4, 4], "pt":"3031"},
                          {"s":[4, 6], "pt":"3032"},
                          {"s":[4, 8], "pt":"3035"},
                          {"s":[4, 10], "pt":"3030"},
                          {"s":[4, 12], "pt":"3029"},
                          {"s":[6, 6], "pt":"3958"},
                          {"s":[6, 8], "pt":"3036"},
                          {"s":[6, 10], "pt":"3033"},
                          {"s":[6, 12], "pt":"3028"},
                          {"s":[6, 14], "pt":"3456"},
                          {"s":[6, 16], "pt":"3027"},
                          {"s":[6, 24], "pt":"3026"},
                          {"s":[8, 8], "pt":"41539"},
                          {"s":[8, 11], "pt":"728"},
                          {"s":[8, 16], "pt":"92438"},
                          {"s":[16, 16], "pt":"91405"}],
        "TILE":          [{"s":[1, 1], "pt":"3070b"},
                          {"s":[1, 2], "pt":"3069b"},
                          {"s":[1, 3], "pt":"63864"},
                          {"s":[1, 4], "pt":"2431"},
                          {"s":[1, 6], "pt":"6636"},
                          {"s":[1, 8], "pt":"4162"},
                          {"s":[2, 2], "pt":"3068b"},
                          {"s":[2, 4], "pt":"87079"},
                          {"s":[3, 6], "pt":"6934"},
                          {"s":[6, 6], "pt":"10202"},
                          {"s":[8, 16], "pt":"48288"}],
        "STUD":          [{"s":[1, 1], "pt":"4073"}],
        "STUD_HOLLOW":   [{"s":[1, 1], "pt":"85861"}],
        # "WING":[[2, 3],
        #         [2, 4],
        #         [3, 6],
        #         [3, 8],
        #         [3, 12],
        #         [4, 4],
        #         [6, 12],
        #         [7, 12]],
        # "ROUNDED_TILE":[[1, 1]],
        # "SHORT_SLOPE":[[1, 1],
        #             [1, 2]],
        "TILE_GRILL":    [{"s":[1, 2], "pt":"2412b"}],
        # "TILE_ROUNDED":[[2, 2]],
        # "PLATE_ROUNDED":[[2, 2]],
        },
    3:{ "BRICK":         [{"s":[1, 1], "pt":"3005"},
                          {"s":[1, 2], "pt":"3004"},
                          {"s":[1, 3], "pt":"3622"},
                          {"s":[1, 4], "pt":"3010"},
                          {"s":[1, 6], "pt":"3009"},
                          {"s":[1, 8], "pt":"3008"},
                          {"s":[1, 10], "pt":"6111"},
                          {"s":[1, 12], "pt":"6112"},
                          {"s":[1, 16], "pt":"2465"},
                          {"s":[2, 2], "pt":"3003"},
                          {"s":[2, 3], "pt":"3002"},
                          {"s":[2, 4], "pt":"3001"},
                          {"s":[2, 6], "pt":"2456"},
                          {"s":[2, 8], "pt":"3007"},
                          {"s":[2, 10], "pt":"3006"},
                          {"s":[4, 6], "pt":"2356"},
                          {"s":[4, 10], "pt":"6212"},
                          {"s":[4, 12], "pt":"4202"},
                          {"s":[4, 18], "pt":"30400"},
                          {"s":[8, 8], "pt":"4201"},
                          {"s":[8, 16], "pt":"4204"},
                          {"s":[10, 10], "pt":"733"},
                          {"s":[10, 20], "pt":"700b"},
                          {"s":[12, 24], "pt":"30072"}],
        "SLOPE":         [{"s":[1, 1], "pt":"54200"},
                          {"s":[1, 2], "pt":"3040b"},
                          {"s":[1, 3], "pt":"4286"},
                          {"s":[1, 4], "pt":"60477"},
                          {"s":[2, 2], "pt":"3039"},
                          {"s":[2, 3], "pt":"3298", "pt2":"3038"},
                          {"s":[2, 4], "pt":"30363", "pt2":"3037"},
                          {"s":[2, 8], "pt":"4445"},
                          {"s":[3, 3], "pt":"4161"},
                          {"s":[4, 3], "pt":"3297"}], # TODO: Add 6x3 option with studs missing between outer two (needs to be coded into slope.py generator)
        "SLOPE_INVERTED":[{"s":[1, 2], "pt":"3665"},
                          {"s":[1, 3], "pt":"4287"},
                          {"s":[2, 2], "pt":"3660p01"},
                          {"s":[2, 3], "pt":"3747a"}],
        "CYLINDER":      [{"s":[1, 1], "pt":"3062b"}],
        "CONE":          [{"s":[1, 1], "pt":"4589"}],
        "CUSTOM 1":      [{"s":[1, 1], "pt":"3005"}],
        "CUSTOM 2":      [{"s":[1, 1], "pt":"3005"}],
        "CUSTOM 3":      [{"s":[1, 1], "pt":"3005"}],
        # "BRICK_STUD_ON_ONE_SIDE":[[1, 1]],
        # "BRICK_INSET_STUD_ON_ONE_SIDE":[[1, 1]],
        # "BRICK_STUD_ON_TWO_SIDES":[[1, 1]],
        # "BRICK_STUD_ON_ALL_SIDES":[[1, 1]],
        # "TILE_WITH_HANDLE":[[1, 2]],
        # "BRICK_PATTERN":[[1, 2]],
        # "DOME":[[2, 2]],
        # "DOME_INVERTED":[[2, 2]],
      },
    # 9:{
    #     "TALL_SLOPE":[[1, 2], [2, 2]]
    #     "TALL_SLOPE_INVERTED":[[1, 2]]
    #     "TALL_BRICK":[[2, 2]]
    # }
    # 15:{
    #     "TALL_BRICK":[[1, 2]]
    # }
    }

def getLegalBrickSizes():
    """ returns a list of legal brick sizes """
    legalBrickSizes = {}
    # add reverses of brick sizes
    for heightKey,types in legalBricks.items():
        legalBrickSizes[heightKey] = {}
        for typ,parts in types.items():
            reverseSizes = [part["s"][::-1] for part in parts]
            legalBrickSizes[heightKey][typ] = uniquify2(reverseSizes + [part["s"] for part in parts])
    return legalBrickSizes


def getLegalBricks():
    """ returns a list of legal brick sizes and part numbers """
    return legalBricks


def getTypesObscuringAbove():
    return ["BRICK", "PLATE", "TILE", "STUD", "SLOPE_INVERTED"]


def getTypesObscuringBelow():
    return ["BRICK", "PLATE", "TILE", "STUD", "SLOPE"]
