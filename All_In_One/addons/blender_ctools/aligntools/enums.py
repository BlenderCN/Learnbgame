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


from enum import Enum


class CustomEnum(Enum):
    def __repr__(self):  # memoizeの為の変更
        return self.__str__()

    @classmethod
    def get(cls, value):
        if value in cls.__members__:
            return cls[value]
        else:
            return cls(value)


class GroupType(CustomEnum):
    NONE = 1
    ALL = 2
    PARENT_CHILD = 3
    LINKED = 4  # edgeで繋がっている状態
    GROUP = 5
    BOUNDING_BOX = 6
    BONE = 7
    PARENT_CHILD_CONNECTED = 8  # bone用


class PivotPoint(CustomEnum):
    CENTER = 1
    MEDIAN = 2
    ACTIVE = 3
    CURSOR = 4
    ROOT = 5
    HEAD_TAIL = 6
    BOUNDING_BOX = 7
    TARGET = 8


class Distance(CustomEnum):
    CLOSEST = 1
    MIN = 2
    CENTER = 3
    MAX = 4


class Space(CustomEnum):
    # LOCAL, NORMAL, GIMBALはindividual_orientationにより個別の値を取りうる
    GLOBAL = 1
    WORLD = 1
    LOCAL = 2
    GRID = 3
    NORMAL = 4
    GIMBAL = 5
    VIEW = 6
    CUSTOM = 7

    REGION = 10
    BONE = 11
    MANIPULATOR = 12
    PLANE = 13
    AXIS = 14


class Axis(CustomEnum):
    X = 1
    Y = 2
    Z = 3


class BoundingBox(CustomEnum):
    AABB = 1
    OBB = 2


class BoneFilter(CustomEnum):
    ALL = 1,
    LAYER = 2
    SELECT = 3
    SELECT_HEAD = 4
    SELECT_TAIL = 5
    SELECT_ANY = 6

    # bone.selectが偽で、親とのuse_connectが真で
    # selectかselect_tailが真、若しくは子とのuse_connectが真で
    # selectが真なら偽とする。それ以外の場合はselect_anyに従う
    SELECT_ANY_OPTIMIZED = 7


class ObjectData(CustomEnum):
    ORIGIN = 1
    MESH = 2
    DM_PREVIEW = 3
    DM_RENDER = 4
