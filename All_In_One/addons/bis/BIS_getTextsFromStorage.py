# Nikita Akimov
# interplanety@interplanety.org

import bpy
from .bis_items import BISItems
from .TextManager import TextManager


class BISGetTextsInfoFromStorage(bpy.types.Operator):
    bl_idname = 'bis.get_texts_info_from_storage'
    bl_label = 'BIS: get items'
    bl_description = 'Search texts in BIS'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        TextManager.items_from_bis(
            context,
            search_filter=context.window_manager.bis_get_texts_info_from_storage_vars.searchFilter,
            page=0
        )
        return {'FINISHED'}


class BISGetTextsInfoFromStoragePrevPage(bpy.types.Operator):
    bl_idname = 'bis.get_texts_info_from_storage_prev_page'
    bl_label = 'BIS: get items'
    bl_description = 'Get prev page'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        TextManager.items_from_bis(
            context,
            search_filter=context.window_manager.bis_get_texts_info_from_storage_vars.searchFilter,
            page=context.window_manager.bis_get_texts_info_from_storage_vars.current_page - 1
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.bis_get_texts_info_from_storage_vars.current_page > 0


class BISGetTextsInfoFromStorageNextPage(bpy.types.Operator):
    bl_idname = 'bis.get_texts_info_from_storage_next_page'
    bl_label = 'BIS: get items'
    bl_description = 'Get next page'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        TextManager.items_from_bis(
            context,
            search_filter=context.window_manager.bis_get_texts_info_from_storage_vars.searchFilter,
            page=context.window_manager.bis_get_texts_info_from_storage_vars.current_page + 1
        )
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.bis_get_texts_info_from_storage_vars.current_page_status not in ('', 'EOF')


class BISGetTextsInfoFromStorageVars(bpy.types.PropertyGroup):
    searchFilter = bpy.props.StringProperty(
        name='Search',
        description='Filter to search',
        default=''
    )
    items = bpy.props.EnumProperty(
        items=lambda self, context: BISItems.get_previews(self, TextManager.storage_type()),
        update=lambda self, context: BISItems.on_preview_select(self, TextManager.storage_type())
    )
    current_page = bpy.props.IntProperty(
        default=0
    )
    current_page_status = bpy.props.StringProperty(
        default=''
    )


def register():
    bpy.utils.register_class(BISGetTextsInfoFromStorage)
    bpy.utils.register_class(BISGetTextsInfoFromStoragePrevPage)
    bpy.utils.register_class(BISGetTextsInfoFromStorageNextPage)
    bpy.utils.register_class(BISGetTextsInfoFromStorageVars)
    bpy.types.WindowManager.bis_get_texts_info_from_storage_vars = bpy.props.PointerProperty(type=BISGetTextsInfoFromStorageVars)


def unregister():
    del bpy.types.WindowManager.bis_get_texts_info_from_storage_vars
    bpy.utils.unregister_class(BISGetTextsInfoFromStorageVars)
    bpy.utils.unregister_class(BISGetTextsInfoFromStorageNextPage)
    bpy.utils.unregister_class(BISGetTextsInfoFromStoragePrevPage)
    bpy.utils.unregister_class(BISGetTextsInfoFromStorage)
