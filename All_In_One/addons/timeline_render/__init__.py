# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_timeline_render
#
# Version history:
#   1.0. - Render frames from the first line of the text block by numbers and diapasones

bl_info = {
    'name': 'TimeLineRender',
    'category': 'Render',
    'author': 'Nikita Akimov',
    'version': (1, 0, 0),
    'blender': (2, 79, 0),
    'location': 'Properties window -> Render Panel > TimeLineRender',
    'wiki_url': 'https://github.com/Korchy/1d_timeline_render',
    'tracker_url': 'https://github.com/Korchy/1d_timeline_render',
    'description': 'TimeLineRender - Render a sequence of frame numbers'
}

from . import timelinerender_ops
from . import timelinerender_panel


def register():
    timelinerender_ops.register()
    timelinerender_panel.register()


def unregister():
    timelinerender_panel.unregister()
    timelinerender_ops.unregister()


if __name__ == '__main__':
    register()
