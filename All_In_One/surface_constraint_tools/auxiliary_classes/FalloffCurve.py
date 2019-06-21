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

from math import pi, sin, sqrt
from random import random

class FalloffCurve():
    def __init__(self, steps = 250):
        self.curve = dict()
        self.steps = steps
        self.profile = 'SMOOTH'
 
    def generate_curve(self):
        domain_max = self.steps - 1
        profile = self.profile
        steps = self.steps

        # Map the domain of steps to the respective range of intensities for
        # each nonrandom falloff curve profile.
        if profile == 'CONSTANT':
            self.curve = {i : 1 for i in range(steps)}
        elif profile == 'SMOOTH':
            C = pi / (2 * domain_max)
            self.curve = {i : sin(C * i) for i in range(steps)}
        elif profile == 'ROUND':
            C = domain_max ** 2
            self.curve = {
                i : sqrt(C - (domain_max - i) ** 2) / domain_max
                for i in range(steps)
            }
        elif profile == 'ROOT':
            C = 1 / sqrt(domain_max)
            self.curve = {i : C * sqrt(i) for i in range(steps)} 
        elif profile == 'SHARP':
            C = 1 / (domain_max ** 2)
            self.curve = {i : C * i ** 2 for i in range(steps)}
        elif profile == 'LINEAR':
            self.curve = {i : i / domain_max for i in range(steps)}

    def get_falloff_map_from_distance_map(self, distance_map, max_distance):
        # Return a falloff map by determining the intensity value for each
        # index in the domain of the distance map.
        if self.profile == 'RANDOM':
            return {index : random() for index in distance_map}
        else:
            C = self.steps - 1
            curve = self.curve
            return {
                index : curve[
                    int((1 - distance_map[index] / max_distance) * C)
                ]
                for index in distance_map
            }

    def reset(self):
        self.__init__()