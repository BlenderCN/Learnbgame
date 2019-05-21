import sys

import bpy
from bpy.app.handlers import persistent

from . import addon, draw, insert, remove, update

smart_enabled = True
try: from . import smart
except: smart_enabled = False

@persistent
def scene_update_pre(none):
    global smart_enabled

    if not insert.authoring():

        if smart_enabled:
            smart.insert_scene_update_pre()

        insert.correct_ids()

    elif not smart_enabled:
        for object in bpy.data.objects:
            object.select = False

    if not smart_enabled:
        for object in bpy.data.objects:
            if object.kitops.main and not object.kitops.id:
                sys.exit()

@persistent
def scene_update_post(none):
    global smart_enabled

    preference = addon.preference()
    option = addon.option()

    if insert.authoring():
        if smart_enabled:
            smart.authoring_scene_update_post()
    else:
        if not insert.operator:
            for object in [object for object in bpy.data.objects if object.kitops.duplicate]:
                remove.object(object, data=True)

        if addon.preference().mode == 'SMART' or addon.preference().enable_auto_select:
            insert.select()

        if not insert.operator:

            if smart_enabled:
                smart.toggles_scene_update_post()

    if not smart_enabled:
        for object in bpy.data.objects:
            if object.kitops.main and not object.kitops.id:
                sys.exit()

@persistent
def load_pre(none):
    global smart_enabled

    if draw.handler:
        bpy.types.SpaceView3D.draw_handler_remove(draw.handler, 'WINDOW')

    draw.handler = None

    if not smart_enabled:
        for object in bpy.data.objects:
            if object.kitops.main and not object.kitops.id:
                sys.exit()

@persistent
def load_post(none):
    global smart_enabled

    option = addon.option()

    draw.handler = bpy.types.SpaceView3D.draw_handler_add(draw.border, (None, bpy.context), 'WINDOW', 'POST_PIXEL')

    if insert.authoring():
        if smart_enabled:
            smart.authoring_load_post()
    else:
        update.category(None, bpy.context)

    if not smart_enabled:
        for object in bpy.data.objects:
            if object.kitops.main and not object.kitops.id:
                sys.exit()

@persistent
def save_pre(none):
    global smart_enabled

    option = addon.option()

    if draw.handler:
        bpy.types.SpaceView3D.draw_handler_remove(draw.handler, 'WINDOW')
        draw.handler = None

    if smart_enabled:
        smart.authoring_save_pre()

    if not smart_enabled:
        for object in bpy.data.objects:
            if object.kitops.main and not object.kitops.id:
                sys.exit()
