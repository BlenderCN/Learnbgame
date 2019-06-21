import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
)
from .dynamic_property_group import DynamicPropertyGroup

KMI_MAP_TYPES = ('KEYBOARD', 'MOUSE', 'TWEAK', 'NDOF', 'TEXTINPUT', 'TIMER')


key_items = [
    (i.identifier, i.name, "", i.value)
    for k, i in bpy.types.Event.bl_rna.properties["type"].enum_items.items()
]
value_items = [
    ('PRESS', "Click", "", 'MESH_CIRCLE', 0),
    ('DOUBLE_CLICK', "Double Click", "", 'ROTACTIVE', 1),
]


def _hotkey_update(self, context):
    if self.hasvar("kmis"):
        for kmi in self.getvar("kmis"):
            self.to_kmi(kmi)

    if self.hasvar("update"):
        try:
            self.getvar("update")(self, context)
        except:
            pass


class Hotkey(DynamicPropertyGroup):
    key = EnumProperty(
        items=key_items, description="Key pressed", update=_hotkey_update)
    ctrl = BoolProperty(
        description="Ctrl key pressed", update=_hotkey_update)
    shift = BoolProperty(
        description="Shift key pressed", update=_hotkey_update)
    alt = BoolProperty(
        description="Alt key pressed", update=_hotkey_update)
    oskey = BoolProperty(
        description="Operating system key pressed", update=_hotkey_update)
    any = BoolProperty(
        description="Any modifier keys pressed", update=_hotkey_update)
    key_mod = EnumProperty(
        items=key_items,
        description="Regular key pressed as a modifier",
        update=_hotkey_update)
    value = EnumProperty(
        name="Value", description="Mode",
        items=value_items, update=_hotkey_update)

    def init(
            self,
            key, ctrl=False, shift=False, alt=False, oskey=False, any=False,
            key_mod='NONE', value='PRESS'):
        self.key = key
        self.ctrl = ctrl
        self.shift = shift
        self.alt = alt
        self.oskey = oskey
        self.any = any
        self.key_mod = key_mod
        self.value = value

    def clear(self):
        self.value = 'PRESS'
        self.key = 'NONE'
        self.ctrl = False
        self.shift = False
        self.alt = False
        self.any = False
        self.oskey = False
        self.key_mod = 'NONE'

    def add_kmi(self, kmi):
        if not self.hasvar("kmis"):
            self.setvar("kmis", [])

        self.getvar("kmis").append(kmi)

    def check_event(self, event, key=True):
        return (not key or self.key == event.type) and \
            self.ctrl == event.ctrl and \
            self.shift == event.shift and \
            self.alt == event.alt and \
            self.oskey == event.oskey

    def draw(
            self, layout, context,
            ctrl=True, shift=True, alt=True, oskey=True, key_mod=True,
            value=True, active=True, label=None):
        box = layout
        col = box.column(True)

        if label:
            col.label(label)

        row = col.row(True)
        if active and self.hasvar("kmis"):
            kmi = self.getvar("kmis") and self.getvar("kmis")[0]
            if kmi:
                row.prop(kmi, "active", "", icon='CHECKBOX_DEHLT', toggle=True)
        if value:
            row.prop(self, "value", "")
        row.prop(self, "key", "", event=True)

        row = col.row(True)
        if ctrl:
            row.prop(self, "ctrl", "Ctrl", toggle=True)
        if shift:
            row.prop(self, "shift", "Shift", toggle=True)
        if alt:
            row.prop(self, "alt", "Alt", toggle=True)
        if oskey:
            row.prop(self, "oskey", "OSKey", toggle=True)
        if key_mod:
            row.prop(self, "key_mod", "", event=True)

    def encode(self):
        # if not self.key or self.key == 'NONE':
        #     return ''

        hotkey = ''
        if self.ctrl:
            hotkey += 'ctrl+'
        if self.shift:
            hotkey += 'shift+'
        if self.alt:
            hotkey += 'alt+'
        if self.oskey:
            hotkey += 'oskey+'
        if self.key_mod and self.key_mod != 'NONE':
            hotkey += self.key_mod + "+"
        hotkey += self.key

        if hotkey:
            hotkey = "%s:%s" % (self.value, hotkey)

        return hotkey

    def decode(self, value):
        mode, _, value = value.partition(":")
        if not value:
            return

        self.value = mode

        parts = value.upper().split("+")

        ctrl = 'CTRL' in parts
        if ctrl:
            parts.remove('CTRL')

        alt = 'ALT' in parts
        if alt:
            parts.remove('ALT')

        shift = 'SHIFT' in parts
        if shift:
            parts.remove('SHIFT')

        oskey = 'OSKEY' in parts
        if oskey:
            parts.remove('OSKEY')

        key_mod = 'NONE' if len(parts) == 1 else parts[0]
        key = parts[-1]

        enum_items = bpy.types.Event.bl_rna.properties["type"].enum_items
        if key_mod not in enum_items:
            key_mod = 'NONE'
        if key not in enum_items:
            key = 'NONE'

        self.key = key
        self.ctrl = ctrl
        self.shift = shift
        self.alt = alt
        self.oskey = oskey
        self.key_mod = key_mod

        _hotkey_update(self, bpy.context)


    def from_kmi(
            self, kmi,
            key=None, ctrl=None, shift=None, alt=None, oskey=None,
            key_mod=None, value=None):
        self.key = kmi.type if key is None else key
        self.ctrl = kmi.ctrl if ctrl is None else ctrl
        self.shift = kmi.shift if shift is None else shift
        self.alt = kmi.alt if alt is None else alt
        self.oskey = kmi.oskey if oskey is None else oskey
        self.key_mod = kmi.key_modifier if key_mod is None else key_mod
        self.value = kmi.value if value is None else value

    def to_kmi(
            self, kmi,
            key=None, ctrl=None, shift=None, alt=None, oskey=None,
            key_mod=None, value=None):

        for map_type in KMI_MAP_TYPES:
            try:
                kmi.type = self.key if key is None else key
                break
            except TypeError:
                kmi.map_type = map_type

        kmi.ctrl = self.ctrl if ctrl is None else ctrl
        kmi.shift = self.shift if shift is None else shift
        kmi.alt = self.alt if alt is None else alt
        kmi.oskey = self.oskey if oskey is None else oskey
        kmi.key_modifier = self.key_mod if key_mod is None else key_mod
        kmi.value = self.value if value is None else value

    def update(self, context):
        pass

    def __str__(self):
        if self.key == 'NONE':
            return 'NONE'

        keys = []
        if self.ctrl:
            keys.append("Ctrl")
        if self.shift:
            keys.append("Shift")
        if self.alt:
            keys.append("Alt")
        if self.oskey:
            keys.append("OSKey")
        if self.key_mod != 'NONE':
            keys.append(self.key_mod)
        keys.append(self.key)
        return " + ".join(keys)


class Hotkeys():

    @staticmethod
    def inst():
        if not hasattr(Hotkeys, "_inst"):
            Hotkeys._inst = Hotkeys()
        return Hotkeys._inst

    def __init__(self):
        self.items = {}
        self.km = None

    def keymap(self, name="Window", space_type='EMPTY', region_type='WINDOW'):
        self.km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            name, space_type, region_type)

    def add(
            self, idname,
            key='NONE',
            ctrl=False, shift=False, alt=False, oskey=False, any=False,
            key_mod='NONE', value='PRESS', hotkey=None, **props):

        if hotkey:
            key, ctrl, shift, alt, oskey, any, key_mod, value = \
                hotkey.key, hotkey.ctrl, hotkey.shift, hotkey.alt, \
                hotkey.oskey, hotkey.any, hotkey.key_mod, hotkey.value

        item = self.km.keymap_items.new(
            idname, key, value,
            ctrl=ctrl, shift=shift, alt=alt, oskey=oskey, any=any,
            key_modifier=key_mod)

        if hotkey:
            hotkey.add_kmi(item)

        if props:
            for p in props.keys():
                setattr(item.properties, p, props[p])

        if self.km.name not in self.items:
            self.items[self.km.name] = []
        self.items[self.km.name].append(item)

        return item

    def remove(self, item):
        self.km.keymap_items.remove(item)

    def keymap_items(self):
        for kmis in self.items.values():
            for kmi in kmis:
                yield kmi

    def clear(self):
        keymaps = bpy.context.window_manager.keyconfigs.addon.keymaps
        for k, v in self.items.items():
            if k in keymaps:
                for item in v:
                    keymaps[k].keymap_items.remove(item)

        self.items.clear()


hotkeys = Hotkeys()


def unregister():
    hotkeys.clear()