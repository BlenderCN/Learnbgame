'''
Copyright (C) 2016 Diego Gangl
diego@sinestesia.co

Created by Diego Gangl. This file is part of Mirage.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import math

import numpy as np

from mathutils import Vector
from mathutils import noise

from . import coords


def thermal(points, talus = 0.05, percentage = 0.1, iterations = 10, variance = 0.1):
    """ Apply thermal erosion to the terrain """
    
    # This method is based on the classic Musgrave (et all) algorithm
    # with a gaussian noise map for terrain hardness. 

    def iterate(points):

        points  = coords.pad(points)

        north   = points - coords.wrapped(points, 'north')
        south   = points - coords.wrapped(points, 'south')
        east    = points - coords.wrapped(points, 'east')
        west    = points - coords.wrapped(points, 'west')

        difference  = north - north.clip (-talus, talus) / terrain_hardness
        difference += south - south.clip (-talus, talus) / terrain_hardness
        difference += west  - west.clip  (-talus, talus) / terrain_hardness
        difference += east  - east.clip  (-talus, talus) / terrain_hardness

        points  -= difference * percentage

        return coords.crop(points)

    # ------------------------------------------------------------------------

    if variance > 0:
       factor = math.sqrt(points.shape[0])
       terrain_hardness = np.random.normal(2, variance, points.shape)
       terrain_hardness *= factor 
       terrain_hardness = coords.pad(terrain_hardness)


    else:
        terrain_hardness = 1

    for i in range(iterations):
        points = iterate(points)

    return points
