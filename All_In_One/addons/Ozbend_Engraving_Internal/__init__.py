# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_Engraving_Internal

bl_info = {
    'name': 'Engraving_Internal',
    'category': 'Render',
    'author': 'Nikita Akimov',
    'version': (1, 1, 0),
    'blender': (2, 79, 0),
    'location': 'Properties window -> Render Panel > EngravingInternal',
    'wiki_url': 'https://github.com/Korchy/Ozbend_Engraving_Internal',
    'tracker_url': 'https://github.com/Korchy/Ozbend_Engraving_Internal',
    'description': 'Engraving_Internal - part of JewelryRender to render only engraving without objects'
}

from . import engraving_internal_ops
from . import engraving_internal_panel


def register():
    engraving_internal_ops.register()
    engraving_internal_panel.register()


def unregister():
    engraving_internal_panel.unregister()
    engraving_internal_ops.unregister()


if __name__ == '__main__':
    register()
