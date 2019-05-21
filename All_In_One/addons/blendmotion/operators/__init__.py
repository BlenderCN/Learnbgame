import bpy

from . import add_bones, export_animation, import_animation


def register():
    add_bones.register()
    export_animation.register()
    import_animation.register()

def unregister():
    add_bones.unregister()
    export_animation.unregister()
    import_animation.unregister()
