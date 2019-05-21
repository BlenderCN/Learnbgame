import logging
import bpy


logger = logging.getLogger(__name__)


class CreateConstraintFromAction(bpy.types.Operator):
    """Removes all the useless fcurves and groups of the active action."""

    bl_idname = "action.create_constraint"
    bl_label = "Create Action Constraints"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        action = context.object.animation_data.action
        action_exists = action is not None
        is_face_action = action.face_action
        return action_exists and is_face_action

    def execute(self, context):
        """Execute the operator."""
        action = context.object.animation_data.action

        if action.name != action.name_backup:
            # rename the constraints to the new action name
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE':
                    for bone in obj.pose.bones:
                        for constraint in bone.constraints:
                            if constraint.type == 'ACTION':
                                if constraint.name == action.name_backup:
                                    constraint.name = action.name
            action.name_backup = action.name

        for group in action.groups:  # each group corresponds to a bone
            obj = context.object
            bone = obj.pose.bones[group.name]

            if action.name in [c.name for c in bone.constraints]:
                logger.info(
                    "Action Constraint `{}` already exists on `{}`, updating its values only.".format(
                        action.name, bone.name
                    )
                )
                constraint = bone.constraints[action.name]
            else:
                logger.info("Adding action constraint on {}".format(bone))
                constraint = bone.constraints.new("ACTION")
                constraint.name = action.name

            target = bpy.data.objects[action.target]
            constraint.target = target
            if action.subtarget:
                constraint.subtarget = action.subtarget

            constraint.transform_channel = action.transform_channel
            constraint.target_space = "LOCAL"

            constraint.action = action

            constraint.frame_start = action.frame_range[0]
            constraint.frame_end = action.frame_range[1]

            constraint.min = action.activation_start
            constraint.max = action.activation_end

        return {"FINISHED"}
