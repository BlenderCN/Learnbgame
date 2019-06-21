import bpy

class SpaceSwitchSettings(bpy.types.PropertyGroup) :
    def update_space(self,context) :
        rig = context.object
        bone = context.active_pose_bone
        space_switch_bone = bone.parent

        world_mat = bone.matrix.copy()

        bone["space"] = [c.name for c in space_switch_bone.constraints].index(self.space)
        rig.update_tag({'OBJECT'})
        bpy.context.scene.update()

        bone.matrix = world_mat

        if context.scene.tool_settings.use_keyframe_insert_auto :
            context.object.keyframe_insert('pose.bones["%s"]["space"]'%bone.name)
            if bone.rotation_mode == 'QUATERNION' :
                mode = 'rotation_quaternion'
            elif bone.rotation_mode == 'AXIS_ANGLE' :
                mode = 'rotation_axis_angle'
            else :
                mode = 'rotation_euler'
            context.object.keyframe_insert('pose.bones["%s"].location'%(bone.name))
            context.object.keyframe_insert('pose.bones["%s"].%s'%(bone.name,mode))
            context.object.keyframe_insert('pose.bones["%s"].scale'%(bone.name))

    def items_space(self,context):
        items = []
        bone = context.active_pose_bone

        space_switch_bone = bone.parent

        for constraint in space_switch_bone.constraints :
            items.append((constraint.name,constraint.name,''))

        return items

    name = bpy.props.StringProperty()
    space = bpy.props.EnumProperty(items = items_space,update= update_space)



class IKFKSettings(bpy.types.PropertyGroup) :
    bone = bpy.props.CollectionProperty(type = bpy.types.PropertyGroup)

    expand = bpy.props.BoolProperty()

    FK_root = bpy.props.StringProperty()
    FK_mid = bpy.props.CollectionProperty(type = bpy.types.PropertyGroup)
    FK_tip = bpy.props.StringProperty()

    IK_last = bpy.props.StringProperty()
    #IK_mid = bpy.props.CollectionProperty(type = bpy.types.PropertyGroup)
    IK_tip = bpy.props.StringProperty()
    IK_pole = bpy.props.StringProperty()



    FK_layer = bpy.props.IntProperty()
    IK_layer = bpy.props.IntProperty()

    #layer_switch = bpy.props.IntProperty(update=layer_switch,min=0,max = 1,options={'ANIMATABLE','LIBRARY_EDITABLE'})

    switch_prop = bpy.props.StringProperty()

    invert_switch = bpy.props.BoolProperty(default = False,description='Invert the switch property')

    extra_settings = bpy.props.BoolProperty()

    pin_elbow = bpy.props.StringProperty()
    target_elbow = bpy.props.StringProperty()

    IK_stretch_last = bpy.props.StringProperty()

    full_snapping = bpy.props.BoolProperty()

class SnappingChainSettings(bpy.types.PropertyGroup) :
    IKFK_bones = bpy.props.CollectionProperty(type = IKFKSettings)
    space_switch_Bones = bpy.props.CollectionProperty(type = SpaceSwitchSettings)

    items = [
    ("IKFK", "IKFK", ""),
    ("SPACE_SWITCH", "Space Switch", "",)
    ]

    snap_type = bpy.props.EnumProperty(items = items)

class SnappingChainPrefs(bpy.types.PropertyGroup) :
    IK_option = bpy.props.BoolProperty()
