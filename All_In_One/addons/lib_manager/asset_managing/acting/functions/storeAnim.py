import bpy
import os
import re
import copy

def find_mirror(name) :
    mirror = None
    prop= False
    if name.startswith('[')and name.endswith(']'):
        prop = True
        name= name[:-2][2:]

    match={
    'R' : 'L',
    'r' : 'l',
    'L' : 'R',
    'l' : 'r',
    }

    separator=['.','_']

    if name.startswith(tuple(match.keys())):
        if name[1] in separator :
            mirror = match[name[0]]+name[1:]

    if name.endswith(tuple(match.keys())):
        if name[-2] in separator :
            mirror = name[:-1]+match[name[-1]]

    if mirror and prop == True:
        mirror='["%s"]'%mirror

    return mirror


def mirror_key(prop,index,attributes,bezier) :
    mirror_attributes=copy.deepcopy(attributes)
    mirror =False

    if prop in ['rotation_euler']:
        if index in [1,2] :
            mirror = True

    elif prop in ['rotation_quaternion','rotation_axis_angle']:
        if index in [2,3] :
            mirror = True

    elif prop in['location'] :
        if index in [0] :
            mirror = True

    if mirror :
        mirror_attributes[1][1] = -attributes[1][1] #value

        if bezier :
            mirror_attributes[3][1] = -attributes[1][1]+(-attributes[1][1]-attributes[3][1])#handle_left y
            mirror_attributes[5][1] = -attributes[1][1]+(-attributes[1][1]-attributes[5][1])#handle_right y

    return mirror_attributes

def store_anim(start,end,only_selected,bezier,mirror) :
    Fcurves={}

    ob = bpy.context.scene.objects.active
    actionFcurves = ob.animation_data.action.fcurves

    if only_selected :
        fcurves =[]
        for fc in actionFcurves :
            if fc.is_valid :
                bone = ob.pose.bones.get(fc.data_path.split('"')[1])
                if bone and bone.bone.select == True:
                    fcurves.append(fc)

        #fcurves = [fc for fc in actionFcurves if fc.is_valid and ob.pose.bones.get(fc.data_path.split('"')[1]).bone.select==True]
    else :
        fcurves = [fc for fc in actionFcurves]

    for fc in fcurves :

        boneId = fc.data_path.split('"')[1]

        mirror_boneId = find_mirror(boneId)
        #print(boneId,mirror_boneId)

        if fc.data_path.endswith(']') :
            prop = fc.data_path.replace('pose.bones["%s"]'%(boneId),"")
        else :
            prop = fc.data_path.replace('pose.bones["%s"].'%(boneId),"")

        mirror_prop = find_mirror(prop)
        print(prop,mirror_prop)

        keyframe_attribute = []
        for keyframe in fc.keyframe_points :
            if keyframe.co[0] in range(start,end+1) :

                if not Fcurves.get(boneId) :
                    Fcurves[boneId]={}

                if not Fcurves[boneId].get(prop) :
                    Fcurves[boneId][prop] = {}

                if not Fcurves[boneId][prop].get(fc.array_index) :
                    Fcurves[boneId][prop][fc.array_index] = []


                keyframe_attribute = [
                    keyframe.interpolation,
                    [keyframe.co[0]-start,round(keyframe.co[1],8)],
                    keyframe.type,
                    ]

                if bezier == True :
                    keyframe_attribute+=[

                    [round(keyframe.handle_left[0],5),round(keyframe.handle_left[1],5)],
                    keyframe.handle_left_type,
                    [round(keyframe.handle_right[0],5),round(keyframe.handle_right[1],5)],
                    keyframe.handle_right_type,
                    keyframe.easing,
                    round(keyframe.back,5),
                    round(keyframe.amplitude,5),
                    round(keyframe.period,5),
                    ]

            if keyframe_attribute :
                Fcurves[boneId][prop][fc.array_index].append(keyframe_attribute)

                if mirror :
                    mirror_attribute = keyframe_attribute.copy()

                    if mirror_boneId and not mirror_prop :
                        if not Fcurves.get(mirror_boneId) :
                            Fcurves[mirror_boneId]={}

                        if not Fcurves[mirror_boneId].get(prop) :
                            Fcurves[mirror_boneId][prop] = {}

                        if not Fcurves[mirror_boneId][prop].get(fc.array_index) :
                            Fcurves[mirror_boneId][prop][fc.array_index] = []


                        Fcurves[mirror_boneId][prop][fc.array_index].append(mirror_key(prop,fc.array_index,mirror_attribute,bezier))

                    elif mirror_prop and not mirror_boneId:
                        if not Fcurves[boneId].get(mirror_prop) :
                            Fcurves[boneId][mirror_prop] = {}

                        if not Fcurves[boneId][mirror_prop].get(fc.array_index) :
                            Fcurves[boneId][mirror_prop][fc.array_index] = []

                        Fcurves[boneId][mirror_prop][fc.array_index].append(mirror_attribute)

                    elif mirror_boneId and mirror_prop:
                        if not Fcurves.get(mirror_boneId) :
                            Fcurves[mirror_boneId]={}

                        if not Fcurves[mirror_boneId].get(mirror_prop) :
                            Fcurves[mirror_boneId][mirror_prop] = {}

                        if not Fcurves[mirror_boneId][mirror_prop].get(fc.array_index) :
                            Fcurves[mirror_boneId][mirror_prop][fc.array_index] = []

                        Fcurves[mirror_boneId][mirror_prop][fc.array_index].append(mirror_key(prop,fc.array_index,mirror_attribute,bezier))

    return Fcurves

def write_anim(path,name,action):

    if not os.path.exists(path):
        os.makedirs(path)

    file = open(os.path.join(path,name+'_action.txt'),'w')   # Trying to create a new file or open one

    for key,value in action.items() :
        file.write(str(key)+'=')
        file.write(str(value)+'\n')

    file.close()
