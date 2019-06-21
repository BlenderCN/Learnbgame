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

# length of file path strings
MAX_QPATH = 64 # even though I cannot change this: If I changed this I'd need to replace a lot of hardcoded 64s

# gla format
GLA_IDENT = b"2LGA"
GLA_VERSION = 6

# glm format
GLM_IDENT = b'2LGM'
GLM_VERSION = 6

SURFACEFLAG_TAG = 0b1
SURFACEFLAG_OFF = 0b10

BONELENGTH = 4

# 0.999 = cos 2.5, 0.996 = cos 5, 0.990 = cos 8
# 0.999 is okay for the player model, but the atst is somewhat less exact
BONE_ANGLE_ERROR_MARGIN = 0.996 # cosine of allowed angle between bone directions for them to be considered equal

# bones to which the parent (with multiple children) should preferably connect
PRIORITY_BONES = {
    'NONE' : [],
    'JKA_HUMANOID' : [
        #legs - ignore [lr]femurX
        "rtibia",
        "ltibia",
        #arms
        #ignore [lr]humerusX
        "rradius",
        "lradius",
        #ignore [lr]radiusX (and all the hand stuff)
        "rhand",
        "lhand",
        #spine - ignore shoulders and legs
        "cervical",
        "lower_lumbar"
    ]
}

# bones that get different parents
# bone index -> new parent index
PARENT_CHANGES = {
    'NONE' : {},
    'JKA_HUMANOID' : {
        #  shoulder fixes
        25 : 24, #rhumerus gets parent rclavical
        38 : 37, #lhumerus gets parent lclavical
        
        #  hand fixes
        #r_d[124]_j1 to rhand
        30 : 29,
        32 : 29,
        34 : 29,
        36 : 29, #rhang_tag_bone to rhand
        #r_d[124]_j2 to r_d[124]_j2
        31 : 30,
        33 : 32,
        35 : 34,
        #l_d[124]_j1 to lhand
        43 : 42,
        45 : 42,
        47 : 42,
        51 : 42, #lhang_tag_bone to lhand
        #l_d[124]_j2 to l_d[124]_j2
        44 : 43,
        46 : 45,
        48 : 47
    }
}