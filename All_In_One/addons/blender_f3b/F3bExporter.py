import f3b,bpy
from .F3bContext import *
from . import Logger as log

# Exporters #
from .exporters import TObjectExporter
from .exporters import SpeakersExporter
from .exporters import GeometryExporter
from .exporters import MaterialExporter
from .exporters import LightExporter
from .exporters import SkeletonExporter
from .exporters import ActionExporter
from .exporters import PhysicsExporter
from .exporters import CollisionPlanes
from .exporters import EmittersExporter
from .exporters import ForceFieldExporter
#############


def startExport(ctx: F3bContext ,scene: bpy.types.Scene):
    log.info("Export to "+ ctx.topath)
    data = f3b.datas_pb2.Data()
    CollisionPlanes.export(ctx,data,scene)
    TObjectExporter.export(ctx,data,scene)
    EmittersExporter.export(ctx,data,scene)
    SpeakersExporter.export(ctx,data,scene)
    GeometryExporter.export(ctx,data,scene)
    MaterialExporter.export(ctx,data,scene)
    LightExporter.export(ctx,data,scene)
    SkeletonExporter.export(ctx,data,scene)
    ActionExporter.export(ctx,data,scene)
    PhysicsExporter.export(ctx,data,scene)
    ForceFieldExporter.export(ctx,data,scene)

    return data
    
