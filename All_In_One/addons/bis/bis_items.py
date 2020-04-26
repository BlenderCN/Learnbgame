# Nikita Akimov
# interplanety@interplanety.org

import bpy
import os
import base64
import bpy.utils.previews


class BISItems:

    items_lists = {}

    @staticmethod
    def register():
        __class__.items_lists['NODE_EDITOR'] = bpy.utils.previews.new()
        __class__.items_lists['NODE_EDITOR'].items = []
        __class__.items_lists['TEXT_EDITOR'] = bpy.utils.previews.new()
        __class__.items_lists['TEXT_EDITOR'].items = []
        __class__.items_lists['VIEW_3D'] = bpy.utils.previews.new()
        __class__.items_lists['VIEW_3D'].items = []

    @staticmethod
    def unregister():
        for item_list in __class__.items_lists.values():
            item_list.items.clear()
            bpy.utils.previews.remove(item_list)
        __class__.items_lists.clear()

    @staticmethod
    def create_items_list(data, list_name, previews=True):
        __class__.clear_items_list(list_name)
        for item_info in data:
            if previews:
                path = __class__.get_preview_path(item_id=int(item_info['id']), list_name=list_name)
                thumb = __class__.items_lists[list_name].load(path, path, 'IMAGE')
                __class__.items_lists[list_name].items.append((item_info['id'], item_info['name'], '', thumb.icon_id, int(item_info['id'])))
            else:
                __class__.items_lists[list_name].items.append((item_info['id'], item_info['name'], '', '', int(item_info['id'])))

    @staticmethod
    def get_previews(self, storage_type):
        if storage_type:
            return __class__.items_lists[storage_type].items
        else:
            return []

    @staticmethod
    def clear_items_list(name):
        __class__.items_lists[name].clear()
        __class__.items_lists[name].items.clear()

    @staticmethod
    def get_preview_relative_dir(item_id, list_name):
        item_dir = 0
        while item_id > item_dir:
            item_dir += 1000
        return 'previews' + os.path.sep + list_name + os.path.sep + str(item_dir - (0 if item_dir == 0 else 1000)) + '-' + str(item_dir)

    @staticmethod
    def get_preview_dir(item_id, list_name):
        return os.path.dirname(__file__) + os.path.sep + __class__.get_preview_relative_dir(item_id=item_id, list_name=list_name)

    @staticmethod
    def get_preview_path(item_id, list_name):
        return __class__.get_preview_dir(item_id=item_id, list_name=list_name) + os.path.sep + str(item_id) + '.jpg'

    @staticmethod
    def update_previews_from_data(data, list_name):
        preview_to_update = ''
        for prewiew_info in data:
            preview_dir = __class__.get_preview_dir(item_id=int(prewiew_info['id']), list_name=list_name)
            if prewiew_info['preview']:
                preview_content = base64.b64decode(prewiew_info['preview'])
                if not os.path.exists(preview_dir):
                    os.makedirs(preview_dir)
                with open(__class__.get_preview_path(item_id=int(prewiew_info['id']), list_name=list_name), 'wb') as current_preview:
                    current_preview.write(preview_content)
            else:
                if not os.path.exists(__class__.get_preview_path(item_id=int(prewiew_info['id']), list_name=list_name)):
                    preview_to_update += ('' if preview_to_update == '' else ',') + prewiew_info['id']
        return preview_to_update

    @staticmethod
    def on_preview_select(self, storage_type):
        if storage_type == 'NODE_EDITOR':
            bpy.ops.bis.get_nodegroup_from_storage(node_group_id=int(self.items))
        elif storage_type == 'TEXT_EDITOR':
            bpy.ops.bis.get_text_from_storage(text_id=int(self.items))
        elif storage_type == 'VIEW_3D':
            bpy.ops.bis.get_mesh_from_storage(mesh_id=int(self.items))

    @staticmethod
    def get_item_name_by_id(item_id, storage):
        item_in_list = [item[1] for item in __class__.items_lists[storage].items if item[4] == item_id]
        if item_in_list:
            return item_in_list[0]
        else:
            return ''


def register():
    BISItems.register()


def unregister():
    BISItems.unregister()
