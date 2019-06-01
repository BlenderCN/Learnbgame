#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

import bpy

from .utils_python import reverse_enumerate
from .bpy_inspect import BlRna

class InputKeyMonitor:
    all_keys = bpy.types.Event.bl_rna.properties["type"].enum_items.keys()
    all_modifiers = {'alt', 'ctrl', 'oskey', 'shift'}
    all_events = bpy.types.Event.bl_rna.properties["value"].enum_items.keys()
    
    def __init__(self, event=None):
        self.event = ""
        self.states = {}
        self.invoke_key = 'NONE'
        self.invoke_event = 'NONE'
        if event is not None:
            self.invoke_key = event.type
            self.invoke_event = event.value
            self.update(event)
    
    def __getitem__(self, name):
        if ":" in name:
            return self.event == name
        return self.states.setdefault(name, False)
    
    def __setitem__(self, name, state):
        self.states[name] = state
    
    def update(self, event):
        if (event.value == 'PRESS') or (event.value == 'DOUBLE_CLICK'):
            self.states[event.type] = True
        elif event.value == 'RELEASE':
            self.states[event.type] = False
        
        self.states['alt'] = event.alt
        self.states['ctrl'] = event.ctrl
        self.states['oskey'] = event.oskey
        self.states['shift'] = event.shift
        
        self.event = event.type+":"+event.value
    
    def keychecker(self, keys):
        km = self
        keys = self.parse_keys(keys)
        def check(state=True):
            for key in keys:
                if key.startswith("!"):
                    if km[key[1:]] != state:
                        return True
                else:
                    if km[key] == state:
                        return True
            return False
        check.is_event = ((":" in keys[0]) if keys else False)
        return check
    
    def combine_key_parts(self, key, keyset, use_invoke_key=False):
        elements = key.split()
        combined0 = "".join(elements)
        combined1 = "_".join(elements)
        
        if use_invoke_key and (combined0 == "{INVOKEKEY}"):
            return self.invoke_key
        
        if combined0 in keyset:
            return combined0
        elif combined1 in keyset:
            return combined1
        
        return ""
    
    def parse_keys(self, keys_string):
        parts = keys_string.split(":")
        keys_string = parts[0]
        event_id = ""
        if len(parts) > 1:
            event_id = self.combine_key_parts(parts[1].upper(), self.all_events)
            if event_id:
                event_id = ":"+event_id
        
        keys = []
        for key in keys_string.split(","):
            key = key.strip()
            is_negative = key.startswith("!")
            prefix = ""
            if is_negative:
                key = key[1:]
                prefix = "!"
            
            key_id = self.combine_key_parts(key.upper(), self.all_keys, True)
            modifier_id = self.combine_key_parts(key.lower(), self.all_modifiers)
            
            if key_id:
                keys.append(prefix+key_id+event_id)
            elif modifier_id:
                if len(event_id) != 0:
                    modifier_id = modifier_id.upper()
                    if modifier_id == 'OSKEY': # has no left/right/ndof variants
                        keys.append(prefix+modifier_id+event_id)
                    else:
                        keys.append(prefix+"LEFT_"+modifier_id+event_id)
                        keys.append(prefix+"RIGHT_"+modifier_id+event_id)
                        keys.append(prefix+"NDOF_BUTTON_"+modifier_id+event_id)
                else:
                    keys.append(prefix+modifier_id)
        
        return keys

class ModeStack:
    def __init__(self, keys, transitions, default_mode, mode='NONE'):
        self.keys = keys
        self.prev_state = {}
        self.transitions = set(transitions)
        self.mode = mode
        self.default_mode = default_mode
        self.stack = [self.default_mode] # default mode should always be in the stack!
    
    def update(self):
        for name in self.keys:
            keychecker = self.keys[name]
            is_on = int(keychecker())
            
            if keychecker.is_event:
                delta_on = is_on * (-1 if name in self.stack else 1)
            else:
                delta_on = is_on - self.prev_state.get(name, 0)
                self.prev_state[name] = is_on
            
            if delta_on > 0:
                if self.transition_allowed(self.mode, name):
                    self.remove(name)
                    self.stack.append(name) # move to top
                    self.mode = name
            elif delta_on < 0:
                if self.mode != name:
                    self.remove(name)
                else:
                    self.find_transition()
    
    def remove(self, name):
        if name in self.stack:
            self.stack.remove(name)
    
    def find_transition(self):
        for i in range(len(self.stack)-1, -1, -1):
            name = self.stack[i]
            if self.transition_allowed(self.mode, name):
                self.mode = name
                self.stack = self.stack[:i+1]
                break
    
    def transition_allowed(self, mode0, mode1):
        is_allowed = (mode0+":"+mode1) in self.transitions
        is_allowed |= (mode1+":"+mode0) in self.transitions
        return is_allowed
    
    def add_transitions(self, transitions):
        self.transitions.update(transitions)
    
    def remove_transitions(self, transitions):
        self.transitions.difference_update(transitions)

class KeyMapUtils:
    keymap_categories = [
        ['Window'],
        ['Screen', 'Screen Editing'],
        ['View2D'],
        ['View2D Buttons List'],
        ['Header'],
        ['Grease Pencil'],
        ['3D View', 'Object Mode', 'Mesh', 'Curve', 'Armature', 'Metaball', 'Lattice', 'Font', 'Pose', 'Vertex Paint', 'Weight Paint', 'Weight Paint Vertex Selection', 'Face Mask', 'Image Paint', 'Sculpt', 'Particle', 'Knife Tool Modal Map', 'Paint Stroke Modal', 'Object Non-modal', 'View3D Walk Modal', 'View3D Fly Modal', 'View3D Rotate Modal', 'View3D Move Modal', 'View3D Zoom Modal', 'View3D Dolly Modal', '3D View Generic'],
        ['Frames'],
        ['Markers'],
        ['Animation'],
        ['Animation Channels'],
        ['Graph Editor', 'Graph Editor Generic'],
        ['Dopesheet'],
        ['NLA Editor', 'NLA Channels', 'NLA Generic'],
        ['Image', 'UV Editor', 'Image Paint', 'UV Sculpt', 'Image Generic'],
        ['Timeline'],
        ['Outliner'],
        ['Node Editor', 'Node Generic'],
        ['Sequencer', 'SequencerCommon', 'SequencerPreview'],
        ['Logic Editor'],
        ['File Browser', 'File Browser Main', 'File Browser Buttons'],
        ['Info'],
        ['Property Editor'],
        ['Text', 'Text Generic'],
        ['Console'],
        ['Clip', 'Clip Editor', 'Clip Graph Editor', 'Clip Dopesheet Editor', 'Mask Editing'],
        ['View3D Gesture Circle'],
        ['Gesture Straight Line'],
        ['Gesture Zoom Border'],
        ['Gesture Border'],
        ['Standard Modal Map'],
        ['Transform Modal Map'],
        ['Paint Curve'], # This one seems to be absent in the UI, so I don't know where it belongs
    ]
    
    @staticmethod
    def search(idname, place=None):
        """Iterate over keymap items with given idname. Yields tuples (keyconfig, keymap, keymap item)"""
        place_is_str = isinstance(place, str)
        keymaps = None
        keyconfigs = bpy.context.window_manager.keyconfigs
        if isinstance(place, bpy.types.KeyMap):
            keymaps = (place,)
            keyconfigs = (next((kc for kc in keyconfigs if place.name in kc), None),)
        elif isinstance(place, bpy.types.KeyConfig):
            keyconfigs = (place,)
        
        for kc in keyconfigs:
            for km in keymaps or kc.keymaps:
                if place_is_str and (km.name != place):
                    continue
                for kmi in km.keymap_items:
                    if kmi.idname == idname:
                        yield (kc, km, kmi)
    
    @staticmethod
    def exists(idname, place=None):
        return bool(next(KeyMapUtils.search(idname), False))
    
    @staticmethod
    def set_active(idname, active, place=None):
        for kc, km, kmi in KeyMapUtils.search(idname, place):
            kmi.active = active
    
    @staticmethod
    def remove(idname, user_defined=True, user_modified=True, place=None):
        for kc, km, kmi in list(KeyMapUtils.search(idname, place)):
            if (not user_defined) and kmi.is_user_defined:
                continue
            if (not user_modified) and kmi.is_user_modified:
                continue
            km.keymap_items.remove(kmi)
    
    @staticmethod
    def index(km, idname):
        for i, kmi in enumerate(km.keymap_items):
            if kmi.idname == idname:
                return i
        return -1
    
    @staticmethod
    def normalize_event_type(event_type):
        if event_type == 'ACTIONMOUSE':
            userprefs = bpy.context.user_preferences
            select_mouse = userprefs.inputs.select_mouse
            return ('RIGHTMOUSE' if select_mouse == 'LEFT' else 'LEFTMOUSE')
        elif event_type == 'SELECTMOUSE':
            userprefs = bpy.context.user_preferences
            select_mouse = userprefs.inputs.select_mouse
            return ('LEFTMOUSE' if select_mouse == 'LEFT' else 'RIGHTMOUSE')
        return event_type
    
    @staticmethod
    def equal(kmi, event, pressed_keys=[]):
        """Test if event corresponds to the given keymap item"""
        modifier_match = (kmi.key_modifier == 'NONE') or (kmi.key_modifier in pressed_keys)
        modifier_match &= kmi.any or ((kmi.alt == event.alt) and (kmi.ctrl == event.ctrl)
            and (kmi.shift == event.shift) and (kmi.oskey == event.oskey))
        kmi_type = KeyMapUtils.normalize_event_type(kmi.type)
        event_type = KeyMapUtils.normalize_event_type(event.type)
        return ((kmi_type == event_type) and (kmi.value == event.value) and modifier_match)
    
    @staticmethod
    def clear(ko):
        if isinstance(ko, bpy.types.KeyMap):
            ko = ko.keymap_items
        elif isinstance(ko, bpy.types.KeyConfig):
            ko = ko.keymaps
        elif isinstance(ko, bpy.types.WindowManager):
            ko = ko.keyconfigs
        
        while len(ko) != 0:
            ko.remove(ko[0])
    
    @staticmethod
    def serialize(ko):
        if isinstance(ko, bpy.types.KeyMapItem):
            kmi = ko # also: kmi.map_type ? (seems that it's purely derivative)
            return dict(idname=kmi.idname, propvalue=kmi.propvalue,
                type=kmi.type, value=kmi.value, any=kmi.any,
                shift=kmi.shift, ctrl=kmi.ctrl, alt=kmi.alt,
                oskey=kmi.oskey, key_modifier=kmi.key_modifier,
                active=kmi.active, show_expanded=kmi.show_expanded,
                id=kmi.id, properties=BlRna.serialize(kmi.properties, ignore_default=True))
        elif isinstance(ko, bpy.types.KeyMap):
            km = ko
            return dict(name=km.name, space_type=km.space_type, region_type=km.region_type,
                is_modal=km.is_modal, is_user_modified=km.is_user_modified,
                show_expanded_children=km.show_expanded_children,
                keymap_items=[KeyMapUtils.serialize(kmi) for kmi in km.keymap_items])
        elif isinstance(ko, bpy.types.KeyConfig):
            kc = ko
            return dict(name=kc.name, keymaps=[KeyMapUtils.serialize(km) for km in kc.keymaps])
    
    @staticmethod
    def deserialize(ko, data, head=False):
        # keymap_items / keymaps / keyconfigs are reported as just "bpy_prop_collection" type
        if isinstance(ko, bpy.types.KeyMap):
            if ko.is_modal:
                kmi = ko.keymap_items.new_modal(data["propvalue"], data["type"], data["value"], any=data.get("any", False),
                    shift=data.get("shift", False), ctrl=data.get("ctrl", False), alt=data.get("alt", False),
                    oskey=data.get("oskey", False), key_modifier=data.get("key_modifier", 'NONE'))
            else:
                kmi = ko.keymap_items.new(data["idname"], data["type"], data["value"], any=data.get("any", False),
                    shift=data.get("shift", False), ctrl=data.get("ctrl", False), alt=data.get("alt", False),
                    oskey=data.get("oskey", False), key_modifier=data.get("key_modifier", 'NONE'), head=head)
            kmi.active = data.get("active", True)
            kmi.show_expanded = data.get("show_expanded", False)
            BlRna.deserialize(kmi.properties, data.get("properties", {}), suppress_errors=True)
        elif isinstance(ko, bpy.types.KeyConfig):
            # Note: for different modes, different space_type are required!
            # e.g. 'VIEW_3D' for "3D View", and 'EMPTY' for "Sculpt"
            km = ko.keymaps.new(data["name"], space_type=data.get("space_type", 'EMPTY'),
                region_type=data.get("region_type", 'WINDOW'), modal=data.get("is_modal", False))
            km.is_user_modified = data.get("is_user_modified", False)
            km.show_expanded_children = data.get("show_expanded_children", False)
            for kmi_data in data.get("keymap_items", []):
                KeyMapUtils.deserialize(km, kmi_data)
        elif isinstance(ko, bpy.types.WindowManager):
            kc = ko.keyconfigs.new(data["name"])
            for km_data in data.get("keymaps", []):
                KeyMapUtils.deserialize(kc, km_data)
    
    @staticmethod
    def insert(km, kmi_datas):
        if not kmi_datas:
            return
        
        km_items = [KeyMapUtils.serialize(kmi) for kmi in km.keymap_items]
        
        def insertion_index(idnames, to_end):
            if "*" in idnames:
                return (len(km_items)-1 if to_end else 0)
            for i, kmi_data in (reverse_enumerate(km_items) if to_end else enumerate(km_items)):
                if kmi_data["idname"] in idnames:
                    return i
            return None
        
        src_count = len(km.keymap_items)
        only_append = True
        for after, kmi_data, before in kmi_datas:
            i_after = (insertion_index(after, True) if after else None)
            i_before = (insertion_index(before, False) if before else None)
            
            if (i_before is None) and (i_after is None):
                i = len(km_items)
            elif i_before is None:
                i = i_after+1
            elif i_after is None:
                i = i_before
            else:
                i = (i_after+1 if "*" not in after else i_before)
            
            only_append &= (i >= src_count)
            
            km_items.insert(i, kmi_data)
        
        if only_append:
            for kmi_data in km_items[src_count:]:
                KeyMapUtils.deserialize(km, kmi_data)
        else:
            KeyMapUtils.clear(km)
            for kmi_data in km_items:
                KeyMapUtils.deserialize(km, kmi_data)
