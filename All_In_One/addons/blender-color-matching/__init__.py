# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/blender-color-matching


bl_info = {
    'name': 'Color matching',
    'category': 'All',
    'author': 'Nikita Akimov',
    'version': (1, 1, 0),
    'blender': (2, 79, 0),
    'location': 'The 3D_View window - T-panel - the ColorMatching tab',
    'wiki_url': 'https://b3d.interplanety.org/en/blender-add-on-color-matching/',
    'tracker_url': 'https://b3d.interplanety.org/en/blender-add-on-color-matching/',
    'description': 'Search for some nearest alternative system colors by RGB value'
}

from . import color_matching_panel
from . import color_matching_ops
from . import color_matching


def register():
    color_matching.register()
    color_matching_ops.register()
    color_matching_panel.register()


def unregister():
    color_matching_panel.unregister()
    color_matching_ops.unregister()
    color_matching.unregister()


if __name__ == '__main__':
    register()
