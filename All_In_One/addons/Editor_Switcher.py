'''
Copyright (C) 2015 Robert Schütze

Created by Robert Schütze

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy

bl_info = {
    "name": "Editor Switcher",
    "description": "A quick way of switching between the editor types.",
    "author": "Robert Schütze",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "Window",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame",
}
    

class EditorSwitcherMenu(bpy.types.Menu):
    bl_idname = "editor_switcher_pie_menu"
    bl_label = "Switcher"
    
    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("window.set_area_type",text="3D View",icon="VIEW3D").type="VIEW_3D"    
        pie.operator("window.set_area_type",text="Node Editor",icon="NODETREE").type="NODE_EDITOR"
        pie.operator("window.set_area_type",text="Graph Editor",icon="IPO").type="GRAPH_EDITOR"
        pie.operator("window.set_area_type",text="Text Editor",icon="TEXT").type="TEXT_EDITOR"
        pie.operator("window.set_area_type",text="UV/Image Editor",icon="IMAGE_COL").type="IMAGE_EDITOR"
        pie.operator("window.set_area_type",text="Dope Sheet",icon="ACTION").type="DOPESHEET_EDITOR"
        pie.operator("window.set_area_type",text="Logic Editor",icon="LOGIC").type="LOGIC_EDITOR"
        pie.operator("window.set_area_type",text="Video Sequence Editor",icon="SEQUENCE").type="SEQUENCE_EDITOR"


class SetAreaTypeOperator(bpy.types.Operator):
    bl_idname = "window.set_area_type"
    bl_label = ""
    bl_options = {"REGISTER"}
    type = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        context.area.type = self.type
        return {"FINISHED"}


addon_keymaps = []
def register_keymaps():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "Window",space_type='EMPTY', region_type='WINDOW')
    kmi = km.keymap_items.new("wm.call_menu_pie", type = "E",alt=True, value = "PRESS")
    kmi.properties.name = "editor_switcher_pie_menu"
    addon_keymaps.append(km)
    
def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
            
def register():
    register_keymaps()
    bpy.utils.register_module(__name__)

def unregister():
    unregister_keymaps()
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
