import bpy
from mathutils import Quaternion
from ..formats.bha.bhafile import BHAFile
from time import process_time
import os


class BHAFileImporter:
    def __init__(self, stabilize_quaternions):
        self._file = None
        self._skin = None
        self._action = None
        self._fps = 30
        self._stabilize_quaternions = stabilize_quaternions

    def load(self, ctx, filename):
        start_time = process_time()
        anim_name = os.path.splitext(os.path.basename(filename))[0]

        self._file = BHAFile()
        self._file.read(filename)

        self._skin = ctx.scene.objects.active
        if not self._skin.animation_data:
            self._skin.animation_data_create()
        self._action = bpy.data.actions.new(name=anim_name)
        self._skin.animation_data.action = self._action

        bpy.ops.object.mode_set(mode='OBJECT')
        self._fps = 30
        ctx.scene.render.fps = self._fps
        self._animate_bone(self._file.root_bone_track, self._skin.pose.bones[0])
        ctx.scene.frame_end = self._action.frame_range[1]
        ctx.scene.frame_start = 0

        print("BHA import took {:f} seconds".format(process_time() - start_time))
        return {'FINISHED'}

    def _animate_bone(self, bone, pose_bone):
        data_path_loc = "pose.bones[\"%s\"].location" % pose_bone.name
        data_path_rot = "pose.bones[\"%s\"].rotation_quaternion" % pose_bone.name

        pos_curve_x = self._action.fcurves.new(data_path=data_path_loc, index=0)
        pos_curve_y = self._action.fcurves.new(data_path=data_path_loc, index=1)
        pos_curve_z = self._action.fcurves.new(data_path=data_path_loc, index=2)
        rot_curve_w = self._action.fcurves.new(data_path=data_path_rot, index=0)
        rot_curve_x = self._action.fcurves.new(data_path=data_path_rot, index=1)
        rot_curve_y = self._action.fcurves.new(data_path=data_path_rot, index=2)
        rot_curve_z = self._action.fcurves.new(data_path=data_path_rot, index=3)

        time = 0
        qs = QuaternionStabilizer()
        for key in bone.keys:
            time += round(self._fps * key.time_step, 5)
            if self._stabilize_quaternions:
                rotation = qs.stabilize(Quaternion(key.rotation).inverted())
            else:
                rotation = Quaternion(key.rotation).inverted()
            pos_curve_x.keyframe_points.insert(time, key.position[0])
            pos_curve_y.keyframe_points.insert(time, key.position[1])
            pos_curve_z.keyframe_points.insert(time, key.position[2])
            rot_curve_w.keyframe_points.insert(time, rotation[0])
            rot_curve_x.keyframe_points.insert(time, rotation[1])
            rot_curve_y.keyframe_points.insert(time, rotation[2])
            rot_curve_z.keyframe_points.insert(time, rotation[3])

        for child_bone, child_pose_bone in zip(bone.children, pose_bone.children):
            self._animate_bone(child_bone, child_pose_bone)


class QuaternionStabilizer:
    def __init__(self):
        self.old = None

    def stabilize(self, q):
        if not self.old:
            rval = q
        else:
            d1 = (self.old - q).magnitude
            d2 = (self.old + q).magnitude
            if d1 < d2:
                rval = q
            else:
                rval = -q
        self.old = rval
        return rval
