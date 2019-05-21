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
    'name': 'Search Menu',
    'author': 'chromoly',
    'version': (1, 0),
    'blender': (2, 77, 0),
    'location': '',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'category': 'UI',
}


# TODO: node.add_search

from collections import OrderedDict, defaultdict
import ctypes as ct
import collections
import fnmatch
import importlib
import itertools
import math
import traceback

import bpy
import bmesh
import bgl
import mathutils.geometry
from mathutils import *

try:
    importlib.reload(structures)
    importlib.reload(utils)
except NameError:
    from . import structures
    from . import utils


class SearchMenuProperty(bpy.types.PropertyGroup):
    idname = bpy.props.StringProperty()
    idname_py = bpy.props.StringProperty()
    label = bpy.props.StringProperty()
    description = bpy.props.StringProperty()
    translation_context = bpy.props.StringProperty()
    is_internal = bpy.props.BoolProperty()


class SearchMenuPreferences(
        utils.AddonKeyMapUtility,
        utils.AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):

    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        col = split.column()

        split.column()
        split.column()

        super().draw(context, layout.column())


def get_operator_type(pyop):
    opinst = pyop.get_instance()
    pyrna = ct.cast(ct.c_void_p(id(opinst)),
                    ct.POINTER(structures.BPy_StructRNA)).contents
    op = ct.cast(ct.c_void_p(pyrna.ptr.data),
                 ct.POINTER(structures.wmOperator)).contents
    return op.type.contents


class SearchMenuCopy(bpy.types.Operator):
    bl_idname = 'wm.search_menu_i18n_copy'
    bl_label = 'Copy'
    bl_description = 'Copy Text'
    bl_options = {'REGISTER', 'INTERNAL'}

    text = bpy.props.StringProperty()

    def execute(self, context):
        context.window_manager.clipboard = self.text
        return {'FINISHED'}


class SearchMenu(bpy.types.Operator):
    bl_idname = 'wm.search_menu_i18n'
    bl_label = 'Search Menu'
    bl_description = 'Pop-up a search menu over all available operators in' \
                     ' current context'
    bl_options = {'REGISTER'}


    operators = bpy.props.CollectionProperty(
        type=SearchMenuProperty,
        options={'SKIP_SAVE'})
    # active_operator_index = bpy.props.IntProperty()

    operator = bpy.props.StringProperty(
    )

    operator_pp = bpy.props.PointerProperty(
        type=SearchMenuProperty,
        name='PointerProperty'
    )

    def _use_translate_update(self, context):
        SearchMenu.init_items(self, context)

    show_translated = bpy.props.BoolProperty(
        name='Translate',
        update=_use_translate_update,
    )
    show_all = bpy.props.BoolProperty(
        name='All',
        update=_use_translate_update,
    )

    def check(self, context):
        return True

    def execute(self, context):
        if self.operator in self.operators:
            item = self.operators[self.operator]
            op = eval('bpy.ops.' + item.idname_py)
            if op.poll():
                op(context.copy(), 'INVOKE_DEFAULT', True)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""

        layout.prop_search(self, 'operator', self, 'operators', text='',
                           text_ctxt='*')

        # interface.c: 3489 RNA_property_editable
        layout.prop_search(self, 'operator_pp', self, 'operators', text='',
                           text_ctxt='*')

        if self.operator in self.operators:
            item = self.operators[self.operator]
            label = bpy.app.translations.pgettext_iface(
                    item.label, item.translation_context)
            layout.label(label, translate=False)
            description = bpy.app.translations.pgettext_tip(
                    item.description, '*')
            layout.label(description, translate=False)
            py_text = 'Python: bpy.ops.' + item.idname_py + '()'
            layout.label(py_text, translate=False)

        row = layout.row()
        split = row.split()
        subrow = split.row()
        subrow.prop(self, 'show_translated', text='Translate', translate=False)
        subrow = split.row()
        subrow.prop(self, 'show_all', text='All')
        if self.operator in self.operators:
            subrow = split.row()
            op = subrow.operator(SearchMenuCopy.bl_idname,
                                 text='Copy', icon='COPYDOWN')
            op.text = '\n'.join([label, description, py_text])
        else:
            subrow = split.row()

    def init_items(self, context):
        def gen_name(item):
            item.name = item.label
            t = item.idname_py.split('.')[0]
            name = ' '.join([s.title() for s in t.split('_')]) + ': '
            label = bpy.app.translations.pgettext_iface(
                item.label, item.translation_context)
            name += label

            if self.show_translated:
                if label != item.label:
                    name += ' / ' + item.label
                else:
                    label_ = bpy.app.translations.pgettext(
                        item.label, item.translation_context)
                    if label_ != label:
                        name += ' / ' + label_
            item.name = name

        self.operators.clear()

        for mod in dir(bpy.ops):
            for func in dir(getattr(bpy.ops, mod)):
                pyop = getattr(getattr(bpy.ops, mod), func)
                if not self.show_all and not pyop.poll():
                    continue
                ot = get_operator_type(pyop)
                rna_tye = pyop.get_rna().rna_type
                item = self.operators.add()
                item.idname_py = pyop.idname_py()
                item.idname = rna_tye.identifier
                item.description = rna_tye.description
                item.label = rna_tye.name
                item.is_internal = bool(ot.flag & structures.OPTYPE_INTERNAL)
                item.translation_context = rna_tye.translation_context
                gen_name(item)

        # 重複するものにはidname_pyを付ける
        d = defaultdict(list)
        for item in self.operators:
            d[item.name].append(item)
        for items in d.values():
            if len(items) > 1:
                for item in items:
                    item.name += '  [' + item.idname_py + ']'

        # ショートカット
        enum_items = bpy.types.Event.bl_rna.properties['type'].enum_items
        enum_names = {e.identifier: e.name for e in enum_items}
        def kmi_shrtcut_to_str(kmi):
            mods = []
            if kmi.any:
                mods.append('Any')
            else:
                for mod in ('shift', 'ctrl', 'alt', 'oskey'):
                    if getattr(kmi, mod):
                        if mod == 'oskey':
                            mods.append('Cmd')
                        else:
                            mods.append(mod.title())
            if kmi.key_modifier != 'NONE':
                mods.append(enum_names[kmi.key_modifier])
            text = enum_names[kmi.type]
            if mods:
                text = ' '.join(mods) + ' ' + text
            return text

        d = {item.idname_py: item for item in self.operators}
        from .. import listvalidkeys
        keymaps = listvalidkeys.context_keymaps(context)
        for km in keymaps:
            for kmi in km.keymap_items:
                if kmi.idname in d:
                    d[kmi.idname].name += '  [' + kmi_shrtcut_to_str(kmi) + ']'
                    del d[kmi.idname]

    def invoke(self, context, event):
        self.init_items(context)
        wm = context.window_manager
        # r = wm.invoke_popup(self)  # popup(draw関数部分)を表示するだけ
        return wm.invoke_props_dialog(self, width=600)


classes = [
    SearchMenuProperty,
    SearchMenuPreferences,
    SearchMenu,
    SearchMenuCopy,
]


addon_keymaps = []


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager

    kc = wm.keyconfigs.addon
    if kc:
        addon_prefs = SearchMenuPreferences.get_instance()
        """:type: SearchMenuPreferences"""
        km = addon_prefs.get_keymap('Window')
        kmi = km.keymap_items.new(SearchMenu.bl_idname, 'SPACE', 'PRESS',
                                  alt=True)
        addon_keymaps.append((km, kmi))

        addon_prefs.register_keymap_items(addon_keymaps)


def unregister():
    addon_prefs = SearchMenuPreferences.get_instance()
    """:type: SearchMenuPreferences"""
    addon_prefs.unregister_keymap_items()

    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)