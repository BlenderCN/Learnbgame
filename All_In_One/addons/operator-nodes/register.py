import bpy
from . import ui
from . import menu
from . import trees
from . import nodes
from . import sockets
from . import contexts
from . import operators

def register():
    trees.register()

    operators.register()
    contexts.register()
    sockets.register()
    nodes.register()
    menu.register()
    ui.register()

def unregister():
    ui.unregister()
    menu.unregister()
    nodes.unregister()
    sockets.unregister()
    contexts.unregister()
    operators.unregister()

    trees.unregister()