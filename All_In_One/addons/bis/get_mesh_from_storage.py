# Nikita Akimov
# interplanety@interplanety.org

import bpy
from bpy.props import IntProperty, BoolProperty
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
from .mesh_manager import MeshManager


class GetMeshFromStorage(Operator):
    bl_idname = 'bis.get_mesh_from_storage'
    bl_label = 'BIS_GetFromStorage'
    bl_description = 'Get Mesh from the BIS'
    bl_options = {'REGISTER', 'UNDO'}

    mesh_id = IntProperty(
        name='mesh_id',
        default=0
    )

    show_message = BoolProperty(
        default=False
    )

    def execute(self, context):
        if self.mesh_id:
            request_rez = MeshManager.from_bis(context, self.mesh_id)
            if request_rez['stat'] == 'OK':
                if self.show_message:
                    bpy.ops.message.messagebox('INVOKE_DEFAULT', message=request_rez['stat'] + ': ' + request_rez['data']['text'])
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='No Mesh To Get')
        return {'FINISHED'}


def register():
    register_class(GetMeshFromStorage)


def unregister():
    unregister_class(GetMeshFromStorage)
