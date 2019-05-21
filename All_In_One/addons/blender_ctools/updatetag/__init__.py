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
    'name': 'Update Tag',
    'author': 'chromoly',
    'version': (0, 3),
    'blender': (2, 77, 0),
    'location': '',
    'description': '',
    'wiki_url': 'https://github.com/chromoly/blender_update_tag',
    'category': '3D View',
}


"""
1. マテリアルやテクスチャのドライバーの値が変更された時に3DViewを更新
2. Sculptモードでブラシ描画の際にRendered表示の3DViewを更新
"""


from ctypes import Structure, POINTER, cast, \
    c_char, c_char_p, c_short, c_int, c_void_p, py_object
import importlib
import time

import bpy

try:
    importlib.reload(utils)
except NameError:
    pass
from . import utils


class UpdateTagPreferences(
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__

    # マテリアルのドライバの値が変わると更新
    use_material = bpy.props.BoolProperty(
        name='Material',
        default=True,
    )
    # テクスチャのドライバの値が変わると更新
    use_texture = bpy.props.BoolProperty(
        name='Texture',
        default=False,
    )
    # sculptモードの時にブラシ描画でRendered表示を更新
    use_sculpt = bpy.props.BoolProperty(
        name='Sculpt',
        default=False,
    )
    sculpt_interval = bpy.props.FloatProperty(
        name='Interval',
        description='0.0: disable',
        default=0.2,
        min=0.0,
        max=5.0,
        step=10,
        precision=1,
        subtype='TIME',
        unit='TIME',
    )

    def draw(self, context):
        layout = self.layout
        split = layout.split()

        col = split.column()
        col.prop(self, 'use_material')

        col = split.column()
        col.prop(self, 'use_texture')

        col = split.column()
        col.prop(self, 'use_sculpt')
        sub = col.column()
        sub.prop(self, 'sculpt_interval')
        sub.active = self.use_sculpt


class MATERIAL_PT_driver_update_tag(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_label = 'Driver Update Tag'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = UpdateTagPreferences.get_instance()
        return prefs.use_material

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.material, 'use_driver_update_tag', text='Enable')


class TEXTURE_PT_driver_update_tag(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'texture'
    bl_label = 'Driver Update Tag'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        prefs = UpdateTagPreferences.get_instance()
        return prefs.use_texture

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.texture, 'use_driver_update_tag', text='Enable')


###############################################################################
# Material / Texture
###############################################################################
driver_values = {}


def check_drivers(adt):
    do_update = False

    if not adt:
        return do_update

    id_data = adt.id_data  # Material or Texture or ShaderNodeTree

    for driver in adt.drivers:
        if driver.is_valid and not driver.mute:
            if id_data not in driver_values:
                prev_values = driver_values[id_data] = {}
            else:
                prev_values = driver_values[id_data]
            value = id_data.path_resolve(driver.data_path)
            if isinstance(value, (int, float)):
                key = driver.data_path
            else:
                value = value[driver.array_index]
                key = (driver.data_path +
                       '[' + str(driver.array_index) + ']')
            if key in prev_values:
                if value != prev_values[key]:
                    do_update = True
                    prev_values[key] = value
            else:
                prev_values[key] = value
    return do_update


def update_materials():
    for ma in bpy.data.materials:
        if not ma.use_driver_update_tag or ma.is_updated:
            continue

        if check_drivers(ma.animation_data):
            ma.update_tag()
        if ma.use_nodes:
            if check_drivers(ma.node_tree.animation_data):
                ma.update_tag()


def update_textures():
    for tex in bpy.data.textures:
        if not tex.use_driver_update_tag or tex.is_updated:
            continue

        if check_drivers(tex.animation_data):
            tex.update_tag()
        if tex.use_nodes:
            if check_drivers(tex.node_tree.animation_data):
                tex.update_tag()


###############################################################################
# Sculpt
###############################################################################
class ListBase(Structure):
    """source/blender/makesdna/DNA_listBase.h: 59"""
    _fields_ = [
        ('first', c_void_p),
        ('last', c_void_p)
    ]


class wmWindow(Structure):
    """source/blender/makesdna/DNA_windowmanager_types.h: 175"""

wmWindow._fields_ = [
    ('next', POINTER(wmWindow)),
    ('prev', POINTER(wmWindow)),

    ('ghostwin', c_void_p),

    ('screen', c_void_p),  # struct bScreen
    ('newscreen', c_void_p),  # struct bScreen
    ('screenname', c_char * 64),

    ('posx', c_short),
    ('posy', c_short),
    ('sizex', c_short),
    ('sizey', c_short),
    ('windowstate', c_short),
    ('monitor', c_short),
    ('active', c_short),
    ('cursor', c_short),
    ('lastcursor', c_short),
    ('modalcursor', c_short),
    ('grabcursor', c_short),  # GHOST_TGrabCursorMode
    ('addmousemove', c_short),

    ('winid', c_int),

    # internal, lock pie creation from this event until released
    ('lock_pie_event', c_short),
    # exception to the above rule for nested pies, store last pie event for operators
    # that spawn a new pie right after destruction of last pie
    ('last_pie_event', c_short),

    ('eventstate', c_void_p),  # struct wmEvent

    ('curswin', c_void_p),  # struct wmSubWindow

    ('tweak', c_void_p),  # struct wmGesture

    ('ime_data', c_void_p),  # struct wmIMEData

    ('drawmethod', c_int),
    ('drawfail', c_int),
    ('drawdata', ListBase),

    ('queue', ListBase),
    ('handlers', ListBase),
    ('modalhandlers', ListBase),

    ('subwindows', ListBase),
    ('gesture', ListBase),

    ('stereo3d_format', c_void_p),  # struct Stereo3dFormat
]


class wmOperatorType(Structure):
    """source/blender/windowmanager/WM_types.h: 518"""
    _fields_ = [
        ('name', c_char_p),
        ('idname', c_char_p),
        ('translation_context', c_char_p),
        ('description', c_char_p),
    ]


class wmOperator(Structure):
    """source/blender/makesdna/DNA_windowmanager_types.h: 344"""

wmOperator._fields_ = [
    ('next', POINTER(wmOperator)),
    ('prev', POINTER(wmOperator)),

    ('idname', c_char * 64),
    ('properties', c_void_p),  # IDProperty

    ('type', POINTER(wmOperatorType)),
    ('customdata', c_void_p),
    ('py_instance', py_object),  # python stores the class instance here

    ('ptr', c_void_p),  # PointerRNA
    ('reports', c_void_p),  # ReportList

    ('macro', ListBase),
    ('opm', POINTER(wmOperator)),
    ('layout', c_void_p),  # uiLayout
    ('flag', c_short),
    ('pad', c_short * 3)
]


class wmEventHandler(Structure):
    """source/blender/windowmanager/wm_event_system.h: 45"""

wmEventHandler._fields_ = [
    ('next', POINTER(wmEventHandler)),
    ('prev', POINTER(wmEventHandler)),  # struct wmEventHandler

    ('type', c_int),
    ('flag', c_int),

    # keeymap handler
    ('keymap', c_void_p),
    ('bblocal', c_void_p),
    ('bbwin', c_void_p),  # const rcti

    # modal operator handler
    ('op', POINTER(wmOperator)),
    ('op_area', c_void_p),  # struct ScrArea
    ('op_region', c_void_p),  # struct ARegion
    ('op_region_type', c_short),

    # ui handler
    ('ui_handle', c_void_p),  # struct wmUIHandlerFunc
    # wmUIHandlerRemoveFunc ui_remove  # callback when handler is removed
    # void *ui_userdata  # user data pointer
    # struct ScrArea *ui_area  # for derived/modal handlers
    # struct ARegion *ui_region  # for derived/modal handlers
    # struct ARegion *ui_menu  # for derived/modal handlers
    #
    #  # drop box handler
    # ListBase *dropboxes
]


def get_modal_handlers(context):
    window = context.window
    if not window:
        return []

    addr = window.as_pointer()
    win = cast(c_void_p(addr), POINTER(wmWindow)).contents

    handlers = []

    ptr = cast(win.modalhandlers.first, POINTER(wmEventHandler))
    while ptr:
        handler = ptr.contents
        area = handler.op_area  # NULLの場合はNone
        region = handler.op_region  # NULLの場合はNone
        idname = 'UNKNOWN'
        if handler.ui_handle:
            idname = 'UI'
        if handler.op:
            op = handler.op.contents
            ot = op.type.contents
            if ot.idname:
                idname = ot.idname.decode()
        handlers.append((handler, idname, area, region,
                         handler.op_region_type))
        ptr = handler.next

    return handlers


prev_times = {}


def update_sculpt(interval):
    context = bpy.context

    if context.mode != 'SCULPT':
        return

    running = False
    handlers = get_modal_handlers(context)
    for handler, idname, area, region, region_type in handlers:
        if idname == 'SCULPT_OT_brush_stroke':
            running = True

    win = context.window
    if running:
        prev_time = prev_times.setdefault(win, None)
        t = time.perf_counter()
        if prev_time is None:
            prev_times[win] = t
        elif interval != 0.0 and t - prev_time > interval:
            context.active_object.update_tag({'DATA'})
            prev_times[win] = t
    else:
        if win in prev_times:
            context.active_object.update_tag({'DATA'})
            del prev_times[win]


###############################################################################
# Scene Callback
###############################################################################
@bpy.app.handlers.persistent
def callback_scene_update_pre(scene):
    """NOTE: preだとワンテンポ遅れるけどpostだと処理前にupdate_tagのフラグが
    消される
    """
    context = bpy.context
    if context.region:
        return

    prefs = UpdateTagPreferences.get_instance()
    if not prefs:
        return
    if prefs.use_material:
        update_materials()
    if prefs.use_texture:
        update_textures()
    if prefs.use_sculpt:
        update_sculpt(prefs.sculpt_interval)


###############################################################################
# Register
###############################################################################
classes = [
    UpdateTagPreferences,
    MATERIAL_PT_driver_update_tag,
    TEXTURE_PT_driver_update_tag,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Material.use_driver_update_tag = bpy.props.BoolProperty(
            name='Driver Update Tag', default=False)
    bpy.types.Texture.use_driver_update_tag = bpy.props.BoolProperty(
            name='Driver Update Tag', default=False)

    bpy.app.handlers.scene_update_pre.append(callback_scene_update_pre)


def unregister():
    bpy.app.handlers.scene_update_pre.remove(callback_scene_update_pre)

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)

    del bpy.types.Material.use_driver_update_tag
    for ma in bpy.data.materials:
        if ma.get('use_driver_update_tag') is not None:
            del ma['use_driver_update_tag']
    del bpy.types.Texture.use_driver_update_tag
    for tex in bpy.data.textures:
        if tex.get('use_driver_update_tag') is not None:
            del tex['use_driver_update_tag']

    driver_values.clear()
    prev_times.clear()


if __name__ == '__main__':
    register()
