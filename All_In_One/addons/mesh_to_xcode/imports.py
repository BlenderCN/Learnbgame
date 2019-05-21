from bpy.types import Operator


class ImportMeshButton(Operator):
    """Import obj or ply meshes to the scene
    """
    bl_idname = 'mesh_to_xcode.import'
    bl_label = 'Import'
    bl_icon = 'IMPORT'

    # TODO import obj and ply
    def execute(self, context):
        print('hello import')
        return { 'FINISHED' }
