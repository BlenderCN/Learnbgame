# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
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


bl_info = {
    'name': 'Region Ruler',
    'author': 'chromoly',
    'version': (2, 4),
    'blender': (2, 77, 0),
    'location': 'View3D > Properties, ImageEditor > Properties',
    'description': '',
    'warning': '',
    'wiki_url': 'https://github.com/chromoly/regionruler',
    'category': '3D View',
}


"""
View3D、ImageEditor、NodeEditorにRulerを表示。

Measureボタンで簡易的な距離、角度の計測が出来る。Shift+左クリックでポインタ
追加、右クリックで削除、Shift+右ドラッグで移動、Measureボタンをもう一度押すか
ESCキーで終了。
設定からSimpleMeasureを有効にしていると、Altキーを押している間この機能が有効に
なる。

各SpaceのUnit,Origin等の値はTextObjectへ保存される。

ModalOperatorの実行中はAutoSaveが無効になるので、wm.save_as_mainfile()等を用い
てその挙動を模倣する。(Windows, Linuxのみ)
"""


from collections import OrderedDict
import decimal
from decimal import Decimal
import importlib
import logging
import math
import os
import platform
# import pprint
import string
import time

import bpy
import bgl
import blf
from mathutils import Matrix, Vector
import mathutils.geometry as geom
from bpy.app.handlers import persistent

# import va
# import va.vaprops as vap
# import va.vagl as vagl
# import va.vaview3d as vav
# import va.vawm as vawm
# import va.vamath as vam
# from va.unitsystem import UnitSystem
try:
    importlib.reload(unitsystem)
    importlib.reload(utils)
    importlib.reload(vagl)
    importlib.reload(vam)
    importlib.reload(vap)
    importlib.reload(vav)
    importlib.reload(vawm)
except NameError:
    from . import unitsystem
    from . import utils
    from . import vagl
    from . import vamath as vam
    from . import vaprops as vap
    from . import vaview3d as vav
    from . import vawm


# 他のModalHandlerが開始する度にRulerを再起動する
KEEP_MODAL_HANDLERS_HEAD = False

# 数値の縁取り
VIEW_3D_NUMBER_OUTLINE = False
IMAGE_EDITOR_NUMBER_OUTLINE = True
NODE_EDITOR_NUMBER_OUTLINE = False
OUTLINE_RADIUS = 5  # 0, 3, 5

# プラットフォームにより2.0の場合あり
PIXEL_SIZE = 1.0


###############################################################################
# Log
###############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setLevel(logging.NOTSET)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(name)s.%(funcName)s():%(lineno)d]: '
    '%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


###############################################################################
# Property
###############################################################################
class RegionRuler_PG_Font(bpy.types.PropertyGroup):
    id = vap.IP(
        'ID',
        'Font ID',
        default=0,
        min=0, max=100, soft_min=0, soft_max=100)
    margin = vap.IP(
        'Margin',
        default=3,
        min=0, max=50, soft_min=0, soft_max=50)
    size = vap.IP(
        'Size',
        'Font size',
        default=10,
        min=1, max=100, soft_min=1, soft_max=100)
    mcsize = vap.IP(
        'MC-Size', 'Font size of mouse coordinate',
        default=12,
        min=1, max=100, soft_min=1, soft_max=100)
    measize = vap.IP(
        'Mea-Size',
        'Font size of measure',
        default=11,
        min=1, max=100, soft_min=1, soft_max=100)


class RegionRuler_PG_Color(bpy.types.PropertyGroup):
    line = vap.FVP(
        'Line',
        default=(1.0, 1.0, 1.0),
        min=0, max=1, soft_min=0, soft_max=1,
        subtype='COLOR_GAMMA', size=3)
    # 線と数字の色をわざわざ分ける必要は無さそうなので
    def number_getter(self):
        return self.line
    def number_setter(self, value):
        self.line = value
    number = vap.FVP(
        'Number',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR_GAMMA', size=3,
        get=number_getter, set=number_setter)
    number_outline = vap.FVP(
        'Number Outline',
        default=(0.0, 0.0, 0.0, 1.0),
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR_GAMMA', size=4)
    cursor = vap.FVP(
        'Cursor',
        default=(1.0, 1.0, 1.0, 0.3),
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR_GAMMA', size=4)
    cursor_bold = vap.FVP(
        'Cursor Bold',
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0,
        subtype='COLOR_GAMMA', size=4)


class RegionRuler_PG(bpy.types.PropertyGroup):
    """WindowManager.region_ruler"""
    def _enabled_update(self, context):
        if not data.ignore_operator_call:
            if self.enable:
                if bpy.ops.view3d.region_ruler.poll():  # ランタイムエラー回避
                    bpy.ops.view3d.region_ruler('INVOKE_DEFAULT', False)
        redraw_regions(context)

    enable = vap.BP('Enable',
                    default=False,
                    update=_enabled_update)

    def _update_redraw(self, context):
        redraw_regions(context)

    _measure = 0

    def _measure_get(self):
        return self.__class__._measure

    def _measure_set(self, value):
        self.__class__._measure = value

    measure = vap.BP('Measure',get=_measure_get, set=_measure_set,
                     update=_update_redraw)

    origin_type = vap.EP(
        'Origin Type',
        items=(('scene', 'Scene', 'Scene origin'),
               ('object', 'Active Object', 'Active object origin'),
               ('cursor', '3D Cursor', ''),
               ('view', 'View Center', 'View center'),
               ('custom', 'Custom', '')),
        default='scene',
        update=_update_redraw
    )
    image_editor_origin_type = vap.EP(
        'Origin Type',
        items=(('uv', 'UV / Image', 'Lower left'),
               ('cursor', '2D Cursor', ''),
               ('view', 'View Center', 'View center'),
               ('custom', 'Custom', '')),
        default='uv',
        update=_update_redraw
    )

    origin_location = vap.FVP(
        'Origin Location',
        default=(0, 0, 0),
        subtype='XYZ',
        unit='LENGTH',
        update=_update_redraw)

    image_editor_origin_location = vap.FVP(
        'Origin Location',
        default=(0, 0),
        subtype='XYZ',
        unit='LENGTH',
        update=_update_redraw)

    unit = vap.EP(
        'Unit',
        items=(('auto', 'Automatic', 'Use scene.unit_settings.system'),
               ('none', 'None', 'Blender unit'),
               ('metric', 'Metric', ''),
               ('imperial', 'Imperial', '')),  # imperialへの対応には問題が残る
        default='auto',
        update=_update_redraw)

    image_editor_unit = vap.EP(
        'ImageEditor Unit',
        items=(('pixel', 'Pixel', ''),
               ('uv', 'UV', '')),
        default='pixel',
        update=_update_redraw,
    )

    node_editor_unit = vap.EP(
        'NodeEditor Unit',
        items=(('node', 'Node',
                'used in Node.location and SpaceNodeEditor.cursor_location'),
               ('view2d', 'View2D', '')),
        default='node',
        update=_update_redraw,
    )

    view_depth = vap.EP(
        'View Depth',
        "Used in 'PERSP' or 'CAMERA'",
        items=(('view', 'View', 'View or Camera'),
               ('cursor', '3D Cursor', '')),
        default='view',
        update=_update_redraw)


space_prop = utils.SpaceProperty(
    [bpy.types.SpaceView3D, 'region_ruler', RegionRuler_PG],
    [bpy.types.SpaceImageEditor, 'region_ruler', RegionRuler_PG],
    [bpy.types.SpaceNodeEditor, 'region_ruler', RegionRuler_PG]

)


class RegionRulerPreferences(
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    def draw_property(self, attr, layout, text=None, skip_hidden=True,
                      row=False, **kwargs):
        """プロパティを描画。別オブジェクトのプロパティを描画する為に
        このメソッドをクラスから呼び出し、selfに別オブジェクトを渡すという
        使い方も可
        """
        if attr == 'rna_type':
            return None
        properties = self.rna_type.properties
        prop = properties[attr] if attr in properties else None

        if skip_hidden and prop.is_hidden:
            return None
        col = layout.column(align=True)
        sub = col.row()
        name = prop.name if text is None else text
        if prop.type == 'BOOLEAN' and prop.array_length == 0:
            sub.prop(self, attr, text=name, **kwargs)
        else:
            if name:
                sub.label(name + ':')
            sub = col.row() if row else col.column()
            if prop.type == 'ENUM' and \
                    (prop.is_enum_flag or 'expand' in kwargs):
                sub.prop(self, attr, **kwargs)  # text=''だとボタン名が消える為
            else:
                sub.prop(self, attr, text='', **kwargs)
        return col

    bl_idname = __name__

    font = vap.PP(
        'Font',
        type=RegionRuler_PG_Font)
    color = vap.PP(
        'Color',
        type=RegionRuler_PG_Color)

    scale_size = vap.IVP(
        'Scale Size',
        '[main, even, odd]',
        default=(6, 3, 3),
        min=0, max=40, soft_min=0, soft_max=40, size=3)
    number_min_px = vap.IVP(
        'Number min px',
        '[5, 1]. 最小グリッドの大きさ(dot)がこの値より大きくなると'
        '最小グリッド*5(or最小グリッド)の位置に数値を表示する。',
        default=(18, 90),  # (18, 36)
        min=1, max=120, soft_min=6, soft_max=60, size=2)
    draw_mouse_coordinates = vap.BP(
        'Mouse Coordinates',
        default=False)
    mouse_coordinates_position = vap.EP(
        'Mouse Coordinates Position',
        items=(('cursor', 'Cursor', ''),
               ('lower_right', 'Lower Right', '')),
        default='cursor')
    autohide_mouse_coordinate = vap.BP(
        'Auto Hide Mouse Coordinates',
        default=True)
    autohide_MC_threshold = vap.IP(
        'Threshold',
        'Auto hide threshold',
        default=10,
        min=0, max=100, soft_min=0, soft_max=100)
    use_simple_measure = vap.BP(
        'Use Simple Measure',
        'Hold alt key',
        default=False)
    use_fill = vap.BP(
        'Use Fill',
        description='Fill text box',
        default=True)
    text_object_name = vap.SP(
        'TextObject Name',
        default='region_ruler.config')

    draw_cross_cursor = vap.BP(
        'Cross Cursor',
        default=False)
    cross_cursor = vap.IVP(
        'Cross Cursor',
        '[offset, size]',
        default=(15, 0),
        min=0, size=2)

    auto_save = vap.BP(
        'Auto Save',
        "If a modal operator is running, don't autosave. "
        'So Use imitated automatic saving '
        '(Sculpt or edit mode data will be saved!)',
        default=True
    )

    def draw(self, context):
        cls = self.__class__
        layout = self.layout
        split = layout.split()

        col = split.column()

        color = self.color
        cls.draw_property(color, 'line', col)
        # cls.draw_property(color, 'number', col)
        cls.draw_property(color, 'number_outline', col)
        prop = cls.draw_property(color, 'cursor', col)
        prop.active = self.draw_cross_cursor

        font = self.font
        # self.draw_property(font, 'id', col)
        cls.draw_property(font, 'size', col, text='Font Size')
        prop = cls.draw_property(font, 'mcsize', col, text='Font Size (MC)')
        prop.active = self.draw_mouse_coordinates
        cls.draw_property(font, 'margin', col)

        col = split.column()
        self.draw_property('scale_size', col, row=True)
        self.draw_property('number_min_px', col, row=True)
        self.draw_property('draw_mouse_coordinates', col)
        prop = self.draw_property('mouse_coordinates_position', col)
        prop.active = self.draw_mouse_coordinates
        prop = self.draw_property('autohide_mouse_coordinate', col)
        prop.active = self.draw_mouse_coordinates
        prop = self.draw_property('autohide_MC_threshold', col)
        prop.active = self.draw_mouse_coordinates and \
            self.autohide_mouse_coordinate

        col = split.column()
        self.draw_property('use_simple_measure', col, text='Simple Measure')
        self.draw_property('draw_cross_cursor', col, row=True)
        prop = self.draw_property('cross_cursor', col, text='', row=True)
        prop.active = self.draw_cross_cursor
        # self.draw_property('image_editor_unit', col, row=True, expand=True)
        # self.draw_property('view_depth', col)
        self.draw_property('use_fill', col)
        self.draw_property('auto_save', col)


###############################################################################
# Data
###############################################################################
def get_widget_unit(context):
    # U.widget_unit = (U.pixelsize * U.dpi * 20 + 36) / 72;
    PIXEL_SIZE = 1.0  # macだと1.0以外の可能性
    U = context.user_preferences
    if U.system.virtual_pixel_mode == 'NATIVE':
        pixel_size = PIXEL_SIZE * 1.0
    else:  # 'DOUBLE'
        pixel_size = PIXEL_SIZE * 2.0
    dpi = U.system.dpi
    return int((pixel_size * dpi * 20 + 36) / 72)


def get_view_location(context):
    prefs = RegionRulerPreferences.get_instance()
    ruler_settings = space_prop.get(context.space_data, 'region_ruler')
    region = context.region
    rv3d = context.region_data
    if ruler_settings.view_depth == 'cursor':
        view_location = context.scene.cursor_location
    else:
        if rv3d.view_perspective == 'CAMERA':
            obj = context.scene.camera
            camera = obj.data
            if camera.dof_object:
                view_location = camera.dof_object.matrix_world.to_translation()
            else:
                mat = obj.matrix_world
                vec = -mat.col[2].to_3d().normalized()  # カメラ視線方向
                if camera.dof_distance != 0.0:
                    f = camera.dof_distance
                else:
                    f = (camera.clip_start + camera.clip_end) / 2
                view_location = mat.to_translation() + f * vec
        else:
            view_location = rv3d.view_location
            if rv3d.view_perspective == 'PERSP':
                vec = vav.project(region, rv3d, view_location)
                if abs(vec[2]) < 1e-5:  # 閾値は適当
                    vec[2] = 0.5
                    view_location = vav.unproject(region, rv3d, vec)
    return view_location


class Data:
    def __init__(self):
        # RegionRuler_PG.enableをTrueとした際に、そのプロパティのupdate関数が
        # オペレータを呼び出すのを抑制する
        self.ignore_operator_call = False

        self.active_window = None  # Window.as_pointer()

        # {Window.as_pointer(): Event, ...}
        self.events = {}
        # {Window.as_pointer(): (x, y), ...}  modal()中に更新
        self.mouse_coords = {}
        # {Window.as_pointer(): [Operator, ...], ...}
        # scene_update_postで終了指定されたものがoperatorsからこちらに移る
        self.exit_waiting = {}

        # {SpaceView3D.as_pointer(): {}, ...}
        self.spaces = OrderedDict()
        # {Window.as_pointer(): Operator, ...}
        self.operators = {}
        # draw callback handler
        self.handle = None  # VIEW_3D
        self.handle_image = None  # IMAGE_EDITOR
        self.handle_node = None  # NODE_EDITOR

        # self.updated_space()で更新するもの
        self.unit_system = None  # modalmouse.UnitSystem
        self.unit_system_2d_x = self.unit_system_2d_y = None  # IMAGE_EDITOR用
        self.view_type = 'top'
        self.sign_x = 1  # 1 or -1
        self.sign_y = 1  # 1 or -1
        self.range_x = [0.0, 0.0]  # 左端、右端のworld座標
        self.range_y = [0.0, 0.0]  # 下端、上端のworld座標
        self.mval = Vector((0.0, 0.0))  # range_xとrange_yを元にしたworld座標
        # self.image_display_aspect = 1.0  # IMAGE_EDITOR用
        self.is_inside = False  # マウスがRegionの内側に有るか
        self.mcbox_x = [0, 0, 0, 0]  # draw_mouse_coordinatesで更新
        self.mcbox_y = [0, 0, 0, 0]  # draw_mouse_coordinatesで更新

        # modal中で更新
        self.prev_region_id = -1  # Region.id

        # Measure
        self.last_region_id = -1
        self.simple_measure = False
        self.measure_points = []  # 3D
        #self.active_point_index = None
        self.shift = None
        self.alt = False
        self.alt_disable_count = 0

        # Auto Save
        self.auto_save_time = time.time()

    def wm_sync(self):
        """WindowManagerに存在しない物をself.operatorsとself.spacesから削除。
        self.spacesに限って必要な要素を追加する。
        """
        # delete operators
        context = bpy.context
        wm = context.window_manager
        prefs = RegionRulerPreferences.get_instance()
        valid_addresses = [win.as_pointer() for win in wm.windows]
        for address in list(self.operators):
            if address not in valid_addresses:
                logger.debug('Delete invalid operator: ' +
                             str(self.operators[address]))
                del self.operators[address]

        # delete and add spaces
        # ruler起動中は新規スペースのenableフラグはTrueとなる
        default_value = bool(self.operators)
        d = OrderedDict()
        for screen in bpy.data.screens:
            for area in screen.areas:
                for space in area.spaces:
                    if space.type in ('VIEW_3D', 'IMAGE_EDITOR',
                                      'NODE_EDITOR'):
                        address = space.as_pointer()
                        if address in self.spaces:
                            value = self.spaces[address]
                        else:
                            value = {'enable': default_value}
                        d[address] = value
        self.spaces.clear()
        self.spaces.update(d)

    def updated_space(self, context, glsettings):
        """draw_callbackの頭で呼び出し、描画に必要な情報を更新する"""
        event = data.events[context.window.as_pointer()]
        region = context.region
        sx, sy = region.width, region.height
        ruler_settings = space_prop.get(context.space_data, 'region_ruler')

        if context.area.type == 'VIEW_3D':
            v3d = context.space_data
            rv3d = context.region_data
            vmat = rv3d.view_matrix
            view_location = get_view_location(context)
            override = {'grid_scale': 1.0,
                        'grid_subdivisions': 10,
                        'view_location': view_location}
            if ruler_settings.unit == 'none':
                override['system'] = 'NONE'
            elif ruler_settings.unit == 'metric':
                override['system'] = 'METRIC'
            elif ruler_settings.unit == 'imperial':
                override['system'] = 'IMPERIAL'
            unit_system = unitsystem.UnitSystem(context, override)
            unit_system_2d_x = unit_system_2d_y = None

            # View: top, right, left, ...
            if hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
                local_grid_rotation = v3d.local_grid_rotation
            else:
                local_grid_rotation = None
            view_type = vav.quat_to_axis_view(rv3d.view_rotation.inverted(),
                                              local_grid_rotation)

            # Region端の座標(BlenderUnit)を求める
            if (ruler_settings.origin_type == 'object' and
                    context.active_object):
                uv_co = context.active_object.matrix_world.to_translation()
                orig = vmat * uv_co
            elif ruler_settings.origin_type == 'cursor':
                orig = vmat * context.scene.cursor_location
            elif ruler_settings.origin_type == 'view':
                orig = Vector((0, 0, 0))
            elif ruler_settings.origin_type == 'custom':
                orig = vmat * ruler_settings.origin_location
            else:  # 'scene'
                if hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
                    orig = vmat * v3d.local_grid_location
                else:
                    orig = vmat * Vector((0, 0, 0))
            halfx = sx / 2 * unit_system.bupd
            halfy = sy / 2 * unit_system.bupd
            sign_x = -1 if view_type in ('left', 'back') else 1
            sign_y = -1 if view_type == 'bottom' else 1
            range_x = [sign_x * (-orig[0] - halfx),
                       sign_x * (-orig[0] + halfx)]
            range_y = [sign_y * (-orig[1] - halfy),
                       sign_y * (-orig[1] + halfy)]
        elif context.area.type == 'IMAGE_EDITOR':
            override = {'grid_scale': 1.0,
                        'grid_subdivisions': 10,
                        'system': 'NONE'}
            unit_system = unitsystem.UnitSystem(context, override)
            view_type = 'top'
            sign_x = sign_y = 1
            vmat = Matrix(glsettings.modelview_matrix).transposed()
            wmat = Matrix(glsettings.projection_matrix).transposed()
            pmat = wmat * vmat
            # X,Y毎にunit_systemを作成
            image_editor_unit = ruler_settings.image_editor_unit
            use_view2d = image_editor_unit == 'uv'
            unit_system_2d_x = unitsystem.UnitSystem(
                context, override, axis='x', use_view2d=use_view2d)
            unit_system_2d_y = unitsystem.UnitSystem(
                context, override, axis='y', use_view2d=use_view2d)
            image_sx, image_sy = unit_system.image_size
            if image_sx == 0:
                image_sx = 256
            if image_sy == 0:
                image_sy = 256
            if ruler_settings.image_editor_origin_type == 'view':
                f = sx * 0.5 * unit_system_2d_x.bupd
                range_x = [-f, f]
                f = sy * 0.5 * unit_system_2d_y.bupd
                range_y = [-f, f]
            else:
                # uv_co: min=(0, 0), max=(1, 1)
                if ruler_settings.image_editor_origin_type == 'cursor':
                    uv_co = context.space_data.cursor_location.copy()
                    uv_co[0] /= image_sx
                    uv_co[1] /= image_sy
                elif ruler_settings.image_editor_origin_type == 'uv':
                    uv_co = Vector((0, 0, 0))
                else:  # 'custom'
                    uv_co = ruler_settings.image_editor_origin_location
                    if ruler_settings.image_editor_unit == 'pixel':
                        uv_co = Vector((uv_co[0] / image_sx,
                                        uv_co[1] / image_sy))
                # X
                bupd = unit_system_2d_x.bupd
                orig = vav.project_v3(sx, sy, pmat, uv_co) * bupd
                range_x = [-orig[0], -orig[0] + sx * bupd]
                # Y
                bupd = unit_system_2d_y.bupd
                orig = vav.project_v3(sx, sy, pmat, uv_co) * bupd
                range_y = [-orig[1], -orig[1] + sy * bupd]
        else:
            override = {'grid_scale': 1.0, 'grid_subdivisions': 10,
                        'system': 'NONE'}
            use_view2d = ruler_settings.node_editor_unit != 'node'
            unit_system = unitsystem.UnitSystem(context, override,
                                                use_view2d=use_view2d)
            unit_system_2d_x = unit_system_2d_y = None
            view_type = 'top'
            sign_x = sign_y = 1
            vmat = Matrix(glsettings.modelview_matrix).transposed()
            wmat = Matrix(glsettings.projection_matrix).transposed()
            pmat = wmat * vmat
            bupd = unit_system.bupd
            co = Vector((0, 0, 0))
            orig = vav.project_v3(sx, sy, pmat, co) * bupd
            range_x = [-orig[0], -orig[0] + sx * bupd]
            orig = vav.project_v3(sx, sy, pmat, co) * bupd
            range_y = [-orig[1], -orig[1] + sy * bupd]

        # Mouse
        if event:
            mco = event.mco_region_mod
            if sx > 0 and sy > 0:
                x = (mco[0] / sx) * (range_x[1] - range_x[0]) + range_x[0]
                y = (mco[1] / sy) * (range_y[1] - range_y[0]) + range_y[0]
            else:
                x = y = 0.0
            mval = Vector((x, y))
            is_inside = 0 <= mco[0] < sx and 0 <= mco[1] < sy
        else:
            mval = Vector((0.0, 0.0))
            is_inside = False
        if self.active_window:
            if self.active_window != context.window.as_pointer():
                is_inside = False

        # 属性の更新
        self.unit_system = unit_system
        self.unit_system_2d_x = unit_system_2d_x
        self.unit_system_2d_y = unit_system_2d_y
        self.view_type = view_type
        self.sign_x = sign_x
        self.sign_y = sign_y
        self.range_x = range_x
        self.range_y = range_y
        # self.image_display_aspect = aspect
        self.mval = mval
        self.is_inside = is_inside
        if is_inside:
            self.last_region_id = region.id


data = Data()


###############################################################################
# Functions
###############################################################################
def is_modal_needed(context):
    """偽を返すならmodalオペレータを終了してもいい。
    """
    wm = context.window_manager
    prefs = RegionRulerPreferences.get_instance()
    if data.simple_measure or RegionRuler_PG._measure:
        return True
    if (prefs.draw_mouse_coordinates or prefs.use_simple_measure or
            prefs.draw_cross_cursor):
        return True
    return False


def redraw_regions(context, region_types={'WINDOW', 'UI'}, window=None):
    win = window or context.window
    for area in win.screen.areas:
        if area.type in ('VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR'):
            for region in area.regions:
                if not region_types or region.type in region_types:
                    region.tag_redraw()


def region_drawing_rectangle(context, area, region):
    """'WINDOW'の描画範囲を表すregion座標を返す。RegionOverlapが有効な場合の
    範囲は 'WINDOW' から 'TOOLS'('TOOL_PROPS'), 'UI' を除外したものになる。
    :return (xmin, ymin, xmax, ymax)
    :rtype (int, int, int, int)
    """
    xmax = region.width - 1
    ymin = 0
    ymax = region.height - 1

    # right scroll bar
    if context.area.type == 'NODE_EDITOR':
        # V2D_SCROLLER_HANDLE_SIZE 等を参照。+1は誤差修正用
        xmax -= int(get_widget_unit(context) * 0.8) + 1

    # render info
    has_render_info = False
    if context.area.type == 'IMAGE_EDITOR':
        image = context.area.spaces.active.image
        if image and image.type == 'RENDER_RESULT':
            has_render_info = True
    elif context.area.type == 'VIEW_3D':
        if context.space_data.viewport_shade == 'RENDERED':
            has_render_info = True
    if has_render_info:
        dpi = context.user_preferences.system.dpi
        ymax -= get_widget_unit(context)

    if not context.user_preferences.system.use_region_overlap:
        return 0, ymin, xmax, ymax

    # Regionが非表示ならidが0。
    # その際、通常はwidth若しくはheightが1になっている。
    # TOOLSが非表示なのにTOOL_PROPSのみ表示される事は無い
    window = tools = tool_props = ui = None
    for ar in area.regions:
        if ar.id != 0:
            if ar.type == 'WINDOW':
                window = ar
            elif ar.type == 'TOOLS':
                tools = ar
            elif ar.type == 'TOOL_PROPS':
                tool_props = ar
            elif ar.type == 'UI':
                ui = ar

    xmin = region.x
    xmax = xmin + region.width - 1
    left_width = right_width = 0
    if tools and ui:
        r1, r2 = sorted([tools, ui], key=lambda ar: ar.x)
        if r1.x == area.x:
            # 両方左
            if r2.x == r1.x + r1.width:
                left_width = r1.width + r2.width
            # 片方ずつ
            else:
                left_width = r1.width
                right_width = r2.width
        # 両方右
        else:
            right_width = r1.width + r2.width
    elif tools:
        if tools.x == area.x:
            left_width = tools.width
        else:
            right_width = tools.width
    elif ui:
        if ui.x == area.x:
            left_width = ui.width
        else:
            right_width = ui.width

    xmin = max(xmin, area.x + left_width) - region.x
    xmax = min(xmax, area.x + area.width - right_width - 1) - region.x
    return xmin, ymin, xmax, ymax


###############################################################################
# Draw font, Box
###############################################################################
def draw_font(font_id, text, outline_color=None):
    """outline_colorを指定したらその色で縁取りする"""
    current_color = vagl.Buffer('double', 4, bgl.GL_CURRENT_COLOR)
    if outline_color:
        color = list(outline_color)
        if len(color) == 3:
            color += [1.0]
        if color[3] != 0.0:
            if OUTLINE_RADIUS == 5:
                color[3] /= 8 / 60  # blf_texture5_draw()より
            elif OUTLINE_RADIUS == 3:
                color[3] /= 4 / 16  # blf_texture3_draw()より
            bgl.glColor4f(*color)
            blf.blur(font_id, OUTLINE_RADIUS)
            vagl.blf_draw(font_id, text)
            blf.blur(font_id, 0)
            bgl.glColor4f(*current_color)

    vagl.blf_draw(font_id, text)


def draw_font_context(context, font_id, text, outline=False,
                      outline_color=None):
    area = context.area
    enable = (area.type == 'IMAGE_EDITOR' and IMAGE_EDITOR_NUMBER_OUTLINE or
              area.type == 'NODE_EDITOR' and NODE_EDITOR_NUMBER_OUTLINE or
              area.type == 'VIEW_3D' and VIEW_3D_NUMBER_OUTLINE)
    if enable and outline and outline_color:
        draw_font(font_id, text, outline_color)
    else:
        draw_font(font_id, text)



def get_background_color(context, y=None):
    """Region座標Yのbackgroundの色を返す
    :param y: region座標
    :return: (R, G, B)
    :rtype: Color
    """
    theme = context.user_preferences.themes['Default']
    if context.area.type == 'VIEW_3D':
        gradients = theme.view_3d.space.gradients
        col_high = gradients.high_gradient
        col_low = gradients.gradient
        if gradients.show_grad and y is not None:
            f = y / context.region.height
            return col_low * (1 - f) + col_high * f
        else:
            return col_high
    else:
        return theme.image_editor.space.back


def draw_line_loop(context, coords, line=False, fill=False,
                   line_color=None, fill_color=None, fill_back_color=False):
    current_color = vagl.Buffer('double', 4, bgl.GL_CURRENT_COLOR)

    if fill:
        if fill_color:
            if len(fill_color) == 3:
                bgl.glColor3f(*fill_color)
            else:
                bgl.glColor4f(*fill_color)
        bgl.glBegin(bgl.GL_QUADS)
        for co in coords:
            if fill_back_color:
                col = get_background_color(context, co[1])
                bgl.glColor3f(*col)
            bgl.glVertex2f(*co)
        bgl.glEnd()
    if line:
        if line_color:
            if len(line_color) == 3:
                bgl.glColor3f(*line_color)
            else:
                bgl.glColor4f(*line_color)
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for co in coords:
            bgl.glVertex2f(*co)
        bgl.glEnd()

    bgl.glColor4f(*current_color)


def draw_box(context, box, line=False, fill=False,
             line_color=None, fill_color=None, fill_back_color=False,
             angle=0.0):
    x, y, w, h = box
    coords = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    if angle != 0.0:
        m = Matrix.Rotation(angle, 2)
        v = Vector(coords[0])
        coords = [m * (Vector(co) - v) + v for co in coords]
    draw_line_loop(context, coords, line, fill, line_color, fill_color,
                   fill_back_color)


def draw_angle_box(context, box, line=False, fill=False,
                   line_color=None, fill_color=None, fill_back_color=False,
                   angle=0.0):
    """ ___w___
       /       | h
       \_______|
       /
    (x, y)
    """
    x, y, w, h = box
    coords = ((x, y), (x + w, y), (x + w, y + h), (x, y + h),
              (x - 4, y + h / 2))
    if angle != 0.0:
        m = Matrix.Rotation(angle, 2)
        v = Vector(coords[0])
        coords = [m * (Vector(co) - v) + v for co in coords]
    draw_line_loop(context, coords, line, fill, line_color, fill_color,
                   fill_back_color)


###############################################################################
# Draw
###############################################################################
def rotated_bbox(box_width, box_height, angle):
    """回転されたbounding boxの幅と高さを求める"""
    mat = Matrix.Rotation(angle, 2)
    hw = box_width / 2
    hh = box_height / 2
    vecs = [mat * Vector((x, y)) for x, y in
            ((hw, hh), (hw, -hh), (-hw, hh), (-hw, -hh))]
    width = max((abs(v[0]) for v in vecs)) * 2
    height = max((abs(v[1]) for v in vecs)) * 2
    return width, height


def get_line_type(prop, cnt, magnification):
    ssmain, sseven, ssodd = prop.scale_size
    sseven = min(ssmain, sseven)
    ssodd = min(ssmain, ssodd)
    if cnt % magnification == 0:
        line_width = 3
        scale_size = ssmain
    else:
        line_width = 1
        if cnt % 2 == 0:
            scale_size = sseven
        else:
            scale_size = ssodd
    return scale_size, line_width


def modify_imperial_symbol(symbol):
    if symbol in ('fur',):
        symbol = 'mi'
    elif symbol in ('ch', 'yd'):
        symbol = "'"
    elif symbol in ('thou',):
        symbol = '"'
    return symbol


def calc_relative_magnification(unit_system):
    """IMPERIALの場合、一つ大きい単位のscalarを現在の単位のscalarで割った数、
    METRICとNONEは10を返す。
    """
    if unit_system == 'IMPERIAL':
        i = unit_system.units.index(unit_system.unit)
        if i == 0:  # mile
            magnification = 10
        else:
            unit_large = unit_system.imperial_units[i - 1]
            magnification = round(unit_large.scalar / unit_system.unit)
    else:
        magnification = 10
    return magnification


def scale_label_interval(context, unit_system, cnt):
    prefs = RegionRulerPreferences.get_instance()
    magnification = calc_relative_magnification(unit_system)
    interval = 0
    if magnification and cnt % magnification == 0:
        interval = 10
    elif cnt % 5 == 0 and unit_system.system in ('NONE', 'METRIC'):
        if unit_system.dpg >= prefs.number_min_px[0]:
            interval = 5
    elif unit_system.dpg >= prefs.number_min_px[1]:
        interval = 1
        if unit_system.system == 'NONE':
            interval = 1
        elif unit_system.dpg >= prefs.number_min_px[1] * 2:
            interval = 1

    return interval


def make_scale_label(context, unit_system, cnt):
    """
    :param unit_system:
    :type unit_system: unitsystem.UnitSystem
    :param cnt:
    :type cnt: int
    :rtype: str
    """

    units = unit_system.units
    unit = unit_system.unit

    if cnt == 0 and unit_system.system != 'NONE':
        return '0' + units.next_basic(unit.symbol)

    interval = scale_label_interval(context, unit_system, cnt)

    if interval == 0:
        return ''

    if unit_system.system == 'NONE':
        value = unit_system.bupg * cnt
        e = max(0, -int(math.log10(unit_system.bupg)))
        text = '{0:.{1}f}'.format(value, e)
    else:
        value = Decimal(unit.scalar) * cnt
        value /= Decimal(str(unit_system.scale_length)).normalize()
        start = end = ''
        if unit_system.use_separate:
            end = unit.symbol
        else:
            if unit_system.system == 'IMPERIAL':
                start = modify_imperial_symbol(unit.symbol)
        exp = unit.symbol
        text = unit_system.num_to_unit(
            value, start=start, end=end, verbose=(False, True, True),
            rounding_exp=exp)

    return text


def clip_start_end(context, start, end, offset, negative):
    region = context.region
    rv3d = context.region_data
    sign = -1 if negative else 1
    sx, sy = region.width, region.height
    q1 = Vector((-1, -1))
    q2 = Vector((sx + 1, -1))
    q3 = Vector((sx + 1, sy + 1))
    q4 = Vector((-1, sy + 1))
    unit_system = data.unit_system

    is_world_coords = len(start) == 3
    line = (end - start).normalized()

    invalid_result = None, None, 0.0

    # World coors
    if is_world_coords:
        start_rco_no_clip = vav.project(region, rv3d, start).to_2d()
        end_rco_no_clip = vav.project(region, rv3d, end).to_2d()
        result = vam.intersect_line_quad_2d(start_rco_no_clip, end_rco_no_clip,
                                            q1, q2, q3, q4, True)
        if result is None:
            return invalid_result
        start_rco, end_rco = result
        if start_rco == end_rco:
            return invalid_result

        # startとoffsetの修正
        if start_rco != start_rco_no_clip:
            p1 = Vector((start_rco[0], start_rco[1], 0.5))
            p2 = Vector((start_rco[0], start_rco[1], 1.0))
            v1 = vav.unproject(region, rv3d, p1)
            v2 = vav.unproject(region, rv3d, p2)
            v3, v4 = geom.intersect_line_line(v1, v2, start, end)
            v = (v3 + v4) / 2
            offset += sign * (start - v).length
            start = v

        # endの修正
        if end_rco != end_rco_no_clip:
            p1 = Vector((end_rco[0], end_rco[1], 0.5))
            p2 = Vector((end_rco[0], end_rco[1], 1.0))
            v1 = vav.unproject(region, rv3d, p1)
            v2 = vav.unproject(region, rv3d, p2)
            v3, v4 = geom.intersect_line_line(v1, v2, start, end)
            end = (v3 + v4) / 2

    # Region coords
    else:
        result = vam.intersect_line_quad_2d(start, end, q1, q2, q3, q4, True)
        if result is None:
            return invalid_result
        start_rco, end_rco = result
        if start_rco == end_rco:
            return invalid_result
        dot_ofs = line.dot(start_rco - start)
        offset += sign * dot_ofs * unit_system.bupd
        start = start_rco
        end = end_rco

    return start, end, offset


def generate_scale_points(context, start, end, offset, negative):
    """目盛のカウントとregion座標を返すジェネレータ"""
    region = context.region
    rv3d = context.region_data
    unit_system = data.unit_system

    sign = -1 if negative else 1

    count, val = divmod(offset, unit_system.bupg)
    count = int(count)
    if val == 0.0:
        scale_start = start.copy()
    else:
        sign = -1 if negative else 1
        if sign == 1:
            count += 1
        count_offset = count * unit_system.bupg
        line = (end - start).normalized()
        if len(start) == 3:
            v = sign * (count_offset - offset) * line
        else:
            v = sign * (count_offset - offset) * unit_system.dpbu * line
        scale_start = start + v

    if (scale_start - start).length > (end - start).length:
        return

    if len(start) == 3:
        offset_vec = (end - start).normalized() * unit_system.bupg
        num = int((end - scale_start).length / unit_system.bupg) + 1
        for _ in range(num):
            yield count, vav.project(region, rv3d, scale_start).to_2d()
            count += sign
            scale_start += offset_vec
    else:
        offset_vec = (end - start).normalized() * unit_system.dpg
        num = int((end - scale_start).length * unit_system.gpd) + 1
        for _ in range(num):
            yield count, scale_start.copy()
            count += sign
            scale_start += offset_vec


def draw_free_ruler(context, prefs, start, end, offset,
                    negative=False, line_feed=False,
                    rotate_text=False,
                    number_upper_side=False, double_side_scale=False,
                    base_line=True,
                    draw_zero={'marker', 'number', 'scale'}):
    """
    :param start: 開始点の座標。
                  Region座標なら二次元、World座標なら三次元を用いる
    :type start: Vector
    :param end: 終了点の座標。
                Region座標なら二次元、World座標なら三次元を用いる
    :type end: Vector
    :param offset: 開始点の値。単位はblenderUnit
    :type offset: float
    :param negative: 真ならstart->endへ進む時に数値が減少する
    :type nagative: bool
    :param line_feed: 数値描画の際、単位が切り替わる毎に改行する。
    :type line_feed: bool
    :param rotate_text: 数値を回転する
    :type rotate_text: bool
    :param number_upper_side: 目盛・数値の描画方向。
    :type number_upper_side: bool
    :param double_side_scale: 目盛をstart->endの線分の両側に描画する。
    :type double_side_scale: bool
    :param base_line: start->endの線分を描画する
    :type base_line: bool
    :param draw_zero: 0位置に描画する要素。
    :type draw_zero: set
    """

    region = context.region
    rv3d = context.region_data
    unit_system = data.unit_system

    # clip
    start, end, offset = clip_start_end(context, start, end, offset, negative)
    if start is None:
        return

    if len(start) == 3:
        start_rco = vav.project(region, rv3d, start).to_2d()
        end_rco = vav.project(region, rv3d, end).to_2d()
    else:
        start_rco = start.copy()
        end_rco = end.copy()
    hvec = (end_rco - start_rco).normalized()
    if number_upper_side:
        vvec = Vector((-hvec[1], hvec[0]))
    else:
        vvec = Vector((hvec[1], -hvec[0]))
    angle = math.atan2(hvec[1], hvec[0])

    # 目盛りの大きさ
    ssmain, sseven, ssodd = prefs.scale_size  # even:偶数
    sseven = min(ssmain, sseven)
    ssodd = min(ssmain, ssodd)

    # Font
    font = prefs.font
    blf.size(font.id, font.size, context.user_preferences.system.dpi)
    _, th = blf.dimensions(font.id, string.digits)
    margin = font.margin

    magnification = calc_relative_magnification(unit_system)

    lines = []
    lines_bold = []
    numbers = []
    numbers_fill = []
    triangles = []

    for count, p in generate_scale_points(
            context, start, end, offset, negative):
        # Scale
        if not (count == 0 and 'scale' not in draw_zero):
            if count % magnification == 0:
                scale_size = ssmain
                line_width = 3
            else:
                scale_size = sseven if count % 2 == 0 else ssodd
                line_width = 1

            # 5-Triangles
            if count % 5 == 0 and count % 10 != 0:
                if unit_system.system != 'IMPERIAL':
                    if ssmain >= 3:
                        v1 = p + vvec * max(0, (ssodd - 3))  # top vertex
                        v2 = vvec * 3
                        v3 = hvec * 2
                        triangles.append((v1 + v2 - v3, v1 + v2 + v3, v1))
                        scale_size = max(0, scale_size - 3)

            if double_side_scale:
                val = (p + vvec * scale_size, p - vvec * scale_size)
            else:
                val = (p, p + vvec * scale_size)
            if line_width == 1:
                lines.append(val)
            else:
                lines_bold.append(val)

        # 数値。複数行の場合は右揃え
        if count == 0 and 'number' not in draw_zero:
            text = ''
        else:
            text = make_scale_label(context, unit_system, count)
        if line_feed:
            text_lines = text.split(' ')
            widths = [blf.dimensions(font.id, t)[0] for t in text_lines]
        else:
            text_lines = [text]
            widths = [blf.dimensions(font.id, text)[0]]
        box_width = max(widths) + margin * 2
        box_height = len(widths) * th + (len(widths) + 1) * margin
        if rotate_text:
            vx = hvec
            vy = -vvec
            h = box_height
        else:
            vx = Vector((1, 0))
            vy = Vector((0, 1))
            rbox_width, h = rotated_bbox(box_width, box_height, -angle)
        box_center = p + (ssmain + h / 2) * vvec
        box_loc = box_center - box_width / 2 * vx - box_height / 2 * vy
        if text:
            for i in range(len(text_lines)):
                txt = text_lines[-i - 1]
                tw = widths[-i - 1]
                fx = box_width - margin - tw
                fy = margin + (th + margin) * i
                v = box_loc + vx * fx + vy * fy
                numbers.append((v[0], v[1], txt))
                v -= (vx + vy) * margin
                w = tw + margin * 2
                h = th + margin * 2
                numbers_fill.append((v[0], v[1], w, h))

        # Origin Triangles
        if count == 0:
            if 'marker' in draw_zero:
                if rotate_text:
                    w = box_width / 2
                else:
                    w = rbox_width / 2
                triangles.append((box_center - hvec * w - vvec * (th / 2),
                                  box_center - hvec * (w + 5),
                                  box_center - hvec * w + vvec * (th / 2)))
                triangles.append((box_center + hvec * w - vvec * (th / 2),
                                  box_center + hvec * w + vvec * (th / 2),
                                  box_center + hvec * (w + 5)))

    # 描画
    if base_line:
        bgl.glColor4f(*(list(prefs.color.line) + [0.5]))
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(*start_rco)
        bgl.glVertex2f(*end_rco)
        bgl.glEnd()

    bgl.glColor3f(*prefs.color.line)

    # 目盛
    for line_width, lines in ((1.0, lines), (3.0, lines_bold)):
        bgl.glLineWidth(line_width)
        bgl.glBegin(bgl.GL_LINES)
        for v1, v2 in lines:
            bgl.glVertex2f(*v1)
            bgl.glVertex2f(*v2)
        bgl.glEnd()
    bgl.glLineWidth(1.0)

    # 三角形
    for p1, p2, p3 in triangles:
        vagl.draw_triangle(p1, p2, p3, poly=True)
        vagl.draw_triangle(p1, p2, p3)

    # 数値
    if rotate_text:
        blf.enable(prefs.font.id, blf.ROTATION)
        blf.rotation(prefs.font.id, 0)
        blf.position(prefs.font.id, region.width + 1, region.height + 1, 0)
        vagl.blf_draw(prefs.font.id, 'test.0123456789')
        blf.rotation(prefs.font.id, angle)
        buf_mag = vagl.Buffer('int', 1)
        buf_min = vagl.Buffer('int', 1)
        bgl.glGetTexParameteriv(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER,
                                buf_mag)
        bgl.glGetTexParameteriv(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER,
                                buf_min)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER,
                            bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER,
                            bgl.GL_LINEAR)
    bgl.glColor3f(*prefs.color.number)
    for number_data, fill_data in zip(numbers, numbers_fill):
        xmin, ymin, w, h = fill_data
        ang = angle if rotate_text else 0.0
        x, y, text = number_data
        blf.position(prefs.font.id, x, y, 0)
        draw_font_context(context, prefs.font.id, text, outline=True,
                          outline_color=prefs.color.number_outline)
        if not prefs.use_fill:
            bgl.glColorMask(0, 0, 0, 0)
            draw_box(context, (xmin, ymin, w, h), fill=True, angle=ang)
            bgl.glColorMask(1, 1, 1, 1)

    if rotate_text:
        blf.rotation(prefs.font.id, 0)
        blf.disable(prefs.font.id, blf.ROTATION)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER,
                            buf_mag[0])
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER,
                            buf_min[0])


def viewport_name(context):
    v3d = context.space_data
    rv3d = context.region_data

    if rv3d.view_perspective == 'CAMERA':
        if v3d.camera and v3d.camera.type == 'CAMERA':
            cam = v3d.camera.data
            if cam.type == 'ORTHO':
                name = 'Camera Ortho'
            elif cam.type == 'PERSP':
                name = 'Camera Persp'
            else:
                name = 'Camera Pano'
        else:
            name = 'Object as Camera'
    elif data.view_type == 'user':
        if rv3d.view_perspective == 'ORTHO':
            name = 'User Ortho'
        else:
            name = 'User Persp'
    else:
        name = data.view_type.title()
        if rv3d.view_perspective == 'ORTHO':
            name += ' Ortho'
        else:
            name += ' Persp'

    if v3d.local_view:
        name += ' (Local)'
    if hasattr(v3d, 'use_local_grid') and v3d.use_local_grid:
        name += ' (LocalGrid)'

    return name


def view3d_upper_left_text_rect(context):
    """View3D左上の文字の範囲を返す。
    blf.size()を呼んで文字サイズを変えるので注意。
    @ view3d_main_area_draw_info() 参照
    :return: region coords [xmin, xmax, ymin, ymax]
    :rtype: [int, int, int, int]
    """
    if context.area.type != 'VIEW_3D':
        return [0, 0, 0, 0]

    region = context.region
    user_pref = context.user_preferences
    if (user_pref.view.show_playback_fps and
            context.screen. is_animation_playing):
        text = 'fps: 000.00'  # 最大長
    elif user_pref.view.show_view_name:
        text = viewport_name(context)
    else:
        return [0, 0, 0, 0]

    dpi = user_pref.system.dpi
    # #define UI_UNIT_X               ((void)0, U.widget_unit)
    # #define UI_UNIT_Y               ((void)0, U.widget_unit)
    # blender/blenkernel/intern/blender.c:507:
    #     U.widget_unit = (U.pixelsize * U.dpi * 20 + 36) / 72;
    widget_unit = get_widget_unit(context)
    # 文字描画位置: [rect.xmin + widget_unit, rect.xmax - widget_unit]

    font_path = context.user_preferences.system.font_path_ui
    font_id = 0
    if font_path:
        try:
            font_id = blf.load(font_path)
        except:
            pass
    blf.size(font_id, 11, dpi)
    w, h = blf.dimensions(font_id, text)
    return [widget_unit, int(widget_unit + w),
            region.height - 1 - widget_unit,
            region.height - 1 - widget_unit + h]


def set_model_view_z(z):
    """
    :param z: 有効範囲は -100 〜 +100
    :type z: int | float
    """
    bgl.glMatrixMode(bgl.GL_MODELVIEW)
    bgl.glLoadIdentity()
    bgl.glTranslated(0.0, 0.0, z)


def draw_mask(context):
    set_model_view_z(50)

    name_rect = view3d_upper_left_text_rect(context)
    margin = 5
    bgl.glColorMask(0, 0, 0, 0)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glVertex2f(name_rect[0] - margin, name_rect[2] - margin)
    bgl.glVertex2f(name_rect[1] + margin, name_rect[2] - margin)
    bgl.glVertex2f(name_rect[1] + margin, name_rect[3] + margin)
    bgl.glVertex2f(name_rect[0] - margin, name_rect[3] + margin)
    bgl.glEnd()
    bgl.glColorMask(1, 1, 1, 1)

    set_model_view_z(0)


def draw_region_rulers(context):
    prefs = RegionRulerPreferences.get_instance()
    area = context.area
    region = context.region
    xmin, ymin, xmax, ymax = region_drawing_rectangle(context, area, region)
    scissor_is_enabled = vagl.Buffer('bool', 0, bgl.GL_SCISSOR_TEST)
    scissor_box = vagl.Buffer('int', 4, bgl.GL_SCISSOR_BOX)
    bgl.glEnable(bgl.GL_SCISSOR_TEST)

    # X-Axis
    if context.area.type == 'IMAGE_EDITOR':
        data.unit_system, data.unit_system_2d_x = \
            data.unit_system_2d_x, data.unit_system
    bgl.glScissor(region.x + xmin, region.y,
                  max(0, (xmax - xmin + 1)), ymax - ymin + 1)
    range_x = data.range_x
    draw_free_ruler(context, prefs, Vector((0, ymax)), Vector((xmax, ymax)),
                    range_x[0], range_x[0] > range_x[1],
                    line_feed=False, rotate_text=False,
                    number_upper_side=False, base_line=False)

    # Y-Axis
    if context.area.type == 'IMAGE_EDITOR':
        data.unit_system, data.unit_system_2d_y = \
            data.unit_system_2d_y, data.unit_system
    bgl.glScissor(region.x + xmin, region.y,
                  xmax - xmin + 1, ymax - ymin + 1)
    range_y = data.range_y
    draw_free_ruler(context, prefs, Vector((xmax, 0)), Vector((xmax, ymax)),
                    range_y[0], range_y[0] > range_y[1],
                    line_feed=True, rotate_text=False,
                    number_upper_side=True, base_line=False)

    # 復帰
    if context.area.type == 'IMAGE_EDITOR':
        data.unit_system, data.unit_system_2d_x, data.unit_system_2d_y = \
            data.unit_system_2d_x, data.unit_system_2d_y, data.unit_system

    if not scissor_is_enabled:
        bgl.glDisable(bgl.GL_SCISSOR_TEST)
    bgl.glScissor(*scissor_box)  # [region.x, region.y, sx, sy]


def draw_unit_box(context, use_fill):
    """右上。
    render情報が表示されている場合でも、propertiesパネル表示用の＋マークと
    重なる事を避ける為表示位置は変えない)
    """
    prefs = RegionRulerPreferences.get_instance()
    if context.area.type == 'VIEW_3D':
        unit_system = data.unit_system
        if unit_system.system == 'NONE':
            text = '{:g}'.format(unit_system.bupg)
        else:
            unit = unit_system.unit
            if unit_system.system == 'METRIC':
                if unit.symbol == 'hm':
                    text = '100m'
                elif unit.symbol == 'dam':
                    text = '10m'
                elif unit.symbol == 'dm':
                    text = '10cm'
                else:
                    text = '1' + unit.symbol
            else:
                if unit.symbol in ('\'', '"'):
                    text = '1' + unit.symbol_alt  # feetとinchが見にくいため
                else:
                    text = '1' + unit.symbol
    elif context.area.type == 'IMAGE_EDITOR':
        fx = data.unit_system_2d_x.bupg
        fy = data.unit_system_2d_y.bupg
        if fx == fy:
            text = '{:g}'.format(fx)
        else:
            text = '{:g}, {:g}'.format(fx, fy)
    else:
        f = data.unit_system.bupg
        text = '{:g}'.format(f)

    area = context.area
    region = context.region
    sx, sy = region.width, region.height
    xmin, ymin, xmax, ymax = region_drawing_rectangle(context, area, region)
    font = prefs.font
    blf.size(font.id, font.size, context.user_preferences.system.dpi)
    _, text_height = blf.dimensions(font.id, string.digits)
    tw, _ = blf.dimensions(font.id, text)
    w = tw + font.margin * 2 + 4  # 見にくいのでちょっと変更
    h = text_height + font.margin * 2
    box = [xmax - w, sy - h - 1, w, h]

    set_model_view_z(20)

    # 背景と枠線
    draw_box(context, box, line=True, fill=use_fill,
             line_color=prefs.color.line, fill_back_color=True)

    # 数値
    bgl.glColor3f(*prefs.color.number)
    blf.position(
        prefs.font.id, xmax - tw - font.margin - 2,
        sy - text_height - font.margin, 0)
    draw_font_context(context, font.id, text, outline=not use_fill,
                      outline_color=prefs.color.number_outline)

    # ステンシル塗りつぶし
    if not use_fill:
        bgl.glColorMask(0, 0, 0, 0)
        draw_box(context, box, fill=True)
        bgl.glColorMask(1, 1, 1, 1)

    set_model_view_z(0)


def draw_measure(context, event):
    """ポイントが空の場合、深度は3DカーソルかViewLocationを使い、
    ポイントの続きの場合はその深度に合わせる。"""
    ruler_settings = space_prop.get(context.space_data, 'region_ruler')
    running_measure = ruler_settings.measure
    prefs = RegionRulerPreferences.get_instance()
    region = context.region
    if not data.is_inside:
        # if data.last_region_id != region.id:
        return
    sx, sy = region.width, region.height
    rv3d = context.region_data
    if not rv3d:
        return

    if not (data.simple_measure or running_measure):
        return

    pmat = rv3d.perspective_matrix
    pimat = pmat.inverted()
    unit_system = data.unit_system
    mco = Vector(event.mco_region_mod)
    ssmain = prefs.scale_size[0]
    font = prefs.font
    margin = font.margin

    blf.size(font.id, font.size, context.user_preferences.system.dpi)
    _, th = blf.dimensions(font.id, string.digits)

    if ruler_settings.view_depth == 'cursor':
        depth_location = context.scene.cursor_location
    else:
        depth_location = rv3d.view_location

    use_fill = prefs.use_fill

    def draw_box_text(box, text):
        draw_box(context, box, line=True, fill=use_fill,
                 line_color=prefs.color.line, fill_back_color=True)
        bgl.glColor3f(*prefs.color.number)
        blf.position(font.id,
                     box[0] + margin, box[1] + margin, 0)
        draw_font_context(context, font.id, text, outline=not use_fill,
                          outline_color=prefs.color.number_outline)
        if not use_fill:
            bgl.glColorMask(0, 0, 0, 0)
            draw_box(context, box, line=True, fill=True,
                     line_color=prefs.color.line, fill_back_color=True)
            bgl.glColorMask(1, 1, 1, 1)

    def draw_angle_box_text(box, text):
        draw_angle_box(context, box, line=True, fill=use_fill,
                       line_color=prefs.color.line, fill_back_color=True)
        bgl.glColor3f(*prefs.color.number)
        blf.position(font.id, box[0] + margin, box[1] + margin, 0)
        draw_font_context(context, font.id, text, outline=not use_fill,
                          outline_color=prefs.color.number_outline)
        if not use_fill:
            bgl.glColorMask(0, 0, 0, 0)
            draw_box(context, box, line=True, fill=True,
                     line_color=prefs.color.line, fill_back_color=True)
            bgl.glColorMask(1, 1, 1, 1)

    # Calc coords ---------------------------------------------------------
    if data.measure_points:
        coordsW = data.measure_points[:]
        coordsR = [vav.project_v3(sx, sy, pmat, v).to_2d()
                   for v in data.measure_points]
        coordsW.append(vav.unproject_v3(sx, sy, pimat, mco,
                                        coordsW[-1], True))
        coordsR.append(mco)
    else:
        coordsW = [vav.unproject_v3(sx, sy, pimat, mco,
                                    depth_location, True)]
        coordsR = [mco]

    def draw_numbers():
        if len(coordsR) > 1:
            v1W = coordsW[-2]
            v2W = coordsW[-1]
            v1R = coordsR[-2]
            v2R = coordsR[-1]  # == mco

            # Width Box -------------------------------------------------------
            value = (v2R[0] - v1R[0]) * unit_system.bupd
            text = make_mouse_coordinate_label(context, unit_system, value)
            tw, _ = blf.dimensions(font.id, text)
            if v2R[0] >= v1R[0]:
                x = mco[0] - tw - margin * 2 - 20
            else:
                x = mco[0] + 20
            y = data.mcbox_x[1]
            wbox = (x, y - th - margin * 2,
                       tw + margin * 2, th + margin * 2)
            draw_box_text(wbox, text)

            # Height Box ------------------------------------------------------
            value = (v2R[1] - v1R[1]) * unit_system.bupd
            text = make_mouse_coordinate_label(context, unit_system, value)
            tw, _ = blf.dimensions(font.id, text)
            if v2R[1] >= v1R[1]:
                y = mco[1] - th - margin * 2 - 20
            else:
                y = mco[1] + 20
            hbox = (data.mcbox_y[0] - tw - margin * 2, y,
                    tw + font.margin * 2, th + margin * 2)
            draw_box_text(hbox, text)

    def draw_mouse_numbers():
        # Around Mouse ----------------------------------------------------
        if len(coordsR) > 1:
            v1W = coordsW[-2]
            v2W = coordsW[-1]
            v1R = coordsR[-2]
            v2R = coordsR[-1]  # == mco

            ofs = 20

            # length
            text = make_mouse_coordinate_label(
                context, unit_system, (v1W - v2W).length)
            tw, _ = blf.dimensions(font.id, text)
            box = [mco[0] + 1.6 * ofs, mco[1] - th - ofs,
                   tw + margin * 2, th + margin * 2]
            draw_box_text(box, text)

            # angle
            v = v2R - v1R
            angle = math.atan2(v[1], v[0])
            if context.scene.unit_settings.system_rotation == 'RADIANS':
                text = "{0:.2f}".format(angle)
            else:
                text = "{0:.2f}".format(math.degrees(angle))
            tw, _ = blf.dimensions(font.id, text)
            box[1] -= th + 10
            box[2] = tw + margin * 2
            draw_angle_box_text(box, text)

        # Basic Cross Scale ---------------------------------------------------
        else:
            vecs = [((sx, mco[1]), False, False),
                    ((0, mco[1]), True, True),
                    ((mco[0], sy), False, True),
                    ((mco[0], 0), True, False)]
            for v, negative, number_upper_side in vecs:
                draw_free_ruler(context, prefs, mco, Vector(v), 0.0,
                                negative=negative, line_feed=True,
                                number_upper_side=number_upper_side,
                                double_side_scale=True,
                                base_line=True,
                                draw_zero=set())

    def draw_scale_numbers():
        bgl.glDepthFunc(bgl.GL_LESS)
        # 後の方が前面に描画される
        for i in reversed(range(len(coordsR) - 1)):
            v1R = coordsR[i]
            v2R = coordsR[i + 1]
            v1W = coordsW[i]
            v2W = coordsW[i + 1]

            # Length ----------------------------------------------------------
            text = make_mouse_coordinate_label(
                context, unit_system, (v1W - v2W).length)
            tw, _ = blf.dimensions(font.id, text)
            _width, height = rotated_bbox(tw + margin * 2, th + margin * 2,
                                         - math.atan2(*(v2R - v1R).yx))
            hvec = (v2R - v1R).normalized()
            vvec = Matrix.Rotation(-math.pi / 2, 2) * hvec
            v = (v2R + v1R) / 2 + (ssmain + height / 2) * vvec
            box = (v[0] - tw / 2 - margin,
                   v[1] - th / 2 - margin,
                   tw + margin * 2, th + margin * 2)
            draw_box_text(box, text)

            # Angle -----------------------------------------------------------
            if i != 0:
                v0W = coordsW[i - 1]
                v0R = coordsR[i - 1]
                angle = (v0W - v1W).angle(v2W - v1W, 0.0)
                v = ((v0R - v1R).normalized() +
                     (v2R - v1R).normalized()).normalized()
                if v.length == 0.0:
                    v = Vector((0, 1))
                v = v1R + v * 30
                if context.scene.unit_settings.system_rotation == 'RADIANS':
                    text = "{0:.2f}".format(angle)
                else:
                    text = "{0:.2f}".format(math.degrees(angle))
                tw, _ = blf.dimensions(font.id, text)
                box = (v[0] - tw / 2 - margin,
                       v[1] - th / 2 - margin,
                       tw + margin * 2, th + margin * 2)
                draw_angle_box_text(box, text)
        bgl.glDepthFunc(bgl.GL_LEQUAL)

    def draw_scales():
        for i in reversed(range(len(coordsR) - 1)):
            v1R = coordsR[i]
            v2R = coordsR[i + 1]
            v1W = coordsW[i]
            v2W = coordsW[i + 1]

            if i == len(coordsR) - 2:
                # Cross Scale
                vR = v2R - v1R
                if vR.length >= 1.0:
                    angle = math.atan2(vR[1], vR[0])
                else:
                    angle = 0.0
                mat = Matrix.Rotation(angle, 2)
                l = vR.length + 3000
                vecs = [((l, 0), False, False),
                        ((-l, 0), True, True),
                        ((0, l), False, True),
                        ((0, -l), True, False)]
                if 'view_location' in unit_system.override:
                    view_loc = unit_system.override['view_location']
                else:
                    view_loc = None
                unit_system.view_location = v1W
                unit_system.update(context)
                for v, negative, number_upper_side in vecs:
                    vec = mat * Vector(v) + v1R
                    draw_free_ruler(context, prefs, v1R, vec, 0.0,
                                    negative=negative, line_feed=True,
                                    number_upper_side=number_upper_side,
                                    double_side_scale=True, draw_zero=set())
                if view_loc is not None:
                    unit_system.view_location = view_loc
                unit_system.update(context)
            else:
                # Single Scale
                draw_free_ruler(context, prefs, v1W, v2W, 0.0,
                                negative=False, line_feed=True,
                                number_upper_side=False,
                                double_side_scale=True,
                                base_line=True,
                                draw_zero={'scale'})

    def draw_backgrount_circle():
        bgl.glColor4f(*(list(prefs.color.line) + [0.5]))
        bgl.glLineWidth(1)

        # Background circle ---------------------------------------------------
        if data.measure_points:
            centerR = coordsR[-2]

            if 0 <= centerR[0] <= sx and 0 <= centerR[1] <= sy:
                vagl.draw_circle(centerR[0], centerR[1],
                                 (centerR - mco).length, 256)
            else:
                angle = (2 * math.pi /
                         (2 * (centerR - mco).length * math.pi / 2.0))
                angle = max(angle, 1E-6)
                mat = Matrix.Rotation(angle, 2)
                v = mco - centerR
                vec = mco.copy()
                bgl.glBegin(bgl.GL_LINE_STRIP)
                while 0 <= vec[0] <= sx and 0 <= vec[1] <= sy:
                    bgl.glVertex2f(*vec)
                    v = v * mat
                    vec = v + centerR
                bgl.glVertex2f(*vec)
                bgl.glEnd()
                mat = Matrix.Rotation(-angle, 2)
                v = mco - centerR
                vec = mco.copy()
                bgl.glBegin(bgl.GL_LINE_STRIP)
                while 0 <= vec[0] <= sx and 0 <= vec[1] <= sy:
                    bgl.glVertex2f(*vec)
                    v = v * mat
                    vec = v + centerR
                bgl.glVertex2f(*vec)
                bgl.glEnd()

        # Background Line -----------------------------------------------------
        if len(coordsR) > 1:
            v1R = coordsR[-2]
            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2f(v1R[0], min(v1R[1], mco[1]))
            bgl.glVertex2f(v1R[0], data.mcbox_x[1])
            bgl.glVertex2f(mco[0], data.mcbox_x[1])
            bgl.glEnd()

            bgl.glBegin(bgl.GL_LINE_STRIP)
            bgl.glVertex2f(min(v1R[0], mco[0]), v1R[1])
            bgl.glVertex2f(data.mcbox_y[0], v1R[1])
            bgl.glVertex2f(data.mcbox_y[0], mco[1])
            bgl.glEnd()


    bgl.glEnable(bgl.GL_BLEND)
    if use_fill:
        draw_backgrount_circle()
        draw_scales()
        draw_scale_numbers()
        draw_numbers()
        draw_mouse_numbers()

    else:
        set_model_view_z(10)
        draw_mouse_numbers()
        set_model_view_z(8)
        draw_numbers()
        set_model_view_z(5)
        draw_scale_numbers()
        set_model_view_z(4)
        draw_scales()
        set_model_view_z(3)
        draw_backgrount_circle()
    bgl.glDisable(bgl.GL_BLEND)

    set_model_view_z(0)


def draw_cross_cursor(context, event):
    running_measure = RegionRuler_PG._measure
    prefs = RegionRulerPreferences.get_instance()
    if not data.is_inside:
        return
    if running_measure or data.simple_measure:
        if context.area.type == 'VIEW_3D':
            if not data.measure_points:
                return
    elif not prefs.draw_cross_cursor:
        return
    elif context.mode in ('SCULPT', 'PAINT_WEIGHT', 'PAINT_VERTEX',
                          'PAINT_TEXTURE'):
        return

    region = context.region
    sx, sy = region.width, region.height
    x, y = event.mco_region_mod
    offset, size = prefs.cross_cursor
    if size <= 0:
        end = [0, sx, 0, sy]
    else:
        s = offset + size
        end = [x - s, x + s, y - s, y + s]
    coords = [
        (x - offset, y), (end[0], y),  # left
        (x + offset, y), (end[1], y),  # right
        (x, y - offset), (x, end[2]),  # bottom
        (x, y + offset), (x, end[3]),  # top
    ]
    if running_measure or data.simple_measure:
        bgl.glColor4f(*(list(prefs.color.line) + [0.5]))
    else:
        bgl.glColor4f(*prefs.color.cursor)
    bgl.glBegin(bgl.GL_LINES)
    for co in coords:
        bgl.glVertex2f(*co)
    bgl.glEnd()


def make_mouse_coordinate_label(context, unit_system, value):
    # 丸めは0方向への切り捨て
    if unit_system.system == 'NONE':
        e = max(0, -int(math.log10(unit_system.bupg) - 1))
        val = Decimal(value)
        exp = Decimal('1e-' + str(e))
        text = str(val.quantize(exp, rounding=decimal.ROUND_DOWN))
    else:
        units = unit_system.units
        start = end = calc_exp = ''
        i = units.index(unit_system.unit)
        for base_unit in units:
            if base_unit.flag & units.UNIT_BASE:
                break
        if unit_system.use_separate:
            end = units.next_basic(unit_system.unit.symbol, False)
            if not end:
                end = units.sorted_basic_symbols[-1]
            # 表記は'mm'迄とする
            if unit_system.system == 'METRIC':
                if units.scalar(end) <= units.scalar('mm'):
                    end = 'mm'
                    calc_exp = end
        else:
            if unit_system.system == 'METRIC':
                unit = unit_system.unit
                start = units.next_basic(unit.symbol, False)
                # 表記は'mm'迄とする
                if unit.scalar <= units.scalar('mm'):
                    start = 'mm'
                calc_exp = start
            else:
                next_unit = units[min(i + 1, len(units) - 1)]
                start = modify_imperial_symbol(next_unit.symbol)
                calc_exp = start

        if calc_exp:
            base_per_dot = unit_system.bupd * unit_system.scale_length
            f = float(base_unit.scalar / units.scalar(calc_exp))
            exp = min(round(math.log10(base_per_dot * f)), 0)
        else:
            exp = 0

        text = unit_system.num_to_unit(value, start=start, end=end,
                                       verbose=(False, True, True),
                                       rounding_exp=exp,
                                       rounding=decimal.ROUND_DOWN)
    return text


def draw_mouse_coordinates_lower_right(context, event, use_fill):
    """マウス座標をカーソルに追従せずに右下に描画"""
    prefs = RegionRulerPreferences.get_instance()

    unit_system = data.unit_system
    font = prefs.font
    blf.size(font.id, font.mcsize, context.user_preferences.system.dpi)
    _, th = blf.dimensions(font.id, string.digits)

    x_label = make_mouse_coordinate_label(context, unit_system, data.mval[0])
    y_label = make_mouse_coordinate_label(context, unit_system, data.mval[1])
    label = x_label + ', ' + y_label
    tw, _ = blf.dimensions(font.id, label)

    region = context.region

    box = [region.width - tw - font.margin * 2,
           0,
           tw + font.margin * 2,
           th + font.margin * 2]

    mco = event.mco_region_mod
    if prefs.autohide_mouse_coordinate:
        f = prefs.autohide_MC_threshold
        if box[0] - f < mco[0] < box[0] + box[2] + f:
            if box[1] - f < mco[1] < box[1] + box[3] + f:
                return

    draw_box(context, box, line=True, fill=use_fill,
             line_color=prefs.color.line, fill_back_color=True)

    blf.position(font.id, box[0] + font.margin, box[1] + font.margin, 0)
    vagl.blf_draw(font.id, label)

    if not use_fill:
        bgl.glColorMask(0, 0, 0, 0)
        draw_box(context, box, fill=True)
        bgl.glColorMask(1, 1, 1, 1)


def draw_mouse_coordinates(context, event, use_fill):
    wm = context.window_manager
    ruler_settings = space_prop.get(context.space_data, 'region_ruler')
    running_measure = ruler_settings.measure
    prefs = RegionRulerPreferences.get_instance()
    # data.mcbox_x, data.ymcboxの計算だけは必要なので
    # data.is_insideがFalseだからといってすぐreturnしない
    if not running_measure and not data.simple_measure:
        if not prefs.draw_mouse_coordinates or not data.is_inside:
            return

    if prefs.mouse_coordinates_position == 'lower_right':
        set_model_view_z(100)
        draw_mouse_coordinates_lower_right(context, event, use_fill)
        set_model_view_z(0)
        if not running_measure and not data.simple_measure:
            return

    area = context.area
    region = context.region
    xmin, ymin, xmax, ymax = region_drawing_rectangle(context, area, region)
    mco = event.mco_region_mod
    ssmain = prefs.scale_size[0]
    triangle_size = 6

    font = prefs.font
    blf.size(font.id, font.mcsize, context.user_preferences.system.dpi)
    _, th = blf.dimensions(font.id, string.digits)

    set_model_view_z(90)

    # X-Axis (Top)
    if area.type == 'IMAGE_EDITOR':
        unit_system = data.unit_system_2d_x
    else:
        unit_system = data.unit_system
    text = make_mouse_coordinate_label(context, unit_system, data.mval[0])
    tw, _ = blf.dimensions(font.id, text)
    boxw = tw + font.margin * 2
    boxh = th + font.margin * 2
    boxx = mco[0] - boxw / 2
    boxy = ymax - ssmain - boxh
    box = [boxx, boxy, boxw, boxh]

    # 3DView左上の文字と重なる場合は塗りつぶす
    rect = view3d_upper_left_text_rect(context)
    use_fill_x = (boxx < rect[1] and boxy < rect[3] and
                  rect[0] < boxx + boxw and rect[2] < boxy + boxh) or use_fill
    blf.size(font.id, font.mcsize, context.user_preferences.system.dpi)

    bgl.glEnable(bgl.GL_BLEND)
    if data.is_inside and (not prefs.autohide_mouse_coordinate or
                           mco[1] < boxy - prefs.autohide_MC_threshold or
                           running_measure):
        draw_box(context, box, line=True, fill=use_fill_x,
                 line_color=prefs.color.line, fill_back_color=True)

        # 上向きの三角形
        x2 = mco[0] - triangle_size / 2
        x3 = x2 + triangle_size
        y2 = ymax - ssmain
        vagl.draw_triangle((x2, y2), (x3, y2), (mco[0], ymax), poly=True)
        vagl.draw_triangle((x2, y2), (x3, y2), (mco[0], ymax))

        bgl.glColor3f(*prefs.color.number)
        blf.position(font.id, boxx + font.margin, boxy + font.margin, 0)
        draw_font_context(context, font.id, text, outline=not use_fill_x,
                          outline_color=prefs.color.number_outline)
        if not use_fill_x:
            bgl.glColorMask(0, 0, 0, 0)
            draw_box(context, box, fill=True)
            bgl.glColorMask(1, 1, 1, 1)

        data.mcbox_x = box

    else:
        data.mcbox_x = [mco[0], ymax - ssmain, 0, 0]

    set_model_view_z(80)

    # Y-Axis (Right)
    if area.type == 'IMAGE_EDITOR':
        unit_system = data.unit_system_2d_y
    else:
        unit_system = data.unit_system
    text = make_mouse_coordinate_label(context, unit_system, data.mval[1])
    text_lines = text.split(' ')
    tw = max([blf.dimensions(font.id, t)[0] for t in text_lines])
    boxw = tw + font.margin * 2
    boxh = th * len(text_lines) + font.margin * (len(text_lines) + 1)
    boxx = xmax - ssmain - boxw
    boxy = mco[1] - boxh / 2
    box = [boxx, boxy, boxw, boxh]

    if data.is_inside and (not prefs.autohide_mouse_coordinate or
                           mco[0] < boxx - prefs.autohide_MC_threshold or
                           running_measure):
        draw_box(context, box, line=True, fill=use_fill,
                 line_color=prefs.color.line, fill_back_color=True)

        # 右向きの三角形
        y2 = mco[1] - triangle_size / 2
        y3 = y2 + triangle_size
        x2 = xmax - ssmain
        vagl.draw_triangle((x2, y2), (xmax, mco[1]), (x2, y3), poly=True)
        vagl.draw_triangle((x2, y2), (xmax, mco[1]), (x2, y3))

        bgl.glColor3f(*prefs.color.number)
        py = mco[1] + boxh / 2 - font.margin - th
        for text_line in text_lines:
            tw, _ = blf.dimensions(font.id, text_line)
            px = xmax - ssmain - tw - font.margin
            blf.position(font.id, px, py, 0)
            draw_font_context(context, font.id, text_line,
                              outline=not use_fill,
                              outline_color=prefs.color.number_outline)
            py -= th + font.margin

        if not use_fill:
            bgl.glColorMask(0, 0, 0, 0)
            draw_box(context, box, fill=True)
            bgl.glColorMask(1, 1, 1, 1)

        data.mcbox_y = box

    else:
        data.mcbox_y = [xmax - ssmain, mco[1], 0, 0]

    set_model_view_z(0)


def draw_callback(context):
    # print('draw_callback(), {}, area: {}, region: {}'.format(
    #       context.screen.name, context.area.as_pointer(), context.region.id))
    wm = context.window_manager
    window = context.window
    prop = space_prop.get(context.space_data, 'region_ruler')
    prefs = RegionRulerPreferences.get_instance()
    ptr = window.as_pointer()

    if data.handle:
        if ptr not in data.operators:
            if is_modal_needed(context):
                bpy.ops.view3d.region_ruler('INVOKE_DEFAULT')
            elif ptr not in data.events:
                bpy.ops.view3d.region_ruler('INVOKE_DEFAULT',
                                            get_event_only=True)

    if not prop.enable:
        return

    glsettings = vagl.GLSettings(context)
    glsettings.push()

    event = data.events[ptr]

    # simpleMeasure表示を消す。ここでのEvent.typeは当てにならない
    if data.alt and not event.alt:
        if event.mco != event.mco_prev:
            data.alt = False
            if data.simple_measure:
                if not prop.measure and not data.alt:
                    data.simple_measure = False
                    data.measure_points.clear()

    data.updated_space(context, glsettings)

    if context.area.type in ('IMAGE_EDITOR', 'NODE_EDITOR'):
        cm = glsettings.region_pixel_space().enter()

    bgl.glColorMask(1, 1, 1, 1)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glDisable(bgl.GL_STENCIL_TEST)
    # bgl.glEnable(bgl.GL_POLYGON_SMOOTH)

    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glDepthMask(bgl.GL_TRUE)
    # Z=0.0で描画したものは0.5で格納, 描画時の値が大きいほど格納値は小さくなる
    bgl.glClearDepth(1.0)
    bgl.glClear(bgl.GL_DEPTH_BUFFER_BIT)
    bgl.glDepthFunc(bgl.GL_LEQUAL)

    if prefs.use_fill:
        # Z: 50
        draw_mask(context)

        # 以下 Z: 0
        draw_region_rulers(context)

        bgl.glDisable(bgl.GL_DEPTH_TEST)

        draw_cross_cursor(context, event)
        draw_unit_box(context, True)
        draw_measure(context, event)
        draw_mouse_coordinates(context, event, True)

    else:
        # z: 50
        draw_mask(context)

        # Z: 90(X-Axis), 80(Y-Axis)
        draw_mouse_coordinates(context, event, False)

        # Z: 20
        draw_unit_box(context, False)

        draw_cross_cursor(context, event)

        # Z: 10-3
        draw_measure(context, event)

        draw_region_rulers(context)

    if context.area.type in ('IMAGE_EDITOR', 'NODE_EDITOR'):
        cm.exit()
    glsettings.pop()
    glsettings.font_size()


def draw_handler_add(context):
    if not data.handle:
        data.handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback, (context,), 'WINDOW', 'POST_PIXEL')
        msg = "SpaceView3D.draw_handler_add(..., 'WINDOW', 'POST_PIXEL')"
        logger.debug(msg)
    if not data.handle_image:
        data.handle_image = bpy.types.SpaceImageEditor.draw_handler_add(
            draw_callback, (context,), 'WINDOW', 'POST_VIEW')
        msg = "SpaceImageEditor.draw_handler_add(..., 'WINDOW', 'POST_VIEW')"
        logger.debug(msg)
    if not data.handle_node:
        data.handle_node = bpy.types.SpaceNodeEditor.draw_handler_add(
            draw_callback, (context,), 'WINDOW', 'POST_VIEW')
        msg = "SpaceNodeEditor.draw_handler_add(..., 'WINDOW', 'POST_VIEW')"
        logger.debug(msg)


def draw_handler_remove():
    if data.handle:
        bpy.types.SpaceView3D.draw_handler_remove(data.handle, 'WINDOW')
        data.handle = None
        logger.debug("SpaceView3D.draw_handler_remove(..., 'WINDOW')")
    if data.handle_image:
        bpy.types.SpaceImageEditor.draw_handler_remove(
            data.handle_image, 'WINDOW')
        data.handle_image = None
        logger.debug("SpaceImageEditor.draw_handler_remove(..., 'WINDOW')")
    if data.handle_node:
        bpy.types.SpaceNodeEditor.draw_handler_remove(data.handle_node,
            'WINDOW')
        data.handle_node = None
        logger.debug("SpaceNodeEditor.draw_handler_remove(..., 'WINDOW')")


###############################################################################
# Operator
###############################################################################
class VIEW3D_OT_region_ruler(bpy.types.Operator):
    bl_description = ''
    bl_idname = 'view3d.region_ruler'
    bl_label = 'Region Ruler'

    bl_options = {'REGISTER'}

    get_event_only = vap.BP('get_event_only',
                            default=False, options={'HIDDEN', 'SKIP_SAVE'})

    def __init__(self):
        self.terminate = False
        self.mco_prev = (0, 0)  # region coords

    @classmethod
    def poll(cls, context):
        data.wm_sync()
        return context.window.as_pointer() not in data.operators

    def modal_measure(self, context, event):
        prefs = RegionRulerPreferences.get_instance()
        running_measure = RegionRuler_PG._measure

        retval = {'PASS_THROUGH'}
        do_redraw = do_redraw_panel = False

        area, region = vawm.mouse_area_region((event.mouse_x, event.mouse_y))
        if area and area.type == 'VIEW_3D' and region.type == 'WINDOW':
            regions = [ar for ar in area.regions if ar.type == 'WINDOW']
            i = regions.index(region)
            v3d = area.spaces.active
            if v3d.region_quadviews:
                rv3d = list(v3d.region_quadviews)[i]
            else:
                rv3d = v3d.region_3d
        else:
            rv3d = None

        if event.type in ('LEFT_ALT', 'RIGHT_ALT'):
            if event.value == 'PRESS':
                data.alt = True
            elif event.value == 'RELEASE':
                data.alt = False
        if event.type == 'MOUSEMOVE':
            if data.alt and not event.alt:
                if (event.mouse_x != event.mouse_prev_x or
                        event.mouse_y != event.mouse_prev_y):
                    data.alt = False

        if data.simple_measure:
            if not running_measure and not data.alt:
                data.simple_measure = False
                data.measure_points.clear()
                retval = {'RUNNING_MODAL'}
                do_redraw = True
        if not event.shift or \
           event.type not in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'):
            data.shift = None

        if region and rv3d:
            mco = (event.mouse_x - region.x, event.mouse_y - region.y)
            if running_measure or data.simple_measure:
                if event.type == 'ESC' and event.value == 'PRESS':
                    RegionRuler_PG._measure = False
                    data.measure_points.clear()
                    do_redraw = True
                    do_redraw_panel = True
                elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                    if data.measure_points:
                        dvec = data.measure_points[-1]
                        vec = vav.unproject(region, rv3d, mco, dvec)
                    else:
                        dvec = Vector(context.scene.cursor_location)
                        vec = vav.unproject(region, rv3d, mco, dvec)
                    if event.shift:
                        data.measure_points.append(vec)
                    else:
                        data.measure_points[:] = [vec]
                    retval = {'RUNNING_MODAL'}
                    do_redraw = True
                elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
                    if data.simple_measure and data.measure_points or \
                       running_measure:
                        if event.shift:
                            data.shift = True
                        else:
                            data.measure_points[-1:] = []
                            do_redraw = True
                        retval = {'RUNNING_MODAL'}
                elif event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'):
                    if data.shift and data.measure_points:
                        dvec = data.measure_points[-1]
                        vec1 = vav.unproject(region, rv3d, self.mco_prev, dvec)
                        vec2 = vav.unproject(region, rv3d, mco, dvec)
                        data.measure_points[-1] += vec2 - vec1
                        retval = {'RUNNING_MODAL'}
            if not running_measure and prefs.use_simple_measure:
                if event.type in ('LEFT_ALT', 'RIGHT_ALT'):
                    if event.value == 'PRESS' and not data.simple_measure:
                        data.simple_measure = True
                        data.measure_points.clear()
                        retval = {'RUNNING_MODAL'}
                    elif event.value == 'RELEASE':
                        data.simple_measure = False
                        data.measure_points.clear()
                        retval = {'RUNNING_MODAL'}
                    do_redraw = True

        return retval, do_redraw, do_redraw_panel

    def modal(self, context, event):
        # event = data.events[context.window.as_pointer()]
        # print(event.type, event.value,
        #       time.time(),
        #       context.window.screen.name,
        #       context.area, context.region,
        #       'shift:', event.shift, 'alt:', event.alt,
        #       (event.mouse_x, event.mouse_y),
        #       (event.mouse_region_x, event.mouse_region_y))

        window = context.window
        ptr = window.as_pointer()

        # scene_update_postで終了指定されたもの
        running_other_modal = ptr in data.exit_waiting
        if running_other_modal:
            ops = data.exit_waiting[ptr]
            if self in ops:
                ops.remove(self)
                if not ops:
                    del data.exit_waiting[ptr]
                msg = 'Exit view3d.region_ruler() (restarted) (Window at {:x})'
                logger.debug(msg.format(context.window.as_pointer()))
                return {'FINISHED', 'PASS_THROUGH'}

        data.mouse_coords[context.window.as_pointer()] = event.mco

        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'PASS_THROUGH'}
        elif event.type == 'MOUSEMOVE':
            # commit 53a3850a8a05249942a0c4a16060e9491456af02
            # source/blender/editors/interface/interface_handlers.c:9200
            # let's make sure we are really not hovering a button by adding
            # a mousemove!
            # XXX some WM_event_add_mousemove calls may become unnecessary
            # with this and can be removed
            #
            # パネル上のボタン類が無い所にマウスを置くと絶えず'MOUSEMOVE'
            # イベントが発生し続ける。
            if (event.mouse_x == event.mouse_prev_x and
                    event.mouse_y == event.mouse_prev_y):
                return {'PASS_THROUGH'}
        elif event.type.startswith('TIMER'):
            return {'PASS_THROUGH'}

        prefs = RegionRulerPreferences.get_instance()
        wm = context.window_manager
        data.wm_sync()

        # exit
        windows = {win.as_pointer(): win for win in wm.windows}
        if not is_modal_needed(context):
            for win in wm.windows:
                op = data.operators.get(win.as_pointer())
                if op:
                    op.terminate = True
                    del data.operators[win.as_pointer()]
        address = context.window.as_pointer()
        if address not in windows:
            # modalオペレータは実行中のwindowが閉じられたら
            # 二度と呼ばれなくなる（筈）なので不要か？
            self.terminate = True
        if self.terminate:
            msg = 'Exit view3d.region_ruler() (Window at {:x})'.format(address)
            logger.debug(msg)
            if address in data.operators:
                del data.operators[address]
            if address in windows:
                redraw_regions(context, window=windows[address])
            # NOTE: View3DのPropertiesPanelでチェックボックスをOFFにして終了す
            # る場合に、マウスが上を通過した他のチェックボックスも切り替わって
            # しまう。{'FINISHED', 'PASS_THROUGH'}を返す事でこれを回避できる。
            # ソースは見てないので詳細不明
            return {'FINISHED', 'PASS_THROUGH'}

        # 非アクティブになったwindowを再描画
        active_window = vawm.active_window(context)
        if active_window:
            act_win_ptr = active_window.as_pointer()
        else:
            act_win_ptr = None
        if data.active_window and data.active_window != act_win_ptr:
            for win in wm.windows:
                if win.as_pointer() == data.active_window:
                    for area in win.screen.areas:
                        if area.type in ('VIEW_3D', 'IMAGE_EDITOR',
                                         'NODE_EDITOR'):
                            space = area.spaces.active
                            if data.spaces[space.as_pointer()]['enable']:
                                for region in area.regions:
                                    if region.type == 'WINDOW':
                                        region.tag_redraw()
        data.active_window = act_win_ptr

        do_redraw = do_redraw_panel = False
        if prefs.cross_cursor or prefs.draw_mouse_coordinates:
            if event.type == 'MOUSEMOVE':
                do_redraw = True

        # Measure
        if not running_other_modal:
            retval, do_redraw_measure, do_redraw_panel_measure = \
                self.modal_measure(context, event)
            do_redraw |= do_redraw_measure
            do_redraw_panel |= do_redraw_panel_measure
        else:
            retval = {'PASS_THROUGH'}

        # 再描画: active region
        area, region = vawm.mouse_area_region(event.mco, find_reverse=True)
        if area and area.type not in ('VIEW_3D', 'IMAGE_EDITOR',
                                      'NODE_EDITOR'):
            area = None
        if area:
            space = area.spaces.active
            prop = space_prop.get(space, 'region_ruler')
            if prop.enable:
                if do_redraw and region:
                    region.tag_redraw()
                if do_redraw_panel:
                    for ar in area.regions:
                        if ar.type == 'UI':
                            ar.tag_redraw()
        # 再描画: prev region
        prev_region = vawm.region_from_id(data.prev_region_id, context.screen)
        prev_area = vawm.get_area_from_data(prev_region)
        if prev_area and prev_area.type not in ('VIEW_3D', 'IMAGE_EDITOR',
                                                'NODE_EDITOR'):
            prev_area = None
        if prev_area and prev_region and prev_region != region:
            space = prev_area.spaces.active
            prop = space_prop.get(space, 'region_ruler')
            if prop.enable:
                prev_region.tag_redraw()

        if region:
            data.prev_region_id = region.id
        else:
            data.prev_region_id = -1

        if region:
            self.mco_prev = (event.mouse_x - region.x,
                             event.mouse_y - region.y)

        if not running_other_modal:
            auto_save(context)

        return retval

    def invoke(self, context, event):
        draw_handler_add(context)

        address = context.window.as_pointer()
        if address in data.operators:
            return {'FINISHED'}

        data.events[address] = event
        if self.get_event_only:
            return {'FINISHED'}

        data.operators[address] = self
        data.mouse_coords[address] = event.mco
        context.window_manager.modal_handler_add(self)
        if KEEP_MODAL_HANDLERS_HEAD:
            handlers = bpy.app.handlers.scene_update_post
            if scene_update_post_handler not in handlers:
                handlers.append(scene_update_post_handler)
        region = context.region
        if region:
            self.mco_prev = (event.mouse_x - region.x,
                             event.mouse_y - region.y)
        redraw_regions(context)
        logger.debug('view3d.region_ruler() (Window at {:x})'.format(address))
        return {'RUNNING_MODAL'}


class VIEW3D_OT_region_ruler_terminate(bpy.types.Operator):
    # bl_description = 'Addonの有効／無効を切り替える際には必ず実行すること'
    # ↑前は落ちたんだけど今は問題ないか
    bl_idname = 'view3d.region_ruler_terminate'
    bl_label = 'Region Ruler Terminate'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        draw_handler_remove()
        redraw_regions(context)

        handlers = bpy.app.handlers.scene_update_post
        if scene_update_post_handler in handlers:
            handlers.remove(scene_update_post_handler)

        for window in context.window_manager.windows:
            op = data.operators.get(window.as_pointer())
            if op:
                op.terminate = True
        return {'FINISHED'}


###############################################################################
# Panel
###############################################################################
class VIEW3D_PT_region_ruler_base:
    bl_label = 'Region Ruler'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    # enum set in {'DEFAULT_CLOSED', 'HIDE_HEADER'}, default {'DEFAULT_CLOSED'}
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        wm = context.window_manager
        ruler_settings = space_prop.get(context.space_data, 'region_ruler')

        layout = self.layout

        if self.bl_space_type == 'VIEW_3D':
            col = layout.column()
            col.prop(ruler_settings, 'unit', text='Unit')
        elif self.bl_space_type == 'IMAGE_EDITOR':
            col = layout.column()
            col.prop(ruler_settings, 'image_editor_unit', text='Unit')
        # elif self.bl_space_type == 'NODE_EDITOR':
        #     col = layout.column()
        #     col.prop(ruler_settings, 'node_editor_unit', text='Unit')

        if self.bl_space_type == 'VIEW_3D':
            col = layout.column()
            col.prop(ruler_settings, 'origin_type', text='Origin')
            if ruler_settings.origin_type == 'custom':
                col.prop(ruler_settings, 'origin_location', text='')
        elif self.bl_space_type == 'IMAGE_EDITOR':
            col = layout.column()
            col.prop(ruler_settings, 'image_editor_origin_type', text='Origin')
            if ruler_settings.image_editor_origin_type == 'custom':
                row = col.row()
                row.prop(ruler_settings, 'image_editor_origin_location',
                         text='')

        if self.bl_space_type == 'VIEW_3D':
            col = layout.column()
            col.prop(ruler_settings, 'view_depth', text='Depth')
            # テンキー5で切り替えた際にはパネルが再描画されない
            v3d = context.space_data
            if v3d:
                for region in [v3d.region_3d] + list(v3d.region_quadviews):
                    if region.view_perspective != 'ORTHO':
                        col.active = True
                        break
                else:
                    col.active = False

        if self.bl_space_type == 'VIEW_3D':
            layout.prop(ruler_settings, 'measure', toggle=True)

        col = layout.column()
        sub = col.split(0.6, True)
        sub.operator('view3d.region_ruler', text='Run')
        sub.operator('view3d.region_ruler_terminate', text='Kill')

    def draw_header(self, context):
        # draw関数の中では一部のプロパティの変更が効かないので
        # sync_spacesやget_settings(no_add=False)を実行しない。
        ruler_settings = space_prop.get(context.space_data, 'region_ruler')
        self.layout.prop(ruler_settings, 'enable', text='')


class VIEW3D_PT_region_ruler(VIEW3D_PT_region_ruler_base, bpy.types.Panel):
    bl_space_type = 'VIEW_3D'

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'VIEW_3D'


class VIEW3D_PT_region_ruler_image(VIEW3D_PT_region_ruler_base,
                                   bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'IMAGE_EDITOR'


class VIEW3D_PT_region_ruler_node(VIEW3D_PT_region_ruler_base,
                                  bpy.types.Panel):

    bl_space_type = 'NODE_EDITOR'

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'NODE_EDITOR'


###############################################################################
# AutoSave
###############################################################################
def auto_save(context):
    """ModalOperator中はAutoSaveが働かないのでこちらで再現する
    """
    prefs = RegionRulerPreferences.get_instance()
    file_prefs = context.user_preferences.filepaths
    if not file_prefs.use_auto_save_temporary_files or not prefs.auto_save:
        return None

    if platform.system() not in ('Linux', 'Windows'):
        # os.gitpid()が使用出来ず、ファイル名が再現出来無い為
        return False

    t = time.time()
    # 指定時間に達しているか確認
    if t - data.auto_save_time < file_prefs.auto_save_time * 60:
        return None

    # 保存先となるパスを生成
    pid = os.getpid()
    if bpy.data.is_saved:
        file_name = os.path.basename(bpy.data.filepath)
        name = os.path.splitext(file_name)[0]
        save_base_name = '{}-{}.blend'.format(name, pid)
    else:
        save_base_name = '{}.blend'.format(pid)
    # auto_saveはUserPrefのTempディレクトリに行われる。
    # bpy.app.tempdirはその下の'blender_******'ディレクトリを指す。
    # 例: '/tmp/blender_Q7s8pE/'  (最後は必ず区切り文字で終わる)
    # ※tempdirに'/home/'等の権限が無いパスを指定していた場合、下位ディレクトリ
    # ('blender_******')が生成されず、bpy.app.tempdirも'/home/'になる。
    save_dir = os.path.dirname(os.path.dirname(bpy.app.tempdir))
    if platform.system() == 'Windows' and not os.path.exists(save_dir):
        save_dir = bpy.utils.user_resource('AUTOSAVE')
    save_path = os.path.join(save_dir, save_base_name)

    # 既にファイルが存在して更新時間がdata.auto_save_timeより進んでいたら
    # その時間と同期する
    if os.path.exists(save_path):
        st = os.stat(save_path)
        if data.auto_save_time < st.st_mtime:
            data.auto_save_time = st.st_mtime
    # 指定時間に達しているか確認
    if t - data.auto_save_time < file_prefs.auto_save_time * 60:
        return None

    logger.debug("Try auto save '{}' ...".format(save_path))

    # ディレクトリ生成
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
        except:
            logger.error("Unable to save '{}'".format(save_dir), exc_info=True)
            data.auto_save_time = t
            return False
    # Save
    try:
        bpy.ops.wm.save_as_mainfile(
            False, filepath=save_path, compress=False, relative_remap=True,
            copy=True, use_mesh_compat=False)
    except:
        logger.error("Unable to save '{}'".format(save_dir), exc_info=True)
        data.auto_save_time = t
        return False
    else:
        logger.info("Auto Save '{}'".format(save_path))
        # 設定し直す事で内部のタイマーがリセットされる
        data.auto_save_time = os.stat(save_path).st_mtime
        file_prefs.auto_save_time = file_prefs.auto_save_time
        return True


###############################################################################
# Save / Load / Register
###############################################################################
@persistent
def load_pre_handler(dummy):
    logger.debug('Load Pre')
    draw_handler_remove()

    # 古いアドレスが再利用されるかもしれないので初期化しておく
    data.operators.clear()
    data.spaces.clear()
    # 消さなくても大丈夫だろうけど一応
    data.active_window = None
    data.events.clear()
    data.mouse_coords.clear()
    data.exit_waiting.clear()

    RegionRuler_PG._measure = 0


@persistent
def load_post_handler(dummy):
    logger.debug('Load Post')

    # 読み込み時にAutoSaveのタイマーリセット
    data.auto_save_time = time.time()

    data.wm_sync()

    add_callback = False
    for space in (space for screen in bpy.data.screens
                  for area in screen.areas
                  for space in area.spaces
                  if space.type in {'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR'}):
        prop = space_prop.get(space, 'region_ruler')
        if prop.enable:
            add_callback = True
            break

    if add_callback:
        draw_handler_add(bpy.context)


@persistent
def scene_update_post_handler(dummy):
    """他のModalOperatorが開始され、マウスが動いたのに再描画がされない状況に
    対応する為、Rulerを再起動しハンドラの先頭に登録し直す。
    """
    window = bpy.context.window
    if not window:
        return
    ptr = window.as_pointer()
    if ptr == data.active_window and ptr in data.operators:
        event = data.events[ptr]
        mco = (event.mouse_x, event.mouse_y)
        if mco != data.mouse_coords[ptr]:
            logger.debug('Other modal operator started. Restart ruler')
            op = data.operators.pop(ptr)
            data.exit_waiting.setdefault(ptr, []).append(op)
            vawm.operator_call(bpy.ops.view3d.region_ruler,
                               'INVOKE_DEFAULT', _scene_update=False)


classes = [
    RegionRuler_PG_Font,
    RegionRuler_PG_Color,
    RegionRuler_PG,
    RegionRulerPreferences,
    VIEW3D_OT_region_ruler,
    VIEW3D_OT_region_ruler_terminate,
    VIEW3D_PT_region_ruler,
    VIEW3D_PT_region_ruler_image,
    VIEW3D_PT_region_ruler_node,
]


# Event.mco: (mouse_x, mouse_y)
def event_mco_get(self):
    return self.mouse_x, self.mouse_y


# Event.mco_prev (mouse_prev_x, mouse_prev_y)
def event_mco_prev_get(self):
    return self.mouse_prev_x, self.mouse_prev_y


# Event.mco_region (mouse_region_x, mouse_region_y)
def event_mco_region_get(self):
    return self.mouse_region_x, self.mouse_region_y


def event_mco_region_mod_get(self):
    region = bpy.context.region
    if region:
        return self.mouse_x - region.x, self.mouse_y - region.y
    else:
        return None


def register():
    logger.debug('Register RegionRuler')
    # bpy.utils.register_module(__name__)
    for cls in classes:
        bpy.utils.register_class(cls)
    space_prop.register()

    bpy.types.Event.mco = property(event_mco_get)
    bpy.types.Event.mco_prev = property(event_mco_prev_get)
    bpy.types.Event.mco_region = property(event_mco_region_get)
    bpy.types.Event.mco_region_mod = property(event_mco_region_mod_get)

    # Add handlers
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.load_post.append(load_post_handler)

    # Clear data
    data.operators.clear()
    data.spaces.clear()

    # Auto Run
    # register()中ではbpy.contextが_RestrictContextになっているので不可


def unregister():
    logger.debug('Unregister RegionRuler')
    draw_handler_remove()

    space_prop.unregister()
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)

    # Event.mco, Event.mco_region
    for attr in ('mco', 'mco_prev', 'mco_region'):
        try:
            delattr(bpy.types.Event, attr)
        except AttributeError:
            pass

    # Remove handlers
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.load_post.remove(load_post_handler)


if __name__ == '__main__':
    register()
