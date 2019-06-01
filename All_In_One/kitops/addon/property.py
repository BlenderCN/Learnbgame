import sys

import bpy

from bpy.types import PropertyGroup
from bpy.props import *

from . utility import insert, update


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

class File(PropertyGroup):
    location = StringProperty()
    icon = StringProperty()
    icon_id = IntProperty()

class Folder(PropertyGroup):
    thumbnail = EnumProperty(update=update.thumbnails, items=thumbnails)
    active_index = IntProperty(update=update.active_index)
    blends = CollectionProperty(type=File)
    icon = StringProperty()
    folder = StringProperty()

class KPack(PropertyGroup):
    active_index = IntProperty()
    categories = CollectionProperty(type=Folder)

class Data(PropertyGroup):
    id = StringProperty()
    insert = BoolProperty()

class Object(PropertyGroup):
    id = StringProperty()
    collection = StringProperty()
    label = StringProperty()
    author = StringProperty()
    insert = BoolProperty()
    inserted = BoolProperty()
    main_object = PointerProperty(type=bpy.types.Object)
    reserved_target = PointerProperty(type=bpy.types.Object)
    applied = BoolProperty()
    duplicate = BoolProperty()
    mirror = BoolProperty()
    mirror_target = PointerProperty(type=bpy.types.Object)
    animated = BoolProperty()

    mirror_x = BoolProperty(
        name = 'X',
        description = 'Mirror INSERT on Y axis of the INSERT target',
        update = smart.update.mirror_x,
        default = False)

    mirror_y = BoolProperty(
        name = 'Y',
        description = 'Mirror INSERT on X axis of the INSERT target',
        update = smart.update.mirror_y,
        default = False)

    mirror_z = BoolProperty(
        name = 'Z',
        description = 'Mirror INSERT on Z axis of the INSERT target',
        update = smart.update.mirror_z,
        default = False)

    insert_target = PointerProperty(
        name = 'Insert target',
        description = 'Target object for the INSERT',
        update = smart.update.insert_target,
        type = bpy.types.Object)

    main = BoolProperty(
        name = 'Main object',
        description = 'This object will become the main object of all the other objects for this INSERT',
        update = smart.update.main,
        default = False)

    type = EnumProperty(
        name = 'Object type',
        description = 'Change KIT OPS object type',
        items = [
            ('SOLID', 'Solid', 'This object does NOT cut and is renderable'),
            ('WIRE', 'Wire', 'This object does NOT cut and is NOT renderable'),
            ('CUTTER', 'Cutter', 'This object does cut and is NOT renderable')],
        update = smart.update.type,
        default = 'SOLID')

    boolean_type = EnumProperty(
        name = 'Boolean type',
        description = 'Boolean type to use for this object',
        items = [
            ('DIFFERENCE', 'Difference', 'Combine two meshes in a subtractive way'),
            ('UNION', 'Union', 'Combine two meshes in an additive way'),
            ('INTERSECT', 'Intersect', 'Keep the part of the mesh that intersects with modifier object')],
        default = 'DIFFERENCE')

    selection_ignore = BoolProperty(
        name = 'Selection ignore',
        description = 'Do not select this object when using auto select',
        default = False)

    ground_box = BoolProperty(
        name = 'Ground box',
        description = 'Use to tell kitops that this is a ground box object for thumbnail rendering',
        default = False)

class Scene(PropertyGroup):
    thumbnail_scene = BoolProperty(
        name = 'Thumbnail scene',
        description = 'Tells KIT OPS that this scene is a thumbnail render scene for INSERTS',
        default = False)

    auto_parent = BoolProperty(
        name = 'Auto parent',
        description = 'Automatically parent all objects to the main object when saving\n  Note: Incorrect parenting can lead to an unusable INSERT',
        default = True)

    animated = BoolProperty(
        name = 'Animated',
        description = 'Begin the timeline when you add this insert',
        default = False)

class Options(PropertyGroup):
    kpack = PointerProperty(type=KPack)

    author = StringProperty(
        name = 'Author',
        description = 'Kit author',
        update = smart.update.author,
        default = '')

    auto_scale = BoolProperty(
        name = 'Auto scale',
        description = 'Scale INSERTS based on object size',
        default = True)

    auto_select = BoolProperty(
        name = 'Auto select INSERT',
        description = 'Select all objects related to the INSERT when selecting normally in blender',
        default = True)

    show_modifiers = BoolProperty(
        name = 'Modifiers',
        description = 'Toggle KIT OPS boolean modifier visibility',
        update = update.show_modifiers,
        default = True)

    show_solid_objects = BoolProperty(
        name = 'Solid objects',
        description = 'Show the KIT OPS solid objects',
        update = update.show_solid_objects,
        default = True)

    show_cutter_objects = BoolProperty(
        name = 'Cutter objects',
        description = 'Show the KIT OPS cutter objects',
        update = update.show_cutter_objects,
        default = True)

    show_wire_objects = BoolProperty(
        name = 'Wire objects',
        description = 'Show the KIT OPS wire objects',
        update = update.show_wire_objects,
        default = True)
