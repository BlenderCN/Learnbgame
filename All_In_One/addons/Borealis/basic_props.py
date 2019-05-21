# -*- coding: utf-8 -*-
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

'''
Contains basic model properties and their definitions.

This module contains all the basic properties used in an NWN model.

@author: Erik Ylipää
'''


def get_animation_categories():
    """ Build and return the animation data """
    return classifications


walkmesh_materials = [{"name": "Dirt", "color": (0.3, 0.3, 0.2)},
                           {"name": "Obscuring", "color": (1, 1, 1)},
                           {"name": "Grass", "color": (0, 0.5, 0)},
                           {"name": "Stone", "color": (0.2, 0.2, 0.2)},
                           {"name": "Wood", "color": (0.04, 0.01, 0.01)},
                           {"name": "Water", "color": (0, 0, 0.7)},
                           {"name": "Nonwalk", "color": (0.7, 0, 1)},
                           {"name": "Transparent", "color": (0, 1, 1)},
                           {"name": "Carpet", "color": (0.2, 0.05, 0.1)},
                           {"name": "Metal", "color": (0.02, 0.02, 0.02)},
                           {"name": "Puddles", "color": (0, 0.5, 0.5)},
                           {"name": "Swamp", "color": (0, 0.25, 0)},
                           {"name": "Mud", "color": (0.36, 0.2, 0.1)},
                           {"name": "Leaves", "color": (0, 0.75, 0)},
                           {"name": "Lava", "color": (0.75, 0, 0)},
                           {"name": "BottomlessPit", "color": (0.015, 0.005, 0.03)},
                           {"name": "DeepWater", "color": (0, 0.005, 0.08)},
                           {"name": "Door", "color": (0.14, 0.05, 0.02)},
                           {"name": "Snow", "color": (0.5, 0.5, 1)},
                           {"name": "Sand", "color": (0.4, 0.3, 0.1)}]


classifications = ["Character", "Item", "Door", "Effect", "GUI", "Tile"]
