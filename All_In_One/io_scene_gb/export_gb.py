import bpy
import utility

if 'structs.gb' in locals():
    import importlib

    importlib.reload(structs.gb)
else:
    import structs.gb


def scene_export(context, filepath):
    raise NotImplementedError
