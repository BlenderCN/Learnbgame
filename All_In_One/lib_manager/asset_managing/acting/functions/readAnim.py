import bpy
import os

from . storeAnim import mirror_key,find_mirror

def find_fcurve_path(ob,boneId,path, array_index) :
    try :
        dstChannel = eval('ob.pose.bones["%s"].%s[%d]'%(boneId,path,array_index))
        dstChannelStr = 'ob.pose.bones["%s"].%s[%d]'%(boneId,path,array_index)
        data_path = 'pose.bones["%s"].%s'%(boneId,path)

    except SyntaxError:
        try :
            dstChannel = eval('ob.pose.bones["%s"]%s'%(boneId,path))
            dstChannelStr = 'ob.pose.bones["%s"]%s'%(boneId,path)
            data_path = 'pose.bones["%s"]%s'%(boneId,path)
        except KeyError :
            dstChannel = None
            dstChannelStr = None
            data_path = None

    except :
        try :
            dstChannel = eval('ob.pose.bones["%s"].%s'%(boneId,path))
            dstChannelStr = 'ob.pose.bones["%s"].%s'%(boneId,path)
            data_path = 'pose.bones["%s"].%s'%(boneId,path)

        except KeyError :
            dstChannel = None
            dstChannelStr = None
            data_path = None

    return dstChannel,dstChannelStr,data_path

def read_anim(action,blend,left,right,selected_only,mirror,frame_current):

    ob = bpy.context.scene.objects.active
    current_frame = frame_current

    selected_bones = [bone.name for bone in ob.pose.bones if bone.bone.select==True]

    if not len(selected_bones) or not selected_only:
        selected_bones =[bone.name for bone in ob.pose.bones]

    exclude_suffixe = []
    if not left :
        exclude_suffixe.append('.L')
    if not right :
        exclude_suffixe.append('.R')

    exclude_suffixe = tuple(exclude_suffixe)

    for fcurve,value in action.items():
        if mirror :
            mirrored_fcurve = find_mirror(fcurve)
            if find_mirror(fcurve) :
                fcurve = mirrored_fcurve

        bone = ob.pose.bones.get(fcurve)
        if bone :
            for path,channel in value.items() :
                exclude_fc = False
                if path.endswith(exclude_suffixe) or fcurve.endswith(exclude_suffixe) or fcurve not in selected_bones:
                    print(fcurve)
                    exclude_fc = True

                if mirror :
                    mirrored_path = find_mirror(path)
                    if mirrored_path :
                        path = mirrored_path


                for array_index,attributes in channel.items() :

                    correct_path = find_fcurve_path(ob,fcurve,path, array_index)
                    dstChannel = correct_path[0]
                    dstChannelStr = correct_path[1]
                    data_path = correct_path[2]


                    for keysetting in attributes :
                        if mirror  :
                            if len(keysetting)<3 :
                                keysetting = mirror_key(path,array_index,keysetting,True)
                            else :
                                keysetting = mirror_key(path,array_index,keysetting,False)

                        dict = {
                            'interpolation' :       keysetting[0],
                            'type' :                keysetting[2],
                                }

                        if len(keysetting)<3 :
                            dict['handle_left']=        [keysetting[3][0]+current_frame,keysetting[3][1]]
                            dict['handle_left_type']=   keysetting[4]
                            dict['handle_right']=       [keysetting[5][0]+current_frame,keysetting[5][1]]
                            dict['handle_right_type']=  keysetting[6]
                            dict['easing']=             keysetting[7]
                            dict['back']=               keysetting[8]
                            dict['amplitude']=          keysetting[9]
                            dict['period']=             keysetting[10]

                        if exclude_fc :
                            newValue = keysetting[1][2]
                        else :
                            newValue = keysetting[1][2]+(keysetting[1][1]-keysetting[1][2])*blend


                        if dstChannelStr:
                            #  KEYFRAME CREATION
                            if not exclude_fc :
                                if not ob.animation_data:
                                    ob.animation_data_create()

                                if not ob.animation_data.action :
                                    action = bpy.data.actions.new(ob.name)
                                    ob.animation_data.action = action

                                fcurves = ob.animation_data.action.fcurves

                                fc = fcurves.find(data_path,array_index)

                                if not fc :
                                    group = ob.animation_data.action.groups.get(fcurve)
                                    fc = fcurves.new(data_path,array_index,fcurve)

                                if not fc.group and fcurve not in ob.animation_data.action.groups.keys():
                                    group = ob.animation_data.action.groups.new(fcurve)
                                    fc.group = group
                                #print(attributes['co'][0])

                                keyframe = fc.keyframe_points.insert(frame=float(keysetting[1][0])+current_frame, value=newValue)

                                for key in dict :
                                    exec('keyframe.%s = dict[key]'%(key))


                            #newValue = keysetting[1][1]

                            if type(dstChannel) == int:
                                exec('%s = %s'%(dstChannelStr,int(newValue)))
                            else :
                                exec('%s = %s'%(dstChannelStr,float(newValue)))

    if ob.proxy_group :
        for o in ob.proxy_group.dupli_group.objects :
            if o.type == 'MESH' :
                o.data.update()
