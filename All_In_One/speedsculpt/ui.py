import bpy
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)

from .functions import *
from .operators import *
from .lattice import *
from .curves import *
from bpy.types import Curve, SurfaceCurve, TextCurve

import os
from os.path import isfile, join
from os import remove, listdir


##------------------------------------------------------  
#
# UI
#
##------------------------------------------------------ 



        

# -----------------------------------------------------------------------------
#    Help
# ----------------------------------------------------------------------------- 
class HelpPrimitives(bpy.types.Menu):
    bl_idname = "view3d.help_primitives"
    bl_label = "Help Primitives"

    def draw(self, context):
        layout = self.layout
        layout.label("Create primitives for booleans")
        layout.label("You can combine Mesh and Metaballs")
        layout.separator()  
        layout.label("Example :") 
        layout.operator("wm.url_open", text="Add And combine primitives").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/primitives.gif"
        
        
class HelpSkin(bpy.types.Menu):
    bl_idname = "view3d.help_skin"
    bl_label = "Help Skin"

    def draw(self, context):
        layout = self.layout
        layout.label("Create objects with skin Modifier")
        layout.label("Create Fast Character with Skin, Origin + Mirror On") 
        layout.separator()  
        layout.label("Examples :") 
        layout.operator("wm.url_open", text="Add Skin and combine").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/skin_simple.gif"
        layout.operator("wm.url_open", text="Create a character with Skin").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/skin_character.gif"
        
        
                     
class HelpCurves(bpy.types.Menu):
    bl_idname = "view3d.help_curves"
    bl_label = "Help Curves"

    def draw(self, context):
        layout = self.layout
        layout.label("Need Blender 2.78", icon='ERROR')
        layout.separator()  
        layout.label("Create Curve and use BBox to make surface")
        layout.label("Create Curve and convert it to skin Modifier") 
        layout.label("Slice Objects with curves, make holes etc") 
        layout.separator()  
        layout.label("Examples :") 
        layout.operator("wm.url_open", text="Convert Curve to skin").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/convert_curve.gif" 
        layout.operator("wm.url_open", text="Slice/Cut/Rebool objects with curves").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/curves_slice.gif" 
        
class HelpGPLine1(bpy.types.Menu):
    bl_idname = "view3d.help_gpline_1"
    bl_label = "How to Use Gpline"

    def draw(self, context):
        layout = self.layout
        layout.label("Create surfaces with Bsurface")
        layout.separator() 
        layout.label("1 - Draw Grease Pencil Lines")
        layout.label("2 - Press Add Bsurface to create surface")
        layout.separator()  
        layout.label("Example :") 
        layout.operator("wm.url_open", text="Add surface with Bsurface").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/gp_lines.gif" 

class HelpGPLine2(bpy.types.Menu):
    bl_idname = "view3d.help_gpline_2"
    bl_label = "How to Use Gpline"

    def draw(self, context):
        layout = self.layout
        layout.label("1 - Press D and Draw Grease Pencil Lines")
        layout.label("2 - Press Space to exit Grease Pencil")  
        layout.label("3 - Press Add Bsurface to create surface")       
        
class HelpLattice(bpy.types.Menu):
    bl_idname = "view3d.help_lattice"
    bl_label = "Help Lattice"

    def draw(self, context):
        layout = self.layout
        layout.label("Create Lattice and deform objects")  
        layout.label("Create Lattice from mask in Sculpt mode and deform your mesh")   
        layout.separator()  
        layout.label("Example :") 
        layout.operator("wm.url_open", text="Add Lattice and deform objects").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/lattices.gif" 
               
        
class HelpSymmetrize(bpy.types.Menu):
    bl_idname = "view3d.help_symmetrize"
    bl_label = "Help Symmetrize"

    def draw(self, context):
        layout = self.layout
        layout.label("Symmetrize your mesh in object, Sculpt and Dyntopo")
        layout.separator()  
        layout.label("Example :") 
        layout.operator("wm.url_open", text="Symmetrize mesh in Sculpt/Object/Dyntopo").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/symmetrize.gif" 

class HelpRemesh(bpy.types.Menu):
    bl_idname = "view3d.help_remesh"
    bl_label = "Help Remesh"

    def draw(self, context):
        layout = self.layout
        layout.label("Remesh - Add Remesh Modifier to make 3D printed objetcs")
        layout.label("Decimate - Simplify your mesh or use mask to simplify a part of it")    
        layout.separator()  
        layout.label("Examples :") 
        layout.operator("wm.url_open", text="Remesh object").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/remesh.gif" 
        layout.operator("wm.url_open", text="Decimate mesh with mask").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/decimate.gif" 

class HelpExtractMask(bpy.types.Menu):
    bl_idname = "view3d.help_extract_mask"
    bl_label = "Help Extract Mask"

    def draw(self, context):
        layout = self.layout
        layout.label("Extract new mesh from Sculpt mask") 
        layout.separator()  
        layout.label("Example :") 
        layout.operator("wm.url_open", text="Extract mesh with mask").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/extract_mask.gif" 

class HelpQuickPose(bpy.types.Menu):
    bl_idname = "view3d.help_quick_pose"
    bl_label = "Help Quick Pose"

    def draw(self, context):
        layout = self.layout
        layout.label("Make a quick pose of your model") 
        layout.label("You can use mask to pose only a part")  
        layout.separator() 
        layout.label("Direct Pose :")   
        layout.label("Click on Create Bones, place the vertice, extrude it")
        layout.label("Click on the Pose button and make your pose")    
        layout.separator() 
        layout.label("Mask Pose :")   
        layout.label("Click on Use Mask and Add Mask")  
        layout.label("Paint your mask")  
        layout.label("Click on Create Bones, place the vertice, extrude it")
        layout.label("Click on the Pose button and make your pose") 
        layout.separator() 
        layout.label("You can Edit and smooth your mask") 
        layout.separator() 
        layout.label("The creation of the Armature don't work in Local View", icon='ERROR')
        
        layout.separator()  
        layout.label("Example :") 
        layout.operator("wm.url_open", text="Quick Pose with mask").url = "http://www.pitiwazou.com/wp-content/uploads/2016/08/quick_pose_mask.gif"

# -----------------------------------------------------------------------------
#    Options
# -----------------------------------------------------------------------------
def Options(self, context):
    layout = self.layout
    WM = context.window_manager
    toolsettings = context.tool_settings
    sculpt = toolsettings.sculpt
    addon_pref = get_addon_preferences()

    row = layout.row(align=True)
    row.prop(addon_pref, "smooth_mesh", text="Smooth")
    row.prop(addon_pref, "update_detail_flood_fill", text="Update")
    row = layout.row(align=True)
    row.prop(addon_pref, "flat_shading", text="Flat")
    row.prop(addon_pref, "fill_holes_dyntopo", text="Fill Holes")

    if context.object is not None:
        remesh = False
        for mod in bpy.context.active_object.modifiers:
            if mod.type == "REMESH":
                remesh = True
        if remesh:
            layout.prop(WM, "apply_remesh", text="Apply Remesh")
                 
# -----------------------------------------------------------------------------
#    Add Primitives
# ----------------------------------------------------------------------------- 
def AddPrimitives(self, context):
    """ Sub panel for the adding assets """
    layout = self.layout
    WM = context.window_manager
    toolsettings = context.tool_settings
    sculpt = toolsettings.sculpt
    obj = context.active_object
    
    self.show_help = get_addon_preferences().show_help
    
        
    # Add Primitives
    
    row = layout.row(align=True)
    row.prop(WM, "show_primitives", text="Add Primitives", icon='TRIA_UP' if WM.show_primitives else 'TRIA_DOWN')
    if self.show_help :    
        row.menu("view3d.help_primitives",text="", icon='TRIA_RIGHT')
    if WM.show_primitives:
        box = layout.box()
        split = box.split()
        box = split.column(align=True) 
        row = box.row(align=True)
        row.prop(WM, "origin",text="Origin")
        if context.object is not None :
            row.prop(WM, "primitives_parenting", text ="Parent")
        
        box.prop(WM, "add_mirror", text ="Add Mirror")
        
        if WM.add_mirror :
            box.label("Mirror Object:")
            box.prop_search(WM, "ref_obj", bpy.data, 'objects', text="")
        
        row = box.row(align=True)
        row.scale_x = 2
        row.operator("object.custom_add_primitives", text = "", icon = 'MATSPHERE').primitive = "sphere"
        row.operator("object.custom_add_primitives",text="", icon ='MESH_CYLINDER').primitive = "cylinder"
        row.operator("object.custom_add_primitives",text="", icon ='MESH_CUBE').primitive = "cube"
        row.operator("object.custom_add_primitives",text="", icon ='MESH_CONE').primitive = "cone"
        row.operator("object.custom_add_primitives",text="", icon ='MESH_TORUS').primitive = "torus"  
        
        # Metaballs
        row = box.row(align=True)
        row.scale_x = 2
        row.operator("object.custom_add_metaballs", text = "", icon = 'META_BALL').metaballs = "ball"
        row.operator("object.custom_add_metaballs",text="", icon ='META_CAPSULE').metaballs = "capsule"
        row.operator("object.custom_add_metaballs",text="", icon ='META_CUBE').metaballs = "cube"
        row.operator("object.custom_add_metaballs",text="", icon ='META_ELLIPSOID').metaballs = "hellipsoid"
        row.operator("object.custom_add_metaballs",text="", icon ='META_PLANE').metaballs = "plane"        
           
        if len([obj for obj in context.selected_objects if obj.type == 'META']) >= 1:
            split = box.split()
            col = split.column(align=True)
            col.label("Metaballs Options:")
            row = col.row(align=True)
            row.prop(bpy.context.object.data, "resolution", text="Resolution")
            row = col.row(align=True)
            row.prop(bpy.context.object.data, "threshold", text="Threshold")
            row = col.row(align=True)
            row.prop(WM, "metaballs_pos_neg", expand=True)
            
            if len([obj for obj in context.selected_objects if obj.type == 'META' and obj.mode == "EDIT"]) == 1:
                col.prop(bpy.context.object.data.elements.active, "stiffness", text="Stiffness")
                col.prop(bpy.context.object.data.elements.active, "hide", text="Hide")


        # Skin
        box = layout.box()
        split = box.split()
        box = split.column(align=True) 
        
        row.scale_y = 1.2
        row = box.row(align=True)
        row.operator("object.add_skin",text="Add Skin", icon ='MOD_SKIN')
        if self.show_help :
            row.menu("view3d.help_skin",text="", icon='TRIA_RIGHT')
        
        if context.object is not None :
            mirror = False
            skin = False  
            bevel = False  
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "SKIN" and bpy.context.object.mode == "EDIT":
                    skin = True
                if mod.type == "MIRROR":
                    mirror = True
                if mod.type == "BEVEL":
                    bevel = True  
                         
            if skin:    
                box.operator("object.skin_root_mark", text='Mark Root', icon='META_EMPTY')
                row = box.row(align=True) 
                row.operator("object.skin_loose_mark_clear", text='Mark Loose').action='MARK'
                row.operator("object.skin_loose_mark_clear", text='Clear Loose').action='CLEAR'
                row = box.row(align=True) 
                row.operator("object.skin_radii_equalize", text="Equalize Radii")
            
                split = box.split()
                col = split.column(align=True)
                #Mirror 
                if mirror:
                    row = col.row(align=True)
                    if "Mirror_Skin" in obj.modifiers:
                        row = col.row(align=True)
                        row.prop(bpy.context.active_object.modifiers["Mirror_Skin"], "show_viewport", text="Hide Mirror") 
                        row.prop(WM, "use_clipping", text = "", icon='UV_EDGESEL')   
                        row.operator("object.remove_mirror", text = "", icon='X')
                        
                        
                    elif "Mirror" in obj.modifiers:
                        row = col.row(align=True)
                        row.prop(bpy.context.active_object.modifiers["Mirror"], "show_viewport", text="Hide Mirror") 
                        row.prop(WM, "use_clipping", text = "", icon='UV_EDGESEL') 
                        row.operator("object.remove_mirror", text = "", icon='X')
                        
                
                #Bevel
                if bevel:
                    row = col.row(align=True)
                    row.prop(bpy.context.active_object.modifiers["Bevel"], "width", text="Bevel Width") 
                    row.prop(bpy.context.active_object.modifiers["Bevel"], "show_viewport", text="") 
                    row.operator("object.remove_bevel", text="", icon='X') 
                    
                
                
                #Smooth Skin
                if "Smooth_skin" in obj.modifiers:
                    row = col.row(align=True)
                    row.prop(bpy.context.active_object.modifiers["Smooth_skin"], "levels", text="Smooth Level") 
                    row.prop(bpy.context.active_object.modifiers["Smooth_skin"], "show_viewport", text="") 
                    row.operator("object.remove_smooth_skin", text="", icon='X') 
                
                split = box.split()
                col = split.column(align=True)       
                if not bevel: 
                    row = col.row(align=True)
                    row.operator("object.add_gp_bevel", text="Add Bevel", icon='MOD_BEVEL')    
                    
                if not mirror: 
                    row = col.row(align=True)
                    row.operator("object.add_mirror", text="Add Mirror", icon='MOD_MIRROR')  
                
                if not "Smooth_skin" in obj.modifiers:
                    row = col.row(align=True)
                    row.operator("object.add_smooth_skin", text="Add Smooth", icon='MOD_SUBSURF')     
                

        box = layout.box()
        split = box.split()
        col = split.column(align=True)

        row = col.row(align=True)
        row.operator("object.create_lathe", text="Lathe", icon='MOD_MULTIRES') 
        row.operator("object.create_curve", text="Curve", icon='LINE_DATA')
        
        if self.show_help : 
            row.menu("view3d.help_curves",text="", icon='TRIA_RIGHT')

        if context.object is not None:
            screw = False
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "SCREW":
                    screw = True


            if not screw :
                if len(bpy.context.selected_objects) == 1:
                    obj1 = bpy.context.active_object
                    if obj1.type == 'CURVE' :
                        row = col.row(align=True)
                        row.prop(bpy.context.object.data,"resolution_u", text="Resolution")
                        row = col.row(align=True)
                        row.operator("object.convert_curve_to_skin", text="Convert To Skin", icon='MOD_SKIN')


                if len(bpy.context.selected_objects) >= 2:
                    obj1 = bpy.context.active_object
                    obj2 = bpy.context.selected_objects[1] if bpy.context.selected_objects[0] == obj1 else bpy.context.selected_objects[0]

                    if obj1.type == 'MESH' and obj2.type == 'CURVE':
                        row = col.row(align=True)
                        row.prop(WM, "direct_cut",text="Slice")
                        row = col.row(align=True)
                        row.operator("object.cut_boolean", text="Cut", icon='MOD_BOOLEAN')
                        row.operator("object.cut_boolean_rebool", text="Rebool")



                # Bbox
                if len(bpy.context.selected_objects) == 1:
                    obj1 = bpy.context.active_object
                    if obj1.type == 'CURVE' :

                        box = layout.box()
                        split = box.split()
                        col = split.column(align=True)
                        row = col.row(align=True)


                        if bpy.context.object.data.bevel_depth == 0 :
                            row = col.row(align=True)
                            row.prop(WM, "bbox_bevel", text="Bevel")
                            row = col.row(align=True)
                            row.prop(WM, "bbox_offset", text="Offset")
                            row = col.row(align=True)
                            row.prop(WM, "bbox_depth", text="Depth")

                        elif bpy.context.object.data.bevel_depth > 0 :
                            row = col.row(align=True)
                            row.prop(bpy.context.object.data,"bevel_depth", text="Bevel")
                            row = col.row(align=True)
                            row.prop(bpy.context.object.data,"offset", text="Offset")
                            row = col.row(align=True)
                            row.prop(bpy.context.object.data,"extrude", text="Depth")

                        else:
                            pass
                        row = col.row()
                        row.prop(WM, "bbox_convert", text="Stay in curve Mode")
                        row = col.row()
                        row.prop(WM, "smooth_result", text="Smooth the mesh")
                        row = col.row()
                        row.operator("object.bbox", text="BBox", icon='MOD_DYNAMICPAINT')

            else :
                row = col.row(align=True)
                row.scale_x=0.5
                row.prop(bpy.context.active_object.modifiers["Screw"], "axis", text="Axis")
                row = col.row(align=True)
                row.prop(bpy.context.active_object.modifiers["Screw"], "steps", text="Steps")
                row = col.row(align=True)
                row.prop(bpy.context.active_object.modifiers["Screw"], "use_normal_flip", text="Flip Normals")


                if len([obj for obj in context.selected_objects if context.object is not None if obj.type == 'CURVE']) == 1:
                    row = col.row(align=True)
                    row.operator("object.create_empty", text="Add empty", icon='OUTLINER_OB_EMPTY')
                
        # GP Lines
        if context.object is not None and bpy.context.object.mode == "EDIT":
            if "Solidify" in obj.modifiers:
                solidify = False
                mirror = False
                shrinkwrap = False
                bevel = False
                for mod in bpy.context.active_object.modifiers:
                    if mod.type == "SOLIDIFY":
                        solidify = True
                    if mod.type == "MIRROR":
                        mirror = True  
                    if mod.type == "SHRINKWRAP":
                        shrinkwrap = True     
                    if mod.type == "BEVEL":
                        bevel = True       
                
                box = layout.box()
                split = box.split()
                col = split.column(align=True)
                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator("gpencil.surfsk_add_surface", text="Add BSurface", icon='MOD_DYNAMICPAINT') 
                if self.show_help : 
                    row.menu("view3d.help_gpline_2", text="", icon='TRIA_RIGHT')
                

                col.separator()

                #Solidify       
                if solidify:    
                    row = col.row(align=True)
                    row.scale_y = 1
                    row = col.row(align=True)
                    row.prop(bpy.context.active_object.modifiers["Solidify"], "thickness", text="Thickness")
                    row.prop(bpy.context.active_object.modifiers["Solidify"], "show_viewport", text="")
                    row = col.row(align=True)
                    col.prop(bpy.context.active_object.modifiers["Solidify"], "offset", text="Offset")
             
                if shrinkwrap: 
                    row = col.row(align=True)
                    row.prop(bpy.context.active_object.modifiers["Shrinkwrap"], "show_viewport", text="Hide Shrinkwrap") 
                    row.operator("object.remove_shrinkwrap", text = "", icon='X')

                if mirror:
                    row = col.row(align=True)
                    if "Mirror_Skin" in obj.modifiers:
                        row = col.row(align=True)
                        row.prop(bpy.context.active_object.modifiers["Mirror_Skin"], "show_viewport", text="Hide Mirror") 
                        row.prop(WM, "use_clipping", text = "", icon='UV_EDGESEL') 
                        row.operator("object.remove_mirror", text = "", icon='X')  
                        
                    elif "Mirror" in obj.modifiers:
                        row = col.row(align=True)
                        row.prop(bpy.context.active_object.modifiers["Mirror"], "show_viewport", text="Hide Mirror") 
                        row.prop(WM, "use_clipping", text = "", icon='UV_EDGESEL') 
                        row.operator("object.remove_mirror", text = "", icon='X')
                
                
                if bevel:
                    row = col.row(align=True)
                    row.prop(bpy.context.active_object.modifiers["Bevel"], "width", text="Bevel Width") 
                    row.prop(bpy.context.active_object.modifiers["Bevel"], "show_viewport", text="") 
                    row.operator("object.remove_bevel", text="", icon='X') 
                    
                         
                #Mirror 
                if not mirror: 
                    row = col.row(align=True)
                    row.operator("object.add_mirror", text="Add Mirror", icon='MOD_MIRROR')
                
                #Bevel
                if not bevel: 
                    row = col.row(align=True)
                    row.operator("object.add_gp_bevel", text="Add Bevel", icon='MOD_BEVEL')    
                    
        else:
            box = layout.box()
            split = box.split()
            col = split.column(align=True)
            if "mesh_bsurfaces" in bpy.context.user_preferences.addons:
                row = col.row(align=True)
                row.operator("object.creategpline", text="Create GP Lines", icon='MOD_DYNAMICPAINT') 
                if self.show_help : 
                    row.menu("view3d.help_gpline_1", text="", icon='TRIA_RIGHT')
            else : 
                col.label("    Activate Bsurface", icon='ERROR') 
                row = col.row(align=True)
                col.operator("screen.userpref_show",text="Open User Prefs", icon='PREFERENCES')             
                     
# -----------------------------------------------------------------------------
#    Lattice
# -----------------------------------------------------------------------------                
def Lattice(self, context):
    """ Sub panel for the adding assets """
    
    WM = context.window_manager
    obj = bpy.context.active_object  

    layout = self.layout
    if len([obj for obj in context.selected_objects if context.object is not None if obj.type in ['MESH', 'LATTICE'] ]) >= 1:
        row = layout.row(align=True)
        row.prop(WM, "show_lattice", text="Lattice", icon='TRIA_UP' if WM.show_lattice else 'TRIA_DOWN')
        if self.show_help : 
            row.menu("view3d.help_lattice",text="", icon='TRIA_RIGHT')
        if WM.show_lattice:
            if context.object is not None and obj.type == 'MESH' :
                lattice = False
                for mod in obj.modifiers:
                    if mod.type == "LATTICE":
                        lattice = True
                if not lattice:
                    box = layout.box()
                    split = box.split()
                    col = split.column(align=True)
                    row = col.row(align=True)
                    row.prop(WM, "copy_orientation", text="Don't Copy Orientation")
                    row = col.row(align=True)
                    row.prop(WM, "lattice_u", text="U:")
                    row = col.row(align=True)
                    row.prop(WM, "lattice_v", text="V:")
                    row = col.row(align=True)
                    row.prop(WM, "lattice_w", text="W:")
                    if bpy.context.object.mode == "SCULPT":
                        row = col.row(align=True)
                        row.scale_y = 1.2
                        row.operator("object.add_lattice", text="Add Lattice From Mask", icon='BRUSH_MASK')
                    else :
                        row = col.row(align=True)
                        row.scale_y = 1.2
                        row.operator("object.add_lattice", icon='OUTLINER_OB_LATTICE')
                            
                else :
                    box = layout.box()
                    split = box.split()
                    box = split.column(align=True)
                    row = box.row(align=True)
                    row.operator("object.apply_lattice_modifier", text="Apply Lattice", icon='FILE_TICK')
                    row.prop(WM, "hide_lattice", text="", icon='RESTRICT_VIEW_OFF' if WM.hide_lattice else 'RESTRICT_VIEW_ON')
                    row.operator("object.remove_lattice_modifier", text="", icon='X') 
                    
                    if bpy.context.object.mode == "OBJECT":
                        if bpy.context.object.vertex_groups:
                            for vgroup in obj.vertex_groups:
                                if vgroup.name.startswith("S"):
                                    if len(context.selected_objects) == 1:
                                        row = box.row(align=True)
                                        row.operator("object.lattice_add_mask", text="Edit Mask", icon='BRUSH_MASK') 
                                        row = box.row(align=True)
                                        row.operator("object.lattice_smooth_mask", text="Smooth Mask", icon='BRUSH_MASK')  
                    
                        else :
                            if len(context.selected_objects) == 1:
                                row = box.row(align=True)
                                row.operator("object.lattice_add_mask", text="Add Mask", icon='BRUSH_MASK') 
                                
                    if bpy.context.object.mode == "SCULPT":
                        
                            row = box.row(align=True)
                            row.operator("object.valid_lattice_mask", text="Valid Mask", icon='FILE_TICK') 
                        
                        
            elif len([obj for obj in context.selected_objects]) >= 2:
                box = layout.box()
                split = box.split()
                box = split.column(align=True)
                box.operator("object.connect_lattice", text="Connect To Lattice", icon='OUTLINER_OB_LATTICE')        
               

            elif len([obj for obj in context.selected_objects if obj.type == 'LATTICE' ]) == 1:
                box = layout.box()
                split = box.split()
                col = split.column(align=True)
                row = col.row(align=True)
                row.operator("operator.apply_lattice_objects", text="Apply Lattice", icon='FILE_TICK')
                row.operator("operator.remove_lattice_objects", text="", icon='X')   
                row = col.row(align=True)
                row.prop(context.object.data, "points_u")
                row = col.row(align=True)
                row.prop(context.object.data, "points_v")
                row = col.row(align=True)
                row.prop(context.object.data, "points_w")  
                
                
                row = col.row(align=True)
                row.prop(WM, "lattice_interp", text="")
                
                
# -----------------------------------------------------------------------------
#    Symmetrize
# -----------------------------------------------------------------------------                
def Symmetrize(self, context):
    """ Sub panel for the adding assets """
    layout = self.layout
    WM = context.window_manager
    toolsettings = context.tool_settings
    sculpt = toolsettings.sculpt
    
                    
    # Symmetrize
    if len([obj for obj in context.selected_objects if context.object is not None if obj.type == 'MESH' if bpy.context.object.mode in ["OBJECT","SCULPT"] ]) == 1:
        
        row = layout.row(align=True)
        row.prop(WM, "show_symmetrize", text="Symmetrize", icon='TRIA_UP' if WM.show_symmetrize else 'TRIA_DOWN')
        if self.show_help : 
            row.menu("view3d.help_symmetrize",text="", icon='TRIA_RIGHT')
        if WM.show_symmetrize:
            box = layout.box()
            split = box.split()
            box = split.column(align=True)
            row = box.row(align=True)
            row.operator("object.symmetrize", text = "+X to -X").symmetrize_axis = "positive_x"   
            row.operator("object.symmetrize", text = "-X to +X").symmetrize_axis = "negative_x"  
            row = box.row(align=True)
            row.operator("object.symmetrize", text = "+Y to -Y").symmetrize_axis = "positive_y"   
            row.operator("object.symmetrize", text = "-Y to +Y").symmetrize_axis = "negative_y"    
            row = box.row(align=True)
            row.operator("object.symmetrize", text = "+Z to -Z").symmetrize_axis = "positive_z"   
            row.operator("object.symmetrize", text = "-Z to +Z").symmetrize_axis = "negative_z"                              
# -----------------------------------------------------------------------------
#    Remesh/Decimate
# ----------------------------------------------------------------------------- 
def Remesh(self, context):
    """ Sub panel for the adding assets """
    layout = self.layout
    WM = context.window_manager
    toolsettings = context.tool_settings
    sculpt = toolsettings.sculpt
    obj = bpy.context.active_object
    
    # Remesh
    if len([obj for obj in context.selected_objects if context.object is not None if obj.type == 'MESH' if bpy.context.object.mode in ["OBJECT","SCULPT"]]) == 1:
        row = layout.row(align=True)
        row.prop(WM, "show_remesh", text="Remesh/Decimate", icon='TRIA_UP' if WM.show_remesh else 'TRIA_DOWN')
        if self.show_help : 
            row.menu("view3d.help_remesh",text="", icon='TRIA_RIGHT')
        if WM.show_remesh:
            
            # Remesh
            remesh = False
            smooth = False
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "REMESH":
                    remesh = True
                if mod.type == "SMOOTH":
                    smooth = True  
            if not remesh :
                if bpy.context.object.mode == "OBJECT":
                    box = layout.box()
                    split = box.split()
                    box = split.column(align=True)
                    box.operator("object.remesh", text="Remesh", icon='MOD_REMESH') 
                      
            if remesh and smooth :
                box = layout.box()
                split = box.split()
                col = split.column(align=True)
                row = col.row(align=True)
                row.operator("object.apply_remesh_smooth", text="Apply Remesh", icon='FILE_TICK')
                row.prop(WM, "hide_remesh_smooth", text="", icon='RESTRICT_VIEW_OFF' if WM.hide_remesh_smooth else 'RESTRICT_VIEW_ON')
                row.operator("object.remove_remesh_smooth", text="", icon='X') 
   
            if remesh:  
                row = col.row(align=True)
                row.prop(bpy.context.active_object.modifiers["R_Remesh"], "octree_depth", text="Remesh Depth")
              
            if smooth:
                row = col.row(align=True)
                row.prop(bpy.context.active_object.modifiers["R_Smooth"], "iterations", text="Smooth Repeat")
                
        
            # Decimate
            decimate = False
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "DECIMATE":
                    decimate = True
                    
            if not decimate :
                if bpy.context.object.mode == "SCULPT":
                    box = layout.box()
                    split = box.split()
                    box = split.column(align=True)
                    box.operator("object.decimate_mask", text="Mask Decimate", icon='MOD_DECIM') 
            
                elif bpy.context.object.mode == "OBJECT":
                    box = layout.box()
                    split = box.split()
                    box = split.column(align=True)
                    box.operator("object.decimate", text="Decimate", icon='MOD_DECIM')   
                       
            if decimate:
                box = layout.box()
                split = box.split()
                col = split.column(align=True)
                row = col.row(align=True)
                row.operator("object.apply_decimate", text="Apply Decimate", icon='FILE_TICK')
                row.prop(bpy.context.active_object.modifiers["Decimate"], "show_viewport", text="")
                row.operator("object.remove_decimate", text="", icon='X') 
                
                row = col.row(align=True)
                row.prop(bpy.context.active_object.modifiers["Decimate"], "ratio", text="Ratio")
                
                if bpy.context.object.mode == "OBJECT":
                    row = col.row(align=True)
                    if not bpy.context.object.modifiers["Decimate"].vertex_group :
                        row.operator("object.add_mask", text="Add Mask", icon='BRUSH_MASK') 
                        
                    else :
                        row.operator("object.edit_decimate_mask", text="Edit Mask", icon='BRUSH_MASK') 
                        row.prop(bpy.context.active_object.modifiers["Decimate"],"invert_vertex_group", text="", icon='ARROW_LEFTRIGHT') 
                        row.operator("object.remove_mask", text="", icon='X')  
                    
                elif bpy.context.object.mode == "SCULPT":
                    row = col.row(align=True)    
                    row.operator("object.valid_decimate_mask", text="Valid Mask", icon='FILE_TICK') 


# -----------------------------------------------------------------------------
#    Extract Mask
# -----------------------------------------------------------------------------
def ExtractMask(self, context):
    """ Sub panel for the adding assets """
    layout = self.layout
    WM = context.window_manager
    toolsettings = context.tool_settings
    sculpt = toolsettings.sculpt
    obj = bpy.context.active_object

    # Extract Mask
    if len([obj for obj in context.selected_objects if context.object is not None if obj.type == 'MESH' if bpy.context.object.mode in ["OBJECT", "SCULPT"]]) == 1:
        
        row = layout.row(align=True)
        row.prop(WM, "show_extract", text="Mask Operations", icon='TRIA_UP' if WM.show_extract else 'TRIA_DOWN')
        if self.show_help : 
            row.menu("view3d.help_extract_mask",text="", icon='TRIA_RIGHT')
        if WM.show_extract:
            if bpy.context.object.mode == "SCULPT":
                box = layout.box()
                box.prop(WM, "extract_cut_delete", expand=True)
                
                if WM.extract_cut_delete == 'extract':
                    split = box.split()
                    col = split.column(align=True)  
                    col.prop(WM, "add_solidify", text="Add Solidify")
                    if WM.add_solidify :
                        split = box.split()
                        col = split.column(align=True)
                        col.prop(WM, "solidify_thickness", text="Thickness")
                        col.prop(WM, "solidify_offset", text="Offset")
                        col.prop(WM, "rim_only", text="Rim Only")
                        col.prop(WM, "apply_solidify", text="Apply Solidify")
                    col.prop(WM, "comeback_in_sculpt_mode", text="Go To Sculpt")
                    col.separator()
                    col.operator("object.extract_mask", text ="Extract mask", icon ='BRUSH_TEXMASK') 
                 
                 
                if WM.extract_cut_delete == 'cut': 
                    split = box.split()
                    col = split.column(align=True)  
                    col.prop(WM, "comeback_in_sculpt_mode", text="Go To Sculpt")
                    col.operator("object.cut_by_mask", text="Cut Masked Part") 
                    

                if WM.extract_cut_delete == 'duplicate': 
                    split = box.split()
                    col = split.column(align=True)   
                    col.prop(WM, "comeback_in_sculpt_mode", text="Go To Sculpt")  
                    col.operator("object.duplicate_by_mask", text="Duplicate Masked Part") 
                    
                
                if WM.extract_cut_delete == 'remove': 
                    split = box.split()
                    col = split.column(align=True)   
                    col.operator("object.delete_by_mask", text="Delete Masked Part")                     


            elif bpy.context.object.mode == "OBJECT":
                box = layout.box()
                split = box.split()
                box = split.column(align=True)
                
                solidify = False
                for mod in bpy.context.active_object.modifiers:
                    if mod.type == "SOLIDIFY":
                        solidify = True
                if solidify:  
                    split = box.split()
                    col = split.column(align=True)
                    col.prop(bpy.context.active_object.modifiers["Solidify"], "thickness", text="Thickness")
                    col.prop(bpy.context.active_object.modifiers["Solidify"], "offset", text="Offset")  
                    col.prop(bpy.context.active_object.modifiers["Solidify"], "use_rim_only", text="Only Rim")     

                else:  
                    row = box.row(align=True) 
                    row.operator("object.add_extract_mask", text="Add Mask", icon='BRUSH_MASK')   


# -----------------------------------------------------------------------------
#    Quick Pose
# ----------------------------------------------------------------------------- 
def QuickPose(self, context):
    """ Sub panel for the adding assets """
    layout = self.layout
    WM = context.window_manager
    obj = bpy.context.active_object
    
    
    if len([obj for obj in context.selected_objects if obj.type == 'MESH']) == 1:
        row = layout.row(align=True)
        row.prop(WM, "show_quickpose", text="Quick Pose", icon='TRIA_UP' if WM.show_quickpose else 'TRIA_DOWN')
        if self.show_help : 
            row.menu("view3d.help_quick_pose",text="", icon='TRIA_RIGHT')
        if WM.show_quickpose:
            # Armature
            armature = False
            for mod in bpy.context.active_object.modifiers:
                if mod.type == "ARMATURE":
                    armature = True
                    
            if not armature :
                if bpy.context.object.mode == "SCULPT":
                    box = layout.box()
                    split = box.split()
                    col = split.column(align=True)
                    row = col.row(align=True)
                    row.operator("object.quick_pose_add_mask", text="Add Mask", icon='BRUSH_MASK') 
                    box.operator("object.quick_pose_create_bones", text="Create Bones", icon='POSE_HLT')             
                    
                elif bpy.context.object.mode == "OBJECT":
                    box = layout.box()
                    split = box.split()
                    col = split.column(align=True)
                    row = col.row()
                    row.prop(WM, "use_mask", text="Use Mask")
                    row = col.row()
                    if WM.use_mask:
                        row.operator("object.quick_pose_add_mask", text="Add Mask", icon='BRUSH_MASK')
                    else :
                        box.operator("object.quick_pose_create_bones", text="Create Bones", icon='POSE_HLT')   
                 
                elif bpy.context.object.mode == 'EDIT': 
                    
                    bs_vertex = True
                    for obj in bpy.context.selected_objects:
                        if obj.name != "BS_Vertex" :
                            bs_vertex = False
                            break
                    if bs_vertex :    
                        box = layout.box()
                        split = box.split()
                        col = split.column(align=True)
                        row = col.row()
                        box.operator("object.quick_pose_convert_bones", text="Pose", icon='ARMATURE_DATA')
                    
                
           
            if armature:
                
                if bpy.context.object.mode == "OBJECT":
                    box = layout.box()
                    split = box.split()
                    col = split.column(align=True)
                    row = col.row(align=True)
                    if not "Armature" in obj.modifiers:    
                        if WM.use_mask:
                            row.operator("object.quick_pose_add_mask", text="Add Mask", icon='BRUSH_MASK') 
                        else :
                            row.operator("object.quick_pose_create_bones", text="Create Bones", icon='POSE_HLT')       
                        
                    else :
                        row.prop(bpy.context.active_object.modifiers["Armature"], "show_viewport", text="Hide Armature")

                        row.operator("object.apply_quick_pose_modifier", text="", icon='FILE_TICK')
                        row.operator("object.remove_quick_pose_modifier", text="", icon='X')
                        
                        
                        if WM.use_mask:
                            row = col.row(align=True)
                            row.operator("object.edit_quick_pose_mask", text="Edit Mask", icon='BRUSH_MASK')
                            row = col.row(align=True)
                            row.operator("object.quick_pose_smooth_mask", text="Smooth Mask", icon='BRUSH_SMOOTH')
                        
                elif bpy.context.object.mode == "SCULPT":
                    box = layout.box()
                    split = box.split()
                    row = split.row(align=True)   
                    row.operator("object.valid_quick_pose_mask", text="Valid Mask", icon='FILE_TICK') 


# Panel                 
class SpeedSculptMenu(bpy.types.Panel):
    bl_idname = "speedsculpt_menu"
    bl_label = "SpeedSculpt"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    
    def draw(self, context):
        layout = self.layout
        WM = context.window_manager
        toolsettings = context.tool_settings
        sculpt = toolsettings.sculpt
        obj = context.active_object
        
        if context.object is not None and bpy.context.object.mode == 'POSE': 
            
            layout.operator("object.symmetrize_bones", text="Symmetrize Bones", icon='OUTLINER_OB_ARMATURE') 
            
        elif context.object is not None and bpy.context.object.mode == 'EDIT' and obj.type == 'ARMATURE':   
            layout.operator("object.update_armature", text="Update Armature", icon='OUTLINER_OB_ARMATURE')

        else:    
            if bpy.context.area.type == 'VIEW_3D':
                col = layout.column()
                sub = col.column(align=True)
                row = sub.row(align=True)
                row.scale_y = 1.5
                row.scale_x = 1.5
                
                if hasattr(sculpt, "constant_detail"):
                    row.prop(sculpt, "constant_detail")
                else:
                    row.prop(sculpt, "constant_detail_resolution")   
                         
            if context.object is not None and bpy.context.object.mode == 'SCULPT':
                row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
            
#            if context.object is not None and not bpy.context.object.mode == 'EDIT' and not obj.type == "CURVE": 
            if context.object is not None and not bpy.context.object.mode == 'EDIT':     
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator("object.update_dyntopo", text="", icon='FILE_TICK')
                
                if len([obj for obj in context.selected_objects]) == 1:
                    if not bpy.context.object.mode in ["SCULPT","POSE"]:
                        if obj.modifiers:
                            if "Mirror_primitive" in obj.modifiers:
                                row = sub.row(align=True)
                                row.scale_y = 1.5
                                row.operator("object.boolean_sculpt_union_difference", text = "Union/Apply Modifiers", icon="MOD_BOOLEAN").operation_type = 'UNION'
                
                meta_objects = False
                no_modifiers = True
                if len(bpy.context.selected_objects) >= 2:
                # if len([obj for obj in context.selected_objects if context.object is obj.type in ['MESH', 'META'] if bpy.context.object.mode in ["OBJECT", "SCULPT"]]) >= 2:
                    if not bpy.context.object.mode in ["SCULPT","POSE"]:
                        for obj in bpy.context.selected_objects:
                            if obj.modifiers :
                                no_modifiers = False
                                break 
                            if obj.type == 'META' :
                                meta_objects = True
                                
                        if no_modifiers and not meta_objects :  
                            row = sub.row(align=True)
                            row.scale_y = 1.5  
                            row.operator("object.boolean_sculpt_rebool", text="R  ", icon="MOD_BOOLEAN") 
                            row.operator("object.boolean_sculpt_union_difference", text = "D  ", icon="MOD_BOOLEAN").operation_type = 'DIFFERENCE'
                            row.operator("object.boolean_sculpt_union_difference", text = "U  ", icon="MOD_BOOLEAN").operation_type = 'UNION'
                        else:
                            row = sub.row(align=True)
                            row.scale_y = 1.5
                            row.operator("object.boolean_sculpt_union_difference", text = "Union", icon="MOD_BOOLEAN").operation_type = 'UNION'
                    
            
            Options(self, context)
            AddPrimitives(self, context)
            Lattice(self, context)
            Symmetrize(self, context)
            Remesh(self, context)
            ExtractMask(self, context)
            QuickPose(self, context)
        
        
                        
        
# Panel                 
class SpeedSculptMenuUI(bpy.types.Panel):
    bl_label = "SpeedSculpt"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        WM = context.window_manager
        toolsettings = context.tool_settings
        sculpt = toolsettings.sculpt
        obj = context.active_object

        if context.object is not None and bpy.context.object.mode == 'POSE':

            layout.operator("object.symmetrize_bones", text="Symmetrize Bones", icon='OUTLINER_OB_ARMATURE')

        elif context.object is not None and bpy.context.object.mode == 'EDIT' and obj.type == 'ARMATURE':
            layout.operator("object.update_armature", text="Update Armature", icon='OUTLINER_OB_ARMATURE')

        else:
            if bpy.context.area.type == 'VIEW_3D':
                col = layout.column()
                sub = col.column(align=True)
                row = sub.row(align=True)
                row.scale_y = 1.5
                row.scale_x = 1.5

                if hasattr(sculpt, "constant_detail"):
                    row.prop(sculpt, "constant_detail")
                else:
                    row.prop(sculpt, "constant_detail_resolution")

            if context.object is not None and bpy.context.object.mode == 'SCULPT':
                row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')

                #            if context.object is not None and not bpy.context.object.mode == 'EDIT' and not obj.type == "CURVE":
            if context.object is not None and not bpy.context.object.mode == 'EDIT':
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator("object.update_dyntopo", text="", icon='FILE_TICK')

                if len([obj for obj in context.selected_objects]) == 1:
                    if not bpy.context.object.mode in ["SCULPT", "POSE"]:
                        if obj.modifiers:
                            if "Mirror_primitive" in obj.modifiers:
                                row = sub.row(align=True)
                                row.scale_y = 1.5
                                row.operator("object.boolean_sculpt_union_difference", text="Union/Apply Modifiers",
                                             icon="MOD_BOOLEAN").operation_type = 'UNION'

                meta_objects = False
                no_modifiers = True
                if len(bpy.context.selected_objects) >= 2:
                    if not bpy.context.object.mode in ["SCULPT", "POSE"]:
                        for obj in bpy.context.selected_objects:
                            if obj.modifiers:
                                no_modifiers = False
                                break
                            if obj.type == 'META':
                                meta_objects = True

                        if no_modifiers and not meta_objects:
                            row = sub.row(align=True)
                            row.scale_y = 1.5
                            row.operator("object.boolean_sculpt_rebool", text="R  ", icon="MOD_BOOLEAN")
                            row.operator("object.boolean_sculpt_union_difference", text="D  ",
                                         icon="MOD_BOOLEAN").operation_type = 'DIFFERENCE'
                            row.operator("object.boolean_sculpt_union_difference", text="U  ",
                                         icon="MOD_BOOLEAN").operation_type = 'UNION'
                        else:
                            row = sub.row(align=True)
                            row.scale_y = 1.5
                            row.operator("object.boolean_sculpt_union_difference", text="Union",
                                         icon="MOD_BOOLEAN").operation_type = 'UNION'

            Options(self, context)
            AddPrimitives(self, context)
            Lattice(self, context)
            Symmetrize(self, context)
            Remesh(self, context)
            ExtractMask(self, context)
            QuickPose(self, context)
                    
          
            
            
            