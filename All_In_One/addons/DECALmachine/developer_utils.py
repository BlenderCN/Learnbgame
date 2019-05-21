import os
import pkgutil
import importlib
import rna_keymap_ui


def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    def get_submodule_names(path=path[0], root=""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else:
                module_names.append(root + module_name)
        return module_names

    def import_submodules(names):
        modules = []
        for name in names:
            modules.append(importlib.import_module("." + name, package_name))
        return modules

    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)

    names = get_submodule_names()
    modules = import_submodules(names)
    if reload:
        reload_modules(modules)
    return modules


def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)


def get_keymap_item(km, kmi_name, prop=None, value=None):
    for idx, item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[idx] == kmi_name:
            if prop is None:
                return item
            else:
                if getattr(km.keymap_items[idx].properties, prop) == value:
                    return item
    return None


def show_keymap(condition, kc, keymap, addon, col, prop=None, value=None):
    km = kc.keymaps[keymap]
    if condition:
        kmi = get_keymap_item(km, addon, prop, value)

        kmi.active = True
        col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
    else:
        kmi = get_keymap_item(km, addon, prop, value)
        kmi.active = False
