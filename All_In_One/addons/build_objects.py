'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

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
    "name": "Build Meshes",
    "description": "Build all selected Meshes using a build modifier",
    "author": "Your Name",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Learnbgame"
}
    

class BuildMeshesOperator(bpy.types.Operator):
    bl_idname = "mesh.build"
    bl_label = "Build selected objects"
    bl_description = ""
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        for object in bpy.context.selected_objects:
            bpy.context.scene.objects.active = object
            bpy.ops.object.mode_set(mode = "EDIT")
            bpy.ops.mesh.select_mode(type = "FACE")
            bpy.ops.mesh.select_all(action = "SELECT")
            bpy.ops.mesh.sort_elements(type = "CURSOR_DISTANCE")
            bpy.ops.object.mode_set(mode = "OBJECT")
            
            modifier_name = "build modifier"
            # remove existing modifier
            if modifier_name in object.modifiers:
                object.modifiers.remove(object.modifiers[modifier_name])
                
            object.modifiers.new(type = "BUILD", name = modifier_name)
        return {"FINISHED"}
    
class BuildMeshesPanel(bpy.types.Panel):
    bl_idname = "BuildMeshesPanel"
    bl_label = "Build Meshes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.build")
        
        
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
            
            
        