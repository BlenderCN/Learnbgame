from .insertKeyframe import insert_keyframe

import bpy

def reset_props(bone,insertKeyframe):
    ob = bpy.context.object

    if bone.rotation_mode =='QUATERNION':
        bone.rotation_quaternion = 1,0,0,0

    if bone.rotation_mode == 'AXIS_ANGLE':
        bone.rotation_axis_angle = 0,0,1,0

    else :
        bone.rotation_euler = 0,0,0

    bone.location = 0,0,0
    bone.scale = 1,1,1

    for key,value in bone.items() :
        if ob.data.DefaultValues.get(bone.name) :
            if key != '_RNA_UI':
                if key in ob.data.DefaultValues[bone.name] :
                    bone[key] = ob.data.DefaultValues[bone.name][key]

                else :
                    if type(value)== int :
                        bone[key]=0
                    else :
                        bone[key]=0.0
        else :
            if type(value)== int :
                bone[key]=0
            else :
                bone[key]=0.0

    if insertKeyframe == 1 :
        insert_keyframe(bone)
