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

# <pep8 compliant>


"""
# Blender Add-on: Reload Add-on
blenderを再起動せずにアドオンを再読み込みする

##  Info Header -> Help -> Reload Addon
メニューから選択したアドオンをリロードする。表示されるのは更新のあった物のみ。

##  UserPreferences -> Header -> Reload
更新のあったアドオンを全てリロード。

##  UserPreferences -> Add-ons -> System: Reload Add-on
初期設定では一秒間隔でファイルの変更を監視し、変更のあったアドオンを画面に表示、そのボタンを押す事でリロードを行う。

Show All で現在有効な全てのアドオンを表示。変更のあった物にはアイコンが付く。

監視は UserPreference -> Add-ons 画面が表示されている場合にのみ働く。
間隔は Time Step で設定。単位は秒。0でこの機能を無効化。
無効化した場合は、Check Update で手動更新する。

Exclude Pattern で監視対象外のディレクトリを正規表現で指定する。
初期状態では \__pycache__ 、 .で始まるディレクトリ、 ~で終わるファイルを無視する。

## Command
Add-onをリロード
```
bpy.ops.wm.addon_reload(module='module_name')
```

更新のあったアドオンを全てリロード
```
bpy.ops.wm.addon_reload_all()
```
"""


import importlib
import os
import re
import sys
import time
import traceback

import bpy
import addon_utils


bl_info = {
    'name': 'Reload Add-on',
    'author': 'chromoly',
    'version': (0, 1),
    'blender': (2, 76, 0),
    'location': 'UserPreferences -> Add-ons -> Reload Add-on, '
                'UserPreferences -> Header -> Reload, '
                'Info -> Header -> Help -> Reload Add-on',
    'description': '',
    'warning': '',
    'wiki_url': '',
    "category": "Learnbgame",
}


# モジュール名をキー、ファイルパスと更新時間で構成される辞書を値とする辞書
module_mtimes = None
""":type: dict[str, dict[str, float]]"""

# 更新されたモジュール名を入れる
module_updated = set()

# 自動更新した時間
prev_time = time.time()


class ReloadAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_all = bpy.props.BoolProperty(
        name='Show All',
        default=False,
    )
    check_interval = bpy.props.IntProperty(
        name='Time Step',
        description='Interval in seconds between update check'
                    '(Available only if display UserPreferences->Add-ons)',
        min=0,
        max=60,
        default=1,
        subtype='TIME'
    )
    exclude_pattern = bpy.props.StringProperty(
        name='Exclude Pattern',
        description='Regular expression pattern',
        default='((.*{s})?__pycache__|(.*{s})?\..*|.*~$)'.format(s=os.sep),
    )

    def draw(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""
        column = layout.column()

        split = column.split(0.15)
        row = split.row()
        row.prop(self, 'show_all')
        row = split.row()
        row.operator('wm.addon_check_update', icon='FILE_REFRESH')
        row.prop(self, 'check_interval')
        row.prop(self, 'exclude_pattern')

        flow = column.column_flow(2)

        addons = context.user_preferences.addons
        if self.show_all:
            module_names = list(addons.keys())
        else:
            module_names = [addon.module for addon in addons
                     if addon.module in module_updated]

        def sort_func(name):
            if name in sys.modules:
                return addon_utils.module_bl_info(sys.modules[name])['name']
            else:
                return name
        module_names.sort(key=sort_func)

        for module_name in module_names:
            if module_name == __name__:
                continue
            row = flow.row()
            if module_name in module_updated:
                icon = 'FILE_REFRESH'
            else:
                icon = 'NONE'
            if module_name in sys.modules:
                mod = sys.modules[module_name]
                name = addon_utils.module_bl_info(mod)['name']
            else:
                name = module_name
            op = row.operator('wm.addon_reload', text=name, icon=icon)
            op.module = module_name

    @classmethod
    def get_prefs(self):
        return bpy.context.user_preferences.addons[__name__].preferences


def get_module_mtimes(module_name=None):
    prefs = ReloadAddonPreferences.get_prefs()
    pattern = prefs.exclude_pattern

    mod_mtimes = {}
    for addon in bpy.context.user_preferences.addons:
        mod_name = addon.module
        if module_name and module_name != mod_name:
            continue
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
        else:
            try:
                importlib.import_module(mod_name)
            except:
                traceback.print_exc()
                mod_mtimes[mod_name] = {}
                continue
        mtimes = {}
        if hasattr(mod, '__path__'):
            for mod_path in mod.__path__:
                for root, dirs, files in os.walk(mod_path):
                    for d in list(dirs):
                        p = os.path.join(root, d)
                        relpath = os.path.relpath(p, mod_path)
                        if re.match(pattern, relpath):
                            dirs.remove(d)
                    for file in files:
                        path = os.path.join(root, file)
                        relpath = os.path.relpath(path, mod_path)
                        if re.match(pattern, relpath):
                            continue
                        mtimes[path] = os.path.getmtime(path)
        else:
            path = mod.__file__
            mtimes[path] = os.path.getmtime(path)
        mod_mtimes[mod_name] = mtimes
    return mod_mtimes


def check_update():
    global module_mtimes, prev_time
    updated = False
    if module_mtimes is None:
        module_mtimes = get_module_mtimes()
    else:
        mtimes = get_module_mtimes()
        for mod_name, d in mtimes.items():
            if mod_name in module_mtimes:
                if d != module_mtimes[mod_name]:
                    module_updated.add(mod_name)
                    updated = True
            else:
                module_updated.add(mod_name)
                updated = True
        module_mtimes.update(mtimes)
    prev_time = time.time()
    return updated


def reload_addon(context, module_name):
    addons = context.user_preferences.addons
    if module_name not in addons:
        return False

    addon = addons[module_name]
    module_name = addon.module
    if module_name in sys.modules:
        mod = sys.modules[module_name]
        try:
            mod.unregister()
        except:
            traceback.print_exc()
        del mod
    ccc = []

    for km, kmi in ccc:
        km.keymap_items.remove(kmi)
    # ccc.clear()


    for key in list(sys.modules):
        if key == module_name or key.startswith(module_name + '.'):
            del sys.modules[key]

    bpy.ops.wm.addon_refresh()
    try:
        mod = importlib.import_module(module_name)
        mod.register()
    except:
        # for key in list(sys.modules):
        #     if key == module_name or key.startswith(module_name + '.'):
        #         del sys.modules[key]
        # bpy.ops.wm.addon_disable(module=module_name)
        traceback.print_exc()
        return False

    mtimes = get_module_mtimes(module_name)
    module_mtimes[module_name] = mtimes[module_name]
    if module_name in module_updated:
        module_updated.remove(module_name)
    print("Reload '{}'".format(module_name))
    return True


def redraw_userprefs(context):
    if context.user_preferences.active_section == 'ADDONS':
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'USER_PREFERENCES':
                    area.tag_redraw()


class WM_OT_addon_check_update(bpy.types.Operator):
    bl_idname = 'wm.addon_check_update'
    bl_label = 'Check Update'

    def execute(self, context):
        check_update()
        redraw_userprefs(context)
        return {'FINISHED'}


class WM_OT_addon_reload(bpy.types.Operator):
    bl_idname = 'wm.addon_reload'
    bl_label = 'Reload Add-on'
    bl_description = 'Reload add-on'

    module = bpy.props.StringProperty(name='Module Name')

    def execute(self, context):
        if not reload_addon(context, self.module):
            return {'CANCELLED'}

        redraw_userprefs(context)
        return {'FINISHED'}


class WM_OT_addon_reload_all(bpy.types.Operator):
    bl_idname = 'wm.addon_reload_all'
    bl_label = 'Reload Add-ons'
    bl_description = 'Reload updated add-ons'

    def execute(self, context):
        addons = context.user_preferences.addons
        check_update()
        result = False
        for addon in addons:
            if addon.module in module_updated:
                result |= reload_addon(context, addon.module)
        if not result:
            return {'CANCELLED'}

        redraw_userprefs(context)
        return {'FINISHED'}


@bpy.app.handlers.persistent
def scene_update_pre(scene):
    global module_mtimes, prev_time

    context = bpy.context

    # メインループからの呼び出しの場合は必ずNoneになる
    if context.region:
        return

    if module_mtimes is None:
        check_update()
    else:
        prefs = ReloadAddonPreferences.get_prefs()
        if prefs.check_interval == 0:
            return
        if time.time() - prev_time > prefs.check_interval:
            if context.user_preferences.active_section == 'ADDONS':
                for win in context.window_manager.windows:
                    for area in win.screen.areas:
                        if area.type == 'USER_PREFERENCES':
                            updated = check_update()
                            if updated:
                                area.tag_redraw()
                            return


def userprefs_header_draw(self, context):
    layout = self.layout
    if context.user_preferences.active_section == 'ADDONS':
        layout.operator('wm.addon_reload_all', text='Reload',
                        icon='FILE_REFRESH')


class INFO_MT_help_addon_reload(bpy.types.Menu):
    bl_idname = 'INFO_MT_help_addon_reload'
    bl_label = 'Reload Add-on'

    def draw(self, context):
        layout = self.layout
        check_update()

        addons = context.user_preferences.addons
        module_names = [addon.module for addon in addons
                        if addon.module in module_updated]

        def sort_func(name):
            if name in sys.modules:
                return addon_utils.module_bl_info(sys.modules[name])['name']
            else:
                return name
        module_names.sort(key=sort_func)

        for module_name in module_names:
            if module_name == __name__:
                continue
            if module_name in sys.modules:
                mod = sys.modules[module_name]
                name = addon_utils.module_bl_info(mod)['name']
                text = name + ' (' + sys.modules[module_name].__file__ + ')'
            else:
                text = module_name
            op = layout.operator('wm.addon_reload', text=text)
            op.module = module_name


def info_menu_draw(self, context):
    layout = self.layout
    layout.menu('INFO_MT_help_addon_reload', icon='FILE_REFRESH')


classes = [
    WM_OT_addon_check_update,
    WM_OT_addon_reload,
    WM_OT_addon_reload_all,
    INFO_MT_help_addon_reload,
    ReloadAddonPreferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.scene_update_pre.append(scene_update_pre)
    bpy.types.USERPREF_HT_header.append(userprefs_header_draw)
    bpy.types.INFO_MT_help.append(info_menu_draw)


def unregister():
    bpy.types.USERPREF_HT_header.remove(userprefs_header_draw)
    bpy.types.INFO_MT_help.remove(info_menu_draw)
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
