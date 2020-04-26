import bpy

from .functions import match_bones,bind_bones,update_rig
from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty


class BindBones(bpy.types.Operator):
    bl_idname = "bonematch.bind_bones"
    bl_label = "Bind bones to metarig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.object
        metarig = context.scene.BoneMatch.metarig

        bind_bones(rig,metarig)

        return {'FINISHED'}

class MatchBones(bpy.types.Operator):
    bl_idname = "bonematch.match_bones"
    bl_label = "Match bones to metarig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.object
        metarig = context.scene.BoneMatch.metarig

        match_bones(rig,metarig)

        return {'FINISHED'}

class UpdateRig(bpy.types.Operator):
    bl_idname = "bonematch.update_rig"
    bl_label = "Update rig "
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = context.object
        autorig = context.scene.BoneMatch.autorig
        metarig = context.scene.BoneMatch.metarig

        update_rig(rig,autorig,metarig)

        return {'FINISHED'}
