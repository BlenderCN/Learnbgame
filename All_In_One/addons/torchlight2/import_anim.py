from .utils import *

def create_fcurves(action, data_path, dim, group=""):
    return tuple(action.fcurves.new(data_path, i, group) for i in range(dim))

def insert_keyframe(fcurves, time, values, interpolation="LINEAR"):
    for fcu, val in zip(fcurves, values):
        kf = fcu.keyframe_points.insert(time, val, {'FAST'})
        kf.interpolation = interpolation

def load_animation(anm_input, xml_dir, fps, arm_obj):
    xml_output = os.path.join(xml_dir, os.path.basename(anm_input).split('.')[0] + "_anm.xml")

    convert_to_xml(anm_input, xml_output)
    skelElem = xml.dom.minidom.parse(xml_output).documentElement

    boneElements = find(skelElem, "bones")
    bone_list = [Bone(boneElem) for boneElem in child_iter(boneElements, "bone")]

    animElements = find(skelElem, "animations")
    for animElem in child_iter(animElements, "animation"):
        name = animElem.getAttribute("name")
        length = getFloatAttr(animElem, "length")

        bpy.context.scene.render.fps = fps
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = round(fps * length)

        baseInfo = find(animElem, "baseinfo")
        if baseInfo:
            print(baseInfo.getAttribute("baseanimationname"))
            print(baseInfo.getAttribute("basekeyframetime"))

        trackElements = find(animElem, "tracks")
        create_bones_animation(name, bone_list, trackElements, fps, arm_obj)

def create_bones_animation(name, bone_list, trackElements, fps, obj):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    obj.animation_data_create()
    obj.animation_data.action = action
    data_path = "pose.bones[\"{:s}\"].{:s}"

    ZERO = Vector()
    QUAT_ID = Quaternion((1.0, 0.0, 0.0, 0.0))
    MAT_AXIS_ROT = Matrix((
        ( 0.0,  1.0,  0.0,  0.0),
        (-1.0,  0.0,  0.0,  0.0),
        ( 0.0,  0.0,  1.0,  0.0),
        ( 0.0,  0.0,  0.0,  1.0),
    ))
    MAT_AXIS_ROT_INV = Matrix((
        ( 0.0, -1.0,  0.0,  0.0),
        ( 1.0,  0.0,  0.0,  0.0),
        ( 0.0,  0.0,  1.0,  0.0),
        ( 0.0,  0.0,  0.0,  1.0),
    ))
    MAT_ROT_Y90 = Matrix((
        ( 0.0,  0.0,  1.0,  0.0),
        ( 0.0,  1.0,  0.0,  0.0),
        (-1.0,  0.0,  0.0,  0.0),
        ( 0.0,  0.0,  0.0,  1.0),
    ))

    def calcKeyframeData(pose_bone, loc, quat):
        mat_basis = quat.to_matrix().to_4x4()
        mat_basis.translation = loc
        mat_basis = MAT_AXIS_ROT_INV * mat_basis * MAT_AXIS_ROT

        if pose_bone.parent:
            bone = pose_bone.bone
            mat_offset = bone.matrix.to_4x4()
            mat_offset.translation = bone.head
            mat_offset.translation.y += bone.parent.length
            mat_offset_inv = mat_offset.inverted()
            mat_basis = mat_offset_inv *  mat_basis
        else:
            mat_basis = MAT_ROT_Y90 * mat_basis

        return mat_basis.translation, mat_basis.to_quaternion()

    track_dict = dict()
    for trackElem in child_iter(trackElements, "track"):
        bone_name = trackElem.getAttribute("bone")
        track_dict[bone_name] = trackElem

    for bone_data in bone_list:
        try:
            pose_bone = obj.pose.bones[bone_data.name]
        except KeyError:
            print(bone_data.name, "not found")
            continue

        loc  = bone_data.position
        quat = bone_data.rotation

        fcu_loc  = create_fcurves(action, data_path.format(bone_data.name, "location"),            3, bone_data.name)
        fcu_quat = create_fcurves(action, data_path.format(bone_data.name, "rotation_quaternion"), 4, bone_data.name)

        trackElem = track_dict.get(bone_data.name)
        if not trackElem:
            # insert rest pose, so we can easily switch between actions
            kf_loc, kf_quat = calcKeyframeData(pose_bone, loc, quat)
            insert_keyframe(fcu_loc,  0, kf_loc)
            insert_keyframe(fcu_quat, 0, kf_quat)
            continue

        keyframeElements = find(trackElem, "keyframes")
        for keyframeElem in child_iter(keyframeElements, "keyframe"):
            time = getFloatAttr(keyframeElem, "time")
            for elem in child_iter(keyframeElem):
                if elem.tagName == "translate":
                    translation = Vector(getVecAttr(elem, "xyz"))

                elif elem.tagName == "rotate":
                    angle = getFloatAttr(elem, "angle")
                    axisElem = find(elem, "axis")
                    axis = tuple(getVecAttr(axisElem, "xyz"))
                else:
                    raise ValueError("Invalid tagname %s" % elem.tagName)

            kf_loc, kf_quat = calcKeyframeData(
                pose_bone,
                loc  + translation,
                quat * Quaternion(axis, angle))
            insert_keyframe(fcu_loc,  time*fps, kf_loc)
            insert_keyframe(fcu_quat, time*fps, kf_quat)
