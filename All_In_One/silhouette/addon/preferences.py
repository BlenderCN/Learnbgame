import bpy

from bpy.types import AddonPreferences
from bpy.props import FloatVectorProperty

from .config import defaults

class silhouette(AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    default = defaults

    background_color = FloatVectorProperty(
        name = 'Background Color',
        description = 'The background color to use when displaying silhouettes.',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = default['background_color']
    )

    def draw(self, context):

        layout = self.layout

        layout.prop(self, 'background_color')
