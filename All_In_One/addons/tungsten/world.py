import bpy
from bl_ui import properties_world

from . import base
from .texture import ColorTextureProperty

base.compatify_class(properties_world.WORLD_PT_context_world)
base.compatify_class(properties_world.WORLD_PT_custom_props)

@base.register_root_panel
class W_PT_world(properties_world.WorldButtonsPanel, base.RootPanel):
    bl_label = "Tungsten World"
    prop_class = bpy.types.World

    @classmethod
    def get_object(cls, context):
        return context.world

    PROPERTIES = {
        'emission': ColorTextureProperty(
            name='Emission',
            description='Emission',
            default=(0.1, 0.1, 0.2),
        ),
    }

    @classmethod
    def to_scene_data(self, scene, world):
        w = world.tungsten
        d = {
            'type': 'infinite_sphere',
            'bsdf': {'type': 'null'},
            'emission': w.emission.to_scene_data(scene, w),
        }

        if d['emission'] == [0.0, 0.0, 0.0]:
            del d['emission']

        return d

    def draw_for_object(self, world):
        layout = self.layout
        w = world.tungsten

        w.emission.draw(layout, w)
