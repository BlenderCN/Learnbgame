#!BPY

# Copyright (c) <2013> Daniel Peterson
# License: MIT Software License <www.mini3d.org/license>


import bpy
import sys
import struct
import math
import mathutils

from .panels import AttributeProperty

def getMini3dScene():
    mini3dScene = bpy.data.scenes.get("Mini3d Settings")
    if mini3dScene is None:
        mini3dScene = bpy.data.scenes.new("Mini3d Settings")

    return mini3dScene

class EXPORT_UL_list(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, translate=False, icon_value=icon)
            layout.prop(item, "export", text="")

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class ExportM3DOperator(bpy.types.Operator):
    """
    Export to Mini3d format (.m3d)
    """
    bl_idname = "export.m3d"
    bl_label = "ExportM3D"
    filepath = bpy.props.StringProperty(subtype='FILE_PATH')

    active_object = bpy.props.IntProperty() 
    active_mesh = bpy.props.IntProperty()  
    active_armature = bpy.props.IntProperty()  
    active_action = bpy.props.IntProperty()  
    active_material = bpy.props.IntProperty()  
    active_scene = bpy.props.IntProperty()  
    
    def execute(self, context):
        filePath = bpy.path.ensure_ext(self.filepath, ".m3d")

        from . import export_m3d
        export_m3d.save(context, filePath)
        return {'FINISHED'}

    def _checkNO(self, val):
        if val == 'NO': return None
        else: return val

    def invoke(self, context, event):
        getMini3dScene().export = False
    
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".m3d")
            
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def draw(self, context):
        layout = self.layout
        layout.label(text="Meshes:")
        layout.template_list('EXPORT_UL_list', '', bpy.data, "meshes", self, "active_mesh")

        layout.label(text="Materials:")
        layout.template_list('EXPORT_UL_list', '', bpy.data, "materials", self, "active_material")

        layout.label(text="Armatures:")
        layout.template_list('EXPORT_UL_list', '', bpy.data, "armatures", self, "active_armature")

        layout.label(text="Actions:")
        layout.template_list('EXPORT_UL_list', '', bpy.data, "actions", self, "active_action")

        layout.label(text="Scenes:")
        layout.template_list('EXPORT_UL_list', '', bpy.data, "scenes", self, "active_scene")

        index = self.active_scene
        size = len(bpy.data.scenes)
        
        if index >= 0 and index < size:
            scene = bpy.data.scenes[index]

            layout.label(text="Objects:")
            layout.template_list('EXPORT_UL_list', '', scene, "objects", self, "active_object")
            