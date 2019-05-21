# Copyright (C) 2018 chippwalters, masterxeon1001 All Rights Reserved

bl_info = {
    'name': 'KIT OPS PRO',
    'author': 'Chipp Walters, MX2, proxe',
    'version': (1, '0          Commit: 648'),
    'blender': (2, 80, 0),
    'location': 'View3D > Toolshelf (T)',
    'description': 'Streamlined kit bash library with additional productivity tools',
    'category': 'Learnbgame'}

import bpy

from bpy.utils import register_class, unregister_class
from bpy.props import PointerProperty

from . addon import *
from .addon.utility import addon as addon_util
from .addon.utility import handler, draw, update

try:
    from .addon.utility import smart

    smart_objects = [
        smart.ApplyInsert,
        smart.RemoveInsert,
        smart.RenderThumbnail,
        smart.AlignHorizontal,
        smart.AlignVertical,
        smart.AlignLeft,
        smart.AlignRight,
        smart.AlignTop,
        smart.AlignBottom,
        smart.StretchWide,
        smart.StretchTall]
except:

    smart_objects = []

objects = [
    operator.Purchase,
    operator.visit,
    operator.Documentation,
    operator.AddKPackPath,
    operator.RemoveKPackPath,
    operator.RefreshKPacks,
    operator.AddInsert,
    operator.SelectInserts,
    panel.Tools,
    panel.List,
    preference.Folder,
    preference.KitOps,
    property.File,
    property.Folder,
    property.KPack,
    property.Data,
    property.Object,
    property.Scene,
    property.Options]

objects += smart_objects

def register():
    bpy.app.handlers.scene_update_pre.append(handler.scene_update_pre)
    bpy.app.handlers.scene_update_post.append(handler.scene_update_post)
    bpy.app.handlers.load_pre.append(handler.load_pre)
    bpy.app.handlers.load_post.append(handler.load_post)
    bpy.app.handlers.save_pre.append(handler.save_pre)
    bpy.app.handlers.save_post.append(handler.load_post)

    for object in objects:
        register_class(object)

    bpy.types.WindowManager.kitops = PointerProperty(name='KIT OPS', type=property.Options)
    bpy.types.Scene.kitops = PointerProperty(name='KIT OPS', type=property.Scene)
    bpy.types.Object.kitops = PointerProperty(name='KIT OPS', type=property.Object)
    bpy.types.Lamp.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.Camera.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.Speaker.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.Lattice.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.Armature.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.Curve.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.MetaBall.kitops = PointerProperty(name='KIT OPS', type=property.Data)
    bpy.types.Mesh.kitops = PointerProperty(name='KIT OPS', type=property.Data)

    print('Registered KIT OPS with {} modules'.format(len(objects)))

    update.icons()

def unregister():
    bpy.app.handlers.scene_update_pre.remove(handler.scene_update_pre)
    bpy.app.handlers.scene_update_post.remove(handler.scene_update_post)
    bpy.app.handlers.load_pre.remove(handler.load_pre)
    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.app.handlers.save_pre.remove(handler.save_pre)
    bpy.app.handlers.save_post.remove(handler.load_post)

    del bpy.types.WindowManager.kitops
    del bpy.types.Scene.kitops
    del bpy.types.Object.kitops
    del bpy.types.Lamp.kitops
    del bpy.types.Camera.kitops
    del bpy.types.Speaker.kitops
    del bpy.types.Lattice.kitops
    del bpy.types.Armature.kitops
    del bpy.types.Curve.kitops
    del bpy.types.MetaBall.kitops
    del bpy.types.Mesh.kitops

    if draw.handler:
        bpy.types.SpaceView3D.draw_handler_remove(draw.handler, 'WINDOW')
        draw.handler = None

    for object in objects:
        unregister_class(object)

    addon_util.icons['main'].close()
    del addon_util.icons['main']
