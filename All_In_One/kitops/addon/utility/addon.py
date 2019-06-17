import os

import bpy

from . import update

name = __name__.partition('.')[0]
icons = {}


class path:

    def __new__(self):
        return os.path.abspath(os.path.join(__file__, '..', '..', '..'))

    def icons():
        return os.path.join(path(), 'icons')

    def default_kpack():
        return os.path.join(path(), 'Master')

    def thumbnail_scene():
        return os.path.join(path.default_kpack(), 'render_scene.blend')

    def default_thumbnail():
        return os.path.join(path.default_kpack(), 'thumb.png')


def preference():
    preference = bpy.context.preferences.addons[name].preferences

    if not len(preference.folders):
        folder = preference.folders.add()
        folder.name = 'KPACK'
        folder.location = path.default_kpack()

    return preference


def option():
    option = bpy.context.window_manager.kitops

    if not option.name:
        option.name = 'options'
        update.options()

    return option
