
from . import bake_mesh
from . import bake_particles
from . import objects
from . import operators
from . import ui
from . import render
from . import create


modules = [
    objects,
    operators,
    bake_mesh,
    bake_particles,
    ui,
    render,
    create
]

def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
