
import bpy

from . import operators


def draw_function(self, context):
    self.layout.operator('fence.add', icon='PLUGIN')


def register():
    bpy.utils.register_class(operators.FenceGeneratorAddFenceOperator)
    bpy.types.INFO_MT_mesh_add.append(draw_function)


def unregister():
    bpy.types.INFO_MT_mesh_add.remove(draw_function)
    bpy.utils.unregister_class(operators.FenceGeneratorAddFenceOperator)
