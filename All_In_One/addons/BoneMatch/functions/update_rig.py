import bpy
from .utils import armature_info
from .match_bones import match_bones
from rigutils.utils import find_rig_users

def update_rig(rig,autorig,metarig):
    scene = bpy.context.scene
    ob = bpy.context.object

    autorig = scene.BoneMatch.autorig

    autorig_copy = autorig.copy()
    autorig_copy.data = autorig.data.copy()

    action = ob.animation_data.action
    name = ob.name

    ob.user_remap(autorig_copy)

    scene.objects.active = autorig_copy

    autorig.user_remap(autorig_copy)

    bpy.ops.bonematch.match_bones()

    if action :
        autorig_copy.animation_data.action = action

    autorig.name = name
    autorig.data.name = name
    #users = find_rig_users(ob)

def old_update_rig(rig,autorig,metarig):
    scene = bpy.context.scene
    #metarig_values = armature_info(metarig)
    rig_values = armature_info(rig)
    active_object = bpy.context.scene.objects.active
    mode = active_object.mode

    data_attr = ['bbone_curveinx','bbone_curveiny','bbone_curveoutx','bbone_curveouty','bbone_in',
    'bbone_out','bbone_rollin','bbone_rollout','bbone_scalein','bbone_scaleout','bbone_segments','bbone_x',
    'bbone_z','show_wire'
    ]

    pose_attr =['custom_shape','custom_shape_scale']



    #ob = bpy.data.objects.new('autorig', autorig.copy())
    ob = autorig.copy()
    ob.name = 'autorig'
    ob.data = autorig.data.copy()

    autorig.user_remap(ob)

    scene.objects.link(ob)
    ob.select = True
    scene.objects.active = ob

    #match with the metarig
    match_bones(ob,metarig)


    extra_bones = [b.name for b in rig.data.bones if b.name not in [b.name for b in autorig.data.bones]]

    bpy.ops.object.mode_set(mode= 'EDIT')

    # add extra bones
    for ref_bone in extra_bones :
        edit_bone = ob.data.edit_bones.new(ref_bone)
        pose_bone = rig.pose.bones.get(ref_bone)
        print("####",edit_bone,pose_bone)
        info  = rig_values.get(ref_bone)

        edit_bone.tail = info['tail']
        edit_bone.head = info['head']
        edit_bone.roll = info['roll']

        edit_bone.parent = ob.data.edit_bones.get(pose_bone.parent.name)


    bpy.ops.object.mode_set(mode= 'OBJECT')

    #constraints
    for ref_bone in extra_bones :
        pose_bone = ob.pose.bones.get(ref_bone)
        ref_pose_bone = rig.pose.bones.get(ref_bone)

        for ref_constraint in ref_pose_bone.constraints :
            c = pose_bone.constraints.new(type = ref_constraint.type)

            for attr in [p.identifier for p in ref_constraint.bl_rna.properties] :
                value = getattr(ref_constraint,attr)
                try :
                    setattr(c,attr,value)
                except :
                    print(attr)

    rig.user_remap(ob)
    #update bone data attributes
    for pbone in ob.pose.bones :
        ref_bone = rig.pose.bones.get(pbone.name)
        if ref_bone :
            for attr in data_attr :
                value = getattr(ref_bone.bone,attr)
                setattr(pbone.bone,attr,value)

            for attr in pose_attr :
                value = getattr(ref_bone,attr)
                setattr(pbone,attr,value)
    #pose attr

    #bpy.data.objects.remove(ob,True)

    bpy.context.scene.objects.active = active_object
    bpy.ops.object.mode_set(mode= mode)
