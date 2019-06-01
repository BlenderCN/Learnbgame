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

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------

offs = [0, 0, 0.2]

Joints = [
    ('origin',      'o', ('head', [-3.3, 0.5, 0.0])),
    ('p_face',       'o', ('origin', [0.0, -1.5, 0.0])),
    ('p_brow_in.R',     'o', ('origin', [-0.3, 0.8, 0.0])),
    ('p_brow_in.L',     'o', ('origin', [0.3, 0.8, 0.0])),
    ('p_brow_out.R',     'o', ('origin', [-0.6, 0.8, 0.0])),
    ('p_brow_out.L',     'o', ('origin', [0.6, 0.8, 0.0])),
    ('p_brow_mid',      'o', ('origin', [0.0, 0.8, 0.0])),
    ('p_up_lid.R',        'o', ('origin', [-0.4, 0.6, 0.0])),
    ('p_up_lid.L',        'o', ('origin', [0.4, 0.6, 0.0])),
    ('p_lo_lid.R',        'o', ('origin', [-0.4, 0.2, 0.0])),
    ('p_lo_lid.L',        'o', ('origin', [0.4, 0.2, 0.0])),
    ('p_nose',       'o', ('origin', [0.0, 0.1, 0.0])),
    ('p_cheek.R',        'o', ('origin', [-0.4, 0.0, 0.0])),
    ('p_cheek.L',        'o', ('origin', [0.4, 0.0, 0.0])),
    ('p_up_lip_mid',       'o', ('origin', [0.0, -0.2, 0.0])),
    ('p_lo_lip_mid',       'o', ('origin', [0.0, -0.8, 0.0])),
    ('p_mouth_mid',       'o', ('origin', [0.0, -0.5, 0.0])),
    ('p_up_lip.R',        'o', ('origin', [-0.25, -0.3, 0.0])),
    ('p_up_lip.L',        'o', ('origin', [0.25, -0.3, 0.0])),
    ('p_lo_lip.R',        'o', ('origin', [-0.25, -0.7, 0.0])),
    ('p_lo_lip.L',        'o', ('origin', [0.25, -0.7, 0.0])),
    ('p_mouth_in.R',        'o', ('origin', [-0.25, -0.5, 0.0])),
    ('p_mouth_in.L',        'o', ('origin', [0.25, -0.5, 0.0])),
    ('p_mouth_out.R',        'o', ('origin', [-0.5, -0.5, 0.0])),
    ('p_mouth_out.L',        'o', ('origin', [0.5, -0.5, 0.0])),
    ('p_tongue',     'o', ('origin', [0.45, -1.5, 0.0])),
    ('p_jaw',        'o', ('origin', [0.0, -1.1, 0.0])),
]

HeadsTails = {
    'p_face' :          ('p_face', ('p_face', [0,0,-1])),
    'p_face_display' :      ('origin', ('origin', [0,0,-1])),
    'p_brow_in.R' :        ('p_brow_in.R', ('p_brow_in.R', offs)),
    'p_brow_in.L' :        ('p_brow_in.L', ('p_brow_in.L', offs)),
    'p_brow_out.R' :        ('p_brow_out.R', ('p_brow_out.R', offs)),
    'p_brow_out.L' :        ('p_brow_out.L', ('p_brow_out.L', offs)),
    'p_brow_mid' :         ('p_brow_mid', ('p_brow_mid', offs)),
    'p_up_lid.R' :       ('p_up_lid.R', ('p_up_lid.R', offs)),
    'p_up_lid.L' :       ('p_up_lid.L', ('p_up_lid.L', offs)),
    'p_lo_lid.R' :       ('p_lo_lid.R', ('p_lo_lid.R', offs)),
    'p_lo_lid.L' :       ('p_lo_lid.L', ('p_lo_lid.L', offs)),
    'p_cheek.R' :       ('p_cheek.R', ('p_cheek.R', offs)),
    'p_cheek.L' :       ('p_cheek.L', ('p_cheek.L', offs)),
    'p_nose' :          ('p_nose', ('p_nose', offs)),
    'p_up_lip_mid' :      ('p_up_lip_mid', ('p_up_lip_mid', offs)),
    'p_lo_lip_mid' :      ('p_lo_lip_mid', ('p_lo_lip_mid', offs)),
    'p_mouth_mid' :      ('p_mouth_mid', ('p_mouth_mid', offs)),
    'p_up_lip.R' :       ('p_up_lip.R', ('p_up_lip.R', offs)),
    'p_up_lip.L' :       ('p_up_lip.L', ('p_up_lip.L', offs)),
    'p_lo_lip.R' :       ('p_lo_lip.R', ('p_lo_lip.R', offs)),
    'p_lo_lip.L' :       ('p_lo_lip.L', ('p_lo_lip.L', offs)),
    'p_mouth_in.R' :       ('p_mouth_in.R', ('p_mouth_in.R', offs)),
    'p_mouth_in.L' :       ('p_mouth_in.L', ('p_mouth_in.L', offs)),
    'p_mouth_out.R' :       ('p_mouth_out.R', ('p_mouth_out.R', offs)),
    'p_mouth_out.L' :       ('p_mouth_out.L', ('p_mouth_out.L', offs)),
    'p_tongue' :        ('p_tongue', ('p_tongue', offs)),
    'p_jaw' :           ('p_jaw', ('p_jaw', offs)),
}

Armature = {
    'p_face' :         (pi, None, F_WIR|F_NOLOCK, L_PANEL),
    'p_face_display' :     (pi, 'p_face', F_WIR|F_RES, L_PANEL),
    'p_brow_in.R' :       (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_brow_in.L' :       (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_brow_out.R' :       (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_brow_out.L' :       (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_brow_mid' :        (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_up_lid.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_up_lid.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_lo_lid.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_lo_lid.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_cheek.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_cheek.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_nose' :         (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_up_lip_mid' :     (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_lo_lip_mid' :     (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_mouth_mid' :     (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_up_lip.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_up_lip.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_lo_lip.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_lo_lip.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_mouth_in.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_mouth_in.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_mouth_out.R' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_mouth_out.L' :      (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_tongue' :       (pi, 'p_face', F_NOLOCK, L_PANEL),
    'p_jaw' :          (pi, 'p_face', F_NOLOCK, L_PANEL),
}

CustomShapes = {
    'p_face' :       'GZM_Cube05',
    'p_face_display' :   'GZM_Face',
    'p_brow_in.L' :     'GZM_Cube025',
    'p_brow_in.R' :     'GZM_Cube025',
    'p_brow_out.L' :     'GZM_Cube025',
    'p_brow_out.R' :     'GZM_Cube025',
    'p_brow_mid' :      'GZM_Cube025',
    'p_up_lid.L' :    'GZM_Cube025',
    'p_up_lid.R' :    'GZM_Cube025',
    'p_lo_lid.L' :    'GZM_Cube025',
    'p_lo_lid.R' :    'GZM_Cube025',
    'p_cheek.L' :    'GZM_Cube025',
    'p_cheek.R' :    'GZM_Cube025',
    'p_nose' :       'GZM_Cube025',
    'p_up_lip_mid' :   'GZM_Cube025',
    'p_lo_lip_mid' :   'GZM_Cube025',
    'p_up_lip.L' :    'GZM_Cube025',
    'p_up_lip.R' :    'GZM_Cube025',
    'p_lo_lip.L' :    'GZM_Cube025',
    'p_lo_lip.R' :    'GZM_Cube025',
    'p_mouth_mid' :   'GZM_Cube025',
    'p_mouth_in.L' :    'GZM_Cube025',
    'p_mouth_in.R' :    'GZM_Cube025',
    'p_mouth_out.L' :    'GZM_Cube025',
    'p_mouth_out.R' :    'GZM_Cube025',
    'p_tongue' :     'GZM_Cube025',
    'p_jaw' :        'GZM_Cube025',
}

B = 0.25

LocationLimits = {
    'p_face_display' :  (0,0, 0,0, 0,0),
    'p_brow_in.L' :     (0,0, 0,0, -B,B),
    'p_brow_in.R' :     (0,0, 0,0, -B,B),
    'p_brow_out.L' :    (0,B, 0,0, -B,B),
    'p_brow_out.R' :    (-B,0, 0,0, -B,B),
    'p_brow_mid' :      (0,0, 0,0, 0,B),
    'p_up_lid.L' :      (0,0, 0,0, -B,B),
    'p_up_lid.R' :      (0,0, 0,0, -B,B),
    'p_lo_lid.L' :      (0,0, 0,0, -B,B),
    'p_lo_lid.R' :      (0,0, 0,0, -B,B),
    'p_cheek.L' :       (-B,B, 0,0, -B,0),
    'p_cheek.R' :       (-B,B, 0,0, -B,0),
    'p_nose' :          (0,0, 0,0, -B,0),
    'p_up_lip_mid' :    (0,0, 0,0, -B,B),
    'p_lo_lip_mid' :    (0,0, 0,0, -B,B),
    'p_up_lip.L' :      (0,0, 0,0, -B,B),
    'p_up_lip.R' :      (0,0, 0,0, -B,B),
    'p_lo_lip.L' :      (0,0, 0,0, -B,B),
    'p_lo_lip.R' :      (0,0, 0,0, -B,B),
    'p_mouth_mid' :     (0,0, 0,0, -B,0),
    'p_mouth_in.L' :    (0,B, 0,0, -B,B),
    'p_mouth_in.R' :    (-B,0, 0,0, -B,B),
    'p_mouth_out.L' :   (-B,B, 0,0, -B,B),
    'p_mouth_out.R' :   (-B,B, 0,0, -B,B),
    'p_tongue' :        (-B,B, 0,0, -B,B),
    'p_jaw' :           (0,0, 0,0, 0,B),
}

RotationLimits = {}
Locks = {}
for bone in LocationLimits.keys():
    Locks[bone] = (1,1,1)

pos = (0,4)
neg = (0,-4)

BoneDrivers = {
    # Brows
    'brow_squeeze'          : ('p_brow_mid', 'LOC_Z', pos, 0, 1.5),
    'brow_mid_up'           : ('p_brow_in', 'LOC_Z', neg, 0, 1.5),
    'brow_mid_down'         : ('p_brow_in', 'LOC_Z', pos, 0, 1.5),
    'brow_outer_up'         : ('p_brow_out', 'LOC_Z', neg, 0, 1.5),
    'brow_outer_down'       : ('p_brow_out', 'LOC_Z', pos, 0, 1.5),
    'cheek_squint'          : ('p_brow_out', 'LOC_X', pos, 0, 1.5),

#   Nose and jaw

    'nose_wrinkle'          : ('p_nose', 'LOC_Z', neg, 0, 1.5),
    'cheek_balloon'         : ('p_cheek', 'LOC_X', pos, 0, 1.5),
    'cheek_narrow'          : ('p_cheek', 'LOC_X', neg, 0, 1.5),
    'cheek_up'              : ('p_cheek', 'LOC_Z', neg, 0, 1.5),

#   Jaw and tongue
    'mouth_open'            : ('p_jaw', 'LOC_Z', pos, -0.3, 1.5),
    'tongue_out'            : ('p_jaw', 'LOC_X', neg, 0, 1.5),
    'tongue_in'             : ('p_jaw', 'LOC_X', pos, 0, 1.5),
    'tongue_up'             : ('p_tongue', 'LOC_Z', neg, 0, 1.5),
    'tongue_wide'           : ('p_tongue', 'LOC_X', pos, 0, 1.5),
    'tongue_back_up'        : ('p_tongue', 'LOC_X', neg, 0, 1.5),

#   Mouth expressions
    'mouth_wide'            : ('p_mouth_out', 'LOC_X', pos, 0, 1.5),
    'mouth_narrow'          : ('p_mouth_out', 'LOC_X', neg, 0, 1.5),
    'mouth_corner_up'       : ('p_mouth_out', 'LOC_Z', neg, 0, 1.5),
    'mouth_corner_down'     : ('p_mouth_out', 'LOC_Z', pos, 0, 1.5),

#   Lips part
    'lips_part'             : ('p_mouth_mid', 'LOC_Z', neg, -0.5, 1.5),

    'mouth_up'              : ('p_mouth_in', 'LOC_Z', neg, 0, 1.5),
    'mouth_down'            : ('p_mouth_in', 'LOC_Z', pos, 0, 1.5),
    'mouth_corner_in'       : ('p_mouth_in', 'LOC_X', pos, 0, 1.5),

#   Lips in _ out
    'lips_upper_out'        : ('p_up_lip_mid', 'LOC_Z', neg, 0, 1.5),
    'lips_upper_in'         : ('p_up_lip_mid', 'LOC_Z', pos, 0, 1.5),
    'lips_lower_out'        : ('p_lo_lip_mid', 'LOC_Z', neg, 0, 1.5),
    'lips_lower_in'         : ('p_lo_lip_mid', 'LOC_Z', pos, 0, 1.5),

#   Lips up _ down
    'lips_mid_upper_up'     : ('p_up_lip', 'LOC_Z', neg, 0, 1.5),
    'lips_mid_upper_down'   : ('p_up_lip', 'LOC_Z', pos, 0, 1.5),
    'lips_mid_lower_up'     : ('p_lo_lip', 'LOC_Z', neg, 0, 1.5),
    'lips_mid_lower_down'   : ('p_lo_lip', 'LOC_Z', pos, 0, 1.5),

}


def DeformDrivers(fp, amt):
    return []
    lidBones = [
    ('DEF_uplid.L', 'p_up_lid.L', (0, 40*D)),
    ('DEF_lolid.L', 'p_lo_lid.L', (0, 20*D)),
    ('DEF_uplid.R', 'p_up_lid.R', (0, 40*D)),
    ('DEF_lolid.R', 'p_lo_lid.R', (0, 20*D)),
    ]

    drivers = []
    for (driven, driver, coeff) in lidBones:
        drivers.append(    (driven, 'ROTQ', 'AVERAGE', None, 1, coeff,
         [("var", 'TRANSFORMS', [('OBJECT', amt.name, driver, 'LOC_Z', C_LOC)])]) )
    return drivers


BodyLanguageTextureDrivers = {
    # Brows
    'browsMidDown' : (3, 'p_brow_mid', 'LOC_Z', neg),
    'browsSqueeze' : (4, 'p_brow_mid', 'LOC_X', neg),
    'squint.L' : (5, 'p_cheek.L', 'LOC_X', pos),
    'squint.R' : (6, 'p_cheek.R', 'LOC_X', neg),
}



