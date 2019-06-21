import os

import bpy

name = __name__.partition('.')[0]

icons = {}


class path:


    def __new__(self):
        return os.path.abspath(os.path.join(__file__, '..', '..', '..'))


    def icons():
        return os.path.join(path(), 'icons')


def preference():
    preference = bpy.context.preferences.addons[name].preferences

    return preference
