import bpy
import re


bl_info = {
    'name': 'Camtime',
    'author': 'Mark Riedesel (Klowner)',
    'version': (0, 0, 1),
    'blender': (2, 70, 0),
    'description': 'Auto-seek to frame based on active Camera attributes',
    "category": "Learnbgame",
    'support': 'COMMUNITY',
}


class Camtime(object):
    frameExpr = re.compile(r'^.*frame\[([0-9]*)\].*$')

    def __init__(self):
        self.currentCam = None

    def __call__(self, scene):
        newCam = scene.camera
        gotoFrame = None

        if newCam != self.currentCam:
            cam = self.currentCam = newCam

            # Does the newly selected camera have a frame specifier
            # in the name? eg: 'Camera20_frame[42]'
            match = self.frameExpr.match(cam.name)
            if match:
                gotoFrame = int(match.groups()[0])

            # If the newly selected camera has a custom property
            # name `frame`, jump to it.
            elif cam.data.get('frame'):
                gotoFrame = cam.data.get('frame')

            if gotoFrame:
                bpy.context.scene.frame_set(gotoFrame)


def register():
    bpy.app.handlers.scene_update_pre.append(Camtime())


def unregister():
    for handler in bpy.app.handlers.scene_update_pre:
        if isinstance(handler, Camtime):
            bpy.app.handlers.scene_update_pre.remove(handler)
