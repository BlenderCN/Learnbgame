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
    ("sternum-0",           "v", 1528),
    ("sternum",             "l", ((0.8, "sternum-0"), (0.2, "neck"))),

    ("l-clav-end",          "vl", ((0.6, 8077), (0.4, 8237))),
    ("l-clav-1",            "l", ((0.5, "l-clavicle"), (0.5, "l-clav-end"))),

    ("r-clav-end",          "vl", ((0.6, 1385), (0.4, 1559))),
    ("r-clav-1",            "l", ((0.5, "r-clavicle"), (0.5, "r-clav-end"))),

    ("l-upper-arm",         "vl", ((0.5, 8121), (0.5, 8361))),
    ("l-deltoid-1",         "vl", ((0.5, 8077), (0.5, 8243))),
    ("l-deltoid-2",         "vl", ((0.5, 8320), (0.5, 8347))),

    ("r-upper-arm",         "vl", ((0.5, 1433), (0.5, 1689))),
    ("r-deltoid-1",         "vl", ((0.5, 1385), (0.5, 1565))),
    ("r-deltoid-2",         "vl", ((0.5, 1648), (0.5, 1675))),

    ("l-serratus-ik",       "l", ((-0.5, "l-serratus-1"), (1.5, "l-serratus-2"))),
    ("r-serratus-ik",       "l", ((-0.5, "r-serratus-1"), (1.5, "r-serratus-2"))),

    ("r-serratus-ik",       "l", ((-0.5, "r-serratus-1"), (1.5, "r-serratus-2"))),
    ("r-serratus-ik",       "l", ((-0.5, "r-serratus-1"), (1.5, "r-serratus-2"))),

    ("l-scapula-1",         "vl", ((0.05, 8215), (0.95, 8263))),
    ("l-scapula-2",         "vl", ((0.2, 8073), (0.8, 10442))),

    ("r-scapula-1",         "vl", ((0.05, 1535), (0.95, 1585))),
    ("r-scapula-2",         "vl", ((0.2, 1381), (0.8, 3775))),

    ("l-elbow-tip",         "v", 10058),
    ("r-elbow-tip",         "v", 3390),

    ("l-elbow",             "n", ("l-elbow-raw", "l-upper-arm", "l-elbow-tip", "l-hand")),
    ("r-elbow",             "n", ("r-elbow-raw", "r-upper-arm", "r-elbow-tip", "r-hand")),

    ("l-forearm-1",         "l", ((0.75, "l-elbow"), (0.25, "l-hand"))),
    ("r-forearm-1",         "l", ((0.75, "r-elbow"), (0.25, "r-hand"))),

    ("l-wrist-top",         "v", 10548),
    ("l-hand-end",          "v", 9944),

    ("r-wrist-top",         "v", 3883),
    ("r-hand-end",          "v", 3276),
]


HeadsTails = {
    "DEF-sternum" :             ("neck", "sternum"),

    "clavicle.L" :          ("l-clavicle", "l-clav-end"),
    "scap-parent.L" :       ("l-clavicle", "l-clav-1"),
    "DEF-scapula.L" :       ("l-scapula-2", "l-scapula-1"),
    "serratusIk.L" :        ("l-serratus-ik", ("l-serratus-ik", ysmall)),
    "DEF-deltoid.L" :        ("l-deltoid-1", "l-deltoid-2"),
    "shoulderIk.L" :         ("l-deltoid-2", ("l-deltoid-2", ysmall)),

    "clavicle.R" :          ("r-clavicle", "r-clav-end"),
    "scap-parent.R" :       ("r-clavicle", "r-clav-1"),
    "DEF-scapula.R" :       ("r-scapula-2", "r-scapula-1"),
    "serratusIk.R" :        ("r-serratus-ik", ("r-serratus-ik", ysmall)),
    "DEF-deltoid.R" :       ("r-deltoid-1", "r-deltoid-2"),
    "shoulderIk.R" :        ("r-deltoid-2", ("r-deltoid-2", ysmall)),

    "shoulder01.L" :          ("l-clav-end", "l-upper-arm"),
    "upper_arm.L" :         ("l-upper-arm", "l-elbow"),
    "forearm.L" :           ("l-elbow", "l-hand"),
    "DEF-elbow_fan.L" :         ("l-elbow", "l-forearm-1"),
    "hand.L" :              ("l-hand", "l-hand-end"),

    "shoulder01.R" :          ("r-clav-end", "r-upper-arm"),
    "upper_arm.R" :         ("r-upper-arm", "r-elbow"),
    "forearm.R" :           ("r-elbow", "r-hand"),
    "DEF-elbow_fan.R" :         ("r-elbow", "r-forearm-1"),
    "hand.R" :              ("r-hand", "r-hand-end"),

}

Planes = {
    "PlaneArm.L" :         ('l-upper-arm', 'l-elbow-tip', 'l-hand'),
    "PlaneHand.L" :        ('l-plane-hand-1', 'l-plane-hand-2', 'l-plane-hand-3'),
    "PlaneArm.R" :         ('r-upper-arm', 'r-elbow-tip', 'r-hand'),
    "PlaneHand.R" :        ('r-plane-hand-1', 'r-plane-hand-2', 'r-plane-hand-3'),
}

Armature = {
    "DEF-sternum" :         (0, "chest-1", F_DEF|F_CON, L_DEF),

    "clavicle.L" :          (0, "chest-1", F_DEF, L_SPINE|L_LARMFK|L_LARMIK),
    "shoulder01.L" :          (0, "clavicle.L", 0, L_HELP),
    "scap-parent.L" :       (0, "chest-1", 0, L_HELP),
    "DEF-scapula.L" :       (0, "scap-parent.L", F_DEF, L_DEF),

    "clavicle.R" :          (0, "chest-1", F_DEF, L_SPINE|L_RARMFK|L_RARMIK),
    "shoulder01.R" :          (0, "clavicle.R", 0, L_HELP),
    "scap-parent.R" :       (0, "chest-1", 0, L_HELP),
    "DEF-scapula.R" :       (0, "scap-parent.R", F_DEF, L_DEF),

    "DEF-deltoid.L" :       (0, "clavicle.L", F_DEF, L_DEF),
    "DEF-deltoid.R" :       (0, "clavicle.R", F_DEF, L_DEF),

    "pectIk.L" :            (0, "clavicle.L", 0, L_HELP),
    "pectIk.R" :            (0, "clavicle.R", 0, L_HELP),

    "upper_arm.L" :         ("PlaneArm.L", "shoulder01.L", F_DEF, L_LARMFK),
    "shoulderIk.L" :        (0, "upper_arm.L", 0, L_HELP),
    "serratusIk.L" :        (0, "upper_arm.L", 0, L_HELP),
    "forearm.L" :           ("PlaneArm.L", "upper_arm.L", F_DEF|F_CON, L_LARMFK, P_YZX),
    "hand.L" :              ("PlaneHand.L", "forearm.L", F_DEF|F_CON, L_LARMFK, P_YZX),

    "upper_arm.R" :         ("PlaneArm.R", "shoulder01.R", F_DEF, L_RARMFK),
    "shoulderIk.R" :        (0, "upper_arm.R", 0, L_HELP),
    "serratusIk.R" :        (0, "upper_arm.R", 0, L_HELP),
    "forearm.R" :           ("PlaneArm.R", "upper_arm.R", F_DEF|F_CON, L_RARMFK, P_YZX),
    "hand.R" :              ("PlaneHand.R", "forearm.R", F_DEF|F_CON, L_RARMFK, P_YZX),

    "DEF-elbow_fan.L" :         ("PlaneArm.L", "upper_arm.L", F_DEF|F_CON, L_DEF, P_YZX),
    "DEF-elbow_fan.R" :         ("PlaneArm.R", "upper_arm.R", F_DEF|F_CON, L_DEF, P_YZX),
}


RotationLimits = {
    'clavicle.L' :      (-16,50, -70,70,  -45,45),
    'clavicle.R' :      (-16,50,  -70,70,  -45,45),
    'upper_arm.L' :     (-45,135, -60,60, -135,135),
    'upper_arm.R' :     (-45,135, -60,60, -135,135),
    #'forearm.L' :       (-45,180, 0,0, -90,90),
    #'forearm.R' :       (-45,180, 0,0, -90,90),
    'hand.L' :          (-90,70, -90,90, -20,20),
    'hand.R' :          (-90,70, -90,90, -20,20),
}

Locks = {
    'forearm.L' :       (0,1,0),
    'forearm.R' :       (0,1,0),
}

CustomShapes = {
    "clavicle.L" :      "GZM_Shoulder",
    "clavicle.R" :      "GZM_Shoulder",
    "upper_arm.L" :     "GZM_Circle025",
    "upper_arm.R" :     "GZM_Circle025",
    "forearm.L" :       "GZM_Circle025",
    "forearm.R" :       "GZM_Circle025",
    "hand.L" :          "GZM_Hand",
    "hand.R" :          "GZM_Hand",
}

clavInf = 0.4

Constraints = {
    "DEF-sternum" : [("CopyRot", C_LOCAL, 0.2, ["neck", "neck", (1,0,0), (0,0,0), False])],

    "DEF-deltoid.L" : [
        ("IK", 0, 1, ["shoulderIk.L", "shoulderIk.L", 1, None, (1,0,1)])
        ],

    "DEF-deltoid.R" : [
        ("IK", 0, 1, ["shoulderIk.R", "shoulderIk.R", 1, None, (1,0,1)])
        ],

    "scap-parent.L" : [
        ("CopyRot", C_LOCAL, 0.5, ["clavicle.L", "clavicle.L", (1,0,1), (0,0,0), False])
        ],

    "scap-parent.R" : [
        ("CopyRot", C_LOCAL, 0.5, ["clavicle.R", "clavicle.R", (1,0,1), (0,0,0), False])
        ],

    "DEF-elbow_fan.L" : [
        ("CopyRot", 0, 0.75, ["forearm.L", ("DEF-forearm.01.L", "forearm.L"), (1,1,1), (0,0,0), False])
        ],

    "DEF-elbow_fan.R" : [
        ("CopyRot", 0, 0.75, ["forearm.R", ("DEF-forearm.01.R", "forearm.R"), (1,1,1), (0,0,0), False])
        ],

}
'''
    "DEF-clav-0.L" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.L", "clavicle.L", (1,1,1), (0,0,0), False])],
    "DEF-clav-1.L" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.L", "clavicle.L", (1,1,1), (0,0,0), False])],
    "DEF-clav-2.L" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.L", "clavicle.L", (1,1,1), (0,0,0), False])],
    "DEF-clav-3.L" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.L", "clavicle.L", (1,1,1), (0,0,0), False])],

    "DEF-clav-0.R" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.R", "clavicle.R", (1,1,1), (0,0,0), False])],
    "DEF-clav-1.R" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.R", "clavicle.R", (1,1,1), (0,0,0), False])],
    "DEF-clav-2.R" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.R", "clavicle.R", (1,1,1), (0,0,0), False])],
    "DEF-clav-3.R" : [("CopyRot", C_LOCAL, clavInf, ["clavicle.R", "clavicle.R", (1,1,1), (0,0,0), False])],
'''
