import bpy
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)
     
quickpose=[]


class UpdateArmature(bpy.types.Operator):
    bl_idname = "object.update_armature"
    bl_label = "Update Armature"
    bl_description = "Update the Armature"
    bl_options = {"REGISTER","UNDO"}


    def execute(self, context):
        
        armature = context.active_object
        #Suis en edit, je passe en pose, je met en rest pose et je passe en object
        bpy.ops.object.mode_set(mode='POSE')
#        bpy.ops.pose.transforms_clear()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #je selectionne la hierarchie parent et enfant
        bpy.ops.object.select_more()
        
        #je selectionne le mesh supprime le parentage
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
        bpy.ops.object.parent_clear(type='CLEAR')
        
        mesh_object = context.active_object
        #je vire l armature et les vertex groups
        bpy.ops.object.modifier_remove(modifier="Armature")
        
        obj = context.active_object
        #Remove Vgroups
        for vgroup in obj.vertex_groups:
            if vgroup.name.startswith("B"):
                obj.vertex_groups.remove(vgroup)
        
        armature.select = True
        bpy.context.scene.objects.active = armature 
        
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active=obj
        obj.select=True
        
        
        armature_mod = bpy.context.object.modifiers.get("Armature")
        if armature_mod :
            bpy.context.object.modifiers["Armature"].vertex_group = "Mask_Group"
            bpy.context.object.modifiers["Armature"].use_deform_preserve_volume = True
            bpy.context.object.modifiers["Armature"].show_in_editmode = True
            bpy.context.object.modifiers["Armature"].show_on_cage = True


        bpy.ops.object.select_all(action='DESELECT')  
        
        armature.select=True
        bpy.context.scene.objects.active = armature          
        bpy.ops.object.posemode_toggle()
        return {"FINISHED"}
    
class SymmetrizeBones(bpy.types.Operator):
    bl_idname = "object.symmetrize_bones"
    bl_label = "Symmetrize Bones"
    bl_description = "Symmetrize Bones"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.autoside_names(type='XAXIS')
        bpy.ops.armature.symmetrize()
        
        bpy.ops.object.update_armature()
        
#        bpy.ops.object.mode_set(mode='POSE')
        
        return {"FINISHED"}
        
    
# Add Mask
class QuickPoseAddMask(bpy.types.Operator):
    bl_idname = "object.quick_pose_add_mask"
    bl_label = "Quick Pose Add Mask"
    bl_description = "Add Mask to make a Quick Pose"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        obj = context.active_object
        paint = context.tool_settings.image_paint
        
        del(quickpose[:])  
        
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
        bpy.ops.paint.brush_select(sculpt_tool='MASK')

        return {"FINISHED"}
               
# Edit Mask
class EditQuickPoseMask(bpy.types.Operator):
    bl_idname = "object.edit_quick_pose_mask"
    bl_label = "Edit Quick Pose Mask"
    bl_description = "Edit the Quick Pose mask"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        
        bpy.context.object.modifiers["Armature"].show_viewport = False
        bpy.ops.object.mode_set(mode='SCULPT')
        return {"FINISHED"}
  
# Valid the Quick Pose Mask            
class ValidQuickPoseMask(bpy.types.Operator):
    bl_idname = "object.valid_quick_pose_mask"
    bl_label = "Valide Quick Pose Mask"
    bl_description = "Valid the Quick Pose mask"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        WM = bpy.context.window_manager
        
        obj_list = [obj for obj in bpy.context.selected_objects]
        obj = context.active_object
        for obj in obj_list:  
            bpy.context.scene.objects.active = obj
            obj.select = True
            
            #Remove Vgroups
            for vgroup in obj.vertex_groups:
                if vgroup.name.startswith("M"):
                    obj.vertex_groups.remove(vgroup)
            
            bpy.ops.paint.hide_show(action='HIDE', area='MASKED')

            bpy.ops.object.mode_set(mode='EDIT')
            
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.reveal()                           
            
            #Add Vgroup
            obj.vertex_groups.new("Mask_Group")
            for vgroup in obj.vertex_groups:
                if vgroup.name.startswith("M"):
                    bpy.ops.object.vertex_group_assign()
            
            bpy.ops.object.quick_pose_smooth_mask() 
            
        bpy.context.object.modifiers["Armature"].show_viewport = True         
            
        return {"FINISHED"}   

# Smooth Group
class QuickPoseSmoothMask(bpy.types.Operator):
    bl_idname = "object.quick_pose_smooth_mask"
    bl_label = "Quick Pose Smooth Mask"
    bl_description = "Smooth The Mask"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        obj = context.active_object
        for vgroup in obj.vertex_groups:
            if vgroup.name.startswith("M"):
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')

                bpy.ops.object.mode_set(mode='WEIGHT_PAINT') 
                bpy.context.object.data.use_paint_mask_vertex = True
                bpy.ops.object.vertex_group_set_active(group='Mask_Group')
                bpy.ops.object.vertex_group_select()
                bpy.ops.object.vertex_group_smooth(factor=1)
                bpy.ops.object.vertex_group_smooth(repeat=500)
                bpy.context.object.data.use_paint_mask_vertex = False
                bpy.ops.object.mode_set(mode = 'OBJECT')
        return {"FINISHED"}
       
# Create bones            
class QuickPoseCreateBones(bpy.types.Operator):
    bl_idname = "object.quick_pose_create_bones"
    bl_label = "Create Quick Pose Bones"
    bl_description = "Quick Pose Create Bones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        WM = bpy.context.window_manager
        
        for obj in bpy.context.selected_objects:
            quickpose.append(obj)
        
        if WM.use_mask:
            #Create Vgroup from mask
            obj_list = [obj for obj in bpy.context.selected_objects]
            obj = context.active_object
            for obj in obj_list:  
                bpy.context.scene.objects.active = obj
                obj.select = True
                
                #Remove Vgroups
                for vgroup in obj.vertex_groups:
                    if vgroup.name.startswith("M"):
                        obj.vertex_groups.remove(vgroup)
                
                bpy.ops.paint.hide_show(action='HIDE', area='MASKED')

                bpy.ops.object.mode_set(mode='EDIT')
                
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.reveal()  
                
                #Add Vgroup
                obj.vertex_groups.new("Mask_Group")
                for vgroup in obj.vertex_groups:
                    if vgroup.name.startswith("M"):
                        bpy.ops.object.vertex_group_assign()
                
                
                #Smooth Vertex Group
                bpy.ops.object.mode_set(mode='WEIGHT_PAINT') 
                bpy.context.object.data.use_paint_mask_vertex = True
                bpy.ops.object.vertex_group_smooth(factor=1, source='ALL')
                bpy.ops.object.vertex_group_smooth(repeat=500)
                bpy.context.object.data.use_paint_mask_vertex = False
                bpy.ops.object.mode_set(mode = 'OBJECT')        
        
        
        #Add snap Volume
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_element = 'VOLUME'
        bpy.context.scene.tool_settings.snap_target = 'MEDIAN'
            
        #Add Vertex  
        if not WM.origin:  
            bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.mesh.primitive_plane_add()
        bpy.context.active_object.name = "BS_Vertex"
        
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.merge(type='CENTER')
        
        if bpy.context.space_data.use_occlude_geometry == True :
            bpy.context.space_data.use_occlude_geometry = False
        else :
            pass
        
        
        if not WM.origin: 
            bpy.ops.transform.translate('INVOKE_DEFAULT')   
        else:
            bpy.ops.transform.translate('INVOKE_DEFAULT')
#            bpy.ops.transform.translate('INVOKE_DEFAULT', contraint_axis(False, False, True))        
#        bpy.ops.transform.translate('INVOKE_DEFAULT')
        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0
        bpy.context.space_data.cursor_location[0] = 0
        
        return {"FINISHED"}

# Convert Bones   
class QuickPoseConvertBones(bpy.types.Operator):
    bl_idname = "object.quick_pose_convert_bones"
    bl_label = "Quick PoseConvert Bones"
    bl_description = "Convert vertex to bones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        actObj = context.active_object
           
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='SKIN')
        bpy.ops.object.skin_armature_create(modifier="Skin")
        bpy.context.active_object.name = "Armature_Quick_Pose"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


        bpy.ops.object.select_all(action='DESELECT')

        actObj.select = True
        bpy.ops.object.delete()
        bpy.data.objects["Armature_Quick_Pose"].select = True
        Armature = context.active_object
            
        for obj in quickpose :
            obj.select = True 
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active=obj
            obj.select=True
            
            
            armature = bpy.context.object.modifiers.get("Armature")
            if armature :
                bpy.context.object.modifiers["Armature"].vertex_group = "Mask_Group"
                bpy.context.object.modifiers["Armature"].use_deform_preserve_volume = True
                bpy.context.object.modifiers["Armature"].show_in_editmode = True
                bpy.context.object.modifiers["Armature"].show_on_cage = True


        bpy.ops.object.select_all(action='DESELECT')  
        
        Armature.select=True
        bpy.context.scene.objects.active = Armature          
        bpy.ops.object.posemode_toggle()
        
        #Remove snap 
        bpy.context.scene.tool_settings.use_snap = False 
        return {"FINISHED"}

      
# Remove Quick Pose Modifier
class RemoveQuickPose(bpy.types.Operator):
    bl_idname = "object.remove_quick_pose_modifier"
    bl_label = "Remove Quick Pose Modifier"
    bl_description = "Remove Quick Pose Modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        act_obj = bpy.context.active_object   
        
        #Delete Armature  
        armature = bpy.context.object.modifiers.get("Armature") 
        if armature:
            bpy.ops.object.modifier_remove(modifier="Armature")
        
        #Remove Vgroups    
        bpy.ops.object.vertex_group_remove(all=True)
         
        bpy.ops.object.select_all(action='DESELECT') 
        
        #Remove quickpose
        bpy.data.objects['Armature_Quick_Pose'].select = True 
        bpy.ops.object.mode_set(mode='OBJECT')  
        bpy.ops.object.delete(use_global=False) 
        
        act_obj.select=True
        bpy.context.scene.objects.active = act_obj
           
        del(quickpose[:])           

        return {"FINISHED"}  

#apply Quick Pose
class ApplyQuickPose(bpy.types.Operator):
    bl_idname = "object.apply_quick_pose_modifier"
    bl_label = "Apply Quick Pose Modifier"
    bl_description = "Apply Quick Pose Modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        act_obj = bpy.context.active_object   
        
        #Apply Armature  
        armature = bpy.context.object.modifiers.get("Armature") 
        if armature:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Armature")
        
        #Remove Mask
        bpy.ops.object.mode_set(mode='SCULPT') 
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        bpy.ops.object.mode_set(mode='OBJECT') 
 
        #Remove Vgroups    
        bpy.ops.object.vertex_group_remove(all=True)
         
        bpy.ops.object.select_all(action='DESELECT') 
        
        #Remove quickpose
        bpy.data.objects['Armature_Quick_Pose'].select = True 
        bpy.ops.object.mode_set(mode='OBJECT')  
        bpy.ops.object.delete(use_global=False) 
        
        act_obj.select=True
        bpy.context.scene.objects.active = act_obj
           
        del(quickpose[:])           

        return {"FINISHED"} 

            
        