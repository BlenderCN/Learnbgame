import bpy
from mathutils import Vector
from console_python import add_scrollback

import os
import sys


def run_operator_register(a, b):
    base = os.path.dirname(__file__)
    path_to_file = os.path.join(base, a, b)

    text = bpy.data.texts.load(path_to_file)
    ctx = bpy.context.copy()
    ctx['edit_text'] = text
    bpy.ops.text.run_script(ctx)

    msg = 'added ' + b
    add_scrollback(msg, 'INFO')


# def register():
#     bpy.utils.register_module(__name__)


# def unregister():
#     bpy.utils.unregister_module(__name__)
