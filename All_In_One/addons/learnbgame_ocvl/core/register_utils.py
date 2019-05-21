import sys
from importlib import reload
from logging import getLogger

import bpy

logger = getLogger(__name__)


def ocvl_register(cls):
    try:
        if "bl_rna" not in cls.__dict__:
            bpy.utils.register_class(cls)
            logger.debug("Cass registrated: {}".format(cls))
    except ValueError as e:
        logger.warning(e)
        logger.warning("Class {} already registered".format(cls))


def ocvl_unregister(cls):
    try:
        if "bl_rna" in cls.__dict__:
            bpy.utils.unregister_class(cls)
    except RuntimeError as e:
        # logger.exception(e)
        logger.warning("Class {} problem with unregister".format(cls))


def reload_ocvl_modules():

    for module_name in sys.modules.keys():
        if "ocvl" in module_name:
            reload(sys.modules[module_name])


def register_node(cls):
    from ocvl.core.node_categories import is_node_class_name
    if is_node_class_name(cls.__name__):
        cls.__annotations__.update({"n_id": bpy.props.StringProperty(default='')})
        cls.__annotations__.update({"n_meta": bpy.props.StringProperty(default='')})
        cls.__annotations__.update({"n_error": bpy.props.StringProperty(default='')})
        cls.__annotations__.update({"n_error_line": bpy.props.IntProperty(default=0)})
        cls.bl_idname = cls.bl_idname if getattr(cls, 'bl_idname', None) else cls.__name__
        cls.bl_label = cls.bl_label if getattr(cls, 'bl_label', None) else cls.bl_idname[4:-4]
        cls.bl_icon = cls.bl_icon if getattr(cls, 'bl_icon', None) else 'OUTLINER_OB_EMPTY'
    ocvl_register(cls)


def unregister_node(cls):
    ocvl_unregister(cls)