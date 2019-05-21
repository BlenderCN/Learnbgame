import bpy
from . utils.recursion import no_recursion
from . tree_context import update_contexts
from . tree_info import update_if_necessary
from bpy.app.handlers import scene_update_post, persistent

@persistent
@no_recursion
def update(scene):
    update_if_necessary()
    update_contexts()


def register():
    scene_update_post.append(update)

def unregister():
    scene_update_post.remove(update)
