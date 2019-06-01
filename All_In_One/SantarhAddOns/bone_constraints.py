import bpy
import os

class TheOthersBoneLocationConstraints(bpy.types.Operator):
    bl_idname = "pose.the_other_bone_location_constraints"
    bl_label = "The Other Bone Location Constraints"
    bl_description = "Constraints the others bone location"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = bpy.context.active_object
        target = bpy.context.active_pose_bone
        others = bpy.context.selected_pose_bones
        others.remove(target)

        for bone in others:
            c = target.constraints.new(type='COPY_LOCATION')
            c.target = armature
            c.subtarget = bone.name
            c.use_offset = True
            c.target_space = 'LOCAL'
            c.owner_space = 'LOCAL'
            c.influence = 1 / len(others)

        return {'FINISHED'}
