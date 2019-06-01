import os
import bpy
import sys
import inspect
import pkgutil
import importlib
import bpy_types

def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py

    Individual modules can define a __reload_order_index__ property which
    will be used to reload the modules in a specific order. The default is 0.
    """
    def iter_submodule_names(path = path[0], root = ""):
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                yield from get_submodule_names(sub_path, sub_root)
            else:
                yield root + module_name

    def import_submodules(names):
        for name in names:
            yield importlib.import_module("." + name, package_name)

    def reload_modules(modules):
        modules.sort(key = lambda module: getattr(module, "__reload_order_index__", 0))
        for module in modules:
            importlib.reload(module)

    def iter_classes_to_register():
        module_name = os.path.basename(path[0])
        typemap_list = bpy_types.TypeMap.get(module_name, ())
        for cls_weakref in typemap_list:
            yield cls_weakref()

    names = list(iter_submodule_names())
    modules = list(import_submodules(names))
    if reload:
        reload_modules(modules)

    classes = list(iter_classes_to_register())

    return modules, classes
