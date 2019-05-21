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
    "name"              : "SHIFT - Batch Property",
    "author"            : "Andrej Szontagh",
    "version"           : (1,0),
    "blender"           : (2, 5, 9),
    "api"               : 39307,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Set and manage custom properites for all selected objects at once"}

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

    literals.append (('l3', '%' + keyword + '>>>>'))
    literals.append (('l2', '%' + keyword + '>>>'))
    literals.append (('l1', '%' + keyword + '>>'))
    literals.append (('l0', '%' + keyword + '>'))
    literals.append (('r3', '%' + keyword + '<<<<'))
    literals.append (('r2', '%' + keyword + '<<<'))
    literals.append (('r1', '%' + keyword + '<<'))
    literals.append (('r0', '%' + keyword + '<'))

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
        if not  r [0]:  result = result.replace (r [1], substition_string)
        elif    r [0][0] == 'l':
            try:    i = int (r[0][1]);  result = result.replace (r [1], substition_string.split  (r [2], i + 1)[i + 1])
            except: pass
        elif    r [0][0] == 'r':
            try:    i = int (r[0][1]);  result = result.replace (r [1], substition_string.rsplit (r [2], i + 1)[0])
            except: pass

    return (result)
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### CHECK NAMES
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processCheckNames (op, name, owner):

    op.report ({'INFO'}, "Check names : ")
    op.report ({'INFO'}, "")

    # parsing formatting string
    repl1 = formatNameParse (name, 'name')
    repl2 = formatNameParse (name, 'nameo')
    repl3 = formatNameParse (name, 'named')

    # object
    if   (owner == '1'):

        for obj in bpy.context.selected_objects:
            try:
                owner = obj.name;
                fname = formatName (name,  owner, repl1);
                fname = formatName (fname, obj.name, repl2);
                fname = formatName (fname, obj.data.name, repl3);
                op.report ({'INFO'}, "Object : '" + obj.name + "'" + (" " * (40 - len (obj.name))) + "Owner : '" + owner + "'" + (" " * (40 - len (owner))) + " Name : '" + fname + "'");
            except: pass
            
    # data
    elif (owner == '2'):

        for obj in bpy.context.selected_objects:
            try:
                owner = obj.data.name;
                fname = formatName (name,  owner, repl1);
                fname = formatName (fname, obj.name, repl2);
                fname = formatName (fname, obj.data.name, repl3);
                op.report ({'INFO'}, "Object : '" + obj.name + "'" + (" " * (40 - len (obj.name))) + "Owner : '" + owner + "'" + (" " * (40 - len (owner))) + " Name : '" + fname + "'");
            except: pass

    # material
    elif (owner == '3'):

        for obj in bpy.context.selected_objects:
            try:
                owner = obj.active_material.name;
                fname = formatName (name,  owner, repl1);
                fname = formatName (fname, obj.name, repl2);
                fname = formatName (fname, obj.data.name, repl3);
                op.report ({'INFO'}, "Object : '" + obj.name + "'" + (" " * (40 - len (obj.name))) + "Owner : '" + owner + "'" + (" " * (40 - len (owner))) + " Name : '" + fname + "'");
            except: pass

    # texture
    elif (owner == '4'):

        for obj in bpy.context.selected_objects:
            try:
                owner = obj.active_material.active_texture.name;
                fname = formatName (name,  owner, repl1);
                fname = formatName (fname, obj.name, repl2);
                fname = formatName (fname, obj.data.name, repl3);
                op.report ({'INFO'}, "Object : '" + obj.name + "'" + (" " * (40 - len (obj.name))) + "Owner : '" + owner + "'" + (" " * (40 - len (owner))) + " Name : '" + fname + "'");
            except: pass
            
    # particle settings
    elif (owner == '5'):

        for obj in bpy.context.selected_objects:
            try:
                owner = obj.particle_systems.active.settings.name;
                fname = formatName (name,  owner, repl1);
                fname = formatName (fname, obj.name, repl2);
                fname = formatName (fname, obj.data.name, repl3);
                op.report ({'INFO'}, "Object : '" + obj.name + "'" + (" " * (40 - len (obj.name))) + "Owner : '" + owner + "'" + (" " * (40 - len (owner))) + " Name : '" + fname + "'");
            except: pass
            
    op.report ({'INFO'}, "")
    op.report ({'INFO'}, "Readme !")
            
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROPERTY REMOVE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def removeProperty (name, owner):

    if (name != ''):

        # object
        if   (owner == '1'):

            for obj in bpy.context.selected_objects:
                try:    del obj [name]
                except: pass
                    
        # data
        elif (owner == '2'):

            for obj in bpy.context.selected_objects:
                try:    del obj.data [name]
                except: pass

        # material
        elif (owner == '3'):

            for obj in bpy.context.selected_objects:
                try:    del obj.active_material [name]
                except: pass

        # texture
        elif (owner == '4'):

            for obj in bpy.context.selected_objects:
                try:    del obj.active_material.active_texture [name]
                except: pass

        # particle settings
        elif (owner == '5'):

            for obj in bpy.context.selected_objects:
                try:    del obj.particle_systems.active.settings [name]
                except: pass
                
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROPERTY SET
####------------------------------------------------------------------------------------------------------------------------------------------------------
                
def setProperty (op, name, value, owner, overwrite):

    props = bpy.context.scene.shift_batchproperty

    success = False

    if (name != ''):

        value_ = value
        
        try:    value = int (value)
        except:
            try:    value = float (value)
            except: pass

        if type (value) == str :

            # parsing formatting string
            repl  = formatNameParse (value, 'name')
            replo = formatNameParse (value, 'nameo')
            repld = formatNameParse (value, 'named')

            # object
            if   (owner == '1'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            fname = formatName (value, obj.name, replo)
                            fname = formatName (fname, obj.data.name, repld)
                            obj [name] = formatName (fname, obj.name, repl)
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj [name];
                            
                            op.report ({'INFO'}, "WARNING | Property already exist : object '" + obj.name + "', property '" + name + "'");
                            
                        except:
                            try:
                                fname = formatName (value, obj.name, replo)
                                fname = formatName (fname, obj.data.name, repld)
                                obj [name] = formatName (fname, obj.name, repl)
                                success = True
                            except: pass
                        
            # data
            elif (owner == '2'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            fname = formatName (value, obj.name, replo)
                            fname = formatName (fname, obj.data.name, repld)
                            obj.data [name] = formatName (fname, obj.data.name, repl)
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.data [name];

                            op.report ({'INFO'}, "WARNING | Property already exist : data '" + obj.data.name + "', property '" + name + "'");
                            
                        except:
                            try:
                                fname = formatName (value, obj.name, replo)
                                fname = formatName (fname, obj.data.name, repld)
                                obj.data [name] = formatName (fname, obj.data.name, repl)
                                success = True
                            except: pass

            # material
            elif (owner == '3'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            fname = formatName (value, obj.name, replo)
                            fname = formatName (fname, obj.data.name, repld)
                            obj.active_material [name] = formatName (fname, obj.active_material.name, repl)                            
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.active_material [name];

                            op.report ({'INFO'}, "WARNING | Property already exist : material '" + obj.active_material.name + "', property '" + name + "'");
                        
                        except:
                            try:
                                fname = formatName (value, obj.name, replo)
                                fname = formatName (fname, obj.data.name, repld)
                                obj.active_material [name] = formatName (fname, obj.active_material.name, repl)
                                success = True
                            except: pass

            # texture
            elif (owner == '4'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            fname = formatName (value, obj.name, replo)
                            fname = formatName (fname, obj.data.name, repld)
                            obj.active_material.active_texture [name] = formatName (fname, obj.active_material.active_texture.name, repl)
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.active_material.active_texture [name];
                            
                            op.report ({'INFO'}, "WARNING | Property already exist : texture'" + obj.active_material.active_texture.name + "', property '" + name + "'");

                        except:
                            try:
                                fname = formatName (value, obj.name, replo)
                                fname = formatName (fname, obj.data.name, repld)
                                obj.active_material.active_texture [name] = formatName (fname, obj.active_material.active_texture.name, repl)
                                success = True
                            except: pass
                        
            # particle settings
            elif (owner == '5'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            fname = formatName (value, obj.name, replo)
                            fname = formatName (fname, obj.data.name, repld)
                            obj.particle_systems.active.settings [name] = formatName (fname, obj.particle_systems.active.settings.name, repl)
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.particle_systems.active.settings [name];

                            op.report ({'INFO'}, "WARNING | Property already exist : particle system settings'" + obj.particle_systems.active.settings.name + "', property '" + name + "'");
                            
                        except:
                            try:
                                fname = formatName (value, obj.name, replo)
                                fname = formatName (fname, obj.data.name, repld)
                                obj.particle_systems.active.settings [name] = formatName (fname, obj.particle_systems.active.settings.name, repl)
                                success = True
                            except: pass
                        
        else :

            # object
            if   (owner == '1'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            obj [name] = value
                            success = True                            
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj [name]

                            op.report ({'INFO'}, "WARNING | Property already exist : object '" + obj.name + "', property '" + name + "'");
                            
                        except:
                            obj [name] = value
                            success = True                            
                        
            # data
            elif (owner == '2'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.data [name] = value
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.data [name];

                            op.report ({'INFO'}, "WARNING | Property already exist : data '" + obj.data.name + "', property '" + name + "'");
                            
                        except:
                            obj.data [name] = value
                            success = True

            # material
            elif (owner == '3'):

                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.active_material [name] = value
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.active_material [name];
                            
                            op.report ({'INFO'}, "WARNING | Property already exist : material '" + obj.active_material.name + "', property '" + name + "'");
                            
                        except:
                            obj.active_material [name] = value
                            success = True

            # texture
            elif (owner == '4'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.active_material.active_texture [name] = value
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.active_material.active_texture [name];

                            op.report ({'INFO'}, "WARNING | Property already exist : texture'" + obj.active_material.active_texture.name + "', property '" + name + "'");
                            
                        except:
                            obj.active_material.active_texture [name] = value
                            success = True

            # particle settings
            elif (owner == '5'):
                
                if (overwrite):
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.particle_systems.active.settings [name] = value
                            success = True
                        except: pass
                else:
                    for obj in bpy.context.selected_objects:
                        try:
                            obj.particle_systems.active.settings [name];

                            op.report ({'INFO'}, "WARNING | Property already exist : particle system settings'" + obj.particle_systems.active.settings.name + "', property '" + name + "'");
                            
                        except:
                            obj.particle_systems.active.settings [name] = value
                            success = True


    # add property name and value into history

    if (success):

        found = False
        for l in range (len (props.history_names)):

            if (props.history_names [l].name == name):      found = True;   break;

        if (not found):
            props.history_names.add ();     props.history_names [-1].name = name;

        found = False
        for l in range (len (props.history_values)):

            if (props.history_values [l].name == name):     found = True;   break;

        if (not found):
            props.history_values.add ();    props.history_values [-1].name = value_;
            
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SET
####------------------------------------------------------------------------------------------------------------------------------------------------------
    
def process1Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property1_name, props.property1_value, props.property1_owner, props.overwrite)
def process2Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property2_name, props.property2_value, props.property2_owner, props.overwrite)
def process3Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property3_name, props.property3_value, props.property3_owner, props.overwrite)
def process4Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property4_name, props.property4_value, props.property4_owner, props.overwrite)
def process5Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property5_name, props.property5_value, props.property5_owner, props.overwrite)
def process6Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property6_name, props.property6_value, props.property6_owner, props.overwrite)
def process7Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property7_name, props.property7_value, props.property7_owner, props.overwrite)
def process8Set     (op): props = bpy.context.scene.shift_batchproperty;  setProperty (op, props.property8_name, props.property8_value, props.property8_owner, props.overwrite)

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS REMOVE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def process1Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property1_name, props.property1_owner) 
def process2Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property2_name, props.property2_owner)
def process3Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property3_name, props.property3_owner)
def process4Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property4_name, props.property4_owner)
def process5Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property5_name, props.property5_owner)
def process6Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property6_name, props.property6_owner)
def process7Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property7_name, props.property7_owner)
def process8Remove  (op): props = bpy.context.scene.shift_batchproperty;  removeProperty (op, props.property8_name, props.property8_owner)

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS CLEAR
####------------------------------------------------------------------------------------------------------------------------------------------------------

def process1Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property1_name = '';  props.property1_value = '';
def process2Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property2_name = '';  props.property2_value = '';
def process3Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property3_name = '';  props.property3_value = '';
def process4Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property4_name = '';  props.property4_value = '';
def process5Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property5_name = '';  props.property5_value = '';
def process6Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property6_name = '';  props.property6_value = '';
def process7Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property7_name = '';  props.property7_value = '';
def process8Clear   (): props = bpy.context.scene.shift_batchproperty;  props.property8_name = '';  props.property8_value = '';

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SWITCH BANK
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSwitchBank   (bank):

    props = bpy.context.scene.shift_batchproperty        

    # create bank fields
    if (len (props.propertyfields) != 128):

        for i in range (128):

            props.propertyfields.add ()

    # offsets
    bank_active = (props.bank  - 1) * 8
    bank_new    = (bank        - 1) * 8

    # save actual values
    
    props.propertyfields [bank_active + 0].name = props.property1_name;
    props.propertyfields [bank_active + 1].name = props.property2_name;
    props.propertyfields [bank_active + 2].name = props.property3_name;
    props.propertyfields [bank_active + 3].name = props.property4_name;
    props.propertyfields [bank_active + 4].name = props.property5_name;
    props.propertyfields [bank_active + 5].name = props.property6_name;
    props.propertyfields [bank_active + 6].name = props.property7_name;
    props.propertyfields [bank_active + 7].name = props.property8_name;

    props.propertyfields [bank_active + 0].value = props.property1_value;
    props.propertyfields [bank_active + 1].value = props.property2_value;
    props.propertyfields [bank_active + 2].value = props.property3_value;
    props.propertyfields [bank_active + 3].value = props.property4_value;
    props.propertyfields [bank_active + 4].value = props.property5_value;
    props.propertyfields [bank_active + 5].value = props.property6_value;
    props.propertyfields [bank_active + 6].value = props.property7_value;
    props.propertyfields [bank_active + 7].value = props.property8_value;
    
    props.propertyfields [bank_active + 0].owner = props.property1_owner;
    props.propertyfields [bank_active + 1].owner = props.property2_owner;
    props.propertyfields [bank_active + 2].owner = props.property3_owner;
    props.propertyfields [bank_active + 3].owner = props.property4_owner;
    props.propertyfields [bank_active + 4].owner = props.property5_owner;
    props.propertyfields [bank_active + 5].owner = props.property6_owner;
    props.propertyfields [bank_active + 6].owner = props.property7_owner;
    props.propertyfields [bank_active + 7].owner = props.property8_owner;
    
    # restore values from new bank

    props.property1_name = props.propertyfields [bank_new + 0].name;
    props.property2_name = props.propertyfields [bank_new + 1].name;
    props.property3_name = props.propertyfields [bank_new + 2].name;
    props.property4_name = props.propertyfields [bank_new + 3].name;
    props.property5_name = props.propertyfields [bank_new + 4].name;
    props.property6_name = props.propertyfields [bank_new + 5].name;
    props.property7_name = props.propertyfields [bank_new + 6].name;
    props.property8_name = props.propertyfields [bank_new + 7].name;

    props.property1_value = props.propertyfields [bank_new + 0].value;
    props.property2_value = props.propertyfields [bank_new + 1].value;
    props.property3_value = props.propertyfields [bank_new + 2].value;
    props.property4_value = props.propertyfields [bank_new + 3].value;
    props.property5_value = props.propertyfields [bank_new + 4].value;
    props.property6_value = props.propertyfields [bank_new + 5].value;
    props.property7_value = props.propertyfields [bank_new + 6].value;
    props.property8_value = props.propertyfields [bank_new + 7].value;
    
    props.property1_owner = props.propertyfields [bank_new + 0].owner;
    props.property2_owner = props.propertyfields [bank_new + 1].owner;
    props.property3_owner = props.propertyfields [bank_new + 2].owner;
    props.property4_owner = props.propertyfields [bank_new + 3].owner;
    props.property5_owner = props.propertyfields [bank_new + 4].owner;
    props.property6_owner = props.propertyfields [bank_new + 5].owner;
    props.property7_owner = props.propertyfields [bank_new + 6].owner;
    props.property8_owner = props.propertyfields [bank_new + 7].owner;
    
    # set new bank
    props.bank = bank
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------

class SHIFT_BatchProperty_OpSet (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set all properties to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Set (self)
        process2Set (self)
        process3Set (self)
        process4Set (self)
        process5Set (self)
        process6Set (self)
        process7Set (self)
        process8Set (self)
        return {'FINISHED'}

class SHIFT_BatchProperty_OpClear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_clear"
    bl_label    = "SHIFT - Batch Property"
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
    
class SHIFT_BatchProperty_OpRemove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove all properties from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Remove (self)
        process2Remove (self)
        process3Remove (self)
        process4Remove (self)
        process5Remove (self)
        process6Remove (self)
        process7Remove (self)
        process8Remove (self)
        return {'FINISHED'}
    
class SHIFT_BatchProperty_Op1Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator1_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Set (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op2Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator2_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process2Set (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op3Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator3_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process3Set (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op4Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator4_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process4Set (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op5Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator5_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process5Set (self)        
        return {'FINISHED'}    
class SHIFT_BatchProperty_Op6Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator6_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process6Set (self)        
        return {'FINISHED'}
class SHIFT_BatchProperty_Op7Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator7_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process7Set (self)        
        return {'FINISHED'}
class SHIFT_BatchProperty_Op8Set (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator8_set"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set property to all selected objects"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process8Set (self)        
        return {'FINISHED'}
    
class SHIFT_BatchProperty_Op1Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator1_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Clear ()
        return {'FINISHED'}
class SHIFT_BatchProperty_Op2Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator2_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process2Clear ()
        return {'FINISHED'}
class SHIFT_BatchProperty_Op3Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator3_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process3Clear ()
        return {'FINISHED'}
class SHIFT_BatchProperty_Op4Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator4_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process4Clear ()
        return {'FINISHED'}
class SHIFT_BatchProperty_Op5Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator5_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process5Clear ()        
        return {'FINISHED'}    
class SHIFT_BatchProperty_Op6Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator6_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process6Clear ()        
        return {'FINISHED'}
class SHIFT_BatchProperty_Op7Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator7_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process7Clear ()        
        return {'FINISHED'}
class SHIFT_BatchProperty_Op8Clear (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator8_clear"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Clear property name and value"
    bl_register = True
    bl_undo     = True    
    def execute (self, context):
        process8Clear ()        
        return {'FINISHED'}

class SHIFT_BatchProperty_Op1Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator1_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process1Remove (self)
        return {'FINISHED'}    
class SHIFT_BatchProperty_Op2Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator2_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process2Remove (self)
        return {'FINISHED'}    
class SHIFT_BatchProperty_Op3Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator3_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process3Remove (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op4Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator4_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process4Remove (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op5Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator5_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process5Remove (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op6Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator6_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process6Remove (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op7Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator7_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process7Remove (self)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op8Remove (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator8_remove"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Remove property from all selected objects"
    bl_register = True
    bl_undo     = True
    def execute (self, context):
        process8Remove (self)
        return {'FINISHED'}

class SHIFT_BatchProperty_Op1Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator1_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property1_value, props.property1_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op2Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator2_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property2_value, props.property2_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op3Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator3_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property3_value, props.property3_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op4Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator4_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property4_value, props.property4_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op5Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator5_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property5_value, props.property5_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op6Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator6_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property6_value, props.property6_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op7Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator7_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property7_value, props.property7_owner)
        return {'FINISHED'}
class SHIFT_BatchProperty_Op8Check (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator8_check"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Prints formatted name(s)"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        props = bpy.context.scene.shift_batchproperty        
        processCheckNames (self, props.property8_value, props.property8_owner)
        return {'FINISHED'}

class SHIFT_BatchProperty_Op1Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank1"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 1"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (1);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op2Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank2"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 2"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (2);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op3Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank3"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 3"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (3);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op4Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank4"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 4"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (4);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op5Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank5"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 5"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (5);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op6Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank6"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 6"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (6);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op7Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank7"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 7"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (7);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op8Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank8"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 8"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (8);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op9Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank9"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 9"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (9);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op10Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank10"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 10"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (10);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op11Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank11"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 11"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (11);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op12Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank12"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 12"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (12);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op13Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank13"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 13"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (13);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op14Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank14"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 14"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (14);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op15Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank15"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 15"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (15);
        return {'FINISHED'}
class SHIFT_BatchProperty_Op16Bank (bpy.types.Operator):
    bl_idname   = "object.batch_property_operator_bank16"
    bl_label    = "SHIFT - Batch Property"
    bl_description  = "Set bank 16"
    bl_register = True
    bl_undo     = False
    def execute (self, context):
        processSwitchBank (16);
        return {'FINISHED'}

class SHIFT_BatchProperty_OpHelp (bpy.types.Operator):

    bl_idname       = "object.batch_property_operator_help"
    bl_label        = "SHIFT - Batch Property"
    bl_description  = "Prints help information about supported expressions into info panel."
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        self.report ({'INFO'}, "")
        self.report ({'INFO'}, "Batch Property Help ..")
        self.report ({'INFO'}, "")
        self.report ({'INFO'}, "Variations (value field) : ")
        self.report ({'INFO'}, " - Expression : '..%nameo%..'                    - object name")
        self.report ({'INFO'}, " - Expression : '..%named%..'                    - object data name")
        self.report ({'INFO'}, " - Expression : '..%name%..'                     - object/datablock name")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]>[delimiter]%..'    - object/datablock name cut from 1. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]>>[delimiter]%..'   - object/datablock name cut from 2. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]>>>[delimiter]%..'  - object/datablock name cut from 3. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]>>>>[delimiter]%..' - object/datablock name cut from 4. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]<[delimiter]%..'    - object/datablock name cut from 1. occurence of delimiter string from right.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]<<[delimiter]%..'   - object/datablock name cut from 2. occurence of delimiter string from right.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]<<<[delimiter]%..'  - object/datablock name cut from 3. occurence of delimiter string from right.")
        self.report ({'INFO'}, " - Expression : '..%name[o/d]<<<<[delimiter]%..' - object/datablock name cut from 4. occurence of delimiter string from right.")
        self.report ({'INFO'}, "")        
        self.report ({'INFO'}, "Examples : ")
        self.report ({'INFO'}, " - Expression : '%name<.%_special'          = 'myobject.011'      -> 'myobject_special'")
        self.report ({'INFO'}, " - Expression : '%nameo>_%_special'         = 'a_aa_myobject.011' -> 'aa_myobject.011_special'")
        self.report ({'INFO'}, " - Expression : 'group1%named>>_%_special'  = 'a_aa_myobject.011' -> 'group1myobject.011_special'")
        self.report ({'INFO'}, "")
        self.report ({'INFO'}, "Readme !")

        return {'FINISHED'}

class PropertyNames (bpy.types.PropertyGroup):
    
    name = StringProperty (name='Name',  description='Name  of the property', maxlen = 128, default='none')
    
class PropertyValues (bpy.types.PropertyGroup):
    
    name = StringProperty (name='Value', description='Value of the property', maxlen = 128, default='none')
    
class PropertyFields (bpy.types.PropertyGroup):
    
    name = StringProperty (
        name        = "Name",
        description = "Name of property",
        default     = "")
    
    value = StringProperty (
        name        = "Value",
        description = "Value of property",
        default     = "")
    
    owner = EnumProperty (
        name        = "",
        description = "Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default     = '1')
    
class SHIFT_BatchProperty_panel (bpy.types.Panel):
     
    bl_idname   = "object.batch_property_panel"
    bl_label    = "SHIFT - Batch Property"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):

        props = bpy.context.scene.shift_batchproperty        

        layout = self.layout;   layout_ = layout

        layout.label       ('Set properties for all selected objects at once')
        
        layout = layout_.box ()

        col = layout.column (align = True)
        
        row = col.row    (align = True)
        for i in range (8):
            bank = 1 + i;   n = str (bank)
            if (bank == props.bank):    row.operator    ('object.batch_property_operator_bank' + n, n, emboss = False)
            else:                       row.operator    ('object.batch_property_operator_bank' + n, n, emboss = True)
        
        row = col.row    (align = True)
        for i in range (8):
            bank = 9 + i;   n = str (bank)
            if (bank == props.bank):    row.operator    ('object.batch_property_operator_bank' + n, n, emboss = False)
            else:                       row.operator    ('object.batch_property_operator_bank' + n, n, emboss = True)

        layout = layout_.box ()
        
        row = layout.row    (align = True)
        row.operator        ('object.batch_property_operator_set',    'Set')
        row.operator        ('object.batch_property_operator_clear',  'Clear')
        row.operator        ('object.batch_property_operator_remove', 'Remove')

        for i in range (8):

            n = i + 1
        
            box = layout.box    ()
            box_ = box.box      ()
            box_.prop_search    (props, 'property' + str (n) + '_name',  props, 'history_names')
            split = box_.split  (percentage = 0.95, align = True)
            split.prop_search   (props, 'property' + str (n) + '_value', props, 'history_values')
            split.operator      ('object.batch_property_operator' + str (n) + '_check', 'C')
            
            row = box.row       (align = True)
            row.operator        ('object.batch_property_operator' + str (n) + '_set',      'Set')
            row.operator        ('object.batch_property_operator' + str (n) + '_clear',    'Clear')
            row.operator        ('object.batch_property_operator' + str (n) + '_remove',   'Remove')
            row.separator       ()
            row.separator       ()
            row.prop            (props, 'property' + str (n) + '_owner')
        
        box = layout.box    ()
        split = box.split   (percentage = 0.5, align = False)
        split.prop          (props, 'overwrite')
        split.operator      ('object.batch_property_operator_help', 'Help')
        
        layout_.separator   ()


class SHIFT_BatchProperty_props (bpy.types.PropertyGroup):
    """
    bpy.context.scene.shift_batchproperty
    """
    
    # options

    propertyfields = CollectionProperty (
        type        = PropertyFields,
        name        = 'Property Fields',
        description = 'Property values and properties collection')
        
    # ----------------------------------------------------------
    bank = IntProperty (
        name        = "Bank",
        description = "Active bank",
        min         = 1,
        max         = 16,
        default     = 1)

    # ----------------------------------------------------------
    property1_name = StringProperty (
        name        = "1. Name",
        description = "Name of property",
        default     = "")
    property2_name = StringProperty (
        name        = "2. Name",
        description = "Name of property",
        default     = "")
    property3_name = StringProperty (
        name        = "3. Name",
        description = "Name of property",
        default     = "")
    property4_name = StringProperty (
        name        = "4. Name",
        description = "Name of property",
        default     = "")
    property5_name = StringProperty (
        name        = "5. Name",
        description = "Name of property",
        default     = "")
    property6_name = StringProperty (
        name        = "6. Name",
        description = "Name of property",
        default     = "")
    property7_name = StringProperty (
        name        = "7. Name",
        description = "Name of property",
        default     = "")
    property8_name = StringProperty (
        name        = "8. Name",
        description = "Name of property",
        default     = "")
    
    # ----------------------------------------------------------
    property1_value = StringProperty (
        name        = "1. Value",
        description = "Value of property",
        default     = "")
    property2_value = StringProperty (
        name        = "2. Value",
        description = "Value of property",
        default     = "")
    property3_value = StringProperty (
        name        = "3. Value",
        description = "Value of property",
        default     = "")
    property4_value = StringProperty (
        name        = "4. Value",
        description = "Value of property",
        default     = "")
    property5_value = StringProperty (
        name        = "5. Value",
        description = "Value of property",
        default     = "")
    property6_value = StringProperty (
        name        = "6. Value",
        description = "Value of property",
        default     = "")
    property7_value = StringProperty (
        name        = "7. Value",
        description = "Value of property",
        default     = "")
    property8_value = StringProperty (
        name        = "8. Value",
        description = "Value of property",
        default     = "")

    # ----------------------------------------------------------
    property1_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property2_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property3_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property4_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property5_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property6_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property7_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
    property8_owner = EnumProperty(
        name="",
        description="Select the poperty owner",
        items=[("0","Owner","Select the poperty owner"),
               ("1","Obj","Set property to object"),
               ("2","Dat","Set property to object data"),
               ("3","Mat","Set property to active material of object"),
               ("4","Tex","Set property to active texture of object"),
               ("5","Par","Set property to active particle system settings of object"),
              ],
        default='1')
            
    # ----------------------------------------------------------
    overwrite = BoolProperty (
        name        = "Overwrite",
        description = "Overwrites existing properties",
        default     = True)    

    # ----------------------------------------------------------
    history_names = CollectionProperty (
        type        = PropertyNames,
        name        = 'History (names)',
        description = 'Property names history')
                        
    # ----------------------------------------------------------
    history_values = CollectionProperty (
        type        = PropertyValues,
        name        = 'History (values)',
        description = 'Property values history')
    
def register ():

    bpy.utils.register_module (__name__)

    bpy.types.Scene.shift_batchproperty = bpy.props.PointerProperty (type = SHIFT_BatchProperty_props)
     
def unregister ():
    
    bpy.utils.unregister_module (__name__)

    try:    del bpy.types.Scene.shift_batchproperty
    except: pass

if __name__ == "__main__":
    
    register ()
