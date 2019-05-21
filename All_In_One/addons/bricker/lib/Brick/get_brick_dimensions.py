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

def get_brick_dimensions(height=1, zScale=1, gap_percentage=0.01):
    """
    returns the dimensions of a brick in Blender units

    Keyword Arguments:
    height         -- height of a standard brick in Blender units
    zScale         -- height of the brick in plates (1: standard plate, 3: standard brick)
    gap_percentage -- gap between bricks relative to brick height
    """

    scale = height/9.6
    dimensions = {}
    dimensions["height"] = scale*9.6*(zScale/3)
    dimensions["width"] = scale*8
    dimensions["gap"] = scale*9.6*gap_percentage
    dimensions["stud_height"] = scale*1.8
    dimensions["stud_radius"] = scale*2.4
    dimensions["thickness"] = scale*1.6
    dimensions["tube_thickness"] = scale*0.855
    dimensions["support_width"] = scale*0.8
    dimensions["support_height"] = dimensions["height"]*0.65
    dimensions["slope_support_width"] = scale*0.6  # eyeballed
    dimensions["slope_support_height"] = scale*2.4  # eyeballed
    dimensions["bar_radius"] = scale*1.6
    dimensions["logo_width"] = scale*4.8 # originally scale*3.74
    dimensions["tick_width"] = scale*0.6
    dimensions["tick_depth"] = scale*0.3
    dimensions["slope_tick_depth"] = scale*0.375
    dimensions["slit_height"] = scale*0.3
    dimensions["slit_depth"] = scale*0.3
    dimensions["oblong_support_dist"] = scale
    dimensions["oblong_support_radius"] = scale*0.6
    dimensions["support_height_triple"] = (dimensions["height"]*3)*0.65
    dimensions["logo_offset"] = (dimensions["height"] / 2) + (dimensions["stud_height"])
    # round all values in dimensions
    for k in dimensions:
        dimensions[k] = round(dimensions[k], 8)

    return dimensions
