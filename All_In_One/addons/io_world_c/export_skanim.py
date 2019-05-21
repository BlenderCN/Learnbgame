import bpy
import math

def get_pose_bone_matrix(pose_bone):
    local_matrix = pose_bone.matrix_channel.to_3x3()
    if pose_bone.parent is None:
        return local_matrix
    else:
        return pose_bone.parent.matrix_channel.to_3x3().inverted() * local_matrix

class AnimBone(object):
    def __init__(self):
        self.rotation = []

class AnimFrame(object):
    def __init__(self):
        self.bones = []
        self.origin = []

class AnimMarker(object):
    def __init__(self):
        self.name = ""
        self.frame = 0

class Anim(object):
    def __init__(self):
        self.frame_count = 0
        self.joint_count = 0
        self.frames = []
        self.markers = []

    def extract(self, b_armature, b_scene):
        self.frame_count = 1 + (b_scene.frame_end - b_scene.frame_start)
        self.joint_count = len(b_armature.data.bones)

        for frame_index in range(b_scene.frame_start, b_scene.frame_end + 1):
            b_scene.frame_set(frame_index)
            frame = AnimFrame()

            for b_bone in b_armature.pose.bones:
                bone = AnimBone()
                if b_bone.parent is None:
                    bone_head = b_bone.head - b_bone.bone.head_local
                    frame.origin = [bone_head[0], bone_head[1], bone_head[2]]

                quat = get_pose_bone_matrix(b_bone).to_quaternion()
                bone.rotation = [quat[0], quat[1], quat[2], quat[3]]
                frame.bones.append(bone)

            self.frames.append(frame)

        b_scene.frame_set(b_scene.frame_start)

        for b_marker in b_scene.timeline_markers:
            if b_marker.frame < b_scene.frame_start or b_marker.frame > b_scene.frame_end:
                continue

            marker = AnimMarker()

            marker.frame = b_marker.frame - b_scene.frame_start
            marker.name = b_marker.name

            self.markers.append(marker)


def export(b_armature, filename):
    file_version = 3

    b_scene = bpy.context.scene

    anim = Anim()
    anim.extract(b_armature, b_scene)

    file = open(filename, "w")
    file.write("# World C - SkelAnim\n")
    file.write("version: %i\n" % file_version)
    file.write("frame_count: %i\n" % anim.frame_count)
    file.write("joint_count: %i\n" % anim.joint_count)
    file.write("marker_count: %i\n" % len(anim.markers))

    file.write("frames: \n")
    for frame in anim.frames:
        file.write("[%f, %f, %f]\n" % (frame.origin[0], frame.origin[1], frame.origin[2]))
        for bone in frame.bones:
            file.write("[%f, %f, %f, %f]\n" % (bone.rotation[0], bone.rotation[1], bone.rotation[2], bone.rotation[3]))

    file.write("markers: \n")
    for marker in anim.markers:
        file.write("( %s ), %i\n" % (marker.name, marker.frame))

    file.close()
