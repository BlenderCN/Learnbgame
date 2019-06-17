#####################################################################################
# Copyright (C) 2014-2014 Blender Muscle Tools
# based on code by Coloremblem copyright (C) 2014-2014 Blender Muscle Tools
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher
#####################################################################################

bl_info = {
    "name" : "Muscle Tools",
    "author" : "Tristan Salzmann",
    "version" : (1, 4),
    "blender" : (2, 71, 0),
    "location" : "View3D > Tools",
    "description" : "An interface to create muscles in Blender and adjust them",
    "category" : "Rigging"}
    
#
#START BLENDER MUSCLE TOOLS
#


import bpy
from bpy.props import *

import mathutils
from math import pi


#
#MUSCLE DEPENDENCY UPDATE START
#

class updateDependencies(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Update Dependencies"
    bl_category = "Muscle"
    
    def draw(self, context):
        layout = self.layout
        layout.label("Update Buttons", icon="FILE_BACKUP")
        col = layout.split().column(align=True)
        col.operator("update.props", icon="FILE_REFRESH")
        col.operator("update.drivers", icon="LOAD_FACTORY")
        
        col.operator("muscle.components", icon="FULLSCREEN_EXIT")
       
        
#CREATE AN UPDATE PROPERTIES BUTTON
class updateProperties(bpy.types.Operator):
    bl_idname = "update.props"
    bl_label = "Update Properties"
    bl_description = "Updates all muscle properties"
    
    def execute(self, context):
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except:
            print("ALREADY IN OBJECT MODE")
        bpy.ops.mesh.primitive_cube_add(radius=1)
        actObj = bpy.context.active_object
        actObj.name = "proxy_muscle_prop_mesh"
        
        #BASE LENGHT
        bpy.types.Object.Base_Lenght = FloatProperty(
            name = "Base Lenght",
            min = 1.000, max = 2.000,
            description = "sets the distance between the muscle bone and the controller",
            default = 1.000)
        
        #JIGGLE CONTROL
        bpy.types.Object.Jiggle_Control = FloatProperty(
            name = "Jiggle Control",
            min = 0.000, max = 1.000,
            description = "sets how much the jiggle is controlled",
            default = 0.500)
            
        #JIGGLE DAMPING
        bpy.types.Object.Jiggle_Damping = FloatProperty(
            name = "Jiggle Damping",
            min = 0.000, max = 50.000,
            description = "sets how much the jiggle is damped",
            default = 1.000)
            
        #JIGGLE MASS
        bpy.types.Object.Jiggle_Mass = FloatProperty(
            name = "Jiggle Mass",
            min = 0.000, max = 1.000,
            description = "sets the weight of the jiggle",
            default = 0.500)
            
        #JIGGLE STIFFNESS
        bpy.types.Object.Jiggle_Stiffness = FloatProperty(
            name = "Jiggle Stiffness",
            min = 0.000, max = 1.000,
            description = "sets the stiffness of the jiggle",
            default = 0.800)
            
        #MUSCLE SHAPE
        bpy.types.Object.Muscle_Shape = FloatProperty(
            name = "Muscle Shape",
            min = -1.000, max = 1.000,
            description = "sets the shape of the muscle by its shapekeys which got created",
            default = 0.000)
            
        #JIGGLE RENDER
        bpy.types.Object.Jiggle_Render = BoolProperty(
            description = "sets if the jiggle is visible in the render",
            name = "Jiggle Render")
            
        #RENDER RESOLUTION
        bpy.types.Object.Render_Resolution = IntProperty(
            name = "Render Resolution",
            min = 0, max = 3,
            description = "subdivisions of the muscle in the render",
            default = 0)
            
        #VIEW RESOLUTION
        bpy.types.Object.View_Resolution = IntProperty(
            name = "View Resolution",
            min = 0, max = 3,
            description = "subdivisions of the muscle",
            default = 0)
            
        #JIGGLE_VIEW
        bpy.types.Object.Jiggle_View = BoolProperty(
            description = "sets if the jiggle is visible in the 3D View",
            name = "Jiggle View")
            
        #VOLUME
        bpy.types.Object.Volume = IntProperty(
            name = "Volume",
            min = 0, max = 100,
            description = "sets how big and thin the muscle gets by stretching or squashing it",
            default = 1)
            
        #SET THE OBJECTS RNA PROPS
        actObj.Base_Lenght = 1
        actObj.Jiggle_Control = 0.5
        actObj.Jiggle_Damping = 1
        actObj.Jiggle_Mass = 0.5
        actObj.Jiggle_Stiffness = 0.8
        actObj.Muscle_Shape = 0
        actObj.Jiggle_Render = False
        actObj.Render_Resolution = 0
        actObj.View_Resolution = 0
        actObj.Jiggle_View = False
        actObj.Volume = 1
        
        bpy.ops.object.delete(use_global=False)
        
        return{"FINISHED"}
    
    
#CREATE AN UPDATE DRIVERS BUTTON
class updateProperties(bpy.types.Operator):
    bl_idname = "update.drivers"
    bl_label = "Update Drivers"
    bl_description= "Updates all drivers from selected muscle objects"
    
    def execute(self, context):
        try:
            for a in range(len(bpy.context.selected_objects)):
                try:
                    #PROPERTIES DRIVER UPDATE
                    for b in range(len(bpy.context.selected_objects[a].animation_data.drivers)):
                        bpy.data.objects[bpy.context.selected_objects[a].name].animation_data.drivers[b].driver.type = "AVERAGE"
                        
                        #SHAPE KEY DRIVER UPDATE
                        for s in range(len(bpy.data.objects[bpy.context.selected_objects[a].name].data.shape_keys.animation_data.drivers)):
                            bpy.data.objects[bpy.context.selected_objects[a].name].data.shape_keys.animation_data.drivers[s].driver.type = "AVERAGE"
                        
                        #PARENT ARMATURE DRIVER UPDATE
                        parentArm = bpy.data.objects[bpy.context.selected_objects[a].name].parent
                        
                        for c in range(len(parentArm.animation_data.drivers)):
                            parentArm.animation_data.drivers[c].driver.type = "AVERAGE"
                        
                        
                except:
                    self.report({"ERROR"}, str(bpy.context.selected_objects[a].name)+" was failed to adjust")
        except:
            self.report({"ERROR"}, "Select at least one muscle")
        return{"FINISHED"}
    

#
#MUSCLE DEPENDENCY UPDATE END
#

#
#CREATE MUSCLE LAYOUT START
#

class createMuscle(bpy.types.Panel):
    bl_space_type="VIEW_3D"
    bl_region_type="TOOLS"
    bl_label="Muscle Creator"
    bl_category="Muscle" 
    
    def draw(self, context):
        layout = self.layout
        
        layout.label("Build a Muscle", icon ="META_ELLIPSOID")
        
        layout.operator("create.button", text="Create muscle object")
        try:
            #CHECK IF OBJECT IS A MESH AND IF IT HAS A PROPERTY CALLED "musName"
            if bpy.context.active_object.type == "MESH" and any("musName" in s for s in bpy.context.active_object.items()):
                
                col = layout.column(align=True)
                
                col.prop(bpy.context.active_object, "musName")
                col.prop(bpy.context.active_object, "musSmooth")
                col.prop(bpy.context.active_object, "musSize")
                col.prop(bpy.context.active_object, "musRadius")
                col.operator("update.button", text="Update muscle object")
                
        except:
            print("NO MUSCLE SELECTED")

#
#CREATE MUSCLE LAYOUT END
#        




#
#CREATE MUSCLE BUTTON START
#

class createButton(bpy.types.Operator):
    bl_idname="create.button"
    bl_label="Create Muscle"
    bl_description="Creates a custom muscle which you can edit"
    
    def execute(self, context):
           
            #create 5 verts, string them together to make 5 edges.  
            coord1 = (-2.0, 0.0, 0.0)  
            coord2 = (-1.0, 0.0, -0.5)  
            coord3 = (0.0, 0.0, -0.8)  
            coord4 = (1.0, 0.0, -0.5)
            coord5 = (2.0, 0.0, 0.0)   
              
            Verts = [coord1, coord2, coord3, coord4, coord5]  
            Edges = [[0,1],[1,2],[2,3],[3,4]]  
              
            muscle_mesh = bpy.data.meshes.new("Muscle_Data")  
            muscle_mesh.from_pydata(Verts, Edges, [])  
            muscle_mesh.update()  
            
            #Check if muscle name already exists
            cloneCounter = 0
            for a in bpy.data.objects:
                if any("Muscle" in c.name for c in bpy.data.objects):
                    cloneCounter = cloneCounter + 1
            
            if cloneCounter == 0:
                muscleMain = "Muscle" 
                  
            else:
                if any("Muscle" in s.name for s in bpy.data.objects):
                    muscleMain = "Muscle." + str(cloneCounter+1)
                            
            muscle_object = bpy.data.objects.new(muscleMain, muscle_mesh)  
            muscle_object.data = muscle_mesh  
              
            scene = bpy.context.scene  
            scene.objects.link(muscle_object)
            bpy.context.scene.objects.active = bpy.data.objects[muscleMain]
            
            
            # Add screw modifier for screwing the muscle shape
            bpy.ops.object.modifier_add(type='SCREW')
            bpy.context.object.modifiers["Screw"].axis = 'X'
            bpy.context.object.modifiers["Screw"].use_normal_flip = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Screw")
            
            actObj = bpy.context.active_object
            
            #
            #CREATE PROPERTIES START
            #

            #Muscle Name
            bpy.types.Object.musName = StringProperty(
            name="Name", default="newMuscle", description="Name of the muscle")

            #Muscle Size
            bpy.types.Object.musSize = FloatProperty(
            name="Size", default=1.0, min=0.0, max=10.0, description="Size of the muscle")

            #Muscle Radius
            bpy.types.Object.musRadius = FloatProperty(
            name="Radius", default=1.0, min=0.0, max=10.0, description="Radius of the muscle")

            #Muscle Smooth
            bpy.types.Object.musSmooth = IntProperty(
            name="Smooth", default=1, min=0, max=3, description="Smooth factor of the muscle")
            
            actObj.musName = "newMuscle"
            actObj.musSize = 1.0
            actObj.musRadius = 1.0
            actObj.musSmooth = 1
            
            #
            #CREATE PROPERTIES END
            #
        
            return{"FINISHED"}

#
#CREATE MUSCLE BUTTON END
#




#
#CREATE UPDATE BUTTON START
#

class updateButton(bpy.types.Operator):
    bl_idname="update.button"
    bl_label="Update"
    bl_description="Updates the values you have entered"
    
    def execute(self, context):
            
        
            #Set Values to Muscle
            
            #Name to muscle
            bpy.context.active_object.name = bpy.context.active_object.musName
            
            #Scale to muscle
            bpy.context.active_object.scale[0] = bpy.context.active_object.musSize
            bpy.context.active_object.scale[1] = bpy.context.active_object.musSize
            bpy.context.active_object.scale[2] = bpy.context.active_object.musSize
            
            #Radius to muscle
            bpy.context.active_object.scale[1] = bpy.context.active_object.musRadius
            bpy.context.active_object.scale[2] = bpy.context.active_object.musRadius
            
            #Smooth to muscle
            checkS = 1
            try:
                if bpy.context.object.modifiers["Subsurf"].name == "Subsurf":
                    checkS = 1
            except:
                checkS = 0
                
            
            if bpy.context.active_object.musSmooth > 0 and checkS == 0:
                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subsurf"].levels = bpy.context.active_object.musSmooth   
            
            elif bpy.context.active_object.musSmooth > 0 and checkS == 1:
                bpy.context.object.modifiers["Subsurf"].levels = bpy.context.active_object.musSmooth
            else:
                bpy.ops.object.modifier_remove(modifier="Subsurf")

    
            return{"FINISHED"}

#
#CREATE UPDATE BUTTON END
#


#
#MUSCLE SHAPE PANEL
#

class muscleTool(bpy.types.Panel):     # panel to display new property
    bl_space_type = "VIEW_3D"       # show up in: 3d-window
    bl_region_type = "TOOLS"           # show up in: Tools panel
    bl_label = "Muscle Shape"           # name of the new panel
    bl_category = "Muscle"
 
    def draw(self, context):
        
        #define variables to safe namespaces
        layout = self.layout
        row = layout.row()
        
        #VARIBALES FOR HIDING THE PANEL OR NOT
        try:
            propCount = len(bpy.context.active_object.items())
        except:
            layout.label("No object selected")
        
        row.label("Shape Control", icon = "MOD_SUBSURF")

        # display "Properties" ID-property, of the active object
        try:
            if propCount >= 11:
                layout = self.layout
                col = layout.column(align=True)
                
                col.prop(bpy.context.active_object, "View_Resolution")
                col.prop(bpy.context.active_object, "Render_Resolution")
                col.prop(bpy.context.active_object, "Muscle_Shape", slider=True)
                col.prop(bpy.context.active_object, "Base_Lenght", slider=True)
                col.prop(bpy.context.active_object, "Volume", slider=True)
            else:
                row = layout.row()
                row.label("select a muscle")
        except:
            print("NO OBJECT SELECTED")
            
#
#JIGGLE TOOL PANEL
#
        
class jiggleTool(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Muscle Jiggle"
    bl_category = "Muscle"
    
    def draw(self, context): 
        
        #define variables to safe namespaces
        layout = self.layout
        row = layout.row()
        
        #VARIBALES FOR HIDING THE PANEL OR NOT
        try:
            propCount = len(bpy.context.active_object.items())
        except:
            layout.label("No object selected")
               
        row.label("Jiggle control", icon="MOD_WARP")
        
        # display "Properties" ID-property, of the active object
        try:
            if propCount >= 11:
                layout = self.layout
                col = layout.column(align=True)
                
                col.prop(bpy.context.active_object, "Jiggle_View")
                col.prop(bpy.context.active_object, "Jiggle_Render")
                col.prop(bpy.context.active_object, "Jiggle_Control", slider=True)
                col.prop(bpy.context.active_object, "Jiggle_Mass", slider=True)
                col.prop(bpy.context.active_object, "Jiggle_Stiffness", slider=True)
                col.prop(bpy.context.active_object, "Jiggle_Damping", slider=True)
                col.prop_search(bpy.context.active_object.modifiers["muscle_softbody"].settings, "vertex_group_goal", bpy.context.active_object, "vertex_groups", text="Vertex Group")
            else:
                row = layout.row()
                row.label("select a muscle")
        except:
            print("NO OBJECT SELECTED")

#     
#ADD PROPERTIES
#

#CREATE MUSCLE NAME PROPERTY
bpy.types.Scene.MusGrpProp = StringProperty(
    name = "Name",
    default = "enter name",
    description = "Name of the converted muscle")

#CREATE THE USE NAME PROPERTY
bpy.types.Scene.useObjName = BoolProperty(
    name ="Use object name",
    default=False, 
    description="Uses the name of the object as the muscle name")


        
#
#MAKE MUSCLE CONVERT PANEL 
# 
class makeMusclePara(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Muscle Options"
    bl_category = "Muscle"
    
    def draw(self, context):
        
        layout = self.layout
        row = layout.row()
        split = layout.split()
        col = split.column(align=True)
               
        row.label("Convert Object to Muscle", icon="SNAP_NORMAL")
        col.prop(bpy.context.scene, 'useObjName')
        col.prop(bpy.context.scene, 'MusGrpProp')    
        col.operator('make.muscle')
        col.operator('delete.muscle')
        
        split = layout.split()
        col = split.column(align=True)
       
        
        #BIND TO SKIN TAB 
        layout = self.layout
        row = layout.row()
        split = layout.split()
        col = split.column(align=True)
              
        col.label("Bind to Skin", icon="MOD_ARMATURE")
        col.operator('bind.stretchmuscle')



#DEFINE MUSCLE PARAM BUTTON       
class OBJECT_OT_makeMuscle(bpy.types.Operator):
    bl_label = "Convert to Muscle" #Button label
    bl_idname = "make.muscle" #Name used to refer to this operator
    bl_description = "Converts the selected object to a muscle object" # tooltip
    
    
###START SET CONVERT PARAMETERS    
    
    def execute(self,context):
        try:
            
            if bpy.context.scene.useObjName == True:
                bpy.context.scene.MusGrpProp = bpy.context.active_object.name 
                    
            if bpy.context.active_object.type != "MESH":
                self.report({'ERROR'}, "Please Select a Object with Mesh Type")
            
            elif bpy.context.scene['MusGrpProp'] == "":
                self.report({"ERROR"}, "Please Insert a name for your muscle")
                
            elif any(str(bpy.context.scene.MusGrpProp)+"_grp" in g.name for g in bpy.data.groups):
                self.report({"ERROR"}, "Group already exists please choose another muscle name")
            
            else:
                
                #DELETE MUSCLE BUILD PROPERTIES
                try:
                    bpy.ops.wm.properties_remove(data_path = 'object', property = 'musName')                    
                    bpy.ops.wm.properties_remove(data_path = 'object', property = 'musSmooth')
                    bpy.ops.wm.properties_remove(data_path = 'object', property = 'musRadius')
                    bpy.ops.wm.properties_remove(data_path = 'object', property = 'musSize')
                except:
                    print("NO PROPERTIES FOUND TO DELETE")

                    
                
                #GET OBJECT INFORMATION
                GrpName = bpy.context.scene['MusGrpProp']
                bpy.context.object.name = GrpName
                SelObj = bpy.context.object
                DimX = bpy.context.object.dimensions[0]
                DimY = bpy.context.object.dimensions[1]
                DimZ = bpy.context.object.dimensions[2]
                
                #SET HIGHEST DIMENSION IN ATTRIBUTE
                if DimX >= DimY and DimX >= DimZ :
                    maxDim = DimX
                    
                elif DimY >= DimX and DimY >= DimZ:
                    maxDim = DimY
                
                elif DimZ >= DimX and DimZ >= DimY:
                    maxDim = DimZ
        #
        #START ADD OBJECT PROPERTYS
        #
                
                #BASE LENGHT
                bpy.types.Object.Base_Lenght = FloatProperty(
                    name = "Base Lenght",
                    min = 1.000, max = 2.000,
                    description = "sets the distance between the muscle bone and the controller",
                    default = 1.000)
                
                #JIGGLE CONTROL
                bpy.types.Object.Jiggle_Control = FloatProperty(
                    name = "Jiggle Control",
                    min = 0.000, max = 1.000,
                    description = "sets how much the jiggle is controlled",
                    default = 0.500)
                    
                #JIGGLE DAMPING
                bpy.types.Object.Jiggle_Damping = FloatProperty(
                    name = "Jiggle Damping",
                    min = 0.000, max = 50.000,
                    description = "sets how much the jiggle is damped",
                    default = 1.000)
                    
                #JIGGLE MASS
                bpy.types.Object.Jiggle_Mass = FloatProperty(
                    name = "Jiggle Mass",
                    min = 0.000, max = 1.000,
                    description = "sets the weight of the jiggle",
                    default = 0.500)
                    
                #JIGGLE STIFFNESS
                bpy.types.Object.Jiggle_Stiffness = FloatProperty(
                    name = "Jiggle Stiffness",
                    min = 0.000, max = 1.000,
                    description = "sets the stiffness of the jiggle",
                    default = 0.800)
                    
                #MUSCLE SHAPE
                bpy.types.Object.Muscle_Shape = FloatProperty(
                    name = "Muscle Shape",
                    min = -1.000, max = 1.000,
                    description = "sets the shape of the muscle by its shapekeys which got created",
                    default = 0.000)
                    
                #JIGGLE RENDER
                bpy.types.Object.Jiggle_Render = BoolProperty(
                    description = "sets if the jiggle is visible in the render",
                    name = "Jiggle Render")
                    
                #RENDER RESOLUTION
                bpy.types.Object.Render_Resolution = IntProperty(
                    name = "Render Resolution",
                    min = 0, max = 3,
                    description = "subdivisions of the muscle in the render",
                    default = 0)
                    
                #VIEW RESOLUTION
                bpy.types.Object.View_Resolution = IntProperty(
                    name = "View Resolution",
                    min = 0, max = 3,
                    description = "subdivisions of the muscle",
                    default = 0)
                    
                #JIGGLE_VIEW
                bpy.types.Object.Jiggle_View = BoolProperty(
                    description = "sets if the jiggle is visible in the 3D View",
                    name = "Jiggle View")
                    
                #VOLUME
                bpy.types.Object.Volume = IntProperty(
                    name = "Volume",
                    min = 0, max = 100,
                    description = "sets how big and thin the muscle gets by stretching or squashing it",
                    default = 1)
                    
                #SET THE OBJECTS RNA PROPS
                SelObj.Base_Lenght = 1
                SelObj.Jiggle_Control = 0.5
                SelObj.Jiggle_Damping = 1
                SelObj.Jiggle_Mass = 0.5
                SelObj.Jiggle_Stiffness = 0.8
                SelObj.Muscle_Shape = 0
                SelObj.Jiggle_Render = False
                SelObj.Render_Resolution = 0
                SelObj.View_Resolution = 0
                SelObj.Jiggle_View = False
                SelObj.Volume = 1
                    
                #PRINT ALL RNA PROPERTIES FOR THE SELECTED OBJECT
                def printProp(rna, path):
                    try:
                        print('    %s%s =' % (rna.name, path), eval("rna"+path))
                    except:
                        print('    %s%s does not exist' % (rna.name, path))
         
                ob = bpy.context.object
                print("%s RNA properties" % ob)
                printProp(ob, ".Base_Lenght")
                printProp(ob, ".Jiggle_Control")
                printProp(ob, ".Jiggle_Damping")
                printProp(ob, ".Jiggle_Mass")
                printProp(ob, ".Jiggle_Stiffness")
                printProp(ob, ".Muscle_Shape")
                printProp(ob, ".Jiggle_Render")
                printProp(ob, ".Render_Resolution")
                printProp(ob, ".View_Resolution")
                printProp(ob, ".Jiggle_View")
                printProp(ob, ".Volume")
                print("%s ID properties" % ob)
                printProp(ob, "['Base_Lenght']")
                printProp(ob, "['Jiggle_Control']")
                printProp(ob, "['Jiggle_Damping']")
                printProp(ob, "['Jiggle_Mass']")
                printProp(ob, "['Jiggle_Stiffness']")
                printProp(ob, "['Muscle_Shape']")
                printProp(ob, "['Jiggle_Render']")
                printProp(ob, "['Render_Resolution']")
                printProp(ob, "['View_Resolution']")
                printProp(ob, "['Jiggle_View']")
                printProp(ob, "['Volume']")
                print("%s ID properties" % ob.data)
                printProp(ob, "['Base_Lenght']")
                printProp(ob, "['Jiggle_Control']")
                printProp(ob, "['Jiggle_Damping']")
                printProp(ob, "['Jiggle_Mass']")
                printProp(ob, "['Jiggle_Stiffness']")
                printProp(ob, "['Muscle_Shape']")
                printProp(ob, "['Jiggle_Render']")
                printProp(ob, "['Render_Resolution']")
                printProp(ob, "['View_Resolution']")
                printProp(ob, "['Jiggle_View']")
                printProp(ob, "['Volume']")
                
                

        #            
        #END ADD OBJECT PROPERTYS
        #
                
                #SET OBJECT ADJUSTMENTS
                bpy.ops.object.convert(target='MESH')
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
                       
                #ADD SHAPE_KEY PARAMETERS
                bpy.ops.object.shape_key_add(from_mix=False)
                bpy.context.object.shape_key_add(name=str(GrpName)+"_thin", from_mix=False)
                bpy.context.object.shape_key_add(name=str(GrpName)+"_fat", from_mix=False)
                
                #ADD JIGGLE PARAMETERS
                bpy.ops.object.modifier_add(type='SOFT_BODY')
                bpy.ops.object.modifier_add(type='SUBSURF')
                
                #ADD NEW GROUP
                bpy.ops.group.create(name= str(GrpName)+"_grp")
                MainGrpName = str(GrpName)+"_grp"
                
                #ADD DEFORM PARAMETERS
                bpy.ops.object.armature_add(location =(0,0,0))
                bpy.context.object.name = str(GrpName) + "_armature"
                bpy.data.armatures[0].name = str(GrpName)+"_armdata"
                bpy.ops.object.posemode_toggle()
                bpy.context.object.data.bones["Bone"].name = str(GrpName) + "_bone"
                bpy.ops.object.posemode_toggle()
                bpy.ops.transform.resize(value=(maxDim, maxDim, maxDim))
                bpy.ops.object.group_link(group=MainGrpName)
                armdata = str(GrpName)+"_armdata"
                armature = str(GrpName)+"_armature"
                bpy.context.object.draw_type = 'WIRE'



                
                #POSE GROUP OBJECTS
                bpy.ops.object.select_pattern(pattern = GrpName)
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.select_pattern(pattern = str(GrpName)+"_armature")
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                bpy.ops.object.select_all(action='TOGGLE')

                if maxDim == DimX:
                    
                    bpy.ops.object.select_pattern(pattern = str(GrpName)+"_armature")
                    bpy.ops.transform.rotate(value = 1.5708, axis=(0, 1, 0))
                    print("Rotatet on Y")
                    
                elif maxDim == DimY:
                    
                    bpy.ops.object.select_pattern(pattern = str(GrpName)+"_armature")
                    bpy.ops.transform.rotate(value = 1.5708, axis=(1, 0, 0))
                    print("Rotatet on X")
                    
                elif maxDim == DimZ:
                    
                    bpy.ops.object.select_pattern(pattern = str(GrpName)+"_armature")
                    bpy.ops.transform.rotate(value = 1.5708, axis=(0, 0, 0))
                    print("Not rotatet")
                
                bpy.ops.object.select_all(action='TOGGLE')
                
                #BIND ARMATURE TO OBJECT 
                bpy.ops.object.select_pattern(pattern = GrpName)
                bpy.ops.object.select_pattern(pattern = str(GrpName)+"_armature")
                bpy.ops.object.parent_set(type='BONE')
                bpy.ops.object.select_all(action='TOGGLE')
                
                #ADD STRETCH CONTROLLER
                bpy.ops.object.select_pattern(pattern = str(GrpName)+"_armature")
                bpy.ops.object.editmode_toggle()
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='TOGGLE')
                bpy.ops.object.empty_add(type='CUBE')
                bpy.context.object.empty_draw_size = 0.5
                bpy.context.object.name = str(GrpName) + "_stretch_ctrl"
                bpy.ops.object.group_link(group=MainGrpName)
                
                #ADD STRETCH CONSTRAINT
                bpy.ops.object.select_all(action='TOGGLE')
                bpy.context.scene.objects.active = bpy.data.objects[str(GrpName)+"_armature"]
                bpy.context.scene.objects.active
                bpy.ops.object.posemode_toggle()
                bpy.ops.pose.select_all(action='TOGGLE')
                bpy.ops.pose.constraint_add(type='STRETCH_TO')
                bpy.context.object.pose.bones[str(GrpName) + "_bone"].constraints["Stretch To"].target = bpy.data.objects[str(GrpName) + "_stretch_ctrl"]
                bpy.ops.object.posemode_toggle()
                bpy.ops.object.select_all(action='TOGGLE')
                bpy.context.scene.objects.active = bpy.data.objects[GrpName]
                bpy.context.scene.objects.active
                bpy.ops.object.modifier_move_up(modifier="Armature")
                bpy.ops.object.modifier_move_up(modifier="Armature")
                bpy.ops.object.select_all(action='TOGGLE')
                
        #        
        #START ADD DRIVERS
        #    
           
                #SELECT MUSCLE OBJECT
                bpy.context.scene.objects.active = bpy.data.objects[GrpName]
                bpy.context.scene.objects.active

        #Description Example//

        #
        #//SHAPE
        #
                
                #SUBDIVISION SURFACE VIEW RESOLUTION
                #Define which property should be driven
                SubsurfViewDrv = SelObj.driver_add('modifiers["Subsurf"].levels').driver   
                #Define the driver type 
                SubsurfViewDrv.type = 'AVERAGE'                                            
                #Define if the debug info should be shown
                SubsurfViewDrv.show_debug_info = True                                       

                #Create a new Driver Variable   
                SubsurfViewVar = SubsurfViewDrv.variables.new()                             
                #Define the name of the variable
                SubsurfViewVar.name = "view_resolution"                                     
                #Define the variable type
                SubsurfViewVar.type = 'SINGLE_PROP'                                         

                #Define a new Driver Target 
                SubsurfViewTar = SubsurfViewVar.targets[0]                                  
                #Define a new Driver id Type
                SubsurfViewTar.id_type = 'OBJECT'                                           
                #Define the Object which contains the custom property which drives the Property
                SubsurfViewTar.id = bpy.data.objects[GrpName]                               
                #Define the Custom Property of the object
                SubsurfViewTar.data_path = "View_Resolution" 
        #//        
                #SUBDIVISION SURFACE RENDER VIEW RESOLUTION
                SubsurfRenViewDrv = SelObj.driver_add('modifiers["Subsurf"].render_levels').driver
                SubsurfRenViewDrv.type = 'AVERAGE'
                SubsurfRenViewDrv.show_debug_info = True
                
                SubsurfRenViewVar = SubsurfRenViewDrv.variables.new()
                SubsurfRenViewVar.name = "render_resolution"
                SubsurfRenViewVar.type = 'SINGLE_PROP'
                
                SubsurfRenViewTar = SubsurfRenViewVar.targets[0]
                SubsurfRenViewTar.id_type = 'OBJECT'
                SubsurfRenViewTar.id = bpy.data.objects[GrpName]
                SubsurfRenViewTar.data_path = "Render_Resolution"

        #//        
                #MUSCLE THIN SHAPE
                MusThin = SelObj.data.shape_keys.driver_add('key_blocks["'+str(GrpName)+'_thin"].value')
                MusThinDrv = MusThin.driver
                MusThinDrv.type = 'AVERAGE'
                MusThinDrv.show_debug_info = True
                
                MusThinVar = MusThinDrv.variables.new()
                MusThinVar.name = "muscle_thin_shape"
                MusThinVar.type = 'SINGLE_PROP'
                
                MusThinTar = MusThinVar.targets[0]
                MusThinTar.id_type = 'OBJECT'
                MusThinTar.id = bpy.data.objects[GrpName]
                MusThinTar.data_path = "Muscle_Shape"
                
                MusThinMod = MusThin.modifiers[0]
                MusThinMod.mode = 'POLYNOMIAL'
                MusThinMod.poly_order = 1
                MusThinMod.coefficients = (0.0, -1.0)
        #//        
                #MUSCLE FAT SHAPE
                MusFat = SelObj.data.shape_keys.driver_add('key_blocks["'+str(GrpName)+'_fat"].value')
                MusFatDrv = MusFat.driver
                MusFatDrv.type = 'AVERAGE'
                MusFatDrv.show_debug_info = True
                
                MusFatVar = MusFatDrv.variables.new()
                MusFatVar.name = "muscle_fat_shape"
                MusFatVar.type = 'SINGLE_PROP'
                
                MusFatTar = MusFatVar.targets[0]
                MusFatTar.id_type = 'OBJECT'
                MusFatTar.id = bpy.data.objects[GrpName]
                MusFatTar.data_path = "Muscle_Shape"
                
                MusFatMod = MusFat.modifiers[0]
                MusFatMod.mode = 'POLYNOMIAL'
                MusFatMod.poly_order = 1
                MusFatMod.coefficients = (0.0, 1.0)
                

        #
        #//JIGGLE
        #go to object mode for adjusting jiggle propertys
             
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.scene.objects.active = bpy.data.objects[GrpName]
                bpy.context.scene.objects.active
                
                #JIGGLE VIEW
                JiggleViewDrv = SelObj.driver_add('modifiers["Softbody"].show_viewport').driver
                JiggleViewDrv.type = 'AVERAGE'
                JiggleViewDrv.show_debug_info = True
                
                JiggleViewVar = JiggleViewDrv.variables.new()
                JiggleViewVar.name = "jiggle_view"
                JiggleViewVar.type = 'SINGLE_PROP'
                
                JiggleViewTar = JiggleViewVar.targets[0]
                JiggleViewTar.id_type = 'OBJECT'
                JiggleViewTar.id = bpy.data.objects[GrpName]
                JiggleViewTar.data_path = "Jiggle_View"
        #//        
                #JIGGLE RENDER VIEW
                JiggleRenViewDrv = SelObj.driver_add('modifiers["Softbody"].show_render').driver
                JiggleRenViewDrv.type = 'AVERAGE'
                JiggleRenViewDrv.show_debug_info = True
                
                JiggleRenViewVar = JiggleRenViewDrv.variables.new()
                JiggleRenViewVar.name = "jiggle_render"
                JiggleRenViewVar.type = 'SINGLE_PROP'
                
                JiggleRenViewTar = JiggleRenViewVar.targets[0]
                JiggleRenViewTar.id_type = 'OBJECT'
                JiggleRenViewTar.id = bpy.data.objects[GrpName]
                JiggleRenViewTar.data_path = "Jiggle_Render"
        #//        
                #JIGGLE CONTROL
                JiggleControlDrv = SelObj.driver_add('modifiers["Softbody"].settings.goal_min').driver
                JiggleControlDrv.type = 'AVERAGE'
                JiggleControlDrv.show_debug_info = True
                
                JiggleControlVar = JiggleControlDrv.variables.new()
                JiggleControlVar.name = "jiggle_control"
                JiggleControlVar.type = 'SINGLE_PROP'
                
                JiggleControlTar = JiggleControlVar.targets[0]
                JiggleControlTar.id_type = 'OBJECT'
                JiggleControlTar.id = bpy.data.objects[GrpName]
                JiggleControlTar.data_path = "Jiggle_Control"
        #//        
                #JIGGLE DAMPING
                JiggleDampingDrv = SelObj.driver_add('modifiers["Softbody"].settings.goal_friction').driver
                JiggleDampingDrv.type = 'AVERAGE'
                JiggleDampingDrv.show_debug_info = True
                
                JiggleDampingVar = JiggleDampingDrv.variables.new()
                JiggleDampingVar.name = "jiggle_damping"
                JiggleDampingVar.type = 'SINGLE_PROP'
                
                JiggleDampingTar = JiggleDampingVar.targets[0]
                JiggleDampingTar.id_type = 'OBJECT'
                JiggleDampingTar.id = bpy.data.objects[GrpName]
                JiggleDampingTar.data_path = "Jiggle_Damping"
        #//        
                #JIGGLE MASS
                JiggleMassDrv = SelObj.driver_add('modifiers["Softbody"].settings.mass').driver
                JiggleMassDrv.type = 'AVERAGE'
                JiggleMassDrv.show_debug_info = True
                
                JiggleMassVar = JiggleMassDrv.variables.new()
                JiggleMassVar.name = "jiggle_mass"
                JiggleMassVar.type = 'SINGLE_PROP'
                
                JiggleMassTar = JiggleMassVar.targets[0]
                JiggleMassTar.id_type = 'OBJECT'
                JiggleMassTar.id = bpy.data.objects[GrpName]
                JiggleMassTar.data_path = "Jiggle_Mass"        
        #//        
                #JIGGLE STIFFNESS
                JiggleStiffDrv = SelObj.driver_add('modifiers["Softbody"].settings.goal_spring').driver
                JiggleStiffDrv.type = 'AVERAGE'
                JiggleStiffDrv.show_debug_info = True
                
                JiggleStiffVar = JiggleStiffDrv.variables.new()
                JiggleStiffVar.name = "jiggle_stiffness"
                JiggleStiffVar.type = 'SINGLE_PROP'
                
                JiggleStiffTar = JiggleStiffVar.targets[0]
                JiggleStiffTar.id_type = 'OBJECT'
                JiggleStiffTar.id = bpy.data.objects[GrpName]
                JiggleStiffTar.data_path = "Jiggle_Stiffness"
                
        #//     
                #BASE LENGHT
                BaseLenghtDrv = bpy.data.objects[str(GrpName)+'_armature'].driver_add('pose.bones["'+str(GrpName)+'_bone"].constraints["Stretch To"].rest_length').driver            
                BaseLenghtDrv.type = 'AVERAGE'
                BaseLenghtDrv.show_debug_info = True
                
                BaseLenghtVar = BaseLenghtDrv.variables.new()
                BaseLenghtVar.name = "base_lenght"
                BaseLenghtVar.type = 'SINGLE_PROP'
                
                BaseLenghtTar = BaseLenghtVar.targets[0]
                BaseLenghtTar.id_type = 'OBJECT'
                BaseLenghtTar.id = bpy.data.objects[GrpName]
                BaseLenghtTar.data_path = "Base_Lenght"
                
        #//     
                #VOLUME
                VolumeDrv = bpy.data.objects[str(GrpName)+'_armature'].driver_add('pose.bones["'+str(GrpName)+'_bone"].constraints["Stretch To"].bulge').driver            
                VolumeDrv.type = 'AVERAGE'
                VolumeDrv.show_debug_info = True
                
                VolumeVar = VolumeDrv.variables.new()
                VolumeVar.name = "volume"
                VolumeVar.type = 'SINGLE_PROP'
                
                VolumeTar = VolumeVar.targets[0]
                VolumeTar.id_type = 'OBJECT'
                VolumeTar.id = bpy.data.objects[GrpName]
                VolumeTar.data_path = "Volume"          
        #
        #END ADD DRIVERS
        #
                
                #SET ARMATURE ORIGIN
                bpy.context.scene.objects.active = bpy.data.objects[str(GrpName) + "_armature"]
                bpy.data.objects[str(GrpName) + "_armature"].select = True
                bpy.ops.object.posemode_toggle()
                bpy.ops.pose.select_all(action='SELECT')
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                bpy.ops.object.posemode_toggle()
                bpy.ops.object.select_all(action='DESELECT')
                
                #RENAME MODIFIERS
                bpy.context.scene.objects.active = bpy.data.objects[GrpName]
                
                bpy.context.active_object.modifiers["Softbody"].name = "muscle_softbody"
                bpy.context.active_object.modifiers["Subsurf"].name = "muscle_subsurf"
                
                
                #FINISH CONVERTION
                print("MUSCLE RIG ADDED")
                print("MUSCLE ATTRIBUTES ADDED")
                print(maxDim)
                print("GROUP NAME:", GrpName)
                print("CONVERTION SUCCESFUL")
        except:
            self.report({"ERROR"}, "An error occurred. Make sure you select an object")
             
        return{"FINISHED"}        


#
#END SET CONVERT PARAMETERS
#        


#       
#START DELETE MUSCLE PARAMTERES
#   

#DEFINE DELETE MUSCLE ATTRIBUTES BUTTON
class OBJECT_OT_deleteMuscle(bpy.types.Operator):
    bl_label= "Delete Muscle Attributes"
    bl_idname= "delete.muscle"
    bl_description= "Deletes muscle attributes if the object is a muscle object"     
           
    def execute(self, context):
         
        try:
            #GET OBJECT INFORMATION
            deleteObject = bpy.context.active_object
            deleteName = deleteObject.name
            
            bpy.context.active_object.driver_remove('modifiers["muscle_subsurf"].levels')
            bpy.context.active_object.driver_remove('modifiers["muscle_subsurf"].render_levels')
            bpy.context.active_object.driver_remove('modifiers["muscle_softbody"].show_render')
            bpy.context.active_object.driver_remove('modifiers["muscle_softbody"].show_viewport')
            bpy.context.active_object.driver_remove('modifiers["muscle_softbody"].settings.mass')
            bpy.context.active_object.driver_remove('modifiers["muscle_softbody"].settings.goal_min')
            bpy.context.active_object.driver_remove('modifiers["muscle_softbody"].settings.goal_spring')
            bpy.context.active_object.driver_remove('modifiers["muscle_softbody"].settings.goal_friction')
            bpy.context.active_object.data.shape_keys.driver_remove('key_blocks["'+str(deleteName)+'_thin"].value')
            bpy.context.active_object.data.shape_keys.driver_remove('key_blocks["'+str(deleteName)+'_fat"].value')
            bpy.ops.object.modifier_remove(modifier="Armature")
            bpy.ops.object.modifier_remove(modifier="muscle_softbody")
            bpy.ops.object.modifier_remove(modifier="muscle_subsurf")
            bpy.ops.object.shape_key_remove(all=True)
            
            bpy.ops.group.objects_remove(group=str(deleteName)+"_grp")
            
            for object in bpy.context.selected_objects:
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Base_Lenght')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Jiggle_Control')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Jiggle_Damping')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Jiggle_Mass')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Jiggle_Render')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Jiggle_Stiffness')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Jiggle_View')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Muscle_Shape')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Render_Resolution')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'View_Resolution')
                bpy.ops.wm.properties_remove(data_path = 'object', property = 'Volume')
            
            print("MUSCLE ATTRIBUTES SUCCESSFULLY DELETED")
                
        except:
            self.report({'ERROR'}, "Make Sure you've selected an Object with Muscle Attributes")       
            
        return{"FINISHED"} 
    
#
#END DELETE MUSCLE PARAMETERS
#


#
#START BIND OPTIONS
#

#Define a Function to store all objects in the scene
def allObjs():
    for ob in bpy.data.objects:
        print ("("+str(ob.name)+"),")
        
#Muscle Bind Stretch Button

class OBJECT_OT_stretchBind(bpy.types.Operator):
    bl_label= "Slide Bind"
    bl_idname= "bind.stretchmuscle"
    bl_description= "Select first muscle then skin"    
           
    def execute(self, context):
        
        try:
            #GET OBJECT INFORMATION
            MuscleSel = bpy.context.selected_objects[1]
            MuscleName = bpy.context.selected_objects[1].name
            
            SkinSel = bpy.context.selected_objects[0]
            SkinName = bpy.context.selected_objects[0].name
            
            #ADD A SLIDE BIND 
            bpy.ops.object.modifier_add(type="SHRINKWRAP")
            try:
                bpy.context.object.modifiers["Shrinkwrap"].target = MuscleSel
                bpy.context.object.modifiers["Shrinkwrap"].name = str(MuscleName)+"_shrinkwrap"
                bpy.context.object.modifiers[str(MuscleName)+"_shrinkwrap"].wrap_method = 'PROJECT'
                bpy.context.object.modifiers[str(MuscleName)+"_shrinkwrap"].cull_face = 'FRONT'
                bpy.ops.object.vertex_group_add()
                bpy.context.active_object.vertex_groups['Group'].name = str(MuscleName)+"_slide"
                bpy.ops.paint.weight_paint_toggle()
                bpy.context.object.modifiers[str(MuscleName)+"_shrinkwrap"].vertex_group = str(MuscleName)+"_slide"
            except:
                bpy.context.object.modifiers["Shrinkwrap"].target = SkinSel
                bpy.context.object.modifiers["Shrinkwrap"].name = str(SkinName)+"_shrinkwrap"
                bpy.context.object.modifiers[str(SkinName)+"_shrinkwrap"].wrap_method = 'PROJECT'
                bpy.context.object.modifiers[str(SkinName)+"_shrinkwrap"].cull_face = 'FRONT'
                bpy.ops.object.vertex_group_add()
                bpy.context.active_object.vertex_groups['Group'].name = str(SkinName)+"_slide"
                bpy.ops.paint.weight_paint_toggle()
                bpy.context.object.modifiers[str(SkinName)+"_shrinkwrap"].vertex_group = str(SkinName)+"_slide"
            print("MUSCLE SLIDE BOUND TO SKIN")
        except:
            
            self.report({'ERROR'}, "Please select first the 'Muscle Object' and second the 'Skin Object'")
        
        return{"FINISHED"}
#
#END BIND OPTIONS
#
        
            

#
#START REGISTER OPTIONS
#
  
def register():     # register panel
    bpy.utils.register_module(__name__)
   

def unregister():   # unregister panel
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

#
#END REGISTER OPTIONS
#


#
#END BLENDER MUSCLE TOOLS
#