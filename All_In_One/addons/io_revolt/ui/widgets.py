"""
Widgets are little panel snippets that generally warn users if something isn't
set up correctly to use a feature. They return true if something isn't right.
They return false if everything is alright.
"""
import bpy
from ..common import *

def widget_texture_mode(self):
    if not texture_mode_enabled():
        props = bpy.context.scene.revolt
        box = self.layout.box()
        box.label(text="Texture Mode is not enabled.", icon='INFO')
        row = box.row()
        if props.prefer_tex_solid_mode:
            row.operator("helpers.enable_textured_solid_mode",
                         text="Enable Texture Mode",
                         icon="POTATO")
        else:
            row.operator("helpers.enable_texture_mode",
                         text="Enable Texture Mode",
                         icon="POTATO")

        return True
    return False

def widget_vertex_color_channel(self, obj):
    if not obj.data.vertex_colors:
        box = self.layout.box()
        box.label(text="No Vertex Color Layer.", icon='INFO')
        row = box.row()
        row.operator("mesh.vertex_color_add", icon='PLUS',
                     text="Create Vertex Color Layer")
        return True
    return False
