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
    'name': 'CTools',
    'author': 'chromoly',
    'version': (1, 4),
    'blender': (2, 77, 0),
    'location': '',
    'description': 'Collection of add-ons',
    'warning': '',
    'wiki_url': 'https://github.com/chromoly/blender_ctools',
    'category': 'User Interface',
}


from collections import OrderedDict
import difflib
import hashlib
import importlib
import inspect
import os
import pathlib
import platform
import shutil
import traceback
import tempfile
import urllib.request
import zipfile

import bpy


sub_module_names = [
    'quickboolean',
    'drawnearest',
    'lockcoords',
    'lockcursor3d',
    'mousegesture',
    'overwrite_builtin_images',
    'listvalidkeys',
    'quadview_move',
    'regionruler',
    'screencastkeys',
    # 'searchmenu',
    'updatetag',
    # 'floating_window',
    'splashscreen',
    'aligntools',
]


def fake_module(mod_name, mod_path, speedy=True, force_support=None):
    """scripts/modules/addon_utils.pyのmodule_refresh関数の中からコピペ改変"""

    import ast
    ModuleType = type(ast)
    try:
        file_mod = open(mod_path, "r", encoding='UTF-8')
    except OSError as e:
        print("Error opening file %r: %s" % (mod_path, e))
        return None

    with file_mod:
        if speedy:
            lines = []
            line_iter = iter(file_mod)
            l = ""
            while not l.startswith("bl_info"):
                l = line_iter.readline()

                if len(l) == 0:
                    break
            while l.rstrip():
                lines.append(l)
                l = line_iter.readline()

            data = "".join(lines)

        else:
            data = file_mod.read()
    del file_mod

    try:
        ast_data = ast.parse(data, filename=mod_path)
    except:
        print("Syntax error 'ast.parse' can't read %r" % mod_path)
        import traceback
        traceback.print_exc()
        ast_data = None

    body_info = None

    if ast_data:
        for body in ast_data.body:
            if body.__class__ == ast.Assign:
                if len(body.targets) == 1:
                    if getattr(body.targets[0], "id", "") == "bl_info":
                        body_info = body
                        break

    if body_info:
        try:
            mod = ModuleType(mod_name)
            mod.bl_info = ast.literal_eval(body.value)
            mod.__file__ = mod_path
            mod.__time__ = os.path.getmtime(mod_path)
        except:
            print("AST error parsing bl_info for %s" % mod_name)
            import traceback
            traceback.print_exc()
            raise

        if force_support is not None:
            mod.bl_info["support"] = force_support

        return mod
    else:
        print("fake_module: addon missing 'bl_info' "
              "gives bad performance!: %r" % mod_path)
        return None


def gen_fake_modules():
    _fake_sub_modules = []  # __name__は'ctools.quickboolean'の様になる
    for name in sub_module_names:
        d = os.path.dirname(__file__)
        mod = fake_module(__name__ + '.' + name,
                          os.path.join(d, name, '__init__.py'))
        if mod:
            _fake_sub_modules.append(mod)
    _fake_sub_modules.sort(
        key=lambda mod: (mod.bl_info['category'], mod.bl_info['name']))

    return OrderedDict(
        [(mod.__name__.split('.')[-1], mod) for mod in _fake_sub_modules])


fake_modules = gen_fake_modules()


# reload
try:
    _ = NAME
    for fake_mod in fake_modules.values():
        try:
            mod = importlib.import_module(fake_mod.__name__)
            importlib.reload(mod)
        except:
            traceback.print_exc()
except NameError:
    pass


NAME = 'ctools'

UPDATE_DRY_RUN = False
UPDATE_DIFF_TEXT = False


"""
サブモジュールでAddonPreferenceを使用する場合

from .utils import AddonPreferences
class RegionRulerPreferences(
        AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    ...

"""


def _get_pref_class(mod):
    for obj in vars(mod).values():
        if inspect.isclass(obj) and issubclass(obj, bpy.types.PropertyGroup):
            if hasattr(obj, 'bl_idname') and obj.bl_idname == mod.__name__:
                return obj


def get_addon_preferences(name=''):
    """登録と取得"""
    addons = bpy.context.user_preferences.addons
    if __name__ not in addons:  # wm.read_factory_settings()
        return None
    prefs = addons[__name__].preferences
    if name:
        if not hasattr(prefs, name):
            fake_mod = fake_modules.get(name)
            mod = importlib.import_module(fake_mod.__name__)
            cls = _get_pref_class(mod)
            if cls:
                prop = bpy.props.PointerProperty(type=cls)
                setattr(CToolsPreferences, name, prop)
                bpy.utils.unregister_class(CToolsPreferences)
                bpy.utils.register_class(CToolsPreferences)
        return getattr(prefs, name, None)
    else:
        return prefs


def register_submodule(mod):
    if not hasattr(mod, '__addon_enabled__'):
        mod.__addon_enabled__ = False
    if not mod.__addon_enabled__:
        mod.register()
        mod.__addon_enabled__ = True


def unregister_submodule(mod):
    if not hasattr(mod, '__addon_enabled__'):
        mod.__addon_enabled__ = False
    if mod.__addon_enabled__:
        mod.unregister()
        mod.__addon_enabled__ = False

        prefs = get_addon_preferences()
        name = mod.__name__.split('.')[-1]
        if hasattr(CToolsPreferences, name):
            delattr(CToolsPreferences, name)
            if prefs:
                bpy.utils.unregister_class(CToolsPreferences)
                bpy.utils.register_class(CToolsPreferences)
                if name in prefs:
                    del prefs[name]


def test_platform():
    return (platform.platform().split('-')[0].lower()
            not in {'darwin', 'windows'})


class CToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    align_box_draw = bpy.props.BoolProperty(
            name='Box Draw',
            description='If applied patch: patch/ui_layout_box.patch',
            default=False)

    def draw(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""

        for mod_name, fake_mod in fake_modules.items():
            info = fake_mod.bl_info
            column = layout.column(align=self.align_box_draw)
            box = column.box()

            # 一段目
            expand = getattr(self, 'show_expanded_' + mod_name)
            icon = 'TRIA_DOWN' if expand else 'TRIA_RIGHT'
            col = box.column()  # boxのままだと行間が広い
            row = col.row()
            sub = row.row()
            sub.context_pointer_set('addon_prefs', self)
            sub.alignment = 'LEFT'
            op = sub.operator('wm.context_toggle', text='', icon=icon,
                              emboss=False)
            op.data_path = 'addon_prefs.show_expanded_' + mod_name
            sub.label('{}: {}'.format(info['category'], info['name']))
            sub = row.row()
            sub.alignment = 'RIGHT'
            if info.get('warning'):
                sub.label('', icon='ERROR')
            sub.prop(self, 'use_' + mod_name, text='')
            # 二段目
            if expand:
                # col = box.column()  # boxのままだと行間が広い
                # 参考: space_userpref.py
                if info.get('description'):
                    split = col.row().split(percentage=0.15)
                    split.label('Description:')
                    split.label(info['description'])
                if info.get('location'):
                    split = col.row().split(percentage=0.15)
                    split.label('Location:')
                    split.label(info['location'])
                if info.get('author') and info.get('author') != 'chromoly':
                    split = col.row().split(percentage=0.15)
                    split.label('Author:')
                    split.label(info['author'])
                if info.get('version'):
                    split = col.row().split(percentage=0.15)
                    split.label('Version:')
                    split.label('.'.join(str(x) for x in info['version']),
                                translate=False)
                if info.get('warning'):
                    split = col.row().split(percentage=0.15)
                    split.label('Warning:')
                    split.label('  ' + info['warning'], icon='ERROR')

                tot_row = int(bool(info.get('wiki_url')))
                if tot_row:
                    split = col.row().split(percentage=0.15)
                    split.label(text='Internet:')
                    if info.get('wiki_url'):
                        op = split.operator('wm.url_open',
                                            text='Documentation', icon='HELP')
                        op.url = info.get('wiki_url')
                    for i in range(4 - tot_row):
                        split.separator()

                # 詳細・設定値
                if getattr(self, 'use_' + mod_name):
                    try:
                        prefs = get_addon_preferences(mod_name)
                    except:
                        traceback.print_exc()
                        continue
                    if prefs and hasattr(prefs, 'draw'):
                        if self.align_box_draw:
                            box = column.box()
                        else:
                            box = box.column()
                        if mod_name == 'overwrite_builtin_images':
                            if not test_platform():
                                box.active = False
                        prefs.layout = box
                        try:
                            prefs.draw(context)
                        except:
                            traceback.print_exc()
                            box.label(text='Error (see console)', icon='ERROR')
                        del prefs.layout

        row = layout.row()
        sub = row.row()
        sub.alignment = 'LEFT'
        op = sub.operator('script.cutils_module_update',
                     icon='FILE_REFRESH')
        op.dry_run = UPDATE_DRY_RUN
        op.diff = UPDATE_DIFF_TEXT
        sub = row.row()
        sub.alignment = 'RIGHT'
        sub.prop(self, 'align_box_draw')


for name, fake_mod in fake_modules.items():
    info = fake_mod.bl_info

    def gen_update(fake_mod):
        def update(self, context):
            name = fake_mod.__name__.split('.')[-1]
            try:
                mod = importlib.import_module(fake_mod.__name__)
                if getattr(self, 'use_' + name):
                    register_submodule(mod)
                else:
                    unregister_submodule(mod)
            except:
                # setattr(self, 'use_' + name, False)
                traceback.print_exc()
        return update

    prop = bpy.props.BoolProperty(
        name=info['name'],
        description=info.get('description', '').rstrip('.'),
        update=gen_update(fake_mod),
    )
    setattr(CToolsPreferences, 'use_' + name, prop)
    prop = bpy.props.BoolProperty()
    setattr(CToolsPreferences, 'show_expanded_' + name, prop)


class SCRIPT_OT_cutils_module_update(bpy.types.Operator):
    """このアドオンのディレクトリの中身を全部消して置換する"""
    bl_idname = 'script.cutils_module_update'
    bl_label = 'Update'

    ctools_dir = os.path.dirname(os.path.abspath(__file__))
    bl_description = 'Download and install addon. ' + \
        'Warning: remove all files under {}/'.format(ctools_dir)

    url = 'https://github.com/chromoly/blender_ctools/archive/master.zip'
    log_name = 'ctools_update.log'  # name of bpy.types.Text

    dry_run = bpy.props.BoolProperty(
            'Dry Run', default=False, options={'SKIP_SAVE'})
    diff = bpy.props.BoolProperty(
            'Create Diff Text', default=True, options={'SKIP_SAVE'})

    def execute(self, context):
        if not self.dry_run:
            # '.git'が存在すればやめる
            if '.git' in os.listdir(self.ctools_dir):
                self.report(type={'ERROR'},
                            message="Found '.git' directory. "
                                    "Please use git command")
                return {'CANCELLED'}

        context.window.cursor_set('WAIT')

        diff_lines = []  # 行末に改行文字を含む
        diff_text = None

        try:
            req = urllib.request.urlopen(self.url)

            with tempfile.TemporaryDirectory() as tmpdir_name:
                with tempfile.NamedTemporaryFile(
                        'wb', suffix='.zip', dir=tmpdir_name,
                        delete=False) as tmpfile:
                    tmpfile.write(req.read())
                    req.close()
                zf = zipfile.ZipFile(tmpfile.name, 'r')
                dirname = ''
                for name in zf.namelist():
                    p = pathlib.PurePath(name)
                    if len(p.parts) == 1:
                        dirname = p.parts[0]
                    zf.extract(name, path=tmpdir_name)
                zf.close()

                ctools_dir_tmp = os.path.join(tmpdir_name, dirname)

                # 差分表示
                src_files = []
                dst_files = []
                ignore_dirs = ['__pycache__', '.git', 'subtree']
                os.chdir(ctools_dir_tmp)
                for root, dirs, files in os.walk('.'):
                    for name in files:
                        p = os.path.normpath(os.path.join(root, name))
                        src_files.append(p)
                    for name in ignore_dirs:
                        if name in dirs:
                            dirs.remove(name)
                os.chdir(self.ctools_dir)
                for root, dirs, files in os.walk('.'):
                    for name in files:
                        p = os.path.normpath(os.path.join(root, name))
                        dst_files.append(p)
                    for name in ignore_dirs:
                        if name in dirs:
                            dirs.remove(name)

                files = []
                for name in src_files:
                    if name in dst_files:
                        files.append((name, 'update'))
                    else:
                        files.append((name, 'new'))
                for name in dst_files:
                    if name not in src_files:
                        files.append((name, 'delete'))

                for name, status in files:
                    if name.endswith(('.py', '.md', '.patch', '.sh')):
                        if status in {'new', 'update'}:
                            p1 = os.path.join(ctools_dir_tmp, name)
                            with open(p1, 'r', encoding='utf-8') as f1:
                                src = f1.readlines()
                        else:
                            src = []
                        if status in {'delete', 'update'}:
                            p2 = os.path.join(self.ctools_dir, name)
                            with open(p2, 'r', encoding='utf-8') as f2:
                                dst = f2.readlines()
                        else:
                            dst = []

                        lines = list(difflib.unified_diff(
                                dst, src, fromfile=name, tofile=name))
                        if lines:
                            for line in lines:
                                diff_lines.append(line)
                    else:
                        if status in {'new', 'update'}:
                            p1 = os.path.join(ctools_dir_tmp, name)
                            with open(p1, 'rb') as f1:
                                src = f1.read()
                            h1 = hashlib.md5(src).hexdigest()
                        if status in {'delete', 'update'}:
                            p2 = os.path.join(self.ctools_dir, name)
                            with open(p2, 'rb') as f2:
                                dst = f2.read()
                            h2 = hashlib.md5(dst).hexdigest()

                        if status == 'new':
                            line = 'New: {}\n'.format(name)
                            diff_lines.append(line)
                        elif status == 'delete':
                            line = 'Delete: {}\n'.format(name)
                            diff_lines.append(line)
                        else:
                            if h1 != h2:
                                line = 'Update: {}\n'.format(name)
                                diff_lines.append(line)
                                line = '    md5: {} -> {}\n'.format(h1, h2)
                                diff_lines.append(line)

                if diff_lines:
                    if self.diff:
                        diff_text = bpy.data.texts.new(self.log_name)
                        diff_text.from_string(''.join(diff_lines))
                    if not self.dry_run:
                        # delete
                        for name in os.listdir(self.ctools_dir):
                            if name == '__pycache__':
                                continue
                            p = os.path.join(self.ctools_dir, name)
                            if os.path.isdir(p):
                                shutil.rmtree(p, ignore_errors=True)
                            elif os.path.isfile(p):
                                os.remove(p)

                        # copy all
                        for name, status in files:
                            if status in {'new', 'update'}:
                                dst = os.path.join(self.ctools_dir, name)
                                dst = os.path.normpath(dst)
                                src = os.path.join(ctools_dir_tmp, name)
                                src = os.path.normpath(src)
                                if not os.path.exists(os.path.dirname(dst)):
                                    os.makedirs(os.path.dirname(dst))
                                with open(dst, 'wb') as dst_f, \
                                     open(src, 'rb') as src_f:
                                    dst_f.write(src_f.read())

        # except:
        #     traceback.print_exc()
        #     self.report(type={'ERROR'}, message='See console')
        #     return {'CANCELLED'}

        finally:
            context.window.cursor_set('DEFAULT')

        if diff_lines:
            if diff_text:
                msg = "See '{}' in the text editor".format(diff_text.name)
                self.report(type={'INFO'}, message=msg)
            if not self.dry_run:
                msg = 'Updated. Please restart.'
                self.report(type={'WARNING'}, message=msg)
        else:
            self.report(type={'INFO'}, message='No updates were found')

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


classes = [
    CToolsPreferences,
    SCRIPT_OT_cutils_module_update,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = get_addon_preferences()

    for name, fake_mod in fake_modules.items():
        if getattr(prefs, 'use_' + name):
            try:
                mod = importlib.import_module(fake_mod.__name__)
                register_submodule(mod)
            except:
                setattr(prefs, 'use_' + name, False)
                traceback.print_exc()


def unregister():
    prefs = get_addon_preferences()
    for name, fake_mod in fake_modules.items():
        if getattr(prefs, 'use_' + name):
            try:
                mod = importlib.import_module(fake_mod.__name__)
                unregister_submodule(mod)
            except:
                traceback.print_exc()

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)
