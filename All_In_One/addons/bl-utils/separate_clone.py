import bpy


bl_info = {
    'name': "Separate Clone",
    'description': "Separate selection without deleting it.",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    "category": "Learnbgame",
}


class SeparateClone(bpy.types.Operator):
    bl_description = "Separate selection without deleting it."
    bl_idname = "mesh.separate_clone"
    bl_label = "Separate Clone"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.mesh.duplicate()
        bpy.ops.mesh.separate(type='SELECTED')
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
