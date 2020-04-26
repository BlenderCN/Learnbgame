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

# <pep8-80 compliant>

import bpy

class ModalHelper():
    def __init__(self):
        # Map a domain of events to the corresponding range of keymap items.
        self.event_map = dict()

        # Store a list of tasks to execute during each iteration of a modal
        # method's event loop.
        self.queue = list()

    def generate_event_map(self, keymap_names = list(), operator_ids = set()):
        # Create a mapping between events and the respective keymap items.  
        # Supplying keymap names and operator ids filters the map to include
        # only event mappings from certain keymaps for particular operators.
        event_map = self.event_map
        keyconfig = bpy.context.window_manager.keyconfigs['Blender User']
        available_keymaps = keyconfig.keymaps

        # If the keymap names are unspecified, search all available keymaps.
        if not keymap_names:
            keymap_names = [keymap.name for keymap in available_keymaps]

        # Search each keymap for the specified operators.
        for name in keymap_names:
            if name in available_keymaps:
                keymap = available_keymaps[name]

                # If a keymap item is found to be associated with one of the
                # operators, map the event to the keymap item.
                if operator_ids:
                    partial_event_map = {(
                            keymap_item.alt, keymap_item.ctrl,
                            keymap_item.oskey, keymap_item.shift,
                            keymap_item.type, keymap_item.value
                        ) : keymap_item
                        for keymap_item in keymap.keymap_items
                        if keymap_item.idname in operator_ids
                    }

                # If no operators are specified, map events for all items in
                # the keymap.
                else:
                    partial_event_map = {(
                            keymap_item.alt, keymap_item.ctrl,
                            keymap_item.oskey, keymap_item.shift,
                            keymap_item.type, keymap_item.value
                        ) : keymap_item
                        for keymap_item in keymap.keymap_items
                    }

                event_map.update(partial_event_map)

    def reset(self):
        self.__init__()