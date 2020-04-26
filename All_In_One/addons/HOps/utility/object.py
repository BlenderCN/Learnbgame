import bpy
from mathutils import Vector

from . import addon, math


def duplicate(obj, name='', link=False):
    duplicate = obj.copy()
    duplicate.data = obj.data.copy()

    if name:
        duplicate.name = name
        duplicate.data.name = name

    addon.log(value=F'Duplicated {obj.name} as: {duplicate.name}', indent=2)

    if link:
        bpy.context.scene.collection.objects.link(duplicate)
        addon.log(value=F'Linked {duplicate.name} to the scene', indent=2)

    return duplicate