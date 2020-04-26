import bpy
import os
import subprocess
import sys

#-----GET PATH-------
def getsppath():
    fp=open(sys.argv[0]+'sppath.txt',"r")
    sppath=fp.read()
    return sppath
    
#-----START SUBSTANCE PAINTER---
def callsubstancepainter(newpath,newbl2sppath):
    if bpy.context.scene.spmeshudmi == False:
        exepath="\""+getsppath()+"\""+" --mesh "+"\""+newpath+"\""+" --export-path "+"\""+newbl2sppath+"\""+" "+"\""+newpath[:-4]+".spp"+"\""
        subprocess.Popen(exepath)
    if bpy.context.scene.spmeshudmi == True:     
        udmi=" --split-by-udim"
        exepath="\""+getsppath()+"\""+" --mesh "+"\""+newpath+"\""+" "+"\""+newpath[:-4]+".spp"+"\""+udmi+" --export-path "+"\""+newbl2sppath+"\""
        print(exepath)
        subprocess.Popen(exepath)

#-----CHANGE MESH---
def callsubstancepainterchangemesh(newpath,newbl2sppath):
    if bpy.context.scene.spmeshudmi == False:
        exepath="\""+getsppath()+"\""+" --mesh "+"\""+newpath+"\""+" "+"\""+newpath[:-4]+".spp"+"\""
        subprocess.Popen(exepath)
    if bpy.context.scene.spmeshudmi == True:
        udmi=" --split-by-udim"   
        exepath="\""+getsppath()+"\""+" --mesh "+"\""+newpath+"\""+" "+"\""+newpath[:-4]+".spp"+"\""+udmi
        subprocess.Popen(exepath)
   

#-----Creater Folder----
def createrFolder(path):
    folder = os.path.exists(path)
    if folder==False:
        os.makedirs(path)
    return path
    
    
#-----------------------------------------
class bgmbl2sp(bpy.types.Operator):
    bl_idname = "my_operator.bgmbl2sp"
    bl_label = "Blender 2 SP"
    bl_description = ""
    bl_options = {"REGISTER"}
    #-----INPUT SP EXE FILE-----
    
    @classmethod
    def poll(cls, context):
        return True
 #-----OUT PUT FILE------
    def execute(self, context):
        if bpy.context.scene.spmeshseleted==True:
            out="selectobj"
        if bpy.context.scene.spmeshseleted==False:
            out="allobj"
                
        newpath=""
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        getfilename=bpy.data.filepath.split("\\").pop()[:-6]
        bl2sppath=createrFolder(directory+"\\"+getfilename)
        newbl2sppath=createrFolder(directory+"\\"+getfilename)
        if (out=="allobj"):
            if directory=="":
                print("Please save you file") 
            if (directory!=""):                  
                    filename=bpy.context.scene.name
                    objss=bpy.context.scene.objects.active
                    newpath=bl2sppath+"\\"+getfilename+".fbx"
                    bpy.ops.export_scene.fbx(filepath=newpath, check_existing=False,
                    axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400',
                    ui_tab='MAIN', use_selection=False, global_scale=1.0, apply_unit_scale=True,
                    bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'},
                    use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False,
                    use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X',
                    use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                    bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True,
                    use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO',
                    embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                    callsubstancepainter(newpath,newbl2sppath)
        if(out=="selectobj"):              
            if directory=="":
                print("Please save you file")
            if (directory!=""):
                    filename=bpy.context.scene.name
                    objss=bpy.context.scene.objects.active
                    newpath=bl2sppath+"\\"+getfilename+"_"+objss.name+".fbx"
                    bpy.ops.export_scene.fbx(filepath=newpath, check_existing=False,
                    axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400',
                    ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True,
                    bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'},
                    use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False,
                    use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X',
                    use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                    bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True,
                    use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO',
                    embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                    callsubstancepainter(newpath,newbl2sppath)
        return {"FINISHED"}
class bgmbl2spchangemesh(bpy.types.Operator):
    bl_idname = "my_operator.bgmbl2spchangemesh"
    bl_label = "Blender 2 SP"
    bl_description = ""
    bl_options = {"REGISTER"}
    #-----INPUT SP EXE FILE-----
    
    @classmethod
    def poll(cls, context):
        return True
 #-----OUT PUT FILE------
    def execute(self, context):
        if bpy.context.scene.spmeshseleted==True:
            out="selectobj"
        if bpy.context.scene.spmeshseleted==False:
            out="allobj"
                
        newpath=""
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        getfilename=bpy.data.filepath.split("\\").pop()[:-6]
        bl2sppath=createrFolder(directory+"\\"+getfilename)
        newbl2sppath=createrFolder(directory+"\\"+getfilename)
        if (out=="allobj"):
            if directory=="":
                print("Please save you file") 
            if (directory!=""):                  
                    filename=bpy.context.scene.name
                    objss=bpy.context.scene.objects.active
                    newpath=bl2sppath+"\\"+getfilename+".fbx"
                    bpy.ops.export_scene.fbx(filepath=newpath, check_existing=False,
                    axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400',
                    ui_tab='MAIN', use_selection=False, global_scale=1.0, apply_unit_scale=True,
                    bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'},
                    use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False,
                    use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X',
                    use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                    bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True,
                    use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO',
                    embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                    callsubstancepainterchangemesh(newpath,newbl2sppath)
        if(out=="selectobj"):              
            if directory=="":
                print("Please save you file")
            if (directory!=""):
                    filename=bpy.context.scene.name
                    objss=bpy.context.scene.objects.active
                    newpath=bl2sppath+"\\"+getfilename+"_"+objss.name+".fbx"
                    bpy.ops.export_scene.fbx(filepath=newpath, check_existing=False,
                    axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400',
                    ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True,
                    bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'},
                    use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False,
                    use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X',
                    use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True,
                    bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
                    bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True,
                    use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO',
                    embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                    callsubstancepainterchangemesh(newpath,newbl2sppath)
        return {"FINISHED"}


