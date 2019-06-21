import bpy
from mathutils import Vector

from . import addon, math


def duplicate(obj, name='', link=False):
    duplicate = obj.copy()
    duplicate.data = obj.data.copy()

    if name:
        duplicate.name = name
        duplicate.data.name = name

    if link:
        bpy.context.scene.collection.objects.link(duplicate)

    return duplicate


def center(obj):
    return 0.125 * math.vector_sum((Vector(bound) for bound in obj.bound_box))
