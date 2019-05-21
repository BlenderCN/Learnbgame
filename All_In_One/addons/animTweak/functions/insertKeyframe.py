import bpy

AvoidValue =[
'pose.bones["hand.ik.L"]["ikfk_switch"]',
'pose.bones["hand.ik.R"]["ikfk_switch"]',
'pose.bones["foot.ik.L"]["ikfk_switch"]',
'pose.bones["foot.ik.R"]["ikfk_switch"]',
]

def insert_keyframe(bone):
    Transforms ={"location":("lock_location[0]","lock_location[1]","lock_location[2]"),
        "scale":("lock_scale[0]","lock_scale[1]","lock_scale[2]")}

    if bone.rotation_mode in 'QUATERNION':
        Transforms["rotation_quaternion"] = ("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]","lock_rotation_w")

    elif bone.rotation_mode == 'AXIS_ANGLE':
        Transforms["rotation_axis_angle"] = ("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]","lock_rotation_w")

    else :
        Transforms["rotation_euler"]=("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]")

    ob = bpy.context.active_object
    interpolation = bpy.context.user_preferences.edit.keyframe_new_interpolation_type

    if not ob.animation_data:
        ob.animation_data_create()

    for prop,lock in Transforms.items() :
        for index,channel in enumerate(lock) :
            #if the channel is not locked
            if not eval("bone."+channel) :
                bone.keyframe_insert(data_path = prop, index=index,group = bone.name)
                fcurve = bpy.context.object.animation_data.action.fcurves.find('pose.bones["%s"].%s'%(bone.name,prop))
                if fcurve :
                    for key in fcurve.keyframe_points :
                        if key.co[0] == bpy.context.scene.frame_current :
                            key.interpolation = interpolation

        for key,value in bone.items() :
            if key != '_RNA_UI' and key not in AvoidValue :
                bone.keyframe_insert(data_path='["%s"]'%key,group = bone.name)
                fcurve = ob.animation_data.action.fcurves.find('pose.bones["%s"]["%s"]'%(bone.name,key))
                if fcurve :
                    for key in fcurve.keyframe_points :
                        if key.co[0] == bpy.context.scene.frame_current :
                            key.interpolation = interpolation
