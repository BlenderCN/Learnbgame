# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Export Import txt raw meshes.",
    "author": "Oscurart",
    "version": (1,3),
    "blender": (2, 6, 2),
    "api": 44400,
    "location": "Import/Export > Raw Meshes",
    "description": "Export and import txt with raw meshes data.",
    "warning": "",
    "wiki_url": "oscurart.blogspot.com",
    "tracker_url": "",
    "category": "Learnbgame",
}




import bpy

## FUNCION EXPORTADORA ------------------------------------------------
def ot_export_raw_meshes (context, filepath, WHOLE):
    for objeto in bpy.context.selected_objects:
        
        if WHOLE == True:
            FILEOUTPUT=filepath.rpartition("/")[0]+ "/"+objeto.name+".txt"
        else:
            FILEOUTPUT=filepath.rpartition("/")[0]+ "/"+objeto.name+"_"+filepath.rpartition("/")[-1]
            
        open(FILEOUTPUT,"w")
        FILE=open(  FILEOUTPUT,"w")
        VERTICESLISTA=[]
        EDGELISTA=[]
        FACELISTA=[]
        UVLISTA=[]
        

        #LISTA PARA VERTICES / CREO UN STRING Y LO CONVIERTO A LIST PARA SUMAR A VERTICESLISTA
        for VERT in objeto.data.vertices[:]:
            VERTEMP="(%s,%s,%s)"  % (VERT.co[0],VERT.co[1],VERT.co[2])        
            VERTICESLISTA.append(tuple(eval(VERTEMP)))

        for FACE in objeto.data.polygons[:]:
            FACETEMP=FACE.vertices[:]
            FACELISTA.append(FACETEMP)

        #LISTA PARA UVS
        
        for LAYER in objeto.data.uv_loop_layers[:]:
            LAYERTEMP=[]
            for DATA in LAYER.data[:]:
                DATATEMP=tuple(eval("(%s,%s)" % (DATA.uv[0],DATA.uv[1])))
                LAYERTEMP.append(DATATEMP)    
            UVLISTA.append(LAYERTEMP)
        
        MIXLIST=[]
        MIXLIST.append(VERTICESLISTA)
        MIXLIST.append(EDGELISTA)
        MIXLIST.append(FACELISTA)
        MIXLIST.append(UVLISTA)

        FILE.writelines(str(MIXLIST))
        # CIERRO ARCHIVO
        FILE.close()             

    return {'FINISHED'}



## FUNCION IMPORTADORA ------------------------------------------------
def ot_import_raw_meshes (context, filepath, WHOLE):
    FILEOUTPUT=filepath
    ARCHIVO=open(FILEOUTPUT,"r")
    PYRAW=ARCHIVO.readlines(0)
    VERTLIST=[]
    PYDATA=eval(PYRAW[0])
    
    objeto=filepath.rpartition("/")[-1].rpartition(".")[0]
    


    # CREO DATA
    MESH=bpy.data.meshes.new(objeto+"data")
    OBJETO=bpy.data.objects.new(objeto,MESH)    
    
    MESH.from_pydata(
        PYDATA[0],
        PYDATA[1],
        PYDATA[2]
    )   
    
    # LINKEO OBJETO
    bpy.context.scene.objects.link(OBJETO)
    MESH.update()
    

    # CREAMOS UVS
    # OBJETO ACTIVO
    bpy.context.scene.objects.active=OBJETO
    OBJETO.select=1
    
    for UV in range(len(PYDATA[-1])):
        bpy.ops.mesh.uv_texture_add()
        
   
    LAYERINDEX=0
    #LISTA PARA UVS    
    for LAYER in PYDATA[-1]: 
        DATAINDEX=0       
        for UV in LAYER:
            OBJETO.data.uv_loop_layers[LAYERINDEX].data[DATAINDEX].uv=UV
            DATAINDEX+=1
        LAYERINDEX+=1      
        
       

    
    print("Object : "+str(objeto))
    
    # CIERRO EL ARCHIVO
    ARCHIVO.close()          
    
    return {'FINISHED'}



## CLASES ===============================================================

## IMPORTO LIBRERIAS
from bpy_extras.io_utils import ExportHelper


## REGISTRA CLASE DE EXPORTACION -------------------------------
class OTExportRawMeshes(bpy.types.Operator, ExportHelper):
    '''This appears in the tooltip of the operator and in the generated docs.'''
    bl_idname = "export.raw_meshes"
    bl_label = "Export Raw Meshes"
    filename_ext = ".txt"
    filter_glob = bpy.props.StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )
            
    use_setting = bpy.props.BoolProperty(
            name="Whole directory",
            description="Export the selected objects in this folder",
            default=True,
            )

    @classmethod
    def poll(cls, context):
        return context.active_object.type == "MESH"

    def execute(self, context):
        return ot_export_raw_meshes(context, self.filepath, self.use_setting)


## REGISTRA CLASE DE IMPORTACION -----------------------------------
class OTImportRawMeshes(bpy.types.Operator, ExportHelper):
    '''This appears in the tooltip of the operator and in the generated docs.'''
    bl_idname = "import_scene.raw_meshes"
    bl_label = "Import Raw Meshes"
    filename_ext = ".txt"
    filter_glob = bpy.props.StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )
            
    use_setting = bpy.props.BoolProperty(
            name="Whole directory",
            description="Import the selected objects in this folder",
            default=True,
            )
    """
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    """
    def execute(self, context):
        return ot_import_raw_meshes(context, self.filepath, self.use_setting)



# MENUES DINAMICOS
def menu_export_raw_meshes(self, context):
    self.layout.operator(OTExportRawMeshes.bl_idname, text="Raw Meshes", icon ='PLUGIN')
def menu_import_raw_meshes(self, context):
    self.layout.operator(OTImportRawMeshes.bl_idname, text="Raw Meshes", icon ='PLUGIN')

def register():
    bpy.utils.register_class(OTExportRawMeshes)
    bpy.utils.register_class(OTImportRawMeshes)
    bpy.types.INFO_MT_file_export.append(menu_export_raw_meshes)
    bpy.types.INFO_MT_file_import.append(menu_import_raw_meshes)

def unregister():
    bpy.utils.unregister_class(OTExportRawMeshes)
    bpy.utils.unregister_class(OTImportRawMeshes)
    bpy.types.INFO_MT_file_export.remove(menu_export_raw_meshes)
    bpy.types.INFO_MT_file_import.remove(menu_import_raw_meshes)


if __name__ == "__main__":
    register()

