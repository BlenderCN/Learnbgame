import bpy

import threading
import subprocess
import re


class SubstanceCheckThread(threading.Thread):

    def __init__(self, path_painter):
        threading.Thread.__init__(self)
        self.path_painter = path_painter

    def run(self):
        subprocess.call([self.path_painter, '-v'])


class SubstanceCheck(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "substance.check"
    bl_label = "Check the number version and path to Substance Painter"

    path = bpy.props.StringProperty(
        name="Substance Painter Path",
    )

    def execute(self, context):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["SubstanceBridge"].preferences
        self.path = str(addon_prefs.path_painter)

        launchpainter = SubstanceCheckThread(self.path)
        launchpainter.start()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SubstanceCheck)


def unregister():
    bpy.utils.unregister_class(SubstanceCheck)
