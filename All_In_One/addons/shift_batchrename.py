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
    "name"              : "SHIFT - Batch Rename",
    "author"            : "Andrej Szontagh",
    "version"           : (1,0),
    "blender"           : (2, 5, 9),
    "api"               : 39307,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Rename multiple objects at once"}


import bpy
import time
import operator
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
#### PROCESS RENAME
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processRename (op):

    start_time = time.clock ()

    # save list
    selected = list (bpy.context.selected_objects)

    # anything selected ?
    if len (selected) == 0: return

    props = bpy.context.scene.shift_batchrename

    # naming ..
    nameo = props.nameo
    named = props.named

    # parsing formatting string
    replo = formatNameParse (nameo, 'name')
    repld = formatNameParse (named, 'name')

    # process all objects
    for i, obj in enumerate (selected):

        if obj and obj.data:

            obj.name        = formatName (nameo, obj.name, replo)
            obj.data.name   = formatName (named, obj.data.name, repld)
              
            op.report ({'INFO'}, "Object : '" + obj.name + "'" + (" " * (40 - len (obj.name))) + " Data : '" + obj.data.name + "'")

    op.report ({'INFO'}, "Rename finished")    
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### CHECK NAMES
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processCheckNames (op):

    op.report ({'INFO'}, "")
    op.report ({'INFO'}, "Check names : ")
    op.report ({'INFO'}, "")

    props = bpy.context.scene.shift_batchrename

    # naming ..
    nameo = props.nameo
    named = props.named

    # parsing formatting string
    replo = formatNameParse (nameo, 'name')
    repld = formatNameParse (named, 'name')

    for obj in bpy.context.selected_objects:

        if obj and obj.data:

            nameoo = formatName (nameo, obj.name, replo)
            namedd = formatName (named, obj.data.name, repld)

            op.report ({'INFO'}, "Object : '" + nameoo + "'" + (" " * (40 - len (nameoo))) + " Data : '" + namedd + "'")
            
    op.report ({'INFO'}, "")
    op.report ({'INFO'}, "Read report")
            
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------

class SHIFT_BatchRename_Op (bpy.types.Operator):

    bl_idname       = "object.batch_rename_operator"
    bl_label        = "SHIFT - Batch Rename"
    bl_description  = "Rename all selected objects using expression, result is printed into info panel."
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        props = bpy.context.scene.shift_batchrename

        processRename (self)
            
        return {'FINISHED'}

class SHIFT_BatchRename_OpCheck (bpy.types.Operator):

    bl_idname       = "object.batch_rename_operator_check"
    bl_label        = "SHIFT - Batch Rename"
    bl_description  = "Prints formatted name(s) into info panel, so you can check it before renaming."
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        props = bpy.context.scene.shift_batchrename
        
        processCheckNames (self)
        
        return {'FINISHED'}
        
class SHIFT_BatchRename_OpHelp (bpy.types.Operator):

    bl_idname       = "object.batch_rename_operator_help"
    bl_label        = "SHIFT - Batch Rename"
    bl_description  = "Prints help information about supported expressions into info panel."
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        self.report ({'INFO'}, "")
        self.report ({'INFO'}, "Batch Rename Help ..")
        self.report ({'INFO'}, "")
        self.report ({'INFO'}, "Variations : ")
        self.report ({'INFO'}, " - Expression : '..%name%..'                - original name")
        self.report ({'INFO'}, " - Expression : '..%name>[delimiter]%..'    - original name cut from 1. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name>>[delimiter]%..'   - original name cut from 2. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name>>>[delimiter]%..'  - original name cut from 3. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name>>>>[delimiter]%..' - original name cut from 4. occurence of delimiter string from left.")
        self.report ({'INFO'}, " - Expression : '..%name<[delimiter]%..'    - original name cut from 1. occurence of delimiter string from right.")
        self.report ({'INFO'}, " - Expression : '..%name<<[delimiter]%..'   - original name cut from 2. occurence of delimiter string from right.")
        self.report ({'INFO'}, " - Expression : '..%name<<<[delimiter]%..'  - original name cut from 3. occurence of delimiter string from right.")
        self.report ({'INFO'}, " - Expression : '..%name<<<<[delimiter]%..' - original name cut from 4. occurence of delimiter string from right.")
        self.report ({'INFO'}, "")        
        self.report ({'INFO'}, "Examples : ")
        self.report ({'INFO'}, " - Expression : '%name<.%_special'          = 'myobject.011'      -> 'myobject_special'")
        self.report ({'INFO'}, " - Expression : '%name>_%_special'          = 'a_aa_myobject.011' -> 'aa_myobject.011_special'")
        self.report ({'INFO'}, " - Expression : 'group1%name>>_%_special'   = 'a_aa_myobject.011' -> 'group1myobject.011_special'")
        self.report ({'INFO'}, "")
        self.report ({'INFO'}, "Readme !")

        return {'FINISHED'}
    
class SHIFT_BatchRename_panel (bpy.types.Panel):
     
    bl_idname   = "object.batch_rename_panel"
    bl_label    = "SHIFT - Batch Rename"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):

        props = bpy.context.scene.shift_batchrename
            
        layout = self.layout

        layout.label        ('Rename multiple objects at once')
        
        box = layout.box()
        split = box.split   (percentage = 0.7, align = False)        
        split.operator      ('object.batch_rename_operator', 'Rename')
        split.operator      ('object.batch_rename_operator_help', 'Help')

        box1 = box.box ()
        
        split = box1.split  (percentage = 0.95, align = True)
        split.prop          (props, 'nameo')
        split.operator      ('object.batch_rename_operator_check', 'C')
        
        split = box1.split  (percentage = 0.95, align = True)
        split.prop          (props, 'named')
        split.operator      ('object.batch_rename_operator_check', 'C')

class SHIFT_BatchRename_props (bpy.types.PropertyGroup):
    """
    bpy.context.scene.shift_batchrename
    """        
                        
    # options
        
    # ----------------------------------------------------------
    nameo = StringProperty (
        name        = "Object",
        description = "Formatting string determining name of object(s)",
        default     = "%name%",
        subtype     = 'NONE')
    named = StringProperty (
        name        = "Data",
        description = "Formatting string determining name of mesh datablock(s)",
        default     = "%name%",
        subtype     = 'NONE')
    
def register ():

    bpy.utils.register_module (__name__)

    bpy.types.Scene.shift_batchrename = bpy.props.PointerProperty (type = SHIFT_BatchRename_props)        
         
def unregister ():

    bpy.utils.unregister_module (__name__)

    try:    del bpy.types.Scene.shift_batchrename
    except: pass    
             
if __name__ == "__main__":
    
    register ()
