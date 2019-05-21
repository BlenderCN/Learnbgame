import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty, IntProperty

class SpeckleSceneObject(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="")

class SpeckleStreamObject(bpy.types.PropertyGroup):
    name = StringProperty(default="SpeckleStream")
    streamId = StringProperty(default="")
    units = StringProperty(default="Meters")

class SpeckleUserAccountObject(bpy.types.PropertyGroup):
    name = StringProperty(default="SpeckleUser")
    email = StringProperty(default="John Doe")
    authToken = StringProperty(default="")
    server = StringProperty(default="")
    streams = CollectionProperty(type=SpeckleStreamObject)
    active_stream = IntProperty(default=0)

class SpeckleSceneSettings(bpy.types.PropertyGroup):
    streams = bpy.props.EnumProperty(
        name="Available streams",
        description="Available streams associated with account.",
        items=[],
        )

    accounts = CollectionProperty(type=SpeckleUserAccountObject)
    active_account = IntProperty(default=0)
    objects = CollectionProperty(type=SpeckleSceneObject)
    scale = FloatProperty(default=0.001)
    user = StringProperty(
    	name="User",
    	description="Current user.",
    	default="Speckle User",
    	)
