#!/usr/bin/env python

import bpy
from .chophuman import ChopHumanPanel, ChopHumanOperator, RenderChoppedHumanOperator


bl_info = {
    'name': 'Chop Human',
    'description': 'Facilitates the creation of 2-D cutout-style characters from MakeHuman output.',
    'author': 'Adam Wentz',
    'version': (0, 1),
    'category': 'MakeHuman'
}


def register():
    bpy.utils.register_class(ChopHumanOperator)
    bpy.utils.register_class(RenderChoppedHumanOperator)
    bpy.utils.register_class(ChopHumanPanel)
    

def unregister():
    bpy.utils.unregister_class(ChopHumanPanel)
    bpy.utils.unregister_class(ChopHumanOperator)
    bpy.utils.unregister_class(RenderChoppedHumanOperator)
    

if __name__ == '__main__':
    register()
