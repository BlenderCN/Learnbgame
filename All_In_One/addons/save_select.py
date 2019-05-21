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
    "name": "Save Selection",
    "description": "Allows you to save temporally the selected vertices",
    "author": "David Velasquez",
    "version": (0, 1),
    "blender": (2, 65, 0),
    "location": "Select",
    "warning": "",
    "category": "Mesh"
}

import bpy

l = []

class SaveSelection(bpy.types.Operator):
    """Temporally save the selected vertices"""
    bl_idname = "object.saveselectedvertices"
    bl_label = "Save Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        C = bpy.context
        ob = C.active_object
        save_select(ob)
        return {'FINISHED'}
        
class GetSelection(bpy.types.Operator):
    """Select the temporally saved vertices"""
    bl_idname = "object.getsavedvertices"
    bl_label = "Get Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        C = bpy.context
        global l
        get_select(l)
        return {'FINISHED'}

class SaveSelectMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_save_select_menu"
    bl_label = "Save or Get Select Vertices"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("object.saveselectedvertices", text="Save Selected Vertices")
        layout.operator("object.getsavedvertices", text="Get Selected Vertices")

def save_select(ob):
    sel = []
    for vertice in ob.data.vertices:
        if vertice.select:
            sel.append(vertice.index)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    global l
    l = sel
    return {'FINISHED'}
            
def get_select(l):
    C = bpy.context
    ob = C.active_object
    for index in l:
        ob.data.vertices[index].select = True

def draw_item(self, context):
    layout = self.layout
    layout.menu(SaveSelectMenu.bl_idname)
    
def register():
    #init_properties()
    bpy.utils.register_class(SaveSelection)
    bpy.utils.register_class(GetSelection)
    bpy.utils.register_class(SaveSelectMenu)
    bpy.types.VIEW3D_MT_select_object.append(draw_item)
    
    
def unregister():
    #clear_properties()
    bpy.utils.unregister_class(SaveSelection)
    bpy.utils.unregister_class(GetSelection)
    bpy.utils.unregister_class(SaveSelectMenu)
    bpy.types.VIEW3D_MT_select_object.remove(draw_item)   
    
if __name__ == "__main__":
    register()