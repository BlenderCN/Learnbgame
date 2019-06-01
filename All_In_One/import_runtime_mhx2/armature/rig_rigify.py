# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from .flags import *

Joints = [
    ('l-ball-1',            'vo', (12889, -0.5, 0, 0)),
    ('l-ball-2',            'vo', (12889, 0.5, 0, 0)),
    ('r-ball-1',            'vo', (6292, 0.5, 0, 0)),
    ('r-ball-2',            'vo', (6292, -0.5, 0, 0)),
]

HeadsTails = {
    'heel.L' :             ('l-ankle', 'l-heel'),
    'heel.02.L' :          ('l-ball-1', 'l-ball-2'),

    'heel.R' :             ('r-ankle', 'r-heel'),
    'heel.02.R' :          ('r-ball-1', 'r-ball-2'),
}

Armature = {
    'heel.L' :             (180*D, 'shin.L', F_CON, L_HELP),
    'heel.02.L' :          (0, 'heel.L', 0, L_HELP),
    'heel.R' :             (180*D, 'shin.R', F_CON, L_HELP),
    'heel.02.R' :          (0, 'heel.R', 0, L_HELP),
}
