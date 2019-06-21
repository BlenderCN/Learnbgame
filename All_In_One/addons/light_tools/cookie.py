import bpy
from bpy.props import BoolProperty, FloatProperty


class ObjectsCreationControls(bpy.types.PropertyGroup):

    UseCookie = bpy.props.BoolProperty(
        description="Enable use of cookie",
        default=False)


class AddCookie(bpy.types.Operator):
    mesh = bpy.ops.mesh

    mesh.primitive_plane_add()
    bpy.context.object.name = "Cookie"
    bpy.context.object.parent = bpy.data.objects["Spot"]
