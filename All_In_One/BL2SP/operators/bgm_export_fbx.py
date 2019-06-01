import bpy
import os


#-----Creater Folder----
def createrFolder(path):
    folder = os.path.exists(path)
    if folder==False:
        os.makedirs(path)
    return path

#-----Creater Folder----   

class bgmexportfbx(bpy.types.Operator):
    bl_idname = "my_operator.bgmexportfbx"
    bl_label = "Bgmexportfbx"
    bl_description = ""
    bl_options = {"REGISTER"}

    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):  
        parName=bpy.context.scene.fbxcommonname
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)
        bl2sppath=createrFolder(directory+"\\bgm2FBX\\")
        objlist=bpy.context.selected_objects
        for objs in objlist:
            bpy.data.objects[objs.name].select=False
         
        for objss in objlist:
            if directory=="":
                print("Please save you file")
            if (directory!=""): 
                bpy.context.scene.objects.active = objss
        #        bpy.ops.object.duplicate(linked=False)
                
                pos=objss.location
                print("pos")
                newpos=(pos[0],pos[1],pos[2])

                obj=bpy.context.scene.objects.active
                bpy.data.objects[obj.name].select=True
                print(obj.name)
                o = obj
                vcos = [ o.matrix_world * v.co for v in o.data.vertices ]
                findCenter = lambda l: ( max(l) + min(l) ) / 2
                x,y,z  = [ [ v[i] for v in vcos ] for i in range(3) ]
                center = [ findCenter(axis) for axis in [x,y,z] ]
                #pos=obj.location
                
                
                #--------FIND CENTER---------
                obj.location=(obj.location[0]-center[0],
                (obj.location[1]-center[1]),
                (obj.location[2]-center[2])+obj.dimensions.z/2)

                bpy.ops.apply.transformall()
                #--------FIND CENTER---------
                newpath=bl2sppath+parName+objss.name+".fbx"  
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
                #--------Set POS---------
                bpy.data.objects[obj.name].location=newpos
                bpy.data.objects[obj.name].select=False
        os.system("start explorer "+bl2sppath)        
        return {"FINISHED"}
        