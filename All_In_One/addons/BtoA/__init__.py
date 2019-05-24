bl_info = {
    "name": "BtoA - Blender to Arnold",
    "author": "Rudy Cortes - rudy@rudycortes.com",
    "version": (0, 0, 2),
    "blender": (2, 5, 9),
    "api": 35622,
    "location": "Render > Engine > Arnold",
    "description": "Arnold integration for blender",
    "warning": "Still early alpha",
    "wiki_url": "https://github.com/fxjeane/BtoA",
    "tracker_url": "https://github.com/fxjeane/BtoA/issues?sort=created&direction=desc&state=open",
    "category": "Learnbgame",
}


import imp
if "bpy" in locals():
    imp.reload(utils)
    imp.reload(BtoAUi)
    imp.reload(Renderer)
    imp.reload(Options)
    imp.reload(Camera)
    imp.reload(Lights)
    imp.reload(Materials)
    imp.reload(Textures)
    imp.reload(Meshes)
else:
    import bpy
    from . import utils
    from . import BtoAUi
    from . import Renderer
    from . import Options
    from . import Camera
    from . import Lights
    from . import Materials
    from . import Textures
    from . import Meshes


def register():
    bpy.utils.register_module(__name__)

def unregister():
    import bpy
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

