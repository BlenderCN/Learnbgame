import bpy
from . import iso_camera
from bpy.props import StringProperty, FloatProperty

bl_info = {
    'name': 'Sprite Tools',
    'author': 'Roman Merkushin',
    'version': (0, 1, 0),
    'location': 'Tool Bar -> Sprite Tools',
    'description': 'Helps to render sprite images',
    'warning': '',
    'wiki_url': 'https://github.com/rmerkushin/blender_sprite_tools',
    'tracker_url': 'https://github.com/rmerkushin/blender_sprite_tools/issues',
    'support': 'COMMUNITY',
    'category': 'Render'
}

bpy.types.Scene.render_prefix = StringProperty(
    name='prefix',
    description='Prefix for sprite names',
    default='sprite',
    maxlen=32
)

bpy.types.Scene.render_path = StringProperty(
    name='path',
    description='Path to render output',
    default='',
    maxlen=1024,
    subtype='DIR_PATH'
)

bpy.types.Scene.camera_distance = FloatProperty(
    name='distance',
    description='Distance between camera and target object',
    default=10,
    precision=5,
    min=0,
    max=100,
    update=iso_camera.update_distance
)


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
