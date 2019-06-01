import logging
import bpy


logger = logging.getLogger(__name__)


class DeleteUselessActionConstraints(bpy.types.Operator):
    """Remove all the action constraints named like the active action that exist on an object that isn't influenced by the action."""

    bl_idname = "action.delete_useles_constraints"
    bl_label = "Delete Useless Action Constraints"
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
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                for bone in obj.pose.bones:
                    for constraint in bone.constraints:
                        if constraint.type == 'ACTION':
                            if action.name == constraint.name and bone.name not in action.groups:
                                logger.info("Removing Constraint `{}` on bone `{}`".format(constraint.name, bone.name))
                                bone.constraints.remove(constraint)

                

        return {"FINISHED"}
