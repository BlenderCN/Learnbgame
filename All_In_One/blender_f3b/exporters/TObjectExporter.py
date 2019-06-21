import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log

def exportCustomProperties(ctx: F3bContext,data: f3b.datas_pb2.Data,src:bpy.types.Object, parent_data:f3b.tobjects_pb2.TObject):
    keys = [k for k in src.keys() if not (k.startswith('_') or k.startswith('cycles'))]
    if len(keys) > 0:
        # custom_params = dst_data.Extensions[f3b.custom_params_pb2.custom_params].add()
        custom_params = data.custom_params.add()
        custom_params.id = "params_" + ctx.idOf(src)
        for key in keys:
            param = custom_params.params.add()
            param.name = key
            value = src[key]
            if isinstance(value, bool):
                param.vbool = value
            elif isinstance(value, str):
                param.vstring = value
            elif isinstance(value, float):
                param.vfloat = value
            elif isinstance(value, int):
                param.vint = value
            elif isinstance(value, mathutils.Vector):
                cnv_vec3(value, param.vvec3)
            elif isinstance(value, mathutils.Quaternion):
                cnv_qtr(value, param.vqtr)
        Relations.add( ctx,data, custom_params.id,  parent_data.id)


def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    for obj in scene.objects: #type: bpy.types.Object         
        if not ctx.isExportable(obj):
           # print("Skip ",obj,"not selected/render disabled")
            continue
        if ctx.checkUpdateNeededAndClear(obj):
            tobject :f3b.tobjects_pb2.TObject = data.tobjects.add()
            tobject.id = ctx.idOf(obj)
            tobject.name = obj.name
            loc, quat, scale = obj.matrix_local.decompose()
            cnv_scale(scale, tobject.scale)
            cnv_translation(loc, tobject.translation)
            if obj.type == 'MESH':
                cnv_rotation(quat, tobject.rotation)
            elif obj.type == 'Armature':
                cnv_rotation(quat, tobject.rotation)
            elif obj.type == 'LAMP' or obj.type=="LIGHT":
                rot = z_backward_to_forward(quat)
                cnv_quatZupToYup(rot, tobject.rotation)
            else:
                cnv_rotation(rot_quat(obj), tobject.rotation)
            if obj.parent is not None:
                Relations.add(ctx, data, ctx.idOf(obj.parent), ctx.idOf(obj))
            exportCustomProperties(ctx,data, obj, tobject)
        else:
            log.debug("Skip "+obj+" already exported")