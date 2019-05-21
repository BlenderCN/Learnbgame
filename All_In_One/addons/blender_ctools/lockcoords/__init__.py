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


bl_info = {
    'name': 'Lock Coordinates',
    'author': 'chromoly',
    'version': (0, 2, 3),
    'blender': (2, 77, 0),
    'location': 'View3D > ToolShelf > Lock Coordinates, '
                'View3D > Header, '
                'View3D > Ctrl + V > Lock, '
                'View3D > Ctrl + Shift + L',
    'description': 'Lock vertices coordinates in mesh edit mode',
    'wiki_url': 'https://github.com/chromoly/blender_lock_coords',
    'category': 'Mesh',
}


"""
Mesh編集中に頂点座標を固定・選択不可にするアドオン。
レンダリング中は動作しない。

副作用：
それなりの負荷がかかる。
bpy.ops.mesh.sort_elements()で頂点の順番が並び替えられる。
頂点レイヤーを使うのでファイルサイズが増加する。int型なので最大で頂点数x4バイト？
"""


import ctypes
import importlib
import platform
import time

import bpy
import bmesh
from mathutils import Vector

try:
    importlib.reload(utils)
except NameError:
    from . import utils


# BMLayerItem name
# 他のアドオンと衝突するようなら変更する
LAYER_LOCK = 'use_lock'  # verts.layers.int
LAYER_X = 'lock_x'  # verts.layers.float
LAYER_Y = 'lock_y'  # verts.layers.float
LAYER_Z = 'lock_z'  # verts.layers.float
LAYER_GX = 'lock_global_x'  # verts.layers.float 0.2.0でのみ使用
LAYER_GY = 'lock_global_y'  # verts.layers.float 0.2.0でのみ使用
LAYER_GZ = 'lock_global_z'  # verts.layers.float 0.2.0でのみ使用
LAYER_TMP_SELECT = '_select'  # [verts|edges|faces].layers.int
LAYER_TMP_HISTORY = '_history'  # [verts|edges|faces].layers.int
LAYER_TMP_ACTIVE = '_active'  # faces.layers.int

# (type, context.ATTR, bpy.data.ATTR)
PREFS_LOCATION = (bpy.types.Scene, 'scene', 'scenes')
# PREFS_LOCATION = (bpy.types.WindowManager, 'window_manager', 'window_managers')

# ロックした頂点を選択不可にするオプションの初期値
DEFAULT_SELECTABLE = False

# メニュー呼び出しに使うショートカット
MENU_KEYMAPS = (
    {'type': 'L', 'value': 'PRESS', 'shift': True, 'ctrl': True},
    {'type': 'BUTTON16MOUSE', 'value': 'PRESS', 'shift': True, 'ctrl': True},
)

# 頂点選択が無効になっている時の速度低下の軽減(linuxのみ)
USE_CTYPES = True


###############################################################################
# Callback
###############################################################################
if platform.system().lower() not in {'darwin', 'windows'}:
    # 'linux'
    blend_cdll = ctypes.CDLL('')
else:
    blend_cdll = None


def scene_update(scene):
    """コールバックを無効化した状態でscene.update()を実行する。
    使用例:
        import lockcoords
        lockcoords.scene_update(scene)

    :type scene: bpy.types.Scene
    """

    func = callback_scene_update_pre
    seq = bpy.app.handlers.scene_update_pre
    added = func in seq
    if added:
        seq.remove(func)
    scene.update()
    if added:
        seq.append(func)


def get_prefs(context):
    obj = getattr(context, PREFS_LOCATION[1])
    return getattr(obj, 'lock_coords', None)


def check_callback():
    """必要に応じて追加と削除を行う"""
    enable = False
    for obj in getattr(bpy.data, PREFS_LOCATION[2]):
        if obj.lock_coords.enable:
            enable = True
    seq = bpy.app.handlers.scene_update_pre
    if enable:
        if callback_scene_update_pre not in seq:
            seq.append(callback_scene_update_pre)
    else:
        if callback_scene_update_pre in seq:
            seq.remove(callback_scene_update_pre)


# Mesh編集中のsceneを格納する
edit_mesh_scenes = set()


def get_layer(bm, type, name):
    if type == float:
        layers = bm.verts.layers.float
    elif type == int:
        layers = bm.verts.layers.int
    else:
        return None
    layer = layers.get(name)
    if not layer:
        layer = layers.new(name)
    return layer


def relock(bm=None):
    """頂点のロック座標を現在の座標で上書きする"""
    if not bm:
        if bpy.context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
        else:
            return
    layer_lock = bm.verts.layers.int.get(LAYER_LOCK)
    if not layer_lock:
        return
    layer_x = get_layer(bm, float, LAYER_X)
    layer_y = get_layer(bm, float, LAYER_Y)
    layer_z = get_layer(bm, float, LAYER_Z)
    for eve in bm.verts:
        if eve[layer_lock]:
            eve[layer_x], eve[layer_y], eve[layer_z] = eve.co


@bpy.app.handlers.persistent
def callback_load_post(dummy):
    """ファイルのロード後に実行"""
    edit_mesh_scenes.clear()
    check_callback()


@bpy.app.handlers.persistent
def callback_save_pre(dummy):
    """ファイルのセーブ前に実行。ロック座標用の頂点レイヤーを削除"""
    for me in bpy.data.meshes:
        if me.is_editmode:
            bm = bmesh.from_edit_mesh(me)
        else:
            skip = True
            if LAYER_LOCK in me.vertex_layers_int:
                skip = False
            for name in (LAYER_X, LAYER_Y, LAYER_Z,
                         LAYER_GX, LAYER_GY, LAYER_GZ):
                if name in me.vertex_layers_float:
                    skip = False
            if skip:
                continue
            bm = bmesh.new()
            bm.from_mesh(me)
        for name in (LAYER_X, LAYER_Y, LAYER_Z):
            layer = bm.verts.layers.float.get(name)
            if layer:
                bm.verts.layers.float.remove(layer)
        # 0.2.0で追加した分
        for name in (LAYER_GX, LAYER_GY, LAYER_GZ):
            layer = bm.verts.layers.float.get(name)
            if layer:
                bm.verts.layers.float.remove(layer)
        if not me.is_editmode:
            bm.to_mesh(me)


@bpy.app.handlers.persistent
def callback_save_post(dummy):
    """editmode中のメッシュに対しcallback_save_preで消したレイヤを追加する"""
    for me in bpy.data.meshes:
        if me.is_editmode:
            bm = bmesh.from_edit_mesh(me)
            relock(bm)


@bpy.app.handlers.persistent
def callback_scene_update_pre(scene):
    """meshに変更が無くても絶えず呼び出す。

    NOTE:
    Object.is_updated_dataはselectやdeselectでは真にならない。
    scene_update_postではmodifierに対応出来ない。
    """

    t = time.perf_counter()

    check_callback()

    context = bpy.context

    """
    NOTE: regionはメインループの際に必ずNoneになる。wm_event_do_notifiers()参照
    """
    if context.region:
        return

    scenes = tuple(bpy.data.scenes)
    for scn in tuple(edit_mesh_scenes):
        if scn not in scenes:
            edit_mesh_scenes.remove(scn)
    if scene:
        if context.mode == 'EDIT_MESH':
            if scene not in edit_mesh_scenes:
                relock()
                edit_mesh_scenes.add(scene)
        else:
            if scene in edit_mesh_scenes:
                edit_mesh_scenes.remove(scene)
            return
    else:
        return

    lock_coords = get_prefs(context)
    if not lock_coords.enable:
        return

    lock_axis = tuple(lock_coords.lock_axis)
    if not any(lock_axis):
        return
    lock_x, loc_y, lock_z = lock_axis
    lock_all = all(lock_axis)
    is_selectable = lock_coords.is_selectable
    use_local_coords = lock_coords.lock_coordinate_system == 'LOCAL'

    actob = context.active_object
    mesh = actob.data
    mat = actob.matrix_world
    imat = mat.inverted()

    bm = bmesh.from_edit_mesh(mesh)  # 所要時間は1e-5程度

    layer_lock = bm.verts.layers.int.get(LAYER_LOCK)
    if not layer_lock:
        return
    layer_x = bm.verts.layers.float.get(LAYER_X)
    layer_y = bm.verts.layers.float.get(LAYER_Y)
    layer_z = bm.verts.layers.float.get(LAYER_Z)
    if not (layer_x and layer_y and layer_z):
        return

    do_select_update = False
    for eve in bm.verts:
        if not eve.hide and eve[layer_lock]:
            x = eve[layer_x]
            y = eve[layer_y]
            z = eve[layer_z]
            if use_local_coords:
                if lock_all:
                    eve.co = x, y, z
                else:
                    co = eve.co
                    if lock_x:
                        co[0] = x
                    if loc_y:
                        co[1] = y
                    if lock_z:
                        co[2] = z
            else:
                lock_co = mat * Vector((x, y, z))
                if lock_all:
                    eve.co = imat * lock_co
                else:
                    co = mat * eve.co
                    if lock_x:
                        co[0] = lock_co[0]
                    if loc_y:
                        co[1] = lock_co[1]
                    if lock_z:
                        co[2] = lock_co[2]
                    eve.co = imat * co
            if not is_selectable:
                if eve.select:
                    eve.select = False
                    do_select_update = True

    """
    NOTE:
    select_flush(True):
        edgeループ(flag:頂点)の後faceループ(flag:頂点)
        flag対象の全てが選択中の場合のみ適用
    select_flush(False):
        edgeループ(flag:頂点)とその中でloopを回してfaceを非選択へ(flag:辺)
        flag対象のいずれかが非選択なら適用
    select_flush_mode():
        選択モードはbm.select_modeを参照する
        if vert選択が有効: edge(flag:頂点)とface(flag:頂点)をループ。
        elif edge選択が有効: face(flag:辺)をループ。
    """

    if do_select_update:
        # EDBM_selectmode_toggleの中で呼び出すのはbm.select_flush(True)に当たる
        # ものなのでbm.select_flush(False)は必須
        bm.select_flush(False)
        ts = context.tool_settings
        select_mode = list(ts.mesh_select_mode)
        if select_mode[0]:
            pass
        elif blend_cdll:
            C = ctypes.c_void_p(context.as_pointer())
            if select_mode[0]:
                mode = 1
            elif select_mode[1]:
                mode = 2
            else:
                mode = 4
            # EDBM_selectmode_toggle(C, type, action, use_extend, use_expand)
            # 3DViewヘッダのボタンは下記のような引数で実行する
            # EDBM_selectmode_toggle(C, SCE_SELECT_VERTEX, -1, shift, ctrl)
            blend_cdll.EDBM_selectmode_toggle(C, mode, -1, False, False)
        else:
            # EDBM_selectmode_set()参照
            if select_mode[1]:
                for v in bm.verts:
                    v.select = False
                for e in bm.edges:
                    if e.select:
                        # hideフラグの判定は代入時にやってくれるので不要
                        e.select = e.select
            else:
                for e in bm.edges:
                    e.select = False
                for f in bm.faces:
                    if f.select:
                        # hideフラグの判定は代入時にやってくれるので不要
                        f.select = True

    bm.normal_update()
    if mesh.is_updated or mesh.is_updated_data:
        bmesh.update_edit_mesh(mesh, tessface=True)

    # print(time.perf_counter() - t)


###############################################################################
# Prorerty
###############################################################################
def prop_update(self, context):
    if context.mode == 'EDIT_MESH':
        lockcoords = get_prefs(context)
        if lockcoords.enable:
            relock()
            if lockcoords.is_selectable:
                bpy.ops.mesh.lock_coords_sort_order()

        # 面選択モード時の面中心に表示されているドットを更新する為
        context.active_object.data.update_tag()

        area = context.area
        if area and area.type == 'VIEW_3D':
            area.tag_redraw()


def prop_update_enable(self, context):
    check_callback()
    prop_update(self, context)


class WM_PROP_LockCoords(bpy.types.PropertyGroup):
    """bpy.types.WindowManager.lock_coords"""
    enable = bpy.props.BoolProperty(
            name='Enable',
            description='Lock vertices coordinates',
            default=False,
            update=prop_update_enable)
    is_selectable = bpy.props.BoolProperty(
            name='Selectable',
            default=DEFAULT_SELECTABLE,
            update=prop_update)
    lock_axis = bpy.props.BoolVectorProperty(
            name='Lock Axis',
            description='Lock axis',
            default=(True, True, True),
            subtype='XYZ', size=3,
            update=prop_update)
    lock_coordinate_system = bpy.props.EnumProperty(
            name='Coordinate System',
            items=(('GLOBAL', 'Global',
                    'Lock with global coordinate system (slower)'),
                   ('LOCAL', 'Local', 'Lock with local coordinate system')),
            default='LOCAL',
            update=prop_update)


###############################################################################
# Operator
###############################################################################
class MESH_OT_lock_coords(bpy.types.Operator):
    bl_description = 'Lock vertex coordinates'
    bl_idname = 'mesh.lock_coords'
    bl_label = 'Lock Coordinates'

    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.EnumProperty(
            name='Lock',
            items=(('LOCK_SEL', 'Lock Selected', ''),
                   ('LOCK_DESEL', 'Lock Deselected', ''),
                   ('UNLOCK_SEL', 'Unlock Selected', ''),
                   ('UNLOCK_DESEL', 'Unlock Deselected', ''),
                   ('UNLOCK_ALL', 'Unlock All', ''),
                   ('INVERT', 'Inverse', ''),
                   ('RELOCK', 'Relock',
                    'Copy current coordinates to locking coordinates'),
                   ),
            default='LOCK_SEL')

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        actob = context.active_object
        bm = bmesh.from_edit_mesh(actob.data)

        layer_lock = get_layer(bm, int, LAYER_LOCK)
        layer_x = get_layer(bm, float, LAYER_X)
        layer_y = get_layer(bm, float, LAYER_Y)
        layer_z = get_layer(bm, float, LAYER_Z)
        for eve in bm.verts:
            if eve.hide:
                continue
            set_lock_co = False
            if self.mode in ('LOCK_SEL', 'LOCK_DESEL'):
                if self.mode == 'LOCK_SEL' and eve.select or \
                   self.mode == 'LOCK_DESEL' and not eve.select:
                    eve[layer_lock] = 1
                    set_lock_co = True
            elif self.mode in ('UNLOCK_SEL', 'UNLOCK_DESEL'):
                if self.mode == 'UNLOCK_SEL' and eve.select or \
                   self.mode == 'UNLOCK_DESEL' and not eve.select:
                    eve[layer_lock] = 0
            elif self.mode == 'UNLOCK_ALL':
                eve[layer_lock] = 0
            elif self.mode == 'INVERT':
                if eve[layer_lock]:
                    eve[layer_lock] = 0
                else:
                    eve[layer_lock] = 1
                    set_lock_co = True
            elif self.mode == 'RELOCK':
                if eve[layer_lock] and eve.select:
                    set_lock_co = True
            if set_lock_co:
                eve[layer_x], eve[layer_y], eve[layer_z] = eve.co

        del bm  # ↓のオペレータの為に参照カウンタを0にする必要がある
        bpy.ops.mesh.lock_coords_sort_order()

        actob.data.update_tag()
        context.area.tag_redraw()

        return {'FINISHED'}


class MESH_OT_lock_coords_sort_order(bpy.types.Operator):
    """Selectableを無効にした状態で重なった頂点を選択する場合、
    始めにマッチする頂点がロックしたものだと、他の頂点が選択出来なくなる。
    (選択 -> scene_update_preで非選択 -> 同じ頂点を選択 の繰り返しになる為)
    これを回避する為に非ロックの頂点をシーケンスの前に持ってくる。

    ※注意！！
    bpy.ops.mesh.sort_elements()を実行すると、それ以前にbmesh.from_edit_mesh()
    で作成していたインスタンスのvertsをforループで回すとbyte文字列が混じる
    というバグが発生する。
    対策は参照カウンタを0にしてデストラクタ関数を呼び
    (bm->py_handleがNULとなる)、bmesh.from_edit_mesh()で
    新規オブジェクトが作成されるようにする事。
    bm.verts.sort(key=lambda elem: int(not elem.select))でも同様の不具合が
    発生する。
    """

    bl_description = 'Sort order of vertices. ' \
                     'Needed for when Selectable is disabled'
    bl_idname = 'mesh.lock_coords_sort_order'
    bl_label = 'Sort Order'

    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        layer_lock = bm.verts.layers.int.get(LAYER_LOCK)
        if not layer_lock:
            return {'CANCELLED'}

        layer_select_v = bm.verts.layers.int.new(LAYER_TMP_SELECT)
        layer_select_e = bm.edges.layers.int.new(LAYER_TMP_SELECT)
        layer_select_f = bm.faces.layers.int.new(LAYER_TMP_SELECT)
        for elem in bm.verts:
            if elem.select:
                elem[layer_select_v] = 1
        for elem in bm.edges:
            if elem.select:
                elem[layer_select_e] = 1
        for elem in bm.faces:
            if elem.select:
                elem[layer_select_f] = 1

        has_select_history = bool(bm.select_history)
        has_active_face = bool(bm.faces.active)
        if has_select_history:
            layer_history_v = bm.verts.layers.int.new(LAYER_TMP_HISTORY)
            layer_history_e = bm.edges.layers.int.new(LAYER_TMP_HISTORY)
            layer_history_f = bm.faces.layers.int.new(LAYER_TMP_HISTORY)
            for i, elem in enumerate(bm.select_history):
                if isinstance(elem, bmesh.types.BMVert):
                    layer = layer_history_v
                elif isinstance(elem, bmesh.types.BMEdge):
                    layer = layer_history_e
                else:
                    layer = layer_history_f
                elem[layer] = i + 1
        if has_active_face:
            layer_active_f = bm.faces.layers.int.new(LAYER_TMP_ACTIVE)
            bm.faces.active[layer_active_f] = 1

        # select only non locked
        bpy.ops.mesh.select_all(action='DESELECT')
        for eve in bm.verts:
            if not eve[layer_lock] and not eve.hide:
                eve.select = True

        del bm

        # sort
        bpy.ops.mesh.sort_elements(type='SELECTED', elements={'VERT'})

        # restore
        bpy.ops.mesh.select_all(action='DESELECT')

        bm = bmesh.from_edit_mesh(context.active_object.data)
        layer_select_v = bm.verts.layers.int.get(LAYER_TMP_SELECT)
        layer_select_e = bm.edges.layers.int.get(LAYER_TMP_SELECT)
        layer_select_f = bm.faces.layers.int.get(LAYER_TMP_SELECT)
        for elem in bm.verts:
            if elem[layer_select_v]:
                elem.select = True
        for elem in bm.edges:
            if elem[layer_select_e]:
                elem.select = True
        for elem in bm.faces:
            if elem[layer_select_f]:
                elem.select = True

        bm.verts.layers.int.remove(layer_select_v)
        bm.edges.layers.int.remove(layer_select_e)
        bm.faces.layers.int.remove(layer_select_f)

        bm.select_history.clear()
        if has_select_history:
            layer_history_v = bm.verts.layers.int.get(LAYER_TMP_HISTORY)
            layer_history_e = bm.edges.layers.int.get(LAYER_TMP_HISTORY)
            layer_history_f = bm.faces.layers.int.get(LAYER_TMP_HISTORY)
            history = {}
            for elem in bm.verts:
                i = elem[layer_history_v]
                if i > 0:
                    history[i] = elem
            for elem in bm.edges:
                i = elem[layer_history_e]
                if i > 0:
                    history[i] = elem
            for elem in bm.faces:
                i = elem[layer_history_f]
                if i > 0:
                    history[i] = elem
            history = sorted(history.items(), key=lambda x: x[0])
            for i, elem in history:
                bm.select_history.add(elem)

            bm.verts.layers.int.remove(layer_history_v)
            bm.edges.layers.int.remove(layer_history_e)
            bm.faces.layers.int.remove(layer_history_f)

        if has_active_face:
            layer_active_f = bm.faces.layers.int.get(LAYER_TMP_ACTIVE)
            for elem in bm.faces:
                if elem[layer_active_f]:
                    bm.faces.active = elem
                    break

            bm.faces.layers.int.remove(layer_active_f)

        # bm.select_flush(False)  # 要るか？
        # bm.normal_update()

        context.active_object.data.update_tag()

        return {'FINISHED'}


class MESH_OT_lock_coords_select(bpy.types.Operator):
    bl_description = ''
    bl_idname = 'mesh.lock_coords_select'
    bl_label = 'Select Locked'

    target = bpy.props.EnumProperty(
        items=(('LOCKED', 'Locked', ''),
               ('NON_LOCKED', 'Non Locked', ''),
               ),
        default='LOCKED'
    )

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        layer_lock = bm.verts.layers.int.get(LAYER_LOCK)
        if self.target == 'LOCKED' and not layer_lock:
            return {'CANCELLED'}
        for eve in bm.verts:
            if not eve.hide:
                if self.target == 'LOCKED':
                    if eve[layer_lock]:
                        eve.select = True
                else:
                    if not layer_lock or not eve[layer_lock]:
                        eve.select = True
        bm.select_flush(True)
        context.area.tag_redraw()
        return {'FINISHED'}


###############################################################################
# Panel
###############################################################################
class MESH_PT_LockCoords(bpy.types.Panel):
    bl_idname = 'MESH_PT_lock_coords'
    bl_label = 'Lock Coordinates'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def draw(self, context):
        lock_coords = get_prefs(context)

        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        col = layout.column()
        col.prop(lock_coords, 'enable')

        col = layout.column(align=True)
        # col.operator_enum('mesh.lock_coords', 'mode')
        op = col.operator('mesh.lock_coords', text='Lock')
        op.mode = 'LOCK_SEL'
        op = col.operator('mesh.lock_coords', text='Unlock')
        op.mode = 'UNLOCK_SEL'
        op = col.operator('mesh.lock_coords', text='Unlock All')
        op.mode = 'UNLOCK_ALL'
        op = col.operator('mesh.lock_coords', text='Inverse')
        op.mode = 'INVERT'
        # op = col.operator('mesh.lock_coords', text='Relock')
        # op.mode = 'RELOCK'

        col = layout.column(align=True)
        col.prop(lock_coords, 'is_selectable')
        col.operator('mesh.lock_coords_sort_order')

        # col = layout.column(align=True)
        # op = col.operator('mesh.lock_coords_select')
        # op.target = 'LOCKED'
        # op = col.operator('mesh.lock_coords_select', text='Select Non Locked')
        # op.target = 'NON_LOCKED'

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(lock_coords, 'lock_axis', text='X', toggle=True, index=0)
        row.prop(lock_coords, 'lock_axis', text='Y', toggle=True, index=1)
        row.prop(lock_coords, 'lock_axis', text='Z', toggle=True, index=2)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(lock_coords, 'lock_coordinate_system', expand=True)

    # def draw_header(self, context):
    #     self.layout.prop(get_prefs(context), 'enable', text='')


###############################################################################
# Menu
###############################################################################
class VIEW3D_MT_edit_mesh_lock_coords(bpy.types.Menu):
    bl_description = ''
    bl_idname = 'VIEW3D_MT_edit_mesh_lock_coords'
    bl_label = 'Lock Coordinates'

    def draw(self, context):
        lock_coords = get_prefs(context)

        layout = self.layout

        layout.prop(lock_coords, 'enable')

        layout.separator()
        # layout.operator_enum('mesh.lock_coords', 'mode')
        op = layout.operator('mesh.lock_coords', text='Lock Selected')
        op.mode = 'LOCK_SEL'
        op = layout.operator('mesh.lock_coords', text='Unlock Selected')
        op.mode = 'UNLOCK_SEL'
        op = layout.operator('mesh.lock_coords', text='Unlock All')
        op.mode = 'UNLOCK_ALL'
        op = layout.operator('mesh.lock_coords', text='Inverse All')
        op.mode = 'INVERT'
        # op = layout.operator('mesh.lock_coords', text='Relock Selected')
        # op.mode = 'RELOCK'

        layout.separator()
        col = layout.column()
        col.prop(lock_coords, 'is_selectable')
        col.operator('mesh.lock_coords_sort_order')

        # layout.separator()
        # op = layout.operator('mesh.lock_coords_select')
        # op.target = 'LOCKED'
        # op = layout.operator('mesh.lock_coords_select',
        #                      text='Select Non Locked')
        # op.target = 'NON_LOCKED'

        layout.separator()
        layout.prop(lock_coords, 'lock_axis', text='Lock X', index=0)
        layout.prop(lock_coords, 'lock_axis', text='Lock Y', index=1)
        layout.prop(lock_coords, 'lock_axis', text='Lock Z', index=2)

        layout.separator()
        # layout.props_enum(lock_coords, 'lock_coordinate_system')
        layout.prop_enum(lock_coords, 'lock_coordinate_system', 'GLOBAL',
                         text='Global Coordinates')
        layout.prop_enum(lock_coords, 'lock_coordinate_system', 'LOCAL',
                         text='Local Coordinates')


def menu_function(self, context):
    self.layout.menu('VIEW3D_MT_edit_mesh_lock_coords', text='Lock')


def draw_header(self, context):
    if context.mode != 'EDIT_MESH':
        return
    lock_coords = get_prefs(context)
    icon = 'LOCKED' if lock_coords.enable else 'UNLOCKED'
    self.layout.prop(lock_coords, 'enable', icon=icon, text='')


###############################################################################
# AddonPreferences
###############################################################################
class LockCoordsPreferences(
        utils.AddonKeyMapUtility,
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__


###############################################################################
# Register
###############################################################################
classes = [
    MESH_OT_lock_coords,
    MESH_OT_lock_coords_sort_order,
    MESH_OT_lock_coords_select,
    WM_PROP_LockCoords,
    MESH_PT_LockCoords,
    VIEW3D_MT_edit_mesh_lock_coords,
    LockCoordsPreferences,
]

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    setattr(PREFS_LOCATION[0],
            'lock_coords',
            bpy.props.PointerProperty(
                    name='Lock Coordinates', type=WM_PROP_LockCoords))
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_function)
    bpy.types.VIEW3D_HT_header.append(draw_header)

    bpy.app.handlers.load_post.append(callback_load_post)
    bpy.app.handlers.save_pre.append(callback_save_pre)
    bpy.app.handlers.save_post.append(callback_save_post)
    bpy.app.handlers.scene_update_pre.append(callback_scene_update_pre)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new('Mesh', space_type='EMPTY',
                            region_type='WINDOW', modal=False)
        for kwargs in MENU_KEYMAPS:
            try:
                kmi = km.keymap_items.new('wm.call_menu', **kwargs)
                kmi.properties.name = 'VIEW3D_MT_edit_mesh_lock_coords'
                addon_keymaps.append((km, kmi))
            except:
                # import traceback
                # traceback.print_exc()
                pass
        addon_prefs = LockCoordsPreferences.get_instance()
        """:type: LockCoordsPreferences"""
        addon_prefs.register_keymap_items(addon_keymaps)


def unregister():
    try:
        delattr(PREFS_LOCATION[0], 'lock_coords')
    except:
        pass
    for obj in getattr(bpy.data, PREFS_LOCATION[2]):
        if obj.get('lock_coords') is not None:
            del obj['lock_coords']

    addon_prefs = LockCoordsPreferences.get_instance()
    """:type: LockCoordsPreferences"""
    addon_prefs.unregister_keymap_items()

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_function)
    bpy.types.VIEW3D_HT_header.remove(draw_header)

    bpy.app.handlers.load_post.remove(callback_load_post)
    bpy.app.handlers.save_pre.remove(callback_save_pre)
    bpy.app.handlers.save_post.remove(callback_save_post)
    if callback_scene_update_pre in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(callback_scene_update_pre)


if __name__ == '__main__':
    register()
