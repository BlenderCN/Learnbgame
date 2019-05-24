bl_info = {
    "name": "Selection Logic",
    "description": "Advanced selections based on logical conditions.",
    "author": "Omar Ahmad",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "",
    "category": "Learnbgame",
}

import bpy
from . import ui
from . import operators

class SelectByExpressionOperator(bpy.types.Operator):
    bl_idname = "mesh.select_by_expression"
    bl_label = "Select By Expression"

    def execute(self, context):
        operators.selectVertices(context)
        return {'FINISHED'}

def register():
    ui.register()
    operators.register()
    bpy.utils.register_class(SelectByExpressionOperator)

def unregister():
    ui.unregister()
    operators.unregister()
    bpy.utils.unregister_class(SelectByExpressionOperator)
