import bpy
import os

class MirrorBoneConstraints(bpy.types.Operator):
    bl_idname = "pose.mirror_bone_constraints"
    bl_label = "Mirror Bone Constraints"
    bl_description = "Mirror bone constraints with replacing bone .L to .R"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def deselect_all_pose_bone(rig_object):
            for b in rig_object.pose.bones:
                b.bone.select = False

        def replace_name_right_to_left(name):
            return name.replace('R', 'L')

        rig = bpy.context.active_object
        targets = bpy.context.selected_pose_bones
        targets_mirror = list(map(lambda x: rig.pose.bones[x.name.replace('R', 'L')], targets))

        for (target, src) in zip(targets, targets_mirror):
            deselect_all_pose_bone(bpy.context.active_object)
            target.bone.select = True
            src.bone.select = True
            rig.data.bones.active = src.bone
            if len(src.constraints) > 0:
                bpy.ops.pose.constraints_copy()
                for c in target.constraints:
                    c.subtarget = c.subtarget.replace('L', 'R')

        deselect_all_pose_bone(bpy.context.active_object)

        return {'FINISHED'}
