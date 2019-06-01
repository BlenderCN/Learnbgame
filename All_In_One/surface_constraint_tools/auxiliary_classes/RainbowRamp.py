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

# <pep8-80 compliant>

from mathutils import Vector

class RainbowRamp():
    def __init__(self, steps = 250):
        self.ramp = dict()
        self.steps = steps

    def generate_ramp(self):
        # The rainbow color ramp is a gradation over the visible portion of the
        # electromagnetic spectrum.  
        red = Vector((1.0, 0.25, 0.25))
        orange = Vector((1.0, 0.7, 0.25))
        yellow = Vector((1.0, 1.0, 0.25))
        green = Vector((0.250, 1.0, 0.596))
        blue = Vector((0.265, 0.25, 1.0)) 
        violet = Vector((0.5, 0.0, 1.0)) 

        # Generate each subramp between neighboring colors.
        interval = self.steps // 5
        violet_to_blue_range = range(interval)
        blue_to_green_range = range(interval, 2 * interval)
        green_to_yellow_range = range(2 * interval, 3 * interval)
        yellow_to_orange_range = range(3 * interval, 4 * interval)
        orange_to_red_range = range(4 * interval, self.steps) 
        C = 1 / interval 
        violet_to_blue_subramp = {
            i : (1 - C * i) * violet + C * i * blue
            for i in violet_to_blue_range
        } 
        offset = interval
        blue_to_green_subramp = {
            i : (1 - C * (i - offset)) * blue + C * (i - offset) * green
            for i in blue_to_green_range
        } 
        offset = 2 * interval
        green_to_yellow_subramp = {
            i : (1 - C * (i - offset)) * green + C * (i - offset) * yellow
            for i in green_to_yellow_range
        }
        offset = 3 * interval
        yellow_to_orange_subramp = {
            i : (1 - C * (i - offset)) * yellow + C * (i - offset) * orange
            for i in yellow_to_orange_range
        }
        C = 1 / (interval - 1)
        offset = 4 * interval
        orange_to_red_subramp = {
            i : (1 - C * (i - offset)) * orange + C * (i - offset) * red
            for i in orange_to_red_range
        }

        # Combine the subramps together to form the complete color ramp.
        self.ramp = violet_to_blue_subramp
        self.ramp.update(blue_to_green_subramp)
        self.ramp.update(green_to_yellow_subramp)
        self.ramp.update(yellow_to_orange_subramp)
        self.ramp.update(orange_to_red_subramp)

    def get_color_map_from_falloff_map(self, falloff_map):
        # Return a color map by determining the rgb color vector for each index
        # in the domain of the falloff map.
        ramp = self.ramp
        steps = self.steps
        return {
            index : ramp[falloff_map[index] * (steps - 1) // 1]
            for index in falloff_map
        }

    def reset(self):
        self.__init__()