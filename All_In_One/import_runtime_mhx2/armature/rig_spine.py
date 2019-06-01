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
    ("cjoint-0",             "vl", ((0.5, 4267), (0.5, 4376))),
    ("cjoint-1",             "vl", ((0.5, 4269), (0.5, 10899))),
    ("cjoint-2",             "vl", ((0.5, 4140), (0.5, 10783))),
    ("cjoint-3",             "vl", ((0.5, 3977), (0.5, 10638))),
    ("cjoint-4",             "vl", ((0.5, 1623), (0.5, 8295))),

    ("neck",                "vl", ((0.3, 809), (0.7, 1491))),
    ("neck-1",              "vl", ((0.5, 825), (0.5, 7536))),

    ("l-serratus-2",        "v", 8110),
    ("r-serratus-2",        "v", 1422),
    ("l-serratus-1",        "l", ((0.3, "r-serratus-2"), (0.7, "l-serratus-2"))),
    ("r-serratus-1",        "l", ((0.3, "l-serratus-2"), (0.7, "r-serratus-2"))),

    ("l-breast",            "vl", ((0.5, 1892), (0.5, 10720))),
    ("r-breast",            "vl", ((0.5, 1892), (0.5, 4065))),
    ("l-nipple",            "v", 8462),
    ("r-nipple",            "v", 1790),

    ("l-pect-ik",           "l", ((-0.2, "cjoint-4"), (1.2, "l-breast"))),
    ("r-pect-ik",           "l", ((-0.2, "cjoint-4"), (1.2, "r-breast"))),

    ("pubis",               "v", 4372),
    ("pubis-1",             "v", 4259),
    ("pubis-2",             "v", 4370),
]

PenisJoints = [
    ("penis-1",             "vl", ((0.5, 15152), (0.5, 15169))),
    ("penis-2",             "vl", ((0.5, 15272), (0.5, 15274))),
    ("penis-3",             "vl", ((0.5, 15320), (0.5, 15326))),
    ("penis-4",             "v", 15319),

    ("l-scrotum-1",         "vl", ((0.5, 15216), (0.5, 15217))),
    ("r-scrotum-1",         "vl", ((0.5, 15238), (0.5, 15252))),
    ("l-scrotum-2",         "v", 15230),
    ("r-scrotum-2",         "v", 15231),

]

HeadsTails = {
    "hips" :               ("cjoint-0", "cjoint-1"),
    "spine" :              ("cjoint-1", "cjoint-2"),
    "spine-1" :            ("cjoint-2", "cjoint-3"),
    "chest" :              ("cjoint-3", "cjoint-4"),
    "chest-1" :            ("cjoint-4", "neck"),
    "neck" :               ("neck", "neck-1"),
    "neck-1" :             ("neck-1", "head"),
    "head" :               ("head", "head-2"),

    "DEF-serratus.L" :     ("l-serratus-1", "l-serratus-2"),
    "DEF-serratus.R" :     ("r-serratus-1", "r-serratus-2"),

    "DEF-pect.L" :         ("cjoint-4", "l-breast"),
    "DEF-pect.R" :         ("cjoint-4", "r-breast"),

    "breast.L" :           ("l-breast", "l-nipple"),
    "breast.R" :           ("r-breast", "r-nipple"),

    "pectIk.L" :           ("l-pect-ik", ("l-pect-ik", ysmall)),
    "pectIk.R" :           ("r-pect-ik", ("r-pect-ik", ysmall)),

    "skull" :              ("head-2", ("head-2", ysmall)),

    "pubis" :              ("pelvis", "pubis"),
}

PenisHeadsTails = {
    "penis_1" :            ("penis-1", "penis-2"),
    "penis_2" :            ("penis-2", "penis-3"),
    "penis_3" :            ("penis-3", "penis-4"),

    "scrotum.L" :          ("l-scrotum-1", "l-scrotum-2"),
    "scrotum.R" :          ("r-scrotum-1", "r-scrotum-2"),
}

Planes = {
}

Armature = {
    "hips" :               (0, None, F_DEF, L_SPINE),
    "spine" :              (0, "hips", F_DEF|F_CON, L_SPINE),
    "spine-1" :            (0, "spine", F_DEF|F_CON, L_SPINE),
    "chest" :              (0, "spine-1", F_DEF|F_CON, L_SPINE),
    "chest-1" :            (0, "chest", F_DEF|F_CON, L_SPINE),
    "neck" :               (0, "chest-1", F_DEF|F_CON, L_SPINE),
    "neck-1" :             (0, "neck", F_DEF|F_CON, L_SPINE),
    "head" :               (0, "neck-1", F_DEF|F_CON, L_SPINE),

    "DEF-serratus.L" :     (0, "chest", F_DEF, L_DEF),
    "DEF-serratus.R" :     (0, "chest", F_DEF, L_DEF),
    "DEF-pect.L" :         (0, "chest", 0, L_DEF),
    "DEF-pect.R" :         (0, "chest", 0, L_DEF),
    "breast.L" :           (0, "DEF-pect.L", F_DEF, L_DEF),
    "breast.R" :           (0, "DEF-pect.R", F_DEF, L_DEF),

}

# Terminators needed by OpenSim

TerminatorArmature = {
    "skull" :               (0, "head", F_CON, L_HELP),
    "toe_end.L" :           (0, "toe.L", F_CON, L_HELP),
    "toe_end.R" :           (0, "toe.R", F_CON, L_HELP),
}

PenisArmature = {
    "penis_1" :             (0, "hips", F_DEF|F_SCALE|F_NOLOCK, L_TWEAK),
    "penis_2" :             (0, "penis_1", F_DEF|F_SCALE|F_CON, L_TWEAK),
    "penis_3" :             (0, "penis_2", F_DEF|F_SCALE|F_CON, L_TWEAK),
    "scrotum.L" :           (0, "hips", F_DEF|F_SCALE|F_NOLOCK, L_TWEAK),
    "scrotum.R" :           (0, "hips", F_DEF|F_SCALE|F_NOLOCK, L_TWEAK),
}

RotationLimits = {
    "spine" :           (-30,30, -30,30, -30,30),
    "spine-1" :         (-30,30, -30,30, -30,30),
    "chest" :           (-20,20, 0,0, -20,20),
    "chest-1" :         (-20,20, 0,0, -20,20),
    "neck" :            (-45,45, -45,45, -60,60),
}

Locks = {}

CustomShapes = {
    "root" :            "GZM_Root",
    "hips" :            "GZM_CrownHips",
    "spine" :           "GZM_CircleSpine",
    "spine-1" :         "GZM_CircleSpine",
    "chest" :           "GZM_CircleSpine",
    "chest-1" :         "GZM_CircleChest",
    "neck" :            "GZM_Neck",
    "neck-1" :          "GZM_Neck",
    "head" :            "GZM_Head",
    "breast.L" :        "GZM_Breast_L",
    "breast.R" :        "GZM_Breast_R",
}

Constraints = {
    "DEF-serratus.L" : [
        ("IK", 0, 0.2, ["serratusIk.L", "serratusIk.L", 1, None, (1,0,1)])
        ],

    "DEF-serratus.R" : [
        ("IK", 0, 0.2, ["serratusIk.R", "serratusIk.R", 1, None, (1,0,1)])
        ],

    "DEF-pect.L" : [
        ("IK", 0, 0.2, ["pectIk.L", "pectIk.L", 1, None, (1,0,1)])
        ],

    "DEF-pect.R" : [
        ("IK", 0, 0.2, ["pectIk.R", "pectIk.R", 1, None, (1,0,1)])
        ],


}

