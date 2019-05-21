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
    'name': 'Lock 3D Cursor',
    'author': 'chromoly',
    'version': (0, 3),
    'blender': (2, 77, 0),
    'location': '3D View',
    'description': 'commit a791153: 3D Cursor: Add option to lock it in place '
                   'to prevent accidental modification',
    'warning': '',
    'wiki_url': 'https://github.com/chromoly/lock_cursor3d',
    'tracker_url': '',
    'category': '3D View'
}

"""
commit a791153ca5e6f87d50396e188a3664b579884161
3D Cursor: Add option to lock it in place to prevent accidental modification

これを再現したものになります

各SpaceView3DのフラグはScreenのIDPropertyに保存されます
"""


import importlib

import bpy

try:
    importlib.reload(utils)
except NameError:
    from . import utils


TARGET_KEYCONFIG = 'Blender'  # or 'Blender User'


space_prop = utils.SpaceProperty(
    [bpy.types.SpaceView3D,
     'lock_cursor_location',
     bpy.props.BoolProperty(
         name='Lock Cursor Location',
         description='3D Cursor location is locked to prevent it from being '
                     'accidentally moved')
     ]
)


class VIEW3D_OT_cursor3d_restrict(bpy.types.Operator):
    bl_idname = 'view3d.cursor3d_restrict'
    bl_label = 'Cursor 3D'
    bl_options = set()

    @classmethod
    def poll(cls, context):
        if bpy.ops.view3d.cursor3d.poll():
            if not context.space_data.lock_cursor_location:
                return True
        return False

    def invoke(self, context, event):
        return bpy.ops.view3d.cursor3d(context.copy(), 'INVOKE_DEFAULT')


draw_func_bak = None


def panel_draw_set():
    global draw_func_bak

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        layout.prop(space_prop.get(view), 'lock_cursor_location')
        col = layout.column()
        col.active = not view.lock_cursor_location
        col.prop(view, 'cursor_location', text='Location')
        if hasattr(view, 'use_cursor_snap_grid'):
            col = layout.column()
            U = context.user_preferences
            col.active = not U.view.use_mouse_depth_cursor
            col.prop(view, "use_cursor_snap_grid", text="Cursor to Grid")

    draw_func_bak = None

    cls = bpy.types.VIEW3D_PT_view3d_cursor
    if hasattr(cls.draw, '_draw_funcs'):
        # bpy_types.py: _GenericUI._dyn_ui_initialize
        for i, func in enumerate(cls.draw._draw_funcs):
            if func.__module__ == cls.__module__:
                cls.draw._draw_funcs[i] = draw
                draw_func_bak = func
                break
    else:
        draw_func_bak = cls.draw
        cls.draw = draw


def panel_draw_restore():
    cls = bpy.types.VIEW3D_PT_view3d_cursor
    if hasattr(cls.draw, '_draw_funcs'):
        if draw_func_bak:
            for i, func in enumerate(cls.draw._draw_funcs):
                if func.__module__ == __name__:
                    cls.draw._draw_funcs[i] = draw_func_bak
    else:
        cls.draw = draw_func_bak


keymap_items = []


@bpy.app.handlers.persistent
def scene_update_pre(scene):
    """起動後に一度だけ実行"""
    kc = bpy.context.window_manager.keyconfigs[TARGET_KEYCONFIG]
    if kc:
        km = kc.keymaps.get('3D View')
        if km:
            for kmi in km.keymap_items:
                if kmi.idname == 'view3d.cursor3d':
                    kmi.idname = 'view3d.cursor3d_restrict'
                    keymap_items.append((km, kmi))
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)


classes = [
    VIEW3D_OT_cursor3d_restrict
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    """
    NOTE: 特定Areaを最大化すると一時的なScreenが生成されるので
    lock_cursor_location属性はScreenでは不適。WindowManagerを使う。
    """
    space_prop.register()

    bpy.app.handlers.scene_update_pre.append(scene_update_pre)

    panel_draw_set()


def unregister():
    panel_draw_restore()

    if scene_update_pre in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(scene_update_pre)

    space_prop.unregister()

    for km, kmi in keymap_items:
        # km.keymap_items.remove(kmi)
        kmi.idname = 'view3d.cursor3d'
    keymap_items.clear()

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
