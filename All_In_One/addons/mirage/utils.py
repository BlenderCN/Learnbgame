'''
Copyright (C) 2015 Diego Gangl, Jacques Lucke
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

import os
import pkgutil
import importlib

import bpy
import math

import numpy as np


def is_selected_and_mesh(context):
    result = False
    
    if len(context.selected_objects) == 1: 
        if (context.object is not None and context.object.type == 'MESH'):
            result = True
    
    return result      


def force_redraw():
    """
        Forces the UI to redraw

        This makes me cry at night but looks like
        it's the only way to do it.

        Modified from a snippet by CoDEManX in the
        bf-python list to work in a limited context.
    """

    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()



def get_heights(bm, sort = False):
    """ Get heights from a mesh as a 2D numpy array """

    size = math.sqrt(len(bm.verts))

    if sort:
        bm.verts.sort(key=lambda v: v.co.y * int(size) + v.co.x)

    bm.verts.ensure_lookup_table()

    heights = np.zeros((size, size))

    for i, vert in enumerate(bm.verts):
        x = i % size
        y = i // size

        heights[x, y] = vert.co.z

    return heights



def debug_numpy():
    """ Set print options in numpy for debugging """

    np.set_printoptions(precision   = 4,
                        threshold   = 10000,
                        suppress    = True,
                        linewidth   = 80)



def set_heights(bm, heights, mesh):
    """ Apply a list or numpy array of heights to a mesh """

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
                
    side = int(math.sqrt(len(bm.verts)))

    for x in range(side):
        for y in range(side):
            i = (y * side) + x
            z = heights[x][y]

            bm.verts[i].co.z = z

    for face in bm.faces:
        face.smooth = True

    bm.normal_update()
    bm.to_mesh(mesh)



def remap(values, src_min, src_max, dst_min, dst_max):
    """ Map the value in old range to a new range """
    
    src_bounds = [src_min, src_max]
    dst_bounds = [dst_min, dst_max]
    
    return np.interp(values, src_bounds, dst_bounds)
