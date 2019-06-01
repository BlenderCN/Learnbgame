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
    for obj in scene.objects:
        if  not ctx.isExportable(obj) or obj.type!= 'MESH':
            #sprint("Skip ",obj,"not selected/render disabled")
            continue
 
        for m in obj.modifiers:
            if m.type == "COLLISION":
                if ctx.checkUpdateNeededAndClear(obj) and ctx.checkUpdateNeededAndClear(obj.data):
                    cplane=data.cr_collisionplanes.add()
                    cplane.id = ctx.idOf(obj)
                    cplane.name = obj.name
                    wm = obj.matrix_world
                    cnv_vec3(cnv_toVec3ZupToYup(wm.to_translation()), cplane.point)
                    rot=wm.to_quaternion()
                    normal=None
                    ps = obj.data.polygons
                    for p in ps:
                        normal=(p.normal)
                        break
                    cnv_vec3(cnv_toVec3ZupToYup(rot*normal), cplane.normal)
                    cnv_vec3(cnv_toVec3ZupToYup(obj.dimensions), cplane.extents)
                    cplane.damping=m.settings.damping_factor
                    cplane.damping_randomness=m.settings.damping_random
                    cplane.friction=m.settings.friction_factor
                    cplane.friction_randomness=m.settings.friction_random
                    cplane.stickiness=m.settings.stickiness
                    cplane.permeability=m.settings.permeability
                    cplane.kill_particles=m.settings.use_particle_kill