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


import importlib

import bpy


def get_addon_preferences(name):
    """AddonPreferencesのインスタンスを返す
    :param name: モジュール名。 e.g. 'ctools', 'ctools.quadview_move'
    :type name: str
    :rtype: AddonPreferences
    """
    context = bpy.context
    if '.' in name:
        pkg, mod = name.split('.')
        module = importlib.import_module(pkg)
        if getattr(module, 'NAME', '') == 'ctools':
            prefs = module.get_addon_preferences(mod)
            return prefs
        else:
            prefs = context.user_preferences.addons[pkg].preferences
            return getattr(prefs, mod)
    else:
        return context.user_preferences.addons[name].preferences


class AddonPreferences:
    @classmethod
    def get_instance(cls, package=''):
        if not package:
            package = __package__
        return get_addon_preferences(package)

    @classmethod
    def register(cls):
        if '.' in __package__:
            cls.get_instance()
        c = super()
        if hasattr(c, 'register'):
            c.register()

    @classmethod
    def unregister(cls):
        c = super()
        if hasattr(c, 'unregister'):
            c.unregister()


class SpaceProperty:
    """
    bpy.types.Spaceに仮想的なプロパティを追加

    # インスタンス生成
    space_prop = SpaceProperty(
        [[bpy.types.SpaceView3D, 'lock_cursor_location',
          bpy.props.BoolProperty()]])

    # 描画時
    def draw(self, context):
        layout = self.layout
        view = context.space_data
        prop = space_prop.get_prop(view, 'lock_cursor_location')
        layout.prop(prop, 'lock_cursor_location')

    # register / unregister
    def register():
        space_prop.register()

    def unregister():
        space_prop.unregister()
    """

    space_types = {
        'EMPTY': bpy.types.Space,
        'NONE': bpy.types.Space,
        'CLIP_EDITOR': bpy.types.SpaceClipEditor,
        'CONSOLE': bpy.types.SpaceConsole,
        'DOPESHEET_EDITOR': bpy.types.SpaceDopeSheetEditor,
        'FILE_BROWSER': bpy.types.SpaceFileBrowser,
        'GRAPH_EDITOR': bpy.types.SpaceGraphEditor,
        'IMAGE_EDITOR': bpy.types.SpaceImageEditor,
        'INFO': bpy.types.SpaceInfo,
        'LOGIC_EDITOR': bpy.types.SpaceLogicEditor,
        'NLA_EDITOR': bpy.types.SpaceNLA,
        'NODE_EDITOR': bpy.types.SpaceNodeEditor,
        'OUTLINER': bpy.types.SpaceOutliner,
        'PROPERTIES': bpy.types.SpaceProperties,
        'SEQUENCE_EDITOR': bpy.types.SpaceSequenceEditor,
        'TEXT_EDITOR': bpy.types.SpaceTextEditor,
        'TIMELINE': bpy.types.SpaceTimeline,
        'USER_PREFERENCES': bpy.types.SpaceUserPreferences,
        'VIEW_3D': bpy.types.SpaceView3D,
    }
    # space_types_r = {v: k for k, v in space_types.items()}

    def __init__(self, *props):
        """
        :param props: [[space_type, attr, prop], ...]
            [[文字列かbpy.types.Space, 文字列,
              bpy.props.***()かPropertyGroup], ...]
            bpy.types.PropertyGroupを使う場合はあらかじめregister_class()で
            登録しておく
        :type props: list[list]
        """
        self.props = [list(elem) for elem in props]
        for elem in self.props:
            space_type = elem[0]
            if isinstance(space_type, str):
                elem[0] = self.space_types[space_type]
        self.registered = []
        self.save_pre = self.save_post = self.load_post = None

    def gen_save_pre(self):
        @bpy.app.handlers.persistent
        def save_pre(dummy):
            wm = bpy.context.window_manager
            for (space_type, attr, prop), (cls, wm_prop_name) in zip(
                    self.props, self.registered):
                if wm_prop_name not in wm:
                    continue
                d = {p['name']: p for p in wm[wm_prop_name]}  # not p.name
                for screen in bpy.data.screens:
                    ls = []
                    for area in screen.areas:
                        for space in area.spaces:
                            if isinstance(space, space_type):
                                key = str(space.as_pointer())
                                if key in d:
                                    ls.append(d[key])
                                else:
                                    ls.append({})
                    screen[wm_prop_name] = ls
        self.save_pre = save_pre
        return save_pre

    def gen_save_post(self):
        @bpy.app.handlers.persistent
        def save_post(dummy):
            # 掃除
            for cls, wm_prop_name in self.registered:
                for screen in bpy.data.screens:
                    if wm_prop_name in screen:
                        del screen[wm_prop_name]
        self.save_post = save_post
        return save_post

    def gen_load_post(self):
        @bpy.app.handlers.persistent
        def load_post(dummy):
            from collections import OrderedDict
            for (space_type, attr, prop), (cls, wm_prop_name) in zip(
                    self.props, self.registered):
                d = OrderedDict()
                for screen in bpy.data.screens:
                    if wm_prop_name not in screen:
                        continue

                    spaces = []
                    for area in screen.areas:
                        for space in area.spaces:
                            if isinstance(space, space_type):
                                spaces.append(space)

                    for space, p in zip(spaces, screen[wm_prop_name]):
                        key = p['name'] = str(space.as_pointer())
                        d[key] = p
                if d:
                    bpy.context.window_manager[wm_prop_name] = list(d.values())

            # 掃除
            for cls, wm_prop_name in self.registered:
                for screen in bpy.data.screens:
                    if wm_prop_name in screen:
                        del screen[wm_prop_name]

        self.load_post = load_post
        return load_post

    def get_all(self, space_type=None, attr=''):
        """
        :param space_type: プロパティが一つだけの場合のみ省略可
        :type space_type: bpy.types.Space
        :param attr: プロパティが一つだけの場合のみ省略可
        :type attr: str
        :return:
        :rtype:
        """
        if space_type and isinstance(space_type, str):
            space_type = self.space_types.get(space_type)
        context = bpy.context
        for (st, attri, prop), (cls, wm_prop_name) in zip(
                self.props, self.registered):
            if (st == space_type or issubclass(space_type, st) or
                    not space_type and len(self.props) == 1):
                if attri == attr or not attr and len(self.props) == 1:
                    seq = getattr(context.window_manager, wm_prop_name)
                    return seq

    def get(self, space, attr=''):
        """
        :type space: bpy.types.Space
        :param attr: プロパティが一つだけの場合のみ省略可
        :type attr: str
        :return:
        :rtype:
        """
        seq = self.get_all(type(space), attr)
        if seq is not None:
            key = str(space.as_pointer())
            if key not in seq:
                item = seq.add()
                item.name = key
            return seq[key]

    def _property_name(self, space_type, attr):
        return space_type.__name__.lower() + '_' + attr

    def register(self):
        import inspect
        for space_type, attr, prop in self.props:
            if inspect.isclass(prop) and \
                    issubclass(prop, bpy.types.PropertyGroup):
                cls = prop
            else:
                name = 'WM_PG_' + space_type.__name__ + '_' + attr
                cls = type(name, (bpy.types.PropertyGroup,), {attr: prop})
                bpy.utils.register_class(cls)

            collection_prop = bpy.props.CollectionProperty(type=cls)
            wm_prop_name = self._property_name(space_type, attr)
            setattr(bpy.types.WindowManager, wm_prop_name, collection_prop)

            self.registered.append((cls, wm_prop_name))

            def gen():
                def get(self):
                    seq = getattr(bpy.context.window_manager, wm_prop_name)
                    key = str(self.as_pointer())
                    if key not in seq:
                        item = seq.add()
                        item.name = key
                    if prop == cls:
                        return seq[key]
                    else:
                        return getattr(seq[key], attr)

                def set(self, value):
                    seq = getattr(bpy.context.window_manager, wm_prop_name)
                    key = str(self.as_pointer())
                    if key not in seq:
                        item = seq.add()
                        item.name = key
                    if prop != cls:  # PropertyGroupは書き込み不可
                        return setattr(seq[key], attr, value)

                return property(get, set)

            setattr(space_type, attr, gen())

        bpy.app.handlers.save_pre.append(self.gen_save_pre())
        bpy.app.handlers.save_post.append(self.gen_save_post())
        bpy.app.handlers.load_post.append(self.gen_load_post())

    def unregister(self):
        bpy.app.handlers.save_pre.remove(self.save_pre)
        bpy.app.handlers.save_post.remove(self.save_post)
        bpy.app.handlers.load_post.remove(self.load_post)

        for (space_type, attr, prop), (cls, wm_prop_name) in zip(
                self.props, self.registered):
            delattr(bpy.types.WindowManager, wm_prop_name)
            if wm_prop_name in bpy.context.window_manager:
                del bpy.context.window_manager[wm_prop_name]
            delattr(space_type, attr)

            if prop != cls:
                # 元々がbpy.types.PropertyGroupなら飛ばす
                bpy.utils.unregister_class(cls)

            for screen in bpy.data.screens:
                if wm_prop_name in screen:
                    del screen[wm_prop_name]

        self.registered.clear()


def operator_call(op, *args, _scene_update=True, **kw):
    """vawmより
    operator_call(bpy.ops.view3d.draw_nearest_element,
                  'INVOKE_DEFAULT', type='ENABLE', _scene_update=False)
    """
    import bpy
    from _bpy import ops as ops_module

    BPyOpsSubModOp = op.__class__
    op_call = ops_module.call
    context = bpy.context

    # Get the operator from blender
    wm = context.window_manager

    # run to account for any rna values the user changes.
    if _scene_update:
        BPyOpsSubModOp._scene_update(context)

    if args:
        C_dict, C_exec, C_undo = BPyOpsSubModOp._parse_args(args)
        ret = op_call(op.idname_py(), C_dict, kw, C_exec, C_undo)
    else:
        ret = op_call(op.idname_py(), None, kw)

    if 'FINISHED' in ret and context.window_manager == wm:
        if _scene_update:
            BPyOpsSubModOp._scene_update(context)

    return ret


class AddonKeyMapUtility:
    """AddonPreferencesと一緒にこれも継承する

    class ExampleAddonPreferences(AddonKeyMapUtility,
                                  bpy.types.AddonPreferences):
        bl_idname = __name__

        # register, unregister, draw をオーバーライドするなら
        # super関数等を使って元のメソッドを実行する必要がある

        # @classmethod
        # def register(cls):
        #     super().register()

        # @classmethod
        # def unregister(cls):
        #     super().unregister()

        # def draw(self, context):
        #    super().draw(context)
        #    # super().draw(context, self.layout, hierarchy=False, box=True)

    classes = [
        ExampleAddonPreferences,
    ]

    addon_keymaps = []

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)

        kc = bpy.context.window_manager.keyconfigs.addon
        if kc:
            addon_prefs = ExampleAddonPreferences.get_instance()
            km = addon_prefs.get_keymap('Screen')
            kmi = km.keymap_items.new(
                'wm.splash', 'ONE', 'PRESS', ctrl=True, alt=True)
            addon_keymaps.append((km, kmi))  # or addon_keymaps.append(kmi)
            addon_prefs.register_keymap_items(addon_keymaps)

    def unregister():
        addon_prefs = ExampleAddonPreferences.get_instance()
        addon_prefs.unregister_keymap_items()

        for cls in classes[::-1]:
            bpy.utils.unregister_class(cls)

    """

    _ADDON_KEY_MAP_UTILITY_QUALNAME = __qualname__
    _KMU_IDPROP_NAME = 'AddonKeyMapUtility_keymap_items'

    __addon_keymaps = None
    """:type: list"""

    # custom property -----------------------------------------------

    __show_keymaps = False

    def __show_keymaps_get(self):
        return self.__class__.__show_keymaps

    def __show_keymaps_set(self, value):
        self.__class__.__show_keymaps = value

    show_addon_keymaps = bpy.props.BoolProperty(
        name='Show KeyMaps',
        get=__show_keymaps_get,
        set=__show_keymaps_set,
    )

    # property ------------------------------------------------------

    __data = {'keymap_items': {}, 'default_values': {}}

    @property
    def __keymap_items(self):
        """[(km.name, kmi.id), ...]"""
        d = self.__data['keymap_items']
        return d.setdefault(self.as_pointer(), [])

    @property
    def __default_values(self):
        """[[km.name, attrs, props, ...]]"""
        d = self.__data['default_values']
        return d.setdefault(self.as_pointer(), [])

    # register / unregister -----------------------------------------

    @classmethod
    def register(cls):
        """継承したクラスでもregisterを定義するなら、super関数を使って
        このメソッドを呼ぶ。
        super().register()
        """
        classes = [cls.__WM_OT_kmu_keymap_item_add,
                   cls.__WM_OT_kmu_keymap_item_remove,
                   cls.__WM_OT_kmu_keymaps_write,
                   cls.__WM_OT_kmu_keymaps_restore,
                   cls.__WM_MT_kmu_keymap_item_add,
                   ]
        for c in classes:
            c.register_class()

        c = super()
        if hasattr(c, 'register'):
            c.register()

    @classmethod
    def unregister(cls):
        """注意事項はregisterと同じ"""

        classes = [cls.__WM_OT_kmu_keymap_item_add,
                   cls.__WM_OT_kmu_keymap_item_remove,
                   cls.__WM_OT_kmu_keymaps_write,
                   cls.__WM_OT_kmu_keymaps_restore,
                   cls.__WM_MT_kmu_keymap_item_add,
                   ]
        for c in classes[::-1]:
            c.unregister_class()

        c = super()
        if hasattr(c, 'unregister'):
            c.unregister()

    @staticmethod
    def __reversed_keymap_table():
        kc = bpy.context.window_manager.keyconfigs.addon
        km_table = {}
        for km in kc.keymaps:
            for kmi in km.keymap_items:
                km_table[kmi] = km
        return km_table

    @staticmethod
    def __get_keymap(name):
        """KeyMaps.new()の結果を返す。name以外の引数は勝手に補間してくれる。
        :type name: str
        :rtype: bpy.types.KeyMap
        """
        import bpy_extras.keyconfig_utils

        # blenderを起動してis_modalを確認するしか方法が無い
        modal_keymaps = {
            'View3D Gesture Circle', 'Gesture Border',
            'Gesture Zoom Border', 'Gesture Straight Line',
            'Standard Modal Map', 'Knife Tool Modal Map',
            'Transform Modal Map', 'Paint Stroke Modal', 'View3D Fly Modal',
            'View3D Walk Modal', 'View3D Rotate Modal', 'View3D Move Modal',
            'View3D Zoom Modal', 'View3D Dolly Modal', }

        kc = bpy.context.window_manager.keyconfigs.addon
        if not kc:
            return None

        # if 'INVALID_MODAL_KEYMAP' and name in modal_keymaps:
        #     msg = "not support modal keymap: '{}'".format(name)
        #     raise ValueError(msg)

        def get(ls, name):
            for keymap_name, space_type, region_type, children in ls:
                if keymap_name == name:
                    is_modal = keymap_name in modal_keymaps
                    return kc.keymaps.new(keymap_name, space_type=space_type,
                                          region_type=region_type,
                                          modal=is_modal)
                elif children:
                    km = get(children, name)
                    if km:
                        return km

        km = get(bpy_extras.keyconfig_utils.KM_HIERARCHY, name)
        if not km:
            msg = "Keymap '{}' not in builtins".format(name)
            raise ValueError(msg)
        return km

    @classmethod
    def __get_instance(cls, package=''):
        """AddonPreferencesのインスタンスを返す
        :param package: ctools以外には関係ないもの
        :type package: str
        :rtype: AddonPreferences
        """
        return AddonPreferences.get_instance(package)

    def __get_current_values(self):
        import itertools
        import mathutils

        values = []
        km_table = self.__reversed_keymap_table()

        keympap_items = []
        for item in list(self.__keymap_items):
            km_name, kmi_id = item
            km = self.__get_keymap(km_name)
            for kmi in km.keymap_items:
                if kmi.id == kmi_id:
                    keympap_items.append(kmi)
                    break

        for kmi in keympap_items:
            km = km_table[kmi]
            # KeyMapItemの属性
            attrs = {}
            for attr in ('active', 'map_type', 'type', 'value', 'propvalue',
                         'idname', 'any', 'shift', 'ctrl', 'alt', 'oskey',
                         'key_modifier'):
                value = getattr(kmi, attr)
                if isinstance(value, bool):
                    value = int(value)
                attrs[attr] = value
            # オペレータのプロパティ
            props = {}
            if not km.is_modal:
                for attr in kmi.properties.bl_rna.properties.keys():
                    if attr == 'rna_type':
                        continue
                    if kmi.properties.is_property_set(attr):
                        value = getattr(kmi.properties, attr)
                        if isinstance(value, bool):
                            value = int(value)
                        elif isinstance(value, (
                                mathutils.Color, mathutils.Euler,
                                mathutils.Vector, mathutils.Quaternion)):
                            value = list(value)
                        elif isinstance(value, mathutils.Matrix):
                            value = list(
                                itertools.chain.from_iterable(value.col))
                        props[attr] = value

            values.append([km.name, attrs, props])

        return values

    def __set_values(self, values):
        import traceback
        self.__unregister_keymap_items()
        keymap_items = []
        for km_name, attrs, props in values:
            km = self.__get_keymap(km_name)
            if 'INVALID_MODAL_KEYMAP' and km.is_modal:
                raise ValueError(
                    "not support modal keymap: '{}'".format(km.name))
            if km.is_modal:
                args = {name: attrs[name] for name in (
                    'type', 'value', 'propvalue', 'any', 'shift', 'ctrl',
                    'alt', 'oskey', 'key_modifier')}
                kmi = km.keymap_items.new_modal(**args)
                # kmi.propvalue = attrs['propvalue']  # 適用できていないから
                # TODO: ModalKeyMap使用不可。
                #       val: enum "TRANSLATE" not found in ('NONE')
            else:
                args = {name: attrs[name] for name in (
                    'idname', 'type', 'value', 'any', 'shift', 'ctrl', 'alt',
                    'oskey', 'key_modifier')}
                kmi = km.keymap_items.new(**args)
            kmi.active = attrs['active']
            for name, value in props.items():
                try:
                    setattr(kmi.properties, name, value)
                except:
                    traceback.print_exc()
            keymap_items.append(kmi)
        self.__register_keymap_items(keymap_items, False, False)

    def __register_keymap_item(self, kmi):
        """KeyMapItemを登録する
        :param kmi: KeyMapItem 若しくは (KeyMap名, KeyMapItemのid)
        :type kmi: bpy.types.KeyMapItem | (str, int)
        """
        if isinstance(kmi, bpy.types.KeyMapItem):
            km_tabel = self.__reversed_keymap_table()
            km = km_tabel[kmi]
        else:
            km, kmi = kmi
        if 'INVALID_MODAL_KEYMAP' and km.is_modal:
            raise ValueError("not support modal keymap: '{}'".format(km.name))
        self.__keymap_items.append((km.name, kmi.id))

    def __register_keymap_items(self, addon_keymaps, set_default=True,
                                load=True):
        """KeyMapItemを登録する。keymaps_set_default(), keymaps_load() も
        まとめて行う。
        :param addon_keymaps: KeyMapItem 若しくは (KeyMap名, KeyMapItemのid) の
            リスト
        :type addon_keymaps: list[bpy.types.KeyMapItem] | list[(str, int)]
        """
        km_tabel = self.__reversed_keymap_table()
        items = []
        for kmi in addon_keymaps:
            if isinstance(kmi, bpy.types.KeyMapItem):
                km = km_tabel[kmi]
            else:
                km, kmi = kmi
            if 'INVALID_MODAL_KEYMAP' and km.is_modal:
                raise ValueError(
                    "not support modal keymap: '{}'".format(km.name))
            items.append((km.name, kmi.id))
        self.__keymap_items.extend(items)
        if set_default:
            self.__keymaps_set_default()
        if load:
            self.__keymaps_load()
        self.__class__.__addon_keymaps = addon_keymaps

    def __unregister_keymap_item(self, kmi, remove=True):
        """KeyMapItemの登録を解除する
        :param kmi: KeyMapItem 若しくは (KeyMap名, KeyMapItemのid)
        :type kmi: bpy.types.KeyMapItem | (str, int)
        :param remove: KeyMapItemをKeyMapItemsから削除する
        :type remove: bool
        """
        km_table = self.__reversed_keymap_table()
        if isinstance(kmi, bpy.types.KeyMapItem):
            km = km_table[kmi]
            item = (km.name, kmi.id)
        else:
            item = kmi
            km_name, kmi_id = item
            km = self.__get_keymap(km_name)
            for kmi in km.keymap_items:
                if kmi.id == kmi_id:
                    break
            else:
                raise ValueError('KeyMapItem not fond')
        if 'INVALID_MODAL_KEYMAP' and km.is_modal:
            raise ValueError("not support modal keymap: '{}'".format(km.name))
        self.__keymap_items.remove(item)
        if remove:
            km.keymap_items.remove(kmi)

    def __unregister_keymap_items(self, remove=True,
                                  clear_addon_keymaps=True):
        """全てのKeyMapItemの登録を解除する。
        :param remove: KeyMapItemをKeyMap.keymap_itemsから削除する
        :type remove: bool
        :param clear_addon_keymaps:
            register_keymap_items()の第一引数がリストだった場合にそれを空にする
            self.addon_keymaps.clear()
        :type clear_addon_keymaps: bool
        """
        if remove:
            for km_name, kmi_id in self.__keymap_items:
                km = self.__get_keymap(km_name)
                for kmi in km.keymap_items:
                    if kmi.id == kmi_id:
                        break
                else:
                    raise ValueError('KeyMapItem not fond')
                if 'INVALID_MODAL_KEYMAP' and km.is_modal:
                    raise ValueError(
                        "not support modal keymap: '{}'".format(km.name))
                km.keymap_items.remove(kmi)
        self.__keymap_items.clear()
        if clear_addon_keymaps:
            if isinstance(self.__addon_keymaps, list):
                self.__addon_keymaps.clear()

    def __keymaps_set_default(self):
        """現在登録しているKeyMapItemを初期値(restore時の値)とする"""
        self.__default_values.clear()
        self.__default_values[:] = self.__get_current_values()

    def __keymaps_load(self):
        """保存されたキーマップを読んで現在のキーマップを置き換える"""
        addon_prefs = self.__get_instance()
        if self._KMU_IDPROP_NAME not in addon_prefs:
            return False
        self.__set_values(addon_prefs[self._KMU_IDPROP_NAME])
        return True

    def __keymaps_restore(self):
        """キーマップを初期値に戻す"""
        self.__set_values(self.__default_values)

    get_keymap = __get_keymap
    get_instance = __get_instance
    register_keymap_item = __register_keymap_item
    register_keymap_items = __register_keymap_items
    unregister_keymap_item = __unregister_keymap_item
    unregister_keymap_items = __unregister_keymap_items
    keymaps_set_default = __keymaps_set_default
    keymaps_load = __keymaps_load
    keymaps_restore = __keymaps_restore

    def registered_keymap_items(self):
        return self.__keymap_items

    # draw ----------------------------------------------------------

    __EVENT_TYPES = set()
    __EVENT_TYPE_MAP = {}
    __EVENT_TYPE_MAP_EXTRA = {}

    __INDENTPX = 16

    def __indented_layout(self, layout, level):
        if level == 0:
            # Tweak so that a percentage of 0 won't split by half
            level = 0.0001
        indent = level * self.__INDENTPX / bpy.context.region.width

        split = layout.split(percentage=indent)
        col = split.column()
        col = split.column()
        return col

    def __draw_entry(self, display_keymaps, entry, col, level=0):
        idname, spaceid, regionid, children = entry

        for km, km_items in display_keymaps:
            if (km.name == idname and km.space_type == spaceid and
                        km.region_type == regionid):
                self.__draw_km(display_keymaps, km, km_items, children, col,
                               level)

    def __draw_km(self, display_keymaps, km, km_items, children, layout,
                  level):
        from bpy.app.translations import pgettext_iface as iface_
        from bpy.app.translations import contexts as i18n_contexts

        # km = km.active()  # keyconfigs.userのkeymapが返ってくる

        layout.context_pointer_set("keymap", km)

        col = self.__indented_layout(layout, level)

        row = col.row(align=True)
        row.prop(km, "show_expanded_children", text="", emboss=False)
        row.label(text=km.name, text_ctxt=i18n_contexts.id_windowmanager)

        # if km.is_user_modified or km.is_modal:
        if km.is_modal:
            subrow = row.row()
            subrow.alignment = 'RIGHT'

            # if km.is_user_modified:
            #     subrow.operator("wm.keymap_restore", text="Restore")
            if km.is_modal:
                subrow.label(text="", icon='LINKED')
            del subrow

        if km.show_expanded_children:
            if children:
                # Put the Parent key map's entries in a 'global' sub-category
                # equal in hierarchy to the other children categories
                subcol = self.__indented_layout(col, level + 1)
                subrow = subcol.row(align=True)
                subrow.prop(km, "show_expanded_items", text="", emboss=False)
                subrow.label(text=iface_("%s (Global)") % km.name,
                             translate=False)
            else:
                km.show_expanded_items = True

            # Key Map items
            if km.show_expanded_items:
                kmi_level = level + 3 if children else level + 1
                # for kmi in km.keymap_items:
                for kmi in km_items:
                    self.__draw_kmi(km, kmi, col, kmi_level)

            # Child key maps
            if children:
                for entry in children:
                    self.__draw_entry(display_keymaps, entry, col,
                                         level + 1)

            col.separator()

    def __draw_kmi(self, km, kmi, layout, level):
        map_type = kmi.map_type

        col = self.__indented_layout(layout, level)

        if kmi.show_expanded:
            col = col.column(align=True)
            box = col.box()
        else:
            box = col.column()

        split = box.split(percentage=0.01)

        # header bar
        row = split.row()
        row.prop(kmi, "show_expanded", text="", emboss=False)

        row = split.row()
        row.prop(kmi, "active", text="", emboss=False)

        if km.is_modal:
            row.prop(kmi, "propvalue", text="")
        else:
            row.label(text=kmi.name)

        row = split.row()
        row.prop(kmi, "map_type", text="")
        if map_type == 'KEYBOARD':
            row.prop(kmi, "type", text="", full_event=True)
        elif map_type == 'MOUSE':
            row.prop(kmi, "type", text="", full_event=True)
        elif map_type == 'NDOF':
            row.prop(kmi, "type", text="", full_event=True)
        elif map_type == 'TWEAK':
            subrow = row.row()
            subrow.prop(kmi, "type", text="")
            subrow.prop(kmi, "value", text="")
        elif map_type == 'TIMER':
            row.prop(kmi, "type", text="")
        else:
            row.label()

        op = row.operator("wm.kmu_keymap_item_remove", text="", icon='X')
        op.item_id = kmi.id

        # Expanded, additional event settings
        if kmi.show_expanded:
            box = col.box()

            split = box.split(percentage=0.4)
            sub = split.row()

            if km.is_modal:
                sub.prop(kmi, "propvalue", text="")
            else:
                # One day...
                # ~ sub.prop_search(kmi, "idname", bpy.context.window_manager,
                #  "operators_all", text="")
                sub.prop(kmi, "idname", text="")

            if map_type not in {'TEXTINPUT', 'TIMER'}:
                sub = split.column()
                subrow = sub.row(align=True)

                if map_type == 'KEYBOARD':
                    subrow.prop(kmi, "type", text="", event=True)
                    subrow.prop(kmi, "value", text="")
                elif map_type in {'MOUSE', 'NDOF'}:
                    subrow.prop(kmi, "type", text="")
                    subrow.prop(kmi, "value", text="")

                subrow = sub.row()
                subrow.scale_x = 0.75
                subrow.prop(kmi, "any")
                subrow.prop(kmi, "shift")
                subrow.prop(kmi, "ctrl")
                subrow.prop(kmi, "alt")
                subrow.prop(kmi, "oskey", text="Cmd")
                subrow.prop(kmi, "key_modifier", text="", event=True)

            # Operator properties
            box.template_keymap_item_properties(kmi)

    def __draw_filtered(self, display_keymaps, filter_type, filter_text,
                        layout):
        _EVENT_TYPES = self.__EVENT_TYPES
        _EVENT_TYPE_MAP = self.__EVENT_TYPE_MAP
        _EVENT_TYPE_MAP_EXTRA = self.__EVENT_TYPE_MAP_EXTRA

        if filter_type == 'NAME':
            def filter_func(kmi):
                return (filter_text in kmi.idname.lower() or
                        filter_text in kmi.name.lower())
        else:
            if not _EVENT_TYPES:
                enum = bpy.types.Event.bl_rna.properties["type"].enum_items
                _EVENT_TYPES.update(enum.keys())
                _EVENT_TYPE_MAP.update(
                    {item.name.replace(" ", "_").upper(): key for key, item in
                     enum.items()})

                del enum
                _EVENT_TYPE_MAP_EXTRA.update(
                    {"`": 'ACCENT_GRAVE',
                     "*": 'NUMPAD_ASTERIX',
                     "/": 'NUMPAD_SLASH',
                     "RMB": 'RIGHTMOUSE',
                     "LMB": 'LEFTMOUSE',
                     "MMB": 'MIDDLEMOUSE',
                     })
                _EVENT_TYPE_MAP_EXTRA.update(
                    {"%d" % i: "NUMPAD_%d" % i for i in range(10)})
            # done with once off init

            filter_text_split = filter_text.strip()
            filter_text_split = filter_text.split()

            # Modifier {kmi.attribute: name} mapping
            key_mod = {"ctrl": "ctrl", "alt": "alt", "shift": "shift",
                       "cmd": "oskey", "oskey": "oskey", "any": "any",}
            # KeyMapItem like dict, use for comparing against
            # attr: {states, ...}
            kmi_test_dict = {}
            # Special handling of 'type' using a list if sets,
            # keymap items must match against all.
            kmi_test_type = []

            # initialize? - so if a if a kmi has a MOD assigned it wont show up.
            # ~ for kv in key_mod.values():
            # ~    kmi_test_dict[kv] = {False}

            # altname: attr
            for kk, kv in key_mod.items():
                if kk in filter_text_split:
                    filter_text_split.remove(kk)
                    kmi_test_dict[kv] = {True}

            # whats left should be the event type
            def kmi_type_set_from_string(kmi_type):
                kmi_type = kmi_type.upper()
                kmi_type_set = set()

                if kmi_type in _EVENT_TYPES:
                    kmi_type_set.add(kmi_type)

                if not kmi_type_set or len(kmi_type) > 1:
                    # replacement table
                    for event_type_map in (_EVENT_TYPE_MAP,
                                           _EVENT_TYPE_MAP_EXTRA):
                        kmi_type_test = event_type_map.get(kmi_type)
                        if kmi_type_test is not None:
                            kmi_type_set.add(kmi_type_test)
                        else:
                            # print("Unknown Type:", kmi_type)

                            # Partial match
                            for k, v in event_type_map.items():
                                if (kmi_type in k) or (kmi_type in v):
                                    kmi_type_set.add(v)
                return kmi_type_set

            for i, kmi_type in enumerate(filter_text_split):
                kmi_type_set = kmi_type_set_from_string(kmi_type)

                if not kmi_type_set:
                    return False

                kmi_test_type.append(kmi_type_set)
            # tiny optimization, sort sets so the smallest is first
            # improve chances of failing early
            kmi_test_type.sort(key=lambda kmi_type_set: len(kmi_type_set))

            # main filter func, runs many times
            def filter_func(kmi):
                for kk, ki in kmi_test_dict.items():
                    val = getattr(kmi, kk)
                    if val not in ki:
                        return False

                # special handling of 'type'
                for ki in kmi_test_type:
                    val = kmi.type
                    if val == 'NONE' or val not in ki:
                        # exception for 'type'
                        # also inspect 'key_modifier' as a fallback
                        val = kmi.key_modifier
                        if not (val == 'NONE' or val not in ki):
                            continue
                        return False

                return True

        for km, km_items in display_keymaps:
            # km = km.active()  # keyconfigs.userのkeymapが返ってくる
            layout.context_pointer_set("keymap", km)

            if filter_text:
                filtered_items = [kmi for kmi in km_items if filter_func(kmi)]
            else:
                filtered_items = km_items

            if filtered_items:
                col = layout.column()

                row = col.row()
                row.label(text=km.name, icon='DOT')

                for kmi in filtered_items:
                    self.__draw_kmi(km, kmi, col, 1)

        return True

    def __draw_hierarchy(self, display_keymaps, layout):
        from bpy_extras import keyconfig_utils
        for entry in keyconfig_utils.KM_HIERARCHY:
            self.__draw_entry(display_keymaps, entry, layout)

    def draw(self, context, layout=None, hierarchy=False, box=True):
        """キーマップアイテムの一覧を描画。
        :param context: bpy.types.Context
        :param layout: bpy.types.UILayout
        :param hierarchy: 階層表示にする
        :type hierarchy: bool
        :param box: 展開時にBoxで囲む
        :type box: bool
        """
        spref = context.space_data

        if layout is None:
            layout = self.layout
        col = layout.column()

        show_keymaps = self.show_addon_keymaps
        if show_keymaps and box:
            col = col.box()
        col.context_pointer_set('addon_preferences', self)
        sub = col.column()

        subsplit = sub.split()
        subcol = subsplit.column()

        subcolsplit = subcol.split(percentage=0.7)
        row = subcolsplit.row()

        icon = 'TRIA_DOWN' if show_keymaps else 'TRIA_RIGHT'
        row.prop(self, 'show_addon_keymaps', text='', icon=icon,
                 emboss=False)

        display_keymaps = {}
        for item in list(self.__keymap_items):
            km_name, kmi_id = item
            km = self.__get_keymap(km_name)
            for kmi in km.keymap_items:
                if kmi.id == kmi_id:
                    break
            else:
                self.__keymap_items.remove(item)
                continue
            items = display_keymaps.setdefault(km, [])
            items.append(kmi)
        for km, items in display_keymaps.items():
            ls = list(km.keymap_items)
            items.sort(key=ls.index)
        display_keymaps = list(display_keymaps.items())

        if not show_keymaps:
            row.label('{} KeyMap Items'.format(len(self.__keymap_items)))
            return

        row.separator()
        rowsub = row.split(align=True, percentage=0.33)
        # postpone drawing into rowsub, so we can set alert!

        col.separator()

        filter_type = spref.filter_type
        filter_text = spref.filter_text.strip()
        if filter_text or not hierarchy:
            filter_text = filter_text.lower()
            ok = self.__draw_filtered(display_keymaps, filter_type,
                                         filter_text, col)
        else:
            self.__draw_hierarchy(display_keymaps, col)
            ok = True

        colsub = col.split(percentage=0.2).column()
        colsub.operator("wm.kmu_keymap_item_add", text="Add New",
                        icon='ZOOMIN')

        # go back and fill in rowsub
        rowsub.prop(spref, "filter_type", text="")
        rowsubsub = rowsub.row(align=True)
        if not ok:
            rowsubsub.alert = True
        rowsubsub.prop(spref, "filter_text", text="", icon='VIEWZOOM')

        # Write / Restore
        default_km = self.__default_values
        current_km = self.__get_current_values()
        if self._KMU_IDPROP_NAME in self:
            def idprop_to_py(prop):
                if isinstance(prop, list):
                    return [idprop_to_py(p) for p in prop]
                elif hasattr(prop, 'to_dict'):
                    return prop.to_dict()
                elif hasattr(prop, 'to_list'):
                    return prop.to_list()
                else:
                    return prop
            prop = self[self._KMU_IDPROP_NAME]
            idp_km = idprop_to_py(prop)
        else:
            idp_km = None
        subcolsplitrow = subcolsplit.row().split(align=True)
        # Write
        subcolsplitrow_sub = subcolsplitrow.row(align=True)
        if current_km == default_km and self._KMU_IDPROP_NAME not in self:
            subcolsplitrow_sub.enabled = False
        else:
            subcolsplitrow_sub.enabled = current_km != idp_km
        subcolsplitrow_sub.operator('wm.kmu_keymaps_write', text='Write')
        # Restore
        subcolsplitrow_sub = subcolsplitrow.row(align=True)
        if current_km == default_km and self._KMU_IDPROP_NAME not in self:
            subcolsplitrow_sub.enabled = False
        subcolsplitrow_sub.operator('wm.kmu_keymaps_restore', text='Restore')

    # operator ------------------------------------------------------

    class __Helper:
        def get_mangling(self, attr):
            # TODO: クラス名がマングリングされていた場合はエラーとなる
            addon_prefs = bpy.context.addon_preferences
            qualname = addon_prefs._ADDON_KEY_MAP_UTILITY_QUALNAME
            prefix = '_' + qualname.split('.')[-1].lstrip('_')
            return getattr(addon_prefs, prefix + attr)

    class __Registerable(__Helper):
        @classmethod
        def register_class(cls, rename=False):
            import re
            if issubclass(cls, bpy.types.Operator):
                mod, func = cls.bl_idname.split('.')
                class_name = mod.upper() + '_OT_' + func
            elif issubclass(cls, bpy.types.Menu):
                class_name = cls.bl_idname
            else:
                class_name = cls.__name__
            if rename:
                if cls._users == 0 or not hasattr(bpy.types, class_name):
                    while hasattr(bpy.types, class_name):
                        base, num = re.match('([a-zA-Z_]+)(\d*)$',
                                             func).groups()
                        if num == '':
                            func = base + '0'
                        else:
                            func = base + str(int(num) + 1)
                        class_name = mod.upper() + '_OT_' + func
                    cls.bl_idname = mod + '.' + func
                    bpy.utils.register_class(cls)
                    cls._users = 1
                else:
                    print('{} already registered'.format(cls))
            else:
                if hasattr(bpy.types, class_name):
                    getattr(bpy.types, class_name)._users += 1
                else:
                    bpy.utils.register_class(cls)
                    cls._users = 1

        @classmethod
        def unregister_class(cls, force=False):
            if issubclass(cls, bpy.types.Operator):
                mod, func = cls.bl_idname.split('.')
                class_name = mod.upper() + '_OT_' + func
            elif issubclass(cls, bpy.types.Menu):
                class_name = cls.bl_idname
            else:
                class_name = cls.__name__
            if hasattr(bpy.types, class_name):
                other_cls = getattr(bpy.types, class_name)
                if other_cls._users > 0:
                    other_cls._users -= 1
                if force:
                    other_cls._users = 0
                if other_cls._users == 0:
                    bpy.utils.unregister_class(other_cls)
            else:
                bpy.utils.unregister_class(cls)  # 例外を出させるため

    class __WM_OT_kmu_keymap_item_add(__Registerable, bpy.types.Operator):
        bl_idname = 'wm.kmu_keymap_item_add'
        bl_label = 'Add Key Map Item'
        bl_description = 'Add key map item'

        def _get_entries():
            import bpy_extras.keyconfig_utils

            modal_keymaps = {'View3D Gesture Circle', 'Gesture Border',
                             'Gesture Zoom Border', 'Gesture Straight Line',
                             'Standard Modal Map', 'Knife Tool Modal Map',
                             'Transform Modal Map', 'Paint Stroke Modal',
                             'View3D Fly Modal', 'View3D Walk Modal',
                             'View3D Rotate Modal', 'View3D Move Modal',
                             'View3D Zoom Modal', 'View3D Dolly Modal', }

            def get():
                def _get(entry):
                    idname, spaceid, regionid, children = entry
                    if not ('INVALID_MODAL_KEYMAP' and
                                idname in modal_keymaps):
                        yield entry
                        for e in children:
                            yield from _get(e)

                for entry in bpy_extras.keyconfig_utils.KM_HIERARCHY:
                    yield from _get(entry)

            return list(get())

        keymap = bpy.props.EnumProperty(
            name='KeyMap',
            items=[(entry[0], entry[0], '') for entry in _get_entries()])

        def execute(self, context):
            km = self.get_mangling('__get_keymap')(self.keymap)
            if km.is_modal:
                kmi = km.keymap_items.new_modal(
                    propvalue='', type='A', value='PRESS')
            else:
                kmi = km.keymap_items.new(
                    idname='none', type='A', value='PRESS')
            self.get_mangling('__register_keymap_item')(kmi)
            context.area.tag_redraw()
            return {'FINISHED'}

        def invoke(self, context, event):
            if self.properties.is_property_set('keymap'):
                return self.execute(context)
            else:
                return bpy.ops.wm.call_menu(name='WM_MT_kmu_keymap_item_add')

    class __WM_OT_kmu_keymap_item_remove(__Registerable, bpy.types.Operator):
        bl_idname = 'wm.kmu_keymap_item_remove'
        bl_label = 'Remove Key Map Item'
        bl_description = 'Remove key map item'

        item_id = bpy.props.IntProperty()

        def execute(self, context):
            for kmi in context.keymap.keymap_items:
                if kmi.id == self.item_id:
                    self.get_mangling('__unregister_keymap_item')(kmi)
                    return {'FINISHED'}
            context.area.tag_redraw()
            return {'CANCELLED'}

    class __WM_OT_kmu_keymaps_write(__Registerable, bpy.types.Operator):
        bl_idname = 'wm.kmu_keymaps_write'
        bl_label = 'Write KeyMaps'
        bl_description = 'Convert key map items into ID properties ' \
                         '(necessary for \'Save User Settings\')'

        def execute(self, context):
            addon_prefs = context.addon_preferences
            value = self.get_mangling('__get_current_values')()
            addon_prefs[addon_prefs._KMU_IDPROP_NAME] = value
            return {'FINISHED'}

    class __WM_OT_kmu_keymaps_restore(__Registerable, bpy.types.Operator):
        bl_idname = 'wm.kmu_keymaps_restore'
        bl_label = 'Restore KeyMaps'
        bl_description = 'Restore key map items and clear ID properties'

        def execute(self, context):
            addon_prefs = context.addon_preferences
            self.get_mangling('__keymaps_restore')()
            if addon_prefs._KMU_IDPROP_NAME in addon_prefs:
                del addon_prefs[addon_prefs._KMU_IDPROP_NAME]
            context.area.tag_redraw()
            return {'FINISHED'}

    # menu ----------------------------------------------------------

    class __WM_MT_kmu_keymap_item_add(__Registerable, bpy.types.Menu):
        bl_idname = 'WM_MT_kmu_keymap_item_add'
        bl_label = 'Add New'

        def draw(self, context):
            import bpy_extras.keyconfig_utils

            addon_prefs = context.addon_preferences

            layout = self.layout
            column = layout.column()
            column.context_pointer_set('addon_preferences', addon_prefs)

            def get_non_modal_km_hierarchy():
                if not 'INVALID_MODAL_KEYMAP':
                    return bpy_extras.keyconfig_utils.KM_HIERARCHY

                modal_keymaps = {'View3D Gesture Circle', 'Gesture Border',
                                 'Gesture Zoom Border',
                                 'Gesture Straight Line', 'Standard Modal Map',
                                 'Knife Tool Modal Map', 'Transform Modal Map',
                                 'Paint Stroke Modal', 'View3D Fly Modal',
                                 'View3D Walk Modal', 'View3D Rotate Modal',
                                 'View3D Move Modal', 'View3D Zoom Modal',
                                 'View3D Dolly Modal'}

                def get_entry(entry):
                    idname, spaceid, regionid, children = entry
                    if idname not in modal_keymaps:
                        children_non_modal = []
                        for child in children:
                            e = get_entry(child)
                            if e:
                                children_non_modal.append(e)
                        return [idname, spaceid, regionid, children_non_modal]

                km_hierarchy = [e for e in
                                [get_entry(e) for e in
                                 bpy_extras.keyconfig_utils.KM_HIERARCHY]
                                if e]
                return km_hierarchy

            km_hierarchy = get_non_modal_km_hierarchy()

            def max_depth(entry, depth):
                idname, spaceid, regionid, children = entry
                if children:
                    d = max([max_depth(e, depth + 1) for e in children])
                    return max(depth, d)
                else:
                    return depth
            depth = 1
            for entry in bpy_extras.keyconfig_utils.KM_HIERARCHY:
                depth = max(depth, max_depth(entry, 1))

            used_keymap_names = {kmname for kmname, kmiid in
                                 self.get_mangling('__keymap_items')}

            # 左の列を全部描画してから右の列にいかないとおかしな事になる

            table = []
            def gen_table(entry, row_index, col_index):
                idname, spaceid, regionid, children = entry
                if row_index > len(table) - 1:
                    table.append([None for i in range(depth)])
                table[row_index][col_index] = idname
                if children:
                    col_index += 1
                    for e in children:
                        row_index = gen_table(e, row_index, col_index)
                else:
                    row_index += 1
                return row_index
            row_index = 0
            col_index = 0
            for entry in km_hierarchy:
                row_index = gen_table(entry, row_index, col_index)

            split_list = []
            for i, row in enumerate(table):
                if row[0] and i > 0:
                    split_list.append((column.split(), False))
                split_list.append((column.split(), True))
            for i in range(depth):
                j = 0
                for split, not_separator in split_list:
                    row = split.row()
                    if not_separator:
                        name = table[j][i]
                        if name:
                            if name in used_keymap_names:
                                icon = 'FILE_TICK'
                            else:
                                icon = 'NONE'
                            op = row.operator('wm.kmu_keymap_item_add',
                                              text=name, icon=icon)
                            op.keymap = name
                        j += 1
                    else:
                        row.separator()
