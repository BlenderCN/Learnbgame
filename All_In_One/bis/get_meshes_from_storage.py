# Nikita Akimov
# interplanety@interplanety.org

from bpy.types import Operator, PropertyGroup, WindowManager
from bpy.utils import register_class, unregister_class
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, PointerProperty
from .mesh_manager import MeshManager
from .bis_items import BISItems


class BISGetMeshesInfoFromStorage(Operator):
    bl_idname = 'bis.get_meshes_info_from_storage'
    bl_label = 'BIS: get items'
    bl_description = 'Search meshes in BIS'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MeshManager.items_from_bis(
            context,
            search_filter=context.window_manager.bis_get_meshes_info_from_storage_vars.searchFilter,
            page=0,
            update_preview=context.window_manager.bis_get_meshes_info_from_storage_vars.updatePreviews
        )
        return {'FINISHED'}


class BISGetMeshesInfoFromStoragePrevPage(Operator):
    bl_idname = 'bis.get_meshes_info_from_storage_prev_page'
    bl_label = 'BIS: get items (prev page)'
    bl_description = 'Get prev page'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MeshManager.items_from_bis(
            context,
            search_filter=context.window_manager.bis_get_meshes_info_from_storage_vars.searchFilter,
            page=context.window_manager.bis_get_meshes_info_from_storage_vars.current_page - 1,
            update_preview=context.window_manager.bis_get_meshes_info_from_storage_vars.updatePreviews
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.bis_get_meshes_info_from_storage_vars.current_page > 0


class BISGetMeshesInfoFromStorageNextPage(Operator):
    bl_idname = 'bis.get_meshes_info_from_storage_next_page'
    bl_label = 'BIS: get items (next page)'
    bl_description = 'Get next page'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MeshManager.items_from_bis(
            context,
            search_filter=context.window_manager.bis_get_meshes_info_from_storage_vars.searchFilter,
            page=context.window_manager.bis_get_meshes_info_from_storage_vars.current_page + 1,
            update_preview=context.window_manager.bis_get_meshes_info_from_storage_vars.updatePreviews
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.bis_get_meshes_info_from_storage_vars.current_page_status not in ('', 'EOF')


class BISGetMeshesInfoFromStorageVars(PropertyGroup):
    searchFilter = StringProperty(
        name='Search',
        description='Filter to search',
        default=''
    )
    updatePreviews = BoolProperty(
        name='Update Previews',
        description='Update previews from server',
        default=False
    )
    items = EnumProperty(
        items=lambda self, context: BISItems.get_previews(self, MeshManager.storage_type(context)),
        update=lambda self, context: BISItems.on_preview_select(self, MeshManager.storage_type(context))
    )
    current_page = IntProperty(
        default=0
    )
    current_page_status = StringProperty(
        default=''
    )


def register():
    register_class(BISGetMeshesInfoFromStorageVars)
    WindowManager.bis_get_meshes_info_from_storage_vars = PointerProperty(type=BISGetMeshesInfoFromStorageVars)
    register_class(BISGetMeshesInfoFromStorage)
    register_class(BISGetMeshesInfoFromStoragePrevPage)
    register_class(BISGetMeshesInfoFromStorageNextPage)


def unregister():
    unregister_class(BISGetMeshesInfoFromStorageNextPage)
    unregister_class(BISGetMeshesInfoFromStoragePrevPage)
    unregister_class(BISGetMeshesInfoFromStorage)
    del WindowManager.bis_get_meshes_info_from_storage_vars
    unregister_class(BISGetMeshesInfoFromStorageVars)
