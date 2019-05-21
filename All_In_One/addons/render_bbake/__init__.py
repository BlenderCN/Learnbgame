bl_info = {
    "name": "Cycles Batch Baker",
    "author": "Florian Felix Meyer (tstscr)",
    "version": (1, 1, 0),
    "blender": (2, 77, 0),
    "location": "Properties >> Render >> BBake",
    "description": "Batch Baking for Cycles",
    "warning": "",
    "wiki_url": "https://github.com/florianfelix/render_bbake/wiki",
    "tracker_url": "https://github.com/florianfelix/render_bbake/issues",
    "category": "Render",
}

if "bpy" in locals():
    import importlib
    importlib.reload(batch_bake_ui)
    importlib.reload(batch_bake_object_data)
    importlib.reload(batch_bake_operators)
    importlib.reload(batch_bake_utils)
else:
    from . import batch_bake_ui
    from . import batch_bake_object_data
    from . import batch_bake_operators
    from . import batch_bake_utils

import bpy

###########################################################################
def register():
    #print('MAIN REGISTER:\n', __name__)
    batch_bake_object_data.register()
    batch_bake_ui.register()
    batch_bake_operators.register()
    batch_bake_utils.register()

def unregister():
    #print('MAIN UN-REGISTER:\n', __name__)
    batch_bake_object_data.unregister()
    batch_bake_ui.unregister()
    batch_bake_operators.unregister()
    batch_bake_utils.unregister()

if __name__ == "__main__":
    register()
