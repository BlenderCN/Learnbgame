# Nikita Akimov
# interplanety@interplanety.org

import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from .mesh_manager import MeshManager
from . import cfg


class BISUpdateMeshInStorage(Operator):
    bl_idname = 'bis.update_mesh_in_storage'
    bl_label = 'Update mesh'
    bl_description = 'Update mesh in the BIS'
    bl_options = {'REGISTER', 'UNDO'}

    show_message = BoolProperty(
        default=False
    )

    def execute(self, context):

        bis_uid_mesh = self.get_bis_uid(context)
        if bis_uid_mesh:
            request_rez = MeshManager.update_in_bis(
                bis_uid=bis_uid_mesh['bis_uid'],
                mesh_list=context.selected_objects[:],
                name=(context.window_manager.bis_add_mesh_to_storage_vars.name if context.window_manager.bis_add_mesh_to_storage_vars.name else bis_uid_mesh['bis_uid_name'])
            )
            if request_rez['stat'] == 'OK':
                context.window_manager.bis_add_mesh_to_storage_vars.name = ''
                context.window_manager.bis_add_mesh_to_storage_vars.tags = ''
                if self.show_message:
                    bpy.ops.message.messagebox('INVOKE_DEFAULT', message=request_rez['stat'] + ': ' + request_rez['data']['text'])
            else:
                if cfg.show_debug_err:
                    print(request_rez)
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='No Mesh to update')
        return {'FINISHED'}

    def draw(self, context):
        self.layout.separator()
        self.layout.label('Update selected Meshes?')
        self.layout.label('This will update the item: " ' + self.get_bis_uid(context)['bis_uid_name'] + ' "')
        self.layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    @classmethod
    def poll(cls, context):
        return cls.get_bis_uid(context) is not None

    @classmethod
    def get_bis_uid(cls, context):
        bis_uid_mesh = None
        if context.selected_objects:
            # first bis_uid from selection
            for mesh in context.selected_objects:
                if 'bis_uid' in mesh:
                    bis_uid_mesh = mesh
            if bis_uid_mesh:
                # same bis_uid in all selected objects
                for mesh in context.selected_objects:
                    if 'bis_uid' in mesh and mesh['bis_uid'] != bis_uid_mesh['bis_uid']:
                        bis_uid_mesh = None
                        break
                # if not same - get bis_uid from active object
                if not bis_uid_mesh:
                    if context.active_object and context.active_object in context.selected_objects:
                        if 'bis_uid' in context.active_object:
                            bis_uid_mesh = context.active_object
        return bis_uid_mesh


def register():
    register_class(BISUpdateMeshInStorage)


def unregister():
    unregister_class(BISUpdateMeshInStorage)
