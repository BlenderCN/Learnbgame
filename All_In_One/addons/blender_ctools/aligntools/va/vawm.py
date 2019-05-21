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


import time
import itertools
import inspect
import ctypes

import bpy
from mathutils import Vector
import bpy_extras.keyconfig_utils

from .. import localutils
from ..localutils import utils

from . import vaoperator



"""
CType               PyType
Screen       sc     screen
ScrArea      sa     area
ARegion      ar     region
SpaceLink    sl     space_data   # area->spacedata.first
View3D       v3d    space_data   # area->spacedata.first
RegionView3D rv3d   region_data  # ar->regiondata;
"""


###############################################################################
# Get Area / Region / SpaceData / RegionData
###############################################################################
region_types = ['WINDOW', 'HEADER', 'CHANNELS', 'TEMPORARY', 'UI', 'TOOLS',
                'TOOL_PROPS', 'PREVIEW']

space_types = ['EMPTY', 'VIEW_3D', 'TIMELINE', 'GRAPH_EDITOR',
               'DOPESHEET_EDITOR', 'NLA_EDITOR', 'IMAGE_EDITOR',
               'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'TEXT_EDITOR',
               'NODE_EDITOR', 'LOGIC_EDITOR', 'PROPERTIES', 'OUTLINER',
               'USER_PREFERENCES', 'INFO', 'FILE_BROWSER', 'CONSOLE']


def mouse_area_region(mco, screen=None, find_reverse=False):
    """マウスカーソルが内側に有るAreaとRegionを返す。
    :param mco: window座標 [event.mouse_x, event.mouse_y]
    :type mco: Vector | list | tuple
    :param screen: screenを指定する。初期値はbpy.context.screen
    :type screen: bpy.types.Screen
    :param find_reverse: region_overlapの事も考え、通常は 'TOOLS', 'PROPERTIES'
        等を最初に確認するが、これを真にすると 'WINDOW' を最初に確認する。
    :type find_reverse: bool
    :rtype: (bpy.types.Area, bpy.types.Region)
    """
    if not screen:
        screen = bpy.context.screen
    for area in screen.areas:
        regions = list(area.regions)
        ls = regions[:]
        regions.sort(key=lambda r: (int(r.type == 'WINDOW'), ls.index(r)),
                     reverse=find_reverse)
        for region in regions:
            if region.id != 0:  # 非表示のものはidが0になる
                if region.x <= mco[0] < region.x + region.width:
                    if region.y <= mco[1] < region.y + region.height:
                        return area, region
    return None, None


def region_from_id(region_id, screen=None):
    """idが一致するRegionを返す
    :type region_id: int
    :rtype: Region
    """
    if region_id == 0:
        return None
    if not screen:
        screen = bpy.context.screen
    for area in screen.areas:
        for region in area.regions:
            if region.id == region_id:
                return region


def get_area_from_data(data):
    """Region若しくはSpaceが所属するAreaを返す
    :type data: Region | Space
    :return:
    """
    if isinstance(data, bpy.types.Region):
        for sa in data.id_data.areas:  # data.id_data == Screen
            for ar in sa.regions:
                if ar == data:
                    return sa
    elif isinstance(data, bpy.types.Space):
        for sa in data.id_data.areas:
            for sl in sa.spaces:
                if sl == data:
                    return sa


###############################################################################
#  Find
###############################################################################
def layouts(use_hidden=True):
    """関連するWindowManagerの要素を纏めた辞書を作る。所要時間2/1000秒程度。
    :param use_hidden: 偽だと非アクティブのSpaceに関する要素を除外する
    :type use_hidden: bool
    :return:
        activeでないspaceに属するregionとrv3dは無視。
        (Area.typeを切り替えれば参照出来るが、再描画されることになるので避ける)
        keyの型によってvalueの辞書の要素が変化。
        bpy.types.Window:
            {'screen': screen, 'areas': [area, ...], 'regions': [region, ...],
             'spaces': [spaces, ...], 'rv3ds': [rv3ds, ...]}
        bpy.types.Screen:
            {'window': window(or None), 'areas': [area, ...],
             'regions': [region, ...], 'spaces': [spaces, ...],
             'rv3ds': [rv3ds, ...]}
        bpy.types.Area:
            {'window': window(or None), 'screen': screen,
             'regions': [region, ...], 'spaces': [spaces, ...],
             'rv3ds': [rv3ds, ...]}
        bpy.types.Region:
            {'window': window(or None), 'screen': screen, 'area': area,
             'space': space, 'rv3d': rv3d}
        bpy.types.Space(and subclasses):
            {'window': window(or None), 'screen': screen,
             'area': area, 'regions': [region, ...],
             'rv3ds': [rv3ds, ...]}
        bpy.types.RegionView3D:
            {'window': window(or None), 'screen': screen,
             'area': area, 'region': [region, ...],
             'space': space}
    :rtype: dict

    NOTE:
    blenkernel/intern/context.c, makesrna/intern/rna_context.c 参照
    window_manager: 変更不可
    window:         変更可
    screen:         変更可
    area:           変更可
    space_data:     areaに依存
    region:         変更可
    region_data:    areaとregionに依存。area.typeで判定後にregionから取得

    area, space_data, region, region_dataは
    pythonオブジェクト作成時にscreenを必要とするので
    context.screenは正しく設定しておくこと。

    region_quadviews:
        [左下, 左上, 右下, 右上]
        Lock,Box,Clipの設定は右下の物を使用し、右上はregion_3dと同じ
        quadviewが無効の場合は空のシーケンスになる
    """

    wm_layouts = {}

    # screen, area, region
    screen_window = {}
    for wm in bpy.data.window_managers:
        for window in wm.windows:
            screen_window[window.screen] = window

    for screen in bpy.data.screens:
        # screen
        window = screen_window.get(screen)
        areas = list(screen.areas)
        regions = list(itertools.chain.from_iterable(
            [area.regions for area in areas]))
        if use_hidden:
            spaces = list(itertools.chain.from_iterable(
                [area.spaces for area in areas]))
        else:
            spaces = [area.spaces.active for area in areas]
        screen_rv3ds = []
        wm_layouts[screen] = {
            'window': window, 'areas': areas, 'regions': regions,
            'spaces': spaces, 'rv3ds': screen_rv3ds}

        for area in areas:
            # area
            active_space = area.spaces.active
            regions = list(area.regions)
            if use_hidden:
                spaces = list(area.spaces)
            else:
                spaces = [active_space]
            area_rv3ds = []
            wm_layouts[area] = {
                'window': window, 'screen': screen, 'regions': regions,
                'spaces': spaces, 'rv3ds': area_rv3ds}

            # space
            for space in spaces:
                if space == active_space:
                    regions = list(area.regions)
                else:
                    regions = []
                space_rv3ds = []
                wm_layouts[space] = {
                    'window': window, 'screen': screen, 'area': area,
                    'regions': regions, 'rv3ds': space_rv3ds}

                # rv3d, region
                if space.type == 'VIEW_3D':
                    if space.region_quadviews:
                        rv3ds = space.region_quadviews
                        screen_rv3ds.extend(rv3ds)
                        area_rv3ds.extend(rv3ds)
                        space_rv3ds.extend(rv3ds)
                    else:
                        rv3d = space.region_3d
                        screen_rv3ds.append(rv3d)
                        area_rv3ds.append(rv3d)
                        space_rv3ds.append(rv3d)
                        rv3ds = [rv3d]

                    if space == active_space:
                        win_regions = [ar for ar in area.regions
                                       if ar.type == 'WINDOW']
                    else:
                        if space.region_quadviews:
                            win_regions = [None] * 4
                        else:
                            win_regions = [None]
                    for region, rv3d in zip(win_regions, rv3ds):
                        wm_layouts[rv3d] = {
                            'window': window, 'screen': screen, 'area': area,
                            'region': region, 'space': space}
                        if region:
                            wm_layouts[region] = {
                                'window': window, 'screen': screen,
                                'area': area, 'space': space, 'rv3d': rv3d}

            for region in area.regions:
                # region
                if region not in wm_layouts:
                    wm_layouts[region] = {
                        'window': window, 'screen': screen, 'area': area,
                        'space': active_space, 'rv3d': None}

    # window. screenのものをコピー改変
    for wm in bpy.data.window_managers:
        for window in wm.windows:
            screen = window.screen
            d = {k: list(v) if isinstance(v, list) else v
                 for k, v in wm_layouts[screen].items()}
            d['screen'] = screen
            del d['window']
            wm_layouts[window] = d

    return wm_layouts


def test_layouts():
    t = time.time()
    screen_layouts = layouts()
    print(time.time() - t, False)
    for key, value in screen_layouts.items():
        # if isinstance(key, bpy.types.SpaceView3D):
        #     print(key)
        print(key)
        for k, v in value.items():
            print('  {}: {}'.format(k, v))
        print()


def find(type, *links, use_hidden=True):
    """条件に該当するwindow managerの要素を取得する。
    e.g.
        areas = find(bpy.types.Area, context.region)
        v3ds = find('SpaceView3D', context.screen)
    :param type: 検索対象の型を指定する。若しくはインスタンスを指定して
        linksで絞り込みを行うといった使い方をする。
        利用出来る型: Window, Screen, Area, Region, Space, RegionView3D
    :type type: bpy_struct | str | collections.abs.Sequence
    :param links: conditionに対して絞り込みを行う
    :type links: Window | Screen | Area | Region | Space | RegionView3D
    :param relations: その都度オペレータを呼び出す事が無いように
                      layouts()の返り値を渡す。
    :type relations: dict
    :rtype: list
    """

    wm_layouts = layouts(use_hidden)

    find_type = type
    if not find_type:
        return []

    if isinstance(find_type, list):
        result = find_type
    else:
        if isinstance(find_type, tuple):
            find_type = tuple(find_type)
        elif isinstance(find_type, str):
            find_type = getattr(bpy.types, find_type)
        elif inspect.isclass(find_type):
            find_type = find_type
        else:
            result = [find_type]
            find_type = None
        if find_type:
            result = [obj for obj in wm_layouts if isinstance(obj, find_type)]

    for link_obj in links:
        if link_obj in wm_layouts:
            link_objects = set(localutils.utils.flatten(
                wm_layouts[link_obj].values()))
        else:
            link_objects = []
        result = [obj for obj in result
                  if obj == link_obj or obj in link_objects]

    return result


###############################################################################
# Get Event
###############################################################################
operator_call = vaoperator.operator_call


def event(window=None):
    """Eventを取得する。所要時間8/10000秒以下"""
    def get_event(context, event):
        return event

    if window and isinstance(window, bpy.types.Window):
        override_context = {'window': window}
    else:
        override_context = {}
    return vaoperator.exec_func(
        get_event, override_context=override_context, use_event=True,
        scene_update=False)


###############################################################################
# Active Window
###############################################################################
class wmWindow(ctypes.Structure):
    _fields_ = [
        ('next', ctypes.c_void_p),  # struct wmWindow
        ('prev', ctypes.c_void_p),  # struct wmWindow
        ('ghostwin', ctypes.c_void_p),

        ('screen', ctypes.c_void_p),  # struct bScreen
        ('newscreen', ctypes.c_void_p),  # struct bScreen
        ('screenname', ctypes.c_char * 64),

        ('posx', ctypes.c_short),
        ('posy', ctypes.c_short),
        ('sizex', ctypes.c_short),
        ('sizey', ctypes.c_short),
        ('windowstate', ctypes.c_short),
        ('monitor', ctypes.c_short),
        ('active', ctypes.c_short),
    ]


def active_window(context):
    for window in context.window_manager.windows:
        p = ctypes.c_void_p(window.as_pointer())
        win = ctypes.cast(p, ctypes.POINTER(wmWindow)).contents
        if win.active:
            return window


###############################################################################
#
###############################################################################
class AreaExist:
    """Screenの中に該当typeのAreaが存在するようにする"""
    def __init__(self, context, type):
        self.context = context
        self.type = type
        self.type_prev = ''
        self.area = None
        self.region = None

    def __enter__(self):
        context = self.context
        type_prev = self.type
        area = context.area or context.screen.areas[0]
        if area.type != self.type:
            for area in context.screen.areas:
                if area.type == self.type:
                    break
            else:
                area = context.area or context.screen.areas[0]
                type_prev = area.type
                area.type = self.type
        for region in area.regions:
            if region.type == 'WINDOW':
                break
        else:
            region = None
        self.type_prev = type_prev
        self.area = area
        self.region = region
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.area.type != self.type_prev:
            self.area.type = self.type_prev


# Note:
# U.widget_unit = (U.pixelsize * U.dpi * 20 + 36) / 72  # @ BKE_userdef_state()
# #define UI_UNIT_X               ((void)0, U.widget_unit)
# #define UI_UNIT_Y               ((void)0, U.widget_unit)
# U.pixelsize = wm_window_pixelsize(win);  # @ wm_window_add_ghostwindow() 通常は1


###############################################################################
# Get Keymap
###############################################################################
"""
bpy_extras.keyconfig_utils.KM_HIERARCHY

KM_HIERARCHY = [
    ('Window', 'EMPTY', 'WINDOW', []),  # file save, window change, exit
    ('Screen', 'EMPTY', 'WINDOW', [     # full screen, undo, screenshot
        ('Screen Editing', 'EMPTY', 'WINDOW', []),    # re-sizing, action corners
        ('Header', 'EMPTY', 'WINDOW', []),            # header stuff (per region)
        ]),

    ('View2D', 'EMPTY', 'WINDOW', []),    # view 2d navigation (per region)
    ('View2D Buttons List', 'EMPTY', 'WINDOW', []),  # view 2d with buttons navigation

    ('User Interface', 'EMPTY', 'WINDOW', [
        ('Eyedropper Modal Map', 'EMPTY', 'WINDOW', []),
        ]),

    ('3D View', 'VIEW_3D', 'WINDOW', [  # view 3d navigation and generic stuff (select, transform)
        ('Object Mode', 'EMPTY', 'WINDOW', []),
        ('Mesh', 'EMPTY', 'WINDOW', []),
        ('Curve', 'EMPTY', 'WINDOW', []),
        ('Armature', 'EMPTY', 'WINDOW', []),
        ('Metaball', 'EMPTY', 'WINDOW', []),
        ('Lattice', 'EMPTY', 'WINDOW', []),
        ('Font', 'EMPTY', 'WINDOW', []),

        ('Pose', 'EMPTY', 'WINDOW', []),

        ('Vertex Paint', 'EMPTY', 'WINDOW', []),
        ('Weight Paint', 'EMPTY', 'WINDOW', []),
        ('Weight Paint Vertex Selection', 'EMPTY', 'WINDOW', []),
        ('Face Mask', 'EMPTY', 'WINDOW', []),
        ('Image Paint', 'EMPTY', 'WINDOW', []),  # image and view3d
        ('Sculpt', 'EMPTY', 'WINDOW', []),

        ('Particle', 'EMPTY', 'WINDOW', []),

        ('Knife Tool Modal Map', 'EMPTY', 'WINDOW', []),
        ('Paint Stroke Modal', 'EMPTY', 'WINDOW', []),
        ('Paint Curve', 'EMPTY', 'WINDOW', []),

        ('Object Non-modal', 'EMPTY', 'WINDOW', []),  # mode change

        ('View3D Walk Modal', 'EMPTY', 'WINDOW', []),
        ('View3D Fly Modal', 'EMPTY', 'WINDOW', []),
        ('View3D Rotate Modal', 'EMPTY', 'WINDOW', []),
        ('View3D Move Modal', 'EMPTY', 'WINDOW', []),
        ('View3D Zoom Modal', 'EMPTY', 'WINDOW', []),
        ('View3D Dolly Modal', 'EMPTY', 'WINDOW', []),

        ('3D View Generic', 'VIEW_3D', 'WINDOW', []),    # toolbar and properties
        ]),

    ('Graph Editor', 'GRAPH_EDITOR', 'WINDOW', [
        ('Graph Editor Generic', 'GRAPH_EDITOR', 'WINDOW', []),
        ]),
    ('Dopesheet', 'DOPESHEET_EDITOR', 'WINDOW', []),
    ('NLA Editor', 'NLA_EDITOR', 'WINDOW', [
        ('NLA Channels', 'NLA_EDITOR', 'WINDOW', []),
        ('NLA Generic', 'NLA_EDITOR', 'WINDOW', []),
        ]),
    ('Timeline', 'TIMELINE', 'WINDOW', []),

    ('Image', 'IMAGE_EDITOR', 'WINDOW', [
        ('UV Editor', 'EMPTY', 'WINDOW', []),  # image (reverse order, UVEdit before Image)
        ('Image Paint', 'EMPTY', 'WINDOW', []),  # image and view3d
        ('UV Sculpt', 'EMPTY', 'WINDOW', []),
        ('Image Generic', 'IMAGE_EDITOR', 'WINDOW', []),
        ]),

    ('Outliner', 'OUTLINER', 'WINDOW', []),

    ('Node Editor', 'NODE_EDITOR', 'WINDOW', [
        ('Node Generic', 'NODE_EDITOR', 'WINDOW', []),
        ]),
    ('Sequencer', 'SEQUENCE_EDITOR', 'WINDOW', [
        ('SequencerCommon', 'SEQUENCE_EDITOR', 'WINDOW', []),
        ('SequencerPreview', 'SEQUENCE_EDITOR', 'WINDOW', []),
        ]),
    ('Logic Editor', 'LOGIC_EDITOR', 'WINDOW', []),

    ('File Browser', 'FILE_BROWSER', 'WINDOW', [
        ('File Browser Main', 'FILE_BROWSER', 'WINDOW', []),
        ('File Browser Buttons', 'FILE_BROWSER', 'WINDOW', []),
        ]),

    ('Info', 'INFO', 'WINDOW', []),

    ('Property Editor', 'PROPERTIES', 'WINDOW', []),  # align context menu

    ('Text', 'TEXT_EDITOR', 'WINDOW', [
        ('Text Generic', 'TEXT_EDITOR', 'WINDOW', []),
        ]),
    ('Console', 'CONSOLE', 'WINDOW', []),
    ('Clip', 'CLIP_EDITOR', 'WINDOW', [
        ('Clip Editor', 'CLIP_EDITOR', 'WINDOW', []),
        ('Clip Graph Editor', 'CLIP_EDITOR', 'WINDOW', []),
        ('Clip Dopesheet Editor', 'CLIP_EDITOR', 'WINDOW', []),
        ]),

    ('Grease Pencil', 'EMPTY', 'WINDOW', [  # grease pencil stuff (per region)
        ('Grease Pencil Stroke Edit Mode', 'EMPTY', 'WINDOW', []),
        ]),
    ('Mask Editing', 'EMPTY', 'WINDOW', []),
    ('Frames', 'EMPTY', 'WINDOW', []),    # frame navigation (per region)
    ('Markers', 'EMPTY', 'WINDOW', []),    # markers (per region)
    ('Animation', 'EMPTY', 'WINDOW', []),    # frame change on click, preview range (per region)
    ('Animation Channels', 'EMPTY', 'WINDOW', []),

    ('View3D Gesture Circle', 'EMPTY', 'WINDOW', []),
    ('Gesture Straight Line', 'EMPTY', 'WINDOW', []),
    ('Gesture Zoom Border', 'EMPTY', 'WINDOW', []),
    ('Gesture Border', 'EMPTY', 'WINDOW', []),

    ('Standard Modal Map', 'EMPTY', 'WINDOW', []),
    ('Transform Modal Map', 'EMPTY', 'WINDOW', []),
    ]
"""


def get_keymap(context, name):
    """
    :type context: bpy.types.Context
    :type name: str
    :rtype: bpy.types.KeyMap
    """
    import bpy_extras.keyconfig_utils

    # これは実際にblenderを起動して値を確認するしか方法が無い
    modal_keymaps = {
        'View3D Gesture Circle',
        'Gesture Border',
        'Gesture Zoom Border',
        'Gesture Straight Line',
        'Standard Modal Map',
        'Knife Tool Modal Map',
        'Transform Modal Map',
        'Paint Stroke Modal',
        'View3D Fly Modal',
        'View3D Walk Modal',
        'View3D Rotate Modal',
        'View3D Move Modal',
        'View3D Zoom Modal',
        'View3D Dolly Modal',
    }

    kc = context.window_manager.keyconfigs.addon
    if not kc:
        return None

    def get(ls, name):
        for keymap_name, space_type, region_type, children in ls:
            if keymap_name == name:
                is_modal = keymap_name in modal_keymaps
                return kc.keymaps.new(keymap_name, space_type=space_type,
                                      region_type=region_type, modal=is_modal)
            elif children:
                km = get(children, name)
                if km:
                    return km

    km = get(bpy_extras.keyconfig_utils.KM_HIERARCHY, name)
    if not km:
        msg = "Keymap '{}' not in builtins".format(name)
        raise ValueError(msg)
    return km


def _dependency_walk(obj, dependency):
    if obj in dependency and dependency[obj][0] is not None:
        return

    def verify(ob, incomplete=False):
        if ob in dependency:
            if not incomplete:
                dependency[ob][0] = []
        else:
            if incomplete:
                dependency[ob] = [None, []]
            else:
                dependency[ob] = [[], []]

    verify(obj)
    for attr, prop in obj.bl_rna.properties.items():
        if attr == 'rna_type':
            continue
        if prop.type == 'POINTER':
            other = getattr(obj, attr)
            if other is not None:
                dependency[obj][0].append((attr, other))
                verify(other, True)
                dependency[other][1].append((obj, attr))
                _dependency_walk(other, dependency)
        elif prop.type == 'COLLECTION':
            other = getattr(obj, attr)
            ob_list = [ob for ob in other if ob is not None]
            if ob_list:
                dependency[obj][0].append((attr, ob_list))
            for i, ob in enumerate(other):
                if ob is not None:
                    verify(ob, True)
                    dependency[ob][1].append((obj, attr, i))
                    _dependency_walk(ob, dependency)


def data_block_dependency():
    """BlendData.user_mapみたいに依存関係を表す辞書を返す
    {obj: [属性名とそのオブジェクトのリスト,
           このオブジェクトが属するオブジェクトとその属性名], ...}
    COLLECTIONならインデックス情報が加わる
    """
    dependency = {}
    _dependency_walk(bpy.data, dependency)
    return dependency


def delete_data_block(data):
    """再起動せずにデータブロックを完全に削除する。

    参考: https://www.blender.org/api/blender_python_api_2_77a_release/
        bpy.types.ID.html#bpy.types.ID.user_clear
    :type data: T
    """
    context = bpy.context
    dependency = data_block_dependency()
    if data.use_fake_user:
        data.use_fake_user = False
    for obj, attr, *index in dependency[data][1]:
        if obj != bpy.data and not index:
            try:
                setattr(obj, attr, None)
                # print('Unlink {} - {}'.format(repr(obj), attr))
            except:
                pass
    if isinstance(data, bpy.types.Screen):
        screens = bpy.data.screens
        windows = []
        for wm in bpy.data.window_managers:
            for win in wm.windows:
                windows.append(win)
        if len(screens) > len(windows):
            for win in windows:
                if win.screen == data:
                    ctx = context.copy()
                    ctx['window'] = win
                    ctx['screen'] = win.screen
                    bpy.ops.screen.screen_set(ctx, delta=-1)
            mapping = bpy.data.user_map([data])  # ID.usersでの判別は不適
            if not mapping[data]:
                if context.screen != data:
                    cur_screen = context.screen
                else:
                    cur_screen = None
                ctx = context.copy()
                ctx['screen'] = data
                bpy.ops.screen.delete(ctx)
                if cur_screen:
                    context.window.screen = cur_screen
                return
    else:
        mapping = bpy.data.user_map([data])
        if not mapping[data]:
            for obj, attr, *index in dependency[data][1]:
                if obj == bpy.data:
                    seq = getattr(bpy.data, attr)
                    seq.remove(data)
                    return

    raise ValueError()
