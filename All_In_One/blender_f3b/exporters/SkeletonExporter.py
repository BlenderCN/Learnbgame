import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log



def export_skeleton(ctx: F3bContext,src, dst):
    dst.id = ctx.idOf(src)
    dst.name = src.name
    # for src_bone in armature.pose.bones:
    for src_bone in src.bones:
        dst_bone = dst.bones.add()
        dst_bone.id = ctx.idOf(src_bone)
        dst_bone.name = src_bone.name

        # retreive transform local to parent
        boneMat = src_bone.matrix_local
        if src_bone.parent:
            boneMat = src_bone.parent.matrix_local.inverted() @ src_bone.matrix_local
        loc, quat, sca = boneMat.decompose()

        # Can't use armature.convert_space
        # boneMat = armature.convert_space(pose_bone=src_bone, matrix=src_bone.matrix, from_space='POSE', to_space='LOCAL_WITH_PARENT')
        # loc, quat, sca = boneMat.decompose()

        cnv_scale(sca, dst_bone.scale)
        cnv_translation(loc, dst_bone.translation)
        # cnv_scale(loc, transform.translation)
        cnv_rotation(quat, dst_bone.rotation)
        # cnv_quatZupToYup(quat, transform.rotation)
        # cnv_quat(quat, transform.rotation)
        if src_bone.parent:
            rel = dst.bones_graph.add()
            rel.ref1 = ctx.idOf(src_bone.parent)
            rel.ref2 = dst_bone.id



def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            #sprint("Skip ",obj,"not selected/render disabled")
            continue
        if obj.type == 'ARMATURE':
            src_skeleton = obj.data
            # src_skeleton = obj.pose
            if ctx.checkUpdateNeededAndClear(src_skeleton):
                dst_skeleton = data.skeletons.add()
                export_skeleton(ctx,src_skeleton, dst_skeleton)
            Relations.add(ctx,data,ctx.idOf(obj),ctx.idOf(src_skeleton))