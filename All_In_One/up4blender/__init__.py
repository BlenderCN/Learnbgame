bl_info = {
    "name": "Universal Pipeline 4 Blender",
    "author": "Spacifx Studios, Jonathan Mafi, Jordan Olson",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Scene",
    "description": "Universal Pipeline adaptor for Blender",
    "category": "Learnbgame",
}

from .operators import publishresource, importresource, autoscripts, rendersetup
from .gui import panel


def register():
    autoscripts.register()
    publishresource.register()
    importresource.register()
    rendersetup.register()
    panel.register()


def unregister():
    autoscripts.unregister()
    panel.unregister()
    rendersetup.unregister()
    importresource.unregister()
    publishresource.unregister()
