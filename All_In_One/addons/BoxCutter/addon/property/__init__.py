import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import PropertyGroup, Object, Collection
from bpy.props import *

from . import data, last, object, snap
from .. utility import addon


def change_start_operation(option, context):
    for tool in context.workspace.tools:
        if tool.idname == 'BoxCutter':
            tool.operator_properties('bc.draw_shape').operation = option.start_operation

    context.workspace.tools.update()


def mesh_objects(option, object):
    return object.type == 'MESH'


def store_collection(option, context):
    bc = context.window_manager.bc

    if not bc.running:
        main = 'Cutters'
        if option.collection and option.stored_collection != option.collection and main not in option.collection.name:
            option.stored_collection = option.collection

            if option.collection and option.shape and option.shape.name not in option.collection.objects:
                option.shape = option.stored_shape if option.stored_shape and option.stored_shape.name in option.collection.objects else None

            if option.collection and not option.shape and len(option.collection.objects):
                option.shape = option.collection.objects[0]


def store_shape(option, context):
    bc = context.window_manager.bc

    if not bc.running:
        if option.shape and option.stored_shape != option.shape:
            option.stored_shape = option.shape


class option(PropertyGroup):
    running: BoolProperty()
    original_active: PointerProperty(type=Object)
    lattice: PointerProperty(type=Object)
    slice: PointerProperty(type=Object)
    inset: PointerProperty(type=Object)
    plane: PointerProperty(type=Object)
    location: FloatVectorProperty()
    mirror_axis: IntVectorProperty()
    stored_collection: PointerProperty(type=Collection)
    stored_shape: PointerProperty(type=Object)

    # TODO: break into bools
    start_operation: EnumProperty(
        name = 'Start Operation',
        description = 'Start with the previously used settings of operation',
        update = change_start_operation,
        items = [
            ('NONE', 'None', '', 'REC', 0),
            ('ARRAY', 'Array', '', 'MOD_ARRAY', 1),
            ('SOLIDIFY', 'Solidify', '', 'MOD_SOLIDIFY', 2),
            ('BEVEL', 'Bevel', '', 'MOD_BEVEL', 3),
            ('MIRROR', 'Mirror', '', 'MOD_MIRROR', 4)],
        default = 'NONE')

    collection: PointerProperty(
        name = 'Collection',
        description = 'Assign collection for shape objects',
        update = store_collection,
        type = Collection)

    shape: PointerProperty(
        name = 'Shape',
        description = 'Assign shape object',
        poll = mesh_objects,
        update = store_shape,
        type = Object)

    snap: PointerProperty(type=snap.option)
    last: PointerProperty(type=last.option)


classes = [
    object.option,
    data.option,
    snap.Points,
    snap.option,
    last.option,
    option]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.bc = PointerProperty(type=option)
    bpy.types.Object.bc = PointerProperty(type=object.option)
    bpy.types.Mesh.bc = PointerProperty(type=data.option)
    bpy.types.Lattice.bc = PointerProperty(type=data.option)


def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.WindowManager.bc
    del bpy.types.Object.bc
    del bpy.types.Mesh.bc
    del bpy.types.Lattice.bc
