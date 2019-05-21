import bpy_extras
import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log

def to_time(frame,fps):
    return int((frame * 1000) / fps)


class Sampler:
    def __init__(self, obj, dst, pose_bone_idx=None):
        self.obj = obj
        self.pose_bone_idx = pose_bone_idx
        self.clip = dst.clips.add()
        if pose_bone_idx is not None:
            self.clip.sampled_transform.bone_name = self.obj.pose.bones[self.pose_bone_idx].name
            self.rest_bone = obj.data.bones[self.pose_bone_idx]
            self.rest_matrix_inverted = self.rest_bone.matrix_local.copy().inverted()
        self.previous_mat4 = None
        self.last_equals = None
        self.cnv_mat = bpy_extras.io_utils.axis_conversion(from_forward='-Y', from_up='Z', to_forward='Z', to_up='Y').to_4x4()

    def capture(self, t):
        if self.pose_bone_idx is not None:
            pbone = self.obj.pose.bones[self.pose_bone_idx]
            mat4 = pbone.matrix
            if pbone.parent:
                mat4 = pbone.parent.matrix.inverted() @ mat4
        else:
            mat4 = self.obj.matrix_local
        if self.previous_mat4 is None or not equals_mat4(mat4, self.previous_mat4, 0.000001):
            if self.last_equals is not None:
                self._store(self.last_equals, self.previous_mat4)
                self.last_equals = None
            self.previous_mat4 = mat4.copy()
            self._store(t, mat4)
        else:
            self.last_equals = t

    def _store(self, t, mat4):
        loc, quat, sca = mat4.decompose()
        dst_clip = self.clip
        dst_clip.sampled_transform.at.append(t)
        dst_clip.sampled_transform.translation_x.append(loc.x)
        dst_clip.sampled_transform.translation_y.append(loc.z)
        dst_clip.sampled_transform.translation_z.append(-loc.y)
        dst_clip.sampled_transform.scale_x.append(sca.x)
        dst_clip.sampled_transform.scale_y.append(sca.z)
        dst_clip.sampled_transform.scale_z.append(sca.y)
        dst_clip.sampled_transform.rotation_w.append(quat.w)
        dst_clip.sampled_transform.rotation_x.append(quat.x)
        dst_clip.sampled_transform.rotation_y.append(quat.z)
        dst_clip.sampled_transform.rotation_z.append(-quat.y)


def export_obj_action(ctx: F3bContext,name,scene, obj, src, dst, fps):
    obj.animation_data.action = src
    dst.id = ctx.idOf(src)
    log.debug("Export animation "+name)
    dst.name = name
    frame_start = int(src.frame_range.x)
    frame_end = int(src.frame_range.y + 1)
    dst.duration = to_time(max(1, float(frame_end - frame_start)),fps)
    samplers = []
    if src.id_root == 'OBJECT':
        dst.target_kind = f3b.animations_kf_pb2.AnimationKF.tobject
        samplers.append(Sampler(obj, dst))
        if obj.type == 'ARMATURE':
            for i in range(0, len(obj.pose.bones)):
                samplers.append(Sampler(obj, dst, i))
    elif src.id_root == 'ARMATURE':
        dst.target_kind = f3b.animations_kf_pb2.AnimationKF.skeleton
        for i in range(0, len(obj.pose.bones)):
            samplers.append(Sampler(obj, dst, i))
    else:
        log.warning("unsupported id_roor => target_kind : " + src.id_root)
        return

    for f in range(frame_start, frame_end):
        scene.frame_set(f)
        for sampler in samplers:
            sampler.capture(to_time(f,fps))


def export(ctx: F3bContext,dst_data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    fps = max(1.0, float(scene.render.fps))
#    for action in bpy.data.actions:
    frame_current = scene.frame_current
    frame_subframe = scene.frame_subframe
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            #sprint("Skip ",obj,"not selected/render disabled")
            continue
        if obj.animation_data:
            action_current = obj.animation_data.action
            for tracks in obj.animation_data.nla_tracks:
                for strip in tracks.strips:
                    action = strip.action
                    if action == None: continue
                    if ctx.checkUpdateNeededAndClear(action):
                        #dst = dst_data.Extensions[f3b.animations_kf_pb2.animations_kf].add()
                        dst = dst_data.animations_kf.add()
                        # export_action(action, dst, fps, cfg)
                        export_obj_action(ctx,tracks.name,scene, obj, action, dst, fps)
                        # relativize_bones(dst, obj)
                    Relations.add(ctx,dst_data,ctx.idOf(action),ctx.idOf(obj))
            obj.animation_data.action = action_current
    scene.frame_set(frame_current, subframe=frame_subframe)