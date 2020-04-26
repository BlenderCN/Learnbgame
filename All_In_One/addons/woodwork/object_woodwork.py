import bpy.types
import bpy.utils
from bpy.props import (
    StringProperty
)

class ObjectWoodworkProperties(bpy.types.PropertyGroup):
    cutting_list_type = StringProperty()
    comments = StringProperty()


def register():
    bpy.utils.register_class(ObjectWoodworkProperties)
    bpy.types.Object.woodwork = bpy.props.PointerProperty(
        type=ObjectWoodworkProperties)


def unregister():
    del bpy.types.Object.woodwork
    bpy.utils.unregister_class(ObjectWoodworkProperties)