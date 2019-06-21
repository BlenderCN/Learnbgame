import bpy
from ..common import *

class RevoltScenePanel(bpy.types.Panel):
    """ Panel for .w properties """
    bl_label = "Re-Volt .w Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"HIDE_HEADER"}


    def draw(self, context):
        props = context.scene.revolt
        layout = self.layout

        layout.label("Re-Volt Properties")

        layout.prop(props, "texture_animations")