import bpy
import os

C = bpy.context
D = bpy.data

def apply_pose(pose_index,blend,left,right,C):
    if C.object and C.object.type=='ARMATURE' and C.object.mode == 'POSE':
        poselib =  bpy.data.actions.get(C.object.PoseLibCustom.poseLibs)

        if poselib:

            fcurves = [fcurve for fcurve in poselib.fcurves if not fcurve.data_path.endswith(('.L"]','.R"]'))]
            if left :
                fcurves += [fcurve for fcurve in poselib.fcurves if fcurve.data_path.endswith('.L"]')]
            if right :
                fcurves += [fcurve for fcurve in poselib.fcurves if fcurve.data_path.endswith('.R"]')]

            for fcurve in fcurves:
                array_index = fcurve.array_index
                channel = fcurve.data_path

                try:
                    dstChannel = eval('bpy.context.object.%s[%d]'%(channel,array_index))
                    dstChannelStr = "bpy.context.object.%s[%d]"%(channel,array_index)
                except TypeError:
                    dstChannel = eval('bpy.context.object.%s'%channel)
                    dstChannelStr = "bpy.context.object.%s"%channel
                    boneStr = "bpy.context.object.%s"%channel
                except:
                    dstChannel = None
                    dstChannelStr = None
                    boneStr = None

                if dstChannelStr:
                    bone = channel.split('"')[1].split("'")[0]

                    group = fcurve.group
                    if not fcurve.group :
                        group = C.object.animation_data.action.groups.new(bone)
                        fcurve.group = group

                    #select = checkSelected(C,C.object)

                    '''
                    if not select:
                        select = C.object.pose.bones
                    if (not select) or group in select:
                    '''

                    if len(bpy.context.selected_pose_bones)==0 :
                        select = [bone.name for bone in bpy.context.object.pose.bones]

                    else :
                        select = [bone.name for bone in bpy.context.selected_pose_bones]

                    #print('toto',C.object.pose.bones.get(bone))
                    #print(select)
                    #print(bone)
                    if bone in select :

                        if type(dstChannel) == type(1):
                            exec('%s = int(dstChannel+(fcurve.evaluate(pose_index)-dstChannel)*blend)'%dstChannelStr)
                        else:
                            exec('%s = dstChannel+(fcurve.evaluate(pose_index)-dstChannel)*blend'%dstChannelStr)
                        #  KEYFRAME CREATION
                        if C.scene.tool_settings.use_keyframe_insert_auto:
                            if not C.object.animation_data:
                                C.object.animation_data_create()

                            try:
                                C.object.keyframe_insert(data_path=channel,index=array_index,group=group.name)
                            except TypeError:
                                C.object.keyframe_insert(data_path=channel,group=group.name)

    #TO DO refresh for character not in group
    #for group in C.object.users_group :
    if C.object.proxy_group :
        for ob in C.object.proxy_group.dupli_group.objects :
            if ob.type == 'MESH' :
                ob.data.update()

    #C.scene.frame_set(C.scene.frame_current-1)
    #C.scene.frame_set(C.scene.frame_current+1)

def main():
    apply_pose(1,1,C)

if __name__ == '__main__':
    main()
