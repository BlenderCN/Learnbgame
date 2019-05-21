# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "vfx toolbox",
    "description": "various helper for vfx tasks.",
    "author": "Christian Brinkmann, David Wiesner",
    "version": (1, 5, 1),
    "blender": (2, 70, 0),
    "location": "3D View > Toolbox",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/p2or/blender-vfxtoolbox",
    "tracker_url": "https://github.com/p2or/blender-vfxtoolbox/issues",
    "category": "VFX"
    }


import bpy
import re
import math
from mathutils import Vector
from math import pi

from bpy.types import Panel
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

# ------------------------------------------------------------------------------------------------
# check naming limitation
# not required since blender 2.65
# ------------------------------------------------------------------------------------------------

def blender_namingLimitation(string):
    blender_version = bpy.app.version
    if blender_version[0] == 2 and blender_version[1] < 66 and len(string) > 21:
        return string[:21]
    else:
        return string

# ------------------------------------------------------------------------------------------------
# basic re functions
# ------------------------------------------------------------------------------------------------

def re_matchString(string, match):
    
    s = string
    n = re.match(r".*" + match + ".*", s)
    
    if n == None:
        return False
    else:
        return True

def re_matchString_ignoreCase(string, match):
    
    s = string
    n = re.match(r".*" + match + ".*", s, re.IGNORECASE) 
    return n


# ------------------------------------------------------------------------------------------------
# get all objects by search string
# ------------------------------------------------------------------------------------------------

def get_allObjectsBySearchString(search_string):

    matchArray = []

    for i in bpy.data.objects:
    
        if re_matchString(i.name, search_string) == True:
            matchArray.append(i)
        
    return matchArray

# ------------------------------------------------------------------------------------------------
# get number sequence
# ------------------------------------------------------------------------------------------------

def get_numberSequence(string):

    try:
        prae = re.findall("#+$", string)
        return '%0'+str(len(prae[0]))+'d', len(prae[0])

    except:
        return '%04d', 0

# ------------------------------------------------------------------------------------------------
# remove char
# ------------------------------------------------------------------------------------------------

def remove_specialCharactersFromString(string, char):
    return re.sub(char, '', string)


# ------------------------------------------------------------------------------------------------
# rename objects
# ------------------------------------------------------------------------------------------------
# new_name: Name_####

def rename_objectsByNewName(object_list, new_name):
    
    preafix = get_numberSequence(new_name)[0]    
    mainName = remove_specialCharactersFromString(new_name, '#')
    
    c = 0
    for i in object_list:
        dynPraefix = preafix % c
        i.name = mainName + dynPraefix
        c += 1
    
    return c

# ------------------------------------------------------------------------------------------------
# set empties
# ------------------------------------------------------------------------------------------------
# Arguments: size, type
# Size: float in [0.0001, 1000], default 0.0

def set_emptyType(selection_list, type):
    for obj in selection_list:
        if (obj.type == 'EMPTY'):
            obj.empty_draw_type = type
            

def set_emptySize(selection_list, size):
    for obj in selection_list:
        if (obj.type == 'EMPTY'):
            # float value 0.01 - 100
            obj.empty_draw_size = size
            

# ------------------------------------------------------------------------------------------------
# get object type (EMPTY, LAMP ... ) 
# ------------------------------------------------------------------------------------------------

def get_objectType(name_string):
    try:
        return bpy.data.objects[name_string].type
    except:
        return False


# ------------------------------------------------------------------------------------------------
# get object type list by object list
# ------------------------------------------------------------------------------------------------

def get_objectTypeList(object_list):
    objectTypes = []
    for i in object_list:
        objectTypes.append(bpy.data.objects[i.name].type)
    
    return list(set(objectTypes))


# ------------------------------------------------------------------------------------------------
# get object by name 
# ------------------------------------------------------------------------------------------------
# if object exists you get the object, else you get zero
# example: get_objectByName('Autoname_2938')
# returns: <bpy_struct, Object <"Autoname_2938">>

def get_objectByName(name_string):
    try:
        return bpy.data.objects[name_string]
    except:
        return False

    
# ------------------------------------------------------------------------------------------------
# make object active
# ------------------------------------------------------------------------------------------------
# make_objectActive('Autoname_2938')
# returns: <bpy_struct, Object <"Autoname_2938">>

def make_objectActive(objectdata):
    try:
        activeObj = bpy.context.scene.objects.active = objectdata
        return activeObj
    except:
        return False


# ------------------------------------------------------------------------------------------------
# get highlighted object by name string
# ------------------------------------------------------------------------------------------------
# if object exists you get the object, else you get zero
# bpy.ops.object.select_pattern(pattern='name_string')

def get_highlightObjectByName(name_string):
    try:
        return bpy.ops.object.select_pattern(pattern=name_string)
    except:
        return False

def get_highlightObjects(selection_list):
    
   for i in selection_list:
        bpy.data.objects[i.name].select = True  

def get_dehighlightObjects(selection_list):
    
   for i in selection_list:
        bpy.data.objects[i.name].select = False
        

# ------------------------------------------------------------------------------------------------
# get all objects in scene by type
# ------------------------------------------------------------------------------------------------
# searches for objects with the defined type in the whole scene

def get_allObjectsInSceneByType(type_string):
    
    objects = []
    
    # searches for type in the selection
    for objs in bpy.data.objects:
        if (objs.type == type_string):
            objects.append(objs)
    
    return objects


# ------------------------------------------------------------------------------------------------
# get objects in selection by type
# ------------------------------------------------------------------------------------------------
# searches for objects with the defined type in the selection 
# ignores all othe objects in selection and returns the given type  

# example:
# (get_ObjectsInSelectionByType('EMPTY'))
# returns: [bpy.data.objects['Auto_00100'], bpy.data.objects['Auto_00357']]

def get_ObjectsInSelectionByType(type_string):
    
    objects = []
    
    # searches for type in the selection
    for objs in bpy.context.selected_objects:
        if (objs.type == type_string):
            objects.append(objs)
    
    return objects


# ------------------------------------------------------------------------------------------------
# get objects in selection
# ------------------------------------------------------------------------------------------------

def get_AllObjectsInSelection():   
    return bpy.context.selected_objects


# ------------------------------------------------------------------------------------------------
# get objects in scene
# ------------------------------------------------------------------------------------------------

def get_AllObjectsInScene():   
    return bpy.data.objects


# ------------------------------------------------------------------------------------------------
# freeze objects
# ------------------------------------------------------------------------------------------------

def get_hideSelectObjects(object_list):
    for i in object_list:
        i.hide_select = True
    bpy.ops.object.select_all(action='DESELECT')
    return True 

def get_dehideSelectObjects(object_list):
    hidedObjs = []
    for i in object_list:
        if i.hide_select == True:
            i.hide_select = False
            hidedObjs.append(i)
    return hidedObjs


# ------------------------------------------------------------------------------------------------
# get objects location
# ------------------------------------------------------------------------------------------------
# objs: array of objects
# returns: array of locations

def get_objectLocation(objs):
    
    locations = []
    for i in objs:
        locations.append(i.location)
    
    return locations


# ------------------------------------------------------------------------------------------------
# get object Name without numbers
# ------------------------------------------------------------------------------------------------
# checks a string for numbersequence: _45896
# and returns it without numbersequence

def get_objectNameWithoutNumbers(string):   
    
    try:
        s = string
        n = re.sub(r"\d+$", "", s) # matches: numbersequence at the end
        n = re.sub(r"\_+$", "", n) # matches: underline-character at the end
        
        # if string only has digits -> reset
        if len(n) == 0:
            n=s
        return n
    
    except:
        return False


# ------------------------------------------------------------------------------------------------
# create vertices
# ------------------------------------------------------------------------------------------------
# name: string for new object name
# verts: 2 dimensional array of position coords - [(-1.0, 1.0, 0.0), (-1.0, -1.0, 0.0)]
# returns the new object


def create_Vertices (name, verts):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.show_name = True
    # Link object to scene
    bpy.context.scene.objects.link(ob)
    me.from_pydata(verts, [], [])
 
    # Update mesh with new data
    me.update()
    return ob


# ------------------------------------------------------------------------------------------------
# create polyline 
# ------------------------------------------------------------------------------------------------
# name: string for new object name
# verts: 2 dimensional array of position coords - [(-1.0, 1.0, 0.0), (-1.0, -1.0, 0.0)]
# edges: 2 dimensional array of vert ids - [(0,1)]
# returns the new object

# example:
# name_string = 'newLine', verts_array = [(-1.0, 1.0, 0.0), (-1.0, -1.0, 0.0)], edges_array = [(0,1)]
# temp = createLine(name_string, verts_array, edges_array)
# returns a new line as object named newLine

def create_PolyLine(name, verts, edges):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.show_name = True
    # Link object to scene
    bpy.context.scene.objects.link(ob)
    me.from_pydata(verts, edges, [])
 
    # Update mesh with new data
    me.update(calc_edges=True)
    return ob



# ================================================================================================
# higher functions
# ================================================================================================

def create_vertsFromObjects(newMesh_name, objects):
    
    if len(objects) > 0:
        # get location array of selection
        locations = get_objectLocation(objects)
        # create new Mesh
        create_Vertices(newMesh_name, locations)
        return True, len(locations)
    else:
        return False
        

# ------------------------------------------------------------------------------------------------
# create edge from empties
# ------------------------------------------------------------------------------------------------

def create_edgeFrom2Objects(objects):
    
    if len(objects) == 2:
        
        # get a name for the edge
        part1 = objects[0].name
        part2 = objects[1].name
        edge_name = part1 + part2 + "_connection"
        
        # get the location of the objects
        verts = get_objectLocation(objects)
        
        # known connections
        edges = [(0,1)]
        create_PolyLine(edge_name, verts, edges)
        return edge_name
    else:
        return False


# ------------------------------------------------------------------------------------------------
# create pointcloud from objects
# ------------------------------------------------------------------------------------------------

def create_PointCloud(objects):
    
    if len(objects) > 0:
        pointcloud_name = get_objectNameWithoutNumbers(objects[0].name) + '_pointcloud'
        create_vertsFromObjects(pointcloud_name, objects)
        return pointcloud_name
        
    else:
        return False


# ------------------------------------------------------------------------------------------------
# create a empty in the center of vertex selection 
# ------------------------------------------------------------------------------------------------
    
def createEmptyFromSelectedVertsInCenter():
    
    # maybe to simple?
    # could be extended to check selection            
    mainObj = bpy.context.active_object.name
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.add(type='EMPTY')
    ob = bpy.context.object
    ob.name = mainObj + '_empty'
    bpy.ops.view3d.snap_selected_to_cursor()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = bpy.data.objects[mainObj] 
    bpy.ops.object.mode_set(mode='EDIT')


# ------------------------------------------------------------------------------------------------
# create empty by vertex selection
# ressource: http://blenderscripting.blogspot.de/2011/07/place-empty-while-in-edit-mode.html
# ------------------------------------------------------------------------------------------------

def createEmptiesFromSelectedVerts():
    
    # get the object 
    activeObj = bpy.context.active_object
    
    # set to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # get the selected verts
    verts = [i.index for i in activeObj.data.vertices if i.select]
    
    # counter
    empty_counter = 0

    for i in verts:
        # get local coordinate
        vert_coordinate = activeObj.data.vertices[i].co
        vert_coordinate = activeObj.matrix_world * vert_coordinate
        
        # unselect all
        for item in bpy.context.selectable_objects:
            item.select = False
        
        # add the empty    
        bpy.ops.object.add(type='EMPTY', location=vert_coordinate)
        newEmpty = bpy.context.active_object
        newEmpty.location = vert_coordinate
        newEmpty.empty_draw_size = newEmpty.empty_draw_size # / 4
        bpy.ops.object.select_all(action='TOGGLE')
        bpy.ops.object.select_all(action='DESELECT')
        empty_counter += 1

    # set object to original state
    bpy.context.scene.objects.active = activeObj
    activeObj.select = True
    bpy.ops.object.mode_set(mode='EDIT')

    return empty_counter

# ------------------------------------------------------------------------------------------------
# validate the ascii file
# ------------------------------------------------------------------------------------------------

def asciiData_validation(filepath):

    columnsLenght = []
    data = []

    try:
        f = open(filepath, 'r')
        for line in f:
            if not line.strip():
                continue
            else:
                line = line.strip()
                columns = line.split()
                if not line.startswith('#'):
                    columnsLenght.append(len(columns))
                    data.append(line)
        f.close()

        if max(columnsLenght) == min(columnsLenght):
            return max(columnsLenght), data
        
        else:
            return False

    except:
        return False


# ------------------------------------------------------------------------------------------------
# read the ascii data
# needs improvements to get dynamic data!
# ------------------------------------------------------------------------------------------------

def read_ascii_file(filepath, startline):
    
    xValues = []
    yValues = []
    zValues = []
    
    validation = asciiData_validation(filepath)
    
    if (validation != False):

        columnsLenght = asciiData_validation(filepath)[0]
        data = asciiData_validation(filepath)[1][startline-1:]

        try:
            for line in data:
                line = line.strip()
                columns = line.split()

                if (columnsLenght == 3):
                    xValues.append(float(columns[0]))
                    yValues.append(float(columns[1]))
                    zValues.append(float(columns[2]))
                elif (columnsLenght == 2):
                    xValues.append(float(columns[0]))
                    yValues.append(float(columns[1]))
                    zValues.append(0)
                elif (columnsLenght == 1):
                    xValues.append(float(columns[0]))
                    yValues.append(0)
                    zValues.append(0)
                else:
                    return False
        except:
            return False

        return columnsLenght, xValues, yValues, zValues
    
    else:
        return False


# ------------------------------------------------------------------------------------------------
# multiply XYZ data
# ------------------------------------------------------------------------------------------------

def multiplyXYZ(xValues, yValues, zValues, multiplyValue):
    
    finalX_Values = []
    finalY_Values = []
    finalZ_Values = []
    
    for i in xValues:
        finalX_Values.append(i*multiplyValue)

    for i in yValues:
        finalY_Values.append(i*multiplyValue)

    for i in zValues:
        finalZ_Values.append(i*multiplyValue)

    return [list(t) for t in zip(finalX_Values, finalY_Values, finalZ_Values)]


# ------------------------------------------------------------------------------------------------
# multiply one dimensional list
# ------------------------------------------------------------------------------------------------

def multiplyList(values, multiplyValue):
    
    finalValues = []
    
    for i in values:
        finalValues.append(i*multiplyValue)

    return finalValues


# ------------------------------------------------------------------------------------------------
# add to data
# ------------------------------------------------------------------------------------------------

def addToXYZ(xValues, yValues, zValues, addValue):
    
    finalX_Values = []
    finalY_Values = []
    finalZ_Values = []
    
    for i in xValues:
        finalX_Values.append(i + addValue)

    for i in yValues:
        finalY_Values.append(i + addValue)

    for i in zValues:
        finalZ_Values.append(i + addValue)

    return [list(t) for t in zip(finalX_Values, finalY_Values, finalZ_Values)]


# ------------------------------------------------------------------------------------------------
# add one dimensional list
# ------------------------------------------------------------------------------------------------

def addList(values, addValue):
    
    finalValues = []
    
    for i in values:
        finalValues.append(i*multiplyValue)

    return finalValues


# ------------------------------------------------------------------------------------------------
# angle to euler
# ------------------------------------------------------------------------------------------------

def anglesToEuler(xValues, yValues, zValues):
    
    finalX_Values = []
    finalY_Values = []
    finalZ_Values = []
    factor = (pi/180)
    
    for i in xValues:
        finalX_Values.append(i*factor)

    for i in yValues:
        finalY_Values.append(i*factor)

    for i in zValues:
        finalZ_Values.append(i*factor)

    return [list(t) for t in zip(finalX_Values, finalY_Values, finalZ_Values)]




# ================================================================================================
#    GUI
# ================================================================================================

# ------------------------------------------------------------------------
#    store vfxtoolbox properties in the active scene
# ------------------------------------------------------------------------

class VfxToolboxSettings(PropertyGroup):

    # http://blender.stackexchange.com/questions/10910/dynamic-enumproperty-by-type-of-selection
    def filter_object_type_callback(scene, context):

        items = [
            ('LOC', "Location", ""),
            ('ROT', "Rotation", ""),
            ('SCL', "Scale", ""),
        ]

        # get selection
        selection = bpy.context.selected_objects

        # get selection type list
        selection_types = get_objectTypeList(selection)

        if len(selection_types) == 1:

            # check for lamps
            if selection_types[0] == 'LAMP':
                items.append(('NRG', "Energy", ""))
                items.append(('CLR', "Color", ""))
            
            # check for cameras
            if selection_types[0] == 'CAMERA':
                items.append(('FCD', "Focus Distance", ""))
                items.append(('FCL', "Focal Length", ""))

        return items

    # set size of selected empties
    EmptySizeProperty_ = FloatProperty(
        name = "Empty Size", 
        description = "Size of empties.",
        default = 1.00,
        min = 0.01,
        max = 100)
    
    # select all empties
    AllOrInSelectionProperty_ = BoolProperty(
        name = "All Empties in Scene", 
        description = "Select all Empties in Scene.",
        default = False)
    
    # search value
    SearchForObjectsProperty_ = StringProperty(
        name = "",
        description = "Search string.",
        default = "Name_")
    
    # rename value
    RenameObjectsProperty_ = StringProperty(
        name = "",
        description = "Rename string with sequence numbers.",
        default = "Name_###")

    # path to ascii file
    AsciiImportPathProperty_ = StringProperty(
        name="",
        description="Path to Ascii File",
        default="", 
        maxlen=1024,
        subtype='FILE_PATH')

    # apply values to LOC ROT SCL
    AsciiTransformationProperty_ = EnumProperty(
        name="Apply Data to:",
        description="Apply Data to attribute.",
        items=(('LOC', "Location", ""),
               ('ROT', "Rotation", ""),
               ('SCL', "Scale", "")),
        default='LOC',
        )

    AsciiObjectProperties_ = EnumProperty(
        items=filter_object_type_callback,
        name="Apply Data to:",
        description="Filter addons by category",
        )


# ------------------------------------------------------------------------
#    gui helper
# ------------------------------------------------------------------------

# Helper function to get user input
def get_Prop(key, scn):
    try:
        val = scn[key]
    except:
        val = 'Undefined'
    return val

# Helper function to get user float input
def get_floatProp(key, scn):
    try:
        val = scn[key]
    except:
        val = 1.00
    return val

# Helper function to print user input
def printProp(label, key, scn):
    try:
        val = scn[key]
    except:
        val = 'Undefined'
    print("%s %s" % (key, val))


# ------------------------------------------------------------------------
#    vfxtoolbox in editmode
# ------------------------------------------------------------------------

class VfxToolbox_panel_editMode(Panel):
    bl_idname = "VfxToolbox_panel_editMode"
    bl_label = "vfx toolbox"
    bl_category = "VFX"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vfxToolbox = scene.vfxToolbox
        
        row = layout.row()
        row.label("Reconstruction:")
        col = layout.column(align=True)
        col.operator("vfxtoolbox.create_empties_fromverts", icon="EDIT") 
        col.operator("vfxtoolbox.create_empty_fromverts_center", icon="EDGESEL")

        
# ------------------------------------------------------------------------
#   create empties from selected verts button
# ------------------------------------------------------------------------
 
class CreateEmptyFromVerts(bpy.types.Operator):
    bl_idname = "vfxtoolbox.create_empties_fromverts"
    bl_label = "Empties from Vertices"
    bl_description = "Creates empties from selected vertices."
    def execute(self, context):
        empties = createEmptiesFromSelectedVerts()
        self.report({'INFO'}, str(empties) + ' Empties created.')
        return {'FINISHED'}


# ------------------------------------------------------------------------
#   create empty in center from selected vert button
# ------------------------------------------------------------------------
 
class CreateEmptyFromVertsCenter(bpy.types.Operator):
    bl_idname = "vfxtoolbox.create_empty_fromverts_center"
    bl_label = "Empty in Center of Selection"
    bl_description = "Creates an empty in the center of the selected vertices."
    
    def execute(self, context):
        createEmptyFromSelectedVertsInCenter()
        self.report({'INFO'}, 'Empty created.')
        return {'FINISHED'}


# ------------------------------------------------------------------------
#    vfxtoolbox in objectmode
# ------------------------------------------------------------------------

class VfxToolbox_panel_objectMode(Panel):
    bl_idname = "VfxToolbox_panel_objectMode"
    bl_label = "vfx toolbox"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "VFX"
    
    @classmethod
    def poll(self,context):
        #scene = context.scene
        return context.active_object is not None
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        vfxToolbox = scene.vfxToolbox

        row = layout.row()
        col = layout.column(align=True)
        col.operator("vfxtoolbox.freeze_selected_objects", icon="RESTRICT_SELECT_ON")
        col.operator("vfxtoolbox.defreeze_all_objects", icon="RESTRICT_SELECT_OFF")
        
        row = layout.row()
        row.label("Scene Building:")
        col = layout.column(align=True)
        col.operator("vfxtoolbox.group_selected_objects", icon="CONSTRAINT")
        col.operator("vfxtoolbox.group_release_children", icon="UNLINKED")
        col.operator("vfxtoolbox.group_select_children", icon="GROUP")

        row = layout.row()
        row.label("Seek & Destroy:")
        col = layout.column(align=True)
        col.prop(vfxToolbox, 'SearchForObjectsProperty_')
        col.operator("vfxtoolbox.find_objects", icon="BORDERMOVE")
        col.prop(vfxToolbox, 'RenameObjectsProperty_')
        col.operator("vfxtoolbox.rename_selected_objects", icon="DRIVER")
        
        row = layout.row()
        #row.label("Scene Setup:")
        col = layout.column(align=True)
        col.operator("vfxtoolbox.select_cameras_and_empties", icon="CAMERA_DATA")
        col.operator("vfxtoolbox.all_empties_in_scene", icon="EMPTY_DATA")
        col.operator("vfxtoolbox.all_empties_in_selection", icon="BORDER_LASSO")

        #layout.separator()

        row = layout.row()
        row.label("Reconstruction:")
        col = layout.column(align=True)
        col.operator("vfxtoolbox.empty_connect", icon="OUTLINER_OB_EMPTY")
        col.operator("vfxtoolbox.empty_pointcloud", icon="STICKY_UVS_DISABLE")
        
        row = layout.row()
        row.label("Empty Appearance:")
        col = layout.column(align=True)
        col.prop(vfxToolbox, 'EmptySizeProperty_', icon='BLENDER', toggle=True)
        col.operator("vfxtoolbox.set_empty_size", icon="SORTSIZE")
        
        #rowsub = col.row(align=True)
        #rowsub.prop(vfxToolbox, 'EmptySizeProperty_', icon='BLENDER', toggle=True)
        #rowsub.operator("vfxtoolbox.set_empty_size", icon="SORTSIZE")

        rowsub = col.row(align=True)
        rowsub.operator("vfxtoolbox.empty_appearance", text="Plain", icon='EMPTY_DATA').number=1
        rowsub.operator("vfxtoolbox.empty_appearance", text="Sphere", icon='MESH_UVSPHERE').number=2
        
        rowsub = col.row(align=True)
        rowsub.operator("vfxtoolbox.empty_appearance", text="Circle", icon='MESH_CIRCLE').number=3
        rowsub.operator("vfxtoolbox.empty_appearance", text="Cube", icon='MESH_CUBE').number=4
        rowsub.operator("vfxtoolbox.empty_appearance", text="Image", icon='IMAGE_ALPHA').number=5
        
        #layout.separator()

        row = layout.row()
        row.label("Animation from Ascii File:")
        col = layout.column(align=True)
        col.prop(vfxToolbox, "AsciiImportPathProperty_")
        rowsub = col.row(align=True)
        rowsub.prop(vfxToolbox, "AsciiObjectProperties_", text="")
        rowsub.operator("vfxtoolbox.import_ascii", icon='IPO')
        col.operator("vfxtoolbox.apply_asciigeo", icon="IPO" )
        
        layout.separator()


# ------------------------------------------------------------------------
#    apply ascii to selection
# ------------------------------------------------------------------------    

class ApplyAsciiToSelectionButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.apply_asciigeo"
    bl_label = "Apply to Selection"
    bl_description = "Apply ascii data to selection."

    startAtLine = bpy.props.IntProperty(
        name = "Start at line:",
        description = "Starting point to read to file.",
        default=1 )

    xColumn = bpy.props.IntProperty(
        name = "X Column:",
        description = "Set the X coloumn.",
        default = 1,
        min = 1,
        max = 3 )

    yColumn = bpy.props.IntProperty(
        name = "Y Column:",
        description = "Set the Y coloumn.",
        default = 2,
        min = 1,
        max = 3 )

    zColumn = bpy.props.IntProperty(
        name="Z Column:",
        description = "Set the Z coloumn.",
        default = 3,
        min = 1,
        max = 3 )

    timelineStart = bpy.props.IntProperty(
        name="Timeline starting point:",
        description = "Offset in timeline.",
        default=1 )

    timelineIncrement = bpy.props.IntProperty(
        name="Offset keys:",
        description = "Insert keframe with an offset.",
        default=1 )


    mult = bpy.props.FloatProperty(
        name = "Multiply values by:", 
        description = "Multiply the values.",
        default = 1.00,
        min = 0.01,
        max = 1000 )

    add = bpy.props.FloatProperty(
        name = "Add values by:", 
        description = "Add X to the values.",
        default = 0 )
    
    def oneDimensionalPropType(self, property_input):
        simple_array = ['NRG', 'FCD', 'FCL']
        
        if property_input in simple_array:
            return True
        else:
            return False
    
    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, width=330)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        vfxToolbox = scene.vfxToolbox
        
        # get dialog values
        mult_value = self.properties.mult
        add_value = self.properties.add
        timelineStart_value = self.properties.timelineStart
        timelineIncrement_value = self.properties.timelineIncrement
        startAtLine_value = self.properties.startAtLine
        xColumn_value = self.properties.xColumn
        yColumn_value = self.properties.yColumn
        zColumn_value = self.properties.zColumn
        
        # get property values
        prop = vfxToolbox.AsciiObjectProperties_
        pathToAscii = get_Prop('AsciiImportPathProperty_', vfxToolbox)

        # get selection
        selection = get_AllObjectsInSelection()
        if len(selection) > 0:
            
            # check if path is given
            if pathToAscii != 'Undefined':
             
                # read the file
                filedata = read_ascii_file(pathToAscii, startAtLine_value)
                if filedata != False:

                    for item in selection:

                        # set start frame and offset
                        frame_num = timelineStart_value
                        offset = timelineIncrement_value

                        # object data
                        ob = bpy.data.objects[item.name]
                        ob_type = get_objectType(item.name)
                        
                        # for Location, Rotation, Scale and Color are 3 Values needed
                        # thatswhy check for "multi dimensional prop type"
                        #   1.1   1.2    1.3
                        #   0.9   1.1    1.3
                        #   ...   ...    ...
                        if self.oneDimensionalPropType(prop) == False:
                            
                            # get data
                            xyz = [list(t) for t in zip(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value])]
                            if add_value != 0: # check for additon
                                xyz = addToXYZ(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value], add_value)
                            if mult_value != 1: # check for multiply
                                xyz = multiplyXYZ(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value], mult_value)

                            # insert location keyframes
                            if prop == 'LOC':
                                for i in xyz:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.location = i
                                    ob.keyframe_insert(data_path="location", index=-1)
                                    frame_num += offset
                                
                                self.report({'INFO'}, 'Added Location Animation.')

                            # insert rotation keyframes
                            elif prop == 'ROT':
                                """ TODO: check values are euler or not """
                                # convert values to Euler
                                xyz = anglesToEuler(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value])
                                for i in xyz:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.rotation_euler = i
                                    ob.keyframe_insert(data_path="rotation_euler", index=-1)
                                    frame_num += offset

                                self.report({'INFO'}, 'Added Rotation Animation.')
                        
                            # insert scale keyframes
                            elif prop == 'SCL':
                                for i in xyz:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.scale = i
                                    ob.keyframe_insert(data_path="scale", index=-1)
                                    frame_num += offset

                                self.report({'INFO'}, 'Added Scale Animation.')

                            # insert color keyframes
                            elif prop == 'CLR' and ob_type == 'LAMP':
                                
                                ob = bpy.data.lamps[item.name]
                                for i in xyz:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.color = i
                                    ob.keyframe_insert(data_path="color", index=-1)
                                    frame_num += offset
                            
                                self.report({'INFO'}, 'Added Color Animation.')


                        else: # else is one dimensional prop type

                            x = filedata[xColumn_value]

                            # check for additon
                            if add_value != 0:
                                x = addList(x, add_value)

                            # check for multiply
                            if mult_value != 1:
                                x = multiplyList(x, add_value)
                            
                            # insert energy keyframes
                            if prop == 'NRG' and ob_type == 'LAMP':
                                ob = bpy.data.lamps[item.name]
                                for i in x:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.energy = i
                                    ob.keyframe_insert(data_path="energy", index=-1)
                                    frame_num += offset

                                self.report({'INFO'}, 'Added Energy Animation.')

                            # insert dof distance keyframes
                            elif prop == 'FCD' and ob_type == 'CAMERA':
                                ob = bpy.data.cameras[item.name]
                                for i in x:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.dof_distance = i
                                    ob.keyframe_insert(data_path="dof_distance", index=-1)
                                    frame_num += offset
                                
                                self.report({'INFO'}, 'Added DOF Distance Animation.')


                            elif prop == 'FCL' and ob_type == 'CAMERA':
                                ob = bpy.data.cameras[item.name]
                                for i in x:
                                    bpy.context.scene.frame_set(frame_num)
                                    ob.lens = i
                                    ob.keyframe_insert(data_path="lens", index=-1)
                                    frame_num += offset
                                
                                self.report({'INFO'}, 'Added Focal Animation.')

                else:
                    self.report({'INFO'}, 'Error creating object. Data not readable.')
            else:
                self.report({'INFO'}, 'No file selected.')
        else:
            self.report({'INFO'}, 'Nothing selected.')
        
        return{'FINISHED'}


# ------------------------------------------------------------------------
#   import ascii data
# ------------------------------------------------------------------------
 
class ImportAsciiButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.import_ascii"
    bl_label = "Build Empty"
    bl_description = "Creates an empty from the file data."
    
    name = bpy.props.StringProperty(
        name="Name of empty:",
        description = "The name of the object.",
        default="custom animation")

    startAtLine = bpy.props.IntProperty(
        name = "Start at line:",
        description = "Starting point to read to file.",
        default=1 )

    xColumn = bpy.props.IntProperty(
        name = "X Column:",
        description = "Set the X coloumn.",
        default = 1,
        min = 1,
        max = 3 )

    yColumn = bpy.props.IntProperty(
        name = "Y Column:",
        description = "Set the Y coloumn.",
        default = 2,
        min = 1,
        max = 3 )

    zColumn = bpy.props.IntProperty(
        name="Z Column:",
        description = "Set the Z coloumn.",
        default = 3,
        min = 1,
        max = 3 )

    timelineStart = bpy.props.IntProperty(
        name="Timeline starting point:",
        description = "Offset in timeline.",
        default=1 )

    timelineIncrement = bpy.props.IntProperty(
        name="Offset keys:",
        description = "Insert keframe with an offset.",
        default=1 )


    mult = bpy.props.FloatProperty(
        name = "Multiply values by:", 
        description = "Multiply the values.",
        default = 1.00,
        min = 0.01,
        max = 1000 )

    add = bpy.props.FloatProperty(
        name = "Add values by:", 
        description = "Add X to the values.",
        default = 0 )


    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, width=330)
        return {'RUNNING_MODAL'}  


    def execute(self, context):
        scene = context.scene
        vfxToolbox = scene.vfxToolbox
        #prop = vfxToolbox.AsciiTransformationProperty_
        prop = vfxToolbox.AsciiObjectProperties_
        name_value = self.properties.name
        mult_value = self.properties.mult
        add_value = self.properties.add
        timelineStart_value = self.properties.timelineStart
        timelineIncrement_value = self.properties.timelineIncrement
        startAtLine_value = self.properties.startAtLine
        xColumn_value = self.properties.xColumn
        yColumn_value = self.properties.yColumn
        zColumn_value = self.properties.zColumn

        #print (vfxToolbox.AsciiImportPathProperty_)
        if (get_Prop('AsciiImportPathProperty_', vfxToolbox) != 'Undefined'):
         
            # read the file
            filedata = read_ascii_file(get_Prop('AsciiImportPathProperty_', vfxToolbox), startAtLine_value)

            # if there is data
            if filedata != False:

                # create empty
                start_pos = (0,0,0)
                bpy.ops.object.add(type='EMPTY', location=start_pos) 
                ob = bpy.context.active_object
                ob.empty_draw_size = ob.empty_draw_size * 4
                ob.name = name_value
                
                # set start frame and offset
                frame_num = timelineStart_value
                offset = timelineIncrement_value

                # get all values #xyz = [list(t) for t in zip(filedata[1], filedata[2], filedata[3])]
                xyz = [list(t) for t in zip(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value])]
                if mult_value != 1: # check for multiply
                    xyz = multiplyXYZ(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value],  mult_value)
                if add_value != 0: # check for additon
                    xyz = addToXYZ(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value],  add_value)

                # insert location keyframes
                if prop == 'LOC':
                    for i in xyz:
                        bpy.context.scene.frame_set(frame_num)
                        ob.location = i
                        ob.keyframe_insert(data_path="location", index=-1)
                        frame_num += offset

                    self.report({'INFO'}, 'Added Location Animation.')

                # insert rotation keyframes
                if prop == 'ROT':
                    xyz = anglesToEuler(filedata[xColumn_value], filedata[yColumn_value], filedata[zColumn_value])
                    for i in xyz:
                        bpy.context.scene.frame_set(frame_num)
                        ob.rotation_euler = i
                        ob.keyframe_insert(data_path="rotation_euler", index=-1)
                        frame_num += offset

                    self.report({'INFO'}, 'Added Rotation Animation.')
                
                # insert scale keyframes
                if prop == 'SCL':
                    for i in xyz:
                        bpy.context.scene.frame_set(frame_num)
                        ob.scale = i
                        ob.keyframe_insert(data_path="scale", index=-1)
                        frame_num += offset

                    self.report({'INFO'}, 'Added Scale Animation.')
                
                
                else: # if nothing matches insert location keyframes
                    for i in xyz:
                        bpy.context.scene.frame_set(frame_num)
                        ob.location = i
                        ob.keyframe_insert(data_path="location", index=-1)
                        frame_num += offset

                    self.report({'INFO'}, 'Added Location Animation.')

                
                self.report({'INFO'}, 'Object created.')   

            else:
                self.report({'INFO'}, 'Error creating object. Data not readable.')
        else:
            self.report({'INFO'}, 'No file selected.')
                     
        return{'FINISHED'}


# ------------------------------------------------------------------------
#    set empty size button
# ------------------------------------------------------------------------
 
class SetEmptySizeButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.set_empty_size"
    bl_label = "Update Size"
    bl_description = "Sets the size of empties in selection." 
    
    def execute(self, context):
        scene = context.scene
        vfxToolbox = scene.vfxToolbox
        
        """ NOT IN USE """
        # if 'all empties in scene' is enabled
        if (vfxToolbox.AllOrInSelectionProperty_) == True:
            # get all empties in scene
            selection = get_allObjectsInSceneByType('EMPTY')
            
            # set size           
            set_emptySize(selection, vfxToolbox.EmptySizeProperty_)
            
            # output result 
            if len(selection) > 1:
                # output result
                self.report({'INFO'}, (str(len(selection)) + ' empties set to: ' +  str(vfxToolbox.EmptySizeProperty_)))
            else:
                self.report({'INFO'}, (str(len(selection)) + ' empty set to: ' +  str(vfxToolbox.EmptySizeProperty_)))
        
        # if 'all empties in scene' is disabled
        else:            
            # get empties in selection
            selection = get_ObjectsInSelectionByType('EMPTY')
            
            if len(selection) > 0:
                # set size
                set_emptySize(selection, vfxToolbox.EmptySizeProperty_)

                if len(selection) > 1:
                    # output result
                    self.report({'INFO'}, (str(len(selection)) + ' empties set to: ' +  str(vfxToolbox.EmptySizeProperty_)[:4]))
                else:
                    self.report({'INFO'}, (str(len(selection)) + ' empty set to: ' +  str(vfxToolbox.EmptySizeProperty_)[:4]))

            #----------------------------------------------------------------------------------- 
            else:
                self.report({'INFO'}, 'Nothing selected.')
                  
        return{'FINISHED'}
 

# ------------------------------------------------------------------------
#   select multiple objects button
# ------------------------------------------------------------------------
 
class FindAndSelectObjectsButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.find_objects"
    bl_label = "Find Object Sequence"
    bl_description = "Selects all objects in the scene by the given search string."
    
    def execute(self, context):
        scene = context.scene
        vfxToolbox = scene.vfxToolbox
        
        if (vfxToolbox.SearchForObjectsProperty_ != 'Undefined'):
            bpy.ops.object.select_all(action='DESELECT')
            selection = get_allObjectsBySearchString(vfxToolbox.SearchForObjectsProperty_)
            n = len(selection)
            
            if n > 0:
                get_highlightObjects(selection)
                self.report({'INFO'}, "%d Object%s selected." % (n, "s"[n==1:]))
            else:
                self.report({'INFO'}, 'Nothing found.')
            
        else:
            self.report({'INFO'}, 'Nothing found.')
                          
        return{'FINISHED'}
 

# ------------------------------------------------------------------------
#   rename multi selection button
# ------------------------------------------------------------------------
 
class RenameSelectionButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.rename_selected_objects"
    bl_label = "Rename Selection"
    bl_description = "Renames selection as sequence."
    
    def execute(self, context):
        scene = context.scene
        vfxToolbox = scene.vfxToolbox

        if (vfxToolbox.RenameObjectsProperty_ != 'Undefined'):        
            selection = get_AllObjectsInSelection()
            if len(selection) > 1 :
                rename_objectsByNewName(selection, vfxToolbox.RenameObjectsProperty_)
                self.report({'INFO'}, 'Objects renamed to ' + vfxToolbox.RenameObjectsProperty_ + '.')
            else:
                self.report({'INFO'}, 'More than 1 object have to be selected.')

        else: 
            self.report({'INFO'}, 'Nothing found.')

        return{'FINISHED'}


# ------------------------------------------------------------------------
#    group objects button
# ------------------------------------------------------------------------

class GroupSelectionButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.group_selected_objects"
    bl_label = "Add Parent"
    bl_description = "Creates a parent for the selection."
   
    def execute(self, context):
        selection = get_AllObjectsInSelection()
        if len(selection) > 0:
            bpy.ops.view3d.snap_cursor_to_selected()
        
            bpy.ops.object.add(type='EMPTY')
        
            bpy.ops.view3d.snap_selected_to_cursor()
            newEmpty = bpy.context.active_object
        
            selection.append(newEmpty)
            get_highlightObjects(selection)  
            bpy.ops.object.parent_set(type='OBJECT')    
        
            get_hideSelectObjects(selection[0:len(selection)-1])

            self.report({'INFO'}, 'Parent created.')

        else:
            self.report({'INFO'}, 'Nothing selected.')

        return{'FINISHED'}


# ------------------------------------------------------------------------
#    release group button
# ------------------------------------------------------------------------

class GroupReleaseMembersButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.group_release_children"
    bl_label = "Clear Parent"
    bl_description = "Releases all children and apply transformations."
   
    def execute(self, context):
        selection = get_AllObjectsInSelection()

        # check selection length
        if len(selection) > 0:
            
            for n in selection:
                objectName = n.name     # get the name
                childList = n.children  # get the childlist

                # check for children
                if len(childList) > 0:
                    for i in childList:
                        subObjectName = i.name
                        hidden = bpy.data.objects[subObjectName].hide_select
                        
                        # check for not selectable objects
                        if (hidden == True):
                            bpy.data.objects[subObjectName].hide_select = False
                        
                        # select the subobject                            
                        bpy.data.objects[subObjectName].select = True

                        # clear the parent with keeping transformations
                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                
                    self.report({'INFO'}, 'Children released.')

                else:
                    self.report({'INFO'}, 'No children.')
            
        else:
            self.report({'INFO'}, 'Nothing selected.')

        return{'FINISHED'}

# ------------------------------------------------------------------------
#    select childs button
# ------------------------------------------------------------------------

class GroupSelectMembersButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.group_select_children"
    bl_label = "Select Children"
    bl_description = "Selects all children of a parent and make them selectable if not."
   
    def execute(self, context):
        selection = get_AllObjectsInSelection()

        # check selection length
        if len(selection) > 0:
            
            for n in selection:
                objectName = n.name     # get the name
                childList = n.children  # get the childlist

                # check for children
                if len(childList) > 0:
                    
                    # set parent to not active
                    bpy.data.objects[objectName].select = False

                    for i in childList:
                        subObjectName = i.name
                        hidden = bpy.data.objects[subObjectName].hide_select
                        
                        # check for not selectable objects
                        if (hidden == True):
                            bpy.data.objects[subObjectName].hide_select = False
                        
                        # select the subobject                            
                        bpy.data.objects[subObjectName].select = True
                
                    self.report({'INFO'}, 'Children selected.')

                else:
                    self.report({'INFO'}, 'No children.')
            
        else:
            self.report({'INFO'}, 'Nothing selected.')

        return{'FINISHED'}


# ------------------------------------------------------------------------
#    freeze selection button
# ------------------------------------------------------------------------   

class FreezeObjectsButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.freeze_selected_objects"
    bl_label = "Freeze Selection"
    bl_description = "Disables the viewport selection of current objects."
   
    def execute(self, context):
        selection = get_AllObjectsInSelection()
        n = len(selection)
        if n > 0:
            get_hideSelectObjects(selection)
            self.report({'INFO'}, "%d Object%s frozen." % (n, "s"[n==1:]))
        else:
            self.report({'INFO'}, 'Nothing selected.')
        return{'FINISHED'} 


# ------------------------------------------------------------------------
#    unfreeze all button
# ------------------------------------------------------------------------ 

class UnfreezeButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.defreeze_all_objects"
    bl_label = "Unfreeze All"
    bl_description = "Enables viewport selection of all objects in scene."
   
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        selection = get_AllObjectsInScene()
        n = len(selection)

        if n > 0:
            freezed_array = get_dehideSelectObjects(selection)
            get_highlightObjects(freezed_array)
            self.report({'INFO'}, "%d Object%s released." % (n, "s"[n==1:]))
        else:
            self.report({'INFO'}, 'Nothing selected.')
        
        return{'FINISHED'} 


# ------------------------------------------------------------------------
#    get empties and camera button
# ------------------------------------------------------------------------ 

class SelectEmptiesAndCamerasButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.select_cameras_and_empties"
    bl_label = "Select Cameras & Empties"
    bl_description = "Selects all cameras and empties."
   
    def execute(self, context):
        # get all empties function
        bpy.ops.object.select_all(action='DESELECT')
        selection_empties = get_allObjectsInSceneByType('EMPTY')
        selction_cams = get_allObjectsInSceneByType('CAMERA')
        count_empties = len(selection_empties)
        count_cams = len(selction_cams)
        n = count_empties + count_cams
        
        if n > 0:
            #highlight all objects
            get_highlightObjects(selection_empties)
            get_highlightObjects(selction_cams)
            self.report({'INFO'}, "%d Object%s selected." % (n, "s"[n==1:]))

        else:
            self.report({'INFO'}, 'Nothing found.')

        return{'FINISHED'} 


# ------------------------------------------------------------------------
#    get all empties in scene button
# ------------------------------------------------------------------------

class SelectAllEmptiesInSceneButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.all_empties_in_scene"
    bl_label = "Select Empties in Scene"
    bl_description = "Selects all empties in scene."
   
    def execute(self, context):
        
        # get all empties function
        bpy.ops.object.select_all(action='DESELECT')
        selection = get_allObjectsInSceneByType('EMPTY')
        n = len(selection)

        if n > 0:
            #highlight all objects
            get_highlightObjects(selection)
            self.report({'INFO'}, "%d Object%s selected." % (n, "s"[n==1:]))

        else:
            self.report({'INFO'}, 'No empty in scene.')

        return{'FINISHED'}    

 
# ------------------------------------------------------------------------
#    get all empties in selection button
# ------------------------------------------------------------------------  
 
class SelectAllEmptiesInSelectionButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.all_empties_in_selection"
    bl_label = "Find Empties in Selection"
    bl_description = "Selects all empties in selection."
 
    def execute(self, context):
        
        # get all empties in selecton function
        selection = get_ObjectsInSelectionByType('EMPTY')
        n = len(selection)
        
        if n > 0:
            # deselect all
            bpy.ops.object.select_all(action='DESELECT')
            
            #highlight all objects
            get_highlightObjects(selection)

            #print info
            self.report({'INFO'}, "%d Object%s selected." % (n, "s"[n==1:]))

        else:
            self.report({'INFO'}, 'No empty in selection.')
        
        return{'FINISHED'}  


# ------------------------------------------------------------------------
#    axes buttons 
# ------------------------------------------------------------------------
 
class EmptyAppearanceButtons(bpy.types.Operator):
    bl_idname = "vfxtoolbox.empty_appearance"
    bl_label = "Button"
    bl_description = "Changes appearance of selected empties."

    number = bpy.props.IntProperty()
    row = bpy.props.IntProperty()
    loc = bpy.props.StringProperty()
 
    def execute(self, context):
        scene = context.scene
        vfxToolbox = scene.vfxToolbox
        
        if self.loc:
            words = self.loc.split()
            self.row = int(words[0])
            self.number = int(words[1])
        
        # helper for setting typenumber
        def get_formatByNumber(button_number_int):
            return ['NONE','PLAIN_AXES','SPHERE','CIRCLE','CUBE','IMAGE'][button_number_int]  

        
        """ NOT IN USE """
        if (vfxToolbox.AllOrInSelectionProperty_) == True:
            
            # get all empties function
            selection = get_allObjectsInSceneByType('EMPTY')
            
            # format empties
            set_emptyType(selection, get_formatByNumber(self.number))
            
        else:
            selection = get_ObjectsInSelectionByType('EMPTY')
            if len(selection) > 0:
                set_emptyType(selection, get_formatByNumber(self.number))
                
            else:
                self.report({'INFO'}, 'Nothing selected.')        
        
        return{'FINISHED'} 


# ------------------------------------------------------------------------
#    connect two empties button
# ------------------------------------------------------------------------

class ConnecttwoEmptiesButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.empty_connect"
    bl_label = "Connect 2 Empties"
    bl_description = "Connects 2 selected empties."
 
    def execute(self, context):
        
        selection = get_ObjectsInSelectionByType('EMPTY')
        if len(selection) == 2:
            newLine_name_string = create_edgeFrom2Objects(selection)
            
            # select the new line
            # newLine_name_string = blender_namingLimitation(newLine_name_string)
            bpy.ops.object.select_pattern(pattern=newLine_name_string)
            
            # deselect all
            bpy.ops.object.select_all(action='DESELECT')

            # hightlight it!
            bpy.data.objects[newLine_name_string].select = True
            self.report({'INFO'}, 'Geometry built.')
        else:
            self.report({'INFO'}, '2 Empties have to be selected.')
        return{'FINISHED'}


# ------------------------------------------------------------------------
#    poincloud button
# ------------------------------------------------------------------------   

class EmptiesToPointcloudButton(bpy.types.Operator):
    bl_idname = "vfxtoolbox.empty_pointcloud"
    bl_label = "Pointcloud from Empties"
    bl_description = "Creates a pointcloud by the positions of the selected empties."
 
    def execute(self, context):

        selection = get_ObjectsInSelectionByType('EMPTY')
        
        if len(selection) > 0:
            newpointcloud_name_string = create_PointCloud(selection)
        
            # deselect all
            bpy.ops.object.select_all(action='DESELECT')
        
            # select the pointclud
            #newpointcloud_name_string = blender_namingLimitation(newpointcloud_name_string)
            bpy.ops.object.select_pattern(pattern=newpointcloud_name_string)
            
            # hightlight it!
            selectPointCloud = get_objectByName(newpointcloud_name_string)
            make_objectActive(selectPointCloud)

            self.report({'INFO'}, 'Pointcloud created.') 
            
        else:
            self.report({'INFO'}, 'No empty in selection.')

        return{'FINISHED'}
    

# ------------------------------------------------------------------------
# register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.vfxToolbox = PointerProperty(type=VfxToolboxSettings)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.vfxToolbox
    
if __name__ == "__main__":
    register()
