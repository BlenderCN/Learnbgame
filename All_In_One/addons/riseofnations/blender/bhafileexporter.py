import bpy
from ..formats.bha.bhafile import BHAFile
from ..formats.bha.bhabonetrack import BHABoneTrack
from time import process_time


class BHAFileExporter:
    def __init__(self):
        self._file = None
        self._scene = None
        self._skin = None
        self._action = None
        self._fps = 30

    def save(self, ctx, filename):
        start_time = process_time()
        self._file = BHAFile()
        self._scene = ctx.scene

        self._skin = self._scene.objects.active
        self._action = self._skin.animation_data.action
        self._fps = self._scene.render.fps

        bpy.ops.object.mode_set(mode='OBJECT')
        self._file.root_bone_track = self._create_bone_tracks(self._skin.pose.bones[0])
        self._file.write(filename)

        print("BHA export took {:f} seconds".format(process_time() - start_time))
        return {'FINISHED'}

    def _create_bone_tracks(self, pose_bone):
        bone_track = BHABoneTrack()

        keyframes = self._get_bone_keyframe_times(pose_bone)
        base_time = 0  # keyframes.pop(0)
        bone_track.add_keys(len(keyframes))

        for bone_track_key, frame in zip(bone_track.keys, keyframes):
            self._scene.frame_set(frame)

            bone_track_key.time_step = (frame - base_time) / self._fps
            bone_track_key.rotation = pose_bone.rotation_quaternion.inverted()
            bone_track_key.position = list(pose_bone.location)

            base_time = frame

        for pose_bone_child in pose_bone.children:
            child = self._create_bone_tracks(pose_bone_child)
            child.parent = bone_track
            bone_track.children.append(child)

        return bone_track

    def _get_bone_keyframe_times(self, pose_bone):
        keyframes = set()
        for fcu in self._action.fcurves:
            if fcu.data_path.split("\"")[1] == pose_bone.name:
                for keyframe in fcu.keyframe_points:
                    keyframes.add(keyframe.co[0])
        return sorted(keyframes)
