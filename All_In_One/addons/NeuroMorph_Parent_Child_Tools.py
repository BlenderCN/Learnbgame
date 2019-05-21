#    NeuroMorph_Parent_Child_Tools.py (C) 2016,  Anne Jorstad
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

bl_info = {  
    "name": "NeuroMorph Parent-Child Tools",
    "author": "Anne Jorstad",
    "version": (0, 1, 0),
    "blender": (2, 7, 7),
    "location": "View3D > NeuroMorph > Parent-Child Tools",
    "description": "Parent-Child Tools",
    "warning": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Learnbgame"
}  
  
import bpy
from bpy.props import *
from mathutils import Vector  
import mathutils
import math
import os
import sys
import re
from os import listdir
import copy
import numpy as np  # must have Blender > 2.7

# Define the panel
class ParentChildPanel(bpy.types.Panel):
    bl_label = "Parent-Child Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):

        # From Proximity Analysis
        split = self.layout.row().split(percentage=0.5)
        col1 = split.column()
        col1.operator("object.show_children", text='Show Children')
        col2 = split.column()
        col2.operator("object.hide_children", text='Hide Children')

        # New
        split = self.layout.row().split(percentage=0.5)
        col1 = split.column()
        col1.operator("object.select_children", text='Select Children')

        # From Measurement Tools
        col2 = split.column()
        col2.operator("mesh.delete_all_children", text = "Delete Children")

        # From Stack Notation
        row = self.layout.row()
        row.operator_menu_enum("object.assign_parent", "select_objects", text = "Assign Parent Object")




# Show/Hide children of active object
class ShowChildren(bpy.types.Operator):
    """Show all children of active object"""
    bl_idname = "object.show_children"
    bl_label = "Show all children of active object"

    def execute(self, context):
        active_ob = bpy.context.object
        children = [ob for ob in bpy.context.scene.objects if ob.parent == active_ob]
        for ob in children:
            ob.hide = False
        return {'FINISHED'}

class HideChildren(bpy.types.Operator):
    """Hide all children of active object"""
    bl_idname = "object.hide_children"
    bl_label = "Hide all children of active object"

    def execute(self, context):
        active_ob = bpy.context.object
        children = [ob for ob in bpy.context.scene.objects if ob.parent == active_ob]
        for ob in children:
            ob.hide = True
        return {'FINISHED'}


# Select children of active object
class SelectChildren(bpy.types.Operator):
    """Select all children of active object"""
    bl_idname = "object.select_children"
    bl_label = "Select all children of active object"

    def execute(self, context):
        active_ob = bpy.context.object
        children = [ob for ob in bpy.context.scene.objects if ob.parent == active_ob]
        bpy.ops.object.select_all(action='DESELECT')
        for ob in children:
            ob.select = True
        return {'FINISHED'}


# Delete children of active object
class DeleteChildren(bpy.types.Operator):
    """Delete all children of active object (parent must be visible)"""
    bl_idname = "mesh.delete_all_children"
    bl_label = "Delete all children of active object (parent must be visible)"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT') 
        ob = bpy.context.object
        bpy.ops.object.select_all(action='DESELECT')

        for child in ob.children:
            child.hide = False
            child.select = True
            bpy.context.scene.objects.active = child  
            bpy.ops.object.delete()

        return {'FINISHED'}


# Assign parent object to all selected objects
class AssignParentObject(bpy.types.Operator):
    '''Assign chosen object as parent to all selected objects'''
    bl_idname = "object.assign_parent"
    bl_label = "Assign Parent Object"

    def available_objects(self,context):
        objs_to_ignore = ["Camera", "Lamp", "Image", "ImageStackLadder"]
        items = [(str(i),x.name,x.name) for i,x in enumerate(bpy.data.objects) if x.parent is None and x.name not in objs_to_ignore]
        return items
    select_objects = bpy.props.EnumProperty(items = available_objects, name = "Available Objects")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
    
    def execute(self,context):
        active_obs = [ob for ob in bpy.data.objects if ob.select == True]

        # The active object will be the parent of all selected objects
        the_parent = bpy.data.objects[int(self.select_objects)]
        bpy.context.scene.objects.active = the_parent
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        for ob in active_obs:
            ob.parent = the_parent

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].show_relationship_lines = False
        return {'FINISHED'}  




if __name__ == "__main__":
    register()

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
