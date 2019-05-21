import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log
from . import GeometryExporter
from . import MaterialExporter

def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            #sprint("Skip ",obj,"not selected/render disabled")
            continue 
        for i in range(len(obj.particle_systems)):
            src_p = obj.particle_systems[i] #Emitter
            src_e = src_p.settings #Settings
            if src_e.type != "EMITTER": continue
            if ctx.checkUpdateNeededAndClear(src_e) or 1==1:  
                dst_e = data.cr_emitters.add()
                dst_e.id=ctx.idOf(obj)+"_em_"+str(i)
                dst_e.name=src_e.name
                print("Export particle emitter " +src_e.name)
                # fps=(1.0/src_e.timestep)
                frame_end=src_e.frame_end
                frame_start=src_e.frame_start
                time_end=frame_end*src_e.timestep
                time_start=frame_start*src_e.timestep
                
                frame_delta=frame_end-frame_start
                time_delta=time_end-time_start
        
                dst_e.emission_delay=time_start
                dst_e.emission_duration=time_delta
                dst_e.particles_per_emission=src_e.count

                # dst_e.time_end=frame_end/fps

                lifetime=src_e.lifetime*src_e.timestep
                randlife=src_e.lifetime_random*src_e.timestep

                dst_e.min_life=lifetime* (1.0 - randlife)
                dst_e.max_life=lifetime
                # dst_e.particles_per_second=int(src_e.count/time_delta)


                if src_e.emit_from == "VERT":
                    dst_e.emit_from=  f3b.datas_pb2.CRParticleEmitter.emit_from_verts
                elif src_e.emit_from=="FACE":
                    dst_e.emit_from=  f3b.datas_pb2.CRParticleEmitter.emit_from_faces
                else:
                    dst_e.emit_from= f3b.datas_pb2.CRParticleEmitter.emit_from_volume

                dst_e.velocity.normal_factor=src_e.normal_factor
                dst_e.velocity.tangent_factor=src_e.tangent_factor
                dst_e.velocity.tangent_phase=src_e.tangent_phase
                cnv_vec3(cnv_toVec3ZupToYup(src_e.object_align_factor),  dst_e.velocity.object_align_factor)
                dst_e.velocity.object_factor=src_e.object_factor
                dst_e.velocity.variation=src_e.factor_random

                if src_e.physics_type=="NEWTON":
                    dst_e.newtonian_influencer.brownian=src_e.brownian_factor
                    dst_e.newtonian_influencer.drag=src_e.drag_factor
                    dst_e.newtonian_influencer.damp=src_e.damping
                    dst_e.timestep=scene.render.fps*src_e.timestep
                    dst_e.newtonian_influencer.die_on_hit=src_e.use_die_on_collision
                
                mesh=None
                if src_e.render_type == "BILLBOARD":
                    dst_e.billboard_renderer.size=src_e.particle_size
                    dst_e.billboard_renderer.size_variation=src_e.size_random
                    mesh=src_e.billboard_object
                else:
                    dst_e.object_renderer.size=src_e.particle_size
                    dst_e.object_renderer.size_variation=src_e.size_random
                    mesh=src_e.instance_object


            
                dst_e.rotation.random_factor=src_e.rotation_factor_random
                dst_e.rotation.velocity=src_e.angular_velocity_factor
                ef_weight_damper=src_e.effector_weights.all
                dst_e.forcefields_influence.gravity=src_e.effector_weights.gravity*ef_weight_damper

                MaterialExporter.exportDDSs()
                MaterialExporter.resetDDSConversionQueue()
                if mesh!=None and mesh.type == 'MESH':
                    ctx.checkUpdateNeededAndClear(mesh.data)
                    if len(mesh.data.polygons) != 0:
                        meshes = GeometryExporter.export_meshes(ctx,mesh,scene, dst_e.meshes,0)
                        for material_index, m in meshes.items():
                            if material_index > -1 and material_index < len(mesh.material_slots):
                                src_mat = mesh.material_slots[material_index].material
                                dst_mat = dst_e.materials.add()
                                MaterialExporter.export_material(ctx,src_mat, dst_mat)
                MaterialExporter.exportDDSs()
                MaterialExporter.resetDDSConversionQueue()
            Relations.add(ctx,data,ctx.idOf(obj),dst_e.id)                   
