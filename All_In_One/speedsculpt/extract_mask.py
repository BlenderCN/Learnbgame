import bpy
import bmesh
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)

##------------------------------------------------------  
#
# Extract Mask
#
##------------------------------------------------------ 
bpy.types.WindowManager.ref_obj = bpy.props.StringProperty()
#Cut
class Cut_By_Mask(bpy.types.Operator):
    bl_idname = "object.cut_by_mask"
    bl_label = "Cut By Mask"
    bl_description = "Cut By Mask"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.active_object
        WM = context.window_manager
        
        #Ref object name
        context.window_manager.ref_obj = context.active_object.name 
        ref_obj = bpy.context.window_manager.ref_obj 
        
        # Go in object duplicate and deselect faces
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate_move()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # hide non masked faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')

        # Go in edit and delete those faces of the second object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.delete(type='FACE')

        # Go in sculpt and unhide faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='SHOW', area='ALL')
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        bpy.ops.object.mode_set(mode='OBJECT') 
        
        #select the first object
        bpy.context.scene.objects.active = bpy.data.objects[ref_obj] 
        bpy.data.objects[ref_obj].select = True
        
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.mask_flood_fill(mode='INVERT')

        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
        # Go in edit and delete those faces
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.delete(type='FACE')
        # Go in sculpt and unhide faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='SHOW', area='ALL')
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        bpy.ops.object.mode_set(mode='OBJECT') 
        
        bpy.ops.object.update_dyntopo() 
        #Comme Back in Sculpt mode    
        if WM.comeback_in_sculpt_mode :
            bpy.ops.object.mode_set(mode='SCULPT')
            if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                pass
            else :
                bpy.ops.sculpt.dynamic_topology_toggle()  
        return {"FINISHED"}
        

#Duplicate
class Duplicate_By_Mask(bpy.types.Operator):
    bl_idname = "object.duplicate_by_mask"
    bl_label = "Duplicate By Mask"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        WM = context.window_manager
        
        # Go in object duplicate and deselect faces
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate_move()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        # hide non masked faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
        # Go in edit and delete those faces
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.delete(type='FACE')
        # Go in sculpt and unhide faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='SHOW', area='ALL')
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        bpy.ops.object.mode_set(mode='OBJECT') 

        bpy.ops.object.update_dyntopo() 
        #Comme Back in Sculpt mode    
        if WM.comeback_in_sculpt_mode :
            bpy.ops.object.mode_set(mode='SCULPT')
            if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                pass
            else :
                bpy.ops.sculpt.dynamic_topology_toggle()  
#        bpy.ops.object.mode_set(mode='SCULPT') 
        return {"FINISHED"}

#Delete
class Delete_By_Mask(bpy.types.Operator):
    bl_idname = "object.delete_by_mask"
    bl_label = "Delete By Mask"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        # hide non masked faces
        bpy.ops.paint.mask_flood_fill(mode='INVERT')
        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
        
        # Go in edit and delete those faces
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.delete(type='FACE')
        
        # Go in sculpt and unhide faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='SHOW', area='ALL')
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.update_dyntopo()  
        bpy.ops.object.mode_set(mode='SCULPT') 
        
        return {"FINISHED"}


#Extract
class ExtractMask(bpy.types.Operator):
    bl_idname = "object.extract_mask"
    bl_label = "Extract Mask"
    bl_description = "Extract the mask to create a new object"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        solidify_thickness = bpy.context.window_manager.solidify_thickness
        solidify_offset = bpy.context.window_manager.solidify_offset
        rim_only = bpy.context.window_manager.rim_only
        WM = context.window_manager
        
        # Go in object duplicate and deselect faces
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate_move()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        # hide non masked faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
        # Go in edit and delete those faces
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.delete(type='FACE')
        # Go in sculpt and unhide faces
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='SHOW', area='ALL')
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        bpy.ops.object.mode_set(mode='OBJECT') 
        
        #Add Solidify with options
        if WM.add_solidify :
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].offset = solidify_offset
            bpy.context.object.modifiers["Solidify"].use_even_offset = True
            bpy.context.object.modifiers["Solidify"].use_quality_normals = True
            bpy.context.object.modifiers["Solidify"].thickness = solidify_thickness
            bpy.context.object.modifiers["Solidify"].use_rim_only = rim_only

            if WM.apply_solidify:
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
                bpy.ops.object.update_dyntopo()
            
        #Comme Back in Sculpt mode    
        if WM.comeback_in_sculpt_mode :
            bpy.ops.object.mode_set(mode='SCULPT')
            if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                pass
            else :
                bpy.ops.sculpt.dynamic_topology_toggle() 
        
#        if WM.update_dyntopo:
#            bpy.ops.object.update_dyntopo()        
                   
        return {"FINISHED"}

# Go in Sculpt to add Mask
class AddExtractMask(bpy.types.Operator):
    bl_idname = "object.add_extract_mask"
    bl_label = "Add Mask"
    bl_description = "Add a mask to the object"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.brush_select(sculpt_tool='MASK')

        return {"FINISHED"}
        
                        