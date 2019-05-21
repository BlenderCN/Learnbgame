bl_info = {
    "name":        "Compute Nodes",
    "description": "Visual functional programming in Blender.",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 1),
    "blender":     (2, 79, 0),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     "Proof of concept!"
}

import sys
from pathlib import Path

# setup llvmlite
try: import llvmlite
except:
    sys.path.append(str(Path(__file__).parents[0] / "libs"))
    try: import llvmlite
    except:
        raise Exception("cannot load llvmlite")
import llvmlite.binding as llvm
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()


import importlib
from . import load_utils
importlib.reload(load_utils)
modules, classes = load_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

import bpy

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for module in modules:
        if hasattr(module, "register"):
            module.register()

    print("Registered {} with {} modules and {} classes."
          .format(bl_info["name"], len(modules), len(classes)))

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()

    print("Unregistered {}.".format(bl_info["name"]))
