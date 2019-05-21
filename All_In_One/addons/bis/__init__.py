# Nikita Akimov
# interplanety@interplanety.org

from . import cfg
from . import add_node_group_to_storage
from . import update_node_group
from . import get_node_group_from_storage
from . import get_nodes_from_storage
from . import nodes_panel
from . import BIS_addTextToStorage
from . import BISUpdateText
from . import BIS_getTextFromStorage
from . import BIS_getTextsFromStorage
from . import texts_panel
from . import mesh_panel
from . import get_meshes_from_storage
from . import add_mesh_to_storage
from . import update_mesh_in_storage
from . import get_mesh_from_storage
from . import WebRequests
from . import MessageBox
from . import bis_items
from . import nodes_tools_ops
if cfg.experimental_enable_bis_custom_nodes:
    from . import nodes_bis_custom


bl_info = {
    'name': 'BIS',
    'category': 'Material',
    'author': 'Nikita Akimov',
    'version': (1, 5, 3),
    'blender': (2, 79, 0),
    'location': 'T-Panel > BIS',
    'wiki_url': 'https://b3d.interplanety.org/en/bis-online-blender-material-storage/',
    'tracker_url': 'https://b3d.interplanety.org/en/bis-online-blender-material-storage/',
    'description': 'BIS - Blender Interplanety Storage'
}


def register():
    add_node_group_to_storage.register()
    update_node_group.register()
    get_node_group_from_storage.register()
    get_nodes_from_storage.register()
    nodes_panel.register()
    if cfg.experimental_enable_bis_custom_nodes:
        nodes_bis_custom.register()
    BIS_addTextToStorage.register()
    BISUpdateText.register()
    BIS_getTextFromStorage.register()
    BIS_getTextsFromStorage.register()
    texts_panel.register()
    mesh_panel.register()
    get_meshes_from_storage.register()
    add_mesh_to_storage.register()
    update_mesh_in_storage.register()
    get_mesh_from_storage.register()
    WebRequests.register()
    MessageBox.register()
    bis_items.register()
    nodes_tools_ops.register()


def unregister():
    nodes_tools_ops.unregister()
    bis_items.unregister()
    MessageBox.unregister()
    WebRequests.unregister()
    get_mesh_from_storage.unregister()
    update_mesh_in_storage.unregister()
    add_mesh_to_storage.unregister()
    get_meshes_from_storage.unregister()
    mesh_panel.unregister()
    texts_panel.unregister()
    BIS_getTextsFromStorage.unregister()
    BIS_getTextFromStorage.unregister()
    BISUpdateText.unregister()
    BIS_addTextToStorage.unregister()
    if cfg.experimental_enable_bis_custom_nodes:
        nodes_bis_custom.unregister()
    nodes_panel.unregister()
    get_nodes_from_storage.unregister()
    get_node_group_from_storage.unregister()
    update_node_group.unregister()
    add_node_group_to_storage.unregister()


if __name__ == "__main__":
    register()
