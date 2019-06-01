'''
Copyright (C) 2018 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Jonathan Denning

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
import random

from mathutils import Color


def get_random_color():
    global random_hsvs, random_index
    h,s,v = random_hsvs[random_index]
    random_index = (random_index + 1) % len(random_hsvs)
    h = (h + (random.random() * 0.1 - 0.05)) % 1
    s = (s - (random.random() * 0.1))
    v = (v - (random.random() * 0.1))
    c = Color((0,0,0))
    c.hsv = (h,s,v)
    return c

def rgb_to_hsv(rgb):
    return Color(rgb).hsv

def hsv_to_rgb(hsv):
    c = Color((0,0,0))
    c.hsv = hsv
    return c

random_hsvs = [
    (h, s, v)
    for h in [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
    for s in [0.5, 0.75, 1.0]
    for v in [0.5, 0.75, 1.0]
]
random.shuffle(random_hsvs)
random_index = 0
