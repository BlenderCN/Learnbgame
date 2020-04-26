import bpy
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)

from .operators import (CheckDyntopo,
                        CheckSmoothMesh)


##------------------------------------------------------  
#
# Add Primitives
#
##------------------------------------------------------ 
class CustomAddPrimitives(bpy.types.Operator):
    bl_idname = "object.custom_add_primitives"
    bl_label = "Custom Add Primitives"
    bl_description = "Create primitives"
    bl_options = {"REGISTER", "UNDO"}
    
    primitive = EnumProperty(
        items = (('sphere', "Sphere", ""),
                 ('cylinder', "Cylinder", ""),
                 ('cube', "Cube", ""),
                 ('cone', "Cone", ""),
                 ('torus', "Torus", "")),
                 default = 'sphere'
                 )
    
    def execute(self, context):
        WM = context.window_manager
        ref_obj = bpy.context.window_manager.ref_obj
        
        if context.object is None:
            WM.primitives_parenting = False
            
        actObj = context.active_object
        
        obj_list = [obj for obj in bpy.context.scene.objects if obj.select]
        
        if context.object is not None :
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if not WM.origin: 
            bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
        
        if context.object is None and not WM.ref_obj :
            WM.add_mirror = False 
               
        if self.primitive == 'sphere':
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, size=1, enter_editmode=False)
        elif self.primitive == 'cylinder':
            bpy.ops.mesh.primitive_cylinder_add(vertices=64, view_align=False, enter_editmode=True)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
            bpy.ops.transform.edge_crease(value=1) 
            bpy.ops.object.mode_set(mode = 'OBJECT')  
        elif self.primitive == 'cube':
            bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False)
        elif self.primitive == 'cone':
            bpy.ops.mesh.primitive_cone_add(vertices=128, radius1=1, radius2=0, depth=2, view_align=False, enter_editmode=False)
        else:
            bpy.ops.mesh.primitive_torus_add(view_align=False, major_segments=120, minor_segments=64, major_radius=1, minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75)
        
        obj_list.append(bpy.context.active_object)
        
        
        if WM.add_mirror :
            if WM.origin  :
                pass
            else :  
                if context.object is None :
                    self.report({'INFO'},"Select Mirror Object First", icon='ERROR') 
                
                else :
                    bpy.ops.object.modifier_add(type='MIRROR')
                    bpy.context.object.modifiers["Mirror"].name = "Mirror_primitive"

                    bpy.context.object.modifiers["Mirror_primitive"].use_x = True
                    bpy.context.object.modifiers["Mirror_primitive"].use_mirror_merge = False
                 
                    if WM.ref_obj :
                        bpy.context.object.modifiers["Mirror_primitive"].mirror_object = bpy.data.objects[ref_obj]
                    
                    elif len([obj for obj in context.selected_objects ]) == 1:
                        bpy.context.object.modifiers["Mirror_primitive"].mirror_object = actObj
                    
        CheckDyntopo()
        CheckSmoothMesh()  
        
        #Parenting
        if WM.primitives_parenting  :
            # Parent the new object to the active object
            for obj in obj_list:
                if not obj.parent:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = obj
                    obj.select=True
                    bpy.context.scene.objects.active = actObj
                    actObj.select=True
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = obj
                    obj.select=True
                
        
        if not WM.origin: 
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            
            
        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0
        bpy.context.space_data.cursor_location[0] = 0
        return {"FINISHED"}

##------------------------------------------------------  
#
# Add Metaballs
#
##------------------------------------------------------ 

# Metaballs    
class CustomAddMetaballs(bpy.types.Operator):
    bl_idname = "object.custom_add_metaballs"
    bl_label = "Custom Add Metaballs"
    bl_description = "Create Metaballs"
    bl_options = {"REGISTER", "UNDO"}
    
    metaballs = EnumProperty(
        items = (('ball', "Ball", ""),
                 ('capsule', "Capsule", ""),
                 ('plane', "Plane", ""),
                 ('hellipsoid', "Hellipsoid", ""),
                 ('cube', "Cube", "")),
                 default = 'ball'
                 )

    def execute(self, context):
        WM = context.window_manager
        
        if context.object is None:
            WM.primitives_parenting = False
            
        actObj = context.active_object
        
        obj_list = [obj for obj in bpy.context.scene.objects if obj.select]
        
        
        if context.object is not None :
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if not WM.origin:
            bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
       
        if self.metaballs == 'ball':
            bpy.ops.object.metaball_add(type='BALL', radius=0.5)
        elif self.metaballs == 'capsule':
            bpy.ops.object.metaball_add(type='CAPSULE', radius=0.5)
        elif self.metaballs == 'hellipsoid':
            bpy.ops.object.metaball_add(type='ELLIPSOID', radius=0.5)
        elif self.metaballs == 'cube':
            bpy.ops.object.metaball_add(type='CUBE', radius=0.5)
        else:
            bpy.ops.object.metaball_add(type='PLANE', radius=0.5)
        
        obj_list.append(bpy.context.active_object)
        
        bpy.context.object.data.elements[0].use_negative = True
        bpy.context.window_manager.metaballs_pos_neg = "positive"
        bpy.context.object.data.resolution = 0.02
        bpy.context.object.data.threshold = 0.01
        bpy.context.object.data.update_method = 'HALFRES'
        
        
        #Parenting
        if WM.primitives_parenting  :
            # Parent the new object to the active object
            for obj in obj_list:
                if not obj.parent:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = obj
                    obj.select=True
                    bpy.context.scene.objects.active = actObj
                    actObj.select=True
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = obj
                    obj.select=True
                    
        if not WM.origin:
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            
        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0
        bpy.context.space_data.cursor_location[0] = 0
        return {"FINISHED"}


# Update Metaballs
def UpdateMetaballs(self, context):  
    if bpy.context.object.data.elements[0].use_negative :
        bpy.context.object.data.elements[0].use_negative = False
    else:
        bpy.context.object.data.elements[0].use_negative = True    



class CleanMetaballs(bpy.types.Operator):
    bl_idname = "object.clean_metaballs"
    bl_label = "Clean Metaballs"
    bl_description = "Remove all the metaballs from the scene"
    bl_options = {"REGISTER","UNDO"}

    def execute(self, context):
        actObj = context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        for x in bpy.data.objects :
            if x.type == 'META':
                bpy.context.scene.objects.active=x
                x.select = True
                bpy.ops.object.delete()
            
                actObj.select = True  
        return {"FINISHED"}             
                   
##------------------------------------------------------  
#
# Skin
#
##------------------------------------------------------ 

# Add skin
class AddSkin(bpy.types.Operator):
    bl_idname = "object.add_skin"
    bl_label = "Add Skin"
    bl_description = "Create Skin Object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        WM = context.window_manager
        actObj = context.active_object   
#        bpy.context.scene.obj1 = bpy.context.active_object.name
        ref_obj = bpy.context.window_manager.ref_obj
        
        if context.object is not None :
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if not WM.origin:
            bpy.ops.view3d.cursor3d('INVOKE_DEFAULT')
        
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=True)
        bpy.ops.mesh.merge(type='CENTER')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        #Add Skin modifier
        bpy.ops.object.modifier_add(type='SKIN')
        bpy.context.object.modifiers["Skin"].use_smooth_shade = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.object.skin_root_mark()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Add Subdiv
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 3

        #Enter in edit mode
        bpy.ops.object.mode_set(mode = 'EDIT')

        if bpy.context.space_data.use_occlude_geometry == True :
            bpy.context.space_data.use_occlude_geometry = False
        else :
            pass
        
        if WM.add_mirror :
            bpy.ops.object.modifier_add(type='MIRROR')
            bpy.context.object.modifiers["Mirror"].use_x = True
            bpy.context.object.modifiers["Mirror"].use_mirror_merge = False
            bpy.ops.object.modifier_move_up(modifier="Mirror")
            bpy.ops.object.modifier_move_up(modifier="Mirror")
            bpy.ops.object.modifier_move_up(modifier="Mirror")

            if WM.ref_obj :
                bpy.context.object.modifiers["Mirror"].mirror_object = bpy.data.objects[ref_obj]
                skin_origin = False
                
            elif bpy.context.active_object :
                bpy.context.object.modifiers["Mirror"].mirror_object = actObj
                skin_origin = False
            
            if WM.origin:
                bpy.context.object.modifiers["Mirror"].name = "Mirror_Skin"
                bpy.context.object.modifiers["Mirror_Skin"].use_mirror_merge = True
                bpy.context.object.modifiers["Mirror_Skin"].use_clip = True
                bpy.ops.object.modifier_move_up(modifier="Mirror_Skin")
                bpy.ops.object.modifier_move_up(modifier="Mirror_Skin")
                bpy.ops.object.modifier_move_up(modifier="Mirror_Skin")

        bpy.context.space_data.cursor_location[1] = 0
        bpy.context.space_data.cursor_location[2] = 0
        bpy.context.space_data.cursor_location[0] = 0
        
        if not WM.origin:
            bpy.ops.transform.translate('INVOKE_DEFAULT') 
          
        return {"FINISHED"}




##------------------------------------------------------  
#
# GP Lines
#
##------------------------------------------------------ 
bpy.types.Scene.obj1 = bpy.props.StringProperty()

# Create GP Line
class CreateGPLines(bpy.types.Operator):
    bl_idname = "object.creategpline"
    bl_label = "Create GP Lines"
    bl_description = "Create GP Lines !! Press D to create Grease Pencil Lines !!"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        selected = context.selected_objects
        actObj = context.active_object if context.object is not None else None
        if actObj :
            bpy.context.scene.obj1 = actObj.name
        
        WM = context.window_manager
        ref_obj = bpy.context.window_manager.ref_obj 
        
        #prepare GP
        if context.selected_objects:
            bpy.context.scene.tool_settings.grease_pencil_source = 'OBJECT'
            bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
            
            
            #Add snap
            bpy.context.scene.tool_settings.use_snap = True
            bpy.context.scene.tool_settings.snap_element = 'FACE'
            
        else :
            bpy.context.scene.tool_settings.use_snap = False
            bpy.context.scene.tool_settings.grease_pencil_source = 'OBJECT'
            bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = 'VIEW'
        

        bpy.context.scene.tool_settings.use_gpencil_continuous_drawing = True
        
        

        #Create Empty mesh
        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False)
        bpy.context.active_object.name= "GP_Surface"
#        bpy.ops.object.shade_smooth()
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.delete(type='VERT')    
        bpy.ops.object.mode_set(mode = 'OBJECT')  
        
        if WM.add_mirror :
            bpy.ops.object.modifier_add(type='MIRROR')
            bpy.context.object.modifiers["Mirror"].use_x = True
            bpy.context.object.modifiers["Mirror"].use_mirror_merge = False

            if WM.ref_obj :
                bpy.context.object.modifiers["Mirror"].mirror_object = bpy.data.objects[ref_obj]
                skin_origin = False
                
            elif actObj :
                bpy.context.object.modifiers["Mirror"].mirror_object = actObj
                skin_origin = False
                
            else :
                bpy.ops.object.modifier_remove(modifier="Mirror")

                  
        #Add Solidify    
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        
        bpy.context.object.modifiers["Solidify"].thickness = 0.4
        bpy.context.object.modifiers["Solidify"].offset = 0
        bpy.context.object.modifiers["Solidify"].use_quality_normals = True
        bpy.context.object.modifiers["Solidify"].use_even_offset = True
        
        #Add subsurf
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 3
        
        #Add Shrinkwrap
        if selected :
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = actObj
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")

        bpy.ops.object.mode_set(mode = 'EDIT')
        
        bpy.ops.gpencil.draw('INVOKE_DEFAULT')
        
        return {"FINISHED"}

# Shrinkwrap Surface on mesh
class ShrinkwrapGPLines(bpy.types.Operator):
    bl_idname = "object.shrinkwrap_gplines"
    bl_label = "Shrinkwrap Gplines"
    bl_description = "Add a Shrinkwrap modifier to fit the object surface"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj_name = bpy.context.scene.obj1
        
        bpy.ops.object.mode_set(mode = 'OBJECT')  
        bpy.ops.object.shade_smooth() 
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[obj_name]
        bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
        bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
        bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {"FINISHED"}

# Clipping Merge Mirror                  
def ClippingMerge(self, context):
    bl_description = "Use Clipping/Merger for the mirror modifier"
    
    obj = context.active_object  
    for mod in obj.modifiers :
        if mod.type == 'MIRROR':
            if mod.use_mirror_merge == True :
                mod.name = "Mirror"
                mod.use_mirror_merge = False
                mod.use_clip = False
            
            else :
                mod.name = "Mirror_Skin"
                mod.use_mirror_merge = True
                mod.use_clip = True    


# Remove the Mirror modifier
class RemoveMirror(bpy.types.Operator):
    bl_idname = "object.remove_mirror"
    bl_label = "Remove Mirror"
    bl_description = "Delete the Mirror modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        mirror = bpy.context.object.modifiers.get("Mirror")
        if mirror :
            bpy.ops.object.modifier_remove(modifier="Mirror")
            
        return {"FINISHED"}

# Remove Bevel
class RemoveBevel(bpy.types.Operator):
    bl_idname = "object.remove_bevel"
    bl_label = "Remove Bevel"
    bl_description = "Delete the Bevel modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        mirror = bpy.context.object.modifiers.get("Bevel")
        if mirror :
            bpy.ops.object.modifier_remove(modifier="Bevel")
            
        return {"FINISHED"}
    
# Remove Remesh
class RemoveSolidify(bpy.types.Operator):
    bl_idname = "object.remove_solidify"
    bl_label = "Remove Solidify"
    bl_description = "Delete the Solidify modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        solidify = bpy.context.object.modifiers.get("Solidify")
        if solidify :
            bpy.ops.object.modifier_remove(modifier="Solidify")
            
        return {"FINISHED"}

#Remove Shrinkwrap
class RemoveShrinkwrap(bpy.types.Operator):
    bl_idname = "object.remove_shrinkwrap"
    bl_label = "Remove Shrinkwrap"
    bl_description = "Delete the Shrinkwrap modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        shrinkwrap = bpy.context.object.modifiers.get("Shrinkwrap")
        if shrinkwrap :
            bpy.ops.object.modifier_remove(modifier="Shrinkwrap")
        
        return {"FINISHED"}    

#Remove Mirror
class RemoveMirror(bpy.types.Operator):
    bl_idname = "object.remove_mirror"
    bl_label = "Remove Mirror"
    bl_description = "Delete the Mirror modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object    
        
        mirrror = bpy.context.object.modifiers.get("Mirror")
        mirrror_skin = bpy.context.object.modifiers.get("Mirror_Skin")
        if mirrror :
            bpy.ops.object.modifier_remove(modifier="Mirror")
        
        elif mirrror_skin :
            bpy.ops.object.modifier_remove(modifier="Mirror_Skin")
        return {"FINISHED"}      


#Add Mirror
class AddMirror(bpy.types.Operator):
    bl_idname = "object.add_mirror"
    bl_label = "Add Mirror Modifier"
    bl_description = "Add Mirror Modifier"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        WM = context.window_manager
        ref_obj = bpy.context.window_manager.ref_obj 
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if WM.add_mirror :
            mirrror = bpy.context.object.modifiers.get("Mirror")
            if not mirrror:
                bpy.ops.object.modifier_add(type='MIRROR')
                bpy.context.object.modifiers["Mirror"].use_mirror_merge = False
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")

            if WM.ref_obj :
                bpy.context.object.modifiers["Mirror"].mirror_object = bpy.data.objects[ref_obj]
                skin_origin = False
        else:
            mirrror = bpy.context.object.modifiers.get("Mirror")
            if not mirrror:
                bpy.ops.object.modifier_add(type='MIRROR')
                bpy.context.object.modifiers["Mirror"].use_mirror_merge = False
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")
                bpy.ops.object.modifier_move_up(modifier="Mirror")        
        bpy.ops.object.mode_set(mode = 'EDIT')     
                
            
                        
        return {"FINISHED"}

class AddGPBevel(bpy.types.Operator):
    bl_idname = "object.add_gp_bevel"
    bl_label = "Add Bevel Modifier"
    bl_description = "Add Bevel Modifier"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        
        bevel = bpy.context.object.modifiers.get("Bevel")
        if not bevel:
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.object.modifiers["Bevel"].show_in_editmode = True
            bpy.context.object.modifiers["Bevel"].limit_method = 'ANGLE'
            bpy.context.object.modifiers["Bevel"].segments = 4
            bpy.context.object.modifiers["Bevel"].angle_limit = 1.53589
            bpy.context.object.modifiers["Bevel"].use_clamp_overlap = False


            bpy.ops.object.modifier_move_down(modifier="Subsurf")  
            
            bpy.ops.object.mode_set(mode = 'EDIT') 
                
        return {"FINISHED"}
                                   
                                   
class AddSmoothSkin(bpy.types.Operator):
    bl_idname = "object.add_smooth_skin"
    bl_label = "Add Smooth Skin"
    bl_description = "Smooth the skin wire"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        actObj = context.active_object
    
        smooth_skin = bpy.context.object.modifiers.get("Smooth_skin")
        if not smooth_skin:
            newMod = actObj.modifiers.new("Smooth_skin","SUBSURF")
            bpy.context.object.modifiers["Smooth_skin"].levels = 2
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")  
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")
            bpy.ops.object.modifier_move_up(modifier="Smooth_skin")
        return {"FINISHED"}

#Remove Mirror
class RemoveSmoothSkin(bpy.types.Operator):
    bl_idname = "object.remove_smooth_skin"
    bl_label = "Remove Smooth skin"
    bl_description = "Delete the Smooth skin modifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):  
        
        smooth_skin = bpy.context.object.modifiers.get("Smooth_skin")
        if smooth_skin :
            bpy.ops.object.modifier_remove(modifier="Smooth_skin")
        
        return {"FINISHED"}      