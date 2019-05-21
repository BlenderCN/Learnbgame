import bpy

class delete_child_delta_location(bpy.types.Operator):
    bl_idname = "object.delete_child_delta_location"
    bl_label = "Delete Child Delta Location"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        randomize_obj = bpy.context.active_object

        # Read active keying set
        keying_set = bpy.context.scene.keying_sets.active

        # Set active keying set
        bpy.context.scene.keying_sets.active = bpy.context.scene.keying_sets_all['Delta Location']

        # Delete delta location key for each child
        if len(randomize_obj.children) > 0:
            for child in randomize_obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=child.name)
                bpy.ops.anim.keyframe_delete()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=randomize_obj.name)

        # Restore active keying set to previous settings
        bpy.context.scene.keying_sets.active = keying_set

        # Delete custom property keys in random_props property group
        # This is just cosmetic to improve workflow (i.e. we're just updating the UI panel)
        randomize_obj.keyframe_delete('random_props.seed_location')
        randomize_obj.keyframe_delete('random_props.location')

        return {'FINISHED'}

class delete_child_delta_rotation(bpy.types.Operator):
    bl_idname = "object.delete_child_delta_rotation"
    bl_label = "Delete Child Delta Rotation"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        randomize_obj = bpy.context.active_object

        # Read active keying set
        keying_set = bpy.context.scene.keying_sets.active

        # Set active keying set
        bpy.context.scene.keying_sets.active = bpy.context.scene.keying_sets_all['Delta Rotation']

        # Delete delta rotation key for each child
        if len(randomize_obj.children) > 0:
            for child in randomize_obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=child.name)
                bpy.ops.anim.keyframe_delete()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=randomize_obj.name)

        # Restore active keying set to previous settings
        bpy.context.scene.keying_sets.active = keying_set

        # Delete custom property keys in random_props property group
        # This is just cosmetic to improve workflow (i.e. we're just updating the UI panel)
        randomize_obj.keyframe_delete('random_props.seed_rotation')
        randomize_obj.keyframe_delete('random_props.rotation')

        return {'FINISHED'}

class delete_child_delta_scale(bpy.types.Operator):
    bl_idname = "object.delete_child_delta_scale"
    bl_label = "Delete Child Delta Scale"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        randomize_obj = bpy.context.active_object

        # Read active keying set
        keying_set = bpy.context.scene.keying_sets.active

        # Set active keying set
        bpy.context.scene.keying_sets.active = bpy.context.scene.keying_sets_all['Delta Scale']

        # Delete delta location keys for each child
        if len(randomize_obj.children) > 0:
            for child in randomize_obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=child.name)
                bpy.ops.anim.keyframe_delete()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=randomize_obj.name)

        # Restore active keying set to previous settings
        bpy.context.scene.keying_sets.active = keying_set

        # Delete custom property keys in random_props property group
        # This is just cosmetic to improve workflow (i.e. we're just updating the UI panel)
        randomize_obj.keyframe_delete('random_props.seed_scale')
        if randomize_obj.random_props.uniform_scale_enabled:
            randomize_obj.keyframe_delete('random_props.uniform_scale')
        else:
            randomize_obj.keyframe_delete('random_props.scale')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(delete_child_delta_location)
    bpy.utils.register_class(delete_child_delta_rotation)
    bpy.utils.register_class(delete_child_delta_scale)

def unregister():
    bpy.utils.unregister_class(delete_child_delta_location)
    bpy.utils.unregister_class(delete_child_delta_rotation)
    bpy.utils.unregister_class(delete_child_delta_scale)
