import bpy
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)

##------------------------------------------------------  
#
# Remesh/Decimate
#
##------------------------------------------------------ 


# Add Remesh modifier
class Remesh(bpy.types.Operator):
    bl_idname = "object.remesh"
    bl_label = "Remesh Object"
    bl_description = "Prepare object for clean remesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object          
        modcount = len(obj.modifiers)     
        
        
        bpy.ops.object.convert(target='MESH') 
        obj = context.active_object
         
        remesh = bpy.context.object.modifiers.get("R_Remesh")
        smooth = bpy.context.object.modifiers.get("R_Smooth")
        skin = bpy.context.object.modifiers.get("Skin")
        subsurf = bpy.context.object.modifiers.get("Subsurf")
        
        if not remesh:
            #Add Remesh        
            r_remesh = obj.modifiers.new("R_Remesh", 'REMESH')
            r_remesh.octree_depth = 7
            r_remesh.mode = 'SMOOTH'
            r_remesh.use_smooth_shade = True
            r_remesh.scale = 0.99
            
            #check for Skin and Apply
            if skin :
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Skin")
                if subsurf:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
                        
            if modcount :
                for i in range (modcount):
                    bpy.ops.object.modifier_move_up(modifier="R_Remesh")

        else :
            for i in range (modcount):
                bpy.ops.object.modifier_move_up(modifier="R_Remesh")
                  
        if not smooth :   
            r_smooth = obj.modifiers.new("R_Smooth", 'SMOOTH')
            r_smooth.factor = 1
            r_smooth.iterations = 10
            
            bpy.ops.object.modifier_move_down(modifier="R_Smooth")
            bpy.ops.object.modifier_move_down(modifier="R_Smooth")
            
            if modcount :
                for i in range (modcount):
                    bpy.ops.object.modifier_move_down(modifier="R_Smooth")
            
        else :
            for i in range (modcount):
                bpy.ops.object.modifier_move_down(modifier="R_Smooth")

        return {"FINISHED"}

# Remove the Remesh modifier
class RemoveRemeshSmooth(bpy.types.Operator):
    bl_idname = "object.remove_remesh_smooth"
    bl_label = "Remove Remesh Smooth"
    bl_description = "Delete the Remesh modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        remesh = bpy.context.object.modifiers.get("R_Remesh")
        smooth = bpy.context.object.modifiers.get("R_Smooth")
        if remesh and smooth:
            bpy.ops.object.modifier_remove(modifier="R_Remesh")
            bpy.ops.object.modifier_remove(modifier="R_Smooth")
            
            
        return {"FINISHED"}

# Apply the Remesh modifier
class ApplyRemeshSmooth(bpy.types.Operator):
    bl_idname = "object.apply_remesh_smooth"
    bl_label = "Apply Remesh Smooth"
    bl_description = "Apply Remesh and smooth"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        remesh = bpy.context.object.modifiers.get("R_Remesh")
        smooth = bpy.context.object.modifiers.get("R_Smooth")
        if remesh and smooth:
            bpy.ops.object.modifier_apply(modifier="R_Remesh")
            bpy.ops.object.modifier_apply(modifier="R_Smooth")

        return {"FINISHED"}

# Hide Remesh    
def HideRemeshSmooth(self, context):
    bl_description = "Hide the Remesh Modifier"
    
    if bpy.context.object.modifiers["R_Remesh"].show_viewport == True :
        bpy.context.object.modifiers["R_Remesh"].show_viewport = False
        bpy.context.object.modifiers["R_Smooth"].show_viewport = False
    else:
        bpy.context.object.modifiers["R_Remesh"].show_viewport = True
        bpy.context.object.modifiers["R_Smooth"].show_viewport = True

# Decimate     
class Decimate(bpy.types.Operator):
    bl_idname = "object.decimate"
    bl_label = "Decimate Object"
    bl_description = "Decimate for lighter object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        decimate = bpy.context.object.modifiers.get("Decimate")   
        if not decimate :   
            r_remesh = obj.modifiers.new("Decimate", 'DECIMATE') 

        return {"FINISHED"}    

# Apply Decimate
class ApplyDecimate(bpy.types.Operator):
    bl_idname = "object.apply_decimate"
    bl_label = "Apply decimate"
    bl_description = "Apply Decimate modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.context.active_object    
        
        decimate = bpy.context.object.modifiers.get("Decimate") 
        if decimate:
            bpy.ops.object.modifier_apply(modifier="Decimate")

        return {"FINISHED"}    

# Remove Decimate    
class RemoveDecimate(bpy.types.Operator):
    bl_idname = "object.remove_decimate"
    bl_label = "Remove decimate"
    bl_description = "Remove Decimate modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.context.active_object    
        
        decimate = bpy.context.object.modifiers.get("Decimate") 
        if decimate:
            bpy.ops.object.modifier_remove(modifier="Decimate")

        return {"FINISHED"}        

# Decimate Mask
class DecimateMask(bpy.types.Operator):
    bl_idname = "object.decimate_mask"
    bl_label = "Decimate Mask"
    bl_description = "Decimate the masking part"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj_list = [obj for obj in bpy.context.selected_objects]
        obj = context.active_object
        for obj in obj_list:  
            bpy.context.scene.objects.active = obj
            obj.select = True
            
            #Remove Vgroups
            for vgroup in obj.vertex_groups:
                if vgroup.name.startswith("M"):
                    obj.vertex_groups.remove(vgroup)
            
            bpy.ops.object.mode_set(mode='SCULPT')
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
                    
            bpy.ops.object.mode_set(mode='OBJECT')        
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].vertex_group = "Mask_Group"
            bpy.context.object.modifiers["Decimate"].ratio = 1
   
        return {"FINISHED"}   
  
# Edit Decimate
class EditDecimateMask(bpy.types.Operator):
    bl_idname = "object.edit_decimate_mask"
    bl_label = "Edit Decimate Mask"
    bl_description = "Edit the Decimate mask"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        
        bpy.context.object.modifiers["Decimate"].show_viewport = False
        bpy.ops.object.mode_set(mode='SCULPT')
        return {"FINISHED"}

# Valid the Decimate Mask            
class ValidDecimateMask(bpy.types.Operator):
    bl_idname = "object.valid_decimate_mask"
    bl_label = "Valide Decimate Mask"
    bl_description = "Valid the Decimate mask"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        
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
            
            bpy.context.object.modifiers["Decimate"].vertex_group = "Mask_Group"
            bpy.ops.object.mode_set(mode='OBJECT')          
            bpy.context.object.modifiers["Decimate"].show_viewport = True        
            
        return {"FINISHED"}   

# Add Mask
class AddMask(bpy.types.Operator):
    bl_idname = "object.add_mask"
    bl_label = "Add Mask"
    bl_description = "Add Mask to Decimate custom areas"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        obj = context.active_object
        paint = context.tool_settings.image_paint
        
        bpy.context.object.modifiers["Decimate"].show_viewport = False
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.brush_select(sculpt_tool='MASK')

        
        return {"FINISHED"}
        

# Remove Mask
class RemoveMask(bpy.types.Operator):
    bl_idname = "object.remove_mask"
    bl_label = "Remove Mask"
    bl_description = "Remove Mask"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        obj = context.active_object
        #Remove Vgroups
        for vgroup in obj.vertex_groups:
            if vgroup.name.startswith("M"):
                obj.vertex_groups.remove(vgroup)
        bpy.context.object.modifiers["Decimate"].vertex_group = ""
        
        return {"FINISHED"}