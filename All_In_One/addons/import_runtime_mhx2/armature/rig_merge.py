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

PalmMergers = {
    "hand.L" : ("hand.L",
        ("palm_index.L", "palm_middle.L", "palm_ring.L", "palm_pinky.L", "thumb.01.L")),
    "hand.R" : ("hand.R",
        ("palm_index.R", "palm_middle.R", "palm_ring.R", "palm_pinky.R", "thumb.01.R")),
}

FingerMergers = {
    "f_index.01.L" : ("f_index.03.L", ("f_index.01.L", "f_index.02.L", "f_index.03.L")),
    "f_ring.01.L" : ("f_middle.03.L", ("f_middle.01.L", "f_middle.02.L", "f_middle.03.L", "f_ring.01.L", "f_ring.02.L", "f_ring.03.L", "f_pinky.01.L", "f_pinky.02.L", "f_pinky.03.L")),
    "f_index.01.R" : ("f_index.03.R", ("f_index.01.R", "f_index.02.R", "f_index.03.R")),
    "f_ring.01.R" : ("f_middle.03.R", ("f_middle.01.R", "f_middle.02.R", "f_middle.03.R", "f_ring.01.R", "f_ring.02.R", "f_ring.03.R", "f_pinky.01.R", "f_pinky.02.R", "f_pinky.03.R")),
}

HeadMergers = {
    "head" : ("head", ("head", "lolid.L", "lolid.R", "uplid.L", "uplid.R")),
    "jaw" : ("jaw", ("jaw", "tongue_base", "tongue_mid", "tongue_tip")),
}

NeckMergers = {
    "neck" : ("neck-1", ("neck", "neck-1")),
}

ChestMergers = {
    "chest" : ("chest-1", ("chest", "chest-1", "breast.L", "breast.R")),
}

SpineMergers = {
    "spine" : ("spine-1", ("spine", "spine-1")),
}

ShoulderMergers = {
    "chest" : ("chest", (
        "DEF-serratus.L", "DEF-serratus.R", "serratusIk.L", "serratusIk.R",
        "DEF-pect.L", "DEF-pect.R", "pectIk.L", "pectIk.R",
        )),
    "chest-1" : ("chest-1", (
        "chest-1", "DEF-sternum",
        "DEF-scapula.L", "scapAim.L",
        "DEF-scapula.R", "scapAim.R",
        )),
    "clavicle.L" : ("clavicle.L", (
        "clavicle.L", "DEF-clav-0.L", "DEF-clav-1.L", "DEF-clav-2.L", "DEF-clav-3.L", "DEF-clav-4.L", "DEF-deltoid-1.L",
        "shoulder01.L", "scap-parent.L",
        )),
    "upper_arm.L" : ("upper_arm.L", (
        "upper_arm.L", "DEF-deltoid-2.L", "shoulderIk.L"
        )),
    "clavicle.R" : ("clavicle.R", (
        "clavicle.R", "DEF-clav-0.R", "DEF-clav-1.R", "DEF-clav-2.R", "DEF-clav-3.R", "DEF-clav-4.R", "DEF-deltoid-1.R",
        "shoulder01.R", "scap-parent.R",
        )),
    "upper_arm.R" : ("upper_arm.R", (
        "upper_arm.R", "DEF-deltoid-2.R", "shoulderIk.R"
        )),
}

HipMergers = {
    "hips" : ("hips", (
        "hips", "pelvis.L", "pelvis.R", "DEF-hip.L", "DEF-hip.R", "hipIk.L", "hipIk.R",
        "DEF-gluteus.L", "DEF-gluteus.R", "gluteusIk.L", "gluteusIk.R"
        ))
}

FeetMergers = {
    "foot.L" : ("toe.L", ("foot.L", "toe.L")),
    "foot.R" : ("toe.R", ("foot.R", "toe.R")),
}

ToesMergers = {
    "toe.L" : ("toe.L", (
        "toe.L", "toe1-2.L", "toe1-3.L",
        "toe2-1.L", "toe2-2.L", "toe2-3.L",
        "toe3-1.L", "toe3-2.L", "toe3-3.L",
        "toe4-1.L", "toe4-2.L", "toe4-3.L",
        "toe5-1.L", "toe5-2.L", "toe5-3.L",
        )),
    "toe.R" : ("toe.R", (
        "toe.R", "toe1-2.R", "toe1-3.R",
        "toe2-1.R", "toe2-2.R", "toe2-3.R",
        "toe3-1.R", "toe3-2.R", "toe3-3.R",
        "toe4-1.R", "toe4-2.R", "toe4-3.R",
        "toe5-1.R", "toe5-2.R", "toe5-3.R",
        )),
}

PenisMergers = {
    "hips" : ("hips", (
        "hips", "penis_1", "penis_2", "penis_3", "scrotum.L", "scrotum.R"
        ))
}

ConstraintMergers = {
    "shin.L" : ("shin.L", ("shin.L", "DEF-knee_fan.L")),
    "shin.R" : ("shin.R", ("shin.R", "DEF-knee_fan.R")),
    "forearm.L" : ("forearm.L", ("forearm.L", "DEF-elbow_fan.L")),
    "forearm.R" : ("forearm.R", ("forearm.R", "DEF-elbow_fan.R")),
}
