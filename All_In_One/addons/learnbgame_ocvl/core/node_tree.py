import logging
from collections import defaultdict

import bpy
from ocvl.core.constants import OCVL_NODE_TREE_TYPE
from ocvl.core.register_utils import ocvl_register, ocvl_unregister

logger = logging.getLogger(__name__)


class LinkPointer:

    def __init__(self, link):
        self.pointer = link.as_pointer()
        self.from_node = link.from_node
        self.from_socket = link.from_socket
        self.to_node = link.to_node
        self.to_socket = link.to_socket


LINKS_POINTER_MAP = defaultdict(dict)


class OCVLNodeTree(bpy.types.NodeTree):
    """
    Node tree consisting of linked nodes used for shading, textures and compositing.
    """

    bl_idname = OCVL_NODE_TREE_TYPE
    bl_label = "OCVL Group Tree type"
    bl_icon = "COLOR"

    @classmethod
    def pull(cls, node_tree):
        logger.info("Node Tree Pull", node_tree.bl_idname is OCVL_NODE_TREE_TYPE)
        return node_tree.bl_idname is OCVL_NODE_TREE_TYPE

    def update(self):
        previous_links = LINKS_POINTER_MAP[self.name]
        current_links = {}
        for link in self.links:
            link_pointer = link.as_pointer()
            current_links[link_pointer] = LinkPointer(link)

        previous_keys = set(previous_links.keys())
        current_keys = set(current_links.keys())
        deleted_link = previous_keys - current_keys
        new_links = current_keys - previous_keys

        for link_pointer in deleted_link:
            if LINKS_POINTER_MAP[self.name][link_pointer].to_node.n_id:
                LINKS_POINTER_MAP[self.name][link_pointer].to_node.process()

        for link_pointer in new_links:
            current_links[link_pointer].from_node.process()
        LINKS_POINTER_MAP[self.name] = current_links


def register():
    ocvl_register(OCVLNodeTree)
    from ocvl.core.node_categories import register as node_categories_register
    node_categories_register()


def unregister():
    ocvl_unregister(OCVLNodeTree)
    from ocvl.core.node_categories import unregister as node_categories_unregister
    node_categories_unregister()
