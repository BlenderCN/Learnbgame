import bpy
import logging


logger = logging.getLogger(__name__)


def remove_flat_curves(action):
    """Remove the fcurves where the keyframes all have the same value."""
    logger.info("Removing flat curves of action {}.".format(action.name))
    for fcurve in action.fcurves:
        points = fcurve.keyframe_points
        value = None
        is_flat_curve = True
        for point in points:
            coordinates = point.co
            if value is None:
                value = coordinates[1]
            else:
                if coordinates[1] != value:
                    is_flat_curve = False
                    break
        if is_flat_curve:
            logger.debug("Removing curve {} ".format(fcurve.data_path))
            action.fcurves.remove(fcurve)


def remove_empty_groups(action):
    """Remove the groups that have no channels."""
    logger.info("Removing empty groups of action {}.".format(action.name))
    for group in action.groups:
        if len(group.channels) == 0:
            logger.debug("Removing group {}.".format(group.name))
            action.groups.remove(group)


class CleanAction(bpy.types.Operator):
    """Removes all the useless fcurves and groups of the active action."""
    bl_idname = "action.clean"
    bl_label = "Clean Action"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Make sure there's an active action."""
        return context.object.animation_data.action is not None

    def execute(self, context):
        """Execute the operator."""
        action = context.object.animation_data.action
        remove_flat_curves(action)
        remove_empty_groups(action)
        return {'FINISHED'}
