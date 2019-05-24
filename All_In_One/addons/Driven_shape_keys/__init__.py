import importlib
import sys


module_names_list = [
    "operators",
    "ui"
]

bl_info = {
    "name": "driven_shapes",
    "description": "",
    "author": "Your Name",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame",
}

# ignore this...
# for module_name in module_names_list:
#     if module_name in locals():
#         importlib.reload(sys.modules["{}.{}".format(__name__, module_name)])
#     else:
#         __import__(name = __name__, fromlist = [module_name])


# some iports to do
if "bpy" in locals():
    for module_name in module_names_list:
        importlib.reload(sys.modules["{}.{}".format(__name__, module_name)])
else:
    __import__(name = __name__, fromlist = module_names_list)

import bpy


# The register
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.show_split_shapes_help = bpy.props.BoolProperty(
            name = "Show help",
            description = "Display help for this addon")


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.show_split_shapes_help


if __name__ == "__main__":
    register()
