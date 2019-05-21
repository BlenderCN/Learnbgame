# Nikita Akimov
# interplanety@interplanety.org

import sys
import bpy
import os
import json
from . import cfg
from .NodeNodeGroup import *
from .node_node_group import *
from .addon import Addon
from .WebRequests import WebRequest
from .bis_items import BISItems


class NodeManager:

    @staticmethod
    def items_from_bis(context, search_filter, page, update_preview=False):
        # get page of items list from BIS
        rez = None
        storage_subtype = __class__.get_subtype(context)
        storage_subtype2 = __class__.get_subtype2(context)
        request = WebRequest.send_request({
            'for': 'get_items',
            'search_filter': search_filter,
            'page': page,
            'storage': __class__.storage_type(context),
            'storage_subtype': storage_subtype,
            'storage_subtype2': storage_subtype2,
            'update_preview': update_preview
        })
        if request:
            request_rez = json.loads(request.text)
            rez = request_rez['stat']
            if request_rez['stat'] == 'OK':
                preview_to_update = BISItems.update_previews_from_data(data=request_rez['data']['items'], list_name=__class__.storage_type(context))
                if preview_to_update:
                    request = WebRequest.send_request({
                        'for': 'update_previews',
                        'preview_list': preview_to_update,
                        'storage': __class__.storage_type(context),
                        'storage_subtype': storage_subtype,
                        'storage_subtype2': storage_subtype2
                    })
                    if request:
                        previews_update_rez = json.loads(request.text)
                        if previews_update_rez['stat'] == 'OK':
                            BISItems.update_previews_from_data(data=previews_update_rez['data']['items'], list_name=__class__.storage_type(context))
                BISItems.create_items_list(data=request_rez['data']['items'], list_name=__class__.storage_type(context))
                context.window_manager.bis_get_nodes_info_from_storage_vars.current_page = page
                context.window_manager.bis_get_nodes_info_from_storage_vars.current_page_status = request_rez['data']['status']
        return rez

    @staticmethod
    def node_group_to_json(nodegroup):
        # convert node group to json
        group_in_json = None
        if nodegroup.type == 'GROUP':
            nodegroup_class = 'Node' + nodegroup.bl_idname
            if hasattr(sys.modules[__name__], nodegroup_class):
                group_in_json = getattr(sys.modules[__name__], nodegroup_class).node_to_json(nodegroup)
                if cfg.to_server_to_file:
                    with open(os.path.join(os.path.dirname(bpy.data.filepath), 'send_to_server.json'), 'w') as currentFile:
                        json.dump(group_in_json, currentFile, indent=4)
                if cfg.no_sending_to_server:
                    return None
        return group_in_json

    @staticmethod
    def json_to_node_group(dest_nodetree, node_in_json):
        # recreate node group from json
        if cfg.from_server_to_file:
            with open(os.path.join(os.path.dirname(bpy.data.filepath), 'received_from_server.json'), 'w') as currentFile:
                json.dump(node_in_json, currentFile, indent=4)
        current_node = None
        if dest_nodetree:
            # for older compatibility (v 1.4.1)
            # if all node groups becomes 1.4.2. and later - remove all "else" condition
            node_group_version = node_in_json['BIS_addon_version'] if 'BIS_addon_version' in node_in_json else Addon.node_group_first_version
            if Addon.node_group_version_higher(node_group_version, Addon.current_version()):
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message='This node group was saved in higher BIS version and may not load correctly.\
                 Please download the last BIS add-on version!')
            if Addon.node_group_version_higher(node_group_version, Addon.node_group_first_version):
                # 1.4.2
                node_class = getattr(sys.modules[__name__], 'Node' + node_in_json['bl_idname'])
            else:
                # 1.4.1
                node_class = getattr(sys.modules[__name__], 'NodeBase' + node_in_json['bl_type'])
            current_node = node_class.json_to_node(node_tree=dest_nodetree, node_json=node_in_json)
            current_node.location = (0, 0)
        return current_node

    @staticmethod
    def get_subtype(context):
        # return subtype
        if context.area.spaces.active.type == 'NODE_EDITOR':
            return context.area.spaces.active.tree_type
        else:
            return 'ShaderNodeTree'

    @staticmethod
    def get_subtype2(context):
        # return subtype2
        if context.area.spaces.active.type == 'NODE_EDITOR':
            return context.area.spaces.active.shader_type
        else:
            return 'OBJECT'

    @staticmethod
    def is_procedural(material):
        # check if material (nodegroup) is fully procedural
        rez = True
        for node in material.node_tree.nodes:
            if node.type == 'GROUP':
                rez = __class__.is_procedural(node)
                if not rez:
                    break
            elif node.type == 'TEX_IMAGE':
                rez = False
                break
            elif node.type == 'SCRIPT' and node.mode == 'EXTERNAL':
                rez = False
                break
        return rez

    @staticmethod
    def cpu_render_required(material):
        # check if material (nodegroup) required only CPU render
        rez = False
        for node in material.node_tree.nodes:
            if node.type == 'GROUP':
                rez = __class__.cpu_render_required(node)
                if rez:
                    break
            elif node.type == 'SCRIPT':
                rez = True
                break
        return rez

    @staticmethod
    # returns generator to crate list with all linked items (texts, ...) to current item (nodegroup)
    def get_bis_linked_items(key, nodegroup_in_json):
        for k, v in nodegroup_in_json.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in __class__.get_bis_linked_items(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result in __class__.get_bis_linked_items(key, d):
                            yield result

    @staticmethod
    def storage_type(context):
        # return context.area.spaces.active.type
        return 'NODE_EDITOR'
