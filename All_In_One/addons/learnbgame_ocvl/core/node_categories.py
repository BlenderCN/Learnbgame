import logging
import os
from collections import defaultdict
from importlib import util

import ocvl
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from ocvl.core import constants
from ocvl.core.register_utils import register_node, unregister_node

logger = logging.getLogger(__name__)


class OCVLNodeCategory(NodeCategory):

    @classmethod
    def pull(cls, context):
        logger.info("Categories Node pull")
        return context.space_data.tree_type == constants.OCVL_NODE_TREE_TYPE


def is_node_class_name(class_name):
    return class_name.startswith(constants.PREFIX_NODE_CLASS) and \
           class_name.endswith(constants.SUFFIX_NODE_CLASS) and \
           class_name not in constants.BLACKLIST_FOR_REGISTER_NODE


def auto_register_node_categories(register_mode=True):
    _ocvl_auto_register = register_node if register_mode else unregister_node

    node_classes_list = []
    node_categories_dict = defaultdict(list)
    build_categories = []
    nodes_module_path = os.path.join(ocvl.__path__[0], constants.NAME_NODE_DIRECTORY)

    def process_module(file_name, node_file_path, node_classes_list, _ocvl_auto_register, dir_category=False):
        spec = util.spec_from_file_location("ocvl.{}.{}".format(constants.NAME_NODE_DIRECTORY, file_name), node_file_path)
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for obj_name in dir(mod):
            if is_node_class_name(obj_name):
                node_class = getattr(mod, obj_name)
                if dir_category:
                    node_class.n_category = node_file_path.split(os.sep)[-2]
                if node_class.n_category and node_class.n_auto_register:
                    node_classes_list.append(node_class)
                    _ocvl_auto_register(node_class)

    for file_name in os.listdir(nodes_module_path):

        if not file_name.startswith("__"):
            node_file_path = node_file_path_in = os.path.join(nodes_module_path, file_name)
            if os.path.isfile(node_file_path):
                process_module(file_name, node_file_path, node_classes_list, _ocvl_auto_register)
            elif os.path.isdir(node_file_path):
                for file_name_in in os.listdir(node_file_path_in):
                    if not file_name_in.startswith("__"):
                        node_file_path_in = os.path.join(node_file_path, file_name_in)
                        if os.path.isfile(node_file_path_in):
                            process_module(file_name_in, node_file_path_in, node_classes_list, _ocvl_auto_register, dir_category=True)

    for node_class in node_classes_list:
        node_categories_dict[node_class.n_category].append(NodeItem(node_class.__name__, node_class.__name__[4:-4]))

    for category_name in node_categories_dict.keys():
        build_categories.append(OCVLNodeCategory(
            identifier=constants.ID_TREE_CATEGORY_TEMPLATE.format(category_name),
            name=category_name,
            description=category_name,
            items=node_categories_dict[category_name]
        ))

    if register_mode:
        try:
            register_node_categories(constants.OCVL_NODE_CATEGORIES, build_categories)
        except KeyError as e:
            logger.info("{} already registered.".format(constants.OCVL_NODE_CATEGORIES))
    else:
        unregister_node_categories(constants.OCVL_NODE_CATEGORIES)


def register():
    auto_register_node_categories(register_mode=True)


def unregister():
    auto_register_node_categories(register_mode=False)
