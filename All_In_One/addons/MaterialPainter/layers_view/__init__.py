import bpy
from layers_view import layers_panel, layers_panel_op_actions

def reload():
    from importlib import reload
    modules = [layers_panel_op_actions, layers_panel]
    for module in modules:
        reload(module)


def register():
    print("Registering", __name__)
    bpy.utils.register_module(__name__)
    layers_panel.register()


def unregister():
    print("Unregistering ", __name__)
    bpy.utils.unregister_module(__name__)
    layers_panel.unregister()
