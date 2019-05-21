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
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from .flags import *
from .rig_joints import *

Joints = [
    ('l-wrist-top',         'v', 10548),
    ('l-hand-end',          'v', 9944),
    ('r-wrist-top',         'v', 3883),
    ('r-hand-end',          'v', 3276),

    ('l-palm-02',           'vl', ((0.5, 9906), (0.5, 10500))),
    ('l-palm-03',           'vl', ((0.5, 9895), (0.5, 10497))),
    ('l-palm-04',           'vl', ((0.5, 9897), (0.5, 10495))),
    ('l-palm-05',           'vl', ((0.5, 9894), (0.5, 10494))),

    ('r-palm-02',           'vl', ((0.5, 3238), (0.5, 3834))),
    ('r-palm-03',           'vl', ((0.5, 3227), (0.5, 3831))),
    ('r-palm-04',           'vl', ((0.5, 3226), (0.5, 3829))),
    ('r-palm-05',           'vl', ((0.5, 3232), (0.5, 3828))),

    ('l-plane-hand-1',      'v', 10164),
    ('l-plane-hand-2',      'v', 10576),
    ('l-plane-hand-3',      'v', 9779),

    ('r-plane-hand-1',      'v', 3496),
    ('r-plane-hand-2',      'v', 3911),
    ('r-plane-hand-3',      'v', 3111),

    ('l-plane-thumb-1',     'v', 10291),
    ('l-plane-thumb-2',     'v', 9401),
    ('l-plane-thumb-3',     'v', 9365),

    ('l-plane-index-1',     'v', 9773),
    ('l-plane-index-2',     'v', 8638),
    ('l-plane-index-3',     'v', 8694),

    ('l-plane-middle-1',     'v', 9779),
    ('l-plane-middle-2',     'v', 8798),
    ('l-plane-middle-3',     'v', 8886),

    ('l-plane-ring-1',     'v', 9785),
    ('l-plane-ring-2',     'v', 9022),
    ('l-plane-ring-3',     'v', 9078),

    ('l-plane-pinky-1',     'v', 9793),
    ('l-plane-pinky-2',     'v', 9219),
    ('l-plane-pinky-3',     'v', 9270),

    ('r-plane-thumb-1',     'v', 3623),
    ('r-plane-thumb-2',     'v', 2725),
    ('r-plane-thumb-3',     'v', 2697),

    ('r-plane-index-1',     'v', 3105),
    ('r-plane-index-2',     'v', 1970),
    ('r-plane-index-3',     'v', 2026),

    ('r-plane-middle-1',     'v', 3111),
    ('r-plane-middle-2',     'v', 2130),
    ('r-plane-middle-3',     'v', 2218),

    ('r-plane-ring-1',     'v', 3117),
    ('r-plane-ring-2',     'v', 2354),
    ('r-plane-ring-3',     'v', 2410),

    ('r-plane-pinky-1',     'v', 3125),
    ('r-plane-pinky-2',     'v', 2551),
    ('r-plane-pinky-3',     'v', 2602),
]


HeadsTails = {
    'thumb.01.L' :         ('l-finger-1-1', 'l-finger-1-2'),
    'thumb.02.L' :         ('l-finger-1-2', 'l-finger-1-3'),
    'thumb.03.L' :         ('l-finger-1-3', 'l-finger-1-4'),

    'thumb.01.R' :         ('r-finger-1-1', 'r-finger-1-2'),
    'thumb.02.R' :         ('r-finger-1-2', 'r-finger-1-3'),
    'thumb.03.R' :         ('r-finger-1-3', 'r-finger-1-4'),

    'palm_index.L' :       ('l-palm-02', 'l-finger-2-1'),
    'f_index.01.L' :       ('l-finger-2-1', 'l-finger-2-2'),
    'f_index.02.L' :       ('l-finger-2-2', 'l-finger-2-3'),
    'f_index.03.L' :       ('l-finger-2-3', 'l-finger-2-4'),

    'palm_index.R' :       ('r-palm-02', 'r-finger-2-1'),
    'f_index.01.R' :       ('r-finger-2-1', 'r-finger-2-2'),
    'f_index.02.R' :       ('r-finger-2-2', 'r-finger-2-3'),
    'f_index.03.R' :       ('r-finger-2-3', 'r-finger-2-4'),

    'palm_middle.L' :      ('l-palm-03', 'l-finger-3-1'),
    'f_middle.01.L' :      ('l-finger-3-1', 'l-finger-3-2'),
    'f_middle.02.L' :      ('l-finger-3-2', 'l-finger-3-3'),
    'f_middle.03.L' :      ('l-finger-3-3', 'l-finger-3-4'),

    'palm_middle.R' :      ('r-palm-03', 'r-finger-3-1'),
    'f_middle.01.R' :      ('r-finger-3-1', 'r-finger-3-2'),
    'f_middle.02.R' :      ('r-finger-3-2', 'r-finger-3-3'),
    'f_middle.03.R' :      ('r-finger-3-3', 'r-finger-3-4'),

    'palm_ring.L' :        ('l-palm-04', 'l-finger-4-1'),
    'f_ring.01.L' :        ('l-finger-4-1', 'l-finger-4-2'),
    'f_ring.02.L' :        ('l-finger-4-2', 'l-finger-4-3'),
    'f_ring.03.L' :        ('l-finger-4-3', 'l-finger-4-4'),

    'palm_ring.R' :        ('r-palm-04', 'r-finger-4-1'),
    'f_ring.01.R' :        ('r-finger-4-1', 'r-finger-4-2'),
    'f_ring.02.R' :        ('r-finger-4-2', 'r-finger-4-3'),
    'f_ring.03.R' :        ('r-finger-4-3', 'r-finger-4-4'),

    'palm_pinky.L' :       ('l-palm-05', 'l-finger-5-1'),
    'f_pinky.01.L' :       ('l-finger-5-1', 'l-finger-5-2'),
    'f_pinky.02.L' :       ('l-finger-5-2', 'l-finger-5-3'),
    'f_pinky.03.L' :       ('l-finger-5-3', 'l-finger-5-4'),

    'palm_pinky.R' :       ('r-palm-05', 'r-finger-5-1'),
    'f_pinky.01.R' :       ('r-finger-5-1', 'r-finger-5-2'),
    'f_pinky.02.R' :       ('r-finger-5-2', 'r-finger-5-3'),
    'f_pinky.03.R' :       ('r-finger-5-3', 'r-finger-5-4'),
}

Planes = {
    "PlaneThumb.L" :       ('l-plane-thumb-1', 'l-plane-thumb-2', 'l-plane-thumb-3'),
    "PlaneIndex.L" :       ('l-plane-index-1', 'l-plane-index-2', 'l-plane-index-3'),
    "PlaneMiddle.L" :      ('l-plane-middle-1', 'l-plane-middle-2', 'l-plane-middle-3'),
    "PlaneRing.L" :        ('l-plane-ring-1', 'l-plane-ring-2', 'l-plane-ring-3'),
    "PlanePinky.L" :       ('l-plane-pinky-1', 'l-plane-pinky-2', 'l-plane-pinky-3'),

    "PlaneThumb.R" :       ('r-plane-thumb-1', 'r-plane-thumb-2', 'r-plane-thumb-3'),
    "PlaneIndex.R" :       ('r-plane-index-1', 'r-plane-index-2', 'r-plane-index-3'),
    "PlaneMiddle.R" :      ('r-plane-middle-1', 'r-plane-middle-2', 'r-plane-middle-3'),
    "PlaneRing.R" :        ('r-plane-ring-1', 'r-plane-ring-2', 'r-plane-ring-3'),
    "PlanePinky.R" :       ('r-plane-pinky-1', 'r-plane-pinky-2', 'r-plane-pinky-3'),
}

Armature = {
    'thumb.01.L' :         ("PlaneThumb.L", 'hand.L', F_DEF, L_LPALM, P_YZX),
    'thumb.02.L' :         ("PlaneThumb.L", 'thumb.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'thumb.03.L' :         ("PlaneThumb.L", 'thumb.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'thumb.01.R' :         ("PlaneThumb.R", 'hand.R', F_DEF, L_RPALM, P_YZX),
    'thumb.02.R' :         ("PlaneThumb.R", 'thumb.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'thumb.03.R' :         ("PlaneThumb.R", 'thumb.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_index.L' :       ("PlaneIndex.L", 'hand.L', F_DEF, L_LPALM),
    'f_index.01.L' :       ("PlaneIndex.L", 'palm_index.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_index.02.L' :       ("PlaneIndex.L", 'f_index.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_index.03.L' :       ("PlaneIndex.L", 'f_index.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_index.R' :       ("PlaneIndex.R", 'hand.R', F_DEF, L_RPALM),
    'f_index.01.R' :       ("PlaneIndex.R", 'palm_index.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_index.02.R' :       ("PlaneIndex.R", 'f_index.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_index.03.R' :       ("PlaneIndex.R", 'f_index.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_middle.L' :      ("PlaneMiddle.L", 'hand.L', F_DEF, L_LPALM),
    'f_middle.01.L' :      ("PlaneMiddle.L", 'palm_middle.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_middle.02.L' :      ("PlaneMiddle.L", 'f_middle.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_middle.03.L' :      ("PlaneMiddle.L", 'f_middle.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_middle.R' :      ("PlaneMiddle.R", 'hand.R', F_DEF, L_RPALM),
    'f_middle.01.R' :      ("PlaneMiddle.R", 'palm_middle.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_middle.02.R' :      ("PlaneMiddle.R", 'f_middle.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_middle.03.R' :      ("PlaneMiddle.R", 'f_middle.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_ring.L' :        ("PlaneRing.L", 'hand.L', F_DEF, L_LPALM),
    'f_ring.01.L' :        ("PlaneRing.L", 'palm_ring.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_ring.02.L' :        ("PlaneRing.L", 'f_ring.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_ring.03.L' :        ("PlaneRing.L", 'f_ring.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_ring.R' :        ("PlaneRing.R", 'hand.R', F_DEF, L_RPALM),
    'f_ring.01.R' :        ("PlaneRing.R", 'palm_ring.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_ring.02.R' :        ("PlaneRing.R", 'f_ring.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_ring.03.R' :        ("PlaneRing.R", 'f_ring.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),

    'palm_pinky.L' :       ("PlanePinky.L", 'hand.L', F_DEF, L_LPALM),
    'f_pinky.01.L' :       ("PlanePinky.L", 'palm_pinky.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_pinky.02.L' :       ("PlanePinky.L", 'f_pinky.01.L', F_DEF|F_CON, L_LHANDFK, P_YZX),
    'f_pinky.03.L' :       ("PlanePinky.L", 'f_pinky.02.L', F_DEF|F_CON, L_LHANDFK, P_YZX),

    'palm_pinky.R' :       ("PlanePinky.R", 'hand.R', F_DEF, L_RPALM),
    'f_pinky.01.R' :       ("PlanePinky.R", 'palm_pinky.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_pinky.02.R' :       ("PlanePinky.R", 'f_pinky.01.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
    'f_pinky.03.R' :       ("PlanePinky.R", 'f_pinky.02.R', F_DEF|F_CON, L_RHANDFK, P_YZX),
}

RotationLimits = {}

Locks = {
    'thumb.03.L' :      (0,1,1),
    'f_index.02.L' :    (0,1,1),
    'f_index.03.L' :    (0,1,1),
    'f_middle.02.L' :   (0,1,1),
    'f_middle.03.L' :   (0,1,1),
    'f_ring.02.L' :     (0,1,1),
    'f_ring.03.L' :     (0,1,1),
    'f_pinky.02.L' :    (0,1,1),
    'f_pinky.03.L' :    (0,1,1),

    'thumb.03.R' :      (0,1,1),
    'f_index.02.R' :    (0,1,1),
    'f_index.03.R' :    (0,1,1),
    'f_middle.02.R' :   (0,1,1),
    'f_middle.03.R' :   (0,1,1),
    'f_ring.02.R' :     (0,1,1),
    'f_ring.03.R' :     (0,1,1),
    'f_pinky.02.R' :    (0,1,1),
    'f_pinky.03.R' :    (0,1,1),
}

CustomShapes = {}

Constraints = {
     'thumb.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.L', (1,0,1), (0,0,0), True])],
     'thumb.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.L', (1,0,0), (0,0,0), True])],

     'f_index.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.L', (1,0,1), (0,0,0), True])],
     'f_index.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.L', (1,0,0), (0,0,0), True])],
     'f_index.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.L', (1,0,0), (0,0,0), True])],

     'f_middle.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.L', (1,0,1), (0,0,0), True])],
     'f_middle.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.L', (1,0,0), (0,0,0), True])],
     'f_middle.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.L', (1,0,0), (0,0,0), True])],

     'f_ring.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.L', (1,0,1), (0,0,0), True])],
     'f_ring.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.L', (1,0,0), (0,0,0), True])],
     'f_ring.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.L', (1,0,0), (0,0,0), True])],

     'f_pinky.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.L', (1,0,1), (0,0,0), True])],
     'f_pinky.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.L', (1,0,0), (0,0,0), True])],
     'f_pinky.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.L', (1,0,0), (0,0,0), True])],

     'thumb.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.R', (1,0,1), (0,0,0), True])],
     'thumb.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.R', (1,0,0), (0,0,0), True])],

     'f_index.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.R', (1,0,1), (0,0,0), True])],
     'f_index.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.R', (1,0,0), (0,0,0), True])],
     'f_index.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.R', (1,0,0), (0,0,0), True])],

     'f_middle.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.R', (1,0,1), (0,0,0), True])],
     'f_middle.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.R', (1,0,0), (0,0,0), True])],
     'f_middle.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.R', (1,0,0), (0,0,0), True])],

     'f_ring.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.R', (1,0,1), (0,0,0), True])],
     'f_ring.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.R', (1,0,0), (0,0,0), True])],
     'f_ring.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.R', (1,0,0), (0,0,0), True])],

     'f_pinky.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.R', (1,0,1), (0,0,0), True])],
     'f_pinky.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.R', (1,0,0), (0,0,0), True])],
     'f_pinky.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.R', (1,0,0), (0,0,0), True])],

}

PropLRDrivers = [
    ('thumb.02', 'Rot', ['FingerControl'], 'x1'),
    ('thumb.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_index.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_index.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_index.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_middle.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_middle.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_middle.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_ring.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_ring.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_ring.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_pinky.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_pinky.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_pinky.03', 'Rot', ['FingerControl'], 'x1'),
]

