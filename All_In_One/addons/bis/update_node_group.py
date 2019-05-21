# Nikita Akimov
# interplanety@interplanety.org

import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
import json
from .node_manager import NodeManager
from .WebRequests import WebRequest
from .addon import Addon


class BISUpdateNodegroup(Operator):
    bl_idname = 'bis.update_nodegroup_in_storage'
    bl_label = 'Update nodegroup'
    bl_description = 'Update nodegroup in the BIS'
    bl_options = {'REGISTER', 'UNDO'}

    showMessage = BoolProperty(
        default=False
    )

    def execute(self, context):
        if context.active_node and context.active_node.type == 'GROUP':
            active_node = context.active_node
            if context.area.spaces.active.tree_type == 'ShaderNodeTree':
                if context.space_data.shader_type == 'WORLD':
                    active_node = context.scene.world.node_tree.nodes.active
                elif context.space_data.shader_type == 'OBJECT':
                    active_node = context.active_object.active_material.node_tree.nodes.active
            if 'bis_uid' in active_node:
                node_group_in_json = NodeManager.node_group_to_json(active_node)
                if node_group_in_json:
                    bis_links = list(NodeManager.get_bis_linked_items('bis_linked_item', node_group_in_json))
                    request = WebRequest.send_request({
                        'for': 'update_item',
                        'item_body': json.dumps(node_group_in_json),
                        'storage': context.area.spaces.active.type,
                        'storage_subtype': NodeManager.get_subtype(context),
                        'storage_subtype2': NodeManager.get_subtype2(context),
                        'bis_links': json.dumps(bis_links),
                        'item_id': active_node['bis_uid'],
                        'item_name': node_group_in_json['name'],
                        'addon_version': Addon.current_version()
                    })
                    if request:
                        request_rez = json.loads(request.text)
                        if self.showMessage:
                            bpy.ops.message.messagebox('INVOKE_DEFAULT', message=request_rez['stat'] + ': ' + request_rez['data']['text'])
            else:
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message='ERR: First save this Nodegroup to the BIS!')
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='No NodeGroup selected')
        return {'FINISHED'}

    def draw(self, context):
        self.layout.separator()
        self.layout.label('Update selected nodegroup in the BIS?')
        self.layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


def register():
    register_class(BISUpdateNodegroup)


def unregister():
    unregister_class(BISUpdateNodegroup)
