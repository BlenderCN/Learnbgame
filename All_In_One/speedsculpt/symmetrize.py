import bpy

from .operators import (CheckDyntopo,
                        CheckSmoothMesh)

##------------------------------------------------------  
#
# Symmetrize
#
##------------------------------------------------------   
class Symmetrize(bpy.types.Operator):
    bl_idname = "object.symmetrize"
    bl_label = "Symmetrize"
    bl_description = "Symmetrize the mesh"
    bl_options = {"REGISTER", "UNDO"}
    
    symmetrize_axis = bpy.props.EnumProperty(
        items = (('positive_x', "Positive X", ""),
                 ('negative_x', "Negative X", ""),
                 ('positive_y', "Positive Y", ""),
                 ('negative_y', "Negative Y", ""),
                 ('positive_z', "Positive Z", ""),
                 ('negative_z', "Negative A", "")),
                 default = 'positive_x'
                 )
    
    def execute(self, context):
        WM = context.window_manager
        toolsettings = context.tool_settings
        sculpt = toolsettings.sculpt

        #Sculpt
        if bpy.context.object.mode == "SCULPT":
            
            #check Symmetrize
            if self.symmetrize_axis == 'positive_x':
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                    bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'POSITIVE_X'
                    bpy.ops.sculpt.symmetrize()
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_X')
                
            elif self.symmetrize_axis == 'negative_x':
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                    bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'NEGATIVE_X'
                    bpy.ops.sculpt.symmetrize()
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.symmetrize(direction='NEGATIVE_X')
                    
            elif self.symmetrize_axis == 'positive_y':
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                    bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'POSITIVE_Y'
                    bpy.ops.sculpt.symmetrize()
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_Y')
                     
            elif self.symmetrize_axis == 'negative_y':
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                    bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'NEGATIVE_Y'
                    bpy.ops.sculpt.symmetrize()
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.symmetrize(direction='NEGATIVE_Y') 
                      
            elif self.symmetrize_axis == 'positive_z':
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                    bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'POSITIVE_Z'
                    bpy.ops.sculpt.symmetrize()
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_Z')
                      
            elif self.symmetrize_axis == 'negative_z':
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
                    bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'NEGATIVE_Z'
                    bpy.ops.sculpt.symmetrize()
                else:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.symmetrize(direction='NEGATIVE_Z')
                      
                      
            bpy.ops.object.mode_set(mode = 'SCULPT')
                
                
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.mode_set(mode = 'SCULPT')
            
            #Update Detail Flood fill
            if WM.update_detail_flood_fill :
                if bpy.context.sculpt_object.use_dynamic_topology_sculpting :       
                    bpy.ops.sculpt.detail_flood_fill()
                    bpy.ops.sculpt.optimize()
            else :
                pass
            
            CheckSmoothMesh()
            bpy.ops.object.mode_set(mode = 'SCULPT')
            
        #Object    
        elif bpy.context.object.mode == "OBJECT":
            for obj in bpy.context.selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active=obj
                obj.select=True
                
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                
                #check Symmetrize
                if self.symmetrize_axis == 'positive_x':
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_X')
                elif self.symmetrize_axis == 'negative_x':
                    bpy.ops.mesh.symmetrize(direction='NEGATIVE_X')
                elif self.symmetrize_axis == 'positive_y':
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_Y')  
                elif self.symmetrize_axis == 'negative_y':
                    bpy.ops.mesh.symmetrize(direction='NEGATIVE_Y')   
                elif self.symmetrize_axis == 'positive_z':
                    bpy.ops.mesh.symmetrize(direction='POSITIVE_Z')  
                elif self.symmetrize_axis == 'negative_z':
                    bpy.ops.mesh.symmetrize(direction='NEGATIVE_Z')         
                
                bpy.ops.object.mode_set(mode = 'OBJECT')
                
                CheckDyntopo()
                bpy.ops.object.mode_set(mode = 'OBJECT')
  
                CheckSmoothMesh()
                
            for obj in bpy.context.selected_objects:    
                obj.select=True
                
        return {"FINISHED"}