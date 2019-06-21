from .LOD import *
from .Camera import *
from .Sun import *
from .Renderer import *


class Rig:
    @staticmethod
    def setup(rotation, zoom):
        if CAM_NAME not in bpy.data.objects:
            Camera.add_to_scene()
        if SUN_NAME not in bpy.data.objects:
            Sun.add_to_scene()
        if LOD_NAME not in bpy.data.objects:
            LOD.fit_new()

        Camera.update(rotation, zoom)
        Sun.update(rotation)
        bpy.context.scene.update()

    @staticmethod
    def lod_fit():
        Rig.lod_delete()
        LOD.fit_new()

    @staticmethod
    def lod_delete():
        if LOD_NAME in bpy.data.objects:
            ob = bpy.data.objects[LOD_NAME]
            bpy.data.meshes.remove(ob.data)
            bpy.data.objects.remove(ob, do_unlink=True, do_ui_user=True)
        bpy.context.scene.update()
