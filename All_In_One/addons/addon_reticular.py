# addon_reticular.py (c) 2011 Atom

# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****
        
bl_info = {
    "name": "RE:ticular - Particle system display extension.",
    "author": "Atom.",
    "version": (1,0),
    "blender": (2, 6, 0),
    "api": 41562,
    "location": "View3D > RE:ticular",
    "description": "Adds Trapcode Particular style display type for existing particles.",
    "warning": "",
    "wiki_url":"",
    "tracker_url": "",
    "category": "Learnbgame",
}

"""
This code installs a frame change script and sets up initial objects for RE:ticular to work.

The python script content can be found in the __doc__ section of the def code, below.
"""

import bpy
import sys
import math
from mathutils import Vector
from bpy.props import *
from add_utils import AddObjectHelper

# Objects are managed by name prefix. Customize here...e.g. my_prefix (no longer than 12 characters)
PARENT_PREFIX   = "reticular_"          # Objects named like this are RE:ticular objects whose custom properties are animated by the end-user.
DEBUG = True                            # Enable disable debug output.
CONSOLE_PREFIX = "RE:ticular "

def to_console (passedItem = ""):
    if DEBUG == True:
        print(CONSOLE_PREFIX + passedItem)

############################################################################
# Code for returning names, objects, curves, scenes or meshes.
############################################################################
def fetchIfObject (passedName= ""):
    try:
        result = bpy.data.objects[passedName]
    except:
        result = None
    return result

def fetchIfMesh(passedName=""):
    try:
        result = bpy.data.meshes[passedName]
    except:
        result = None
    return result

def fetchIfText (passedName= ""):
    try:
        result = bpy.data.texts[passedName]
    except:
        result = None
    return result

def returnScene (passedIndex = 0):
    try:
        return bpy.data.scenes[passedIndex]
    except:
        return None

def returnSingleTriangleMesh(passedName):
    me = fetchIfMesh (passedName)
    if me == None:
        vp_points = []
        vp_faces = []
        vp_objects = []
        vp_D1 = Vector([0.06, 0.08, 0.0])
        vp_D2 = Vector([0.06, -0.08, 0.0])
        vp_D3 = Vector([-0.1, 0.0, 0.0])
        vp_scale = 6.0
        c = 0
    
        # Single triangle object at world origin.
        dd = Vector([0.0,0.0,0.0])
        vp_points.append(dd+vp_D1*vp_scale)
        vp_points.append(dd+vp_D2*vp_scale)
        vp_points.append(dd+vp_D3*vp_scale)
        vp_faces.append([c,c+1,c+2])        
    
        me = bpy.data.meshes.new(passedName)
        me.from_pydata(vp_points,[],vp_faces)
    else:
        # Just use the existing mesh.
        pass
    
    # Make sure all verts are deselected.
    for v in me.vertices:
        v.select = False
    me.update()
    return me

def createNewMaterial (passedName,passedRGB):
    tempMat = bpy.data.materials.new(passedName)
    if tempMat != None:
        tempMat.diffuse_color = (passedRGB[0],passedRGB[1],passedRGB[2])
        tempMat.diffuse_shader = 'LAMBERT'
        tempMat.diffuse_intensity = 1.0
        tempMat.specular_color = (0.9,0.9,0.9)
        tempMat.specular_shader = 'COOKTORR'
        tempMat.specular_intensity = 0.0
        tempMat.alpha = 1.0
        tempMat.ambient = 1.0
        tempMat.emit = 0.0
        tempMat.use_diffuse_ramp = True
    return tempMat

def createAddOnIcon (passedName):
    ob = None
    me = returnSingleTriangleMesh("me_" + passedName)
    if me != None:
        try:
            ob = bpy.data.objects.new(passedName,me)
            bpy.context.scene.objects.link(ob)
        except:
            pass    
    return ob

def install_reticular(self, context):
    # Install Tasks.
    # Two components are needed to make this work.
    # 1.) Make sure the frame_reticular.py script is installed and registered in a text window.
    # 2.) Create initial reticular object to house our control parameters.
    
    result = "FAILED: To install RE:ticular."

    # Install the python script that will run when the frame change fires.
    pythonName = "frame_reticular.py"
    txt = fetchIfText(pythonName)
    if txt == None:
        # Looks like there is no frame_change script so let's create one.
        txt = bpy.data.texts.new(pythonName)
        if txt != None:
            txt.clear()
            txt.write(code.__doc__)
            txt.use_module = True

            #Import the code we just created on-the-fly.
            import frame_reticular
        else:
            result = "FAILED: Could not create [" + pythonName + "]."
    else:
        # It exists, so we will assume it is imported already and not try.
        #import frame_reticular
        pass    

    # Time to actually create the object.
    ob = createAddOnIcon(PARENT_PREFIX + "edit_here")          #Create an object to be our RE:ticular parent.
    if ob != None:
        ob.hide_render = True
        # Create the two special materials.
        mat_color_over_time = createNewMaterial("color_over_time",(1.0,0.0,0.0))
        mat_size_over_time = createNewMaterial("size_over_time",(0.0,0.0,1.0))
        #color_element = mat_color_over_time.diffuse_ramp.ColorRampElement.color
        
        # Yikes, bpy.ops (so flaky).
        obSave = bpy.context.object
        bpy.context.scene.objects.active = ob
        bpy.ops.object.material_slot_add()
        ob.material_slots[0].material = mat_color_over_time
        bpy.ops.object.material_slot_add()
        ob.material_slots[1].material = mat_size_over_time
        bpy.context.scene.objects.active = obSave
        
        #collection = ob.Target_List
        #collection.add()
        #l = len(collection)
        #collection[-1].name= ("Target #" +str(l))
        #collection[-1].target_name = "" #(ob.name)
        #collection[-1].group_name = ""  #("grp_" + ob.name)
        #collection[-1].dupligroup = False
        ob["rot_X"] = 0.0
        ob["rot_Y"] = 9.0
        ob["rot_Z"] = 0.0
        ob["enabled"] = 1
        #ob["frame_step"] = 15
        ob["apply_modifiers"] = 0
        #ob["area"] = 50.0
        ob["emitter_name"] = "emitter"
        ob["particle_name"] = "particle"
        #ob["auto_list_step"] = 5
        #ob["_RNA_UI"] = {"area":{"min":1.0, "max":960.0, "description":"The size used by auto generation."}, "is_3d":{"min":0,"max":1, "description":"Restricts automatic generation to 2D or 3D."}, "auto_list_step": {"min":0, "max":180, "description":"Any auto-operations on the target list will use this value as the frame delay offset between targets."}, "Target_List_Index": {"min":0, "max":100, "description":"Internal value, do not animate!"}, "list_from_rephrase": {"description":"Type name of a RE:Frame object here to auto-populate this RE:Frame targets list."}, "enabled": {"min":0, "max":1, "description":"Enable or Disable this RE:Frame object."}}      
        #ob["_RNA_UI"] = {"frame_step":{"min":1, "max":90, "description":"When sampling animation or baking, this step is used."}, "Hold_Value":{"min":5, "max":900, "description":"Number of frames to remain at a target's location. Used by auto-animate button."}, "Travel_Value":{"min":0.0, "max":120.0, "description":"Animate this value to move the camera."}, "enabled": {"min":0, "max":1, "description":"Enable or Disable this RE:Frame object."}, "Target_List_Index":{"min":0, "max":120, "description":"Internal value, do not animate."}}
        result = "SUCCESS: RE:ticular installed."
    else:
        result = "Failed to create RE:ticular object."    
    print(result)

class OBJECT_OT_add_reticular(bpy.types.Operator, AddObjectHelper):
    """RE:ticular Particle Extension"""
    bl_idname = "scene.add_reticular"
    bl_label = "Particle Display ExXtension"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        install_reticular(self, context)
        return {'FINISHED'}

def add_reticular(self, context):
    self.layout.operator(
        OBJECT_OT_add_reticular.bl_idname,
        text="RE:ticular Particle Extensions",
        icon="PARTICLE_DATA")
        
############################################################################
# PANEL code.
############################################################################
# Create operator to select the particles.
class OBJECT_OT_Select_Particles(bpy.types.Operator):
    bl_label = "SelectParticles"
    bl_description ="Select the particles that are managed by this RE:ticular object."
    bl_idname = "ot.select_particles"
    
    def invoke(self,context,event):
        ob = context.object
        if ob != None:
            bpy.ops.object.select_all(action='DESELECT')
            lst = returnObjectNamesLike(PARTICLE_PREFIX)
            for name in lst:
                print(name)
                ob_candidate = fetchIfObject(name)
                if ob_candidate != None:
                    if ob_candidate.parent.name == ob.name:
                        # Select this object
                        ob_candidate.select = True
        return {'FINISHED'}
    
class OBJECT_PT_reticular(bpy.types.Panel):
    bl_label = "RE:ticular"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        ob = context.object
        if ob != None:
            layout = self.layout
            try:
                enabled = ob["enabled"]
            except:
                enabled = 0
                
            if enabled == 1:
                l = len(PARENT_PREFIX)
                if ob.name[:l] == PARENT_PREFIX:
                    # Related items go in this box.
                    col = layout.column_flow(0,align=True)
                    #col = layout.split(0.75,True)
                    
                    box = col.box()
                    #box.scale_x = 0.5
                    box.label("Settings:")
                    row = box.row()
                    
                    row.prop(ob, '["rot_X"]', text="Rotation X")
                    row = box.row()
                    row.prop(ob, '["rot_Y"]', text="Rotation Y")
                    row = box.row()
                    row.prop(ob, '["rot_Z"]', text="Rotation Z")
                    row = box.row()
                    row.prop(ob, '["emitter_name"]', text="Emitter")
                    row = box.row()
                    row.prop(ob, '["particle_name"]', text="Particle")
                    #box.prop(ob, '["apply_modifiers"]', text = "Apply Modifiers")
                    
                    col.operator("ot.select_particles", icon="RESTRICT_SELECT_OFF", text="")
                else:
                    layout.label(" RE:ticular is disabled in custom properties.",icon='INFO')  
            else:
                pass
                #print ("Not a RE:ticular managed object [" + ob.name + "].")

def register():
    # AddOn
    bpy.utils.register_class(OBJECT_OT_add_reticular)
    bpy.types.INFO_MT_add.append(add_reticular)

    # Panel
    bpy.utils.register_class(OBJECT_PT_reticular)
    bpy.utils.register_class(OBJECT_OT_Select_Particles)


def unregister():
    # AddOn
    bpy.utils.unregister_class(OBJECT_OT_add_reticular)

    # Panel
    bpy.utils.unregister_class(OBJECT_PT_reticular)
    bpy.utils.unregister_class(OBJECT_OT_Select_Particles)

if __name__ == '__main__':
    print("Registering RE:ticular AddOn and supporting panel...")
    register() 
    
# This is the code that get's written to the new text window.
def code():
    """
# RE:ticular 1.0 (resembling or forming a network)
# (c) 2011 Atom
# Last update: 11-05-2011
#
# The goal of this script is to create an alternate particle display system that emulates some of the
# features of the Trapcode Particular particle system by Red Giant.

import bpy
from mathutils import Vector
from math import pi, radians

############################################################################
# Globals.
############################################################################
PARENT_PREFIX   = "reticular_"      # Objects named like this are RE:ticular objects whose custom properties are animated by the end-user.
PARTICLE_PREFIX = "rp_"             # Reticular particle prefix.
MATERIAL_PREFIX = "mat_"            # Reticular material prefix.
NAME_LENGTH = 10                    # Make sure name of particles and materials does not exceed NAME_MAX
NAME_MAX = 21                       # Maximum length of any object name.

############################################################################
# Object/Mesh code.
############################################################################
def fetchIfObject (passedObjectName):
	# NOTE: Returns the object even if it is unlinked to the scene.
	try:
		return bpy.data.objects[passedObjectName]
	except:
		return None

def fetchIfMesh(passedName=""):
    try:
        result = bpy.data.meshes[passedName]
    except:
        result = None
    return result

def returnSingleTriangleMesh(passedName):
    me = fetchIfMesh (passedName)
    if me == None:
        vp_points = []
        vp_faces = []
        vp_objects = []
        vp_D1 = Vector([0.06, 0.08, 0.0])
        vp_D2 = Vector([0.06, -0.08, 0.0])
        vp_D3 = Vector([-0.1, 0.0, 0.0])
        vp_scale = 6.0
        c = 0
    
        # Single triangle object at world origin.
        dd = Vector([0.0,0.0,0.0])
        vp_points.append(dd+vp_D1*vp_scale)
        vp_points.append(dd+vp_D2*vp_scale)
        vp_points.append(dd+vp_D3*vp_scale)
        vp_faces.append([c,c+1,c+2])        
    
        me = bpy.data.meshes.new(passedName)
        me.from_pydata(vp_points,[],vp_faces)
    else:
        # Just use the existing mesh.
        pass
    
    # Make sure all verts are deselected.
    for v in me.vertices:
        v.select = False
    me.update()
    return me

############################################################################
# Name code.
############################################################################
def returnAllObjectNames ():
    # NOTE: This returns all object names in Blender, not scene specific.
    result = []
    for ob in bpy.data.objects:
        result.append(ob.name)
    return result 

def returnObjectNamesLike(passedName):
    # Return objects named like our passedName.
    result = []
    isLike = passedName
    l = len(isLike)
    all_obs = returnAllObjectNames()
    for name in all_obs:
        candidate = name[0:l]
        if isLike == candidate:
            result.append(name)
    return result

def returnNameForNumber(passedFrame):
    frame_number = str(passedFrame)
    l = len(frame_number)
    post_fix = frame_number
    if l == 1: 
        post_fix = "000" + frame_number
    if l == 2: 
        post_fix = "00" + frame_number
    if l == 3: 
        post_fix = "0" + frame_number
    return post_fix

############################################################################
# Material code.
############################################################################
def returnMaterialByName(passedName):
    try:
        result = bpy.data.materials[passedName]
    except:
        result = None
    return result

def createNewMaterial (passedName,passedRGB):
    tempMat = bpy.data.materials.new(passedName)
    if tempMat != None:
        tempMat.diffuse_color = (passedRGB[0],passedRGB[1],passedRGB[2])
        tempMat.diffuse_shader = 'LAMBERT'
        tempMat.diffuse_intensity = 1.0
        tempMat.specular_color = (0.9,0.9,0.9)
        tempMat.specular_shader = 'COOKTORR'
        tempMat.specular_intensity = 0.0
        tempMat.alpha = 1.0
        tempMat.ambient = 1.0
        tempMat.emit = 0.0
        tempMat.specular_alpha = 0.0
    return tempMat

def acquireOrCreateMaterial(passedName,passedRGB):
    tempMat = returnMaterialByName(passedName)
    if tempMat == None:
        tempMat = createNewMaterial(passedName,passedRGB)
    return tempMat

def assignMaterial(passedObjectName, passedMaterialName, passedLink = "DATA"):
    result = False
    tempMaterial = returnMaterialByName(passedMaterialName)
    if tempMaterial != None:
        tempObject = fetchIfObject(passedObjectName)
        if tempObject != None:
            if tempObject.material_slots.__len__() > 0:  
                tempObject.material_slots[0].link = passedLink       
                tempObject.material_slots[0].material = tempMaterial
            else:
                temp_slot = bpy.types.MaterialSlot
                tempObject.material_slots.items.__new__(temp_slot)
                tempObject.material_slots[tempObject.material_slots.__len__() - 1].link = passedLink
                tempObject.material_slots[tempObject.material_slots.__len__() - 1].material = tempMaterial
            result = True
        else:
            print("No materials called [" + passedMaterialName + "].")       
    else:
        print("No object called [" + passedObjectName + "].")
    return result
         
############################################################################
# Update code.
############################################################################
def frameChangePre (passedScene):
    fc = passedScene.frame_current
   
    ob_list = returnObjectNamesLike(PARENT_PREFIX)
    if len(ob_list) > 0:
        for name in ob_list:
            print("Reviewing [" + name + "] on frame #" + str(fc) + ".")
            ob_parent = fetchIfObject(name)
            if ob_parent !=None:
                # This is an object that is managed by this script.
                if ob_parent["enabled"] == 1:
                    particle_source = ob_parent["particle_name"]
                    ob_particle = fetchIfObject(particle_source)
                    if ob_particle != None:
                        if len(ob_particle.material_slots) < 1:
                            # The particle source needs to have at least one material slot or the whole thing fails.
                            mat_source = bpy.data.materials.new("auto_generated")
                            ob_particle.data.materials.append(mat_source)
                        else:
                            mat_source = ob_particle.material_slots[0].material 
                        me_particle = ob_particle.data
                    else:
                        me_particle = None
                    
                    if me_particle != None:
                        # Fetch our emitter that contains two ramp materials.
                        emitter_source = ob_parent["emitter_name"]
                        ob_emitter = bpy.data.objects[emitter_source]
                        if ob_emitter != None:
                            if ob_emitter.particle_systems:
                                ps = ob_emitter.particle_systems[0] 
                                if ps != None:
                                    n = 1
                                    particle_parent_name = ob_emitter.name[:NAME_LENGTH]
                                    for x in ps.particles:
                                        # Default our ramp results to None per-particle.
                                        col_temp = None
                                        size_temp = None
                                        
                                        # Make names per-particle.
                                        name_part = particle_parent_name + "_" + returnNameForNumber(n)
                                        particle_name = PARTICLE_PREFIX + name_part
                                        material_name = MATERIAL_PREFIX + name_part
                                        if x.alive_state == 'ALIVE':
                                            age = ((fc - x.birth_time) / x.lifetime)
                                            #print (particle_name + " has an age of " + str(age) + " and material named [" + material_name + "].")
                                            ob_reticular = fetchIfObject(particle_name)
                                            if ob_reticular == None:
                                                # This particle object does not exist so let us create it.
                                                ob_reticular = bpy.data.objects.new(particle_name,me_particle)
                                                passedScene.objects.link(ob_reticular)
                                                # Parent all our reticular particles to our parent so the outliner display does not get out of hand.
                                                ob_reticular.parent = ob_parent
                                                # A new object also needs it's own material (this is what makes reticular special, a material per-particle).
                                                mat_particle =  mat_source.copy()   #acquireOrCreateMaterial (material_name,(1.0,1.0,1.0))
                                                mat_particle.name = material_name
                                                if mat_particle != None:
                                                    # Remember to set the link first or you will re-assign the material linked to the source mesh.
                                                    ob_reticular.material_slots[0].link = 'OBJECT'
                                                    ob_reticular.material_slots[0].material = mat_particle
                                                else:
                                                    print ("No mat_particle.")
                
                                            else:
                                                # Looks like the object already exists, let us fetch it's material.
                                                mat_particle = returnMaterialByName(material_name)
                                                # Let us make sure it is still linked to the scene.
                                                try:
                                                    passedScene.objects.link(ob_reticular)
                                                except:
                                                    pass

                                            # Review the mesh linked to this particle to make sure it is still the correct one.
                                            # For changes to the particle source that occur after RE:ticular particles have been generated.
                                            if me_particle.name != ob_reticular.data.name:
                                                # These names are different so we do have to re-link.
                                                print ("Re-linking particle data, the particle source has changed.")
                                                ob_reticular.data = me_particle
                                            
                                            if mat_particle != None:  
                                                # Fetch the material with the color over time ramp.
                                                mat_color = returnMaterialByName("color_over_time")
                                                if mat_color != None:
                                                    if mat_color.use_diffuse_ramp == True:
                                                        ramp_color = mat_color.diffuse_ramp
                                                        col_temp = ramp_color.evaluate(age)
                                                    else:
                                                        print("Failed to access diffuse_ramp for color.")
                                                else:
                                                    print ("Emitter is missing the [color_over_time] ramp material.")
                                                        
                                                mat_size = returnMaterialByName("size_over_time")
                                                if mat_size != None:
                                                    if mat_size.use_diffuse_ramp == True:
                                                        ramp_size = mat_size.diffuse_ramp
                                                        size_temp = ramp_size.evaluate(age)
                                                    else:
                                                        print("Failed to access diffuse_ramp for size.")
                                                else:
                                                    print ("Emitter is missing the [size_over_time] ramp material.")
                                           
                       
                                                # Change a reticular particle's color based upon a ramp evaluated against particle age.
                                                if col_temp != None:
                                                    if mat_particle != None:
                                                        mat_particle.diffuse_color = (col_temp[0],col_temp[1],col_temp[2])
                                                        #mat_particle.alpha = col_temp[3]
                                                    else:
                                                        print ("No material [" + material_name + "] available to apply results to?")
                                                else:
                                                    print ("Ramp evaluate failed on color_over_time.")
                    
                                                # Change a particle's size based upon a ramp evaluated against particle age.
                                                if size_temp != None:
                                                    # Note: size_temp is an actual color so we assume it is grey-scale to control our particle scale.
                                                    sz = size_temp[0] * x.size
                                                    ob_reticular.scale = [sz,sz,sz]
                                                       
                                                # Map the location of the Blender particle to the reticular particle.
                                                ob_reticular.location = x.location
                                                
                                                if passedScene.frame_current == 1:
                                                    # Reset the rotation to 0.0.
                                                    print("Resetting RE:ticular particle rotation back to 0.")
                                                    ob_reticular.delta_rotation_euler = (0.0,0.0,0.0)
                                                    
                                                # Map the rotation from the RE:ticular panel to the reticular particle (ignore Blender's particle rotation).
                                                tempROT = ob_reticular.delta_rotation_euler
                                                tempROT[0] = tempROT[0] + radians(ob_parent["rot_X"])
                                                tempROT[1] = tempROT[1] + radians(ob_parent["rot_Y"])
                                                tempROT[2] = tempROT[2] + radians(ob_parent["rot_Z"])
                                                ob_reticular.delta_rotation_euler = tempROT
                                                
                                            else:
                                                # Let us try and create a new material for this particle. It doen't seem to have one.
                                                mat_particle =  acquireOrCreateMaterial (material_name,(1.0,1.0,1.0))
                                                if mat_particle != None:
                                                    # Remember to set the link first or you will re-assign the material linked to the source mesh.
                                                    ob_reticular.material_slots[0].link = 'OBJECT'
                                                    ob_reticular.material_slots[0].material = mat_particle
                                                else:
                                                    print (particle_name + " does not have a material [" + material_name + "].")
                                                    
                                        else:
                                            #print (x.alive_state)
                                            # This particle is not alive so make sure the managed reticular particle is unlinked from the scene.
                                            ob_reticular = fetchIfObject(particle_name)
                                            if ob_reticular != None:
                                                try:
                                                    passedScene.objects.unlink(ob_reticular)
                                                except:
                                                    pass
                                        n = n + 1
                        else:
                            print("No mesh based particle name [particle] found in scene.")    

############################################################################
# PANEL code.
############################################################################
# Create operator to select the particles.
class OBJECT_OT_Select_Particles(bpy.types.Operator):
    bl_label = "SelectParticles"
    bl_description ="Select the particles that are managed by this RE:ticular object."
    bl_idname = "ot.select_particles"
    
    def invoke(self,context,event):
        ob = context.object
        if ob != None:
            bpy.ops.object.select_all(action='DESELECT')
            lst = returnObjectNamesLike(PARTICLE_PREFIX)
            for name in lst:
                print(name)
                ob_candidate = fetchIfObject(name)
                if ob_candidate != None:
                    if ob_candidate.parent.name == ob.name:
                        # Select this object
                        ob_candidate.select = True
        return {'FINISHED'}
    
class OBJECT_PT_reticular(bpy.types.Panel):
    bl_label = "RE:ticular"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    def draw(self, context):
        ob = context.object
        if ob != None:
            layout = self.layout
            try:
                enabled = ob["enabled"]
            except:
                enabled = 0
                
            if enabled == 1:
                l = len(PARENT_PREFIX)
                if ob.name[:l] == PARENT_PREFIX:
                    # Related items go in this box.
                    col = layout.column_flow(0,align=True)
                    #col = layout.split(0.75,True)
                    
                    box = col.box()
                    #box.scale_x = 0.5
                    box.label("Settings:")
                    row = box.row()
                    
                    row.prop(ob, '["rot_X"]', text="Rotation X")
                    row = box.row()
                    row.prop(ob, '["rot_Y"]', text="Rotation Y")
                    row = box.row()
                    row.prop(ob, '["rot_Z"]', text="Rotation Z")
                    row = box.row()
                    row.prop(ob, '["emitter_name"]', text="Emitter")
                    row = box.row()
                    row.prop(ob, '["particle_name"]', text="Particle")
                    #box.prop(ob, '["apply_modifiers"]', text = "Apply Modifiers")
                    
                    col.operator("ot.select_particles", icon="RESTRICT_SELECT_OFF", text="")
                else:
                    layout.label(" RE:ticular is disabled in custom properties.",icon='INFO')  
            else:
                pass
                #print ("Not a RE:ticular managed object [" + ob.name + "].")

def register():
    # Panel
    bpy.utils.register_class(OBJECT_PT_reticular)
    bpy.utils.register_class(OBJECT_OT_Select_Particles)

def unregister():
    # Panel
    bpy.utils.unregister_class(OBJECT_PT_reticular)
    bpy.utils.unregister_class(OBJECT_OT_Select_Particles)
    
#if __name__ == '__main__':
print("Registering RE:ticular panel...")
register() 
                      
bpy.app.handlers.frame_change_pre.append(frameChangePre)
    
    """  