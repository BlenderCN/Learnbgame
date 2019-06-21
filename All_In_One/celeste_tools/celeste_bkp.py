import bpy
import os

# OPERADOR DUMMY
def saveBkp (self, context):
    #sin version a versionada
    if not bpy.data.filepath.count("_v"): 
        filelist = [file  for file in os.listdir("%s/VERSIONS/" % (os.path.dirname(bpy.data.filepath))) if file.count("_v") and not file.count("blend1")] 

        filelower = 0
        print(filelist)
        for file in filelist:
            if int(file.split(".")[0][-2:]) > filelower:
                filelower = int(file.split(".")[0][-2:])        

        savepath = "%s/VERSIONS/%s_v%02d.blend" % (os.path.dirname(bpy.data.filepath),bpy.path.basename(bpy.data.filepath).split('.')[0],filelower+1)   
        print("Copia versionada guardada.")   
        bpy.ops.wm.save_as_mainfile()
        bpy.ops.wm.save_as_mainfile(filepath=savepath, copy=True)        

    else:        
        #versionada a sin version
        if bpy.data.filepath.count("_v"):
            filename = "%s/../%s.blend" % (os.path.dirname(bpy.data.filepath),os.path.basename(bpy.data.filepath).rpartition(".")[0].rpartition("_")[0])
            print(filename)
            bpy.ops.wm.save_as_mainfile(filepath=filename, copy=True)       
        print("Copia sin version guardada.")


class CelesteSaveBkp (bpy.types.Operator):
    """Create a new Mesh Object"""
    bl_idname = "file.celeste_save_bkp"
    bl_label = "Celeste Save Backup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        saveBkp(self, context)
        return {'FINISHED'}

    
