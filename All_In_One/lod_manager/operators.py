__reload_order_index__ = 1

import bpy
from .handlers import update_objects_lod
from .utils.copy import copy_properties


class GROUP_OT_add_lod(bpy.types.Operator):
    """Add a new Level Of Detail"""
    bl_idname = "group.lod_add"
    bl_label = "Add Level"

    @classmethod
    def poll(cls, context):
        return context.scene.lod_group in bpy.data.groups

    def execute(self, context):
        group = bpy.data.groups[context.scene.lod_group]
        group.lod.add()

        if len(group.lod) > 1:
            group.lod[-1].distance = group.lod[-2].distance + 1

        return {'FINISHED'}


class GROUP_OT_remove_lod(bpy.types.Operator):
    """Remove this Level"""
    bl_idname = "group.lod_remove"
    bl_label = "Remove Level"

    index = bpy.props.IntProperty(default=0)

    @classmethod
    def poll(cls, context):
        return context.scene.lod_group in bpy.data.groups

    def execute(self, context):
        group = bpy.data.groups[context.scene.lod_group]
        group.lod.remove(self.index)
        return {'FINISHED'}


class OBJECT_OT_lod_update(bpy.types.Operator):
    """Update Objects"""
    bl_idname = "object.lod_update"
    bl_label = "Update Objects"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        update_objects_lod(context.scene, event='viewport')
        return {'FINISHED'}


class OBJECT_OT_lod_copy(bpy.types.Operator):
    """Copy the LOD Object settings from the active object to all selected objects"""
    bl_idname = "object.lod_copy"
    bl_label = "Copy From Active To Selected"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object.type == 'MESH'

    def execute(self, context):
        active_object = context.active_object

        for obj in context.selected_objects:
            if obj != active_object and obj.type == 'MESH':
                copy_properties(active_object.lod, obj.lod)

        return {'FINISHED'}


def register():
    pass


def unregister():
    pass
