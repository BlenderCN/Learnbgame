import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log

import shutil
import os

def export_audio(ctx: F3bContext,src, dst):
    base_name=src.name
    ext="."+src.filepath.lower().split(".")[-1]
    if ext == "":
        ext="."+src.filepath_raw.lower().split(".")[-1]
    if ext == "":
        ext="."+src.name.lower().split(".")[-1]

    origin_file=bpy.path.abspath(src.filepath) 
    print("Base sound name",base_name,"assets path",ctx.topath)
    output_file=os.path.join(ctx.topath,"Sounds",base_name)+ext  
    print("Write sound in",output_file)

    output_parent=os.path.dirname(output_file)
        
    is_packed=src.packed_file

    if ctx.checkUpdateNeededAndClear(src):       
    
        if not os.path.exists(output_parent):
            os.makedirs(output_parent)
          
        if is_packed:
            print(base_name,"is packed inside the blend file. It will be extracted in",output_file)
            with open(output_file, 'wb') as f:
                f.write(src.packed_file.data)
        else:
            print(origin_file,"will be copied in",output_file)
            if origin_file != output_file:
                shutil.copyfile(origin_file, output_file)            
    else:
        print(base_name,"already up to date")
    dst.rpath = "Sounds/"+base_name+ext
    print("Set rpath to", dst.rpath)

def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            #print("Skip ",obj,"not selected/render disabled")
            continue
        if obj.type == 'SPEAKER':
            if ctx.checkUpdateNeededAndClear(obj.data):
                dst_speaker = data.speakers.add()
                dst_speaker.id = ctx.idOf(obj.data)
                dst_speaker.name = obj.name
                export_audio(ctx,obj.data.sound,dst_speaker)
                dst_speaker.volume = obj.data.volume
                dst_speaker.pitch = obj.data.pitch
                dst_speaker.distance_max=obj.data.distance_max
                dst_speaker.distance_reference=obj.data.distance_reference
                dst_speaker.attenuation = obj.data.attenuation
            Relations.add(ctx,data,ctx.idOf(obj.data),  ctx.idOf(obj))
