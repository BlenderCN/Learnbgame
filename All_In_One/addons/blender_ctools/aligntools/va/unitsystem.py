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

from mathutils import Vector
import bgl

from .. import localutils
from ..localutils import units

from . import vagl
from . import vaview3d as vav


def _prop(attr):
    def fget(self):
        """値がNoneの場合は無視する"""
        if attr in self.override:
            value = self.override[attr]
            if value is not None:
                return self.override[attr]
        return getattr(self, '_' + attr)
    def fset(self, value):
        self.override[attr] = value
    def fdel(self):
        if attr in self.override:
            del self.override[attr]
    return property(fget, fset, fdel)


class UnitSystem:
    GRID_MIN_PX = 6.0

    metric_units = localutils.units.metric_units.copy()
    imperial_units = localutils.units.imperial_units.copy()
    mixed_units = localutils.units.mixed_units.copy()
    empty_units = localutils.units.empty_units.copy()

    @property
    def units(self):
        if self.system == 'METRIC':
            return self.metric_units
        elif self.system == 'IMPERIAL':
            return self.imperial_units

    def __init__(self, context, override=None, image_editor_unit='x'):
        """
        :param override: 属性取得の際にこちらを優先する。以下は有効な属性
            system, system_rotation, scale_length, use_separate,
            grid_scale, grid_subdivisions, view_location
        :type override: dict
        :param image_editor_unit: SpaceImageEditorでの単位とアスペクトの処理
            'x': UV座標でX軸を計算する
            'y': UV座標でY軸を計算する
            'pixel_x': 画像のPixelを用いた座標でX軸を計算する
            'pixel_y': 画像のPixelを用いた座標でY軸を計算する
        :type image_editor_unit: str
        """
        self.override = {} if override is None else override

        # 変数 ----------------------------------------------------------------
        # Scene.unit_settings.system ['NONE', 'METRIC', 'IMPERIAL']
        self._system = 'NONE'

        # Scene.unit_settings.system_rotation ['DEGREES', 'RADIANS']
        # num_to_unit(), unit_to_num() で使う
        self._system_rotation = 'DEGREES'

        # Scene.unit_settings.scale_length
        # e.g. system: METRIC, scale_length: 2.0 -> 1BU == 2.0m
        self._scale_length = 1.0

        # Scene.unit_settings.use_separate
        self._use_separate = False

        # SpaceView3D.grid_scale
        self._grid_scale = 1.0

        # SpaceView3D.grid_subdivisions
        self._grid_subdivisions = 10

        # RegionView3D.view_location
        self._view_location = Vector((0, 0, 0))

        # SpaceImageEditorで計算する軸を指定する
        self.image_editor_unit = image_editor_unit

        # 計算結果 ------------------------------------------------------------
        # dpbuとunit_powはsystemに影響されない

        # if self.system == 'NONE': utit = None
        # self.systemが'NONE'ならNone。それ以外ならUnitのインスタンス
        self.unit = None

        # dot per blenderUnit. IMAGE_EDITORの場合は dot per pixel を表す
        self.dpbu = 1.0

        # dot per grid
        self.dx = 1.0

        # grid_scale * 10 ** unit_pow == blenderUnit per grid (system: 'NONE')
        self.unit_pow = 0

        # blenderUnit per grid  (same as rv3d->gridview)
        self.grid_view = 1.0

        # SpaceImageEditorで表示中の画像の大きさ
        self.image_size = [0, 0]

        self.update(context)

    system = _prop('system')
    system_rotation = _prop('system_rotation')
    scale_length = _prop('scale_length')
    use_separate = _prop('use_separate')
    grid_scale = _prop('grid_scale')
    grid_subdivisions = _prop('grid_subdivisions')
    view_location = _prop('view_location')

    # blenderUnit / grid
    @property
    def bupg(self):
        return self.grid_view
    @bupg.setter
    def bupg(self, value):
        self.grid_view = value

    # dot / grid
    @property
    def dpg(self):
        return self.dx
    @dpg.setter
    def dpg(self, value):
        self.dx = value

    # blenderUnit / dot
    @property
    def bupd(self):
        return 1.0 / self.dpbu
    @bupd.setter
    def bupd(self, value):
        self.dpbu = 1.0 / value

    # grid / blenderUnit
    @property
    def gpbu(self):
        return 1.0 / self.grid_view
    @gpbu.setter
    def gpbu(self, value):
        self.grid_view = 1.0 / value

    # grid / dot
    @property
    def gpd(self):
        return 1.0 / self.dx
    @gpd.setter
    def gpd(self, value):
        self.dx = 1.0 / value

    def _get_image_size(self, context):
        image_sx = image_sy = 0
        if context.area.type == 'IMAGE_EDITOR':
            space = context.area.spaces.active
            image = space.image
            if image:
                if image.type in ('RENDER_RESULT', 'COMPOSITING'):
                    # 'POST_VIEW'でのみ使用可能な方法
                    if image.type == 'RENDER_RESULT' or image.pixels:
                        region = context.region
                        mat = vagl.Buffer('double', (4, 4),
                                          bgl.GL_PROJECTION_MATRIX)
                        # 画像のアスペクト比はzoom[1]に反映されている
                        fx = mat[0][0] / space.zoom[0]
                        fy = mat[1][1] / space.zoom[1]
                        image_sx = round(region.width / 2 * fx)
                        image_sy = round(region.height / 2 * fy)
                else:
                    image_sx, image_sy = image.size
        return [image_sx, image_sy]

    def update(self, context):
        """contextの要素でself._***を更新した上でdpbu等を計算する。
        IMAGE_EDITORの場合、グリッド分割は画像のpixelの大きさ迄とする
        """
        # read context --------------------------------------------------------

        if context.area.type == 'VIEW_3D':
            scene = context.scene
            unit_settings = scene.unit_settings
            self._system = unit_settings.system
            self._system_rotation = unit_settings.system_rotation
            self._scale_length = unit_settings.scale_length
            self._use_separate = unit_settings.use_separate
            v3d = context.space_data
            rv3d = context.region_data
            self._grid_scale = v3d.grid_scale
            self._grid_subdivisions = v3d.grid_subdivisions
            self._view_location = Vector(rv3d.view_location)
        else:
            self._system = 'NONE'
            self._system_rotation = 'DEGREES'
            self._scale_length = 1.0
            self._use_separate = False
            self._grid_scale = 1.0
            self._grid_subdivisions = 10
            self._view_location = Vector((0, 0, 0))

        region = context.region
        sx, sy = region.width, region.height
        system = self.system
        view_location = self.view_location

        self.image_size = self._get_image_size(context)

        # Calculate blenderUnit -----------------------------------------------
        if context.area.type == 'VIEW_3D':
            rv3d = context.region_data
            if rv3d is None:
                return False

            # viewinvmat = rv3d.view_matrix.inverted()
            persmat = rv3d.perspective_matrix
            pimat = persmat.to_3x3().inverted()
            if sx >= sy:  # この分岐に大した意味は無い
                v = pimat.col[0].normalized()  # viewのx方向で長さが1bu
            else:
                v = pimat.col[1].normalized()  # viewのy方向で長さが1bu
            v1 = vav.project_v3(sx, sy, persmat, view_location)
            v2 = vav.project_v3(sx, sy, persmat, view_location + v)
            dpbu = dx = (v1 - v2).to_2d().length

            # TODO: from view3d_draw.c
            if 0:
                """
                /* calculate pixelsize factor once, is used for lamps and obcenters */
                {
                    /* note:  '1.0f / len_v3(v1)'  replaced  'len_v3(rv3d->viewmat[0])'
                     * because of float point precision problems at large values [#23908] */
                    float v1[3], v2[3];
                    float len_px, len_sc;

                    v1[0] = rv3d->persmat[0][0];
                    v1[1] = rv3d->persmat[1][0];
                    v1[2] = rv3d->persmat[2][0];

                    v2[0] = rv3d->persmat[0][1];
                    v2[1] = rv3d->persmat[1][1];
                    v2[2] = rv3d->persmat[2][1];

                    len_px = 2.0f / sqrtf(min_ff(len_squared_v3(v1), len_squared_v3(v2)));
                    len_sc = (float)MAX2(ar->winx, ar->winy);

                    rv3d->pixsize = len_px / len_sc;
                }
                """
                v1 = persmat[0].to_3d()
                v2 = persmat[1].to_3d()
                len_px = 2.0 / min(v1.length, v2.length)
                len_sc = max(sx, sy)
                pixsize = len_px / len_sc
                # print(dpbu, 1.0 / pixsize)
                print('pixsize', pixsize)

                def mul_project_m4_v3_zfac(mat, co):
                    return ((mat.col[0][3] * co[0]) + (mat.col[1][3] * co[1]) + (
                    mat.col[2][3] * co[2]) + mat.col[3][3])

                def ED_view3d_pixel_size(mat, co):
                    return mul_project_m4_v3_zfac(mat, co) * pixsize * 1.0

                print('final', ED_view3d_pixel_size(persmat, view_location))

        elif context.area.type == 'IMAGE_EDITOR':
            image_editor_unit = self.image_editor_unit.lower()
            for region in context.area.regions:
                if region.type == 'WINDOW':
                    break
            v2d = region.view2d
            v1 = v2d.region_to_view(0, 0)
            if image_editor_unit in ('pixel_x', 'x'):
                v2 = v2d.region_to_view(region.width, 0)
                bupd = (v2[0] - v1[0]) / region.width
                if image_editor_unit == 'pixel_x':
                    image_sx = self.image_size[0]
                    if image_sx == 0:
                        image_sx = 256  # blenderの仕様。Imageが無い場合は256になる
                    bupd *= image_sx
            else:  # 'pixel_y', 'y':
                v2 = v2d.region_to_view(0, region.height)
                bupd = (v2[1] - v1[1]) / region.height
                if image_editor_unit == 'pixel_y':
                    image_sy = self.image_size[1]
                    if image_sy == 0:
                        image_sy = 256
                    bupd *= image_sy
            dpbu = dx = 1.0 / bupd

        elif context.area.type == 'NODE_EDITOR':
            # view2dでは値が一致しない
            space = context.area.spaces.active
            cursor_bak = space.cursor_location[:]
            space.cursor_location_from_region(0, 0)
            v1 = space.cursor_location[:]
            if region.width > region.height:  # 誤差を少しでも減らすため
                space.cursor_location_from_region(region.width, 0)
                v2 = space.cursor_location
                bupd = (v2[0] - v1[0]) / region.width
            else:
                space.cursor_location_from_region(0, region.height)
                v2 = space.cursor_location
                bupd = (v2[1] - v1[1]) / region.height
            space.cursor_location = cursor_bak
            dpbu = dx = 1.0 / bupd
        elif context.region.view2d:
            v2d = region.view2d
            v1 = v2d.region_to_view(0, 0)
            if region.width > region.height:  # 誤差を少しでも減らすため
                v2 = v2d.region_to_view(region.width, 0)
                bupd = (v2[0] - v1[0]) / region.width
            else:
                v2 = v2d.region_to_view(0, region.height)
                bupd = (v2[1] - v1[1]) / region.height
            dpbu = dx = 1.0 / bupd
        else:
            raise ValueError()

        sublines = self.grid_subdivisions
        unit_pow = 0
        grid_view = self.grid_scale
        dx *= grid_view
        if dx < self.GRID_MIN_PX:
            while dx < self.GRID_MIN_PX:
                dx *= sublines
                grid_view *= sublines
                unit_pow += 1
        else:
            while dx > self.GRID_MIN_PX * sublines:
                if 0:
                    if context.area.type == 'IMAGE_EDITOR':
                        if grid_view / sublines < 1:
                            break
                dx /= sublines
                grid_view /= sublines
                unit_pow -= 1
        self.dpbu = dpbu
        self.unit_pow = unit_pow

        # Calculate Unit ------------------------------------------------------
        if system == 'NONE':
            self.unit = None
            self.dx = dx
            self.grid_view = grid_view
        else:
            f = self.grid_scale / self.scale_length
            self.unit = None
            if system == 'METRIC':
                units = self.metric_units
            else:
                units = self.imperial_units
            units = list(reversed(units))
            for unit in units:
                bupg = float(unit.scalar) * f
                dpg = dpbu * bupg
                if dpg < self.GRID_MIN_PX * 2:
                    continue
                self.unit = unit
                self.dx = dpg
                self.grid_view = bupg
                break
            else:
                self.unit = unit
                self.dx = dpg
                self.grid_view = bupg

        return True

    # String <-> Numeric ------------------------------------------------------
    def unit_to_num(self, string, system=None, system_rotation=None,
                    scale_length=None, use_decimal=False, fallback=None):
        """返り値の単位について、
        長さはBlenderUnitで、角度はsystem_rotation基準とする
        """
        if system is None:
            system = self.system
        if system_rotation is None:
            system_rotation = self.system_rotation
        if scale_length is None:
            scale_length = self.scale_length

        if system == 'NONE':
            units = self.mixed_units
        elif system == 'METRIC':
            units = self.metric_units
        else:
            units = self.imperial_units

        user_def = [['bu', scale_length], ['px', self.bupd * scale_length]]
        if system_rotation == 'RADIANS':
            user_def.extend(
                [['r', scale_length],  # radian
                 ['rad', scale_length],
                 ['d', math.pi / 180 * scale_length],  # degree
                 ['°', math.pi / 180 * scale_length]
                 ])
        else:
            user_def.extend(
                [['r', 180 / math.pi * scale_length],  # radian
                 ['rad', 180 / math.pi * scale_length],
                 ['d', scale_length],  # degree
                 ['°', scale_length]
                 ])
        units.extend(user_def)
        units.update()
        num = units.unit_to_num(string, scale_length, use_decimal)
        units[-len(user_def):] = []
        units.update()
        if num is None:
            return fallback
        return num

    def num_to_unit(self, value, system=None,
                    scale_length=None, use_separate=None, start='', end='mm',
                    verbose=False, rounding_exp=None, rounding=None,
                    normalize=False, eps=None, use_decimal=False):
        """unit_to_num()のように角度には対応していない"""
        if system is None:
            system = self.system
        if system == 'NONE':
            units = self.empty_units
            user_def = [['', 1.0]]
            units.extend(user_def)
            units.update()
        elif system == 'METRIC':
            units = self.metric_units
        else:
            units = self.imperial_units

        if scale_length is None:
            scale_length = self.scale_length
        if use_separate is None:
            use_separate = self.use_separate
        if eps is None:
            eps = 1e-10
        result = units.num_to_unit(
            value, scale_length, use_separate,
            start, end, verbose, rounding_exp, rounding, normalize, eps,
            use_decimal)

        if system == 'NONE':
            units[-len(user_def):] = []
            units.update()

        return result

    # Snap --------------------------------------------------------------------
    @classmethod
    def snap_value(cls, value, scalar):
        return scalar * math.floor(0.5 + value / scalar)

    def snap_grid(self, value: 'Vector or float', precision=False,
                  v3d=None, local_grid_location=None, local_grid_rotation=None):
        """
        valueが四次のVectorの場合、W値はスナップしない。
        v3d: valueが三次(四次)のVectorでlocal_gridが有効であればそれにスナップする
        local_grid_location, local_grid_rotation:
            localgridの情報。v3dより優先される。
        """
        bupg = self.bupg  # == grid_view
        if precision:
            bupg /= 10
        if isinstance(value, Vector):
            vec = value

            origin = quat = None
            if v3d and hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
                origin = v3d.local_grid_location
                quat = v3d.local_grid_rotation
            if local_grid_location:
                origin = local_grid_location
            if local_grid_rotation:
                quat = local_grid_rotation

            if origin and quat and len(vec) >= 3:
                mat = quat.to_matrix().to_4x4()
                mat.translation = origin
                imat = mat.inverted()
                v = imat * vec.to_3d()
                for i in range(3):
                    v[i] = bupg * math.floor(0.5 + v[i] / bupg)
                v = mat * v
                if len(vec) == 4:
                    v = v.resize_4d()
                    v[3] = vec[3]
            else:
                v = vec.copy()
                for i in range(min(len(v), 3)):
                    v[i] = bupg * math.floor(0.5 + v[i] / bupg)
            return v

        else:
            return bupg * math.floor(0.5 + value / bupg)

    def snap_local_grid(self, context, value: 'Vector or float',
                        precision=False, v3d=None):
        if v3d is None:
            v3d = context.space_data
        if v3d and hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
            origin = v3d.local_grid_location
            quat = v3d.local_grid_rotation
        else:
            origin = quat = None
        return self.snap_grid(value, precision,
                              local_grid_location=origin,
                              local_grid_rotation=quat)

    def __str__(self):
        ls = ['UnitSystem:',
              '    system: {}, scale_length: {}, ' + \
                  'grid_scale: {}, grid_subdivisions: {},',
              '    unit:            {}',
              '    dpbu:            {} (dot per blenderUnit)',
              '    dx, dpg:         {} (dot per grid)',
              '    grid_view, bupg: {} (blenderUnit per grid)',
              '    unit_pow:        {} (grid_scale * 10 ** unit_pow -> ' + \
                  'blenderUnit per grid (only system is \'NONE\'))']
        text = '\n'.join(ls)
        text = text.format(self.system, self.scale_length,
                           self.grid_scale, self.grid_subdivisions,
                           None if not self.unit else self.unit.name,
                           self.dpbu, self.dx, self.grid_view, self.unit_pow)
        return text
