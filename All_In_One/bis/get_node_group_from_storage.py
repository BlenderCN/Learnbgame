# Nikita Akimov
# interplanety@interplanety.org

import bpy
from bpy.props import IntProperty
from bpy.utils import register_class, unregister_class
from bpy.types import Operator
import json
from .WebRequests import WebRequest
from .node_manager import NodeManager


class GetNodeGroupFromStorage(Operator):
    bl_idname = 'bis.get_nodegroup_from_storage'
    bl_label = 'BIS_GetFromStorage'
    bl_description = 'Get nodegroup from common part of BIS'
    bl_options = {'REGISTER', 'UNDO'}

    node_group_id = IntProperty(
        name='node_group_id',
        default=0
    )

    def execute(self, context):
        if self.node_group_id:
            subtype = NodeManager.get_subtype(context)
            subtype2 = NodeManager.get_subtype2(context)
            request = WebRequest.send_request({
                'for': 'get_item',
                'storage': NodeManager.storage_type(context=context),
                'storage_subtype': subtype,
                'storage_subtype2': subtype2,
                'id': self.node_group_id
            })
            if request:
                request_rez = json.loads(request.text)
                if request_rez['stat'] != 'OK':
                    bpy.ops.message.messagebox('INVOKE_DEFAULT', message=request_rez['data']['text'])
                else:
                    node_in_json = json.loads(request_rez['data']['item'])
                    dest_node_tree = None
                    if subtype == 'CompositorNodeTree':
                        dest_node_tree = context.area.spaces.active.node_tree
                        if not context.screen.scene.use_nodes:
                            context.screen.scene.use_nodes = True
                    elif subtype == 'ShaderNodeTree':
                        if context.active_object:
                            if not context.active_object.active_material:
                                context.active_object.active_material = bpy.data.materials.new(name='Material')
                                context.active_object.active_material.use_nodes = True
                                for currentNode in context.active_object.active_material.node_tree.nodes:
                                    if currentNode.bl_idname != 'ShaderNodeOutputMaterial':
                                        context.active_object.active_material.node_tree.nodes.remove(currentNode)
                            if subtype2 == 'OBJECT':
                                dest_node_tree = context.active_object.active_material.node_tree
                            elif subtype2 == 'WORLD':
                                dest_node_tree = context.scene.world.node_tree
                    if node_in_json and dest_node_tree:
                        nodegroup = NodeManager.json_to_node_group(dest_node_tree, node_in_json)
                        if nodegroup:
                            nodegroup['bis_uid'] = self.node_group_id
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='No NodeGroup To Get')
        return {'FINISHED'}


def register():
    register_class(GetNodeGroupFromStorage)


def unregister():
    unregister_class(GetNodeGroupFromStorage)
