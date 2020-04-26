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


import math
from enum import Enum, IntEnum
import re
import string
from collections import namedtuple

import bpy
import mathutils
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils import geometry as geom
import bgl
import blf
import bmesh

from . import vaview3d as vav
from . import vamath as vam
from . import vagl
from . import unitsystem, manipulatormatrix
from . import vaprops as vap


class _void:
    pass


def ifel(a, b, condition=_void):
    """三項式の文字数節約"""
    if condition is _void:
        return a if a else b
    else:
        return a if a == condition else b


# def ifel(*args):
#     """三項式の文字数節約"""
#     if len(args) == 3:
#         a, condition, b = args
#         return a if a == condition else b
#     else:
#         a, b = args
#         return a if a else b


class PROP(Enum):
    NONE = 'NONE'
    DISTANCE = 'DISTANCE'
    ANGLE = 'ANGLE'
    NEGATIVE = 'NEGATIVE'
    INVERSE = 'INVERSE'


class CONST(IntEnum):
    """軸制限のフラグ"""
    NONE = 0
    X = 0b100
    Y = 0b010
    Z = 0b001
    XY = 0b110
    XZ = 0b101
    YZ = 0b011
    XYZ = 0b111  # ビット演算に使うが、ModalMouse.const_axisへは使用しない
    # ALL = 0b111
    # VIEW_X = 0b1100
    # VIEW_Y = 0b1010

    WORLD = 1 << 3
    CURRENT = 1 << 4
    VIEW = 1 << 5
    ANGLE = 1 << 6


class NumberInput:
    def __init__(self, owner):
        """
        :type owner: ModalMouse
        """
        self.owner = owner
        self.enable = False
        self.advanced = False
        self.cursor = [0, 0]
        self.labels = []
        self.types = []
        self.fallback = []
        self.flags = []
        self.strings = []
        self.value = []
        self.init_mode()

    @property
    def mode(self):
        return self.owner.mode
    @property
    def modes(self):
        return self.owner.modes
    @property
    def mode_props(self):
        return self.owner.mode.props

    def init_mode(self):
        """labelsとstrings初期化する"""
        props = self.owner.mode.props
        self.cursor[:] = [0, 0]
        self.labels[:] = [prop[0] for prop in props]
        self.types[:] = [prop[1] for prop in props]
        self.fallback[:] = [prop[2] for prop in props]
        self.flags[:] = [set() for i in range(len(props))]
        self.strings[:] = [None] * len(props)
        self.value = [0.0] * len(props)

    def calc(self, index=None, use_fallback=True):
        result = []
        r = range(len(self.strings)) if index is None else [index]
        for i in r:
            s = self.strings[i]
            fallback = self.fallback[i] if use_fallback else None
            if s is None:
                value = fallback
            else:
                value = self.owner.unit_system.unit_to_num(s, fallback=None)
                if value is None:
                    value = fallback
                else:
                    if PROP.NEGATIVE in self.flags[i]:
                        value = -value
                    if PROP.INVERSE in self.flags[i]:
                        value = 1 / value
                    if self.types[i] == PROP.ANGLE:
                        if self.owner.unit_system.system_rotation == 'DEGREES':
                            value = math.radians(value)
            result.append(value)
        if index is None:
            return result
        else:
            return result[0]

    def modal(self, context, event):
        caught = False
        mouse_move = ''

        i, j = self.cursor

        if event.value != 'PRESS':
            return caught, mouse_move

        def insert_string(string):
            i, j = self.cursor
            t = self.strings[i]
            if t is None:
                t = ''
            self.strings[i] = t[:j] + string + t[j:]
            self.cursor[1] += len(string)

        if not self.enable:
            if event.ascii and event.ascii in '0123456789.=*':
                if event.ascii in '0123456789.':
                    insert_string(event.ascii)
                else:
                    if self.strings[i] is None:
                        self.strings[i] = ''
                    self.advanced = True
                self.enable = True
                caught = True
                # 数値入力に入った時の値を保存しておく
                self.value = self.owner.number_input_value[:len(self.strings)]

        else:
            caught = True
            if event.type == 'TAB':
                if len(self.strings) >= 1:
                    if self.strings[i] == '':
                        if self.value:
                            if self.types[i] == PROP.ANGLE and \
                                self.owner.unit_system.system_rotation == 'DEGREES':
                                self.strings[i] = str(math.degrees(self.value[i]))
                            else:
                                self.strings[i] = str(self.value[i])
                    if event.ctrl:
                        self.cursor[0] = (i - 1) % len(self.strings)
                    else:
                        self.cursor[0] = (i + 1) % len(self.strings)
                    i = self.cursor[0]
                    if self.strings[i] is None:
                        self.cursor[1] = 0
                    else:
                        self.cursor[1] = len(self.strings[i])

            elif event.type == 'HOME':
                self.cursor[1] = 0

            elif event.type == 'END':
                self.cursor[1] = len(self.strings[i])

            elif event.type == 'LEFT_ARROW':
                if self.strings[i] is None or j == 0:
                    mouse_move = 'left'
                else:
                    if event.ctrl:
                        pattern = '.*?\s*(\w*|[^\w\s]*)\s*$'
                        m = re.match(pattern, self.strings[i][:j])
                        self.cursor[1] = m.start(1)
                    else:
                        self.cursor[1] = max(0, j - 1)

            elif event.type == 'RIGHT_ARROW':
                if self.strings[i] is None or j == len(self.strings[i]):
                    mouse_move = 'right'
                else:
                    if event.ctrl:
                        pattern = '(\s*|\w*|[^\w\s]*)\s*(.*)'
                        m = re.match(pattern, self.strings[i][j:])
                        self.cursor[1] = m.start(2)
                    else:
                        self.cursor[1] = min(j + 1, len(self.strings[i]))

            elif event.type == 'UP_ARROW':
                mouse_move = 'up'

            elif event.type == 'DOWN_ARROW':
                mouse_move = 'down'

            elif event.type == 'BACK_SPACE':
                t = self.strings[i]
                if t is None:
                    # Noneの箇所でBackSpaceを押したら数値入力を修了する
                    self.enable = False
                elif t == '':
                    self.strings[i] = None
                    # 全ての要素がNoneになったなら数値入力を修了する
                    if set(self.strings) == {None}:
                        self.enable = False
                else:
                    if event.ctrl:  # 前方全て消す
                        self.strings[i] = t[j:]
                        self.cursor[1] = 0
                    else:
                        self.strings[i] = t[:j - 1] + t[j:]
                        self.cursor[1] = max(0, j - 1)

            elif event.type == 'DEL':
                t = self.strings[i]
                if t is not None:
                    if event.ctrl:
                        self.strings[i] = t[:j]
                    else:
                        self.strings[i] = t[:j] + t[j + 1:]

            elif event.type == 'C' and event.ctrl:
                # copy
                if self.strings[i] is not None:
                    context.window_manager.clipboard = self.strings[i]

            elif event.type == 'V' and event.ctrl:
                # paste
                insert_string(context.window_manager.clipboard)

            elif event.ascii:
                if event.ascii in ('=', '*'):
                    if self.advanced and not event.ctrl:
                        insert_string(event.ascii)
                    else:
                        self.advanced ^= True
                elif event.ascii == '-':
                    if self.advanced and not event.ctrl:
                        insert_string(event.ascii)
                    else:
                        self.flags[i] ^= {PROP.NEGATIVE}
                elif event.ascii == '/':
                    if self.advanced and not event.ctrl:
                        insert_string(event.ascii)
                    else:
                        self.flags[i] ^= {PROP.INVERSE}
                elif not event.ctrl:
                    if self.advanced or event.ascii in '0123456789.':
                        insert_string(event.ascii)
                else:
                    # 他の ascii + ctrl は無視する
                    caught = False

        # 非アクティブになったら初期化
        if not self.enable:
            self.init_mode()

        return caught, mouse_move

    def draw(self, context, offset_x, offset_y, font_id=0, font_size=11,
             color=(1, 1, 1), error_color=(1, 1, 0)):
        """返り値は描画したテキストの終端
        None: 初期化時の値を使う
        """
        unit_system = self.owner.unit_system

        text_width_min = 30
        partition = '  '

        dpi = context.user_preferences.system.dpi
        blf.size(font_id, font_size, dpi)

        offset_x_bak = offset_x
        _, text_height = blf.dimensions(font_id, string.printable)

        if not self.labels:
            return offset_x, offset_y

        for i in range(len(self.strings)):
            # [1.23] = 1,23
            # [-(1)] = -1
            # [-1/(12)] = -0.08

            if self.labels[i]:
                head = self.labels[i] + ': '
            else:
                head = ''

            exp_string = self.strings[i]
            is_invalid = False
            pre = post = ''
            if self.enable:
                if exp_string is None:
                    text = head + 'NONE'
                else:
                    if PROP.NEGATIVE in self.flags[i]:
                        if PROP.INVERSE in self.flags[i]:
                            pre = '[-1/('
                            post = ')]'
                        else:
                            pre = '[-('
                            post = ')]'
                    elif PROP.INVERSE in self.flags[i]:
                        pre = '[1/('
                        post = ')]'
                    else:
                        pre = '['
                        post = ']'

                    text = head + pre + exp_string + post

                    if exp_string:
                        if PROP.INVERSE in self.flags[i]:
                            draw_result = True
                        else:
                            try:
                                float(exp_string)
                                draw_result = False
                            except:
                                draw_result = True
                        if draw_result:
                            value = self.calc(i, use_fallback=False)
                            if value is None:
                                is_invalid = True
                                text += ' = invalid'
                            else:
                                if self.types[i] == PROP.ANGLE:
                                    if unit_system.system_rotation == 'DEGREES':
                                        t = '{0:g}°'.format(math.degrees(value))
                                    else:
                                        t = '{0:g}'.format(value)
                                elif self.types[i] == PROP.DISTANCE:
                                    t = unit_system.num_to_unit(value)
                                else:
                                    t = '{0:g}'.format(value)
                                if t == '0':
                                    t = '0.0'
                                text += ' = ' + t

            else:
                val = self.owner.number_input_value
                if val is not None:
                    if isinstance(val, (int, float)):
                        val = [val]
                    value = val[i]
                    if self.types[i] == PROP.ANGLE:
                        if unit_system.system_rotation == 'DEGREES':
                            exp_text = '{0:g}°'.format(math.degrees(value))
                        else:
                            exp_text = '{0:g}'.format(value)
                    elif self.types[i] == PROP.DISTANCE:
                        exp_text = unit_system.num_to_unit(
                            value, use_separate=False, rounding_exp=-6)
                    else:
                        exp_text = '{0:g}'.format(value)
                    if exp_text == '0':
                        exp_text = '0.0'
                    text = head + exp_text
                else:
                    text = ''

            # 描画
            if is_invalid:
                bgl.glColor3f(*error_color)
            else:
                bgl.glColor3f(*color)
            blf.position(font_id, offset_x, offset_y, 0)
            vagl.blf_draw(font_id, text)
            text_width, _ = blf.dimensions(font_id, text)
            text_width = max(text_width_min, text_width)

            # 区切り文字
            if len(self.strings) > 1 and 0 <= i < len(self.strings) - 1:
                bgl.glColor3f(*color)
                blf.position(font_id, offset_x + text_width, offset_y, 0)
                vagl.blf_draw(font_id, partition)
                t_width, _ = blf.dimensions(font_id, partition)
                text_width += t_width

            # cursor描画
            if self.enable and i == self.cursor[0]:
                bgl.glColor3f(*color)
                if exp_string is None:
                    t = head + 'NONE'
                else:
                    t = head + pre + exp_string[:self.cursor[1]]
                t_width, _ = blf.dimensions(font_id, t)
                x = offset_x + t_width
                bgl.glRectf(x - 1, offset_y - 4, x + 1, offset_y + 14)

            offset_x += text_width

            if offset_x > context.region.width and i < len(self.strings) - 1:
                offset_x = offset_x_bak
                offset_y += text_height

        return offset_x, offset_y


#==============================================================================
# Modes
#==============================================================================
class NoneMode:
    name = 'None'
    identity = 'NONE'
    props = []  # [(label, type, fallback), ...]
    # orientations: [[orientation,  # str or CONST.CURRENT
    #                 const_orientation,  # str or CONST.CURRENT
    #                 middle mouse mode],  # CONST.XYZ or CONST.ANGLE
    #                ...]
    orientations = [['GLOBAL', 'GLOBAL', CONST.XYZ],
                    [CONST.CURRENT, CONST.CURRENT, CONST.XYZ],
                    ['VIEW', 'VIEW', CONST.ANGLE]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow',
                  'rotation', 'resize']
    # CONST.VIEW
    consider_const_axis_as_angle = True

    @classmethod
    def poll(cls, context, event, owner):
        """このモードに切り替え可能なら真を返す。
        """
        return owner.mode != 'NONE' and event.type == 'N'

    def calc(self, context, owner, snap=True, number_input=True):
        """
        :type context: bpy.types.Context
        :type owner: ModalMouse
        :type snap: bool
        :type number_input: bool
        :rtype: dict
        """
        return {'_mco': None, '_length': None, '_value': None}

    def header_string(self, context, owner):
        """
        :type owner: ModalMouse
        :rtype: str
        """
        return ''


class TranslationMode(NoneMode):
    name = 'Translation'
    identity = 'TRANSLATION'
    props = [('Dx', PROP.DISTANCE, 0.0),
             ('Dy', PROP.DISTANCE, 0.0),
             ('Dz', PROP.DISTANCE, 0.0)]  # [(label, type, fallback), ...]
    orientations = [['GLOBAL', 'GLOBAL', CONST.XYZ],
                    [CONST.CURRENT, CONST.CURRENT, CONST.XYZ]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow']

    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。"""
        return event.type == 'G'

    @classmethod
    def calc(cls, context, owner, snap=True, number_input=True):
        region = context.region
        rv3d = context.region_data
        omat = owner.orientation.to_3x3()
        oimat = omat.inverted()
        cmat = owner.const_orientation.to_3x3()
        depth_location = ifel(owner.view_location, rv3d.view_location)
        mco_origin_w = owner.mco_origin_w
        mco_modify_w = owner.mco_modify_w

        # view_vec: 画面手前から奥に向かうWorld座標系のベクトル
        view_vec = -rv3d.view_matrix.to_3x3().inverted().col[2]

        if number_input and owner.number_input.enable:
            value = [owner.number_input.calc(i) for i in range(3)]
            translation = Vector(value)
            v_w = owner.mco_origin_w + omat * translation
            mco_draw = vav.project(region, rv3d, v_w).to_2d()
            return {'translation': translation,
                    '_mco': mco_draw,
                    '_length': translation.length,
                    '_value': list(translation)}

        if owner.const_axis == CONST.NONE:
            translation = oimat * mco_modify_w - oimat * mco_origin_w

        elif owner.const_axis == CONST.ANGLE:
            if owner.const_angle is None:
                translation = Vector((0, 0, 0))
            else:
                axis_mat = rv3d.view_matrix.to_3x3().inverted()
                q = Quaternion(view_vec, -owner.const_angle)
                axis_w = q * axis_mat.col[0].normalized()
                v = vav.project(region, rv3d, mco_origin_w + axis_w).to_2d()
                axis = v - owner.mco_origin
                v = owner.mco_relative.project(axis) + owner.mco_origin
                near_w = vav.unproject(region, rv3d, v, depth_location)
                far_w = vav.unproject(region, rv3d, v,
                                      depth_location + view_vec)
                v_w, _ = geom.intersect_line_line(
                    mco_origin_w, mco_origin_w + axis_w, near_w, far_w)
                translation = oimat * v_w - oimat * mco_origin_w
        else:
            def const_axis(index):
                axis = cmat.col[index].normalized()
                v = vav.project(region, rv3d, mco_origin_w + axis).to_2d()
                axis_r = v - owner.mco_origin
                vR = owner.mco_relative.project(axis_r) + owner.mco_origin
                nearW = vav.unproject(region, rv3d, vR, depth_location)
                farW = vav.unproject(region, rv3d, vR,
                                     depth_location + view_vec)
                v5, _ = geom.intersect_line_line(
                    mco_origin_w, mco_origin_w + axis, nearW, farW)
                return oimat * v5 - oimat * mco_origin_w

            def const_plane(index):
                axis = cmat.col[index].normalized()
                plane = vam.PlaneVector(mco_origin_w, axis)
                v = owner.mco_origin + owner.mco_relative
                v1 = vav.unproject(region, rv3d, v, depth_location + view_vec)
                v2 = plane.intersect(mco_modify_w, v1)
                return oimat * v2 - oimat * mco_origin_w

            if owner.const_axis in (CONST.X, CONST.Y, CONST.Z):
                ls = [CONST.X, CONST.Y, CONST.Z]
                i = ls.index(owner.const_axis)
                if owner.axis_test(context, i, cmat):
                    translation = const_axis(i)
                else:
                    f = -owner.mco_relative[1] * owner.unit_system.bupd
                    translation = Vector((0, 0, 0))
                    translation[i] = f
            else:
                if owner.const_axis == CONST.XY:
                    if not owner.axis_test(context, 0, cmat):
                        translation = const_axis(1)
                    elif not owner.axis_test(context, 1, cmat):
                        translation = const_axis(0)
                    else:
                        translation = const_plane(2)
                elif owner.const_axis == CONST.XZ:
                    if not owner.axis_test(context, 0, cmat):
                        translation = const_axis(2)
                    elif not owner.axis_test(context, 2, cmat):
                        translation = const_axis(0)
                    else:
                        translation = const_plane(1)
                else:  # const_axis == CONST.YZ:
                    if not owner.axis_test(context, 1, cmat):
                        translation = const_axis(2)
                    elif not owner.axis_test(context, 2, cmat):
                        translation = const_axis(1)
                    else:
                        translation = const_plane(0)

        if snap and owner.snap:
            if owner.mco_shift_press:
                precision = True
            else:
                precision = False
            if owner.const_axis == CONST.ANGLE:
                f = translation.length
                f = owner.unit_system.snap_grid(f, precision)
                translation = translation.normalized() * f
            else:
                mat = cmat.normalized()
                vec = mat.inverted() * omat * translation
                for i, f in enumerate(vec):
                    vec[i] = owner.unit_system.snap_grid(f, precision)
                translation = oimat * mat * vec

        v_w = owner.mco_origin_w + omat * translation
        mco_draw = vav.project(region, rv3d, v_w).to_2d()

        return {'translation': translation,
                '_mco': mco_draw,
                '_length': translation.length,
                '_value': list(translation)}

    def header_string(self, context, owner):
        return ''


# class Translation2DMode(NoneMode):
#     name = 'Translation 2D'
#     identity = 'TRANSLATION_2D'
#     props = [('Dx', PROP.DISTANCE, 0.0),
#              ('Dy', PROP.DISTANCE, 0.0)]
#     orientations = [['GLOBAL', 'VIEW', CONST.XYZ],
#                     [CONST.CURRENT, 'VIEW', CONST.XYZ]]
#     draw_items = ['origin', 'mco', 'const_axis', 'const_arrow']
#
#     def poll(self, context, event, owner):
#         """このモードに切り替え可能なら真を返す。"""
#         return owner.mode != self and event.type == 'F'
#
#     @classmethod
#     def calc(cls, context, owner, snap=True, number_input=True):
#         region = context.region
#         rv3d = context.region_data
#         omat = owner.orientation.to_3x3()
#         oimat = omat.inverted()
#         depth_location = ifel(owner.view_location, rv3d.view_location)
#         mco_origin_w = owner.mco_origin_w
#         mco_modify_w = owner.mco_modify_w
#
#         if number_input and owner.number_input.enable:
#             value = [owner.number_input.calc(i) for i in range(2)]
#             translation = Vector(value)
#
#         else:
#             if owner.const_axis == CONST.NONE:
#                 translation = oimat * mco_modify_w - oimat * mco_origin_w
#
#             else:
#                 if owner.const_axis == CONST.ANGLE:
#                     a = owner.const_angle
#                     if a is None:
#                         axis = None
#                     else:
#                         axis = Vector((math.cos(a), math.sin(a)))
#                 else:
#                     if owner.const_axis == CONST.X:
#                         axis = Vector((1, 0))
#                     elif owner.const_axis == CONST.Y:
#                         axis = Vector((0, 1))
#                     else:
#                         axis = None
#                 if axis is None:
#                     translation = Vector((0, 0))
#                 else:
#                     v1 = owner.mco_relative.project(axis)
#                     v2 = v1 + owner.mco_origin
#                     v_w = vav.unproject(region, rv3d, v2, depth_location)
#                     translation = oimat * v_w - oimat * mco_origin_w
#
#             if snap and owner.snap:
#                 snap_grid = owner.unit_system.snap_grid
#                 if owner.mco_shift_press:
#                     precision = True
#                 else:
#                     precision = False
#                 if owner.const_axis == CONST.NONE:
#                     for i, f in enumerate(translation):
#                         f = snap_grid(f, precision)
#                         translation[i] = f
#                 else:
#                     v = translation.normalized()
#                     f = translation.length
#                     translation = v * snap_grid(f, precision)
#
#         v = omat * translation + owner.mco_origin_w
#         mco_draw = vav.project(region, rv3d, v).to_2d()
#
#         return {'translation': translation,
#                 '_mco': mco_draw,
#                 '_length': translation.length,
#                 '_value': list(translation)}
#
#     def header_string(self, context, owner):
#         return ''


class Translation2DMode(NoneMode):
    name = 'Translation 2D'
    identity = 'TRANSLATION_2D'
    props = [('Dx', PROP.DISTANCE, 0.0),
             ('Dy', PROP.DISTANCE, 0.0)]
    orientations = [['GLOBAL', 'VIEW', CONST.ANGLE],
                    [CONST.CURRENT, 'VIEW', CONST.ANGLE]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow']

    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。
        """
        return owner.mode != self and event.type == 'F'

    @classmethod
    def calc(cls, context, owner, snap=True, number_input=True):
        region = context.region
        rv3d = context.region_data
        omat = owner.orientation.to_3x3()
        oimat = omat.inverted()
        cmat = owner.const_orientation.to_3x3()
        mco_origin_w = owner.mco_origin_w
        mco_modify_w = owner.mco_modify_w
        depth_location = ifel(owner.view_location, rv3d.view_location)

        if number_input and owner.number_input.enable:
            translation = Vector([owner.number_input.calc(i)
                                  for i in range(2)])
        else:
            def calc_dist(mco_modify):
                v = Vector((mco_modify[0], owner.mco_origin[1]))
                v_w = vav.unproject(region, rv3d, v, depth_location)
                dist_x = (oimat * mco_origin_w - oimat * v_w).length
                if mco_modify[0] < owner.mco_origin[0]:
                    dist_x = -dist_x
                v = Vector((owner.mco_origin[0], mco_modify[1]))
                v_w = vav.unproject(region, rv3d, v, depth_location)
                dist_y = (oimat * mco_origin_w - oimat * v_w).length
                if mco_modify[1] < owner.mco_origin[1]:
                    dist_y = -dist_y
                return Vector((dist_x, dist_y))
            if owner.const_axis == CONST.NONE:
                translation = calc_dist(owner.mco_modify)
            else:
                if owner.const_axis == CONST.ANGLE:
                    a = owner.const_angle
                    if a is None:
                        axis = None
                    else:
                        axis = Vector((math.cos(a), math.sin(a)))
                else:
                    if owner.const_axis == CONST.X:
                        axis = Vector((1, 0))
                    elif owner.const_axis == CONST.Y:
                        axis = Vector((0, 1))
                    else:
                        axis = None
                if axis is None:
                    translation = Vector((0, 0))
                else:
                    mco_r = owner.mco_relative
                    v = mco_r.project(axis) + owner.mco_origin
                    translation = calc_dist(v)

            if snap and owner.snap:
                snap_grid = owner.unit_system.snap_grid
                if owner.mco_shift_press:
                    precision = True
                else:
                    precision = False
                if owner.const_axis == CONST.ANGLE:
                    f = translation.length
                    v = translation.normalized()
                    translation = v * snap_grid(f, precision)
                else:
                    for i, f in enumerate(translation):
                        f = snap_grid(f, precision)
                        translation[i] = f

        axis_x = (oimat * cmat.col[0]).normalized()
        axis_y = (oimat * cmat.col[1]).normalized()
        v = oimat * owner.mco_origin_w
        v += axis_x * translation[0] + axis_y * translation[1]
        v = omat * v
        mco_draw = vav.project(region, rv3d, v).to_2d()

        return {'translation': translation,  # 2D
                '_mco': mco_draw,
                '_length': translation.length,
                '_value': list(translation)}


class DistanceMode(NoneMode):
    name = 'Distance'
    identity = 'DISTANCE'
    props = [('Dist', PROP.DISTANCE, 0.0)]
    orientations = [['GLOBAL', 'VIEW', CONST.ANGLE],
                    [CONST.CURRENT, 'VIEW', CONST.ANGLE]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow']

    # def __init__(self):
    #     self.distance = 0.0
    #     self.mco_draw = Vector((0, 0))

    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。
        """
        return event.type == 'D'

    @classmethod
    def calc(cls, context, owner, snap=True, number_input=True):
        """
        :type context: bpy.types.Context
        :type owner: ModalMouse
        :type snap: bool
        :type number_input: bool
        :rtype: dict
        """

        region = context.region
        rv3d = context.region_data
        omat = owner.orientation.to_3x3()
        oimat = omat.inverted()
        cmat = owner.const_orientation.to_3x3()
        cimat = cmat.inverted()
        depth_location = ifel(owner.view_location, rv3d.view_location)
        mco_origin_w = owner.mco_origin_w
        mco_modify_w = owner.mco_modify_w

        if number_input and owner.number_input.enable:
            dist = owner.number_input.calc(0)

        else:
            if owner.const_axis == CONST.ANGLE:
                a = owner.const_angle
                if a is None:
                    dist = 0.0
                else:
                    axis = Vector((math.cos(a), math.sin(a)))
                    v1 = owner.mco_relative.project(axis)
                    v2 = v1 + owner.mco_origin
                    v_w = vav.unproject(region, rv3d, v2, depth_location)
                    dist = (oimat * v_w - oimat * mco_origin_w).length
                    if axis.dot(v1) < 0:
                        dist = -dist
            else:
                result = Translation2DMode.calc(context, owner, False, False)
                translation = result['translation']
                dist = translation.length
                if owner.const_axis != CONST.NONE:
                    if owner.const_axis == CONST.ANGLE:
                        a = owner.const_angle
                        if a is not None:
                            axis = Vector((math.cos(a), math.sin(a)))
                            d = owner.mco_relative.dot(axis)
                            if d < 0.0:
                                dist = -dist
                    else:
                        sign = 1.0
                        for f in translation:
                            if f < -1e-10:  # TODO: 閾値の調整
                                sign *= -1
                        dist *= sign

            if snap and owner.snap:
                if owner.mco_shift_press:
                    precision = True
                else:
                    precision = False
                dist = owner.unit_system.snap_grid(dist, precision)

        if owner.const_axis == CONST.NONE:
            axis = owner.mco_modify - owner.mco_origin
            if axis.length == 0.0:
                axis = Vector((1, 0))
            else:
                axis.normalize()
        elif owner.const_axis == CONST.ANGLE:
            a = owner.const_angle
            if a is None:
                axis = Vector((1, 0))
            else:
                axis = Vector((math.cos(a), math.sin(a)))
        else:
            if owner.const_axis == CONST.X:
                axis = Vector((1, 0))
            elif owner.const_axis == CONST.Y:
                axis = Vector((0, 1))
            else:
                axis = Vector((1, 0))

        vmat3 = rv3d.view_matrix.to_3x3()
        axis = (oimat * vmat3.inverted() * axis.to_3d()).normalized()
        translation = axis * dist
        v = omat * translation + owner.mco_origin_w
        mco_draw = vav.project(region, rv3d, v).to_2d()

        return {'distance': dist, '_mco': mco_draw, '_value': [dist]}

    def header_string(self, context, owner):
        return ''


class FactorMode(NoneMode):
    name = 'Factor'
    identity = 'FACTOR'
    props = [('Fac', PROP.NONE, 0.0)]
    orientations = [['GLOBAL', 'VIEW', CONST.ANGLE]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow', 'factor']

    # def __init__(self, factor):
    #     self.factor = 0.0
    #     self.mco_draw = Vector((0, 0))

    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。
        """
        return owner.mode != self and event.type == 'F'

    def calc(self, context, owner, snap=True, number_input=True):
        dpf = owner.circle_factor[1] - owner.circle_factor[0]

        if number_input and owner.number_input.enable:
            fac = owner.number_input.calc(0)

        else:
            if owner.const_axis == CONST.NONE:
                fac = owner.mco_relative.length / dpf

            else:
                if owner.const_axis == CONST.ANGLE:
                    a = owner.const_angle
                    if a is None:
                        axis = None
                    else:
                        axis = Vector((math.cos(a), math.sin(a)))
                else:
                    if owner.const_axis == CONST.X:
                        axis = Vector((1, 0))
                    elif owner.const_axis == CONST.Y:
                        axis = Vector((0, 1))
                    else:
                        axis = None
                if axis is None:
                    fac = 0.0
                else:
                    v = owner.mco_relative.project(axis)
                    fac = v.length / dpf
                    if axis.dot(v) < 0:
                        fac = -fac

            if snap and owner.snap:
                if owner.mco_shift_press:
                    scalar = 0.01
                else:
                    scalar = 0.1
                fac = owner.unit_system.snap_value(fac, scalar)

        f = fac
        if owner.const_axis == CONST.NONE:
            axis = owner.mco_modify - owner.mco_origin
            if axis.length == 0.0:
                axis = Vector((1, 0))
            else:
                axis.normalize()
        elif owner.const_axis == CONST.ANGLE:
            a = owner.const_angle
            if a is None:
                axis = Vector((1, 0))
            else:
                axis = Vector((math.cos(a), math.sin(a)))
        else:
            if owner.const_axis == CONST.X:
                axis = Vector((1, 0))
            else:
                axis = Vector((0, 1))
        mco_draw = axis * f * dpf + owner.mco_origin

        return {'factor': fac, '_mco': mco_draw, '_value': [fac]}

    def header_string(self, context, owner):
        return ''


class RotationMode(NoneMode):
    name = 'Rotation'
    identity = 'ROTATION'
    props = [('Rot', PROP.ANGLE, 0.0)]
    orientations = [['GLOBAL', 'GLOBAL', CONST.XYZ],
                    [CONST.CURRENT, CONST.CURRENT, CONST.XYZ]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow',
                  'rotation']


    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。"""
        return owner.mode != self and event.type == 'R'

    def calc(self, context, owner, snap=True, number_input=True):
        region = context.region
        rv3d = context.region_data
        omat = owner.orientation.to_3x3()
        oquat = omat.to_quaternion()
        cmat = owner.const_orientation.to_3x3()

        location = owner.orientation.to_translation()
        pivot = vav.project(region, rv3d, location).to_2d()
        vec1 = owner.mco_origin - pivot
        vec2 = owner.mco_modify - pivot
        view_vec = -rv3d.view_matrix.to_3x3().inverted().col[2]

        # angle
        if number_input and owner.number_input.enable:
            rotation_angle = owner.number_input.calc(0)
        else:
            if vec1.length == 0.0:
                rotation_angle = -vam.vecs_angle(Vector((1, 0)), vec2)
            elif vec2.length == 0.0:
                rotation_angle = 0.0
            else:
                rotation_angle = -vam.vecs_angle(vec1, vec2)  # 時計回りが正
        if owner.const_axis == CONST.ANGLE and owner.const_angle is None:
            rotation_angle = 0.0

        # axis
        negative = False  # 回転軸が画面正面に向かってくる場合、回転角を反転する
        if owner.const_axis == CONST.NONE:
            rotation_axis = oquat.inverted() * view_vec
        elif owner.const_axis == CONST.ANGLE:
            if owner.const_angle is None:
                rotation_axis = Vector((1, 0, 0))
            else:
                axis_mat = rv3d.view_matrix.to_3x3().inverted()
                q = Quaternion(view_vec, -owner.const_angle)
                rotation_axis = cmat.inverted() * (q * axis_mat.col[0])
            rotation_axis.normalize()
        else:
            if owner.const_axis in (CONST.X, CONST.YZ):
                axis_w = cmat.col[0].normalized()
                rotation_axis = Vector((1, 0, 0))
            elif owner.const_axis in (CONST.Y, CONST.XZ):
                axis_w = cmat.col[1].normalized()
                rotation_axis = Vector((0, 1, 0))
            else:
                axis_w = cmat.col[2].normalized()
                rotation_axis = Vector((0, 0, 1))
            if axis_w.dot(view_vec) < -1e-5:
                rotation_angle = -rotation_angle
                negative = True

        if snap and owner.snap:
            snap_value = owner.unit_system.snap_value
            if owner.unit_system.system_rotation == 'DEGREES':
                if owner.mco_shift_press:
                    rot_scalar = math.radians(1.0)
                else:
                    rot_scalar = math.radians(5.0)
            else:
                if owner.mco_shift_press:
                    rot_scalar = 0.01
                else:
                    rot_scalar = 0.1
            rotation_angle = snap_value(rotation_angle, rot_scalar)

        rotation = Quaternion(rotation_axis, rotation_angle)

        if vec1.length == 0.0:
            v = Vector((1, 0)) * vec2.length
        else:
            v = vec1.normalized() * vec2.length
        angle = rotation_angle
        if negative:
            angle = -angle
        v = Matrix.Rotation(-angle, 2) * v
        mco_draw = v + pivot

        return {'rotation_angle': rotation_angle,
                'rotation_axis': rotation_axis,
                'rotation': rotation,
                '_mco': mco_draw,
                '_value': [rotation_angle]}

    def header_string(self, context, owner):
        return ''


class TrackballMode(NoneMode):
    name = 'Trackball'
    identity = 'TRACKBALL'
    props = [('trackball', PROP.ANGLE, 0.0),
             ('', PROP.ANGLE, 0.0)]
    orientations = [['GLOBAL', 'VIEW', CONST.XYZ],
                    [CONST.CURRENT, 'VIEW', CONST.XYZ]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow']

    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。"""
        return owner.mode != self and event.type == 'R'

    def calc(self, context, owner, snap=True, number_input=True):
        omat = owner.orientation.to_3x3()
        oquat = omat.to_quaternion()

        if number_input and owner.number_input.enable:
            value = [owner.number_input.calc(i) for i in range(2)]
            trackball_x, trackball_y = value
        else:
            trackball_x = owner.mco_relative[0] * (math.pi / 320)
            trackball_y = owner.mco_relative[1] * (math.pi / 320)
            if owner.const_axis == CONST.X:
                trackball_y = 0.0
            elif owner.const_axis == CONST.Y:
                trackball_x = 0.0

            if snap and owner.snap:
                if owner.unit_system.system_rotation == 'DEGREES':
                    if owner.mco_shift_press:
                        rot_scalar = math.radians(1.0)
                    else:
                        rot_scalar = math.radians(5.0)
                else:
                    if owner.mco_shift_press:
                        rot_scalar = 0.01
                    else:
                        rot_scalar = 0.1
                snap_value = owner.unit_system.snap_value
                trackball_x = snap_value(trackball_x, rot_scalar)
                trackball_y = snap_value(trackball_y, rot_scalar)

        cmat = owner.const_orientation.to_3x3()
        axis_x = cmat.col[0]
        axis_y = cmat.col[1]
        rot_y = Quaternion(axis_y, trackball_x)
        rot_x = Quaternion(axis_x, -trackball_y)
        trackball = oquat.inverted() * rot_x * rot_y * oquat

        x = trackball_x / (math.pi / 320)
        y = trackball_y / (math.pi / 320)
        mco_draw = Vector((x, y)) + owner.mco_origin

        return {'trackball': trackball,
                'trackball_x': trackball_x,
                'trackball_y': trackball_y,
                '_mco': mco_draw,
                '_value': [trackball_x, trackball_y]}

    def header_string(self, context, owner):
        return ''


class ResizeMode(NoneMode):
    name = 'Resize'
    identity = 'RESIZE'
    props = [('Scale X', PROP.NONE, 1.0),
             ('Y', PROP.NONE, 1.0),
             ('Z', PROP.NONE, 1.0)]
    orientations = [['GLOBAL', 'GLOBAL', CONST.XYZ],
                    [CONST.CURRENT, CONST.CURRENT, CONST.XYZ]]
    draw_items = ['origin', 'mco', 'const_axis', 'const_arrow', 'resize']

    def poll(self, context, event, owner):
        """このモードに切り替え可能なら真を返す。"""
        return owner.mode != self.identity and event.type == 'S'

    def calc(self, context, owner, snap=True, number_input=True):
        region = context.region
        rv3d = context.region_data
        omat = owner.orientation.to_3x3()
        oimat = omat.inverted()

        location = owner.orientation.to_translation()
        pivot = vav.project(region, rv3d, location).to_2d()

        vec1 = owner.mco_origin - pivot
        vec2 = owner.mco_modify - pivot
        l1 = vec1.length
        l2 = vec2.length

        resize_mat = None

        if number_input and owner.number_input.enable:
            value = [owner.number_input.calc(i) for i in range(3)]
            resize = Vector(value)

        else:
            if l1 != 0.0:
                size = l2 / l1
                if vec1.dot(vec2) < 0.0:
                    size = -size
            else:
                size = 1.0

            if snap and owner.snap:
                scalar = 0.01 if owner.mco_shift_press else 0.1
                size = owner.unit_system.snap_value(size, scalar)

            if owner.const_axis == CONST.NONE:
                resize = Vector((size, size, size))
            elif owner.const_axis == CONST.ANGLE:
                if owner.const_angle is None:
                    resize = Vector((1, 1, 1))
                else:
                    vmat = rv3d.view_matrix.to_3x3()
                    vimat = vmat.inverted()
                    v = Vector((0, 0, -1))
                    q = Quaternion(v, owner.const_angle)
                    m1 = q.to_matrix()
                    m2 = Matrix.Identity(3)
                    m2[0][0] = size
                    resize_mat = (oimat * vimat * m1.inverted() *
                                  m2 * m1 * vmat * omat)
                    # TODO: 数値入力と一致しない
                    resize = Vector((size, size, size))
            elif owner.const_axis == CONST.X:
                resize = Vector((size, 1, 1))
            elif owner.const_axis == CONST.Y:
                resize = Vector((1, size, 1))
            elif owner.const_axis == CONST.Z:
                resize = Vector((1, 1, size))
            elif owner.const_axis == CONST.XY:
                resize = Vector((size, size, 1))
            elif owner.const_axis == CONST.XZ:
                resize = Vector((size, 1, size))
            else:  # if owner.const_axis == CONST.YZ:
                resize = Vector((1, size, size))

        if resize_mat is None:
            m = Matrix.Identity(3)
            for i in range(3):
                m[i][i] = resize[i]
            resize_mat = m

        if number_input and owner.number_input.enable:
            ls = sorted(resize, key=lambda f: abs(f))
            f = abs(ls[-1])
        else:
            f = abs(size)
        mco_draw = vec2.normalized() * l1 * f + pivot

        return {'resize': resize,
                'resize_matrix': resize_mat,
                '_mco': mco_draw,
                '_value': list(resize)}

    def header_string(self, context, owner):
        return ''


#==============================================================================
# ModalMouse
#==============================================================================
class ModalMouse:
    """継承することを前提とする"""
    @property
    def mode(self):
        """:rtype: NoneMode"""
        return self._mode
    @mode.setter
    def mode(self, value):
        if isinstance(value, str):
            for mode in self.modes:
                if mode.identity == value:
                    self._mode = mode
                    break
            else:
                for mode in self.modes:
                    if mode.name == value:
                        self._mode = mode
                        break
        else:
            self._mode = value

    shortcuts = {
        'reset': 'P',
        'constraint': 'MIDDLEMOUSE',
        'orientation': 'O',
        'normalize': 'N',
        'x': 'X',
        'y': 'Y',
        'z': 'Z'
    }
    circle_factor = [0, 165]  # [中心の円の半径:35, 外側の円の半径:200]

    font_id = 0
    font_size = 11
    color = (1.0, 1.0, 1.0)
    header_text_color = (1.0, 1.0, 1.0)
    header_error_color = (1.0, 1.0, 0.0)

    ANGLE_LIMIT = math.radians(5.0)

    def __init__(self, context, event, owner,
                 mode='DISTANCE',
                 modes=(DistanceMode(), FactorMode(), Translation2DMode(),
                        TranslationMode(), RotationMode(), ResizeMode(),
                        TrackballMode()),
                 use_normalized=True, view_location=None):
        self.owner = owner
        self.modes = modes
        self.view_location = view_location
        self.use_normalized = use_normalized
        self._mode = ''
        self.mode = mode

        # UnitSystem
        self.unit_system = unitsystem.UnitSystem(
            context, {'view_location': view_location})

        # ManipulatorMatrix
        self.orientation = manipulatormatrix.ManipulatorMatrix(
            context, default_location=context.scene.cursor_location,
            use_normalized=use_normalized)

        # Number Input
        self.number_input = NumberInput(self)
        self.number_input_value = [0.0 for i in range(len(self.mode.props))]

        self.mco_origin = Vector((event.mouse_region_x, event.mouse_region_y))

        # modal()で更新
        self.mco = self.mco_origin.copy()
        self.mco_shift_press = None  # Vector (2D)  (precision mode)
        self.mco_const_press = None  # Vector (2D) 押した状態を確認するため。
        self._mco_const = None  # Vector(2D) or None
        self.is_const_when_press = False  # MiddleMouseを押した時、既にLock
        self.snap = False  # ctrlキー
        self.const_axis = CONST.NONE  # CONST.***
        self._const_angle = 0.0  # float or None. mco_constと連動

        self.orientation_index = 0  # XXXMode.orientationsのインデックス
        self.const_orientation = self.orientation.copy(3)

        self.update_orientation(context)

        self.result = {}

        # update()で更新
        self.mco_relative = Vector((0, 0))
        self.mco_draw = None  # Vector (2D) 描画用
        self.mco_modify = Vector((0, 0))  # shiftとlockを適用
        self.length_draw = 0.0  # float or None

        # calc_***で値の共有
        self.mco_origin_w = Vector((0, 0, 0))  # self.mco_originのworld座標
        self.mco_modify_w = Vector((0, 0, 0))  # self.mco_modifyのworld座標

        # Draw Handler
        self.region_id = 0
        self.header_region_id = 0
        self._handle = None
        self._header_handle = None
        # context.window_manager.modal_handler_add(owner)
        self.draw_handler_add(context)

    def get_region_header(self, context):
        """現在のAreaのHeaderタイプのRegionを返す"""
        for region in context.area.regions:
            if region.type == 'HEADER':
                return region
        return None

    def draw_handler_add(self, context):
        v3d = context.space_data

        self.region_id = context.region.id
        self._handle = v3d.draw_handler_add(self.draw, (context,),
                                            'WINDOW', 'POST_PIXEL')

        header_region = self.get_region_header(context)
        if header_region:
            self.header_region_id = header_region.id
            self._header_handle = v3d.draw_handler_add(
                self.draw_header, (context,), 'HEADER', 'POST_PIXEL')
        else:
            self.header_region_id = 0
            self._header_handle = None

    def draw_handler_remove(self, context):
        v3d = context.space_data
        if self._handle:
            v3d.draw_handler_remove(self._handle, 'WINDOW')
        if self._header_handle:
            v3d.draw_handler_remove(self._header_handle, 'HEADER')

    def update_orientation(self, context):
        """self.manipulator_matrixとself.const_manipulator_matrixの更新"""
        # self.orientation
        omat = self.orientation
        omat.use_normalized = self.use_normalized
        omat.update_orientations(context, view_only=True)
        elem = self.mode.orientations[self.orientation_index]
        orient, const_orient, middle = elem
        if orient == CONST.CURRENT:
            omat.orientation = omat.transform_orientation(context, True)
        else:
            omat.orientation = orient

        # self.const_orientation
        omat = self.const_orientation
        omat.use_normalized = self.use_normalized  # 常に真でいいような
        omat.update_orientations(context, view_only=True)
        if const_orient == CONST.CURRENT:
            omat.orientation = omat.transform_orientation(context, True)
        else:
            omat.orientation = const_orient

    def axis_test(self, context, index, const_mat=None):
        """
        self.orientation.to_3x3().col[index]と
        視点との角度が閾値以下ならFalseを返す
        """
        rv3d = context.region_data
        if const_mat:
            omat = const_mat
        else:
            omat = self.orientation.to_3x3()
        view_vec = -rv3d.view_matrix.to_3x3().inverted().col[2]  # world
        axis = omat.col[index].normalized()
        val = axis.cross(view_vec).length
        val = max(0.0, min(val, 1.0))
        angle = math.asin(val)
        return angle >= self.ANGLE_LIMIT

    def calc_update(self, context):
        region = context.region
        rv3d = context.region_data

        # --- Update UnitSystem ---
        unit_system = self.unit_system
        unit_system.view_location = self.view_location
        unit_system.update(context)

        # --- Update Orientation ---
        self.update_orientation(context)

        # --- Calc Mouse Region Coords ---
        mco = self.mco
        # mco_relative: Shift分を考慮し修正した座標
        if self.mco_shift_press:
            mco_relative = (self.mco_shift_press - self.mco_origin +
                            (mco - self.mco_shift_press) * 0.1)
        else:
            mco_relative = mco - self.mco_origin
        mco_modify = self.mco_origin + mco_relative  # 修正後のmco
        self.mco_relative = mco_relative
        self.mco_modify = mco_modify
        depth_location = ifel(rv3d.view_location, self.view_location)
        self.mco_origin_w = vav.unproject(region, rv3d, self.mco_origin,
                                          depth_location)
        self.mco_modify_w = vav.unproject(region, rv3d, mco_modify,
                                          depth_location)

        # --- Calc ----
        result = self.mode.calc(context, self)
        self.mco_draw = result.get('_mco')
        self.length_draw = result.get('_length')
        self.number_input_value = result.get('_value')

        self.result = {k: v for k, v in result.items()
                       if not k.startswith('_')}

    @property
    def mco_const(self):
        return self._mco_const
    @mco_const.setter
    def mco_const(self, value):
        self._mco_const = value
        if self._mco_const is not None:
            if (self.mco_const - self.mco_origin).length >= 1.0:
                v1 = Vector((1, 0))
                v2 = value - self.mco_origin
                self._const_angle = vam.vecs_angle(v1, v2)
            else:
                self._const_angle = None
        else:
            self._const_angle = None

    @property
    def const_angle(self):
        return self._const_angle
    @const_angle.setter
    def const_angle(self, value):
        self._const_angle = value
        if value is not None:
            if self._mco_const is None:
                self._mco_const = self.mco_origin.copy()
            length = (self._mco_const - self.mco_origin).length
            if length < 1.0:
                length = 20
            v = Vector((math.cos(value), math.sin(value))) * length
            self._mco_const = v + self.mco_origin

    def set_origin(self, mco):
        """現在のマウスカーソルの位置を基準にする。外部から呼ぶ事を想定する。
        region座標。"""
        # mco = Vector((event.mouse_region_x, event.mouse_region_y))
        mco = Vector(mco)
        if self.mco_const:
            self.mco_const = (mco + self.mco_const - self.mco_origin)
        self.mco_origin = mco.copy()

    def modal(self, context, event):
        """modal()中に呼び出す
        :return: enum set in {'RUNNING_MODAL', 'CANCELLED', 'FINISHED',
                 'PASS_THROUGH'}
        """
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'PASS_THROUGH'}

        # orientationの'VIEW'のみを更新
        self.orientation.update_orientations(context, view_only=True)
        self.const_orientation.update_orientations(context, view_only=True)

        caught, mouse_move = self.number_input.modal(context, event)

        if caught:
            self.calc_update(context)
            return {'RUNNING_MODAL'}

        mco = Vector((event.mouse_region_x, event.mouse_region_y))
        self.mco = mco

        mode = self.mode

        def const_axis_mouse_move():
            """中ボタンで軸固定"""
            if not self.mco_const_press:
                return

            relative = mco - self.mco_origin
            elem = self.mode.orientations[self.orientation_index]
            orient, const_orient, middle = elem
            use_angle = middle == CONST.ANGLE
            if event.alt:
                use_angle ^= True

            if use_angle:  # CONST.ANGLE
                if relative.length >= 1.0:
                    self.mco_const = mco.copy()
                    angle = math.atan2(relative[1], relative[0])
                    # ctrlで10°と45°刻み, ctrl+shiftで1°刻み
                    if event.ctrl:
                        if self.unit_system.system_rotation == 'DEGREES':
                            angle = math.degrees(angle)
                            if event.shift:
                                angle = round(angle)
                            else:
                                for a in (45.0, 135.0, -45, -135.0):
                                    if abs(a - angle) < 5.0:
                                        angle = a
                                        break
                                else:
                                    angle = round(angle / 10) * 10
                            self.const_angle = math.radians(angle)
                        else:
                            if event.shift:
                                self.const_angle = round(angle * 100) / 100
                            else:
                                self.const_angle = round(angle * 10) / 10
                    else:
                        self.const_angle = angle
                else:
                    self.mco_const = None  # const_angleもNoneになる
                self.const_axis = CONST.ANGLE

            else:  # # CONST.XYZ
                view_mat3 = context.region_data.view_matrix.to_3x3()
                relative = self.mco_origin - mco
                cmat = self.const_orientation.to_3x3()
                vals = []
                for i in range(3):
                    if self.axis_test(context, i, cmat):
                        v = (view_mat3 * cmat.col[i]).to_2d().normalized()
                        vals.append(abs(vam.dot2d(v, relative)))
                    else:
                        vals.append(0.0)
                i = vals.index(max(vals))
                self.const_axis = [CONST.X, CONST.Y, CONST.Z][i]
                self.mco_const = mco.copy()

        # def set_origin_and_keep_mco_const_relative(origin):
        #     if self.mco_const:
        #         self.mco_const = (origin + self.mco_const - self.mco_origin)
        #     self.mco_origin = origin.copy()

        retval = {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            if self.mco_const_press:
                const_axis_mouse_move()
            else:
                retval = {'PASS_THROUGH'}

        elif event.value == 'PRESS':
            if event.type in ('LEFT_SHIFT', 'RIGHT_SHIFT'):
                self.mco_shift_press = mco.copy()

            elif event.type in ('LEFT_CTRL', 'RIGHT_CTRL'):
                self.snap = True

            elif event.type in ('LEFT_ALT', 'RIGHT_ALT'):
                if self.mco_const_press:
                    const_axis_mouse_move()

            elif event.type == self.shortcuts.get('reset'):
                # set_origin_and_keep_mco_const_relative(mco)
                self.set_origin(mco)

            elif event.type == self.shortcuts.get('constraint'):
                self.mco_const_press = mco.copy()
                self.is_const_when_press = self.const_axis != CONST.NONE
                const_axis_mouse_move()

            elif event.type == self.shortcuts.get('orientation'):
                self.orientation_index += 1
                if self.orientation_index >= len(mode.orientations):
                    self.orientation_index = 0

            elif event.type == self.shortcuts.get('normalize'):
                self.use_normalized ^= True
                # self.update_orientation(context)

            elif event.type in (self.shortcuts.get('x'),
                                self.shortcuts.get('y'),
                                self.shortcuts.get('z')):
                if event.type == self.shortcuts.get('x'):
                    const_axis = CONST.X
                elif event.type == self.shortcuts.get('y'):
                    const_axis = CONST.Y
                else:
                    const_axis = CONST.Z
                inv_const_axis = CONST(const_axis ^ 0b111)
                axis = const_axis if not event.shift else inv_const_axis

                if len(mode.orientations) == 1:
                    if self.const_axis in (const_axis, inv_const_axis):
                        self.const_axis = CONST.NONE
                    else:
                        self.const_axis = axis
                else:
                    if self.const_axis in (const_axis, inv_const_axis):
                        i = self.orientation_index
                        if i == len(mode.orientations) - 1:
                            # 制限無しへ
                            self.orientation_index = 0
                            self.const_axis = CONST.NONE
                        else:
                            self.orientation_index += 1
                            self.const_axis = axis
                        # self.update_orientation(context)
                    else:
                        # 軸制限を有効にする
                        self.const_axis = axis

            else:
                for mode in self.modes:
                    if mode.poll(context, event, self):
                        self.mode = mode
                        self.const_axis = CONST.NONE
                        self.orientation_index = 0
                        # self.update_orientation(context)
                        # set_origin_and_keep_mco_const_relative(mco)
                        self.set_origin(mco)
                        self.number_input.init_mode()
                        break
                else:
                    retval = {'PASS_THROUGH'}

        elif event.value == 'RELEASE':
            if event.type in ('LEFT_SHIFT', 'RIGHT_SHIFT'):
                self.mco_shift_press = None

            elif event.type in ('LEFT_CTRL', 'RIGHT_CTRL'):
                self.snap = False

            elif event.type in ('LEFT_ALT', 'RIGHT_ALT'):
                if self.mco_const_press:
                    const_axis_mouse_move()

            elif event.type == self.shortcuts.get('constraint'):
                if self.mco_const_press:
                    # 軸制限が有効な時にクリックで軸制限解除
                    if self.is_const_when_press:
                        if (mco - self.mco_const_press).length < 1.0:
                            self.mco_const = None
                            self.const_axis = CONST.NONE
                    self.mco_const_press = None

            else:
                retval = {'PASS_THROUGH'}

        else:
            retval = {'PASS_THROUGH'}

        self.calc_update(context)

        return retval

    # Draw --------------------------------------------------------------------
    def draw(self, context):
        region = context.region
        rv3d = context.region_data

        if region.id != self.region_id:
            return

        glsettings = vagl.GLSettings(context)
        glsettings.push()

        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glEnable(bgl.GL_BLEND)

        color = self.color
        if len(color) == 3:
            color = list(color) + [1.0]
        color_half = list(color)
        color_half[3] /= 2
        x, y = self.mco_origin

        omat3 = self.orientation.to_3x3()
        oloc = self.orientation.to_translation()
        vmat = rv3d.view_matrix
        vimat = vmat.inverted()

        mode = self.mode

        # Lock Holding
        if self.mco_const_press:
            flag = vagl.Buffer('bool', 0, bgl.GL_LINE_STIPPLE)
            bgl.glEnable(bgl.GL_LINE_STIPPLE)
            bgl.glLineStipple(2, int(0b101010101010101))
            bgl.glColor4f(*color_half)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(*self.mco_origin)
            bgl.glVertex2f(*self.mco_const)
            bgl.glEnd()
            vagl.glSwitch(bgl.GL_LINE_STIPPLE, flag)
            bgl.glDisable(bgl.GL_LINE_STIPPLE)

        bgl.glColor4f(*color)

        # Origin
        if 'origin' in mode.draw_items:
            vagl.draw_sun(x, y, 5, 16, [0, math.pi], [10, 10])

        # Relative
        if 'mco' in mode.draw_items:
            if self.mco_draw:
                v = self.mco_draw
            else:
                v = self.mco_modify
            vagl.draw_circle(v[0], v[1], 5, 16)

        # Const Axis
        bgl.glColor4f(*color)
        if 'const_arrow' in mode.draw_items:
            if self.const_axis == CONST.ANGLE:
                # Arrow
                vec = (self.mco_origin - self.mco_const).normalized() * 20
                vecn = self.mco_const + vec
                vagl.draw_arrow(vecn[0], vecn[1],
                                self.mco_const[0], self.mco_const[1],
                                headlength=10, headangle=math.radians(90),
                                headonly=True)

                # スナップ時の角度表示。
                # TODO: radianでのスナップ及び表示に対応する
                if self.mco_const_press:
                    # v = self.mco_const - self.mco_origin
                    # angle = math.atan2(v[1], v[0])
                    angle = self.const_angle
                    # if angle < 0:
                    #     angle += math.pi * 2
                    if self.unit_system.system_rotation == 'DEGREES':
                        text = str(round(math.degrees(angle))) + '°'
                    else:
                        text = '{:.2f}'.format(angle)
                    tw, th = blf.dimensions(self.font_id, text)
                    vx = self.mco_const[0] - tw - 20
                    vy = self.mco_const[1] - th / 2
                    blf.position(self.font_id, vx, vy, 0)
                    vagl.blf_draw(self.font_id, text)
        if 'const_axis' in mode.draw_items:
            if self.const_axis & CONST.XYZ:
                locked = [self.const_axis.value & 0b100,
                          self.const_axis.value & 0b010,
                          self.const_axis.value & 0b001]
                cmat = self.const_orientation.to_3x3()
                for i in range(3):
                    if locked[i]:
                        v = cmat.col[i] * 1000
                        v1 = vav.project(region, rv3d, oloc + v).to_2d()
                        v2 = vav.project(region, rv3d, oloc - v).to_2d()
                        col = [0.5, 0.5, 0.5, 1.0]
                        col[i] = 1.0
                        bgl.glColor4f(*col)
                        bgl.glBegin(bgl.GL_LINES)
                        bgl.glVertex2f(*v1)
                        bgl.glVertex2f(*v2)
                        bgl.glEnd()

        # 点線, 円
        bgl.glColor4f(*color)
        if set(mode.draw_items) & {'rotation', 'resize'}:
            pivot = vav.project(region, rv3d, oloc).to_2d()
            flag = vagl.Buffer('bool', 0, bgl.GL_LINE_STIPPLE)
            bgl.glEnable(bgl.GL_LINE_STIPPLE)
            bgl.glLineStipple(8, int(0b101010101010101))
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(*pivot)
            bgl.glVertex2f(*self.mco_origin)
            if 'rotation' in mode.draw_items:
                bgl.glVertex2f(*pivot)
                bgl.glVertex2f(*self.mco_draw)
            bgl.glEnd()
            vagl.glSwitch(bgl.GL_LINE_STIPPLE, flag)
            if 'resize' in mode.draw_items:
                bgl.glColor4f(*color_half)
                r = (self.mco_origin - pivot).length
                vagl.draw_circle(pivot[0], pivot[1], r, 64)

        # Factor
        if 'factor' in mode.draw_items:
            bgl.glColor4f(*color_half)
            vagl.draw_circle(x, y, self.circle_factor[0], 64)
            vagl.draw_circle(x, y, self.circle_factor[1], 64)

        glsettings.pop()

    def draw_header(self, context):

        if context.region.id != self.header_region_id:
            return

        glsettings = vagl.GLSettings(context)
        glsettings.push()

        color = self.color
        if len(color) == 3:
            color = list(color) + [1.0]

        # Background
        theme = context.user_preferences.themes['Default']
        backcol = theme.view_3d.space.header
        bgl.glColor3f(*backcol)
        bgl.glRecti(0, 0, context.region.width, context.region.height)

        space = 10

        offset_x = space
        offset_y = 10

        # --- Number Input ---
        offset_x, offset_y = self.number_input.draw(
            context, offset_x, offset_y, self.font_id,
            self.font_size, self.header_text_color, self.header_error_color)
        offset_x += space

        # --- Length ---
        # Translationの長さ
        if self.length_draw is not None:
            length = self.length_draw
            text = self.unit_system.num_to_unit(length, rounding_exp=-6)
            text = '(' + text + ')'
            blf.position(self.font_id, offset_x, offset_y, 0)
            bgl.glColor4f(*color)
            blf.draw(self.font_id, text)
            offset_x += blf.dimensions(self.font_id, text)[0] + space

        # --- Orientation ---
        text = ''
        omat = self.orientation
        cmat = self.const_orientation
        if omat.orientation != 'GLOBAL' or self.const_axis & CONST.XYZ:
            if text:
                text += ' '
            t = omat.orientation
            if t in ('GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'GIMBAL',
                     'VIEW'):
                t = t.title()
            text += t
            if omat.orientation != cmat.orientation:
                t = cmat.orientation
                if t in ('GLOBAL', 'LOCAL', 'GRID', 'NORMAL', 'GIMBAL',
                         'VIEW'):
                    t = t.title()
                text += '/' + t

        # --- Angle ---
        if self.const_axis != CONST.NONE:
            if text:
                text += ' '
            if self.const_axis & CONST.ANGLE:
                text += 'A: '
                if self.const_angle is None:
                    text += 'NONE'
                else:
                    angle = self.const_angle
                    if self.unit_system.system_rotation == 'DEGREES':
                        text += '{0:.1f}°'.format(math.degrees(angle))
                    else:
                        text += '{0:.2f}'.format(angle)
            else:
                text += '-'.join(self.const_axis.name.upper())
        if text:
            text = '[' + text + ']'
        # e.g.) '[GLOBAL]', '[GLOBAL X-Y]'
        blf.position(self.font_id, offset_x , offset_y, 0)
        bgl.glColor4f(*color)
        blf.draw(self.font_id, text)
        if text:
            offset_x += blf.dimensions(self.font_id, text)[0] + space

        tail_text = self.mode.header_string(context, self)

        if tail_text:
            blf.position(self.font_id, offset_x, offset_y, 0)
            blf.draw(self.font_id, tail_text)

        glsettings.pop()


#==============================================================================
# ModalMouse Test
#==============================================================================
class TEST_OT_modal_mouse(bpy.types.Operator):
    bl_description = ''
    bl_idname = 'view3d.test_modal_mouse'
    bl_label = 'Test Model Mouse'
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    distance = vap.FP("Dist", default=0.0)
    factor = vap.FP("Fac", default=0.0,
                    min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)

    value = vap.FVP("Value", default=(0.0, 0.0, 0.0, 0.0), size=4)

    @classmethod
    def poll(cls, context):
        area = context.area
        return area and area.type == 'VIEW_3D'

    def modal(self, context, event):
        print(event.type, event.value)
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        actob = context.active_object
        mat = actob.matrix_world
        bm = bmesh.from_edit_mesh(actob.data)
        bm.clear()
        bm.from_mesh(self.mesh)

        retval = self.modal_mouse.modal(context, event)
        print(retval)
        # if retval == {'RUNNING_MODAL'}:
        #     return {'RUNNING_MODAL'}

        result = self.modal_mouse.result

        omat = self.modal_mouse.orientation
        id = self.modal_mouse.mode.identity
        if id == 'TRANSLATION':
            vec = result['translation']
            mv = Matrix.Translation(vec)
            m = mat.inverted() * omat * mv * omat.inverted() * mat
            bm.transform(m, {'SELECT'})

        elif id == 'ROTATION':
            rot = result['rotation'].to_matrix().to_4x4()
            m = mat.inverted() * omat * rot * omat.inverted() * mat
            bm.transform(m.to_4x4(), {'SELECT'})

        elif id == 'RESIZE':
            vec = result['resize']
            ms = Matrix.Identity(4)
            for i in range(3):
                ms[i][i] = vec[i]
            m = mat.inverted() * omat * ms * omat.inverted() * mat

            resize_mat = result['resize_matrix']
            resize_mat = resize_mat.to_4x4()
            m = mat.inverted() * omat * resize_mat * omat.inverted() * mat
            bm.transform(m, {'SELECT'})

        elif id == 'TRACKBALL':
            rot = result['trackball'].to_matrix().to_4x4()
            m = mat.inverted() * omat * rot * omat.inverted() * mat
            bm.transform(m.to_4x4(), {'SELECT'})

        bm.normal_update()
        bmesh.update_edit_mesh(actob.data, True, True)

        print(self.modal_mouse.result)

        context.area.tag_redraw()
        if event.type == 'SPACE':
            self.modal_mouse.draw_handler_remove(context)
            bpy.data.meshes.remove(self.mesh)
            return {'FINISHED'}
        elif event.type == 'ESC':
            self.modal_mouse.draw_handler_remove(context)
            bm.clear()
            bm.from_mesh(self.mesh)
            bm.normal_update()
            bmesh.update_edit_mesh(actob.data, True, True)
            bpy.data.meshes.remove(self.mesh)
            context.area.tag_redraw()
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.modal_mouse = ModalMouse(
            context, event, self,
            mode='DISTANCE',
            modes=(DistanceMode(),
                   FactorMode(),
                   Translation2DMode(),
                   TranslationMode(),
                   RotationMode(),
                   ResizeMode(),
                   TrackballMode()
            ),
            use_normalized=False, view_location=None)

        actob = context.active_object
        self.mesh = actob.data.copy()
        bm = bmesh.from_edit_mesh(actob.data)
        bm.to_mesh(self.mesh)
        # self.mesh = bpy.data.meshes.new("tmp")
        # bm = bmesh.from_edit_mesh(actob.data)
        # bm.to_mesh(self.mesh)
        # self.mat = actob.matrix_world.copy()
        # self.rotation_quaternion = actob.rotation_quaternion.copy()
        # self.scale = actob.scale.copy()
        return {'RUNNING_MODAL'}


# bpy.utils.register_class(TEST_OT_modal_mouse)
