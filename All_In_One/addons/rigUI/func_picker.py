import bpy

#from. insert_keyframe import insert_keyframe
from. snapping_utils import *
from .utils import get_IK_bones

try :
    from rigutils.driver_utils import split_path
    from rigutils.insert_keyframe import insert_keyframe
    from rigutils.snap_ik_fk import snap_ik_fk
    from rigutils.utils import find_mirror
except :
    print('You need to install the rigutils module in your blender modules path')

def hide_layers(args) :
    """ """
    ob = bpy.context.object

    layers=[]
    for bone in [b for b in ob.pose.bones if b.bone.select] :
        for i,l in enumerate(bone.bone.layers) :
            if l and i not in layers :
                layers.append(i)

    for i in layers :
        ob.data.layers[i] = not ob.data.layers[i]


def boolean(args) :
    """ data_path, keyable """
    ob = bpy.context.object
    data_path = args['data_path']
    keyable = args['keyable']

    #bone,prop = split_path(data_path)

    try :
        value = ob.path_resolve(data_path)
        #setattr(ob.pose.bones.get(bone),'["%s"]'%prop,not value)
        try :
            exec("ob.%s = %s"%(data_path,not value))
        except :
            exec("ob%s= %s"%(data_path,not value))

        if keyable and bpy.context.scene.tool_settings.use_keyframe_insert_auto :

            if not ob.animation_data:
                ob.animation_data_create()

            ob.keyframe_insert(data_path = data_path ,group = bone)

    except ValueError :
        print("Property don't exist")


def select_layer(args) :
    ob = bpy.context.object

    layers =[]
    for bone in [b for b in ob.pose.bones if b.bone.select] :
        bone_layers = [i for i,l in enumerate(bone.bone.layers) if l]

        for l in bone_layers :
            if l not in layers :
                layers.append(l)

    for bone in ob.pose.bones :
        bone_layers = [i for i,l in enumerate(bone.bone.layers) if l]

        if len(set(bone_layers).intersection(layers)) :
            bone.bone.select = True

def hide_bones(args) :
    ob = bpy.context.object
    selected_bone = [b for b in ob.pose.bones if b.bone.select]

    hide = [b.bone.hide for b in selected_bone if not b.bone.hide]

    visibility = True if len(hide) else False

    for bone in selected_bone :
        bone.bone.hide = visibility


def select_all(args) :
    ob = bpy.context.object
    shapes = ob.data.UI['shapes']
    bones = [s['bone'] for s in shapes if s['shape_type']=='BONE']

    for bone_name in bones :
        bone = ob.pose.bones.get(bone_name)

        if bone :
            bone.bone.select = True

def select_bones(args) :
    """bones (name list)"""
    ob = bpy.context.object
    pBones = ob.pose.bones
    bones_name =args['bones']
    event = args['event']
    if not event.shift :
        for bone in bpy.context.object.pose.bones:
            bone.bone.select = False

    bones = [pBones.get(b) for b in bones_name]

    select = False
    for bone in bones :
        if bone.bone.select == False :
            select =True
            break

    for bone in bones :
        bone.bone.select = select
    ob.data.bones.active = bones[-1].bone

def keyframe_bones(args) :
    print(args)
    event=args['event']
    bones=[]

    for bone in bpy.context.object.pose.bones :
        if not bone.name.startswith(('DEF','ORG','MCH')) and not bone.get('_unkeyable_') ==1 :
            if event.shift :
                bones.append(bone)
            elif not event.shift and bone.bone.select  :
                bones.append(bone)


    for bone in bones :
        insert_keyframe(bone)

def reset_bones(args) :
    event=args['event']
    avoid_value =args['avoid_value']

    ob = bpy.context.object

    bones=[]
    for bone in bpy.context.object.pose.bones :
        if not bone.name.startswith(('DEF','ORG','MCH')) and not bone.get('_unkeyable_') ==1 :
            if event.shift :
                bones.append(bone)
            elif not event.shift and bone.bone.select  :
                bones.append(bone)


    for bone in bones :
        if bone.rotation_mode =='QUATERNION':
            bone.rotation_quaternion = 1,0,0,0

        if bone.rotation_mode == 'AXIS_ANGLE':
            bone.rotation_axis_angle = 0,0,1,0

        else :
            bone.rotation_euler = 0,0,0

        bone.location = 0,0,0
        bone.scale = 1,1,1

        for key,value in bone.items() :
            if key not in avoid_value and type(value) in (int,float):
                if ob.data.get("DefaultValues") and ob.data.DefaultValues['bones'].get(bone.name) :

                    if key in ob.data.DefaultValues['bones'][bone.name] :
                        bone[key] = ob.data.DefaultValues['bones'][bone.name][key]

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

        if bpy.context.scene.tool_settings.use_keyframe_insert_auto :
            insert_keyframe(bone)


def flip_bones(args) :
    event=args['event']

    ob = bpy.context.object
    arm = bpy.context.object.pose.bones

    selected_bones = [bone for bone in ob.pose.bones if bone.bone.select==True ]
    mirrorActive = None

    for bone in selected_bones :
        boneName = bone.name
        mirrorBoneName= find_mirror(boneName)

        mirrorBone = ob.pose.bones.get(mirrorBoneName) if mirrorBoneName else None

        if bpy.context.active_pose_bone == bone :
            mirrorActive = mirrorBone

        #print(mirrorBone)
        if not event.shift and mirrorBone:
            bone.bone.select = False

        if mirrorBone :
            mirrorBone.bone.select = True
        if mirrorActive :
            ob.data.bones.active = mirrorActive.bone

def snap_ikfk(args):
    """ way, chain_index """

    way =args['way']
    chain_index = args['chain_index']
    #auto_switch = self.auto_switch

    ob = bpy.context.object
    armature = ob.data

    SnappingChain = armature.get('SnappingChain')

    poseBone = ob.pose.bones
    dataBone = ob.data.bones

    IKFK_chain = SnappingChain['IKFK_bones'][chain_index]
    switch_prop = IKFK_chain['switch_prop']

    FK_root = poseBone.get(IKFK_chain['FK_root'])
    FK_mid = [poseBone.get(b['name']) for b in IKFK_chain['FK_mid']]
    FK_tip = poseBone.get(IKFK_chain['FK_tip'])

    IK_last = poseBone.get(IKFK_chain['IK_last'])
    IK_tip = poseBone.get(IKFK_chain['IK_tip'])
    IK_pole = poseBone.get(IKFK_chain['IK_pole'])

    invert = IKFK_chain['invert_switch']

    ik_fk_layer = (IKFK_chain['FK_layer'],IKFK_chain['IK_layer'])


    for lock in ('lock_ik_x','lock_ik_y','lock_ik_z') :
        if getattr(IK_last,lock) :
            full_snapping = False
            break


    snap_ik_fk(ob,way,switch_prop,FK_root,FK_tip,IK_last,IK_tip,IK_pole,FK_mid,full_snapping,invert,ik_fk_layer,auto_switch=True)
