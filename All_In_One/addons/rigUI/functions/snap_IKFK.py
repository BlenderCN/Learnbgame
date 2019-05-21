import bpy
from mathutils import Vector,Matrix

def snap_IKFK(limb,way):
    print(limb,way)

    ob = bpy.context.object
    poseBone = ob.pose.bones
    dataBone = ob.data.bones

    if limb.endswith('.R') :
        side ='.R'
    elif limb.endswith('.L') :
        side ='.L'

    if limb.startswith('leg') :

        FK_root = poseBone['thigh.fk'+side]
        FK_mid = poseBone['shin.fk'+side]
        FK_tip = poseBone['foot.fk'+side]

        IK_root = poseBone['MCH-thigh.ik'+side]
        IK_mid = poseBone['MCH-shin.ik'+side]
        IK_tip = poseBone['foot.ik'+side]
        IK_pole = poseBone['knee_target.ik'+side]

    elif limb.startswith('arm'):
        FK_root = poseBone['upper_arm.fk'+side]
        FK_mid = poseBone['forearm.fk'+side]
        FK_tip = poseBone['hand.fk'+side]

        IK_root = poseBone['MCH-upper_arm.ik'+side]
        IK_mid = poseBone['MCH-forearm.ik'+side]
        IK_tip = poseBone['hand.ik'+side]
        IK_pole = poseBone['elbow_target.ik'+side]

    #######FK2IK
    if way == 'to_FK' :
        FK_root.matrix = IK_root.matrix
        bpy.context.scene.update()
        FK_mid.matrix = IK_mid.matrix
        bpy.context.scene.update()
        FK_tip.matrix = IK_tip.matrix
        bpy.context.scene.update()
        FK_root.location = [0,0,0]
        FK_mid.location = [0,0,0]
        FK_tip.location =[0,0,0]

        if FK_root.get('stretch_length'):
            FK_root['stretch_length'] = IK_mid.length/IK_mid.bone.length


    #######IK2FK
    elif way == 'to_IK' :
        poseHead,dataHead = FK_root.head,FK_root.bone.matrix_local.to_translation()
        poseTail,dataTail = FK_mid.tail,FK_tip.bone.matrix_local.to_translation()
        poseJoint,dataJoint = FK_mid.head,FK_mid.bone.matrix_local.to_translation()
        poseMiddle,dataMiddle = (poseHead+poseTail)/2,(dataHead+dataTail)/2
        dataPole = IK_pole.bone.matrix_local.to_translation()

        rest_distance = Vector(dataJoint-dataPole).length
        #distanceFactor = rest_distance/Vector(poseJoint-poseMiddle).length

        IK_tip.matrix = FK_tip.matrix

        IK_pole.matrix = Matrix.Translation(Vector(poseJoint-poseMiddle).normalized()*rest_distance+poseJoint)
