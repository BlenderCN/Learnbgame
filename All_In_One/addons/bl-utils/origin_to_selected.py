import bpy


bl_info = {
    'name': "Origin To Selected",
    'description': "Move origin of the mesh to selection",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    'category': "Mesh",
}


class OriginToSelected(bpy.types.Operator):
    bl_description = "Move origin of the mesh to selection"
    bl_idname = "mesh.origin_to_selected"
    bl_label = "Origin To Selected"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
