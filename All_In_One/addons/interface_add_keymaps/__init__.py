# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#   the Free Software Foundation Inc.
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "custom keymapper",
    "author": "zeffii",
    "version": (0, 1, 0),
    "blender": (2, 6, 1),
    "location": "3diview, in mesh edit mode",
    "description": "Adds 1,2,3 as vert/edge/face selection.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy

def set_custom_keymaps(context):
    wm = context.window_manager

    # ------- set possible conflicting keymaps to inactive
    if True:
        deactivate_list = ['ONE', 'TWO', 'THREE']
        view3d_km_items = wm.keyconfigs.default.keymaps['3D View'].keymap_items
        for j in view3d_km_items:
            if j.type in deactivate_list and j.name == 'Layers':
                j.active = False

    # ------- set new useful keymaps
    if True:
        my_keymap = {   'ONE': "True, False, False", 
                        'TWO': "False, True, False", 
                        'THREE': "False, False, True"}
        
        km = wm.keyconfigs.default.keymaps['Mesh']
        for k, v in my_keymap.items():
            new_shortcut = km.keymap_items.new('wm.context_set_value', k, 'PRESS')
            new_shortcut.properties.data_path = 'tool_settings.mesh_select_mode'
            new_shortcut.properties.value = v
        
    print('complete')


class DesiredKeymapsPutter(bpy.types.Operator):
    bl_idname = "scene.place_keymaps"
    bl_label = "Custom keymaps (one shot)"

    def execute(self, context):
        set_custom_keymaps(context)
        return{'FINISHED'}



def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()