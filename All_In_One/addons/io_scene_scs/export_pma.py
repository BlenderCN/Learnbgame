##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

"""
Note:
    "rb" used in this file variables means "root bone"
"""

from mathutils import Quaternion, Vector
from . import help_funcs

class PMAheader:
    def __init__(self, version, name, no_keyframes, rb_anim_flag,  no_bones, anim_duration,
                 keyframes_times_offs=0, bones_indxs_offs=0, keyframes_data_offs=0,
                 rb_movement_data_offs=0, rb_rotations_data_offs=0):
        self.__version = version
        self.__name = help_funcs.EncodeNameCRC(name)
        self.__no_keyframes = no_keyframes
        self.__rb_anim_flag = rb_anim_flag
        self.__no_bones = no_bones
        self.__anim_duration = anim_duration
        self.__keyframes_times_offs = keyframes_times_offs
        self.__bones_indxs_offs = bones_indxs_offs
        self.__keyframes_data_offs = keyframes_data_offs
        self.__rb_movemnt_data_offs = rb_movement_data_offs
        self.__rb_rot_data_offs = rb_rotations_data_offs

    def to_scs_bytes(self):
        bytes = help_funcs.UInt32ToByts(self.__version)
        bytes += help_funcs.UInt64ToByts(self.__name)
        bytes += help_funcs.UInt16ToByts(self.__no_keyframes)
        bytes += help_funcs.UInt16ToByts(self.__rb_anim_flag)
        bytes += help_funcs.UInt32ToByts(self.__no_bones)
        bytes += help_funcs.FloatToByts(self.__anim_duration)
        bytes += help_funcs.UInt32ToByts(self.__keyframes_times_offs)
        bytes += help_funcs.UInt32ToByts(self.__bones_indxs_offs)
        bytes += help_funcs.UInt32ToByts(self.__keyframes_data_offs)
        bytes += help_funcs.UInt32ToByts(self.__rb_movemnt_data_offs)
        bytes += help_funcs.UInt32ToByts(self.__rb_rot_data_offs)
        return bytes

    def bytes_len(self):
        return len(self.to_scs_bytes())

class PMAKeyFrame:
    def __init__(self, stretch_quat=Quaternion(), rot_quat=Quaternion(),
                 trans_vec=Vector(), scale_vec=Vector()):
        self.__stretch_quat = stretch_quat
        self.__rot_quat = rot_quat
        self.__trans_vec = trans_vec
        self.__scale_vec = scale_vec

    def to_scs_bytes(self):
        bytes = help_funcs.FloatQuatToByts(self.__stretch_quat)
        bytes += help_funcs.FloatQuatToByts(self.__rot_quat)
        bytes += help_funcs.FloatVecToByts(self.__trans_vec)
        bytes += help_funcs.FloatVecToByts(self.__scale_vec)
        return bytes

    def bytes_len(self):
        return  len(self.to_scs_bytes())

class PMARBMovementKeyFrame:
    def __init__(self, movement_vec):
        self.__movement_vec = movement_vec
    def to_scs_bytes(self):
        return help_funcs.FloatVecToByts(self.__movement_vec)
    def bytes_len(self):
        return 3*4

class PMARBRotationKeyFrame:
    def __init__(self, rotation_vec):
        self.__rotation_vec = rotation_vec
    def to_scs_bytes(self):
        return help_funcs.FloatQuatToByts(self.__movement_vec)
    def bytes_len(self):
        return 4*4

class PMASave:
    def __init__(self):
        pass


