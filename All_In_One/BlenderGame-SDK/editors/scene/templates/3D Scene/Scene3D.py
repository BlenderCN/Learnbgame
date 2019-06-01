from SDK_utils import *
import bpy
from . import ressource

class Scene3D(ressource.Scene):

    def __init__(self):

        new_scene = bpy.data.scenes.new("Scene 3D")
        new_scene.
        bpy.context.screen.scene = new_scene
        