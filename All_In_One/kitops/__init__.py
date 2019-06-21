# Copyright (C) 2018 chippwalters, masterxeon1001 All Rights Reserved

bl_info = {
    'name': 'KIT OPS',
    'author': 'Chipp Walters, MX2, proxe',
    'version': (1, '13          Commit: 754'),
    'blender': (2, 80, 0),
    'location': 'View3D > Toolshelf (T)',
    'description': 'Streamlined kit bash library with additional productivity tools',
    'wiki_url': 'https://docs.google.com/document/d/1rjyJ-AbKuPRL-J9-48l5KPNHBkDcFE4UQ51Jsm5eqiM/edit?usp=sharing',
    'category': '3D View'}

import bpy

from bpy.props import PointerProperty

from . addon import preference, property
from . addon.interface import operator, panel
from . addon.utility import handler


def register():
    preference.register()
    property.register()

    operator.register()
    panel.register()

    handler.register()


def unregister():
    handler.unregister()

    panel.unregister()
    operator.unregister()

    property.unregister()
    preference.unregister()
