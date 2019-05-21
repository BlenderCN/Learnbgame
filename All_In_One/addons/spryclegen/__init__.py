import bpy
from . import (
    ops,
    exporter,
    preview,
    ui
)

bl_info = {
    "name": "sprycle (.spry)",
    "author": "Goran Milovanovic",
    "blender": (2, 7, 1),
    "location": "File > Import-Export",
    "description": "Export sprite animation data to sprycle (.spry) file.",
    "wiki_url": "https://github.com/GoranM/sprycle/wiki",
    "tracker_url": "https://github.com/GoranM/sprycle/issues",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

modules = ops.modules + [exporter, preview, ui]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()
