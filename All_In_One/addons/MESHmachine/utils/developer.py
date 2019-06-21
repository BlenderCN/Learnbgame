import os
import pkgutil
import importlib
import rna_keymap_ui
import time


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


def get_keymap_item(km, kmi, kmi_prop=None):
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi:
            if kmi_prop:
                # if km.keymap_items[i].properties.name == kmi_value:
                prop = kmi_prop[0]
                value = kmi_prop[1]
                if getattr(km.keymap_items[i].properties, prop) == value:
                    return km_item
            else:
                return km_item
    return None


def draw_keymap_item(km, kmi, kc, layout):
    if kmi:
        layout.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, layout, 0)


def output_traceback(self):
    import traceback
    print()
    traceback.print_exc()

    tb = traceback.format_exc() + "\nPLEASE REPORT THIS ERROR to mesh@machin3.io"
    self.report({'ERROR'}, tb)


chronicle = []


class Benchmark():
    def __init__(self, do_benchmark):
        if do_benchmark:
            os.system("clear")
        self.do_benchmark = do_benchmark
        self.start_time = self.time = time.time()
        self.chronicle = []

    def measure(self, name=""):
        if self.do_benchmark:
            t = time.time() - self.time
            self.time += t
            self.chronicle.append(t)

            global chronicle
            if chronicle:
                diff = self.chronicle[-1] - chronicle[len(self.chronicle) - 1]
                diff = "+ %.6f" % diff if diff > 0 else ("%.6f" % diff).replace("-", "- ")

                print("--- %f (%s) - %s" % (t, diff, name))
            else:
                print("--- %f - %s" % (t, name))

    def total(self):
        if self.do_benchmark:
            t = time.time() - self.start_time
            self.chronicle.append(t)

            global chronicle
            if chronicle:
                diff = self.chronicle[-1] - chronicle[len(self.chronicle) - 1]
                diff = "+ %.6f" % diff if diff > 0 else ("%.6f" % diff).replace("-", "- ")

                print("  » %f (%s) - %s" % (t, diff, "total"))
            else:
                print("  » %f - %s" % (t, "total"))

            chronicle = self.chronicle
