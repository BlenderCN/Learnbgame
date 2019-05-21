import bpy
from . import (
    exporter,
    ops,
    ui
)

bl_info = {
    "name": "BDX (.bdx)",
    "author": "Goran Milovanovic",
    "blender": (2, 7, 6),
    "location": "File > Import-Export",
    "description": "Export scene to BDX (.bdx) file.",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'TESTING',
    "category": "Import-Export"
}

modules = ops.modules + [exporter, ui]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()
