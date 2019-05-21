import bpy


class ExportActionData(bpy.types.Operator):
    """Operator to export the animation data of the current action into a JSON file."""

    bl_idname = "yallah.export_action_data"
    bl_label = """Export the animation data of the current action into a JSON file."""

    json_filename = bpy.props.StringProperty(name="Action JSON File",
                                             description="The json file that will hold the animation data",
                                             subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        obj = context.active_object  # type: bpy.types.Object
        if obj is not None:
            anim_data = obj.animation_data
            if anim_data is not None:
                act = anim_data.action
                if act is not None:
                    return True

        return False

    def execute(self, context):

        import json

        obj = context.active_object  # type: bpy.types.Object
        act = obj.animation_data.action
        fcurves = act.fcurves

        out_data = {}

        for fc in fcurves:  # type: bpy.types.FCurve

            print("Inserting dp {} idx {}".format(fc.data_path, fc.array_index))

            if fc.data_path not in out_data:
                index_dict = {}
                out_data[fc.data_path] = index_dict
            else:
                index_dict = out_data[fc.data_path]

            points = []
            for kfpoint in fc.keyframe_points:  # type: bpy.types.Keyframe
                points.append([kfpoint.co[0], kfpoint.co[1]])  # we save it as a 2-array, not as Vector

            index_dict[fc.array_index] = points

        with open(self.json_filename, 'w') as out_file:
            json.dump(obj=out_data, fp=out_file, indent=2)

        return {'FINISHED'}


class SetDummyUserToAllActions(bpy.types.Operator):
    """Operator to set 'F' (dummy user) to all actions."""

    bl_idname = "yallah.set_dummy_user_to_all_actions"
    bl_label = "Set 'F' (dummy user) to all actions"

    @classmethod
    def poll(cls, context):
        if not (context.mode == 'POSE' or context.mode == 'OBJECT'):
            return False

        return True

    def execute(self, context):

        import bpy

        for actions in bpy.data.actions:
            actions.use_fake_user = True

        return {'FINISHED'}


class CreateAPoseAction(bpy.types.Operator):
    """Operator to set an A-Pose animation key frame."""

    A_POSE_ACTION_NAME = "A-Pose"

    bl_idname = "yallah.create_apose_action"
    bl_label = "Creates an action called " + A_POSE_ACTION_NAME\
               + " with one keyframe at position 1 with the character reset in identity position."

    @classmethod
    def poll(cls, context):
        if not (context.mode == 'POSE' or context.mode == 'OBJECT'):
            return False

        obj = context.active_object  # type: bpy.types.Object
        if not obj.type == "ARMATURE":
            return False

        return True

    def execute(self, context):

        obj = bpy.context.active_object

        # Create the action
        if CreateAPoseAction.A_POSE_ACTION_NAME not in bpy.data.actions:
            bpy.data.actions.new(CreateAPoseAction.A_POSE_ACTION_NAME)
        if obj.animation_data is None:
            obj.animation_data_create()

        obj.animation_data.action = bpy.data.actions[CreateAPoseAction.A_POSE_ACTION_NAME]

        # Keyframe position
        bpy.context.scene.frame_set(1)

        # Object
        # Clear object position and pose.
        # bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.object.scale_clear()
        obj.keyframe_insert("location", frame=1)
        obj.keyframe_insert("rotation_euler", frame=1)
        obj.keyframe_insert("scale", frame=1)

        # Bones
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        # Insert the keyframe for the bones
        bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')

        # Be sure that the action stays in memory.
        bpy.data.actions[CreateAPoseAction.A_POSE_ACTION_NAME].use_fake_user = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ExportActionData)
    bpy.utils.register_class(SetDummyUserToAllActions)
    bpy.utils.register_class(CreateAPoseAction)


def unregister():
    bpy.utils.unregister_class(ExportActionData)
    bpy.utils.unregister_class(SetDummyUserToAllActions)
    bpy.utils.unregister_class(CreateAPoseAction)


