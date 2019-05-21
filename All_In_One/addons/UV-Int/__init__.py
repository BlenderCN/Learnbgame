# Nikita Akimov
# interplanety@interplanety.org

bl_info = {
    'name': 'UV-Int',
    'category': 'UV',
    'author': 'Nikita Akimov',
    'version': (1, 0, 1),
    'blender': (2, 79, 0),
    'location': 'UV/Image Editor -> T-Panel > UV-Int',
    'wiki_url': 'https://b3d.interplanety.org/en/uv-int-add-on/',
    'tracker_url': 'https://b3d.interplanety.org/en/uv-int-add-on/',
    'description': 'UV-Int - some additional tools for working with uv-map'
}

from . import uv_int
from . import uv_int_panel


def register():
    uv_int.register()
    uv_int_panel.register()


def unregister():
    uv_int.unregister()
    uv_int_panel.unregister()


if __name__ == "__main__":
    register()
