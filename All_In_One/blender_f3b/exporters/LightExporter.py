import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log

def export_light(ctx: F3bContext,src, dst):
    dst.id = ctx.idOf(src)
    dst.name = src.name
    kind = src.type
    if kind == 'SUN' or kind == 'AREA' or kind == 'HEMI':
        dst.kind = f3b.datas_pb2.Light.directional
        dst.cast_shadow = True
    elif kind == 'POINT':
        dst.kind = f3b.datas_pb2.Light.point     
        dst.cast_shadow = True   
    elif kind == 'SPOT':
        dst.kind = f3b.datas_pb2.Light.spot
        dst.spot_angle.max = src.spot_size * 0.5
        dst.spot_angle.linear.begin = (1.0 - src.spot_blend)
        dst.cast_shadow = True
    
    processed=False
    if src.node_tree!=None and len(src.node_tree.nodes)>0: 
        for node in src.node_tree.nodes:
            if node.type == "EMISSION":
                cnv_color(node.inputs[0].default_value, dst.color)
                #if kind=="POINT":
                 #       dst.radial_distance.max=node.inputs[1].default_value
                dst.intensity = node.inputs[1].default_value
                dst.cast_shadow = src.cycles.cast_shadow
                processed=True                
                
    if not processed:         
        dst.cast_shadow = getattr(src, 'use_shadow', False)
        cnv_color(src.color, dst.color)
        dst.intensity = src.energy
        dst.radial_distance.max = src.distance
        if hasattr(src, 'falloff_type'):
            falloff = src.falloff_type
            if falloff == 'INVERSE_LINEAR':
                dst.radial_distance.max = src.distance
                dst.radial_distance.inverse.scale = 1.0
            elif falloff == 'INVERSE_SQUARE':
                dst.radial_distance.max = src.distance  # math.sqrt(src.distance)
                dst.radial_distance.inverse_square.scale = 1.0
            elif falloff == 'LINEAR_QUADRATIC_WEIGHTED':
                if src.quadratic_attenuation == 0.0:
                    dst.radial_distance.max = src.distance
                    dst.radial_distance.inverse.scale = 1.0
                    dst.radial_distance.inverse.constant = 1.0
                    dst.radial_distance.inverse.linear = src.linear_attenuation
                else:
                    dst.radial_distance.max = src.distance
                    dst.radial_distance.inverse_square.scale = 1.0
                    dst.radial_distance.inverse_square.constant = 1.0
                    dst.radial_distance.inverse_square.linear = src.linear_attenuation
                    dst.radial_distance.inverse_square.linear = src.quadratic_attenuation
        if getattr(src, 'use_sphere', False):
            dst.radial_distance.linear.end = 1.0


def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            continue
        if obj.type == 'LAMP' or obj.type == 'LIGHT':
            src_light = obj.data
            if ctx.checkUpdateNeededAndClear(src_light):
                dst_light = data.lights.add()
                export_light(ctx,src_light, dst_light)
            Relations.add(ctx,data,ctx.idOf(src_light),ctx.idOf(obj))
