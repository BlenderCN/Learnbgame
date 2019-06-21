import re
import sys

import bpy

from bpy.types import PropertyGroup
from bpy.props import *
from bpy.utils import register_class, unregister_class

from . utility import addon, insert, update, shader

try: from . utility import smart
except:
    class smart:
        class update:
            def mirror_x(prop, context): sys.exit()
            def mirror_y(prop, context): sys.exit()
            def mirror_z(prop, context): sys.exit()
            def insert_target(prop, context): sys.exit()
            def main(prop, context): sys.exit()
            def type(prop, context): sys.exit()
            def author(prop, context): sys.exit()


def thumbnails(prop, context):
    return insert.thumbnails[prop.folder].images


def kpack_enum(pt, context):
    option = addon.option()

    items = []

    if len(option.kpack.categories):
        for index, category in enumerate(option.kpack.categories):
            if not option.filter or option.kpack.active_index == index or re.search(option.filter, category.name, re.I):
                items.append((category.name, category.name, '', category.blends[category.active_index].icon_id, index))

    return items

class file(PropertyGroup):
    location: StringProperty()
    icon: StringProperty()
    icon_id: IntProperty()


class folder(PropertyGroup):
    thumbnail: EnumProperty(update=update.thumbnails, items=thumbnails)
    active_index: IntProperty(update=update.active_index)
    blends: CollectionProperty(type=file)
    icon: StringProperty()
    folder: StringProperty()


class kpack(PropertyGroup):
    active_index: IntProperty()
    categories: CollectionProperty(type=folder)


class mat(PropertyGroup):
    material: BoolProperty()


class data(PropertyGroup):
    id: StringProperty()
    insert: BoolProperty()


class object(PropertyGroup):
    id: StringProperty()
    collection: StringProperty()
    label: StringProperty()
    author: StringProperty()
    insert: BoolProperty()
    inserted: BoolProperty()
    main_object: PointerProperty(type=bpy.types.Object)
    reserved_target: PointerProperty(type=bpy.types.Object)
    applied: BoolProperty()
    duplicate: BoolProperty()
    mirror: BoolProperty()
    mirror_target: PointerProperty(type=bpy.types.Object)
    animated: BoolProperty()

    mirror_x: BoolProperty(
        name = 'X',
        description = 'Mirror INSERT on Y axis of the INSERT target',
        update = smart.update.mirror_x,
        default = False)

    mirror_y: BoolProperty(
        name = 'Y',
        description = 'Mirror INSERT on X axis of the INSERT target',
        update = smart.update.mirror_y,
        default = False)

    mirror_z: BoolProperty(
        name = 'Z',
        description = 'Mirror INSERT on Z axis of the INSERT target',
        update = smart.update.mirror_z,
        default = False)

    insert_target: PointerProperty(
        name = 'Insert target',
        description = 'Target obj for the INSERT',
        update = smart.update.insert_target,
        type = bpy.types.Object)

    main: BoolProperty(
        name = 'Main obj',
        description = 'This obj will become the main obj of all the other objs for this INSERT',
        update = smart.update.main,
        default = False)

    type: EnumProperty(
        name = 'Object type',
        description = 'Change KIT OPS obj type',
        items = [
            ('SOLID', 'Solid', 'This obj does NOT cut and is renderable'),
            ('WIRE', 'Wire', 'This obj does NOT cut and is NOT renderable'),
            ('CUTTER', 'Cutter', 'This obj does cut and is NOT renderable')],
        update = smart.update.type,
        default = 'SOLID')

    boolean_type: EnumProperty(
        name = 'Boolean type',
        description = 'Boolean type to use for this obj',
        items = [
            ('DIFFERENCE', 'Difference', 'Combine two meshes in a subtractive way'),
            ('UNION', 'Union', 'Combine two meshes in an additive way'),
            ('INTERSECT', 'Intersect', 'Keep the part of the mesh that intersects with modifier obj')],
        default = 'DIFFERENCE')

    selection_ignore: BoolProperty(
        name = 'Selection ignore',
        description = 'Do not select this obj when using auto select',
        default = False)

    ground_box: BoolProperty(
        name = 'Ground box',
        description = 'Use to tell kitops that this is a ground box obj for thumbnail rendering',
        default = False)


class scene(PropertyGroup):
    thumbnail_scene: BoolProperty(
        name = 'Thumbnail scene',
        description = 'Tells KIT OPS that this scene is a thumbnail render scene for INSERTS',
        default = False)

    auto_parent: BoolProperty(
        name = 'Auto parent',
        description = 'Automatically parent all objs to the main obj when saving\n  Note: Incorrect parenting can lead to an unusable INSERT',
        default = False)

    animated: BoolProperty(
        name = 'Animated',
        description = 'Begin the timeline when you add this insert',
        default = False)


class options(PropertyGroup):
    kpack: PointerProperty(type=kpack)

    kpacks: EnumProperty(
        name = 'KPACKS',
        description = 'Available KPACKS',
        items = kpack_enum,
        update = update.kpacks)

    filter: StringProperty(
        name = 'Filter',
        description = 'Filter the kpacks list',
        options = {'TEXTEDIT_UPDATE'},
        default = '')

    author: StringProperty(
        name = 'Author',
        description = 'Kit author',
        update = smart.update.author,
        default = '')

    auto_scale: BoolProperty(
        name = 'Auto scale',
        description = 'Scale INSERTS based on obj size',
        default = True)

    auto_select: BoolProperty(
        name = 'Auto select INSERT',
        description = 'Select all objs related to the INSERT when selecting normally in blender',
        default = True)

    show_modifiers: BoolProperty(
        name = 'Modifiers',
        description = 'Toggle KIT OPS boolean modifier visibility',
        update = update.show_modifiers,
        default = True)

    show_solid_objects: BoolProperty(
        name = 'Solid objs',
        description = 'Show the KIT OPS solid objs',
        update = update.show_solid_objects,
        default = True)

    show_cutter_objects: BoolProperty(
        name = 'Cutter objs',
        description = 'Show the KIT OPS cutter objs',
        update = update.show_cutter_objects,
        default = True)

    show_wire_objects: BoolProperty(
        name = 'Wire objs',
        description = 'Show the KIT OPS wire objs',
        update = update.show_wire_objects,
        default = True)

classes = [
    file,
    folder,
    kpack,
    mat,
    data,
    object,
    scene,
    options]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.kitops = PointerProperty(name='KIT OPS', type=options)
    bpy.types.Scene.kitops = PointerProperty(name='KIT OPS', type=scene)
    bpy.types.Object.kitops = PointerProperty(name='KIT OPS', type=object)
    bpy.types.GreasePencil.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Light.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Camera.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Speaker.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Lattice.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Armature.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Curve.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.MetaBall.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Mesh.kitops = PointerProperty(name='KIT OPS', type=data)
    bpy.types.Material.kitops = PointerProperty(name='KIT OPS', type=mat)

    # shader.register()
    update.icons()
    addon.option()


def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.WindowManager.kitops
    del bpy.types.Scene.kitops
    del bpy.types.Object.kitops
    del bpy.types.GreasePencil.kitops
    del bpy.types.Light.kitops
    del bpy.types.Camera.kitops
    del bpy.types.Speaker.kitops
    del bpy.types.Lattice.kitops
    del bpy.types.Armature.kitops
    del bpy.types.Curve.kitops
    del bpy.types.MetaBall.kitops
    del bpy.types.Mesh.kitops
    del bpy.types.Material.kitops

    # shader.unregister()

    addon.icons['main'].close()
    del addon.icons['main']
