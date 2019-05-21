import bpy
from mathutils import Matrix
'''
def apply_mat(mat_sc,mat_dest,loc=False,rot=False,scale=False) :
    loc_sc,rot_sc,scale_sc = mat_source.decompose()
    loc_dest,rot_dest,scale_dest = mat_dest.decompose()

    matrix = mat_sc.copy()

    if loc :
        matrix =loc_dest


    if not rot :
        rot = rot_dest
    else :
        rot = rot_sc

    if not scale :
        scale = scale_dest
    else :
        scale = scale_sc



    return matrix
'''
def find_mirror(name) :
    mirror = None
    prop= False

    if name :

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

    else :
        return None


def mirror_path(dp) :
    bone = split_path(dp)[0]
    prop = split_path(dp)[1]

    mirror_bone = find_mirror(bone)

    if not mirror_bone :
        mirror_bone = bone

    if prop :
        mirror_prop = find_mirror(prop)

        if not mirror_prop :
            mirror_prop = prop

        mirror_data_path = dp.replace('["%s"]'%prop,'["%s"]'%mirror_prop)

    mirror_data_path = dp.replace('["%s"]'%bone,'["%s"]'%mirror_bone)



    if dp!= mirror_data_path :
        return mirror_data_path

    else :
        return None

def split_path(path) :
    try :
        bone_name = path.split('["')[1].split('"]')[0]

    except :
        bone_name = None

    try :
        prop_name = path.split('["')[2].split('"]')[0]
    except :
        prop_name = None

    return bone_name,prop_name

def get_IK_bones(IK_last):
    ik_chain = IK_last.parent_recursive
    ik_len = 0

    #Get IK len :
    for c in IK_last.constraints :
        if c.type == 'IK':
            ik_len = c.chain_count -2
            break

    IK_root = ik_chain[ik_len]

    IK_mid= ik_chain[:ik_len]

    IK_mid.reverse()
    IK_mid.append(IK_last)

    return IK_root,IK_mid

def bone_list(chain):
    bones = []

    names = ['FK_root','FK_tip','IK_tip','IK_pole']

    for bone in chain.FK_mid :
        bones.append(bone.name)

    for name in names :
        bones.append(chain[name])
    return bones


def insert_keyframe(bone,custom_prop=True):
    ob = bpy.context.object

    Transforms ={"location":("lock_location[0]","lock_location[1]","lock_location[2]"),
        "scale":("lock_scale[0]","lock_scale[1]","lock_scale[2]")}

    if bone.rotation_mode in 'QUATERNION':
        Transforms["rotation_quaternion"] = ("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]","lock_rotation_w")

    elif bone.rotation_mode == 'AXIS_ANGLE':
        Transforms["rotation_axis_angle"] = ("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]","lock_rotation_w")

    else :
        Transforms["rotation_euler"]=("lock_rotation[0]","lock_rotation[1]","lock_rotation[2]")

    #interpolation = bpy.context.user_preferences.edit.keyframe_new_interpolation_type

    if not ob.animation_data:
        ob.animation_data_create()

    for prop,lock in Transforms.items() :
        for index,channel in enumerate(lock) :
            #if the channel is not locked
            if not eval("bone."+channel) :
                ob.keyframe_insert(data_path = 'pose.bones["%s"].%s'%(bone.name,prop), index = index,group = bone.name)

            '''

                bone.keyframe_insert(data_path = prop, index=index,group = bone.name)
                fcurve = bpy.context.object.animation_data.action.fcurves.find('pose.bones["%s"].%s'%(bone.name,prop))
                if fcurve :
                    for key in fcurve.keyframe_points :
                        if key.co[0] == bpy.context.scene.frame_current :
                            key.interpolation = interpolation
                            '''

        if custom_prop == True :
            for key,value in bone.items() :
                if key != '_RNA_UI' and key and type(value) in (int,float):
                    ob.keyframe_insert(data_path = 'pose.bones["%s"]["%s"]'%(bone.name,key) ,group = bone.name)
                    '''
                    bone.keyframe_insert(data_path='["%s"]'%key,group = bone.name)
                    fcurve = ob.animation_data.action.fcurves.find('pose.bones["%s"]["%s"]'%(bone.name,key))
                    if fcurve :
                        for key in fcurve.keyframe_points :
                            if key.co[0] == bpy.context.scene.frame_current :
                                key.interpolation = interpolation
                                '''
