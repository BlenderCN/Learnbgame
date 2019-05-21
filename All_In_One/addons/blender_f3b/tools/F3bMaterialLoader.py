import bpy,re,os;
from bpy_extras.io_utils import ExportHelper;
from bpy.props import StringProperty, BoolProperty, EnumProperty;
from bpy.types import Operator;
from bpy.types import Menu, Panel, UIList,UILayout

EXPORTABLE_MAT_PATTERN=re.compile("\\!\s*([^;]+)")
EXPORTABLE_INPUT_PATTERN=re.compile("\\!\s*([^;]+)")
SRGB_PATTERN=re.compile("[ ,]srgb\s*=\s*\'([^']+)")

FORMAT_EXT={
    "bmp":"bmp",
    "dds":"dds",
    "hdr":"hdr",
    "targa":"tga",
    "jpeg":"jpg",
    "targa_raw":"tga",
    "targa":"tga",
    "png":"png"
}


def listF3bMaterials():
    f3bmaterials=[]
    for ng in bpy.data.node_groups:
        matname=ng.name
        if EXPORTABLE_MAT_PATTERN.match(matname):
            f3bmaterials.append(matname)  
    return f3bmaterials


def findF3bMaterial(intree,filter):
    output=None
    for  n in intree.nodes:
        if (isinstance(n,bpy.types.ShaderNodeOutputMaterial)):
            output=n
            break
    if output:
        print("Found output "+str(n))
    else:
        print("No output found, add.")
        output=intree.nodes.new('ShaderNodeOutputMaterial')
    matnode=output.inputs[0].links[0].from_node if len(output.inputs[0].links) > 0 else None
    if matnode!=None and isinstance(matnode, bpy.types.ShaderNodeGroup) and EXPORTABLE_MAT_PATTERN.match(matnode.node_tree.name) and (filter==None or filter==matnode.node_tree.name):
        return [matnode,output ]
    else:
        return [None,output ]
    
        

def selectMaterial(node_tree,mat):
    cmat,out=findF3bMaterial(node_tree,mat)
    if cmat:
        print("Found material node "+str(cmat))
        return cmat
    else:
        print("Material node not found, create a new one")
        matnode=node_tree.nodes.new('ShaderNodeGroup')
        matnode.node_tree=bpy.data.node_groups[mat]
        node_tree.links.new(matnode.outputs[0], out.inputs[0]);       
        return matnode
    
    
def loadImages(material,path,inputs):
    for input_name,input in inputs:
        if not input.type=="RGBA": continue
        issrgb=SRGB_PATTERN.search(input_name)
        if issrgb:
            issrgb=issrgb.group(1)=="true"
        else: issrgb=False
        
        input_name=input_name.split("+")[0]
        input_name= input_name.strip()
        

        for i in range(0,2):
            found=False
            file_name=material.name
         
            if i == 1 and file_name.endswith("_Mat"):
                file_name=file_name[:-len("_Mat")]
            file_name+="_"+input_name
            file_path=path+file_name
        
            for k in FORMAT_EXT:
                ext=FORMAT_EXT[k]
                file=file_path+"."+ext
                #print("Search "+file)
                if os.path.isfile(file):
                    print("Set "+input_name+" srgb "+str(issrgb))
                    bimg=None                    
                    if input.is_linked and input.links[0].from_node.type == "TEX_IMAGE":
                        bimg=input.links[0].from_node;                                        
                    else:
                        bimg=material.node_tree.nodes.new('ShaderNodeTexImage')
                        material.node_tree.links.new(bimg.outputs[0], input);                                        
                    bimg.image=bpy.data.images.load(file)
                    bimg.image.name=file_name
                    bimg.color_space="COLOR" if issrgb else "NONE"                
                    found=True
                    break
            if found: break
            

def loadParam(material,input_name,input,type,value):
    matnode=material.node_tree.nodes.new('ShaderNodeGroup')
    matnode.node_tree=bpy.data.node_groups[type]
    material.node_tree.links.new(matnode.outputs[0], input);           

def loadParams(material,path,inputs):
    for input_name,input in inputs:        
        input_name=input_name.split("+")[0]
        input_name= input_name.strip()

        for i in range(0,2):
            file_name=material.name
            if i == 1 and file_name.endswith("_Mat"):
                file_name=file_name[:-len("_Mat")]
                
            file_name+="_"+input_name
            file_path=path+file_name
            
            file=file_path+".param"
            #print("Set "+file)
            if os.path.isfile(file):
                type=None
                value=None
                with open(file,'r') as f:
                    parts=f.read().split(":")
                    if len(parts)>0: type=parts[0].strip()
                    if len(parts)>1: value=parts[1].strip()
                print("Set "+input_name+" -> "+str(type)+" ("+str(value)+")")        
                loadParam(material,input_name,input,type,value)                
                break    

def run(path,mat):
    for  obj in bpy.context.scene.objects:
        if obj.select_get():
            for  i in range(0,len(obj.material_slots)):
                material=obj.material_slots[i].material
                if(not material):
                    continue
                material.use_nodes=True
                matnode=selectMaterial(material.node_tree,mat)
                if path:
                    f3binputs=[]
                    for input in matnode.inputs:
                        input_name=EXPORTABLE_INPUT_PATTERN.match(input.name)
                        if input_name:
                            f3binputs.append([input_name.group(1),input])                            
                    loadImages(material,path,f3binputs)
                    loadParams(material,path,f3binputs)
                    
                            
class F3B_TOOLS_material_load(Operator, ExportHelper):
    bl_idname = "f3btools.material_load"
    bl_label = "Select textures path"
    filename_ext = ""
    
    use_filter_folder = True
    selected_mat = bpy.props.StringProperty('!cr/Forward/PBR/PBR.j3md; CR_PBR') # TODO: Different default

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
        
    
    def execute(self, context):
        path=self.filepath
        if (not os.path.isdir(path)):
            path=os.path.split(os.path.abspath(path))[0]+os.path.sep
        print("Use "+self.selected_mat)
        run(path,self.selected_mat) 
        return {"FINISHED"}
        

class F3B_TOOLS_material_list(Operator):
    bl_idname = "f3btools.material_list"
    bl_label = "Load material"

    def listmat(self,context):
        mats=listF3bMaterials()
        out=[]
        for m in mats:
            out.append((m,m,m))
        return out

    mats: bpy.props.EnumProperty(
        items=listmat
    )
    
    def execute(self, context):
        bpy.ops.f3btools.material_load('INVOKE_DEFAULT',selected_mat=self.mats)
        return{'FINISHED'}

class F3B_TOOLS_PT_material_panel(Panel):
    bl_label = "F3b Material"
    bl_idname = "F3B_TOOLS_PT_material_panel"
    bl_context = "material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw(self, context):
        self.layout.operator_menu_enum(F3B_TOOLS_material_list.bl_idname, property="mats",text="Load Material")

def register():
    bpy.utils.register_class(F3B_TOOLS_material_list)
    bpy.utils.register_class(F3B_TOOLS_PT_material_panel)
    bpy.utils.register_class(F3B_TOOLS_material_load)
      

def unregister():
    bpy.utils.unregister_class(F3B_TOOLS_material_list)
    bpy.utils.unregister_class(F3B_TOOLS_PT_material_panel)
    bpy.utils.unregister_class(F3B_TOOLS_material_load)
