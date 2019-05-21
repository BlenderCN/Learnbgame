import bpy

class key_child_delta_location(bpy.types.Operator):
    bl_idname = "object.key_child_delta_location"
    bl_label = "Key Child Delta Location"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        randomize_obj = bpy.context.active_object

        # Read active keying set
        keying_set = bpy.context.scene.keying_sets.active

        # Set active keying set
        bpy.context.scene.keying_sets.active = bpy.context.scene.keying_sets_all['Delta Location']

        # Key delta location for each child
        if len(randomize_obj.children) > 0:
            for child in randomize_obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=child.name)
                bpy.ops.anim.keyframe_insert()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=randomize_obj.name)

        # Restore active keying set to previous settings
        bpy.context.scene.keying_sets.active = keying_set

        # Key custom properties in random_props property group
        # This is just cosmetic to improve workflow (i.e. we're just updating the UI panel)
        randomize_obj.keyframe_insert('random_props.seed_location')
        # Locate seed_location fcurve
        for curve in randomize_obj.animation_data.action.fcurves:
            if curve.data_path == 'random_props.seed_location':
                seed_curve = curve
        num_keyframes = len(seed_curve.keyframe_points)
        seed_curve.keyframe_points[num_keyframes - 1].interpolation = 'CONSTANT'
        randomize_obj.keyframe_insert('random_props.location')

        return {'FINISHED'}

class key_child_delta_rotation(bpy.types.Operator):
    bl_idname = "object.key_child_delta_rotation"
    bl_label = "Key Child Delta Rotation"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        randomize_obj = bpy.context.active_object

        # Read active keying set
        keying_set = bpy.context.scene.keying_sets.active

        # Set active keying set
        bpy.context.scene.keying_sets.active = bpy.context.scene.keying_sets_all['Delta Rotation']

        # Key delta location
        if len(randomize_obj.children) > 0:
            for child in randomize_obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=child.name)
                bpy.ops.anim.keyframe_insert()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=randomize_obj.name)

        # Restore active keying set to previous settings
        bpy.context.scene.keying_sets.active = keying_set

        # Key custom properties in random_props property group
        # This is just cosmetic to improve workflow (i.e. we're just updating the UI panel)
        randomize_obj.keyframe_insert('random_props.seed_rotation')
        # Locate seed_rotation fcurve
        for curve in randomize_obj.animation_data.action.fcurves:
            if curve.data_path == 'random_props.seed_rotation':
                seed_curve = curve
        num_keyframes = len(seed_curve.keyframe_points)
        seed_curve.keyframe_points[num_keyframes - 1].interpolation = 'CONSTANT'
        randomize_obj.keyframe_insert('random_props.rotation')

        return {'FINISHED'}

class key_child_delta_scale(bpy.types.Operator):
    bl_idname = "object.key_child_delta_scale"
    bl_label = "Key Child Delta Scale"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        randomize_obj = bpy.context.active_object

        # Read active keying set
        keying_set = bpy.context.scene.keying_sets.active

        # Set active keying set
        bpy.context.scene.keying_sets.active = bpy.context.scene.keying_sets_all['Delta Scale']

        # Key delta location
        if len(randomize_obj.children) > 0:
            for child in randomize_obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=child.name)
                bpy.ops.anim.keyframe_insert()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_name(name=randomize_obj.name)

        # Restore active keying set to previous settings
        bpy.context.scene.keying_sets.active = keying_set

        # Key custom properties in random_props property group
        # This is just cosmetic to improve workflow (i.e. we're just updating the UI panel)
        randomize_obj.keyframe_insert('random_props.seed_scale')
        # Locate seed_scale fcurve
        for curve in randomize_obj.animation_data.action.fcurves:
            if curve.data_path == 'random_props.seed_scale':
                seed_curve = curve
        num_keyframes = len(seed_curve.keyframe_points)
        seed_curve.keyframe_points[num_keyframes - 1].interpolation = 'CONSTANT'
        if randomize_obj.random_props.uniform_scale_enabled:
            randomize_obj.keyframe_insert('random_props.uniform_scale')
        else:
            randomize_obj.keyframe_insert('random_props.scale')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(key_child_delta_location)
    bpy.utils.register_class(key_child_delta_rotation)
    bpy.utils.register_class(key_child_delta_scale)

def unregister():
    bpy.utils.unregister_class(key_child_delta_location)
    bpy.utils.unregister_class(key_child_delta_rotation)
    bpy.utils.unregister_class(key_child_delta_scale)
