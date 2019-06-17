import bpy
from bpy.types import Operator, Macro
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)

#pour sauver le tmp
from os.path import isfile, join
import os
from os import remove, listdir
from .functions import *

import bmesh

##------------------------------------------------------  
#
# Save Tmp
#
##------------------------------------------------------  
def save_tmp():
    """ Save the current blend in the blender tmp file """
 
    tmp_file = bpy.context.user_preferences.filepaths.temporary_directory
    if isfile(join(tmp_file, "speedsculpt_backup.blend")):
        os.remove(join(tmp_file, "speedsculpt_backup.blend"))
 
    bpy.ops.wm.save_as_mainfile(
        filepath = join(tmp_file, "speedsculpt_backup.blend"),
        copy = True
        )                           
##------------------------------------------------------  
#
# Check Options
#
##------------------------------------------------------      

#Dyntopo
def CheckDyntopo():
    update_detail_flood_fill = get_addon_preferences().update_detail_flood_fill
    flat_shading = get_addon_preferences().flat_shading
    
    #Check modes
    constant = False
    relative = False
    brush = False
    if bpy.context.scene.tool_settings.sculpt.detail_type_method == 'CONSTANT':
        constant = True
    elif bpy.context.scene.tool_settings.sculpt.detail_type_method == 'BRUSH':
        brush = True
    elif bpy.context.scene.tool_settings.sculpt.detail_type_method == 'RELATIVE':
        relative = True
          
    subdiv_collapse = False
    collapse = False
    subdivide = False
    if bpy.context.scene.tool_settings.sculpt.detail_refine_method == 'SUBDIVIDE':
        subdivide = True
    elif bpy.context.scene.tool_settings.sculpt.detail_refine_method == 'COLLAPSE':
        collapse = True
    elif bpy.context.scene.tool_settings.sculpt.detail_refine_method == 'SUBDIVIDE_COLLAPSE':
        subdiv_collapse = True
        
#++++++++++++++++++++++++++++++++++++        
    #Add detail flood fill
    # if WM.update_detail_flood_fill :
    if update_detail_flood_fill:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.mode_set(mode = 'SCULPT')
        #Check Dyntopo
        if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
            pass
        else :
            bpy.ops.sculpt.dynamic_topology_toggle()
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE_COLLAPSE'
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'CONSTANT'
        
        #shading    
        # if not WM.flat_shading :
        if not flat_shading:
            bpy.context.scene.tool_settings.sculpt.use_smooth_shading = True
        else :
            bpy.context.scene.tool_settings.sculpt.use_smooth_shading = False   
            
        bpy.ops.sculpt.detail_flood_fill()
        bpy.ops.sculpt.optimize()
    
    #activate dyntopo
    else :
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.mode_set(mode = 'SCULPT')
        #Check Dyntopo
        if bpy.context.sculpt_object.use_dynamic_topology_sculpting :
            pass
        else :
            bpy.ops.sculpt.dynamic_topology_toggle()   
             
#++++++++++++++++++++++++++++++++++++
        
    #Assign previous mode
    if constant:
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'CONSTANT'
    elif relative : 
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'RELATIVE' 
    elif brush :
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'BRUSH'   
        
    if subdivide:
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE'
    elif collapse:
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'COLLAPSE'
    elif subdiv_collapse : 
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE_COLLAPSE'    
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
            
#Smoothmesh    
def CheckSmoothMesh():
    smooth_mesh = get_addon_preferences().smooth_mesh

    # if WM.smooth_mesh :
    if smooth_mesh :
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].factor = 1
        bpy.context.object.modifiers["Smooth"].iterations = 2
        #Apply
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")   
        
#Smoothmesh for mask
class Check_smooth_Mesh(bpy.types.Operator):
    bl_idname = "object.check_smooth_mesh"
    bl_label = "Check Smooth Mesh"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        obj = context.active_object
        smooth_mesh = get_addon_preferences().smooth_mesh
        
        # if WM.smooth_mesh :
        if smooth_mesh:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.modifier_add(type='SMOOTH')
            bpy.context.object.modifiers["Smooth"].factor = 1
            bpy.context.object.modifiers["Smooth"].iterations = 2
            #Make smooth only on the vertexgroup if it exist
            for vgroup in obj.vertex_groups:
                if vgroup.name == "Mask_Group":
                    bpy.context.object.modifiers["Smooth"].vertex_group = "Mask_Group"
            #Apply        
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")   
        return {"FINISHED"}
        
selection = list() 
#convert Metaballs
def convert_mataballs_curve(to_convert):
    
    # on selectionne les metaballs et on les convertit
    for obj in to_convert:
        obj.select = True
        
    bpy.context.scene.objects.active = bpy.context.selected_objects[0]       
    bpy.ops.object.convert(target='MESH')
    
    #remove holes
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    sel_edges=[e for e in bm.edges if e.select]
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
    if len(sel_edges)>0:
      for e in bm.edges:
        if e not in sel_edges: e.select=False
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    
    bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode = 'OBJECT')  

#Apply and Separate 
class ApplySeparate(bpy.types.Operator):
    bl_idname = "object.apply_separate"
    bl_label = "Apply and Separate"
    bl_description = "Apply Modifiers and Separate objects"
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
 
        # recuperation de la liste des obj selectionne mais sans les metaballs ni les curves
        # elles seront ajoutees une fois converties
        for obj in bpy.context.selected_objects:
            if obj.type not in ['META', 'CURVE', 'FONT']:
                selection.append(obj)
 
        # recuperation des metaballs et curves       
        to_convert = [obj for obj in context.selected_objects if obj.type in [ 'META', 'CURVE', 'FONT']]
 
        bpy.ops.object.select_all(action = 'DESELECT')
 
        # si il y a des metaballs ou des curves
        if to_convert:
            # convertion des metaballs et curves via la fonction
            convert_mataballs_curve(to_convert)
            # on ajoute le nouvel obj a la list "selection"
            selection.append(bpy.context.active_object)
 
        for obj in selection:
            obj.select = True
            if obj.modifiers:
                bpy.context.scene.objects.active=obj
                for mod in obj.modifiers :
                    
                    if mod.show_viewport == False :
                        bpy.ops.object.modifier_remove(modifier=mod.name)

                    if mod.type == 'MIRROR':
                        if not "Mirror_Skin" in obj.modifiers:
                            mod.use_mirror_merge = False
                            mod.use_clip = False
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                    else:
                        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name) 
 
        for obj in context.selected_objects :
            bpy.context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode = 'OBJECT')
 
            if not obj in selection:
                selection.append(obj)
 
        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
 
        del(selection[:])
 
        return {"FINISHED"}   
     
##------------------------------------------------------  
#
# Update Dyntopo
#
##------------------------------------------------------ 
class UpdateDyntopo(bpy.types.Operator):
    bl_idname = "object.update_dyntopo"
    bl_label = "Update Dyntopo"
    bl_description = "Update object with the current detail size"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.auto_save = get_addon_preferences().auto_save
        object = bpy.context.active_object
        fill_holes_dyntopo = get_addon_preferences().fill_holes_dyntopo
        
        if self.auto_save:
            save_tmp()
        bpy.context.user_preferences.edit.use_global_undo = True
        
        #SCULPT
        if bpy.context.object.mode == "SCULPT":
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            bpy.ops.object.mode_set(mode = 'SCULPT')
            
            #Fill Hole
            if fill_holes_dyntopo:
                #Fill Holes
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='EDGE')
                bm = bmesh.from_edit_mesh(bpy.context.object.data)
                sel_edges=[e for e in bm.edges if e.select]
                bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
                if len(sel_edges)>0:
                  for e in bm.edges:
                    if e not in sel_edges: e.select=False
                bpy.ops.mesh.edge_face_add()
                bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                
                bpy.ops.mesh.select_more()
                bpy.ops.mesh.select_more()
                
                #create vertex group and assign vertices   
                object.vertex_groups.new("Mask_Group") 
                for vgroup in object.vertex_groups:
                    if vgroup.name == "Mask_Group":
                        bpy.ops.object.vertex_group_assign()
                
                #mask from faces
                bpy.ops.mesh.hide(unselected=False)
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.mask_flood_fill(mode='VALUE', value=1)
                bpy.ops.paint.hide_show(action='SHOW', area='ALL')
                bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)

            
            #Check Dyntopo and smooth
            bpy.ops.object.check_smooth_mesh()
            CheckDyntopo()
            
            bpy.ops.object.mode_set(mode = 'SCULPT')
            
        #OBJECT
        elif bpy.context.object.mode == "OBJECT":
            
            for obj in bpy.context.selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active=obj
                obj.select=True
                     
                if obj.type == 'META' : 
                    bpy.ops.object.convert(target='MESH')  
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                
                if obj.type in ['CURVE', 'FONT'] :   
                    bpy.ops.object.convert(target='MESH')
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    
                    #remove holes
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.select_mode(type='EDGE')
                    bm = bmesh.from_edit_mesh(bpy.context.object.data)
                    sel_edges=[e for e in bm.edges if e.select]
                    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
                    if len(sel_edges)>0:
                      for e in bm.edges:
                        if e not in sel_edges: e.select=False
                    bpy.ops.mesh.edge_face_add()
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                    bpy.ops.object.mode_set(mode='EDIT')  
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.remove_doubles()
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True) 
                    
                if obj.modifiers:
                    if not "Mirror_primitive" in obj.modifiers:
                        bpy.ops.object.apply_separate()
                        bpy.ops.object.boolean_sculpt_union_difference() 
                
                
                # if WM.fill_holes_dyntopo:
                if fill_holes_dyntopo:
                    #Fill Holes
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type='EDGE')
                    bm = bmesh.from_edit_mesh(bpy.context.object.data)
                    sel_edges=[e for e in bm.edges if e.select]
                    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=False)
                    if len(sel_edges)>0:
                      for e in bm.edges:
                        if e not in sel_edges: e.select=False
                    bpy.ops.mesh.edge_face_add()
                    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                    
                    bpy.ops.mesh.select_more()
                    bpy.ops.mesh.select_more()
                    
                    #create vertex group and assign vertices   
                    obj.vertex_groups.new("Mask_Group") 
                    for vgroup in obj.vertex_groups:
                        if vgroup.name == "Mask_Group":
                            bpy.ops.object.vertex_group_assign()

                    bpy.ops.mesh.hide(unselected=False)
                    bpy.ops.object.mode_set(mode='SCULPT')
                    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=1)
                    bpy.ops.paint.hide_show(action='SHOW', area='ALL')
                    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)

                    bpy.ops.object.mode_set(mode='OBJECT')
                
                bpy.ops.object.check_smooth_mesh()
                CheckDyntopo()
 
                bpy.ops.object.mode_set(mode = 'OBJECT')
         
        #Remove Vgroup             
        for vgroup in object.vertex_groups:
            if vgroup.name == "Mask_Group":
                object.vertex_groups.remove(vgroup)
                        
        bpy.context.scene.tool_settings.use_snap = False

        return {"FINISHED"}
        
##------------------------------------------------------  
#
# Boolean Union/Difference
#
##------------------------------------------------------    
# UNION / Difference 
class BooleanSculptUnionDifference(bpy.types.Operator):
    bl_idname = "object.boolean_sculpt_union_difference"
    bl_label = "Boolean Union Difference"
    bl_description = "Combine objects !!10x faster on blender 2.77.3!!"
    bl_options = {"REGISTER", "UNDO"}
    
    operation_type = bpy.props.EnumProperty(
        items = (('UNION', "", ""),
                ('DIFFERENCE', "", "")),
                default = 'UNION',
                )
             
    def execute(self, context):
        WM = context.window_manager
        Detailsize = bpy.context.window_manager.detail_size
        self.auto_save = get_addon_preferences().auto_save
        
        #save Temp
        if self.auto_save:
            save_tmp()
        
        bpy.context.user_preferences.edit.use_global_undo = True
        
        actObj = context.active_object  
        
 
        
        #Separate objects
        if self.operation_type == 'UNION':
            bpy.ops.object.apply_separate()
        
        #Union
        actObj = context.active_object
        for selObj in bpy.context.selected_objects:
            if selObj != context.active_object and(selObj.type == "MESH"):
                act_obj = context.active_object
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                newMod = act_obj.modifiers.new("Boolean"+ selObj.name,"BOOLEAN")
                newMod.operation = self.operation_type
                
                # Check Remesh
                remesh = False
                for mod in bpy.context.active_object.modifiers:
                    if mod.type == "REMESH":
                        remesh = True  
                if not remesh :
                    #check Blender version
                    if (2, 77, 0) < bpy.app.version:
                        newMod.solver = 'BMESH'
                            
                if remesh :
                    if (2, 77, 0) < bpy.app.version:
                        newMod.solver = 'CARVE'
                    
                newMod.object = selObj
                bpy.ops.object.modifier_apply (modifier=newMod.name)
                bpy.ops.object.select_all(action='DESELECT')
                selObj.select = True
                bpy.ops.object.delete()
                act_obj.select=True                  
        
        #Update Dyntopo and Smooth
        CheckDyntopo()
        CheckSmoothMesh()
        
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {"FINISHED"}

# Boolean Rebool       
class BooleanSculptRebool(bpy.types.Operator):
    bl_idname = "object.boolean_sculpt_rebool"
    bl_label = "Boolean Rebool"
    bl_description = "Slice object in two parts !!10x faster on blender 2.77.3!!"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        WM = context.window_manager
        self.auto_save = get_addon_preferences().auto_save
        actObj = context.active_object  
        
        #save Temp
        if self.auto_save:
            save_tmp()
            
        bpy.context.user_preferences.edit.use_global_undo = True
   
        final_list = []
        act_obj = context.active_object
        obj_bool_list = [obj for obj in context.selected_objects if obj != act_obj and obj.type == 'MESH']
        bpy.ops.object.select_all(action='DESELECT')
        
        
        final_list.append(act_obj)
        for obj in obj_bool_list:
            act_obj.select=True
            act_obj.modifiers.new("Boolean", 'BOOLEAN')
            act_obj.modifiers["Boolean"].object = obj
            act_obj.modifiers["Boolean"].operation = 'DIFFERENCE'
            
            # Check Remesh
            remesh = False
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "REMESH":
                    remesh = True
            if not remesh :
                #check Blender version
                if (2, 77, 0) < bpy.app.version:
                    act_obj.modifiers["Boolean"].solver = 'BMESH'
                else:
                    pass
                
            if remesh :
                if (2, 77, 0) < bpy.app.version:
                    act_obj.modifiers["Boolean"].solver = 'CARVE'
                else:
                    pass
                
            bpy.ops.object.duplicate_move()
            
#            bpy.context.active_object.name= "temptoto"
            tempobj = bpy.context.active_object
            
            final_list.append(tempobj)
            
            tempobj.modifiers["Boolean"].operation = 'INTERSECT'
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Boolean')
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            
            
            act_obj.select=True
            bpy.context.scene.objects.active = act_obj 
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Boolean')
            
            act_obj.select=False
            tempobj.select=False
            obj.select = True 
            bpy.ops.object.delete(use_global=False) 
              
            act_obj.select=True
            

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') 
        bpy.ops.object.select_all(action='DESELECT')   
        
        for obj in final_list :
            obj.select = True
            bpy.context.scene.objects.active = obj 
            
            CheckDyntopo()
            CheckSmoothMesh()
            obj.select = False
            
        bpy.context.scene.objects.active = act_obj
        act_obj.select = True
        return {"FINISHED"}







