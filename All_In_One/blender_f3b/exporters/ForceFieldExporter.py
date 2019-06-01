import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log

def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    if scene.use_gravity:
        force_field=data.cr_forcefields.add()
        force_field.id="sceneGravity"
        cnv_vec3(cnv_toVec3ZupToYup(scene.gravity), force_field.gravity.strength)