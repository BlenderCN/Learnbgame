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

Joints1 = [
    ("l-gluteus-1",         "vl", ((0.1, 10955), (0.9, 10859))),
    ("r-gluteus-1",         "vl", ((0.1, 4327), (0.9, 4224))),
    ("l-gluteus-2",         "l", ((0.8, "l-upper-leg"), (0.2, "l-knee"))),
    ("r-gluteus-2",         "l", ((0.8, "r-upper-leg"), (0.2, "r-knee"))),

    ("l-hip-ik",            "v", 10920),
    ("r-hip-ik",            "v", 4290),
    ("l-hip",               "l", ((0.7, "l-hip-ik"), (0.3, "pelvis"))),
    ("r-hip",               "l", ((0.7, "r-hip-ik"), (0.3, "pelvis"))),
]

Joints2 = [
    ("l-knee-tip",          "v", 11223),
    ("r-knee-tip",          "v", 4605),

    ("l-knee",              "n", ("l-knee-raw", "l-upper-leg", "l-knee-tip", "l-ankle")),
    ("r-knee",              "n", ("r-knee-raw", "r-upper-leg", "r-knee-tip", "r-ankle")),

    ("l-shin-1",            "l", ((0.75, "l-knee"), (0.25, "l-ankle"))),
    ("r-shin-1",            "l", ((0.75, "r-knee"), (0.25, "r-ankle"))),

    ("l-toe-2",             "p", ("l-foot-2", "l-foot-1", "l-foot-2")),
    ("r-toe-2",             "p", ("r-foot-2", "r-foot-1", "r-foot-2")),

    ("l-heel-y",            "v", 12877),
    ("l-heel-z",            "v", 12442),
    ("l-heel",              "p", ("l-toe-2", "l-foot-1", "l-heel-z")),
    ("r-heel-y",            "v", 6280),
    ("r-heel-z",            "v", 5845),
    ("r-heel",              "p", ("r-toe-2", "r-foot-1", "r-heel-z")),
]


HeadsTails = {
    "pelvis.L" :           ("cjoint-0", "l-upper-leg"),
    "thigh.L" :            ("l-upper-leg", "l-knee"),
    "shin.L" :             ("l-knee", "l-ankle"),
    "foot.L" :             ("l-ankle", "l-foot-1"),
    "toe.L" :              ("l-foot-1", "l-toe-2"),

    "pelvis.R" :           ("cjoint-0", "r-upper-leg"),
    "thigh.R" :            ("r-upper-leg", "r-knee"),
    "shin.R" :             ("r-knee", "r-ankle"),
    "foot.R" :             ("r-ankle", "r-foot-1"),
    "toe.R" :              ("r-foot-1", "r-toe-2"),

    "toe_end.L" :          ("l-toe-2", ("l-toe-2", zsmall)),
    "toe_end.R" :          ("r-toe-2", ("r-toe-2", zsmall)),

    "DEF-knee_fan.L" :         ("l-knee", "l-shin-1"),
    "DEF-knee_fan.R" :         ("r-knee", "r-shin-1"),

    "DEF-gluteus.L" :          ("l-gluteus-1", "l-gluteus-2"),
    "DEF-gluteus.R" :          ("r-gluteus-1", "r-gluteus-2"),
    "gluteusIk.L" :        ("l-gluteus-2", ("l-gluteus-2", ysmall)),
    "gluteusIk.R" :        ("r-gluteus-2", ("r-gluteus-2", ysmall)),

    "DEF-hip.L" :              ("pelvis", "l-hip"),
    "DEF-hip.R" :              ("pelvis", "r-hip"),
    "hipIk.L" :            ("l-hip-ik", ("l-hip-ik", ysmall)),
    "hipIk.R" :            ("r-hip-ik", ("r-hip-ik", ysmall)),

}

Planes = {
    "PlaneLeg.L" :         ("l-upper-leg", "l-knee-tip", "l-ankle"),
    "PlaneFoot.L" :        ("l-ankle", "l-toe-2", "l-foot-1"),
    "PlaneLeg.R" :         ("r-upper-leg", "r-knee-tip", "r-ankle"),
    "PlaneFoot.R" :        ("r-ankle", "r-toe-2", "r-foot-1"),
}

Armature = {
    "pelvis.L" :           (0, "hips", F_DEF, L_TWEAK),
    "thigh.L" :            ("PlaneLeg.L", "pelvis.L", F_DEF, L_LLEGFK),
    "shin.L" :             ("PlaneLeg.L", "thigh.L", F_DEF|F_CON, L_LLEGFK, P_YZX),
    "foot.L" :             ("PlaneFoot.L", "shin.L", F_DEF|F_CON, L_LLEGFK, P_YZX),
    "toe.L" :              ("PlaneFoot.L", "foot.L", F_DEF|F_CON, L_LLEGFK, P_YZX),

    "pelvis.R" :           (0, "hips", F_DEF, L_TWEAK),
    "thigh.R" :            ("PlaneLeg.R", "pelvis.R", F_DEF, L_RLEGFK),
    "shin.R" :             ("PlaneLeg.R", "thigh.R", F_DEF|F_CON, L_RLEGFK, P_YZX),
    "foot.R" :             ("PlaneFoot.R", "shin.R", F_DEF|F_CON, L_RLEGFK, P_YZX),
    "toe.R" :              ("PlaneFoot.R", "foot.R", F_DEF|F_CON, L_RLEGFK, P_YZX),

    "DEF-gluteus.L" :      (0, "hips", F_DEF, L_DEF),
    "DEF-gluteus.R" :      (0, "hips", F_DEF, L_DEF),
    "gluteusIk.L" :        (0, "thigh.L", 0, L_HELP),
    "gluteusIk.R" :        (0, "thigh.R", 0, L_HELP),

    "DEF-hip.L" :          (0, "hips", F_DEF, L_DEF),
    "DEF-hip.R" :          (0, "hips", F_DEF, L_DEF),
    "hipIk.L" :            (0, "thigh.L", 0, L_HELP),
    "hipIk.R" :            (0, "thigh.R", 0, L_HELP),

    "DEF-knee_fan.L" :         ("PlaneLeg.L", "thigh.L", F_DEF|F_CON, L_DEF, P_YZX),
    "DEF-knee_fan.R" :         ("PlaneLeg.R", "thigh.R", F_DEF|F_CON, L_DEF, P_YZX),
}

RotationLimits = {
    "thigh.L" :         (-160,90, -45,45, -140,80),
    "thigh.R" :         (-160,90, -45,45, -80,140),
    "shin.L" :          (0,170, -40,40, 0,0),
    "shin.R" :          (0,170, -40,40, 0,0),
    "foot.L" :          (-90,45, -30,30, -30,30),
    "foot.R" :          (-90,45, -30,30, -30,30),
    "toe.L" :           (-20,60, 0,0, 0,0),
    "toe.R" :           (-20,60, 0,0, 0,0),
}

Locks = {
    "shin.L" :          (0,0,1),
    "shin.R" :          (0,0,1),
    "toe.L" :           (0,1,1),
    "toe.R" :           (0,1,1),
}

CustomShapes = {
    "thigh.L" :         "GZM_Circle025",
    "thigh.R" :         "GZM_Circle025",
    "shin.L" :          "GZM_Circle025",
    "shin.R" :          "GZM_Circle025",
    "foot.L" :          "GZM_Foot",
    "foot.R" :          "GZM_Foot",
    "toe.L" :           "GZM_Toe",
    "toe.R" :           "GZM_Toe",
}

Constraints = {
    "DEF-gluteus.L" : [
        ("IK", 0, 0.5, ["gluteusIk.L", "gluteusIk.L", 1, None, (1,0,1)])
        ],
    "DEF-gluteus.R" : [
        ("IK", 0, 0.5, ["gluteusIk.R", "gluteusIk.R", 1, None, (1,0,1)])
        ],

    "DEF-hip.L" : [
        ("IK", 0, 1.0, ["hipIk.L", "hipIk.L", 1, None, (1,0,1)])
        ],
    "DEF-hip.R" : [
        ("IK", 0, 1.0, ["hipIk.R", "hipIk.R", 1, None, (1,0,1)])
        ],

    "DEF-knee_fan.L" : [
        ("CopyRot", 0, 0.75, ["shin.L", ("DEF-shin.01.L", "shin.L"), (1,1,1), (0,0,0), False])
        ],

    "DEF-knee_fan.R" : [
        ("CopyRot", 0, 0.75, ["shin.R", ("DEF-shin.01.R", "shin.R"), (1,1,1), (0,0,0), False])
        ],
}

