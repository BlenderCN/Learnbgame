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

# <pep8 compliant>

bl_info = {
    'name': 'Shapekey pinning',
    'author': 'Thomas Larsson',
    'version': '0.1',
    'blender': (2, 5, 6),
    "api": 34786,
    "location": "View3D > UI panel > Shapekey pinning",
    "description": "Shapekey pinning",
    "warning": "",
    "category": "Learnbgame"
}

import bpy, os, mathutils
from mathutils import *
from bpy.props import *


#    class VIEW3D_OT_ResetExpressionsButton(bpy.types.Operator):
#

class VIEW3D_OT_ResetExpressionsButton(bpy.types.Operator):
    bl_idname = "shapepin.reset_expressions"
    bl_label = "Reset expressions"

    def execute(self, context):
        keys = context.object.data.shape_keys
        if keys:
            for block in keys.key_blocks:
                block.value = 0.0
        return{'FINISHED'}    


#
#    class VIEW3D_OT_KeyExpressionButton(bpy.types.Operator):
#

class VIEW3D_OT_KeyExpressionsButton(bpy.types.Operator):
    bl_idname = "shapepin.key_expressions"
    bl_label = "Key"

    def execute(self, context):
        keys = context.object.data.shape_keys
        keyAll = context.scene.keyAll
        if keys:
            keylist = findActiveFcurves(keys.animation_data)
            frame = context.scene.frame_current
            for block in keys.key_blocks:
                if (keyAll or (block.name in keylist)):
                    block.keyframe_insert("value", index=-1, frame=frame)
        return{'FINISHED'}    

def findActiveFcurves(adata):            
    if adata:
        action = adata.action
    else:
        return []
    if action:
        keylist = []
        for fcu in action.fcurves:
            words = fcu.data_path.split('"')
            keylist.append(words[1])
        return keylist
    return []

#
#    class VIEW3D_OT_PinExpressionButton(bpy.types.Operator):
#

class VIEW3D_OT_PinExpressionButton(bpy.types.Operator):
    bl_idname = "shapepin.pin_expression"
    bl_label = "Pin"
    expression = bpy.props.StringProperty()

    def execute(self, context):
        keys = context.object.data.shape_keys
        keyAll = context.scene.keyAll
        if keys:
            frame = context.scene.frame_current
            for block in keys.key_blocks:  
                oldvalue = block.value
                block.value = 1.0 if block.name == self.expression else 0.0
                if (context.tool_settings.use_keyframe_insert_auto and 
                    (keyAll or (block.value > 0.01) or (abs(block.value-oldvalue) > 0.01))):
                    block.keyframe_insert("value", index=-1, frame=frame)
        return{'FINISHED'}    

#
#    class ExpressionsPanel(bpy.types.Panel):
#

class ExpressionsPanel(bpy.types.Panel):
    bl_label = "Pin shapekeys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    @classmethod
    def poll(cls, context):
        return context.object and (context.object.type == 'MESH')

    def draw(self, context):
        layout = self.layout
        layout.label(text="Expressions")
        layout.operator("shapepin.reset_expressions")
        layout.prop(context.scene, "keyAll")
        layout.operator("shapepin.key_expressions")
        layout.separator()
        keys = context.object.data.shape_keys
        if keys:
            for block in keys.key_blocks:
                row = layout.split(0.75)
                row.prop(block, 'value', text=block.name)
                row.operator("shapepin.pin_expression", text="Pin").expression = block.name
        return

###################################################################################    
#
#    initialize and register
#
###################################################################################    

def init():
    bpy.types.Scene.keyAll = BoolProperty(
    name="Key all",
    description="Set keys for all shapes",
    default=False)

def register():
    init()
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass


if __name__ == "__main__":
    register()

    
