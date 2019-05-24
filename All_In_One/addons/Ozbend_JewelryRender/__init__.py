# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender

bl_info = {
    'name': 'JewelryRender',
    "category": "Learnbgame",
    'author': 'Nikita Akimov',
    'version': (1, 4, 0),
    'blender': (2, 79, 0),
    'location': 'Properties window -> Render Panel > JewelryRender',
    'wiki_url': 'https://github.com/Korchy/Ozbend_JewelryRender',
    'tracker_url': 'https://github.com/Korchy/Ozbend_JewelryRender',
    'description': 'JewelryRender - project manager to render jewelry'
}

from . import jewelryrender_ops
from . import jewelryrender_panel


def register():
    jewelryrender_ops.register()
    jewelryrender_panel.register()


def unregister():
    jewelryrender_panel.unregister()
    jewelryrender_ops.unregister()


if __name__ == '__main__':
    register()
