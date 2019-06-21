import bpy
from bpy.app.handlers import persistent
from . import utils as ut

def select_frame(frame):
    display = [o for o in bpy.context.scene.objects if "display_" in o.name][0]
    ut.uvs(display, ut.uvs(frame))
    ut.make_active(frame)


# Public

@persistent
def animate(scene):
    """ 
    A bpy.app.handlers.frame_change_pre callback.

    Manipulates the UV coordinates of the display plane, 
    to simulate a preview of the sprite animation cycle.

    """

    selected = bpy.context.active_object
    frames = [o for o in scene.objects if ut.base_name(o) == ut.base_name(selected)]
    frames.sort(key=lambda o: o.matrix_world.translation.x)
    select_frame(ut.next_object(frames, selected))


def register():
    bpy.app.handlers.frame_change_pre.append(animate)

def unregister():
    bpy.app.handlers.frame_change_pre.remove(animate)
