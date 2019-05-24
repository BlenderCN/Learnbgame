bl_info = {
    "name": "Valve vmesh_c importer",
    "author": "Perry & Ricochet",
    "blender": (2, 7, 4),
    "api": 35622,
    "location": "File > Import-Export",
    "description": ("Import compiled vmesh animations."),
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

from . import vmesh_import

import bpy
from bpy.props import *

def vmeshimport( file ):
    import importlib
    importlib.reload(vmesh_import)
    print('Reloading vmesh_import...')
    vmesh_import.import_file( file )

def nameExists(name):
    exist = 0
    for object in bpy.context.scene.objects:
        if object.name == name:
            exist += 1

    return exist
    
def getInputFilename(self,filename):
    checktype = filename.split('\\')[-1].split('.')[-1]
    print ("------------",filename)
    if checktype.lower() != 'vmesh_c':
        print ("  Selected file = ",filename)
        raise (IOError, "The selected input file is not a *.vmesh_c file")
        #self.report({'INFO'}, ("Selected file:"+ filename))
    else:
        vmeshimport(filename)       
        
class IMPORT_OT_vmesh(bpy.types.Operator):
    #Import a vmesh file
    bl_idname = "import_scene.vmesh_c"
    bl_label = "Import vmesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    filepath = StringProperty(
            name="File Path",
            description="Filepath used for importing the vmsh file",
            maxlen= 1024,
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(
            default="*.vmesh_c",
            options={'HIDDEN'},
            )

    def execute(self, context):
        getInputFilename(self,self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):   
        context.window_manager.fileselect_add(self) 
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(IMPORT_OT_vmesh.bl_idname, text="Compiled vmesh (*.vmesh_c)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()