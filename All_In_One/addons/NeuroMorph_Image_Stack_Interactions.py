#    NeuroMorph_Image_Stack_Interactions.py (C) 2016,  Biagio Nigro, Anne Jorstad, Tom Boissonnet
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

bl_info = {  
    "name": "NeuroMorph Image Stack Interactions",
    "author": "Biagio Nigro, Anne Jorstad, Tom Boissonnet",
    "version": (1, 3, 0),
    "blender": (2, 7, 6),
    "location": "View3D > Object Image Superposition",
    "description": "Superimposes image files over 3D objects interactively",
    "warning": "",  
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Neuro_tool/visualization",  
    "tracker_url": "",  
    "category": "Learnbgame"
}  
  
import bpy
from bpy.props import *
from bpy.app.handlers import persistent
from mathutils import Vector  
import mathutils
import math
import os
import sys
import re
from os import listdir

# Define the panel
class SuperimposePanel(bpy.types.Panel):
    bl_label = "Image Stack Interactions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):
        self.layout.label("--Display Images from Stack--")

        self.layout.label("Image Stack Dimensions (microns):")
        row = self.layout.row()
        row.prop(context.scene , "x_side")
        row.prop(context.scene , "y_side")
        row.prop(context.scene , "z_side")

        row = self.layout.row(align=True)
        row.prop(context.scene, "image_path_X")
        row.operator("importfolder_x.tif", text='', icon='FILESEL')

        row = self.layout.row(align=True)
        row.prop(context.scene, "image_path_Y")
        row.operator("importfolder_y.tif", text='', icon='FILESEL')

        row = self.layout.row(align=True)
        row.prop(context.scene, "image_path_Z")
        row.operator("importfolder_z.tif", text='', icon='FILESEL')
        
        split = self.layout.row().split(percentage=0.6)  # percentage=0.53
        colL = split.column()
        colR = split.column()
        colR.operator("object.clear_images", text='Clear Images')

        row = self.layout.row()
        row.operator("superimpose.tif", text='Show Images at Vertex')

        split = self.layout.row().split(percentage=0.6)
        col1 = split.column()
        col1.operator("object.modal_operator", text='Scroll Through Image Stack')
        col2 = split.column().row()
        col2.prop(context.scene , "shift_step")

        row = self.layout.row()
        row.prop(context.scene , "render_images")

        self.layout.label("--Retrieve Object from Image--")

        split = self.layout.row().split(percentage=0.33)
        col1 = split.column()
        col1.operator("object.point_operator", text='Display Grid')
        col2 = split.column().row()
        col2.prop(context.scene , "x_grid") 
        col2.prop(context.scene , "y_grid") 
        col2.prop(context.scene , "z_grid")
        
        row = self.layout.row()
        row.operator("object.pickup_operator", text='Display Object at Selected Vertex')
        
        row = self.layout.row()
        row.operator("object.show_names", text='Show Names')
        row.operator("object.hide_names", text='Hide Names')
        
        self.layout.label("--Mesh Transparency--") 
        row = self.layout.row()
        row.operator("object.add_transparency", text='Add Transparency')
        row.operator("object.rem_transparency", text='Remove Transpanrency')
        row = self.layout.row()
        if bpy.context.object is not None:
          mat=bpy.context.object.active_material
          if mat is not None:
             row.prop(mat, "alpha", slider=True)
             row.prop(mat, "diffuse_color", text="")



class ClearImages(bpy.types.Operator):
    """Clear all images in memory (necessary if new image folder contains same names as previous folder)"""
    bl_idname = "object.clear_images"
    bl_label = "Clear all images in memory (necessary if new image folder contains same names as previous folder)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        im_ob_list = [ob for ob in bpy.context.scene.objects if ob.name == "Image"]
        if len(im_ob_list) > 0:  # delete it
            for im_ob in im_ob_list:
                bpy.context.scene.objects.active = im_ob
                im_ob.select = True
                bpy.ops.object.delete()

            # Activate an object so other functions have appropriate modes
            ob_0 = [ob_0 for ob_0 in bpy.data.objects if ob_0.type == 'MESH' and ob_0.hide == False][0]
            bpy.context.scene.objects.active = ob_0
            ob_0.select = True

        for f in bpy.data.images:
            f.user_clear()
            bpy.data.images.remove(f)
        return {'FINISHED'}




def active_node_mat(mat):
    # TODO, 2.4x has a pipeline section, for 2.5 we need to communicate
    # which settings from node-materials are used
    if mat is not None:
        mat_node = mat.active_node_material
        if mat_node:
            return mat_node
        else:
            return mat
    return None            

class SelectStackFolderZ(bpy.types.Operator):  # adjusted
    """Select location of the Z stack images (original image stack)"""
    bl_idname = "importfolder_z.tif"
    bl_label = "Select folder of the Z stack images"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if bpy.context.scene.image_path_Z != self.directory:
            bpy.context.scene.image_path_Z = self.directory

            # load image filenames and extract file extension
            LoadImageFilenames('Z')
            if len(bpy.context.scene.imagefilepaths_z) < 1:
                self.report({'INFO'},"No image files found in selected directory")
            else:
                example_name = bpy.context.scene.imagefilepaths_z[0].name
                file_ext = os.path.splitext(example_name)[1]
                bpy.context.scene.image_ext_Z = file_ext
        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        self.exte_Z = bpy.context.scene.image_ext_Z
        return {"RUNNING_MODAL"}

class SelectStackFolderX(bpy.types.Operator):  # adjusted
    """Select location of the X stack images (optional)"""
    bl_idname = "importfolder_x.tif"
    bl_label = "Select folder of the X stack images"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if bpy.context.scene.image_path_X != self.directory:
            bpy.context.scene.image_path_X = self.directory

            # load image filenames and extract file extension
            LoadImageFilenames('X')
            if len(bpy.context.scene.imagefilepaths_x) < 1:
                self.report({'INFO'}, "No image files found in selected directory")
            else:
                example_name = bpy.context.scene.imagefilepaths_x[0].name
                file_ext = os.path.splitext(example_name)[1]
                bpy.context.scene.image_ext_X = file_ext
        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        self.exte_X = bpy.context.scene.image_ext_X
        return {"RUNNING_MODAL"}

class SelectStackFolderY(bpy.types.Operator):  # adjusted
    """Select location of the Y stack images (optional)"""
    bl_idname = "importfolder_y.tif"
    bl_label = "Select folder of the Y stack images"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if bpy.context.scene.image_path_Y != self.directory:
            bpy.context.scene.image_path_Y = self.directory

            # load image filenames and extract file extension
            LoadImageFilenames('Y')
            if len(bpy.context.scene.imagefilepaths_y) < 1:
                self.report({'INFO'}, "No image files found in selected directory")
            else:
                example_name = bpy.context.scene.imagefilepaths_y[0].name
                file_ext = os.path.splitext(example_name)[1]
                bpy.context.scene.image_ext_Y = file_ext
        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        self.exte_Y = bpy.context.scene.image_ext_Y
        return {"RUNNING_MODAL"}


def LoadImageFilenames(orientation) :
    """Load the images of the stack indicated by orientation (in 'Z','X','Y')"""
    image_file_extensions = ["png", "tif", "tiff", "bmp", "jpg", "jpeg", "tga"]  # can add others as needed
    if(orientation == 'Z'):
        imagefilepaths = bpy.context.scene.imagefilepaths_z
        file_min = bpy.context.scene.file_min_Z
        path = bpy.context.scene.image_path_Z
    elif (orientation == 'X'):
        imagefilepaths = bpy.context.scene.imagefilepaths_x
        file_min = bpy.context.scene.file_min_X
        path = bpy.context.scene.image_path_X
    elif (orientation == 'Y'):
        imagefilepaths = bpy.context.scene.imagefilepaths_y
        file_min = bpy.context.scene.file_min_Y
        path = bpy.context.scene.image_path_Y

    # get filenames at image_path, extract filenames of type (image extension with most elements) in correct order
    filenames = [f for f in listdir(path) if os.path.isfile(os.path.join(path, f))]
    grouped = {extension:[f for f in filenames
                    if os.path.splitext(f)[1].lower() == os.path.extsep+extension]
                    for extension in image_file_extensions}
    largest_group = max(grouped.values(), key=len)

    # sort only the filenames, then add the full path
    sorted_filenames = sort_nicely([f for f in largest_group])
    the_filepaths = [os.path.join(path, f) for f in sorted_filenames]

    imagefilepaths.clear()

    # insert into CollectionProperty
    for f in the_filepaths:
        imagefilepaths.add().name = f

    # store minimum image index
    min_im_name = sorted_filenames[0]
    id_string = re.search('([0-9]+)', min_im_name)  # only searches filename, not full path
    file_min = int(id_string.group())

    if(orientation == 'Z'):
        bpy.context.scene.file_min_Z = file_min
    elif (orientation == 'X'):
        bpy.context.scene.file_min_X = file_min
    elif (orientation == 'Y'):
        bpy.context.scene.file_min_Y = file_min

def sort_nicely( filenames ):
    # Sort the given list in the way that humans expect
    # eg 10 comes after 2, 010 comes after 10
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(filenames, key=alphanum_key)


class DisplayImageButton(bpy.types.Operator):  # adjusted
    """Display available image plane at selected vertex"""
    bl_idname = "superimpose.tif"
    bl_label = "Superimpose images"
    
    def execute(self, context):
        if bpy.context.mode == 'EDIT_MESH':
            Nz = len(bpy.context.scene.imagefilepaths_z)
            if Nz > 0:
                if (bpy.context.active_object.type=='MESH'):
                    DisplayImageFunction('Z')
                else:
                    self.report({'INFO'},"Select a vertex on a mesh object")
            else:
                self.report({'INFO'},"No image files found in the Z directory")
            Nx = len(bpy.context.scene.imagefilepaths_x)
            if Nx > 0:
                if (bpy.context.active_object.type == 'MESH'):
                    DisplayImageFunction('X')
                else:
                    self.report({'INFO'}, "Select a vertex on a mesh object")
            else:
                self.report({'INFO'},"No image files found in the X directory")
            Ny = len(bpy.context.scene.imagefilepaths_y)
            if Ny > 0:
                if (bpy.context.active_object.type == 'MESH'):
                    DisplayImageFunction('Y')
                else:
                    self.report({'INFO'}, "Select a vertex on a mesh object")
            else:
                self.report({'INFO'},"No image files found in the Y directory")
            if (Ny <= 0 and Nz <=0 and Nx <=0):
                self.report({'INFO'},"No image files found in the selected directories")
        return {'FINISHED'}
  
def DisplayImageFunction(orientation):
    """For the given orientation, it search for the closest image to the selected
    vertex. Then it display the image in the good orientation."""
    x_max = bpy.context.scene.x_side
    y_max = bpy.context.scene.y_side
    z_max = bpy.context.scene.z_side
    x_min = 0.0
    y_min = 0.0
    z_min = 0.0

    if(orientation == 'Z'):
        scale_here = max(x_max, y_max)  # image is loaded with max dimension = 1
        scale_vec = [scale_here, scale_here, scale_here]
        image_files = bpy.context.scene.imagefilepaths_z
        exte = bpy.context.scene.image_ext_Z
        N = len(image_files)
        delta = (z_max-z_min)/(N-1)
        locs = [delta*n for n in range(N)]  # the z locations of each image in space
        newName = "Image Z"
        #The rotation that we need to apply on the image.
        rotX = 3.141592653
        rotY = 0
        rotZ = 0
    elif (orientation == 'X'):
        scale_here = max(y_max, z_max)  # image is loaded with max dimension = 1
        scale_vec = [scale_here, scale_here, scale_here]
        image_files = bpy.context.scene.imagefilepaths_x
        exte = bpy.context.scene.image_ext_X
        N = len(image_files)
        delta = (x_max-x_min)/(N-1)
        locs = [delta*n for n in range(N)]  # the x locations of each image in space
        newName = "Image X"
        #The rotation that we need to apply on the image.
        rotX = 0
        rotY = -3.141592653/2
        rotZ = 3.141592653
    elif (orientation == 'Y'):
        scale_here = max(x_max, z_max)  # image is loaded with max dimension = 1
        scale_vec = [scale_here, scale_here, scale_here]
        image_files = bpy.context.scene.imagefilepaths_y
        exte = bpy.context.scene.image_ext_Y
        N = len(image_files)
        delta = (y_max-y_min)/(N-1)
        locs = [delta*n for n in range(N)]  # the y locations of each image in space
        newName = "Image Y"
        #The rotation that we need to apply on the image.
        rotX = -3.141592653/2
        rotY = 0
        rotZ = 0

    myob = bpy.context.active_object
    bpy.ops.object.mode_set(mode = 'OBJECT')

    all_obj = [item.name for item in bpy.data.objects]
    for object_name in all_obj:
       bpy.data.objects[object_name].select = False

    # remove previous empty objects
    candidate_list = [item.name for item in bpy.data.objects if item.name == newName]
    for object_name in candidate_list:
       bpy.data.objects[object_name].select = True
       delete_plane(bpy.data.objects[object_name])
    bpy.ops.object.delete()

    # collect selected verts
    selected_id = [i.index for i in myob.data.vertices if i.select]
    original_object = myob.name

    for v_index in selected_id:
       # get local coordinate, turn into word coordinate
       vert_coordinate = myob.data.vertices[v_index].co
       vert_coordinate = myob.matrix_world * vert_coordinate

       # unselect all
       for item in bpy.context.selectable_objects:
           item.select = False

       # this deals with adding the empty
       bpy.ops.object.empty_add(type='IMAGE', location=vert_coordinate, rotation=(rotX,rotY,rotZ))
       im_ob = bpy.context.active_object
       im_ob.name = newName
       im_ob.image_from_stack_interactions = True

       # find closest image slice to orientation-coord of vertex
       if(orientation == 'Z'):
            point = vert_coordinate[2]
       elif(orientation == 'X'):
            point = vert_coordinate[0]
       elif(orientation == 'Y'):
            point = vert_coordinate[1]
          
       min_dist = float('inf')
       for ii in range(len(locs)):
         if abs(locs[ii]-point) < min_dist:
             min_dist = abs(locs[ii]-point)
             ind = ii

       im_ob.scale = scale_vec
       coord = locs[ind]
       if(orientation == 'Z'):
            locX = 0
            locY = y_max
            locZ = coord
       elif(orientation == 'X'):
            locX = coord
            locY = y_max
            locZ = 0
       elif(orientation == 'Y'):
            locX = 0
            locY = coord
            locZ = z_max

       im_ob.location = (locX, locY, locZ)  # this is correct

       #Lock the translations in directions different form the orientation of 
       #the image.
       if(orientation == 'Z'):
            im_ob.lock_location[0] = True # x
            im_ob.lock_location[1] = True # y
       elif(orientation == 'X'):
            im_ob.lock_location[2] = True # z
            im_ob.lock_location[1] = True # y            
       elif(orientation == 'Y'):
            im_ob.lock_location[0] = True # x
            im_ob.lock_location[2] = True # z
            
       if (bpy.context.scene.render_images):
           create_plane(im_ob)

       bpy.ops.object.select_all(action='TOGGLE')
       bpy.ops.object.select_all(action='DESELECT')

    # set original object to active, selects it, place back into editmode
    bpy.context.scene.objects.active = myob
    myob.select = True
    bpy.ops.object.mode_set(mode = 'OBJECT')

def update_render_images(self, context):

    im_ob_list = [item for item in bpy.data.objects if (item.name =='Image Z' or item.name =='Image X' or item.name =='Image Y')]
    for im_ob in im_ob_list:
       if(bpy.context.scene.render_images):
            create_plane(im_ob)
       else :
            delete_plane(im_ob)   

def create_plane(im_ob):
    x_max = bpy.context.scene.x_side
    y_max = bpy.context.scene.y_side
    z_max = bpy.context.scene.z_side
    if("Image Z" in im_ob.name):
        orientation = 'Z'
        pl_dimensions = (x_max, y_max, 0)
        pl_location = (x_max/2, y_max/2, im_ob.location[2])
        pl_rotation = (3.141592, 0.0, 0.0)
        pl_name = 'Plane Z'
        mat_name = 'Mat Z'
        texture_name = 'Text Z'
    elif("Image X" in im_ob.name):
        orientation = 'X'
        pl_dimensions = (z_max, y_max, 0)
        pl_location = (im_ob.location[0], y_max/2, z_max/2)
        pl_rotation = (0.0, -3.141592/2, 3.141592653)
        pl_name = 'Plane X'
        mat_name = 'Mat X'
        texture_name = 'Text X'
    elif("Image Y" in im_ob.name):
        orientation = 'Y'
        pl_dimensions = (x_max, z_max, 0)
        pl_location = (x_max/2, im_ob.location[1], z_max/2)
        pl_rotation = (-3.141592/2, 0.0, 0.0)
        pl_name = 'Plane Y'
        mat_name = 'Mat Y'
        texture_name = 'Text Y'

    #Deselecting all object before creating the parent links
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_plane_add(location=pl_location, rotation=pl_rotation)
    pl_ob = bpy.context.active_object
    bpy.context.scene.objects.active = im_ob
    isImageVisible = im_ob.hide
    if (isImageVisible):
        #If the image is not displayed, the parent_set function fail
        im_ob.hide = False
    #pl_ob.parent = im_ob
    bpy.ops.object.parent_set(keep_transform=True, type='OBJECT')
    pl_ob.dimensions = pl_dimensions
    pl_ob.lock_location[0] = True # x
    pl_ob.lock_location[1] = True # y
    pl_ob.lock_location[2] = True # y
    pl_ob.name = pl_name
    pl_ob.hide = True
    pl_ob.select = False
    if (isImageVisible):
        im_ob.hide = True

    #Creating it's associated texture and material
    pl_ob.data.uv_textures.new()
    cTex = bpy.data.textures.new(texture_name, type = 'IMAGE')


    mat = bpy.data.materials.new(mat_name)
    mat.use_shadeless = True

    mtex = mat.texture_slots.add()
    mtex.texture = cTex
    mtex.texture_coords = 'UV'
    mtex.mapping = 'FLAT'
    pl_ob.data.materials.append(mat)
    
    
def delete_plane(im_ob):
    selected_ob = bpy.context.selected_objects

    bpy.ops.object.select_all(action='DESELECT')
    ob_hadPlane = False
    childs = im_ob.children
    for child in childs:
        if ('Plane ' in child.name):
            child.select = True
            child.hide = False
            ob_hadPlane = True
    bpy.ops.object.delete()

    if ob_hadPlane:
        if ('Image Z' in im_ob.name):
            mat = bpy.data.materials['Mat Z']
            text = bpy.data.textures['Text Z']
        elif ('Image X' in im_ob.name):
            mat = bpy.data.materials['Mat X']
            text = bpy.data.textures['Text X']
        elif ('Image Y' in im_ob.name):
            mat = bpy.data.materials['Mat Y']
            text = bpy.data.textures['Text Y']
        bpy.data.materials.remove(mat) 
        bpy.data.textures.remove(text)  

    for ob in selected_ob:
        ob.select = True

class ImageScrollOperator(bpy.types.Operator):
    """Scroll through image stack from selected image with mouse scroll wheel"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    def __init__(self):
        #print("Start")
        tmpvar=0  # needs something here to compile

    def __del__(self):
        #print("End")
        tmpvar=0  # needs something here to compile

    def modal(self, context, event):

     if bpy.context.mode == 'OBJECT':
       if (bpy.context.active_object.type=='EMPTY'):

            if not bpy.context.active_object.image_from_stack_interactions:
                self.report({'INFO'},"Image not created with this tool, use Image Stack Notation tools instead.")
                return {'FINISHED'}

            im_ob = bpy.context.active_object
            (ind, N, delta, orientation, image_files, locs) = getIndex(im_ob)

            movement = 1
            #If the user press shift, the movement is increased.
            if event.shift:
                movement = bpy.context.scene.shift_step
                if (movement <= 0):
                    movement = 1;

            #Images can be moved backward with the mouseWheelDown or the key -
            if event.type == 'WHEELDOWNMOUSE' or event.type == 'NUMPAD_MINUS':  # Apply
              if ind >= movement:
                 ind = ind - movement
                 moveImage(im_ob, -delta*movement, orientation)
                 #No need to call the load_im function because the handler will
                 # do it (see print_updated_objects()).
            #Images can be moved forward with the mouseWheelDown or the key +
            elif event.type == 'WHEELUPMOUSE' or event.type == 'NUMPAD_PLUS':  # Apply
               if ind < N-movement:
                 ind = ind + movement
                 moveImage(im_ob, delta*movement, orientation)

            elif event.type == 'LEFTMOUSE':  # Confirm
                return {'FINISHED'}
            elif event.type in ('RIGHTMOUSE', 'ESC'):  # Cancel
                return {'CANCELLED'}
            return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if bpy.ops.object.mode_set.poll():
          bpy.ops.object.mode_set(mode='OBJECT')
          if (bpy.context.active_object.type=='EMPTY'):
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
          else:
             return {'FINISHED'}

def moveImage(im_ob, delta, orientation):
    """The image is moved switch it's orientation"""
    if (orientation == 'Z'):
        im_ob.location.z = im_ob.location.z + delta
    elif (orientation == 'X'):
        im_ob.location.x = im_ob.location.x + delta
    elif (orientation == 'Y'):
        im_ob.location.y = im_ob.location.y + delta


def load_im(ind, image_files, im_ob, orientation):
# check if image already loaded, only load new image if not
    if (orientation == 'Z'):
        newid = ind+bpy.context.scene.file_min_Z
    elif (orientation == 'X'):
        newid = ind+bpy.context.scene.file_min_X
    elif (orientation == 'Y'):
        newid = ind+bpy.context.scene.file_min_Y
    full_path = image_files[newid].name
    filename_only = os.path.split(full_path)[1]
    if filename_only not in bpy.data.images:
        bpy.data.images.load(full_path)  # often produces TIFFReadDirectory: Warning, can ignore
    im_ob.data = bpy.data.images[filename_only]


def getIndex(im_ob):
    """Find the index of the image currently displayed, according to it's
    current position"""
    imageName = im_ob.name

    #This function also extract information here and return it, either the
    # several function that call it would do it several times.
    if (imageName == "Image Z"):
        directory = bpy.context.scene.image_path_Z
        exte = bpy.context.scene.image_ext_Z
        image_files = bpy.context.scene.imagefilepaths_z
        N = len(image_files)
        max=bpy.context.scene.z_side
        orientation = 'Z'
        point_location = im_ob.location.z
    elif (imageName == "Image X"):
        directory = bpy.context.scene.image_path_X
        exte = bpy.context.scene.image_ext_X
        image_files = bpy.context.scene.imagefilepaths_x
        N = len(image_files)
        max=bpy.context.scene.x_side
        orientation = 'X'
        point_location = im_ob.location.x
    elif (imageName == "Image Y"):
        directory = bpy.context.scene.image_path_Y
        exte = bpy.context.scene.image_ext_Y
        image_files = bpy.context.scene.imagefilepaths_y
        N = len(image_files)
        max=bpy.context.scene.y_side
        orientation = 'Y'
        point_location = im_ob.location.y
   
    min=0
    delta = (max-min)/(N - 1)
    locs = [delta*n for n in range(N)]        

    min_dist=float('inf')
    for ii in range(len(locs)):
       if abs(locs[ii]-point_location) < min_dist:
           min_dist = abs(locs[ii]-point_location)
           ind = ii 

    return (ind, N, delta, orientation, image_files, locs)


#A handler that call the function after each time the scene is updated.
# (add as handler in the register function)
@persistent
def print_updated_objects(scene):
    """Called when that the scene is updated. It look for the updated images and
    load the image corresponding to it's actual location."""
    for im_ob in scene.objects:
        # Search for the updated objects
        if im_ob.is_updated:
            # Only look at the images, we don't want to do anything on the objects
            if (im_ob.name in ["Image Z","Image X","Image Y"]):
                (ind, N, delta, orientation, image_files, locs) = getIndex(im_ob)
                load_im(ind, image_files, im_ob, orientation)
                if (im_ob.name == "Image Z"): 
                    im_ob.location.z = locs[ind]
                elif (im_ob.name == "Image X"):
                    im_ob.location.x = locs[ind]
                elif (im_ob.name == "Image Y"):
                    im_ob.location.y = locs[ind]



# (add as handler in the register function)
@persistent
def set_image_for_frame(scene):
    """Do the same thing as print_updated_objects, when rendering plane is
checked. Set also the texture of the planes.
    """
    if(bpy.context.scene.render_images):
        for im_ob in scene.objects:
            if (im_ob.name in ["Image Z","Image X","Image Y"]):
                (ind, N, delta, orientation, image_files, locs) = getIndex(im_ob)
                load_im(ind, image_files, im_ob, orientation)
                if (im_ob.name == "Image Z"): 
                    im_ob.location.z = locs[ind]
                elif (im_ob.name == "Image X"):
                    im_ob.location.x = locs[ind]
                elif (im_ob.name == "Image Y"):
                    im_ob.location.y = locs[ind]
                set_texture(im_ob)
                
#A handler to change light property when the script is loaded
def setLight(scene):
    bpy.context.scene.world.light_settings.use_environment_light = True
    #And we remove the handler just after we set the light on
    bpy.app.handlers.scene_update_post.remove(setLight)

# Same Handler that is called when a new blend file is loaded
@persistent
def setLightLoad(scene):
    bpy.context.scene.world.light_settings.use_environment_light = True

def set_texture(im_ob):
    for child in im_ob.children:
        if child.name == 'Plane Z':
            child.data.uv_textures[0].data[0].image = im_ob.data
            child.data.materials['Mat Z'].texture_slots['Text Z'].texture.image = im_ob.data
        elif child.name == 'Plane X':
            child.data.uv_textures[0].data[0].image = im_ob.data
            child.data.materials['Mat X'].texture_slots['Text X'].texture.image = im_ob.data
        elif child.name == 'Plane Y':
            child.data.uv_textures[0].data[0].image = im_ob.data
            child.data.materials['Mat Y'].texture_slots['Text Y'].texture.image = im_ob.data

class PointOperator(bpy.types.Operator):
    """Display grid on selected image for object point selection"""
    bl_idname = "object.point_operator"
    bl_label = "Choose Point Operator"
    
    def execute(self, context):
                      
     if bpy.context.mode == 'OBJECT': 
      if bpy.context.active_object is not None:  
             
        if (bpy.context.active_object.name=='Image Z'): 
            mt = bpy.context.active_object
            zlattice=mt.location.z
            x_off=bpy.context.scene.x_side
            y_off=bpy.context.scene.y_side
            xg=bpy.context.scene.x_grid
            yg=bpy.context.scene.y_grid
        elif (bpy.context.active_object.name=='Image X'):
            mt = bpy.context.active_object
            zlattice=mt.location.x
            x_off=bpy.context.scene.z_side
            y_off=bpy.context.scene.y_side
            xg=bpy.context.scene.z_grid
            yg=bpy.context.scene.y_grid
        elif (bpy.context.active_object.name=='Image Y'): 
            mt = bpy.context.active_object
            zlattice=mt.location.y
            x_off=bpy.context.scene.x_side
            y_off=bpy.context.scene.z_side
            xg=bpy.context.scene.x_grid
            yg=bpy.context.scene.z_grid
        else :
            return {"FINISHED"}
 
        tmpActiveObject = bpy.context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        #delete previous grids
        all_obj = [item.name for item in bpy.data.objects]
        for object_name in all_obj:
          if object_name[0:4]=='Grid':
            delThisObj(bpy.data.objects[object_name])

        bpy.context.scene.objects.active = tmpActiveObject  
          
        if (bpy.context.active_object.name=='Image Z'): 
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(0.0+x_off/2,0.0+y_off/2, zlattice-0.0001))
        elif (bpy.context.active_object.name=='Image X'):
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(zlattice-0.0001,0.0+y_off/2, 0.0+x_off/2), rotation=(0,3.141592/2,0)) 
        elif (bpy.context.active_object.name=='Image Y'): 
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(0.0+x_off/2, zlattice-0.0001, 0.0+y_off/2), rotation=(3.141592/2,0,0)) 
        
        grid = bpy.context.active_object
        grid.scale.x=x_off/2
        grid.scale.y=y_off/2
        grid.draw_type = 'WIRE'  # don't display opaque grey on the reverse side

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
          
     return {"FINISHED"}


class PickupOperator(bpy.types.Operator):
    """Display mesh objects at all selected grid vertices (will be visible in their respective layers)"""
    # this will only work if all objects are in the same layer
    bl_idname = "object.pickup_operator"
    bl_label = "Pick up object Operator"
    
    def execute(self, context):
     if bpy.context.mode == 'EDIT_MESH':   
       if bpy.context.active_object is not None:
         if bpy.context.active_object.name[0:4]=="Grid":
           bpy.ops.object.mode_set(mode = 'OBJECT') 
           grid=bpy.context.active_object 
           selected_idx = [i.index for i in grid.data.vertices if i.select]
           lidx=len(selected_idx)
           l=len(bpy.data.objects)

           if l>0 and lidx>0:  # loop over all selected vertices
             mindist=float('inf')

             for myob in bpy.data.objects:
               picked_obj_name=""   
               if myob.type=='MESH':
                  if myob.name[0:4]!='Grid':
                    for v_index in selected_idx:
                      #get local coordinate, turn into word coordinate
                      vert_coordinate = grid.data.vertices[v_index].co  
                      vert_coordinate = grid.matrix_world * vert_coordinate

                      dist=-1.0
                      if pointInBox(vert_coordinate, myob)==True:
                        dist=findMinDist(vert_coordinate, myob)
                        if dist==0:
                           mindist=dist
                           picked_obj_name=myob.name
                           showObj(picked_obj_name)
                        elif dist>0 and pointInsideMesh(vert_coordinate, myob)==True:
                           mindist=dist
                           picked_obj_name=myob.name
                           showObj(picked_obj_name)

           all_obj = [item.name for item in bpy.data.objects]
           for object_name in all_obj:
             bpy.data.objects[object_name].select = False  
             if object_name[0:4]=='Grid':
                delThisObj(bpy.data.objects[object_name])
             
     return {"FINISHED"}


class ShowNameButton(bpy.types.Operator):
    """Display names of selected objects in the scene"""
    bl_idname = "object.show_names"
    bl_label = "Show Object names"

    def execute(self, context):

        # If show_relationship_lines is not set to false, a blue line
        # from the location of the name object to the origin appears.
        # This line exists between every child object and parent object,
        # but most objects in scene have "location" of (0,0,0).
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].show_relationship_lines = False  # hide parent-child relationship line

        if bpy.context.mode == 'OBJECT': 
         if bpy.context.active_object is not None:      
          if (bpy.context.active_object.type=='MESH'):    
           
            mt = bpy.context.active_object
            child=mt.children
            center=centermass(mt)

            #add empty and make it child
            bpy.ops.object.add(type='EMPTY', location=center)
            emo = bpy.context.active_object
            emo.parent = mt
            #bpy.ops.object.constraint_add(type='CHILD_OF')  # for versions of Blender <= 2.66
            #emo.constraints['Child Of'].target = mt
            #bpy.ops.constraint.childof_set_inverse(constraint=emo.constraints['Child Of'].name, owner='OBJECT')
            emo.name=mt.name+" "
            emo.show_name=True
            emo.empty_draw_size = emo.empty_draw_size / 100

            mt.select=False
            emo.select=False
            stringtmp=""
           
            for obch in child:
               obch.select=True
               bpy.context.scene.objects.active = obch
               if (obch.type=='MESH'):
                  ind=obch.name.find("_")
                  if ind!=-1:
                    stringname=obch.name[0:ind]
                    if (stringname!=stringtmp):

                       center=centermass(obch)
                       bpy.ops.object.add(type='EMPTY', location=center)
                       em = bpy.context.active_object
                       em.parent = mt
                       #bpy.ops.object.constraint_add(type='CHILD_OF')  # for versions of Blender <= 2.66
                       #em.constraints['Child Of'].target = mt
                       #bpy.ops.constraint.childof_set_inverse(constraint=em.constraints['Child Of'].name, owner='OBJECT')
                       em.name=stringname+" "
                       em.show_name=True
                       em.empty_draw_size = emo.empty_draw_size / 100
                       obch.select=False
                       emo.select=False
                       stringtmp=stringname

        return {'FINISHED'}


class HideNameButton(bpy.types.Operator):
    """Hide names of selected objects in the scene"""
    bl_idname = "object.hide_names"
    bl_label = "Hide Object names"

    def execute(self, context):
        if bpy.context.mode == 'OBJECT': 
         if bpy.context.active_object is not None:  
          mt = bpy.context.active_object    
          if (mt.type=='MESH'):    
           
           child=mt.children
                      
           mt.select=False
                     
           for obch in child:
               if (obch.type=='EMPTY'): 
                 obch.select = True
                 bpy.context.scene.objects.active = obch
        
                 bpy.ops.object.delete() 
        return {'FINISHED'}


#calculate center of mass of a mesh 
def centermass(me):
  sum=mathutils.Vector((0,0,0))
  for v in me.data.vertices:
    sum =sum+ v.co
  center = (sum)/len(me.data.vertices)
  return center 

#control mesh visibility
def showObj(obname):
   if bpy.data.objects[obname].hide == True:
         bpy.data.objects[obname].hide = False
      

#check if a point falls within bounding box of a mesh
def pointInBox(point, obj):
    
    bound=obj.bound_box
    minx=float('inf')
    miny=float('inf')
    minz=float('inf')
    maxx=-1.0
    maxy=-1.0
    maxz=-1.0
    
    minx=min(bound[0][0], bound[1][0],bound[2][0],bound[3][0],bound[4][0],bound[5][0],bound[6][0],bound[6][0])
    miny=min(bound[0][1], bound[1][1],bound[2][1],bound[3][1],bound[4][1],bound[5][1],bound[6][1],bound[6][1])
    minz=min(bound[0][2], bound[1][2],bound[2][2],bound[3][2],bound[4][2],bound[5][2],bound[6][2],bound[6][2])
    
    maxx=max(bound[0][0], bound[1][0],bound[2][0],bound[3][0],bound[4][0],bound[5][0],bound[6][0],bound[6][0])
    maxy=max(bound[0][1], bound[1][1],bound[2][1],bound[3][1],bound[4][1],bound[5][1],bound[6][1],bound[6][1])
    maxz=max(bound[0][2], bound[1][2],bound[2][2],bound[3][2],bound[4][2],bound[5][2],bound[6][2],bound[6][2])
    
    if (point[0]>minx and point[0]<maxx and point[1]>miny and point[1]<maxy and point[2]>minz and point[2]<maxz):
       return True
    else: 
       return False
    
# calculate minimum distance among a point in space and mesh vertices    
def findMinDist(point, obj):
    idx = [i.index for i in obj.data.vertices]
    min_dist=float('inf') 
    for v_index in idx:
       vert_coordinate = obj.data.vertices[v_index].co  
       vert_coordinate = obj.matrix_world * vert_coordinate
       a=(point[0]-vert_coordinate[0])*(point[0]-vert_coordinate[0])
       b=(point[1]-vert_coordinate[1])*(point[1]-vert_coordinate[1])
       c=(point[2]-vert_coordinate[2])*(point[2]-vert_coordinate[2])
       dist=math.sqrt(a+b+c)
       if (dist<min_dist):
            min_dist=dist
    return min_dist


# check if point is surrounded by a mesh
def pointInsideMesh(point,ob):
    
    if "surf" in ob.name or "vol" in ob.name or "solid" in ob.name:  # don't display measurement objects
        return False

    # copy values of ob.layers
    layers_ob = []
    for l in range(len(ob.layers)):
        layers_ob.append(ob.layers[l])

    axes = [ mathutils.Vector((1,0,0)), mathutils.Vector((0,1,0)), mathutils.Vector((0,0,1)), mathutils.Vector((-1,0,0)), mathutils.Vector((0,-1,0)), mathutils.Vector((0,0,-1))  ]
    orig=point
    layers_all = [True for l in range(len(ob.layers))]
    ob.layers = layers_all  # temporarily assign ob to all layers, for ray_cast()

    this_visibility = ob.hide
    ob.hide = False
    bpy.context.scene.update()

    max_dist = 10000.0
    outside = False
    count = 0
    for axis in axes:  # send out rays, if cross this object in every direction, point is inside
        result,location,normal,index = ob.ray_cast(orig,orig+axis*max_dist)  # this will error if ob is in a different layer
        if index != -1:
            count = count+1

    ob.layers = layers_ob
    ob.hide = this_visibility

    bpy.context.scene.update()
    
    if count<6:
        return False
    else: 
        # turn on the layer(s) containing ob in the scene
        for l in range(len(bpy.context.scene.layers)):
            bpy.context.scene.layers[l] = bpy.context.scene.layers[l] or layers_ob[l]

        return  True
      

# delete object
def delThisObj(obj):
    bpy.data.objects[obj.name].select = True
    #bpy.ops.object.select_name(name=obj.name)
    bpy.context.scene.objects.active = obj
    bpy.ops.object.delete() 


def ShowBoundingBox(obname):
    bpy.data.objects[obname].show_bounds = True
    return


class AddTranspButton(bpy.types.Operator):
    """Define transparency of selected mesh object"""
    bl_idname = "object.add_transparency"
    bl_label = "Add Transparency"

    def execute(self, context):
      if bpy.context.mode == 'OBJECT':
       if (bpy.context.active_object is not None and  bpy.context.active_object.type=='MESH'):
           myob = bpy.context.active_object
           myob.show_transparent=True
           bpy.data.materials[:]
           if bpy.context.object.active_material:
             matact=bpy.context.object.active_material
             matact.use_transparency=True
             matact.transparency_method = 'Z_TRANSPARENCY'
             matact.alpha = 0.5
             #matact.diffuse_color = (0.8,0.8,0.8)
           else:
             matname=""
             for mater in bpy.data.materials[:]:
                if mater.name=="_mat_"+myob.name:
                   matname=mater.name
                   break
             if matname=="":
                mat = bpy.data.materials.new("_mat_"+myob.name)
             else:
                mat=bpy.data.materials[matname]
             mat.use_transparency=True
             mat.transparency_method = 'Z_TRANSPARENCY'
             mat.alpha = 0.5
             mat.diffuse_color = (0.8,0.8,0.8)
             context.object.active_material = mat

      return {'FINISHED'}


class RemTranspButton(bpy.types.Operator):
    """Remove transparency of selected mesh object"""
    bl_idname = "object.rem_transparency"
    bl_label = "Remove Transparency"

    def execute(self, context):
      if bpy.context.mode == 'OBJECT':
       if (bpy.context.active_object is not None and bpy.context.active_object.type=='MESH'):
           myob = bpy.context.active_object
           if bpy.context.object.active_material:
               matact=bpy.context.object.active_material
               if matact.name[0:5]=="_mat_":

                  matact.use_transparency=False
                  bpy.ops.object.material_slot_remove()
                  bpy.data.materials[:].remove(matact)
                  myob.show_transparent=False
               else:
                  matact.alpha = 1
                  matact.use_transparency=False
                  myob.show_transparent=False

      return {'FINISHED'}


##count number of files within a folder
#def countFiles(path, exte):  # not currently used
  #count=0
  #minim=2**31-1
  #dirs = os.listdir( path )
  #for item in dirs:
    #if os.path.isfile(os.path.join(path, item)):
       #if item[-4:] == exte:
         #count = count+1
         
         #if int(item[-7:-4]) < minim:
           #minim=int(item[-7:-4])
  #bpy.context.scene.file_min=minim
  #return count

#def extract_file_index( filename ):  # not currently used
    ## returns last numerical string of filename, eg 'text012text034.png' returns 34
    #file_id = int(re.findall('([0-9]+)', filename)[-1])



def register():
    bpy.utils.register_module(__name__)
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    kmi = km.keymap_items.new(ImageScrollOperator.bl_idname, 'Y', 'PRESS', ctrl=True) 

    bpy.app.handlers.scene_update_post.append(setLight)
    bpy.app.handlers.load_post.append(setLightLoad)
    bpy.app.handlers.frame_change_post.append(set_image_for_frame)
    bpy.app.handlers.scene_update_post.append(print_updated_objects)

    # Define properties
    bpy.types.Scene.x_side = bpy.props.FloatProperty \
          (
            name = "x",
            description = "x-dimension of image stack (microns)",
            default = 1
          )
    bpy.types.Scene.y_side = bpy.props.FloatProperty \
          (
            name = "y",
            description = "y-dimension of image stack (microns)",
            default = 1
          )
    bpy.types.Scene.z_side = bpy.props.FloatProperty \
          (
            name = "z",
            description = "z-dimension of image stack (microns)",
            default = 1
          )

    bpy.types.Scene.image_ext_Z = bpy.props.StringProperty \
          (
            name = "extZ",
            description = "Image Extension Z",
            default = ".tif"
          )

    bpy.types.Scene.image_ext_X = bpy.props.StringProperty \
            (
            name = "extX",
            description = "Image Extension X",
            default = ".tif"
        )

    bpy.types.Scene.image_ext_Y = bpy.props.StringProperty \
            (
            name="extY",
            description="Image Extension Y",
            default=".tif"
        )

    bpy.types.Scene.image_path_Z = bpy.props.StringProperty \
          (
            name = "Source_Z",
            description = "Location of images in the stack Z (XY-plane): use this when only one image stack",
            default = "/"
          )

    bpy.types.Scene.image_path_X = bpy.props.StringProperty \
            (
            name = "(Source_X)",
            description = "Location of images in the stack X (YZ-plane)",
            default = "/"
        )

    bpy.types.Scene.image_path_Y = bpy.props.StringProperty \
            (
            name="(Source_Y)",
            description="Location of images in the stack Y (XZ-plane)",
            default="/"
        )

    bpy.types.Scene.x_grid = bpy.props.IntProperty \
          (
            name = "nx",
            description = "Number of grid points in x",
            default = 50
          )

    bpy.types.Scene.y_grid = bpy.props.IntProperty \
          (
            name = "ny",
            description = "Number of grid points in y",
            default = 50
          )

    bpy.types.Scene.z_grid = bpy.props.IntProperty \
          (
            name = "nz",
            description = "Number of grid points in z",
            default = 50
          )

    bpy.types.Scene.file_min_Z = bpy.props.IntProperty \
          (
            name = "file_min_Z",
            description = "min Z file number",
            default = 0
          )
    bpy.types.Scene.file_min_X = bpy.props.IntProperty \
            (
            name = "file_min_X",
            description = "min X file number",
            default=0
        )
    bpy.types.Scene.file_min_Y = bpy.props.IntProperty \
            (
            name="file_min_Y",
            description="min Y file number",
            default=0
        )

    bpy.types.Scene.shift_step = bpy.props.IntProperty \
            (
            name="Shift step",
            description="Step size for scrolling through image stack while holding shift",
            default=10
        )
    
    bpy.types.Scene.render_images = bpy.props.BoolProperty \
            (
            name="Include images in render",
            description="Must be checked to have images rendered as visible textured planes in an animation",
            default=False,
            update=update_render_images
        )

    bpy.types.Scene.imagefilepaths_z = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.imagefilepaths_x = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.imagefilepaths_y = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    bpy.types.Object.image_from_stack_interactions = bpy.props.BoolProperty(name = "Image created from Stack Interactions tool", default=False)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.app.handlers.scene_update_post.remove(print_updated_objects)
    bpy.app.handlers.frame_change_post.remove(set_image_for_frame)
    bpy.app.handlers.load_post.remove(setLightLoad)

    del bpy.types.Scene.x_side
    del bpy.types.Scene.y_side
    del bpy.types.Scene.z_side
    del bpy.types.Scene.image_ext_X
    del bpy.types.Scene.image_ext_Y
    del bpy.types.Scene.image_ext_Z
    del bpy.types.Scene.image_path_X
    del bpy.types.Scene.image_path_Y
    del bpy.types.Scene.image_path_Z
    del bpy.types.Scene.x_grid
    del bpy.types.Scene.y_grid
    del bpy.types.Scene.z_grid
    del bpy.types.Scene.file_min_X
    del bpy.types.Scene.file_min_Y
    del bpy.types.Scene.file_min_Z
    del bpy.types.Scene.shift_step
    del bpy.types.Scene.render_images
    del bpy.types.Scene.imagefilepaths_x
    del bpy.types.Scene.imagefilepaths_y
    del bpy.types.Scene.imagefilepaths_z
    del bpy.types.Object.image_from_stack_interactions

if __name__ == "__main__":
    register()
    