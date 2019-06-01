import re
import bpy
from mathutils import Vector, Quaternion, Matrix

from .utils import XMLWriter, get_bone_order

SKELETON = '<skeleton blendmode="average">'
BONE = '<bone id="{id:d}" name="{name:s}">'
POSITION = '<position x="{x:g}" y="{y:g}" z="{z:g}" />'
ROTATION = '<rotation angle="{angle:g}">'
AXIS = '<axis x="{x:g}" y="{y:g}" z="{z:g}" />'
BONEPARENT = '<boneparent bone="{bone:s}" parent="{parent:s}" />'
ANIMATION = '<animation name="{name:s}" length="{length:g}">'
TRACK = '<track bone="{bone:s}">'
KEYFRAME = '<keyframe time="{time:g}">'
TRANSLATE = '<translate x="{x:g}" y="{y:g}" z="{z:g}" />'
ROTATE = '<rotate angle="{angle:g}">'

class AnimData:
    def __init__(self, bone):
        self.name = bone.name
        self.bone = bone
        self.loc = [None]*3
        self.rot = [None]*4

    def get_loc(self, index):
        return Vector(fcu.keyframe_points[index].co.y for fcu in self.loc)

    def get_rot(self, index):
        return Quaternion(fcu.keyframe_points[index].co.y for fcu in self.rot)

    def do_skip(self):
        return not all(self.loc) and not all(self.rot)

    def __iter__(self):
        iter_loc = tuple(iter(fcu.keyframe_points) for fcu in self.loc)
        iter_rot = tuple(iter(fcu.keyframe_points) for fcu in self.rot)
        return zip(*iter_loc, *iter_rot)

"""
skeleton
    bones
        bone
            position
            rotation
                axis
    bonehierarchy
        boneparent
    animations
        animation
            tracks
                track
                    keyframes
                        keyframe
                            translate
                            rotate
                                axis
"""

ZERO = Vector()
QUAT_ID = Quaternion((1.0, 0.0, 0.0, 0.0))
MAT4_ROT = Matrix((
    ( 0.0,  1.0,  0.0,  0.0),
    (-1.0,  0.0,  0.0,  0.0),
    ( 0.0,  0.0,  1.0,  0.0),
    ( 0.0,  0.0,  0.0,  1.0),
))
MAT4_ROT_INV = Matrix((
    ( 0.0, -1.0,  0.0,  0.0),
    ( 1.0,  0.0,  0.0,  0.0),
    ( 0.0,  0.0,  1.0,  0.0),
    ( 0.0,  0.0,  0.0,  1.0),
))
MAT3_ROT_INV = Matrix((
    ( 0, -1,  0),
    ( 1,  0,  0),
    ( 0,  0,  1)
))
MAT_ROT_Y90_INV = Matrix((
    ( 0.0,  0.0, -1.0,  0.0),
    ( 0.0,  1.0,  0.0,  0.0),
    ( 1.0,  0.0,  0.0,  0.0),
    ( 0.0,  0.0,  0.0,  1.0),
))

def write_skeleton(stream, ob, bind_pose=False):
    xml = XMLWriter(stream)
    am = ob.data

    bone_order = get_bone_order(am)
    bones = tuple(am.bones[name] for name in bone_order)

    if not bind_pose:
        action = ob.animation_data.action
        anm_data = collect_anm_data(action, am, bone_order)

    xml.tag_open_format(SKELETON)
    xml.tag_open("bones")
    for bid, bone in enumerate(bones):
        if bind_pose:
            loc, rot = calc_rest(bone)
        else:
            ad = anm_data[bone.name]
            if ad.do_skip(): continue
            loc, rot = calc_keyframe(bone, ad.get_loc(0), ad.get_rot(0))
        write_bone(xml, bone.name, bid, loc, rot)
    xml.tag_close("bones")

    xml.tag_open("bonehierarchy")
    for bone in bones:
        if bone.parent is None:
            continue
        if not bind_pose:
            ad = anm_data[bone.name]
            if ad.do_skip(): continue
        xml.tag_format(BONEPARENT, bone=bone.name, parent=bone.parent.name)
    xml.tag_close("bonehierarchy")

    xml.tag_open("animations")

    if not bind_pose:
        fps = bpy.context.scene.render.fps
        anm_length = (action.frame_range[1] - action.frame_range[0]) / fps
        xml.tag_open_format(ANIMATION, name=action.name, length=anm_length)
        xml.tag_open("tracks")
        for bone_name in bone_order:
            ad = anm_data[bone_name]
            if ad.do_skip():
                print("Skipping ",  ad.name)
                continue
            write_track(xml, ad, fps)
        xml.tag_close("tracks")
    else:
        xml.tag_open_format(ANIMATION, name="Bind", length=0)
        xml.tag_format("<tracks />")

    xml.tag_close("animation")
    xml.tag_close("animations")
    xml.tag_close("skeleton")
    xml.finish()

def collect_anm_data(action, armature, bone_names):
    data_path_pattern = re.compile('pose\.bones\["(?P<name>.+?)"\]\.(?P<attr>location|rotation_quaternion)')

    anm_data = {bone_name: AnimData(armature.bones[bone_name]) for bone_name in bone_names}

    for fcu in action.fcurves:
        mo = data_path_pattern.match(fcu.data_path)
        if mo is None: continue

        ad = anm_data[mo.group("name")]
        if mo.group("attr") == "location": ad.loc[fcu.array_index] = fcu
        else                             : ad.rot[fcu.array_index] = fcu

    return anm_data

def calc_rest(bone):
    has_parent = bone.parent is not None
    if not has_parent:
        rot = (bone.matrix * MAT3_ROT_INV).to_quaternion()
        loc = bone.head
    else:
        mat = bone.parent.matrix_local.inverted() * bone.matrix_local
        mat = MAT4_ROT * mat * MAT4_ROT_INV
        loc, rot, scale = mat.decompose()

    return loc, rot

def write_bone(xml, name, bid, loc, rot):
    axis, angle = rot.to_axis_angle()
    xml.tag_open_format(BONE, name=name, id=bid)
    xml.tag_format(POSITION, x=loc.x, y=loc.y, z=loc.z)
    xml.tag_open_format(ROTATION, angle=angle)
    xml.tag_format(AXIS, x=axis.x, y=axis.y, z=axis.z)
    xml.tag_close("rotation")
    xml.tag_close("bone")

def calc_keyframe(bone, loc, rot):
    mat_basis = rot.to_matrix().to_4x4()
    mat_basis.translation = loc

    if bone.parent is not None:
        mat_offset = bone.matrix.to_4x4()
        mat_offset.translation = bone.head
        mat_offset.translation.y += bone.parent.length
        mat_basis = mat_offset * mat_basis
    else:
        mat_basis = MAT_ROT_Y90_INV * mat_basis

    mat_basis = MAT4_ROT * mat_basis * MAT4_ROT_INV
    loc, rot, scale = mat_basis.decompose()
    return loc, rot

def is_same_time(kfp):
    return all(abs(kfp[0].co.x - kfp[i].co.x) < 5e-4 for i in range(1, 7))

def write_track(xml, anm_data, fps):
    xml.tag_open_format(TRACK, bone=anm_data.name)
    xml.tag_open("keyframes")

    loc0, rot0_inv, first_frame = None, None, True

    for kfpts in anm_data:
        assert is_same_time(kfpts)

        loc =     Vector(kfp.co.y for kfp in kfpts[0:3])
        rot = Quaternion(kfp.co.y for kfp in kfpts[3:7])
        loc, rot = calc_keyframe(anm_data.bone, loc, rot)

        if first_frame:
            loc0 = loc
            rot0_inv = rot.inverted()
            first_frame = False

        loc = loc - loc0
        rot = rot0_inv * rot

        write_keyframe(xml, kfpts[0].co.x / fps, loc, rot)

    xml.tag_close("keyframes")
    xml.tag_close("track")

def write_keyframe(xml, time, loc, rot):
    axis, angle = rot.to_axis_angle()
    xml.tag_open_format(KEYFRAME, time=time)
    xml.tag_format(TRANSLATE, x=loc.x, y=loc.y, z=loc.z)
    xml.tag_open_format(ROTATE, angle=angle)
    xml.tag_format(AXIS, x=axis.x, y=axis.y, z=axis.z)
    xml.tag_close("rotate")
    xml.tag_close("keyframe")
