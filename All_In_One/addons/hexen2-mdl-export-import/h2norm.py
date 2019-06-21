# vim:ts=4:et
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

# <pep8 compliant>

from mathutils import Vector

# Covert normals to quake's normal palette. Implementation taken from ajmdl
#
# AJA: I use the following shortcuts to speed up normal lookup:
#
# Firstly, a preliminary match only uses the first quadrant
# (where all coords are >= 0).  Then we use the appropriate
# normal index for the actual quadrant.  We can do this because
# the 162 MDL/MD2 normals are not arbitrary but are mirrored in
# every quadrant.  The eight numbers in the lists above are the
# indices for each quadrant (+++ ++- +-+ +-- -++ -+- --+ ---).
#
# Secondly we use the axis with the greatest magnitude (of the
# incoming normal) to search an axis-specific group, which means
# we only need to check about 1/3rd of the normals.
# Actually, about 1/14th (taniwha)
x_group = (
    (Vector((1.0000, 0.0000, 0.0000)), (52,52,52,52,143,143,143,143)),
    (Vector((0.9554, 0.2952, 0.0000)), (51,51,55,55,141,141,145,145)),
    (Vector((0.9511, 0.1625, 0.2629)), (53,63,57,70,142,148,146,151)),
    (Vector((0.8642, 0.4429, 0.2389)), (46,61,56,69,19,147,123,150)),
    (Vector((0.8507, 0.5257, 0.0000)), (41,41,54,54,18,18,116,116)),
    (Vector((0.8507, 0.0000, 0.5257)), (60,67,60,67,144,155,144,155)),
    (Vector((0.8090, 0.3090, 0.5000)), (48,62,58,68,16,149,124,152)),
    (Vector((0.7166, 0.6817, 0.1476)), (42,43,111,100,20,25,118,117)),
    (Vector((0.6882, 0.5878, 0.4253)), (47,76,140,101,21,156,125,161)),
    (Vector((0.6817, 0.1476, 0.7166)), (49,65,59,66,15,153,126,154)),
    (Vector((0.5878, 0.4253, 0.6882)), (50,75,139,102,17,157,128,160)) )
y_group = (
    (Vector((0.0000, 1.0000, 0.0000)), (32,32,104,104,32,32,104,104)),
    (Vector((0.0000, 0.9554, 0.2952)), (33,30,107,103,33,30,107,103)),
    (Vector((0.2629, 0.9511, 0.1625)), (36,39,109,105,34,31,122,115)),
    (Vector((0.2389, 0.8642, 0.4429)), (35,38,108,97,23,29,121,113)),
    (Vector((0.5257, 0.8507, 0.0000)), (44,44,112,112,27,27,119,119)),
    (Vector((0.0000, 0.8507, 0.5257)), (6,28,106,90,6,28,106,90)),
    (Vector((0.5000, 0.8090, 0.3090)), (37,40,110,98,22,26,120,114)),
    (Vector((0.1476, 0.7166, 0.6817)), (8,71,136,92,7,77,130,91)),
    (Vector((0.4253, 0.6882, 0.5878)), (45,73,138,99,24,158,131,159)),
    (Vector((0.7166, 0.6817, 0.1476)), (42,43,111,100,20,25,118,117)),
    (Vector((0.6882, 0.5878, 0.4253)), (47,76,140,101,21,156,125,161)) )
z_group = (
    (Vector((0.0000, 0.0000, 1.0000)), (5,84,5,84,5,84,5,84)),
    (Vector((0.2952, 0.0000, 0.9554)), (12,85,12,85,2,82,2,82)),
    (Vector((0.1625, 0.2629, 0.9511)), (14,86,134,96,4,83,132,89)),
    (Vector((0.4429, 0.2389, 0.8642)), (13,74,133,95,1,81,127,87)),
    (Vector((0.5257, 0.0000, 0.8507)), (11,64,11,64,0,80,0,80)),
    (Vector((0.0000, 0.5257, 0.8507)), (9,79,137,93,9,79,137,93)),
    (Vector((0.3090, 0.5000, 0.8090)), (10,72,135,94,3,78,129,88)),
    (Vector((0.6817, 0.1476, 0.7166)), (49,65,59,66,15,153,126,154)),
    (Vector((0.5878, 0.4253, 0.6882)), (50,75,139,102,17,157,128,160)),
    (Vector((0.1476, 0.7166, 0.6817)), (8,71,136,92,7,77,130,91)),
    (Vector((0.4253, 0.6882, 0.5878)), (45,73,138,99,24,158,131,159)) )

def map_normal(n):
    fn = Vector((abs(n.x),abs(n.y),abs(n.z)));
    group = x_group
    if fn.y > fn.x and fn.y > fn.z:
        group = y_group
    if fn.z > fn.x and fn.z > fn.y:
        group = z_group
    best = 0
    best_dot = -1
    for i in range(len(group)):
        dot = group[i][0].dot(fn)
        if dot > best_dot:
            best = i
            best_dot = dot
    quadrant = 0
    if n.x < 0:
        quadrant += 4
    if n.y < 0:
        quadrant += 2
    if n.z < 0:
        quadrant += 1
    return group[best][1][quadrant]
