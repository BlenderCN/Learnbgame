import bpy
import os

C = bpy.context
D = bpy.data

def checkSelected(object):
    ret = ()
    for bone in object.pose.bones:
        if bone.bone.select:
            ret += (bone.name,)
    return(ret)

def apply_pose(pose_index,blend,C):
    if C.object and C.object.type=='ARMATURE' and C.object.mode == 'POSE':
        poselib =  bpy.data.actions.get(C.object.PoseLibCustom.poseLibs)

        if poselib:
            for fcurve in poselib.fcurves:
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
                    group = channel.split('"')[1].split("'")[0]
                    select = checkSelected(C.object)
                    if (not select) or group in select:

                        if type(dstChannel) == type(1):
                            exec('%s = int(dstChannel+(fcurve.evaluate(pose_index)-dstChannel)*blend)'%dstChannelStr)
                        else:
                            exec('%s = dstChannel+(fcurve.evaluate(pose_index)-dstChannel)*blend'%dstChannelStr)
                        #  KEYFRAME CREATION
                        if C.scene.tool_settings.use_keyframe_insert_auto:
                            if not C.object.animation_data:
                                C.object.animation_data_create()

                            try:
                                C.object.keyframe_insert(data_path=channel,index=array_index,group=group)
                            except TypeError:
                                C.object.keyframe_insert(data_path=channel,group=group)

    C.scene.frame_set(C.scene.frame_current-1)
    C.scene.frame_set(C.scene.frame_current+1)

def main():
    apply_pose(1,1,C)

if __name__ == '__main__':
    main()
