import bpy
from .base import register_class

@register_class
class TungstenPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    tungsten_server_path = bpy.props.StringProperty(
        name="Tungsten Server Path",
        description="Tungsten Server Path",
        subtype='FILE_PATH',
        default='',
    )

    def draw(self, context):
        lay = self.layout

        lay.prop(self, 'tungsten_server_path')
