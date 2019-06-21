'''
Copyright (C) 2015 Diego Gangl
<diego@sinestesia.co>

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


import random
import math
import warnings

import numpy

from mathutils import Vector
from mathutils import noise

from .. import data
from .. import utils
from . import erosion
from . import coords


def process_terrain():
    """ Generate terrain in a Thread """
    
    settings = data.settings('terrain')

    # 1. SEED 
    # ------------------------------------------------------------------------
    if settings.auto_seed:
        seed = random.randint(0,2000000000)
    else:
        seed = settings.seed

    numpy.random.seed(seed)


    # 2. WHITE NOISE -> 1/f^p FILTER
    # ------------------------------------------------------------------------
    if settings.detail_level == 'custom':
        size        = settings.detail_custom
        base_grid   = settings.detail_base
    else:
        size        = 2**int(settings.detail_level)
        base_grid   = 128

    roughness = utils.remap(settings.roughness, 0, 10, 3, 1.8)
    heights   = numpy.random.normal(2,1, (base_grid, base_grid))

    heights.astype('float16', copy = False)
    heights = filter_noise(heights,base_grid, size, roughness)

    heights    = utils.remap(heights, heights.min(), heights.max(),
                                      0,             1)

    # 3. VORONOI MIX 
    # ------------------------------------------------------------------------
    scale_factor = utils.remap(settings.deformation, 0, 10, 1, 4)
    H            = utils.remap(settings.roughness, 0, 10, 2, 1)
    influence    = max(10 - settings.roughness, 1)

    heights     += voronoi_map(size, scale_factor, H, influence)

    # 4. VERTICAL SCALE
    # ------------------------------------------------------------------------
    heights = utils.remap(heights, heights.min(), heights.max(),
                                   0,             settings.max_height)

    # 5. ALPINE
    # ------------------------------------------------------------------------
    if settings.alpine > 0:
        alpine  = utils.remap(settings.alpine, 1, 10, 2, 8)

        heights   -= heights**0.5
        max_height = max(heights.max(), 0.001)
        heights   += numpy.power(heights, settings.alpine)/max_height**alpine
        heights    = utils.remap(heights, heights.min(), heights.max(),
                                 0,       settings.max_height)

    # 6. STRATA
    # ------------------------------------------------------------------------
    if settings.use_strata:
        frequency = settings.strata_frequency * math.pi 
        strength  = settings.strata_strength / 100

        heights   = strata(heights, frequency, strength, settings.strata_invert)



    # 7. EROSION
    # ------------------------------------------------------------------------
    if settings.use_thermal:
        talus        = utils.remap(settings.thermal_talus, 0.5236,   0.7854, 
                                                           0.01,     0.05)

        percentage   = utils.remap(settings.thermal_strength, 1 ,    10,
                                                              0.01,  0.25)

        heights = erosion.thermal(heights, talus, percentage)



    # 8. SLOPES
    # ------------------------------------------------------------------------

    if settings.use_slopes:
        if settings.slope_X > 0:
            slope_X  = utils.remap(settings.slope_X, 0,10,0.25,10)
            base_X   = settings.slope_min_X / 10

            if settings.slope_invert_X:
                slope_X *= -1

            heights *= coords.linear_mask(size, 'X', slope_X) + base_X

        if settings.slope_Y > 0:
            slope_Y  = utils.remap(settings.slope_Y, 0,10,0.25,10)
            base_Y   = settings.slope_min_Y / 10

            if settings.slope_invert_Y:
                slope_Y *= -1

            heights *= coords.linear_mask(size, 'Y', slope_Y) + base_Y


        heights = utils.remap(heights, heights.min(), heights.max(),
                              0,       settings.max_height)


    # 9. SEA LEVEL / PLATEAU
    # ------------------------------------------------------------------------
    heights = heights.clip(settings.sea_level, settings.plateau_level)

    if settings.sea_level > 0:
        heights = utils.remap(heights, heights.min(), heights.max(),
                              0,       settings.max_height - settings.sea_level)



    # 10. EDGES
    # ------------------------------------------------------------------------
    if settings.edges == 'SMOOTH' or settings.edges == 'ISLAND':
        smooth_factor = utils.remap(settings.edge_smoothed_factor, 0, 1, 1, 2.5)        
        heights = edges_smooth(heights, size, smooth_factor)
        
    elif settings.edges== 'STRAIGHT':
        heights = edges_straight(heights, size)



    return (seed, heights.tolist())
    


def filter_noise(base, base_grid, size, power=2.6):
    """ Filter the base noise frequencies using 1/f^p """

    frequency = numpy.fft.fft2(base)
    frequency = numpy.fft.fftshift(frequency)


    if base_grid != size:
        diff  = (size - base_grid) // 2

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            frequency    = numpy.pad(frequency, diff, 
                                    mode='constant')


    f_filter = coords.radial_mask(size)
    f_filter = numpy.where(f_filter < 1/size, 1/size, f_filter)

    frequency *= 1/f_filter**power 

    return abs(numpy.fft.ifft2(frequency))



def edges_straight(heights, size):
    """ Make edges straight """
    
    heights[:,0]        = 0
    heights[:,size-1]   = 0

    heights[0,:]        = 0
    heights[size-1,:]   = 0

    return heights


def edges_smooth(heights, size, smooth):
    """ Smooth values to zero (plane) """
    
    mask = coords.radial_mask(size, smooth)
    mask = utils.remap(mask, 0, mask.max(), 1, 0)
    
    return heights * (mask**smooth)


def voronoi_map(size, scale_factor, H, influence):
    """ Build a disturbed voronoi texture to mix with noise """

    voronoi_map = numpy.zeros((size,size), dtype='float16')
    factor = (size / scale_factor)
    
    for x in range(size):
        for y in range(size):
            
            # Scale coordinates
            scaled_x = x / factor
            scaled_y = y / factor
            
            coords = Vector((scaled_x, scaled_y, 0))
                
            # Distort coordinates with noise
            distortion = noise.fractal(coords, H, 2, 8)

            coords[0] += distortion / H
            coords[1] += distortion / H

            voronoi_data = noise.voronoi(coords)
            points = voronoi_data[0]
                

            # Voronoi F1F2
            value = points[1] - points[0]
                            
            voronoi_map[x,y] = value 

    return voronoi_map / influence


def strata(heights, frequency, strength, invert):
    """ Apply a stratified effect to terrain """
    
    steps = numpy.sin(heights * frequency) * frequency
    steps = abs(steps)

    if invert:
        strength *= -1

    return heights + (steps * strength)
            
