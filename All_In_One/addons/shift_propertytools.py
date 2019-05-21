#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### HEADER
####------------------------------------------------------------------------------------------------------------------------------------------------------

bl_info = {
    "name"              : "SHIFT - Property Tools",
    "author"            : "BBC",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Property Tools"}


import bpy
import time
import math
import random
import mathutils

from math       import *
from bpy.props  import *

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### FORMATTING NAMES - PARSE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def formatNameParse (format_string, keyword):

    literals = []

    literals.append (('l0', '%>'    + keyword))
    literals.append (('l1', '%>>'   + keyword))
    literals.append (('l2', '%>>>'  + keyword))
    literals.append (('l3', '%>>>>' + keyword))
    literals.append (('r3', '%'     + keyword + '<<<<'))
    literals.append (('r2', '%'     + keyword + '<<<'))
    literals.append (('r1', '%'     + keyword + '<<'))
    literals.append (('r0', '%'     + keyword + '<'))

    fstr = str (format_string)

    replaces = []

    fl = len (fstr)

    for lt in literals :

        ltok  = lt [0]
        ltstr = lt [1];     ll = len (ltstr)

        index = fstr.find (ltstr)

        while index >= 0:
            
            delimiter = ''; index += ll
            
            while ((index < fl) and (fstr [index] != '%')):
                
                delimiter += fstr [index]; index += 1

            if delimiter != '':

                replaces.append ((ltok, ltstr + delimiter + '%', delimiter))

                fstr = fstr.replace (ltstr + delimiter + '%', '')
                
                index = fstr.find (ltstr)
                
            else: break

    if (fstr.find ('%' + keyword + '%') >= 0):
        
        replaces.append ((None, '%' + keyword + '%', None))

    literals [:] = []

    return replaces

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### FORMATTING NAMES - SUBSTITUTE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def formatName (format_string, substition_string, replaces):

    result = format_string
    for r in replaces:
        if not  r [0]:  result = format_string.replace (r [1], substition_string)
        elif    r [0][0] == 'l':
            try:    i = int (r[0][1]);  result = format_string.replace (r [1], substition_string.split  (r [2], i + 1)[i + 1])
            except: pass
        elif    r [0][0] == 'r':
            try:    i = int (r[0][1]);  result = format_string.replace (r [1], substition_string.rsplit (r [2], i + 1)[0])
            except: pass

    return (result)
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### CHECK NAMES
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processCheckNames (name, owner):

    print ('Check names : ')
    print ('')

    # parsing formatting string
    repl = formatNameParse (name, 'name')

    # object
    if   (owner == '0'):

        for obj in bpy.context.selected_objects:
            try:    print ("Object :", obj.name, "Name :", formatName (name, obj.name, repl))
            except: pass
                
    # mesh
    elif (owner == '1'):

        for obj in bpy.context.selected_objects:
            try:    print ("Object :", obj.name, "Name :", formatName (name, obj.data.name, repl))
            except: pass

    # material
    elif (owner == '2'):

        for obj in bpy.context.selected_objects:
            try:    print ("Object :", obj.name, "Name :", formatName (name, obj.active_material.name, repl))
            except: pass

    # texture
    elif (owner == '3'):

        for obj in bpy.context.selected_objects:
            try:    print ("Object :", obj.name, "Name :", formatName (name, obj.active_material.active_texture.name, repl))
            except: pass
            
    # particle settings
    elif (owner == '4'):

        for obj in bpy.context.selected_objects:
            try:    print ("Object :", obj.name, "Name :", formatName (name, obj.particle_systems.active.settings.name, repl))
            except: pass
            
    print ('')
            
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROPERTY REMOVE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def removeProperty (name, owner):

    scene = bpy.context.scene

    if (name != ''):

        # object
        if   (owner == '0'):

            for obj in bpy.context.selected_objects:
                try:    del obj [name]
                except: pass
                    
        # mesh
        elif (owner == '1'):

            for obj in bpy.context.selected_objects:
                try:    del obj.data [name]
                except: pass

        # material
        elif (owner == '2'):

            for obj in bpy.context.selected_objects:
                try:    del obj.active_material [name]
                except: pass

        # texture
        elif (owner == '3'):

            for obj in bpy.context.selected_objects:
                try:    del obj.active_material.active_texture [name]
                except: pass

        # particle settings
        elif (owner == '4'):

            for obj in bpy.context.selected_objects:
                try:    del obj.particle_systems.active.settings [name]
                except: pass
                
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROPERTY SET
####------------------------------------------------------------------------------------------------------------------------------------------------------
                
def setProperty (name, value, owner, overwrite):

    scene = bpy.context.scene

    scene.shift_pt_history.add ()
    scene.shift_pt_history [-1].name = name

    if (name != ''):
        
        try:    value = int (value)
        except:
            try:    value = float (value)
            except: pass

        if type (value) == str :

            # parsing formatting string
            repl = formatNameParse (value, 'name')

            # object
            if   (owner == '0'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        obj [name] = formatName (value, obj.name, repl)
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj [name];    print ('WARNING | Property already exist : object \'', obj.name, '\' , property \'', name, '\'')
                        except: obj [name] = formatName (value, obj.name, repl)
                        
            # mesh
            elif (owner == '1'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        obj.data [name] = formatName (value, obj.data.name, repl)
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.data [name];    print ('WARNING | Property already exist : object data \'', obj.data.name, '\' , property \'', name, '\'')
                        except: obj.data [name] = formatName (value, obj.data.name, repl)

            # material
            elif (owner == '2'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material [name] = formatName (value, obj.active_material.name, repl)
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material [name];    print ('WARNING | Property already exist : object data \'', obj.active_material.name, '\' , property \'', name, '\'')
                        except: obj.active_material [name] = formatName (value, obj.active_material.name, repl)

            # texture
            elif (owner == '3'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material.active_texture [name] = formatName (value, obj.active_material.active_texture.name, repl)
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material.active_texture [name];    print ('WARNING | Property already exist : object data \'', obj.active_material.active_texture.name, '\' , property \'', name, '\'')
                        except: obj.active_material.active_texture [name] = formatName (value, obj.active_material.active_texture.name, repl)
                        
            # particle settings
            elif (owner == '4'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:    obj.particle_systems.active.settings [name] = formatName (value, obj.particle_systems.active.settings.name, repl)
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.particle_systems.active.settings [name];    print ('WARNING | Property already exist : object data \'', obj.particle_systems.active.settings.name, '\' , property \'', name, '\'')
                        except: obj.particle_systems.active.settings [name] = formatName (value, obj.particle_systems.active.settings.name, repl)
                        
        else :

            # object
            if   (owner == '0'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        obj [name] = value
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj [name];    print ('WARNING | Property already exist : object \'', obj.name, '\' , property \'', name, '\'')
                        except: obj [name] = value
                        
            # mesh
            elif (owner == '1'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        obj.data [name] = value
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.data [name];    print ('WARNING | Property already exist : object data \'', obj.data.name, '\' , property \'', name, '\'')
                        except: obj.data [name] = value

            # material
            elif (owner == '2'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material [name] = value
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material [name];    print ('WARNING | Property already exist : object data \'', obj.active_material.name, '\' , property \'', name, '\'')
                        except: obj.active_material [name] = value

            # texture
            elif (owner == '3'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material.active_texture [name] = value
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.active_material.active_texture [name];    print ('WARNING | Property already exist : object data \'', obj.active_material.active_texture.name, '\' , property \'', name, '\'')
                        except: obj.active_material.active_texture [name] = value

            # particle settings
            elif (owner == '4'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:    obj.particle_systems.active.settings [name] = value
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:    obj.particle_systems.active.settings [name];    print ('WARNING | Property already exist : object data \'', obj.particle_systems.active.settings.name, '\' , property \'', name, '\'')
                        except: obj.particle_systems.active.settings [name] = value
                        
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SET
####------------------------------------------------------------------------------------------------------------------------------------------------------
    
def process1Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property1, scene.shift_pt_property1_value, scene.shift_pt_property1_owner, scene.shift_pt_overwrite)
def process2Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property2, scene.shift_pt_property2_value, scene.shift_pt_property2_owner, scene.shift_pt_overwrite)
def process3Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property3, scene.shift_pt_property3_value, scene.shift_pt_property3_owner, scene.shift_pt_overwrite)
def process4Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property4, scene.shift_pt_property4_value, scene.shift_pt_property4_owner, scene.shift_pt_overwrite)
def process5Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property5, scene.shift_pt_property5_value, scene.shift_pt_property5_owner, scene.shift_pt_overwrite)
def process6Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property6, scene.shift_pt_property6_value, scene.shift_pt_property6_owner, scene.shift_pt_overwrite)
def process7Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property7, scene.shift_pt_property7_value, scene.shift_pt_property7_owner, scene.shift_pt_overwrite)
def process8Set     (): scene = bpy.context.scene;  setProperty (scene.shift_pt_property8, scene.shift_pt_property8_value, scene.shift_pt_property8_owner, scene.shift_pt_overwrite)

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS REMOVE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def process1Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property1, scene.shift_pt_property1_owner) 
def process2Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property2, scene.shift_pt_property2_owner)
def process3Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property3, scene.shift_pt_property3_owner)
def process4Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property4, scene.shift_pt_property4_owner)
def process5Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property5, scene.shift_pt_property5_owner)
def process6Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property6, scene.shift_pt_property6_owner)
def process7Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property7, scene.shift_pt_property7_owner)
def process8Remove  (): scene = bpy.context.scene;  removeProperty (scene.shift_pt_property8, scene.shift_pt_property8_owner)

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS CLEAR
####------------------------------------------------------------------------------------------------------------------------------------------------------

def process1Clear   (): scene = bpy.context.scene;  scene.shift_pt_property1 = '';  scene.shift_pt_property1_value = '';
def process2Clear   (): scene = bpy.context.scene;  scene.shift_pt_property2 = '';  scene.shift_pt_property2_value = '';
def process3Clear   (): scene = bpy.context.scene;  scene.shift_pt_property3 = '';  scene.shift_pt_property3_value = '';
def process4Clear   (): scene = bpy.context.scene;  scene.shift_pt_property4 = '';  scene.shift_pt_property4_value = '';
def process5Clear   (): scene = bpy.context.scene;  scene.shift_pt_property5 = '';  scene.shift_pt_property5_value = '';
def process6Clear   (): scene = bpy.context.scene;  scene.shift_pt_property6 = '';  scene.shift_pt_property6_value = '';
def process7Clear   (): scene = bpy.context.scene;  scene.shift_pt_property7 = '';  scene.shift_pt_property7_value = '';
def process8Clear   (): scene = bpy.context.scene;  scene.shift_pt_property8 = '';  scene.shift_pt_property8_value = '';


####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS REMOVE UV
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processRemoveUV (name, preserve):

    start_time = time.clock ()
    
    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects
    
    # log
    print ('\nRemove starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        if (obj.type == 'MESH'):

            # set active object
            scene.objects.active = obj

            # saving vertex normals
            if preserve :
                
                normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]
            
            try:

                # set active layer
                obj.data.uv_textures.active = obj.data.uv_textures [name]

            except: print ("ERROR | Object : '" + obj.name + "' Unable to find UV layer with name : '" + name + "'"); continue

            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')

            # remove uv layer
            bpy.ops.mesh.uv_texture_remove ()
                
            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

            if preserve :

                # restoring normals
                for v in obj.data.vertices:    v.normal = normals [v.index]

                # clean up                
                normals [:] = []

            # log
            print (i + 1, "Object : '" + obj.name + "'")
            
        else:
            
            # log
            print (i + 1, "Object : '" + obj.name + "' is not a mesh")
        
    # log            
    print ('')
    print ('Remove finished in %.4f sec.' % (time.clock () - start_time))
            
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS REMOVE ALL UV
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processRemoveAllUV (preserve):

    start_time = time.clock ()
    
    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects
    
    # log
    print ('\nRemove starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        if (obj.type == 'MESH'):

            # set active object
            scene.objects.active = obj

            # saving vertex normals
            if preserve :
                
                normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]
            
            # remove all layers
            for uv_tex in obj.data.uv_textures:
            
                # set active layer
                obj.data.uv_textures.active = uv_tex

                # edit mode
                bpy.ops.object.mode_set (mode = 'EDIT')

                # remove uv layer
                bpy.ops.mesh.uv_texture_remove ()
                    
                # object mode
                bpy.ops.object.mode_set (mode = 'OBJECT')

            if preserve :

                # restoring normals
                for v in obj.data.vertices:    v.normal = normals [v.index]

                # clean up                
                normals [:] = []

            # log
            print (i + 1, "Object : '" + obj.name + "'")
            
        else:
            
            # log
            print (i + 1, "Object : '" + obj.name + "' is not a mesh")
        
    # log            
    print ('')
    print ('Remove finished in %.4f sec.' % (time.clock () - start_time))
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS REMOVE COLOR
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processRemoveColor (name, preserve):

    start_time = time.clock ()
    
    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects
    
    # log
    print ('\nRemove starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        if (obj.type == 'MESH'):

            # set active object
            scene.objects.active = obj

            # saving vertex normals
            if preserve :
                
                normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]
            
            try:

                # set active layer
                obj.data.vertex_colors.active = obj.data.vertex_colors [name]

            except: print ("ERROR | Object : '" + obj.name + "' Unable to find vertex color layer with name : '" + name + "'"); continue

            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')

            # remove uv layer
            bpy.ops.mesh.vertex_color_remove ()
                
            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

            if preserve :

                # restoring normals
                for v in obj.data.vertices:    v.normal = normals [v.index]

                # clean up                
                normals [:] = []
                
            # log
            print (i + 1, "Object : '" + obj.name + "'")
            
        else:
            
            # log
            print (i + 1, "Object : '" + obj.name + "' is not a mesh")
        
    # log            
    print ('')
    print ('Remove finished in %.4f sec.' % (time.clock () - start_time))

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS REMOVE ALL COLOR
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processRemoveAllColor (preserve):

    start_time = time.clock ()
    
    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects
    
    # log
    print ('\nRemove starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        if (obj.type == 'MESH'):

            # set active object
            scene.objects.active = obj

            # saving vertex normals
            if preserve :
                
                normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]
            
            # remove all layers
            for vcol in obj.data.vertex_colors:

                # set active layer
                obj.data.vertex_colors.active = vcol

                # edit mode
                bpy.ops.object.mode_set (mode = 'EDIT')

                # remove uv layer
                bpy.ops.mesh.vertex_color_remove ()
                    
                # object mode
                bpy.ops.object.mode_set (mode = 'OBJECT')

            if preserve :

                # restoring normals
                for v in obj.data.vertices:    v.normal = normals [v.index]

                # clean up                
                normals [:] = []
                
            # log
            print (i + 1, "Object : '" + obj.name + "'")
            
        else:
            
            # log
            print (i + 1, "Object : '" + obj.name + "' is not a mesh")
        
    # log            
    print ('')
    print ('Remove finished in %.4f sec.' % (time.clock () - start_time))
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------

class PropertyToolsOpSet (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set all properties to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Set ()
        process2Set ()
        process3Set ()
        process4Set ()
        process5Set ()
        process6Set ()
        process7Set ()
        process8Set ()
        return {'FINISHED'}

class PropertyToolsOpClear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear all properties"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Clear ()
        process2Clear ()
        process3Clear ()
        process4Clear ()
        process5Clear ()
        process6Clear ()
        process7Clear ()
        process8Clear ()
        return {'FINISHED'}
    
class PropertyToolsOpRemove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove all properties from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Remove ()
        process2Remove ()
        process3Remove ()
        process4Remove ()
        process5Remove ()
        process6Remove ()
        process7Remove ()
        process8Remove ()
        return {'FINISHED'}
    
class PropertyToolsOp1Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator1_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Set ()
        return {'FINISHED'}
class PropertyToolsOp2Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator2_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process2Set ()
        return {'FINISHED'}
class PropertyToolsOp3Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator3_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process3Set ()
        return {'FINISHED'}
class PropertyToolsOp4Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator4_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process4Set ()
        return {'FINISHED'}
class PropertyToolsOp5Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator5_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process5Set ()        
        return {'FINISHED'}    
class PropertyToolsOp6Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator6_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process6Set ()        
        return {'FINISHED'}
class PropertyToolsOp7Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator7_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process7Set ()        
        return {'FINISHED'}
class PropertyToolsOp8Set (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator8_set"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process8Set ()        
        return {'FINISHED'}
    
class PropertyToolsOp1Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator1_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Clear ()
        return {'FINISHED'}
class PropertyToolsOp2Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator2_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process2Clear ()
        return {'FINISHED'}
class PropertyToolsOp3Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator3_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process3Clear ()
        return {'FINISHED'}
class PropertyToolsOp4Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator4_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process4Clear ()
        return {'FINISHED'}
class PropertyToolsOp5Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator5_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process5Clear ()        
        return {'FINISHED'}    
class PropertyToolsOp6Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator6_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process6Clear ()        
        return {'FINISHED'}
class PropertyToolsOp7Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator7_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process7Clear ()        
        return {'FINISHED'}
class PropertyToolsOp8Clear (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator8_clear"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process8Clear ()        
        return {'FINISHED'}

class PropertyToolsOp1Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator1_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Remove ()
        return {'FINISHED'}    
class PropertyToolsOp2Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator2_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process2Remove ()
        return {'FINISHED'}    
class PropertyToolsOp3Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator3_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process3Remove ()
        return {'FINISHED'}
class PropertyToolsOp4Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator4_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process4Remove ()
        return {'FINISHED'}
class PropertyToolsOp5Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator5_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process5Remove ()
        return {'FINISHED'}
class PropertyToolsOp6Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator6_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process6Remove ()
        return {'FINISHED'}
class PropertyToolsOp7Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator7_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process7Remove ()
        return {'FINISHED'}
class PropertyToolsOp8Remove (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator8_remove"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process8Remove ()
        return {'FINISHED'}

class PropertyToolsOp1Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator1_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property1_value, scene.shift_pt_property1_owner)
        return {'FINISHED'}
class PropertyToolsOp2Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator2_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property2_value, scene.shift_pt_property2_owner)
        return {'FINISHED'}
class PropertyToolsOp3Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator3_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property3_value, scene.shift_pt_property3_owner)
        return {'FINISHED'}
class PropertyToolsOp4Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator4_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property4_value, scene.shift_pt_property4_owner)
        return {'FINISHED'}
class PropertyToolsOp5Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator5_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property5_value, scene.shift_pt_property5_owner)
        return {'FINISHED'}
class PropertyToolsOp6Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator6_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property6_value, scene.shift_pt_property6_owner)
        return {'FINISHED'}
class PropertyToolsOp7Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator7_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property7_value, scene.shift_pt_property7_owner)
        return {'FINISHED'}
class PropertyToolsOp8Check (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator8_check"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processCheckNames (scene.shift_pt_property8_value, scene.shift_pt_property8_owner)
        return {'FINISHED'}

class PropertyToolsOpRemoveUV (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_remove_uv"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove UV layer from multiple objects by its name"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processRemoveUV (scene.shift_pt_name_uv, scene.shift_pt_preserve)
        return {'FINISHED'}
    
class PropertyToolsOpRemoveAllUV (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_remove_all_uv"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove all UV layers from multiple objects"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processRemoveAllUV (scene.shift_pt_preserve)
        return {'FINISHED'}
    
class PropertyToolsOpRemoveColor (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_remove_color"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove vertex color layer from multiple objects by its name"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processRemoveColor (scene.shift_pt_name_color, scene.shift_pt_preserve)
        return {'FINISHED'}
    
class PropertyToolsOpRemoveAllColor (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_remove_all_color"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Remove all vertex color layers from multiple objects"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        scene = bpy.context.scene
        processRemoveAllColor (scene.shift_pt_preserve)
        return {'FINISHED'}
    
class PropertyToolsOpToogleAllEdges (bpy.types.Operator):
    bl_idname   = "object.property_tools_operator_toogle_all_edges"
    bl_label    = "SHIFT - Property Tools"
    bl_description  = "Toogle of displaing of all edges in wire mode for all selected meshes"
    bl_register = True
    bl_undo     = False
    def execute (self, context):        
        selected = bpy.context.selected_objects
        
        for obj in selected:
            if (obj.type == 'MESH'):    obj.data.show_all_edges = not obj.data.show_all_edges
        
        return {'FINISHED'}

class PropertyNames (bpy.types.PropertyGroup):
    name = StringProperty (name='Name', description='Name of the property', maxlen = 128, default='none')
    
class PropertyToolsPanel (bpy.types.Panel):
     
    bl_idname   = "object.property_tools_panel"
    bl_label    = "SHIFT - Property Tools"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):
        
        layout = self.layout;   layout_ = layout

        box1 = layout.box   ()

        box = box1.box      ()
        split = box.split   (percentage = 0.8, align = True)
        split.operator      ('object.property_tools_operator_remove_uv',        'Remove')
        split.operator      ('object.property_tools_operator_remove_all_uv',    'All')
        box.prop            (context.scene, 'shift_pt_name_uv')

        box = box1.box      ()
        split = box.split   (percentage = 0.8, align = True)
        split.operator      ('object.property_tools_operator_remove_color',     'Remove')
        split.operator      ('object.property_tools_operator_remove_all_color', 'All')
        box.prop            (context.scene, 'shift_pt_name_color')

        box = box1.box      ()
        box.prop            (context.scene, 'shift_pt_preserve')
        
        layout.separator ()

        layout = layout.box ()
        
        row = layout.row    (align = True)
        row.operator        ('object.property_tools_operator_set',    'Set')
        row.operator        ('object.property_tools_operator_clear',  'Clear')
        row.operator        ('object.property_tools_operator_remove', 'Remove')

        for i in range (8):

            n = i + 1
        
            box = layout.box    ()
            box1 = box.box      ()
            box1.prop_search    (context.scene, 'shift_pt_property' + str (n), context.scene, 'shift_pt_history')
            split = box1.split  (percentage = 0.95, align = True)
            split.prop          (context.scene, 'shift_pt_property' + str (n) + '_value')
            split.operator      ('object.property_tools_operator' + str (n) + '_check', 'C')
            
            row = box.row       (align = True)
            row.operator        ('object.property_tools_operator' + str (n) + '_set',      'Set')
            row.operator        ('object.property_tools_operator' + str (n) + '_clear',    'Clear')
            row.operator        ('object.property_tools_operator' + str (n) + '_remove',   'Remove')
            row.separator       ()
            row.separator       ()
            row.prop            (context.scene, 'shift_pt_property' + str (n) + '_owner')
        
        box = layout.box    ()
        box.prop            (context.scene, 'shift_pt_overwrite')

        box = layout_.box   ()
        box.operator        ('object.property_tools_operator_toogle_all_edges',    'Toogle Display All Edges')
        
        layout_.separator   ()
                        
def register ():

    bpy.utils.register_module (__name__)

    # options

    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_name_uv = StringProperty (
        name        = "UV Texture",
        description = "Name of UV layer",
        default     = "")
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_name_color = StringProperty (
        name        = "Vertex Colors",
        description = "Name of vertex color layer",
        default     = "")

    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_preserve = BoolProperty (
        name        = "Preserve Vertex Normals",
        description = "Preserves vertex normals",
        default     = False)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_property1 = StringProperty (
        name        = "1. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property2 = StringProperty (
        name        = "2. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property3 = StringProperty (
        name        = "3. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property4 = StringProperty (
        name        = "4. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property5 = StringProperty (
        name        = "5. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property6 = StringProperty (
        name        = "6. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property7 = StringProperty (
        name        = "7. Name",
        description = "Name of property",
        default     = "")
    bpy.types.Scene.shift_pt_property8 = StringProperty (
        name        = "8. Name",
        description = "Name of property",
        default     = "")
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_property1_value = StringProperty (
        name        = "1. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property2_value = StringProperty (
        name        = "2. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property3_value = StringProperty (
        name        = "3. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property4_value = StringProperty (
        name        = "4. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property5_value = StringProperty (
        name        = "5. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property6_value = StringProperty (
        name        = "6. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property7_value = StringProperty (
        name        = "7. Value",
        description = "Value of property",
        default     = "")
    bpy.types.Scene.shift_pt_property8_value = StringProperty (
        name        = "8. Value",
        description = "Value of property",
        default     = "")

    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_property1_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property2_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property3_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property4_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property5_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property6_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property7_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
    bpy.types.Scene.shift_pt_property8_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("0","Obj","Set property to object"),
               ("1","Msh","Set property to object data"),
               ("2","Mat","Set property to active material of object"),
               ("3","Tex","Set property to active texture of object"),
               ("4","Par","Set property to active particle system settings of object"),
              ],
        default='0')
            
    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_overwrite = BoolProperty (
        name        = "Overwrite",
        description = "Overwrites existing properties",
        default     = True)    

    # ----------------------------------------------------------
    bpy.types.Scene.shift_pt_history = CollectionProperty (
        type        = PropertyNames,
        name        = 'History',
        description = 'Property names history')
     
def unregister ():
    
    bpy.utils.unregister_module (__name__)

    del bpy.types.Scene.shift_pt_name_uv
    del bpy.types.Scene.shift_pt_name_color

    del bpy.types.Scene.shift_pt_preserve
    
    del bpy.types.Scene.shift_pt_property1
    del bpy.types.Scene.shift_pt_property2
    del bpy.types.Scene.shift_pt_property3
    del bpy.types.Scene.shift_pt_property4
    del bpy.types.Scene.shift_pt_property5
    del bpy.types.Scene.shift_pt_property6
    del bpy.types.Scene.shift_pt_property7
    del bpy.types.Scene.shift_pt_property8
        
    del bpy.types.Scene.shift_pt_property1_value
    del bpy.types.Scene.shift_pt_property2_value
    del bpy.types.Scene.shift_pt_property3_value
    del bpy.types.Scene.shift_pt_property4_value
    del bpy.types.Scene.shift_pt_property5_value
    del bpy.types.Scene.shift_pt_property6_value
    del bpy.types.Scene.shift_pt_property7_value
    del bpy.types.Scene.shift_pt_property8_value
    
    del bpy.types.Scene.shift_pt_property1_owner
    del bpy.types.Scene.shift_pt_property2_owner
    del bpy.types.Scene.shift_pt_property3_owner
    del bpy.types.Scene.shift_pt_property4_owner
    del bpy.types.Scene.shift_pt_property5_owner
    del bpy.types.Scene.shift_pt_property6_owner
    del bpy.types.Scene.shift_pt_property7_owner
    del bpy.types.Scene.shift_pt_property8_owner
    
    del bpy.types.Scene.shift_pt_overwrite
    del bpy.types.Scene.shift_pt_history

if __name__ == "__main__":
    
    register ()
