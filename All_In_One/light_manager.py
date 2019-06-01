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


import bpy, random

bl_info = {
    "name": "Lighting Manager",
    "description": "Simplifies using 3-Point-Lighting etc.",
    "author": "Jacques Lucke",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D",
    "warning": "This is a not-tested-program",
    "wiki_url": "",
    "category": "Learnbgame",
}
    

class LightingPanel(bpy.types.Panel):
    bl_idname = "LightingPanel"
    bl_label = "Lighting"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("light.create", text = "Create")
        
        for object in context.scene.objects:
            if not object.name.endswith("lamp"): continue
            
            box = layout.box()
            row = box.row(align = True)
            row.prop(object, "[\"setup_name\"]", text = "Name")
            op = row.operator("light.remove", text = "", icon = "X")
            op.name = object["setup_name"]
            
            empty = get_corresponding_empty(object)
            col = box.column(align = True)
            col.prop(empty, "rotation_euler", index = 2, text = "Rotation")
            col.prop(object, "location", index = 0, text = "Distance")
            col.prop(object, "location", index = 2, text = "Height")
            
            col = box.column(align = True)
            col.prop(object.data, "color", text = "Color")
            col.prop(object.data, "shadow_soft_size", text = "Softness")
        
        
class CreateLightSetup(bpy.types.Operator):
    bl_idname = "light.create"
    bl_label = "Lighting"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        create_single_light_setup(bpy.context.active_object, "light1", 5, 0.2, 2)
        return {"FINISHED"}
    
class RemoveSetup(bpy.types.Operator):
    bl_idname = "light.remove"
    bl_label = "Remove"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    name = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        for object in context.scene.objects:
            if "setup_name" in object:
                if object["setup_name"] == self.name:
                    lamp = object
                    empty = get_corresponding_empty(lamp)
                    remove(lamp)
                    remove(empty)
        return {"FINISHED"}
            
  
def get_corresponding_empty(lamp):
    try:
        return lamp.constraints[0].target
    except: return None   

def remove(object):
    bpy.context.scene.objects.unlink(object) 
    
def create_single_light_setup(target, name, distance, rotation, height):
    rand = str(round(random.random()*1000))
    empty = create_empty(name + rand + "empty")
    lamp = create_lamp(name + rand + "lamp", type = "SUN")
    lamp.location = [distance, 0, height]
    empty.rotation_euler[2] = rotation
     
    parent(empty, target)
    parent(lamp, empty)
    
    trackto(lamp, target)
    
    
def create_lamp(name, type):
    lamp_data = bpy.data.lamps.new(name = name, type = type)
    lamp = bpy.data.objects.new(name = name, object_data = lamp_data)
    lamp["setup_name"] = name
    bpy.context.scene.objects.link(lamp)
    return lamp   

def create_empty(name):
    empty = bpy.data.objects.new(name = name, object_data = None)
    bpy.context.scene.objects.link(empty)
    return empty 

def parent(child, parent):
    constraint = child.constraints.new(type = "CHILD_OF")
    constraint.target = parent
    
def trackto(child, parent):
    constraint = child.constraints.new(type = "TRACK_TO")
    constraint.target = parent
    constraint.up_axis = "UP_X"
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
        
                