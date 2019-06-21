import bpy

def refresh_poseLib():
    poseLibs = [action.name for action in bpy.data.actions if len(action.pose_markers)>0]
    sortedItems=[]

    if bpy.context.object.PoseLibCustom.filtered == True :
        #baseName of the rig to match with the action name
        idName = bpy.context.object.name.split('_')[0]
        poseLibs = [p for p in poseLib if p.split('_')[0] == idName]

        for poseLib in sorted(poseLibs):
            sortedItems.append((poseLib,poseLib,""))

    else :
        for poseLib in sorted(poseLibs):
            sortedItems.append((poseLib,poseLib,""))

    bpy.types.Object.




def filterPoseLib():
