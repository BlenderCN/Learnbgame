
if "bpy" in locals():
    import imp
    unregister()
    #pylint: disable=used-before-assignment
    imp.reload(pman)
    imp.reload(blend2bam)
    imp.reload(learnbgame_engine)
    imp.reload(ui)
    imp.reload(operators)
    imp.reload(properties)
else:
    import bpy
    import sys
    import os
    # Add this folder to the path to find PyOpenGL and pkg_resources
    FILEDIR = os.path.dirname(__file__)
    sys.path.append(FILEDIR)
    # ... and pman
    sys.path.append(os.path.join(FILEDIR, 'pman'))
    import pman
    # .. and blend2bam
    sys.path.append(os.path.join(FILEDIR, 'panda3d-blend2bam'))
    import blend2bam
    from . import learnbgame_engine
    from . import ui
    from . import operators
    from . import properties

@bpy.app.handlers.persistent
def load_handler(_dummy):
    operators.update_blender_path()

def register():
    learnbgame_engine.register()
    ui.register()
    operators.register()
    properties.register()
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    ui.unregister()
    learnbgame_engine.unregister()
    operators.unregister()
    properties.unregister()
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
