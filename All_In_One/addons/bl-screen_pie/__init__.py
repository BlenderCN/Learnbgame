from . import screen_pie

import bpy


bl_info = {'name': 'Screen Pie Menu',
           'description': 'Select screen using pie menu.',
           'location' : "Add shortcut to `ui.screen_pie_menu`",
           'author': 'miniukof',
           'version': (0, 0, 2),
           'blender': (2, 76, 11),
           'category': 'User Interface',
           'wiki_url': 'https://github.com/miniukof/bl-screen_pie'
          }


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
