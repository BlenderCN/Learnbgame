import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import PropertyGroup
from bpy.props import *

from . utility import addon


class option(PropertyGroup):
    running: BoolProperty()


class object(PropertyGroup):
    shape: BoolProperty()
    slice: BoolProperty()
    applied: BoolProperty()


class data(PropertyGroup):
    removeable: BoolProperty()
    q_beveled: BoolProperty()


classes = [
    option,
    object,
    data]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.bc = PointerProperty(type=option)
    addon.log(value=F'Added window manager pointer property')

    bpy.types.Object.bc = PointerProperty(type=object)
    addon.log(value=F'Added object pointer property')

    bpy.types.Mesh.bc = PointerProperty(type=data)
    addon.log(value=F'Added mesh data pointer property')

    bpy.types.Lattice.bc = PointerProperty(type=data)
    addon.log(value=F'Added lattice data pointer property')


def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.WindowManager.bc
    addon.log(value=F'Removed window manager pointer property')

    del bpy.types.Object.bc
    addon.log(value=F'Removed object pointer property')

    del bpy.types.Mesh.bc
    addon.log(value=F'Removed mesh data pointer property')

    del bpy.types.Lattice.bc
    addon.log(value=F'Added lattice data pointer property')
