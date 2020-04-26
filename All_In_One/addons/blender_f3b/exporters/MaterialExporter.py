import re,os

import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from . import Relations
from ..F3bContext import *
from ..Utils import *
from .. import Logger as log
from .. import DDSWriter
import shutil
import hashlib


CONVERT_TO_DDS_QUEUE=[]

CYCLES_EXPORTABLE_MATS_PATTERN=re.compile("\\!\s*([^;]+)")
CYCLES_MAT_INPUT_PATTERN=re.compile("\\!\s*([^;]+)")
CYCLES_CUSTOM_NODEINPUT_PATTERN=re.compile("([^;]+)")
               
EXT_FORMAT_MAP={"targa":"tga","jpeg":"jpg","targa_raw":"tga"}
             

def exportDDSs():
    if len(CONVERT_TO_DDS_QUEUE) == 0: return
    BATCH_SIZE=8 
    ii=0
    while True:
        xinputs=""
        xoutputs=""
        xformats=""
        xsrgb=""
        n=BATCH_SIZE
        if len(CONVERT_TO_DDS_QUEUE)<n:
            n=len(CONVERT_TO_DDS_QUEUE)
        for fi in range(0,n):
            f=CONVERT_TO_DDS_QUEUE[ii]
            if xinputs!="":
                xinputs+=","
            xinputs+=f[1]
            if xoutputs!="":
                xoutputs+=","
            xoutputs+=f[2]
            if xformats!="":
                xformats+=","
            xformats+=f[0]
            if xsrgb!="":
                xsrgb+=","
            xsrgb+=("true" if f[3] else "false")
            ii+=1
            if ii==len(CONVERT_TO_DDS_QUEUE):
                break
        DDSWriter.export(xformats,xsrgb,xinputs,xoutputs)
        if ii==len(CONVERT_TO_DDS_QUEUE):
            break 
    for f in CONVERT_TO_DDS_QUEUE:
        try:
            chash_file=f[1]+".dds.exp_hash"
            os.rename(chash_file+".temp",chash_file)
            os.remove(f[1]) 
        except: pass

def export_tex(ctx, solid,args,src, dst):
    base_name=src.name
    ext="."+src.file_format.lower()
    if ext == ".":
        ext="."+src.filepath.lower().split(".")[-1]
    if ext == "":
        ext="."+src.filepath_raw.lower().split(".")[-1]
    if ext == "":
        ext="."+src.name.lower().split(".")[-1]
    pext=ext[1:]
    if pext in EXT_FORMAT_MAP:
        ext="."+EXT_FORMAT_MAP[pext]

    origin_file=bpy.path.abspath(src.filepath) 
    print("Base texture name",base_name,"assets path",ctx.topath)
    output_file=os.path.join(ctx.topath,"Textures",base_name)+ext  
    print("Write texture in",output_file)

    output_parent=os.path.dirname(output_file)
        
    is_packed=src.packed_file
    dst.id = ctx.idOf(src)

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

        toDDS=not ext==".dds" and ctx.cfg.optionToDDS

        if toDDS: 
            chash=""
            chash_file=output_file+".dds.exp_hash"

            print("Read previous hash "+chash_file)
            if os.path.exists(chash_file):
                with open(chash_file,'r') as f:
                    chash=f.read().strip()
            print(chash)

            print("Read current hash from "+output_file)
            exphash=hashlib.sha256()
            with open(output_file,'rb') as f:
                while True:
                    data = f.read(65536)
                    if not data:
                        break
                    exphash.update(data)
            exphash=str(exphash.hexdigest())
            print(exphash)


            if exphash != chash:       
                with open(chash_file+".temp",'w') as f:
                    f.write(exphash)

                print("Convert to DDS")  
                dds_file=os.path.join(ctx.topath,"Textures",base_name)+".dds"       
                dds_args=args
                format =None
                srgb=False
                if "dds{" in dds_args:
                    dds_args=dds_args[dds_args.index("dds{")+4:]
                    dds_args=dds_args[:dds_args.index("}")]
                    dds_args=dds_args.split(",")
                    for dds_arg in dds_args:
                        key,value=dds_arg.split("=")
                        key=key.strip()
                        if key=="solid" and solid and value!=None:      
                            format=value.replace("'","").strip()
                        elif key=="alpha" and not solid and value!=None:
                            format=value.replace("'","").strip()
                        elif key=="srgb":
                            srgb=True

                if format==None:
                    format="UNCOMPRESSED"
                if srgb:
                    print("Use SRGB")

                format=format.upper()
            
                if format=="ATI2" or format=="3DC":
                    format="ATI_3DC"
                elif format=="DXT1" or format=="DXT3" or format=="DXT5":
                    format="S3TC_"+format
                elif format=="UNCOMPRESSED":
                    format="ARGB8"
                CONVERT_TO_DDS_QUEUE.append((format,output_file,dds_file,srgb))
            else:
                print("Already converted to DDS. Skip")              
                os.remove(output_file)

    else:
        print(base_name,"already up to date")

    if ctx.cfg.optionToDDS:  ext=".dds"
    dst.rpath = "Textures/"+base_name+ext
    print("Set rpath to", dst.rpath)
        
def parseNode(ctx: F3bContext,input_node,input_type,dst_mat,input_label):                    
    #input_node=input.links[0].from_node
    #input_type=input_node.type      
    parts=input_label.split("+")
    input_label=parts[0]
    args=parts[1] if len(parts)>1 else ""
    input_label=input_label.strip()

    if input_type=="RGB" or input_type=="RGBA":
        prop=dst_mat.properties.add()
        prop.id=input_label
        cnv_color(input_node.outputs[0].default_value,prop.vcolor)
        print("Found color",prop.vcolor)
    # Deprecated:  Use custom Float and Int nodes instead
    #elif input_type=="VALUE":
    #    prop=dst_mat.properties.add()
    #    prop.id=input_label
    #    prop.value=input_node.outputs[0].default_value
    #    print("Found value",prop.value)
    elif input_type=="TEXTURE":
        prop=dst_mat.properties.add()
        prop.id=input_label
        export_tex(ctx,True,args,input_node.texture.image,prop.texture)
        print("Found texture")
    elif input_type=="TEX_IMAGE":
        prop=dst_mat.properties.add()
        prop.id=input_label
        solid=len(input_node.outputs[1].links)==0 #If alpha is not connected= solid
        export_tex(ctx,solid,args,input_node.image,prop.texture)
        print("Found texture")
    elif input_type=="GROUP": # Custom nodes groups as input
        name=input_node.node_tree.name
        name=CYCLES_CUSTOM_NODEINPUT_PATTERN.match(name)
        if name != None:
            name=name.group(0).upper()
            if name == "VEC3":
                x,y,z=input_node.inputs
                x=x.default_value
                y=y.default_value
                z=z.default_value
                prop=dst_mat.properties.add()
                prop.id=input_label
                cnv_vec3((x,y,z), prop.vvec3)
                print("Found vec3",prop.vvec3)
            elif name == "VEC2":
                x,y=input_node.inputs
                x=x.default_value
                y=y.default_value
                prop=dst_mat.properties.add()
                prop.id=input_label
                cnv_vec2((x,y), prop.vvec2)
                print("Found vec2",prop.vvec2)
            elif name == "VEC4" or name == "QTR":
                x,y,z,w=input_node.inputs
                x=x.default_value
                y=y.default_value
                z=z.default_value
                w=w.default_value
                prop=dst_mat.properties.add()
                prop.id=input_label
                cnv_vec4((x,y,z,w), prop.vvec4 if name == "QTR" else prop.vqtr)
                print("Found vec4",prop.vvec4)
            elif name=="RGBA":
                r,g,b,a=input_node.inputs
                
                r=r.default_value
                g=g.default_value
                b=b.default_value
                a=a.default_value
                
                prop=dst_mat.properties.add()
                prop.id=input_label
                cnv_color((r,g,b,a),prop.vcolor)
                print("Found color",prop.vcolor)
            elif name == "FLOAT":
                prop=dst_mat.properties.add()
                prop.id=input_label            
                prop.vfloat=float(input_node.inputs[0].default_value)
                print("Found Float",prop.vfloat)
            elif name == "INT":
                prop=dst_mat.properties.add()
                prop.id=input_label            
                prop.vint=int(input_node.inputs[0].default_value)
                print("Found Int",prop.vint)
            elif name == "TRUE":
                prop=dst_mat.properties.add()
                prop.id=input_label            
                prop.vbool=True
                print("Found boolean TRUE")
            elif name == "FALSE":
                prop=dst_mat.properties.add()
                prop.vbool=False     
                prop.id=input_label     
                print("Found boolean FALSE")          
            elif name == "PRESET":
                for n in input_node.outputs[0].links[0].from_node.node_tree.nodes:
                    if n.type=="GROUP_OUTPUT":
                        input_node=n.inputs[0].links[0].from_node
                        input_type=input_node.type
                        print("Found preset")
                        parseNode(ctx,input_node,input_type,dst_mat,input_label)
                        print("Preset end")
                        break    
            else: 
                print(input_type,"not supported [1]",name)
    else: 
        print(input_type,"not supported")


def dumpCyclesExportableMats(intree,outarr,parent=None):
    if intree==None: return
    name=intree.name
    name_match=CYCLES_EXPORTABLE_MATS_PATTERN.match(name)
    if name_match!=None and intree!=None:
        material_path=name_match.group(1)
        mat=parent
        outarr.append([material_path,mat])
    if isinstance(intree, bpy.types.NodeTree):        
        for node in intree.nodes:
            dumpCyclesExportableMats(node,outarr,intree) 
    try:             
        dumpCyclesExportableMats(intree.node_tree,outarr,intree)
    except: pass





def export_material(ctx: F3bContext,src_mat, dst_mat):
    dst_mat.id = ctx.idOf(src_mat)
    dst_mat.name = src_mat.name
    cycles_mat=[]
    dumpCyclesExportableMats(src_mat.node_tree,cycles_mat)
    if len(cycles_mat)>0: 
        dst_mat.mat_id,cycles_mat=cycles_mat[0]
        dst_mat.name=src_mat.name
        for input in cycles_mat.inputs:
            input_label=input.name
            input_label=CYCLES_MAT_INPUT_PATTERN.match(input_label)
            if input_label == None:
               print("Skip ",input.name)                
            else:
                input_label=input_label.group(1)
                print("Export ",input_label)
                input_label=input_label.strip()
                if len(input.links) > 0: 
                    input_node=input.links[0].from_node
                    input_type=input_node.type    
                    parseNode(ctx,input_node,input_type,dst_mat,input_label)
                

def resetDDSConversionQueue():
    global CONVERT_TO_DDS_QUEUE
    CONVERT_TO_DDS_QUEUE=[]

def export(ctx: F3bContext,data: f3b.datas_pb2.Data,scene: bpy.types.Scene):
    resetDDSConversionQueue()
    for obj in scene.objects:
        if not ctx.isExportable(obj):
            continue
        if obj.type == 'MESH':
            for i in range(len(obj.material_slots)):
                src_mat = obj.material_slots[i].material
                if  ctx.checkUpdateNeededAndClear(src_mat):
                    dst_mat = data.materials.add()
                    export_material(ctx,src_mat, dst_mat)
    if ctx.cfg.optionToDDS: exportDDSs()
    resetDDSConversionQueue()

    