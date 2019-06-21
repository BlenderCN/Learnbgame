import sys

import bpy
from bpy.app.handlers import persistent, depsgraph_update_pre, depsgraph_update_post, load_pre, load_post, save_pre

from . import addon, shader, insert, remove, update

smart_enabled = True
try: from . import smart
except: smart_enabled = False


#TODO: switch to timer modal
class pre:


    @persistent
    def depsgraph(none):
        if not insert.authoring():

            if smart_enabled:
                smart.insert_depsgraph_update_pre()

            insert.correct_ids()

        elif not smart_enabled:
            for obj in bpy.data.objects:
                try:
                    obj.select_set(False)
                except RuntimeError: pass

        if not smart_enabled:
            for obj in bpy.data.objects:
                if obj.kitops.main and not obj.kitops.id:
                    sys.exit()


    @persistent
    def load(none):
        # if shader.handler:
        #     bpy.types.SpaceView3D.draw_handler_remove(shader.handler, 'WINDOW')

        # shader.handler = None

        if not smart_enabled:
            for obj in bpy.data.objects:
                if obj.kitops.main and not obj.kitops.id:
                    sys.exit()


    @persistent
    def save(none):
        option = addon.option()

        # if shader.handler:
        #     bpy.types.SpaceView3D.draw_handler_remove(shader.handler, 'WINDOW')
        #     shader.handler = None

        if smart_enabled:
            smart.authoring_save_pre()

        if not smart_enabled:
            for obj in bpy.data.objects:
                if obj.kitops.main and not obj.kitops.id:
                    sys.exit()


class post:


    @persistent
    def depsgraph(none):
        preference = addon.preference()
        option = addon.option()

        if insert.authoring():
            if smart_enabled:
                smart.authoring_depsgraph_update_post()
        else:
            if not insert.operator:
                for obj in [ob for ob in bpy.data.objects if ob.kitops.duplicate]:
                    remove.object(obj, data=True)

            if addon.preference().mode == 'SMART' or addon.preference().enable_auto_select:
                insert.select()

            if not insert.operator:

                if smart_enabled:
                    smart.toggles_depsgraph_update_post()

        if not smart_enabled:
            for obj in bpy.data.objects:
                if obj.kitops.main and not obj.kitops.id:
                    sys.exit()


    @persistent
    def load(none):
        option = addon.option()

        # shader.handler = bpy.types.SpaceView3D.draw_handler_add(shader.border, (None, bpy.context), 'WINDOW', 'POST_PIXEL')

        if insert.authoring():
            if smart_enabled:
                smart.authoring_load_post()
            else:
                for obj in bpy.data.objects:
                    obj.kitops.applied = True

        if not smart_enabled:
            for obj in bpy.data.objects:
                if obj.kitops.main and not obj.kitops.id:
                    sys.exit()


def register():
    depsgraph_update_pre.append(pre.depsgraph)
    depsgraph_update_post.append(post.depsgraph)
    load_pre.append(pre.load)
    load_post.append(post.load)
    save_pre.append(pre.save)


def unregister():
    depsgraph_update_pre.remove(pre.depsgraph)
    depsgraph_update_post.remove(post.depsgraph)
    load_pre.remove(pre.load)
    load_post.remove(post.load)
    save_pre.remove(pre.save)
