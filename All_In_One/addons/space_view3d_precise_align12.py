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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Precise Align",
    "author": "Tjeerd Schouten",
    "version": (1,2),
    "blender": (2, 67, 0),
    "location": "View3D > Relations > Precise Align",
    "description": "Precisely align an object on all axis",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/Precise_Align",
    "tracker_url": "https://developer.blender.org/T31620",
    "category": "Learnbgame",
}

import bpy
import mathutils
from mathutils import Matrix, Vector
from math import radians, degrees

class ErrorMessage:
    none = ""
    edge_invalid = "Error: Select only one Edge, part of active Face"
    not_right_handed = "Error: Coordinate system is not Right Handed"
    two_axis_same = "Error: Two or three Axis are the same" 
 
class ErrorStorage:

    error_message = ""
    
    def SetError(self, error_message):
        self.error_message = error_message
    
    def GetError(self):        
        return self.error_message
        
errorStorage= ErrorStorage()


class EmptyOriginStorage:

    origin_index = 0
    
    def SwapOriginIndex(self, index):
    
        if index == 0:
            self.origin_index = 1
            
        if index == 1:
            self.origin_index = 2
            
        if index == 2:
            self.origin_index = 0

        return self.origin_index 
        
    def GetOriginIndex(self):

        return self.origin_index
            
        
emptyOriginStorage = EmptyOriginStorage()



def GetSourceEmpty(context):

    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        if amount_selected == 1:
    
            #Check whether the active object has an empty 
            name = "Empty." + context.active_object.name
            try:
                obj = bpy.data.objects[name]
            except KeyError:
                return False, bpy.ops.object
            else:        
                return True, obj
                
        if amount_selected > 1:
            return True, context.active_object
            
    else:
        return False, bpy.ops.object
    

def SetNewEmptyTransform(context):

    empty_origin_index = emptyOriginStorage.GetOriginIndex()
    matrix_valid, error_text, matrix = CreateFaceEdgeRotation(context, context.active_object, True, bpy.context.scene.normal_prop, bpy.context.scene.line_prop, bpy.context.scene.tangent_prop, empty_origin_index, bpy.context.scene.axis_normal_dropdown_prop, bpy.context.scene.axis_line_dropdown_prop, bpy.context.scene.axis_tangent_dropdown_prop)
    errorStorage.SetError(error_text)
    source_empty_valid, source_empty = GetSourceEmpty(context)    

    if (source_empty_valid is True) and ((matrix_valid is True) or (error_text == ErrorMessage.not_right_handed)):

        source_empty.matrix_world = matrix
        
        #Make parent?
        if bpy.context.scene.parent_prop is True:
            obj = context.active_object
            bpy.context.scene.objects.active = source_empty
            bpy.ops.object.parent_set(type='OBJECT')
            bpy.context.scene.objects.active = obj

        

def NormalPropertyChanged(self, context):    
    SetNewEmptyTransform(context)

def LinePropertyChanged(self, context):
    SetNewEmptyTransform(context)
    
def TangentPropertyChanged(self, context):
    SetNewEmptyTransform(context)
    
def LineVertexPropertyChanged(self, context):
    SetNewEmptyTransform(context)
    
def NormalDropdownPropertyChanged(self, context):
    SetNewEmptyTransform(context)
    
def LineDropdownPropertyChanged(self, context):
    SetNewEmptyTransform(context)
    
def TangentDropdownPropertyChanged(self, context):
    SetNewEmptyTransform(context)
    
def ParentPropertyChanged (self, context):

    empty_exists, source_empty = GetSourceEmpty(context)
    
    if empty_exists is True:
    
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if bpy.context.scene.parent_prop is True:

            obj = context.active_object
            obj.select = True
            source_empty.select = True 
            
            #Set the empty as a parent of the mesh
            bpy.context.scene.objects.active = source_empty
            bpy.ops.object.parent_set(type='OBJECT')
        
            #Set the mesh to active
            source_empty.select = False
            bpy.context.scene.objects.active = obj 

        else:            
            RemoveParent(context, source_empty)
           
        bpy.ops.object.mode_set(mode='EDIT')
            
            
def SizePropertyChanged (self, context):

    empty_exists, source_empty = GetSourceEmpty(context)

    if empty_exists is True:
        source_empty.empty_draw_size = bpy.context.scene.size_prop




class PreciseAlignUi(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Precise Align"
    bl_category = "Addons"
    bl_options = {"DEFAULT_CLOSED"}

    scnType = bpy.types.Scene
    
    scnType.normal_prop = bpy.props.BoolProperty(name="Normal", description = "Vector created by face normal", default = False, update = NormalPropertyChanged)
    scnType.line_prop = bpy.props.BoolProperty(name="Edge", description = "Vector created by face Edge", default = False, update = LinePropertyChanged)
    scnType.tangent_prop = bpy.props.BoolProperty(name="Tangent", description = "Vector automatically created by face normal and face edge", default = False, update = TangentPropertyChanged)

    axis = [  ( "x", "X", "Map to X axis" ), # return value, name, description
              ( "y", "Y", "Map to Y axis" ),
              ( "z", "Z", "Map to Z axis" )]
                   
    scnType.axis_normal_dropdown_prop = bpy.props.EnumProperty( name = "", items = axis, description = "Map to an axis", default='z', update = NormalDropdownPropertyChanged)
    #context.scene['axis_normal_dropdown_prop'] = 2
    scnType.axis_line_dropdown_prop = bpy.props.EnumProperty( name = "", items = axis, description = "Map to an axis", default='x', update = LineDropdownPropertyChanged )
    #context.scene['axis_line_dropdown_prop'] = 0
    scnType.axis_tangent_dropdown_prop = bpy.props.EnumProperty( name = "", items = axis, description = "Map to an axis", default='y', update = TangentDropdownPropertyChanged )
    #context.scene['axis_tangent_dropdown_prop'] = 1
    
    scnType.parent_prop = bpy.props.BoolProperty(name="Parent to Object", description = "Make the Empty the parent of the Object", default = True, update = ParentPropertyChanged )
    scnType.size_prop = bpy.props.FloatProperty(name = "Size", description = "Size of the empty", default = 1, min = 0.1, max = 10, update = SizePropertyChanged )


    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def draw(self, context):
    
        layout = self.layout
        obj = context.object
        scn = bpy.context.scene
        
        if obj and obj.mode == 'EDIT':
        
            empty_exists, source_empty = GetSourceEmpty(context)

            row = layout.row(align=True)
            row.alignment = 'LEFT'        
            row.label(text="Source Transform: ", icon='MANIPUL')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
                
            if empty_exists is True:
                row.label(source_empty.name, icon='OUTLINER_OB_EMPTY')

            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(text="Flip Vector:")
            row.label(text="Map Vector:")
  
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.prop(scn, "normal_prop") 
            row.prop(scn, "axis_normal_dropdown_prop")
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.prop(scn, "line_prop") 
            row.prop(scn, "axis_line_dropdown_prop")
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.prop(scn, "tangent_prop") 
            row.prop(scn, "axis_tangent_dropdown_prop")
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.swap_empty_origin",text="Swap Empty Origin", icon='MESH_DATA')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(errorStorage.GetError())
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.create_empty",text="Create Empty", icon='OUTLINER_OB_EMPTY')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.prop(scn, "parent_prop") 
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.prop(scn, "size_prop") 
           
            
        if obj and obj.mode == 'OBJECT':
        
#            errorStorage.SetError(ErrorMessage.none)
        
            empty_exists, source_empty = GetSourceEmpty(context)

            row = layout.row(align=True)
            row.alignment = 'LEFT'        
            row.label(text="Source Transform: ", icon='MANIPUL')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'

            amount_selected = len(bpy.context.selected_objects)
            
            if (empty_exists is True) and (amount_selected == 1):
                row.label(source_empty.name, icon='OUTLINER_OB_EMPTY')
                
            if (empty_exists is False) or (amount_selected > 1):
                try:
                    row.label(context.active_object.name, icon='OBJECT_DATA')
                except:
                    print("context.active_object.name doesn't exist")
                
            layout.separator()

            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(text="Align Local Transform:", icon='MANIPUL')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.align_local_transform_position",text="Position", icon='MAN_TRANS')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.align_local_transform_rotation",text="Rotation", icon='MAN_ROT')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.origin_to_3dcursor",text="Origin to 3D Cursor", icon='CURSOR')
            
         #   layout.separator()
			
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(errorStorage.GetError())
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(text="Align Object:", icon='OBJECT_DATA')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.align_object_position",text="Position", icon='MAN_TRANS')
            
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("object.align_object_rotation",text="Rotation", icon='MAN_ROT')
            

  
            
#Get the selected edge of the mesh. Only returns true if only one edge is selected
def GetValidEdge(face_vertices, edges):

    edge_select_amount = 0
    
    #output:
    edge_valid = False
    edge_vertices = []

    #Loop through all the edges in the mesh. This is not very efficient but 
    #total_edge_sel doesn't work and we can't get the active edge either.
    for i in edges:
    
        #Is the edge selected?
        if i.select:
        
            edge_select_amount += 1
            
            if edge_select_amount > 1:
                edge_valid = False
                return edge_valid, edge_vertices
        
            else:
                #Is the edge part of the face as well?
                if EdgePartOfFace(i.vertices, face_vertices) is True:
                
                    #Get the vertices connected to the edge and face
                    edge_vertices = i.vertices  
                    edge_valid = True
                    
    return edge_valid, edge_vertices


            
#Find out if the vertices of an edge are also part of the vertices of a face
def EdgePartOfFace(edge_vertices, face_vertices):

    for i in edge_vertices:
    
        #Is this edge vertex part of the face vertices as well?
        face_vertex_found = False
        for e in face_vertices:
        
            #The edge vertex is the same as the face vertex, so break
            #and try another edge vertex
            if i == e:
                face_vertex_found = True;
                break
                
        if face_vertex_found is False:
            #If we end up here, it means the current edge vertex is not
            #present in the face vertex array. If this is the case, the 
            #line is not part of the face.
            return False
            
    #If we end up here, all edge vertices are part of the face
    #vertices as well
    return True
    
    
#Remove the parent (put object in root)
def RemoveParent(context, obj):

    #Remove any parents. If an Object is a child of another object, the
    #Local Transform orientation settings will be messed up if it is changed
    active_obj = context.active_object
    bpy.context.scene.objects.active = obj
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.context.scene.objects.active = active_obj
    


    
#Set the origin of obj_to_be_changed to the origin of the destination Object
def SetLocalOrigin(context, obj_to_be_changed, destination):

    #Store the active object
    original_active_object = context.active_object 
    
    #Set the input object to active
    context.scene.objects.active = obj_to_be_changed

    # stores the previous location of the cursor
    cursor = bpy.context.scene.cursor_location[:]

    # set the 3D cursor to where you want the new origin to be
    bpy.context.scene.cursor_location = destination.location
    
    # set the active object's origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # reset the 3D cursor to its previous location
    bpy.context.scene.cursor_location = cursor
    
    #Restore the original active object
    context.scene.objects.active = original_active_object
    
    

#Rotates the local transform of the selected objects to the local transform of the active object
def SetLocalTransformRotation(context):

    context.space_data.use_pivot_point_align = False
    context.space_data.transform_orientation = 'LOCAL'
    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        empty_exists, source_empty = GetSourceEmpty(context)
  
        if amount_selected > 1:
        
            # bpy.ops.object.transform_apply works on all the selected objects, but we don't want that.
            #So deselect all first, and later reselect all again.
            original_selected_objects = bpy.context.selected_objects
            
            for i in bpy.context.selected_objects:
                i.select = False

            #Loop through all the objects which were previously selected 
            for i in original_selected_objects:

                #Only set the object if the current object is not the active object at the same time
                if context.active_object != i:
                
                    i.select = True
                    
                    i.rotation_mode = 'QUATERNION'
                    
                    #Store the start rotation of the selected object
                    rotation_before = i.matrix_world.to_quaternion()
                    
                    #Remove any parents. If an Object is a child of another object, the
                    #Local Transform orientation settings will be messed up
                    RemoveParent(context, i)

                    #Align the rotation of the selected object with the rotation of the active object
                    bpy.ops.transform.transform(mode='ALIGN')
                    
                    
                    #Store the rotation of the selected object after it has been rotated
                    rotation_after = i.matrix_world.to_quaternion()
                    
                    #Calculate the difference in rotation from before to after the rotation
                    rotation_difference = rotation_before.rotation_difference(rotation_after)

                    #Rotate the object the opposite way as done with the ALIGN function
                    i.rotation_quaternion = rotation_difference.inverted()
                    
                    
                    obj = context.active_object 
                    context.scene.objects.active = i
                    obj.select = False
                    
                   
                    #Align the local rotation of all the selected objects with the global world orientation 
                    bpy.ops.object.transform_apply(rotation = True)
                    
                    obj.select = True
                    context.scene.objects.active = obj
                    
                    #Set the roation of the selected object to the rotation of the active object
                    i.rotation_quaternion = context.active_object.matrix_world.to_quaternion()
                    
                    #Deselect again
                    i.select = False
                    
            #restore selected objects
            for i in original_selected_objects:
                i.select = True        

        if(amount_selected == 1) and (empty_exists == True) and IsMatrixRightHanded(source_empty.matrix_world):
        
            context.active_object.rotation_mode = 'QUATERNION' 
            
            #Store the start rotation of the selected object
            rotation_before = context.active_object.matrix_world.to_quaternion()
            
            RemoveParent(context, context.active_object)
   
            obj = context.active_object        
            source_empty.select = True 
            context.scene.objects.active = source_empty
            
            #Align the rotation of the selected object with the rotation of the active object
            bpy.ops.transform.transform(mode='ALIGN')
            
            #Set the Object to active
            source_empty.select = False
            context.scene.objects.active = obj 
            
            #Store the rotation of the selected object after it has been rotated
            rotation_after = context.active_object.matrix_world.to_quaternion()
            
            #Calculate the difference in rotation from before to after the rotation
            rotation_difference = rotation_before.rotation_difference(rotation_after)

            #Rotate the object the opposite way as done with the ALIGN function
            context.active_object.rotation_quaternion = rotation_difference.inverted()

            #Align the local rotation of the selected object with the global world orientation 
            bpy.ops.object.transform_apply(rotation = True)

            #Set the rotation of the selected object to the rotation of the active object
            context.active_object.rotation_quaternion = source_empty.matrix_world.to_quaternion()
            


    
        
#Positions the local transform of the selected objects to the local transform of the active object
def SetLocalTransformPosition(context):

    context.space_data.use_pivot_point_align = False
    context.space_data.transform_orientation = 'LOCAL'

    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
    
        empty_exists, source_empty = GetSourceEmpty(context)
    
        if (amount_selected > 1) and IsMatrixRightHanded(context.active_object.matrix_world):

            #Loop through all the selected objects 
            for i in bpy.context.selected_objects:

                #Only set the object if the current object is not the active object at the same time
                if context.active_object != i:

                    SetLocalOrigin(context, i, context.active_object)

        if(amount_selected == 1) and (empty_exists == True) and IsMatrixRightHanded(source_empty.matrix_world):
               
            SetLocalOrigin(context, context.active_object, source_empty)
                
#Align the selected object rotation with the active object
def AlignObjectRotation(context):

    context.space_data.use_pivot_point_align = False
    context.space_data.transform_orientation = 'LOCAL'

    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
            
        empty_exists, source_empty = GetSourceEmpty(context)
    
        if (amount_selected > 1) and IsMatrixRightHanded(context.active_object.matrix_world):
        
            #Loop through all the selected objects 
            for i in bpy.context.selected_objects:

                #Only set the object if the current object is not the active object at the same time
                if context.active_object != i:
                
                    RemoveParent(context, i)

                    #Align the rotation of the selected object with the rotation of the active object
                    bpy.ops.transform.transform(mode='ALIGN') 
        
        
#Align the selected object position with the active object
def AlignObjectPosition(context):

    context.space_data.use_pivot_point_align = False
    context.space_data.transform_orientation = 'LOCAL'

    amount_selected = len(bpy.context.selected_objects)
    
    if amount_selected >= 1:
            
        empty_exists, source_empty = GetSourceEmpty(context) 
 
        if (amount_selected > 1) and (IsMatrixRightHanded(context.active_object.matrix_world)):
        
            #Loop through all the selected objects 
            for i in bpy.context.selected_objects:

                #Only set the object if the current object is not the active object at the same time
                if context.active_object != i:

                    #Global position
                    i.matrix_world.translation = context.active_object.matrix_world.to_translation()

        
def IsMatrixRightHanded(mat):

    x = mat.col[0].to_3d()
    y = mat.col[1].to_3d()
    z = mat.col[2].to_3d()
    check_vector = x.cross(y)
    
    #If the coordinate system is right handed, the angle between z and check_vector
    #should be 0, but we will use 0.1 to take rounding errors into account
    angle = z.angle(check_vector)
    
    if angle <= 0.1:
        return True
    else:
        errorStorage.SetError(ErrorMessage.not_right_handed)
        return False

 
def CreateFaceEdgeRotation(context, obj, force_stay_editmode, flip_normal, flip_line, flip_tangent, empty_origin_index, map_normal, map_line, map_tangent):

    error_message = ErrorMessage.none
    vertex_select_amount = 0
    vertices= []
    
    #TODO: not sure about this mode changing weirdness
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')

    for i in context.active_object.data.vertices:    
        if i.select:        
        
            vertices.append(i)
            vertex_select_amount += 1

    mat = Matrix.Identity(4)

    if vertex_select_amount == 3:
    
        if empty_origin_index == 0:
        
            #Get the vertex coordinate from the index
            localCoord0 = vertices[0].co
            localCoord1 = vertices[1].co
            localCoord2 = vertices[2].co

        if empty_origin_index == 1:
            localCoord0 = vertices[1].co
            localCoord1 = vertices[2].co
            localCoord2 = vertices[0].co
            
        if empty_origin_index == 2:
            localCoord0 = vertices[2].co
            localCoord1 = vertices[0].co
            localCoord2 = vertices[1].co

        #Transform from local to global 
        globalCoord0 = obj.matrix_world * localCoord0
        globalCoord1 = obj.matrix_world * localCoord1
        globalCoord2 = obj.matrix_world * localCoord2
        
        vertex_position_origin = globalCoord0

        
        #Calculate the normal from 3 points
        line_vector = globalCoord1 - globalCoord0
        line_vector.normalize()
        line_vector1 = globalCoord2 - globalCoord0
        line_vector1.normalize()

        normal_vector = line_vector.cross(line_vector1)
        normal_vector.normalize()


        tangent_vector = normal_vector.cross(line_vector)
        tangent_vector.normalize()

        
        if flip_normal is True:
            normal_vector = normal_vector * -1
        
        if flip_line is True:
            line_vector = line_vector * -1

        if flip_tangent == True:
            tangent_vector = tangent_vector * -1
        
        if force_stay_editmode is False:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        #All the axis have to be different (we can't have x, x, z for example)
        if (map_normal != map_line) and (map_normal != map_tangent) and (map_line != map_tangent):
         
            #matrix order: x=0 y=1 z=2 position=3
            if map_line == 'x':
                mat.col[0] = line_vector.to_4d()
            if map_line == 'y':
                mat.col[1] = line_vector.to_4d()
            if map_line == 'z':
                mat.col[2] = line_vector.to_4d()
                
            if map_normal == 'x':
                mat.col[0] = normal_vector.to_4d()
            if map_normal == 'y':
                mat.col[1] = normal_vector.to_4d()
            if map_normal == 'z':
                mat.col[2] = normal_vector.to_4d()
                
            if map_tangent == 'x':
                mat.col[0] = tangent_vector.to_4d()
            if map_tangent == 'y':
                mat.col[1] = tangent_vector.to_4d()
            if map_tangent == 'z':
                mat.col[2] = tangent_vector.to_4d()

            mat.col[3] = vertex_position_origin.to_4d()
            
            #The coordinate system must be right handed
            if IsMatrixRightHanded(mat):
                return True, "", mat
                
            else:
                error_message = ErrorMessage.not_right_handed
                return False, error_message, mat

        else:
            #Invalid axis mapping, so stay in edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            error_message = ErrorMessage.two_axis_same
            return False, error_message, mat

    #No edge was selected, so stay in edit mode
    else:
        bpy.ops.object.mode_set(mode='EDIT')
        
        #Deselect all to work around the bug which causes an edge to appear
        #selected in the 3d view while it is not.
        bpy.ops.mesh.select_all(action = 'DESELECT')

        error_message = ErrorMessage.edge_invalid
        return False, error_message, mat


def CreateEmpty(context, matrix, parent, size):
        
    #Store the mesh object we are working with
    obj = context.active_object
    
    #Currently we are in edit mode, but if we want to add an object,
    #we have to be in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    #Add an empty and set it's properties
    bpy.ops.object.add(type='EMPTY')
    empty = context.object
    empty.empty_draw_type = 'ARROWS'
    empty.empty_draw_size = size
    empty.show_x_ray = True
    empty.name = "Empty." + obj.name
    
    #Set the rotation and translation of the empty
    empty.matrix_world = matrix

    #Select the mesh and set mode to edit again
    obj.select = True

    if parent is True:      
        #Set the empty as a parent of the mesh
        bpy.context.scene.objects.active = empty
        bpy.ops.object.parent_set(type='OBJECT')
    
    #Set the mesh to active
    bpy.context.scene.objects.active = obj 
        
    #Deselect the empty and go back to edit mode
    empty.select = False
    bpy.ops.object.mode_set(mode='EDIT')



class CreateEmptyOperator(bpy.types.Operator):

    bl_idname = "object.create_empty"
    bl_label = "Align Selected Rotation To Active"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
    
        empty_origin_index = emptyOriginStorage.GetOriginIndex()
        matrix_valid, error_text, matrix = CreateFaceEdgeRotation(context, context.active_object, False, bpy.context.scene.normal_prop, bpy.context.scene.line_prop, bpy.context.scene.tangent_prop, empty_origin_index, bpy.context.scene.axis_normal_dropdown_prop, bpy.context.scene.axis_line_dropdown_prop, bpy.context.scene.axis_tangent_dropdown_prop)
        errorStorage.SetError(error_text)
        
        if (matrix_valid is True) or (error_text == ErrorMessage.not_right_handed):

            CreateEmpty(context, matrix, bpy.context.scene.parent_prop, bpy.context.scene.size_prop)

        return {'FINISHED'}
        
        


class SetLocalTransformRotationOperator(bpy.types.Operator):
 
    bl_idname = "object.align_local_transform_rotation"
    bl_label = "Set Object transform rotation"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):

        SetLocalTransformRotation(context)

        return {'FINISHED'}
        
class SetLocalTransformPositionOperator(bpy.types.Operator):
 
    bl_idname = "object.align_local_transform_position"
    bl_label = "Set Object transform position"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):

        SetLocalTransformPosition(context)


        return {'FINISHED'}
        
        
class AlignObjectRotationOperator(bpy.types.Operator):
 
    bl_idname = "object.align_object_rotation"
    bl_label = "Align the Selected Object rotation with the Active Object"

    @classmethod
    def poll(cls, context):           
        return context.active_object != None

    def execute(self, context):

        AlignObjectRotation(context)

        return {'FINISHED'}
        
        
class AlignObjectPositionOperator(bpy.types.Operator):
 
    bl_idname = "object.align_object_position"
    bl_label = "Align the Selected Object postion with the Active Object"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):

        AlignObjectPosition(context)

        return {'FINISHED'}
        
        

class OriginTo3dCursorOperator(bpy.types.Operator):
 
    bl_idname = "object.origin_to_3dcursor"
    bl_label = "Set the Object origin to the 3D Cursor location"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):

        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        return {'FINISHED'}
        
        
        
class SwapEmptyOriginOperator(bpy.types.Operator):
 
    bl_idname = "object.swap_empty_origin"
    bl_label = "Swap the origin of the Empty"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):

        emptyOriginStorage.SwapOriginIndex(emptyOriginStorage.origin_index)
        SetNewEmptyTransform(context)
        
        return {'FINISHED'}
        
## registring
def register(): 
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":

    register()
    
