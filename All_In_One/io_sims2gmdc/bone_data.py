'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

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


class BoneData:


    # Same order as the subgroups section of the GMDC
    bone_parent_table = [
        # Base
        ('simskel',          None,          0),
        ('root_trans',       'simskel',     1),
        ('root_rot',         'root_trans',  2),
        ('spine0',           'root_rot',    3),
        ('spine1',           'spine0',      4),
        ('spine2',           'spine1',      5),
        ('neck',             'spine2',      6),
        ('head',             'neck',        7),
        ('Joint8',           None,          8),
        # Right arm
        ('r_clavicle',       'spine2',      9),
        ('r_upperarm',       'r_clavicle',  10),
        ('r_bicep',          'r_upperarm',  11),
        ('r_forearm',        'r_bicep',     12),
        ('r_wrist',          'r_forearm',   13),
        ('r_hand',           'r_wrist',     14),
        ('r_thumb0',         'r_hand',      15),
        ('r_thumb1',         'r_thumb0',    16),
        ('r_thumb2',         'r_thumb1',    17),
        ('r_index0',         'r_hand',      18),
        ('r_index1',         'r_index0',    19),
        ('r_mid0',           'r_hand',      20),
        ('r_mid1',           'r_mid0',      21),
        ('r_pinky0',         'r_hand',      22),
        ('r_pinky1',         'r_pinky0',    23),
        # Left arm
        ('l_clavicle',       'spine2',      24),
        ('l_upperarm',       'l_clavicle',  25),
        ('l_bicep',          'l_upperarm',  26),
        ('l_forearm',        'l_bicep',     27),
        ('l_wrist',          'l_forearm',   28),
        ('l_hand',           'l_wrist',     29),
        ('l_thumb0',         'l_hand',      30),
        ('l_thumb1',         'l_thumb0',    31),
        ('l_thumb2',         'l_thumb1',    32),
        ('l_index0',         'l_hand',      33),
        ('l_index1',         'l_index0',    34),
        ('l_mid0',           'l_hand',      35),
        ('l_mid1',           'l_mid0',      36),
        ('l_pinky0',         'l_hand',      37),
        ('l_pinky1',         'l_pinky0',    38),
        # Lower body
        ('breathe_trans',    'spine0',      39),
        ('pelvis',          'root_rot',     40),
        # Right leg
        ('r_thigh',          'pelvis',      41),
        ('r_calf',           'r_thigh',     42),
        ('r_foot',           'r_calf',      43),
        ('r_toe',            'r_foot',      44),
        # Left leg
        ('l_thigh',          'pelvis',      45),
        ('l_calf',           'l_thigh',     46),
        ('l_foot',           'l_calf',      47),
        ('l_toe',            'l_foot',      48),
        # Clothes
        ('dress',            'pelvis',      49),
        ('r_longsleeve',     'r_forearm',   50),
        ('r_shortsleeve',    'r_upperarm',  51),
        ('l_longsleeve',     'l_forearm',   52),
        ('l_shortsleeve',    'l_upperarm',  53),
        ('r_pantsleg',       'r_calf',      54),
        ('r_shorts',         'r_thigh',     55),
        ('l_pantsleg',       'l_calf',      56),
        ('l_shorts',         'l_thigh',     57),
        # Misc
        ('Joint58',              None,      58),
        ('backtarget_surface',   'spine1',  59),
        # Hair
        ('c_hair',           'head',        60),
        ('f_hair',           'head',        61),
        ('r_hair',           'head',        62),
        ('l_hair',           'head',        63),
        ('b_hair',           'head',        64)
    ]


    def __init__(self, name, parent, subset, position, rotation):
        self.name       = name
        self.parent     = parent
        self.subset     = subset
        self.position   = position      # Translate  XYZ
        self.rotation   = rotation      # Quaternion WXYZ


    @staticmethod
    def build_bones(gmdc):
        print('Loading skeleton.\n')
        bones = []

        if len(gmdc.model.transforms) == 65:
            for subset, nameset in enumerate(BoneData.bone_parent_table):
                trans_bl = gmdc.model.transforms[subset]

                rotation  = ( -trans_bl[3], trans_bl[0], trans_bl[1], trans_bl[2] )
                translate = ( trans_bl[4], trans_bl[5], trans_bl[6] )
                name = nameset[0]
                parent = nameset[1]

                bones.append(BoneData(name, parent, subset, translate, rotation))
        else:
            for i, trans_bl in enumerate(gmdc.model.transforms):
                rotation  = ( -trans_bl[3], trans_bl[0], trans_bl[1], trans_bl[2] )
                translate = ( trans_bl[4], trans_bl[5], trans_bl[6] )
                name = 'Joint' + str(i)
                parent = None

                bones.append(BoneData(name, parent, i, translate, rotation))

        return bones


    @staticmethod
    def from_armature(armature):
        bones = [None] * len(armature.data.bones)
        if len(bones) == 65:       # Is sim skeleton
            for i, bone in enumerate(armature.data.bones):
                for subset, name in enumerate(BoneData.bone_parent_table):
                    if bone.name == name[0]:
                        rotation = (
                            -bone["rotation"][0], bone["rotation"][1],
                            bone["rotation"][2], bone["rotation"][3]
                        )
                        translate = bone["translate"]
                        bones[subset] = BoneData(bone.name, name[1], subset,
                                            translate, rotation)
        else:
            for subset, bone in enumerate(armature.data.bones):
                rotation = (
                    -bone["rotation"][0], bone["rotation"][1],
                    bone["rotation"][2], bone["rotation"][3]
                )
                translate = bone["translate"]

                bones[subset] = BoneData(bone.name, None, subset,
                                        translate, rotation)
        return bones


    def print(self):
        print(self.name)
        print('Parent:', self.parent)
        print('Subset:', self.subset)
        print('Position:', self.position)
        print('Rotation:', self.rotation)
        print()
