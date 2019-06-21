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

import numpy as np

def wrapped(array, direction):
    """ Return array displaced in a certain direction """
    
    if direction == 'north':
        return np.roll(array, -1, axis = 0)
    if direction == 'south':
        return np.roll(array, 1, axis = 0)
    if direction == 'east':
        return np.roll(array, 1, axis = 1)
    if direction == 'west':
        return np.roll(array, -1, axis = 0)


def pad(array, size = 1):
    """ Pad an array to prevent edge artifacts  """

    return np.pad(array, size, 'edge')


def crop(array, size = 1):
    """ Crop a padded array to it's original size """

    return array[size:-size, size:-size]


def radial_mask(size, length = None):
    """ Create an array with a radial gradient """

    x,y = np.indices((size, size))
    center = size / 2

    mask = np.hypot(x - center, y - center)
    mask = mask.clip(0, center)
    
    return mask


def linear_mask(size, axis, length = None):
    """ Create an array with a linear gradient on an axis """

    x,y = np.indices((size, size))

    if axis == 'X':
        mask = x / size

    elif axis == 'Y':
        mask = y / size


    if length:
        mask = mask**abs(length)

    if length < 0:
        if axis == 'X':
            mask = np.flipud(mask)
        elif axis == 'Y':
            mask = np.fliplr(mask)

    return mask


