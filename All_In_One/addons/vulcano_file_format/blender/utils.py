def is_greater_than_or_equal(tuple1 :tuple, tuple2: tuple):
    for i in range(len(tuple2) - 1):
        if (tuple1[i] < tuple2[i]):
            return False
    return True

def get_utils():
    # load the function  "apply_modifiers" dynamically to support
    # different versions of Blender with incompatible Python APIs:
    # 1. Get the python package name from the module name
    package_name = __name__.rsplit('.', 1) [0]
    # 2. Get the python module name accodring to the version of Blender
    import bpy
    if is_greater_than_or_equal(bpy.app.version, (2, 80, 0)):
        module_name = package_name + ".utils_blender_2_8_0"
    else:
        module_name = package_name + ".utils_blender_2_7_0"
    # 3. Import the corresponding Python module and reload if necessary
    import importlib
    import sys
    if module_name in sys.modules:
        module = sys.modules[module_name]
        importlib.reload(module)
    else:
        module = importlib.import_module(module_name)

    return module