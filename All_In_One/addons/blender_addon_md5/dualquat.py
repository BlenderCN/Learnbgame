import re
import bpy
import math
from mathutils import Vector, Matrix, Quaternion

QID = Quaternion((1.0, 0.0, 0.0, 0.0))

def mat_offset(pose_bone):
    bone = pose_bone.bone
    mat = bone.matrix.to_4x4()
    mat.translation = bone.head
    if pose_bone.parent:
        mat.translation.y += bone.parent.length
    return mat

class DualQuat:
    def __init__(self, r=QID.copy(), d=Quaternion()):
        self.r = r
        self.d = d

    def copy(self):
        return DualQuat(
            self.r.copy(),
            self.d.copy())

    def __mul__(self, other):
        result = self.copy()
        result.r = self.r * other.r
        result.d = (self.r * other.d +
                    self.d * other.r)
        return result

    def __add__(self, other):
        result = self.copy()
        result.r += other.r
        result.d += other.d
        return result

    def __eq__(self, other):
        EPS = 1e-4
        return all(abs(rs - ro) < EPS and abs(ds - do) < EPS
            for rs, ro, ds, do in zip(self.r, other.r, self.d, other.d))

    def __str__(self):
        tuple_4f = "% .6f % .6f % .6f % .6f"
        return " ".join(("Dual Quaternion",
                         "Real:", tuple_4f % tuple(self.r),
                         "Img:",  tuple_4f % tuple(self.d)))

    def __repr__(self):
        return "DualQuat(%s, %s)" % (repr(self.r), repr(self.d))

    def conjugated(self):
        result = self.copy()
        result.r.conjugate()
        result.d.conjugate()
        return result

    def inverted(self):
        result = self.copy()
        result.r.invert()
        result.d = -(result.r * result.d * result.r)
        return result

    def transform(self, vec):
        p = DualQuat(
            QID.copy(),
            Quaternion((0.0, *vec)))

        result = self * p * self.conjugated()
        return Vector(result.d[1:])

    def mulorient(self, quat):
        self.r = quat * self.r
        self.d = quat.inverted() * self.d

    def fixantipodal(self, dq):
        if self.r.dot(dq.r) < 0.0:
            self.r = -self.r
            self.d = -self.d

    def from_loc_rot(self, loc, rot):
        self.r = rot.copy()
        self.d = 0.5 * Quaternion((0.0, *loc)) * rot
        return self

    def to_matrix(self):
        mat = Matrix()
        r = self.r
        d = 2 * (self.d * self.r.conjugated())
        s = r.copy()
        for i in range(4): s[i] *= s[i]

        mat[0][0] = s.w + s.x - s.y - s.z
        mat[1][1] = s.w - s.x + s.y - s.z
        mat[2][2] = s.w - s.x - s.y + s.z
        mat[0][1] = 2 * (r.x * r.y - r.w * r.z)
        mat[1][0] = 2 * (r.x * r.y + r.w * r.z)
        mat[0][2] = 2 * (r.x * r.z + r.w * r.y)
        mat[2][0] = 2 * (r.x * r.z - r.w * r.y)
        mat[1][2] = 2 * (r.y * r.z - r.w * r.x)
        mat[2][1] = 2 * (r.y * r.z + r.w * r.x)

        mat[0][3] = d.x
        mat[1][3] = d.y
        mat[2][3] = d.z

        return mat

    def to_loc_rot(self):
        loc = 2.0 * self.d * self.r.inverted()
        return (
            Vector(loc[1:]),
            self.r.copy())

    def translate(self, t):
        loc, rot = self.to_loc_rot()
        self.from_loc_rot(loc + t, rot)

class BoneAdjustment:
    def __init__(self, name, yaw=0.0, pitch=0.0, roll=0.0, translation=None):
        self.name = name
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll

        if translation is not None:
            translation = 0.25 * Vector(translation)

        self.translation = translation

    def adjust(self, dq):
        axes = (
            Vector(( 0.0,  0.0,  1.0)),
            Vector(( 0.0, -1.0,  0.0)),
            Vector((-1.0,  0.0,  0.0))
        )
        angles = self.yaw, self.pitch, self.roll

        for axis, angle in zip(axes, angles):
            dq.mulorient(Quaternion(axis, math.radians(angle)))

        if self.translation is not None:
            dq.translate(self.translation)

    @staticmethod
    def conv_sauerbraten(dq):
        loc, rot = dq.to_loc_rot()
        rot.w = -rot.w
        rot.y = -rot.y
        loc.y = -loc.y
        dq.from_loc_rot(loc, rot)

    def adjust_sb(self, dq):
        self.conv_sauerbraten(dq)
        self.adjust(dq)
        self.conv_sauerbraten(dq)

def convert_kf_pts(kf_pts, cls):
    return cls(kf.co.y for kf in kf_pts)

def set_kf_pts(kf_pts, iterable):
    for kf, elem in zip(kf_pts, iterable):
        kf.co.y = elem

def create_fcu_dict(action):
    re_data_path = re.compile('pose\.bones\["(?P<name>[^"]*)"\]\.(?P<attr>.*)')
    result = {}

    for fcu in action.fcurves:
        mobj = re_data_path.match(fcu.data_path)
        if mobj is not None:
            attr = mobj.group("attr")
            if  attr == "location": n = 0
            elif attr == "rotation_quaternion": n = 1
            else: raise ValueError

            name = mobj.group("name")
            data = result.get(name)
            if data is None:
                data = [None]*3, [None]*4
                result[name] = data

            data[n][fcu.array_index] = fcu

    return result

def adjust_bone_animation(adjustment, pb, fcu_loc, fcu_rot):
    loc, rot, scale = mat_offset(pb).decompose()
    dq_ofs = DualQuat().from_loc_rot(loc, rot)
    dq_ofs_inv = dq_ofs.inverted()

    iter_loc = zip(*(fcu.keyframe_points for fcu in fcu_loc))
    iter_rot = zip(*(fcu.keyframe_points for fcu in fcu_rot))

    for kf_loc, kf_rot in zip(iter_loc, iter_rot):
        loc = convert_kf_pts(kf_loc, Vector)
        rot = convert_kf_pts(kf_rot, Quaternion)

        dq_frame = DualQuat().from_loc_rot(loc, rot)
        dq_frame = dq_ofs * dq_frame

        adjustment.adjust_sb(dq_frame)

        dq_frame = dq_ofs_inv * dq_frame
        loc, rot = dq_frame.to_loc_rot()

        set_kf_pts(kf_loc, loc)
        set_kf_pts(kf_rot, rot)

def adjust_animation(obj, adjustments):
    action = obj.animation_data.action
    lookup_transform = create_fcu_dict(action)

    for adjustment in adjustments:
        name = adjustment.name
        pose_bone = obj.pose.bones[name]
        fcu_loc, fcu_rot = lookup_transform[name]
        adjust_bone_animation(adjustment, pose_bone, fcu_loc, fcu_rot)

def test():
    obj = bpy.data.objects["Armature_Hands"]
    adjustments = ( BoneAdjustment("Root", 11.9, -5.4, 0.0, (0.4, 0.0, 0.0)), )
    adjust_animation(obj, adjustments)

    bpy.context.scene.frame_set(0)

if __name__ == "__main__":
    test()
