# Nikita Akimov
# interplanety@interplanety.org

import bpy
import json
from . import cfg
from .node_manager import NodeManager
from .WebRequests import WebRequest
from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty, BoolProperty
from bpy.types import Operator, PropertyGroup, Scene
from bpy import app
from .addon import Addon


class BISAddNodeToStorage(Operator):
    bl_idname = 'bis.add_nodegroup_to_storage'
    bl_label = 'BIS_AddToIStorage'
    bl_description = 'Add nodegroup to the BIS'
    bl_options = {'REGISTER', 'UNDO'}

    showMessage = BoolProperty(
        default=False
    )

    def execute(self, context):
        if context.active_node and context.active_node.type == 'GROUP':
            active_node = context.active_node
            node_group_tags = ''
            if context.area.spaces.active.tree_type == 'ShaderNodeTree':
                if context.space_data.shader_type == 'WORLD':
                    active_node = context.scene.world.node_tree.nodes.active
                    node_group_tags = 'world'
                elif context.space_data.shader_type == 'OBJECT':
                    active_node = context.active_object.active_material.node_tree.nodes.active
                    node_group_tags = 'shader'
            elif context.area.spaces.active.tree_type == 'CompositorNodeTree':
                node_group_tags = 'compositing'
            procedural = 0
            if NodeManager.is_procedural(active_node):
                procedural = 1
                node_group_tags += (';' if node_group_tags else '') + 'procedural'
            node_group_tags += (';' if node_group_tags else '') + context.screen.scene.render.engine
            node_group_tags += (';' if node_group_tags else '') + '{0[0]}.{0[1]}'.format(app.version)
            node_group_in_json = NodeManager.node_group_to_json(active_node)
            if node_group_in_json:
                bis_links = list(NodeManager.get_bis_linked_items('bis_linked_item', node_group_in_json))
                if context.scene.bis_add_nodegroup_to_storage_vars.tags != '':
                    node_group_tags += (';' if node_group_tags else '') + context.scene.bis_add_nodegroup_to_storage_vars.tags
                request = WebRequest.send_request({
                    'for': 'add_item',
                    'item_body': json.dumps(node_group_in_json),
                    'storage': context.area.spaces.active.type,
                    'storage_subtype': NodeManager.get_subtype(context),
                    'storage_subtype2': NodeManager.get_subtype2(context),
                    'procedural': procedural,
                    'engine': context.screen.scene.render.engine,
                    'bis_links': json.dumps(bis_links),
                    'item_name': node_group_in_json['name'],
                    'item_tags': node_group_tags.strip(),
                    'addon_version': Addon.current_version()
                })
                if request:
                    context.scene.bis_add_nodegroup_to_storage_vars.tags = ''
                    request_rez = json.loads(request.text)
                    if request_rez['stat'] == 'OK':
                        active_node['bis_uid'] = request_rez['data']['id']
                    else:
                        if cfg.show_debug_err:
                            print(request_rez)
                    if self.showMessage:
                        bpy.ops.message.messagebox('INVOKE_DEFAULT', message=request_rez['stat'])
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='No NodeGroup selected')
        return {'FINISHED'}


class BISAddNodeGroupToStorageVars(PropertyGroup):
    tags = bpy.props.StringProperty(
        name='Tags',
        description='Tags',
        default=''
    )


def register():
    register_class(BISAddNodeToStorage)
    register_class(BISAddNodeGroupToStorageVars)
    Scene.bis_add_nodegroup_to_storage_vars = PointerProperty(type=BISAddNodeGroupToStorageVars)


def unregister():
    del Scene.bis_add_nodegroup_to_storage_vars
    unregister_class(BISAddNodeGroupToStorageVars)
    unregister_class(BISAddNodeToStorage)
