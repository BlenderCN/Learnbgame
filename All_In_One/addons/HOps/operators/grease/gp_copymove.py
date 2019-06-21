import bpy

from mathutils import Vector

from bpy.types import Operator
from bpy.props import FloatProperty


class HOPS_OT_GPCopyMove(Operator):
    bl_idname = 'hops.copy_move'
    bl_label = 'GP Copy / Move'
    bl_description = 'Copy and move grease pencil object'
    bl_options = {'REGISTER', 'UNDO'}

    value_x: FloatProperty(
        name = 'X Value',
        description = 'Amount along the X axis',
        default = 3.0)

    value_y: FloatProperty(
        name = 'Y Value',
        description = 'Amount along the Y axis',
        default = 0.0)


    def execute(self, context):
        object = bpy.context.active_object
        collections = object.users_collection[:]

        new = object.copy()
        new.data = object.data.copy()
        for collection in collections:
            collection.objects.link(new)

        new.location = Vector((
            new.location.x + self.value_x,
            new.location.y + self.value_y,
            new.location.z))

        context.view_layer.objects.active = new

        return {'FINISHED'}
