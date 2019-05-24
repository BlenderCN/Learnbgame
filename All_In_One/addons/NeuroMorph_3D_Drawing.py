#    NeuroMorph_3D_Drawing.py (C) 2018,  Anne Jorstad
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
    "name": "NeuroMorph 3D Drawing",
    "author": "Anne Jorstad, Tom Boissonnet",
    "version": (1, 1, 0),
    "blender": (2, 7, 9),
    "location": "View3D > 3D Drawing",
    "description": "Place markers on images and draw curves to construct surfaces in 3D",
    "warning": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Learnbgame",
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
import copy
import numpy as np  # must have Blender > 2.7
import bmesh  # for looptools
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
# from collections import Counter
from statistics import median
from bpy.types import Operator, Macro



# Define the panel
class StackNotationPanel(bpy.types.Panel):
    bl_label = "3D Drawing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):
        self.layout.label("---------- Display Images from Stack ----------")

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

        # split = self.layout.row().split(percentage=0.6)  # percentage=0.53
        # colL = split.column()
        # colR = split.column()
        # colR.operator("object.clear_images", text='Clear Images')

        split = self.layout.row().split(percentage=0.6)  # percentage=0.53
        colL = split.column()
        colR = split.column()
        colL.operator("superimpose.tif", text='Show Image(s) at Vertex', icon="TEXTURE")  # TEXTURE or IMAGE_DATA
        colR.prop(context.scene , "center_view")

        split = self.layout.row().split(percentage=0.6)
        col1 = split.column()
        col1.operator("object.modal_operator", text='Scroll Through Image Stack', icon="FULLSCREEN_ENTER")
        col2 = split.column().row()
        col2.prop(context.scene , "shift_step")

        row = self.layout.row()
        row.prop(context.scene , "render_images")


        # ----------------------------
        self.layout.label("---------- Mark Points on Image (Click) ----------")

        row = self.layout.row()
        row.prop(context.scene, 'marker_prefix')

        row = self.layout.row()
        row.operator("object.add_sphere", text='Add Marker', icon='MESH_UVSPHERE')

        row = self.layout.row()
        row.prop(context.scene , "coarse_marker")

        row = self.layout.row()
        row.prop(context.scene, "pt_radius")
        if hasattr(context.object, 'data') and context.object.data.name[0:6] == 'Sphere':
            row = self.layout.row()
            row.operator("mesh.update_marker_radius", text = "Update Marker Radius")

        
        # ----------------------------
        self.layout.label("---------- Mark Region on Image (Draw) ----------")

        row = self.layout.row()
        row.prop(context.scene, 'surface_prefix')

        split = self.layout.row().split(percentage=0.6)
        colL = split.column()
        colR = split.column()
        colL.operator("object.draw_curve", text='Draw Object Outline', icon='GREASEPENCIL')
        colR.operator("object.erase_curve", text='Erase', icon="PANEL_CLOSE")
        
        split = self.layout.row().split(percentage=0.6)
        colL = split.column()
        colR = split.column()
        colL.prop(context.scene , "convert_curve_on_release")
        colR.operator("object.convert_curve", text='Use This Curve', icon="OUTLINER_OB_CURVE")

        split = self.layout.row().split(percentage=0.6)
        colL = split.column()
        colR = split.column()
        colL.prop(context.scene, "scene_precision")
        colR.prop(context.scene , "closed_curve")

        row = self.layout.row()
        row.operator("mesh.curves2object", text='Construct Mesh Surface from Curves', icon="OUTLINER_OB_SURFACE")

        split = self.layout.row().split(percentage=0.6)
        colL = split.column()
        colR = split.column()
        colR.operator("object.close_tube", text='Close Open Tube', icon="MESH_CYLINDER")

        # self.layout.label("--For Debugging--")
        # row = self.layout.row()
        # row.operator("object.line_of_best_fit", text='Create Line of Best Fit')
        # row = self.layout.row()
        # row.operator("object.add_sphere_pt0", text='Add sphere at index 0 of this object')
        # # row = self.layout.row()
        # # row.operator("scene.detect_grease_pencil", text='Detect GP mouse release?')


        # ----------------------------
        self.layout.label("---------- Mesh Transparency ---------- ")
        row = self.layout.row()
        row.operator("object.add_transparency", text='Add Transparency')
        row.operator("object.rem_transparency", text='Remove Transpanrency')
        row = self.layout.row()
        if bpy.context.object is not None:
            mat=bpy.context.object.active_material
            if mat is not None:
                row.prop(mat, "alpha", slider=True)
                row.prop(mat, "diffuse_color", text="")




# ###################### See if can use invoke() somehow to wait until GP operation finishes before calling convert curve...
# # unsolved problem:  convert grease pencil curve on mouse click release while in modal,
# #                    currently must move mouse to activate convert curve on release functionality
# # want to run in modal until GP finishes, then interpret the "FINISHED", and call the next operation:  possible?
# # class TestGreasePencilReleaseDetection(bpy.types.Operator):
# #     """Testing"""
# #     bl_idname = "scene.detect_grease_pencil"
# #     bl_label = "Detect Grease Pencil Release"

# #     def execute(self, context):
# #         bpy.ops.ed.undo_push(message="convert curve")
# #         convert_curve_fcn(self, False)
# #         return {'FINISHED'}

# #     def invoke(self, context, event):
# #         bpy.ops.ed.undo_push(message="draw curve")
# #         draw_curve_fcn(self)
# #         return {'RUNNING_MODAL'}
# ######################
# class OperatorAfterGreasePencilMacro(bpy.types.Macro):  #bpy.types.Macro
#     """Macro for detecting grease pencil release and immediately converting curve"""
#     bl_idname = "scene.detect_grease_pencil"  # if in panel then is always called
#     bl_label = "Grease Pencil, Detect Release and Convert Curve"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(cls, context):
#         print("in poll from OperatorAfterGreasePencilMacro")
#         # if bpy.context.scene.grease_pencil is not None and \
#         #     bpy.context.scene.grease_pencil.layers.active.active_frame is not None and \
#         #     hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes') and \
#         #     len(bpy.context.scene.grease_pencil.layers.active.active_frame.strokes) > 0:
#         #         # bpy.ops.ed.undo_push(message="convert curve")
#         #         # convert_curve_fcn(self, False)
#         #         print("should convert now")
#         #         return True
#         return True

#     def execute(self, context):  # doesn't get called
#         print("inside OperatorAfterGreasePencilMacro execute")
#         return {'FINISHED'}




def update_render_images(self, context):
# Must appear before bpy.types.Scene.render_images declaration
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




# Sometimes this is necessary before changing modes
def activate_an_object():
    if bpy.context.active_object is not None:
        if bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

    # ob_0 = [ob_0 for ob_0 in bpy.data.objects if ob_0.type == 'MESH' and ob_0.hide == False][0]
    ob_0 = [ob_0 for ob_0 in bpy.data.objects if ob_0.hide == False][0]
    bpy.context.scene.objects.active = ob_0
    ob_0.select = True

def delete_an_object(ob):
    activate_an_object()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = ob
    ob.select = True
    bpy.ops.object.delete()
    activate_an_object()


# Call this before loading any new image stack folders 
def clear_ims(orientation):
    # orientation in {"X","Y","Z"}

    activate_an_object()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    if orientation == "X":
        im_name = "Image X"
        bpy.context.scene.image_path_X = "/"
        image_files_full = bpy.context.scene.imagefilepaths_x

    elif orientation == "Y":
        im_name = "Image Y"
        bpy.context.scene.image_path_Y = "/"
        image_files_full = bpy.context.scene.imagefilepaths_y

    elif orientation == "Z":
        im_name = "Image Z"
        bpy.context.scene.image_path_Z = "/"
        image_files_full = bpy.context.scene.imagefilepaths_z

        # Also remove ImageStackLadder if Z
        isl = [ob for ob in bpy.data.objects if ob.name == "ImageStackLadder"]
        if isl != []:
            isl = isl[0]
            delete_an_object(isl)

    # Delete image objects
    im_ob_list = [ob for ob in bpy.context.scene.objects if ob.name == im_name]
    if len(im_ob_list) > 0:
        for im_ob in im_ob_list:
            delete_an_object(im_ob)

    # Delete loaded images
    image_files_names = [os.path.split(imf.name)[1] for imf in image_files_full]  # File names only
    for f in bpy.data.images:
        this_name = f.name
        if this_name in image_files_names:
            f.user_clear()
            bpy.data.images.remove(f)
    image_files_full.clear()




# class ClearImages(bpy.types.Operator):
#     """Clear all images and image directories in memory"""
#     # clearing names is necessary if new image folder contains same names as previous folder
#     bl_idname = "object.clear_images"
#     bl_label = "Clear all images in memory (necessary if new image folder contains same names as previous folder)"
#     bl_options = {"REGISTER", "UNDO"}

#     def execute(self, context):
#         # any_ob = bpy.context.scene.objects[0]
#         # any_ob.select = True
#         # bpy.context.scene.objects.active = any_ob
#         # bpy.ops.object.mode_set(mode='OBJECT')
#         # bpy.ops.object.select_all(action='DESELECT')
#         # im_ob_list = [ob for ob in bpy.context.scene.objects if ob.name == "Image"]
#         # if len(im_ob_list) > 0:  # delete it
#         #     for im_ob in im_ob_list:
#         #         bpy.context.scene.objects.active = im_ob
#         #         im_ob.select = True
#         #         bpy.ops.object.delete()

#         #     # Activate an object so other functions have appropriate modes
#         #     ob_0 = [ob_0 for ob_0 in bpy.data.objects if ob_0.type == 'MESH' and ob_0.hide == False][0]
#         #     bpy.context.scene.objects.active = ob_0
#         #     ob_0.select = True

#         # for f in bpy.data.images:
#         #     f.user_clear()
#         #     bpy.data.images.remove(f)

#         # # Also clear image directories
#         # bpy.context.scene.image_path_X = "/"
#         # bpy.context.scene.image_path_Y = "/"
#         # bpy.context.scene.image_path_Z = "/"
#         # bpy.context.scene.imagefilepaths_x.clear()
#         # bpy.context.scene.imagefilepaths_y.clear()
#         # bpy.context.scene.imagefilepaths_z.clear()

#         # # Remove ImageStackLadder
#         # isl = [ob for ob in bpy.data.objects if ob.name == "ImageStackLadder"]
#         # if isl != []:
#         #     isl = isl[0]
#         #     isl.select = True
#         #     bpy.ops.object.delete() 

#         clear_ims("X")
#         clear_ims("Y")
#         clear_ims("Z")

#         return {'FINISHED'}


class ImageScrollOperator(bpy.types.Operator):
    """Scroll through image stack from selected image with mouse scroll wheel"""
    bl_idname = "object.modal_operator"
    bl_label = "Modal Operator"
    bl_options = {"REGISTER", "UNDO"}
    # bl_options = {"GRAB_POINTER"}

    @classmethod
    def poll(self, context):
        # # print("in poll from ImageScrollOperator")
        # if bpy.context.scene.grease_pencil is not None and \
        #     bpy.context.scene.grease_pencil.layers.active.active_frame is not None and \
        #     hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes') and \
        #     len(bpy.context.scene.grease_pencil.layers.active.active_frame.strokes) > 0:
        #         print("should convert curve now, but can't modify data from poll() function...")
        #         # bpy.ops.ed.undo_push(message="convert curve")
        #         # convert_curve_fcn(self)  # "can't modify blend data in this state (drawing/rendering)""
        return True  # always


    def __init__(self):
        #print("Start")
        tmpvar=0  # needs something here to compile

    def __del__(self):
        #print("End")
        tmpvar=0  # needs something here to compile

    def modal(self, context, event):

      # print("event type: " + event.type)
      # print("event value: " + event.value)
      # if bpy.context.scene.grease_pencil.layers.active.active_frame:
      #   print("active frame exists")
      # if hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes'):
      #   print("strokes exists")

      bpy.data.scenes["Scene"].tool_settings.use_gpencil_continuous_drawing = False
     
      if bpy.context.mode == 'OBJECT' and bpy.context.active_object.type == 'EMPTY':

        if not bpy.context.active_object.image_from_stack_notation:
            self.report({'INFO'},"Image not created with this tool, use Image Stack Interactions tools instead.")
            return {'FINISHED'}

        im_ob = bpy.context.active_object
        (ind, N, delta, orientation, image_files, locs) = getIndex(im_ob)

        # If shift is pressed, the scroll step-size is increased
        movement = 1
        if event.shift:
            movement = bpy.context.scene.shift_step
            if (movement <= 0):
                movement = 1

        
        # Convert grease pencil curve on any action, if convert curve on release is checked
        if bpy.context.scene.convert_curve_on_release and \
            bpy.context.scene.grease_pencil is not None and \
            bpy.context.scene.grease_pencil.layers.active.active_frame is not None and \
            hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes') and \
            len(bpy.context.scene.grease_pencil.layers.active.active_frame.strokes) > 0:
                bpy.ops.ed.undo_push(message="convert curve")
                convert_curve_fcn(self, orientation)


        ### Standard functionality

        # Zoom in and out by adding control to scroll wheel
        elif event.ctrl and event.type == 'WHEELDOWNMOUSE' and event.value == 'PRESS':
            bpy.ops.view3d.zoom(delta=-1)
        elif event.ctrl and event.type == 'WHEELUPMOUSE' and event.value == 'PRESS':
            bpy.ops.view3d.zoom(delta=1)

        # Allow rotating/panning
        elif event.type == 'MIDDLEMOUSE':  
            if event.shift:
                bpy.ops.view3d.move('INVOKE_DEFAULT')
            else:
                bpy.ops.view3d.rotate('INVOKE_DEFAULT')

        # Undo
        elif event.ctrl and event.type == 'Z' and event.value == 'PRESS':
            bpy.ops.ed.undo()
            

        ### Specialty functionality

        # Scroll up and down through the image stack  (now handles 3D)
        elif event.type == 'WHEELDOWNMOUSE' or event.type == 'NUMPAD_MINUS':
            if ind >= movement:
                ind = ind - movement
                # load_im(ind, image_files, im_ob, orientation)  # executed by handler in print_updated_objects() 
                moveImage(im_ob, -delta*movement, orientation)
        elif event.type == 'WHEELUPMOUSE' or event.type == 'NUMPAD_PLUS':
            if ind < N-movement:
                ind = ind + movement
                # load_im(ind, image_files, im_ob, orientation)  # executed by handler in print_updated_objects() 
                moveImage(im_ob, delta*movement, orientation)

        # Mark a sphere on the image at the mouse location 
        elif event.type == 'M' and event.alt and event.value == 'PRESS':

            # Push undo event
            # For currently unknown reasons, two objects are removed on the first undo execution,
            # which is why there are two undo events here.  todo: figure this out (is known problem in Blender)
            bpy.ops.ed.undo_push(message="place marker")
            bpy.ops.ed.undo_push(message="place marker repeat")

            # Intersect ray with image plane
            coord = event.mouse_region_x, event.mouse_region_y  # 2D coordinates of mouse on screen
            place_marker_at_mouse(context, im_ob, coord, orientation)

            # Go back to the main object to continue modal mode
            im_ob.select = True
            bpy.context.scene.objects.active = im_ob

        # Draw with the grease pencil
        elif (event.type == 'D' and event.ctrl and event.value == 'PRESS' and not event.shift) or \
            (event.type == 'D' and event.value == 'PRESS' and not event.shift):
            bpy.ops.ed.undo_push(message="draw curve")
            draw_curve_fcn(self)

        # Erase grease pencil
        elif event.type == 'E' and event.ctrl and event.value == 'PRESS' or \
            (event.type == 'E' and event.value == 'PRESS' and not event.shift):
            bpy.ops.ed.undo_push(message="erase curve")
            erase_curve_fcn(self)

        # Convert drawn curve into 3D mesh curve (if grease pencil strokes exist)
        elif event.type == 'D' and event.ctrl and event.shift and event.value == 'PRESS' and \
            bpy.context.scene.grease_pencil.layers.active.active_frame is not None and \
            hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes') and \
            len(bpy.context.scene.grease_pencil.layers.active.active_frame.strokes) > 0:
                bpy.ops.ed.undo_push(message="convert curve")
                convert_curve_fcn(self, orientation)

        # # Convert grease pencil curve into 3D mesh immediately after drawing completes
        # # todo:  cannot detect end of grease pencil drawing (event is eaten by grease pencil routine instead of passed on),
        # #        so this action happens on any event after grease pencil drawing is terminated (eg mouse move)
        # if bpy.types.Scene.convert_curve_on_release and event.type == 'LEFTMOUSE' and event.value == 'RELEASE':  
        #     # the above is not detected at end of grease pencil session
        #     print("DETECTED GP MOUSE RELEASE!!")
        #     convert_curve_fcn(self)
        # elif bpy.context.scene.convert_curve_on_release and \
        #     bpy.context.scene.grease_pencil is not None and \
        #     bpy.context.scene.grease_pencil.layers.active.active_frame is not None and \
        #     hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes') and \
        #     len(bpy.context.scene.grease_pencil.layers.active.active_frame.strokes) > 0:
        #         bpy.ops.ed.undo_push(message="convert curve DETECTED 2")
        #         convert_curve_fcn(self)


        # Draw with the grease pencil and create curve on release??
        elif (event.type == 'Q' and event.value == 'PRESS'):
            bpy.ops.ed.undo_push(message="draw and convert curve")
            bpy.ops.scene.detect_grease_pencil()



        # Exit modal mode
        elif event.type in ('RIGHTMOUSE', 'ESC'):  # Cancel
            return {'CANCELLED'}
        
        # Is probably best to do nothing on left mouse click


        # bpy.ops.ed.undo_push(message="end modal loop undo")
        return {'RUNNING_MODAL'}  # continue to run in modal mode

    def invoke(self, context, event):
        if bpy.ops.object.mode_set.poll():
          bpy.ops.object.mode_set(mode='OBJECT')
          if (bpy.context.active_object.type=='EMPTY'):
            context.window_manager.modal_handler_add(self)

            # self._initial_mouse = event.mouse_x
            # self._initial_frame = context.scene.frame_current

            return {'RUNNING_MODAL'}  # start running in modal mode
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
    """Find the index of the image currently displayed, according to it's current position"""
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



class SelectStackFolderZ(bpy.types.Operator):  # adjusted
    """Select location of the Z stack images (original image stack)"""
    bl_idname = "importfolder_z.tif"
    bl_label = "Select folder of the Z stack images"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    def execute(self, context):
        clear_ims("Z")
        select_folder_execute(self, "Z", "image_path_Z", "imagefilepaths_z", "image_ext_Z")

        # Insert bar of image stack height with vertex at each z,
        # provides a vertex to click on for "show image at vertex" button
        # when there are no objects in the scene
        insert_image_stack_ladder()

        return {'FINISHED'}
    def invoke(self, context, event):
        select_folder_invoke(self, context, "exte_Z", "image_ext_Z")
        return {"RUNNING_MODAL"}

class SelectStackFolderX(bpy.types.Operator):  # adjusted
    """Select location of the X stack images (OPTIONAL)"""
    bl_idname = "importfolder_x.tif"
    bl_label = "Select folder of the X stack images"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    def execute(self, context):
        clear_ims("X")
        select_folder_execute(self, "X", "image_path_X", "imagefilepaths_x", "image_ext_X")
        return {'FINISHED'}
    def invoke(self, context, event):
        select_folder_invoke(self, context, "exte_X", "image_ext_X")
        return {"RUNNING_MODAL"}

class SelectStackFolderY(bpy.types.Operator):  # adjusted
    """Select location of the Y stack images (OPTIONAL)"""
    bl_idname = "importfolder_y.tif"
    bl_label = "Select folder of the Y stack images"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    def execute(self, context):
        clear_ims("Y")
        select_folder_execute(self, "Y", "image_path_Y", "imagefilepaths_y", "image_ext_Y")
        return {'FINISHED'}
    def invoke(self, context, event):
        select_folder_invoke(self, context, "exte_Y", "image_ext_Y")
        return {"RUNNING_MODAL"}

def select_folder_execute(self, orientation, this_path, these_paths, this_ext):
    if getattr(bpy.context.scene, this_path) != self.directory:
        setattr(bpy.context.scene, this_path, self.directory)

        # load image filenames and extract file extension
        LoadImageFilenames(orientation)
        if len(getattr(bpy.context.scene, these_paths)) < 1:
            self.report({'INFO'}, "No image files found in selected directory")
        else:
            example_name = getattr(bpy.context.scene, these_paths)[0].name
            file_ext = os.path.splitext(example_name)[1]
            setattr(bpy.context.scene, this_ext, file_ext)


def execute(self, context):
        bpy.context.scene.image_path = self.directory

        # load image filenames and extract file extension
        LoadImageFilenames_sn(bpy.context.scene.image_path)
        if len(bpy.context.scene.imagefilepaths) < 1:
            self.report({'INFO'},"No image files found in selected directory")
        else:
            example_name = bpy.context.scene.imagefilepaths[0].name
            file_ext = os.path.splitext(example_name)[1]
            bpy.context.scene.image_ext = file_ext

        # insert bar of image stack height with vertex at each z
        insert_image_stack_ladder()

        return {'FINISHED'}



def select_folder_invoke(self, context, self_ext, this_ext):
    WindowManager = context.window_manager
    WindowManager.fileselect_add(self)
    setattr(self, self_ext, getattr(bpy.context.scene, this_ext))



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
            Nz = len(bpy.context.scene.imagefilepaths_z)
            if Nz > 0:
                if (bpy.context.active_object.type=='MESH'):
                    DisplayImageFunction('Z')  # must call Z last as this might return image as active object
                else:
                    self.report({'INFO'},"Select a vertex on a mesh object")
            else:
                self.report({'INFO'},"No image files found in the Z directory")
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

    if (orientation == 'Z'):
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
       # im_ob.image_from_stack_interactions = True
       im_ob.image_from_stack_notation = True  # denote as being created from this tool, to not be confused with Stack Interactions tool


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
       load_im(ind, image_files, im_ob, orientation)  # todo: maybe should be removed once render options are added?


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


    if orientation == 'Z' and bpy.context.scene.center_view:
        # Move cursor to center of image and center view to cursor
        z_coord = coord
        loc = (x_max/2, y_max/2, z_coord)
        bpy.context.scene.cursor_location = loc
        bpy.ops.view3d.view_center_cursor()
    else:
        # Set original object to active, selects it, place back into editmode
        bpy.context.scene.objects.active = myob
        myob.select = True
        bpy.ops.object.mode_set(mode = 'OBJECT')
  


def place_marker_at_mouse(context, im_ob, coord, orientation):
    # coord = 2D coordinates of mouse on screen (event.mouse_region_x/y)
    region = context.region
    rv3d = context.space_data.region_3d
    ray = region_2d_to_vector_3d(region, rv3d, coord)  # direction from view to mouse location
    ray_origin = region_2d_to_origin_3d(region, rv3d, coord)  # origin of view
    
    if orientation == "Z":
        z = im_ob.location.z
        v0 = Vector([0,0,z])  # triangle on image plane
        v1 = Vector([0,1,z])
        v2 = Vector([1,1,z])
    elif orientation == "Y":
        y = im_ob.location.y
        v0 = Vector([0,y,0])  # triangle on image plane
        v1 = Vector([0,y,1])
        v2 = Vector([1,y,1])
    elif orientation == "X":
        x = im_ob.location.x
        v0 = Vector([x,0,0])  # triangle on image plane
        v1 = Vector([x,0,1])
        v2 = Vector([x,1,1])
    loc = mathutils.geometry.intersect_ray_tri(v0, v1, v2, ray, ray_origin, False)  
    # False means no clipping at triangle boundaries, so will get coordinates for
    # any point on plane, regardless of whether inside this triangle
    add_sphere_at_loc(loc) 


def add_sphere_at_loc(loc):
    # assumes image is selected?

    if bpy.context.scene.coarse_marker:
        segs = 5
        rings = 4
    else:
        segs = 32
        rings = 16

    scl = bpy.context.scene.pt_radius
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, size=scl, segments=segs, ring_count=rings)
    obj = bpy.context.object

    sphere_mat_list = [mat for mat in bpy.data.materials if mat.name == "sphere_material"]
    if len(sphere_mat_list) == 0:
        sphere_mat = bpy.data.materials.new("sphere_material")
        sphere_mat.diffuse_color = (1.0, 0.3, 0.0)
        sphere_mat.alpha = .5
    else:
        sphere_mat = sphere_mat_list[0]

    obj.active_material = sphere_mat
    bpy.ops.object.add_transparency()
    obj.name = bpy.context.scene.marker_prefix  # "marker"

    # turn off origin marker
    bpy.context.space_data.show_manipulator = False


class AddTranspButton(bpy.types.Operator):
    """Define transparency of selected mesh object"""
    bl_idname = "object.add_transparency"
    bl_label = "Add Transparency"
    bl_options = {"REGISTER", "UNDO"}

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
    bl_options = {"REGISTER", "UNDO"}

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


def insert_image_stack_ladder():
    # insert bar of image stack height with vertex at each z value in stack

    bpy.ops.object.mode_set(mode='OBJECT')

    # If ImageStackLadder already exists, remove it and replace with new one
    if bpy.data.objects.get("ImageStackLadder") is not None:
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects["ImageStackLadder"].select = True
        bpy.ops.object.delete()


    h = bpy.context.scene.z_side
    n = len(bpy.context.scene.imagefilepaths_z)
    d = h / (n-1)
    pts = [[0,0,z*d+d/2] for z in range(0,n)]
    objname = "ImageStackLadder"

    # assign the point marker radius to default to something reasonable
    rad = get_mesh_density_threshold() * 5
    bpy.context.scene.pt_radius = rad
    rot = [0, 0, -math.pi/4]

    ladder_rad = get_mesh_density_threshold() * 5
    for p in pts:
        loc = p
        #bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=d, location=loc,  end_fill_type='NOTHING')
        bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=ladder_rad, depth=d, location=loc, end_fill_type='NOTHING', rotation=rot)
        bpy.context.active_object.name = "ladder_temp"

    # "join" all cylinders into single object
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if "ladder_temp" in obj.name:
            obj.select = True
    bpy.ops.object.join()
    bpy.context.active_object.name = "ImageStackLadder"

    mat = bpy.data.materials.new("ladder_material")
    mat.diffuse_color = (1.0,0.0,0.0)
    bpy.context.active_object.active_material = mat

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.remove_doubles()

    # cap top and bottom of cylinder, for aesthetic purposes only
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.region_to_loop()
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.view3d.view_selected()
    bpy.ops.object.mode_set(mode = 'EDIT')

    # return in EDIT mode (nothing selected), ready for individual point(s) to be selected


class AddSphere(bpy.types.Operator):
    """Add a spherical marker to the scene at the cursor location on the selected image"""
    bl_idname = "object.add_sphere"
    bl_label = "Add sphere on image to scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.mode == 'OBJECT' and \
           bpy.context.active_object is not None and \
           bpy.context.active_object.type == 'EMPTY':  # if image is selected
                im_ob = bpy.context.active_object
                loc = bpy.context.scene.cursor_location
                add_sphere_at_loc(loc)

                # return with image as active object
                bpy.context.scene.objects.active = im_ob

        else:
            self.report({'INFO'},"Must select image to add marker")
        return {"FINISHED"}


class AddSphere_pt0(bpy.types.Operator):
    """Add a spherical marker to the scene at the vertex index 0 of active object"""
    bl_idname = "object.add_sphere_pt0"
    bl_label = "Add sphere at vertex 0 of active object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        this_ob = bpy.context.object
        loc = this_ob.data.vertices[0].co
        add_sphere_at_loc(loc)
        return {"FINISHED"}



class UpdateMarkerRadius(bpy.types.Operator):
    """Update radii of all spherical markers selected"""
    bl_idname = "mesh.update_marker_radius"
    bl_label = "update marker radius"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        s = bpy.context.scene.pt_radius
        scl = [s,s,s]
        objlist = [obj for obj in bpy.context.selected_objects if hasattr(obj, 'data') and obj.data.name[0:6] == 'Sphere']
        for obj in objlist:
            obj.scale = scl
        return {'FINISHED'}

class DrawCurve(bpy.types.Operator):
    """Draw object outline (from scroll mode, Shortcut: D)"""
    bl_idname = "object.draw_curve"
    bl_label = "draw curve with grease pencil"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        draw_curve_fcn(self)
        bpy.data.scenes["Scene"].tool_settings.use_gpencil_continuous_drawing = False
        return {'FINISHED'}

def draw_curve_fcn(self):
    print("in draw_curve_fcn()")

    # On release, leave grease pencil mode (might want to change functionality in the future)
    bpy.data.scenes["Scene"].tool_settings.use_gpencil_continuous_drawing = False

    blender_vsn = float(bpy.app.version_string[0:4])

    # draw closed curve with grease pencil, can erase
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.gpencil.draw('INVOKE_REGION_WIN',mode='DRAW')
    for g in bpy.data.grease_pencil:
        bpy.data.scenes["Scene"].tool_settings.use_gpencil_continuous_drawing = False

        # Project drawn curves onto image plane 
        if blender_vsn < 2.77:
            g.draw_mode = 'SURFACE'
        else:
            bpy.context.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'

        if blender_vsn >= 2.78:
            for plt in g.palettes:  # color of stroke while drawing
                plt.colors[0].color = Vector([0,1,0])

        for lyr in g.layers:
            if blender_vsn < 2.78:
                lyr.color = Vector([0,1,0])
                lyr.line_width = 2
            else:
                lyr.tint_color = Vector([0,1,0])
                lyr.tint_factor = 1.0
                # should also set line_width, but is no longer a property of the layer in 2.78
            lyr.show_x_ray = False  # visibility from z-buffer, not always visible
    bpy.context.area.type = original_type  # maybe not necessary anymore, v2.78?
    bpy.data.scenes["Scene"].tool_settings.use_gpencil_continuous_drawing = False
    self.report({'INFO'},"Drawing...")


class EraseCurve(bpy.types.Operator):
    """Erase (a portion of) drawn curve (from scroll mode, Shortcut: E)"""
    bl_idname = "object.erase_curve"
    bl_label = "erase (a portion of) drawn curve"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        erase_curve_fcn(self)
        return {'FINISHED'}

def erase_curve_fcn(self):
    # exactly the grease pencil erasor, only here for convenience
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.gpencil.draw('INVOKE_REGION_WIN',mode='ERASER')
    bpy.context.area.type = original_type


class ConvertCurve(bpy.types.Operator):
    """Convert drawn curve to Blender curve"""
    bl_idname = "object.convert_curve"
    bl_label = "convert grease pencil drawing to curve"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        imageName = bpy.context.object.name  # Assume plane is active object
        if imageName[0:5] != "Image":
            self.report({'INFO'},"Image plane of this curve must be active")
            return {'CANCELLED'}
        orientation = imageName[-1]
        convert_curve_fcn(self, orientation)
        return {'FINISHED'}


def convert_curve_fcn(self, orientation):  #, proj_z=False):
    print("in convert_curve_fcn()")

    # Convert grease pencil markings to mesh curve
    # grease pencil drawings are part of current image until converted
    if bpy.context.object.type != "EMPTY":
        self.report({'INFO'},"Image plane of this curve must be active")
        return {'CANCELLED'}

    # for g in bpy.data.grease_pencil:
    #     if g.draw_mode != 'SURFACE':
    #         g.draw_mode = 'SURFACE'
    #         self.report({'INFO'},"Warning: Grease Pencil Drawing Settings changed to Surface mode for currect curve projection")
    bpy.context.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'  # new versions of blender

    the_image = bpy.context.object
    
    # convert curve to polyline, image is still active object
    bpy.ops.gpencil.convert()

    # Erase all grease pencil markings
    original_type = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.gpencil.active_frame_delete()
    bpy.context.area.type = original_type

    # Make the curve the active object
    for obj in bpy.data.objects:
        if "GP_Layer" in obj.name:
            new_curve = obj
    bpy.context.scene.objects.active = new_curve
    new_curve.name = "curve"

    # Toggle Cyclic to make a closed curve
    if bpy.context.scene.closed_curve:
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.curve.cyclic_toggle()
        bpy.ops.object.mode_set(mode = 'OBJECT')

    # Convert to mesh
    print("before curve convert()")
    bpy.ops.object.convert(target='MESH')


    print("nverts before incorrect z-value vertex removal: ", len(bpy.context.active_object.data.vertices))

    # Remove points with incorrect z-value, 
    # eg if drew over another curve, will project single point to height of that curve
    if orientation == "Z":
        N = len(bpy.context.scene.imagefilepaths_z)
        delta_z = bpy.context.scene.z_side / N / 2
        z_ind = 2
    elif orientation == "X":
        N = len(bpy.context.scene.imagefilepaths_x)
        delta_z = bpy.context.scene.x_side / N / 2
        z_ind = 0
    elif orientation == "Y":
        N = len(bpy.context.scene.imagefilepaths_y)
        delta_z = bpy.context.scene.y_side / N / 2
        z_ind = 1
    z_err = delta_z / 2  # arbitrary

    # Use median z-value as representative of curve
    all_zs = [v.co[z_ind] for v in new_curve.data.vertices]
    z_med = median(all_zs)

    # Remove all points not sufficiently close to z_med
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    in_consec_section_to_remove = False
    for ind, v in enumerate(new_curve.data.vertices):
        this_z = v.co[z_ind]
        if (abs(this_z - z_med) > z_err):
            v.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.dissolve_verts()  # deletes verts, connects verts not deleted across hole of deleted verts
    bpy.ops.object.mode_set(mode='OBJECT')


    print("nverts before fork and loop vertex removal: ", len(bpy.context.active_object.data.vertices))

    # Remove extraneous vertices that sometimes appear in the curve conversion (forks and loops)
    nverts = len(bpy.context.active_object.data.vertices)
    if bpy.context.scene.closed_curve:
        # divide curve into three sections, remove bad verts from each section separately
        # thereby forcing the shortest path selection to run through the entire closed curve
        nsub = math.floor(nverts/3)
        remove_extraneous_verts(new_curve, 0, nsub)
        remove_extraneous_verts(new_curve, nsub, 2*nsub)
        remove_extraneous_verts(new_curve, 2*nsub, nverts-1)
    else:
        remove_extraneous_verts(new_curve, 0, nverts-1)  # entire curve


    print("nverts before subdividing necessary edges: ", len(bpy.context.active_object.data.vertices))

    # Subdivide edges where vertices were removed
    nverts = len(bpy.context.active_object.data.vertices)
    # print("nverts before: ", nverts)
    thresh = get_mesh_density_threshold()
    for ind in range(len(bpy.context.active_object.data.edges)):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        edg = bpy.context.active_object.data.edges[ind]
        v0 = bpy.context.active_object.data.vertices[edg.vertices[0]].co
        v1 = bpy.context.active_object.data.vertices[edg.vertices[1]].co
        this_len = get_dist(v0,v1)
        if this_len > thresh:
            print("do some somedividing!")
            ndivs = math.ceil(math.log(this_len / thresh) / math.log(2))
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.context.active_object.data.edges[ind].select = True
            bpy.ops.object.mode_set(mode = 'EDIT')
            for sub_ind in range(ndivs):
                print("subdivide", ind, sub_ind)
                bpy.ops.mesh.subdivide()
            bpy.ops.object.mode_set(mode = 'OBJECT')


        # this_len = max(bpy.context.scene.x_side, bpy.context.scene.y_side)
        # thresh = this_len / 500.0  # from create_curve for remove_doubles, arbitrary
        # thresh = thresh * 5
        # count = 0
        # for ind in range(len(obj.data.edges)):
        #     bpy.ops.object.mode_set(mode = 'OBJECT')
        #     edg = bpy.context.active_object.data.edges[ind]
        #     v0 = obj.data.vertices[edg.vertices[0]].co
        #     v1 = obj.data.vertices[edg.vertices[1]].co
        #     this_len = get_dist(v0,v1)
        #     if this_len > thresh:  # this is slow
        #         bpy.ops.object.mode_set(mode = 'EDIT')
        #         bpy.ops.mesh.select_all(action='DESELECT')
        #         bpy.ops.object.mode_set(mode = 'OBJECT')
        #         bpy.context.active_object.data.edges[ind].select = True
        #         bpy.ops.object.mode_set(mode = 'EDIT')
        #         bpy.ops.mesh.subdivide()
        #         bpy.ops.mesh.subdivide()
        #         bpy.ops.mesh.subdivide()
        #         bpy.ops.object.mode_set(mode = 'OBJECT')
        # bpy.ops.object.mode_set(mode = 'EDIT')
        # bpy.ops.mesh.select_all(action='SELECT')
        # bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')  # todo:  check options
        # bpy.ops.mesh.tris_convert_to_quads()



    print("nverts before curve downsampling: ", len(bpy.context.active_object.data.vertices))

    # Downsample a bit, for speed (do this only at the end of this function!)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # thresh = get_mesh_density_threshold()
    bpy.ops.mesh.remove_doubles(threshold = thresh)
    bpy.ops.object.mode_set(mode = 'OBJECT')


    print("nverts before convert to quads: ", len(bpy.context.active_object.data.vertices))

    # Convert to quads, for speed
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # Return image as only active object, ready to draw again
    bpy.ops.object.select_all(action='DESELECT')
    the_image.select = True
    bpy.context.scene.objects.active = the_image

    print("end of convert_curve_fcn()")



def duplicateObject_tmp(scene, name, copyobj):
 
    # Create new mesh
    mesh = bpy.data.meshes.new(name)
 
    # Create new object associated with the mesh
    ob_new = bpy.data.objects.new(name, mesh)
 
    # Copy data block from the old object into the new object
    ob_new.data = copyobj.data.copy()
    ob_new.scale = copyobj.scale
    ob_new.location = copyobj.location
 
    # Link new object to the given scene and select it
    scene.objects.link(ob_new)
    ob_new.select = True
 
    return ob_new



def remove_extraneous_verts(crv, v0_ind, v1_ind):
# Remove extraneous vertices between vertices v0 and v1 that  
# sometimes appear in the curve conversion (forks and loops)
# assumes crv = active object is mesh curve

    # print(v0_ind, v1_ind, len(crv.data.vertices))

    # Select endpts of curve, highlight shortest path between endpts
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    crv.data.vertices[v0_ind].select = True
    crv.data.vertices[v1_ind].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.shortest_path_select()
    bpy.ops.object.mode_set(mode='OBJECT')


    # # for debugging
    # # problem is that vertices were added in the middle (from subdivide), so v[-1] is no longer at the end
    # count = 0
    # for v in bpy.context.active_object.data.vertices:
    #     if v.select == False:
    #         count += 1
    # if count > .1 * len(bpy.context.active_object.data.vertices):
    #     print("WARNING! about to delete too many vertices!", count, len(bpy.context.active_object.data.vertices))
    #     crv_copy = duplicateObject_tmp(bpy.context.scene, "tmp", bpy.context.active_object)
    # # end debugging



    # # Delete all unselected points:  can't do it this way!
    # # want to keep other sections of the curve if closed curve
    # bpy.ops.object.mode_set(mode='EDIT')
    # bpy.ops.mesh.select_all(action='INVERT')
    # bpy.ops.mesh.delete(type='VERT')
    # bpy.ops.object.mode_set(mode = 'OBJECT')

    # Store indices of all pts not selected:  these are the vertices (and edges) to remove
    bad_inds = []
    for ind in range(v0_ind, v1_ind):
        if not crv.data.vertices[ind].select:
            bad_inds.append(ind)

    # If there were bad vertices, remove them
    if len(bad_inds) > 0:
        # me = new_curve.data # use current object's data
        # me_copy = me.copy()
        # ob = bpy.data.objects.new("CurveWithBadVerts", me_copy)
        # ob.location = new_curve.location
        # scene = bpy.context.scene
        # scene.objects.link(ob)
        # scene.update()

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        for ind in bad_inds:
            crv.data.vertices[ind].select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')



def get_dist(coord1, coord2):
    d = math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2 + \
        (coord1[2] - coord2[2])**2)
    return d

def adjust_vert_indices(newlist, ptset_ind):
# re-adjust vertex indices given than all vertices in ptset have been merged
    newlist_static = copy.deepcopy(newlist)
    kept_ind = min(newlist[ptset_ind])  # the ind of the merged point
    for pt in newlist[ptset_ind]:
        if pt != kept_ind:
            for setind in range(ptset_ind+1, len(newlist)):
                static_list = newlist_static[setind]
                for ind in range(len(static_list)):
                    if static_list[ind] > pt:  # should never have ==
                        newlist[setind][ind] -= 1


def get_mesh_density_threshold():
# defines how dense the mesh should be, the number returned is the distance 
# between mesh points, roughly based on number of vertices per image size;
# used as parameter for remove_doubles on curves and also to define 
# the number of intermediate cuts in the surface construction 
    this_len = max(bpy.context.scene.x_side, bpy.context.scene.y_side)
    npts_per_side = bpy.context.scene.scene_precision
    thresh = this_len / npts_per_side   # 0.01 or less is good
    return thresh


def loft_curves_to_surface(crvs):
# given multiple highlighted mesh curves, create a mesh surface
# use Blender's Edges - Bridge Edge Loops (rather than LoopTools)
# function can handle any number of curves, but current implementation should only
# be passing in pairs of curves around holes (or all curves if no holes)

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.ops.object.select_all(action='DESELECT')
    for c in crvs:
        c.select = True
        bpy.context.scene.objects.active = c  # else on join can get Warning: Active object is not a selected mesh

    # Define number of intermediate layers of edges to create
    # distance based on an approximation for median distance between curves
    p0c0 = crvs[0].data.vertices[0].co
    p0c1 = crvs[1].data.vertices[0].co
    d0 = get_dist(p0c0, p0c1)
    p1c0 = crvs[0].data.vertices[1].co
    p1c1 = crvs[1].data.vertices[1].co
    d1 = get_dist(p1c0, p1c1)
    p2c0 = crvs[0].data.vertices[2].co
    p2c1 = crvs[1].data.vertices[2].co
    d2 = get_dist(p2c0, p2c1)
    this_dist = max(d0, d1, d2)

    thresh = get_mesh_density_threshold() * 2
    ncuts = math.ceil(this_dist / thresh)
    # ncuts = 0

    bpy.ops.object.join()

    obj = bpy.context.object
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # bpy.ops.mesh.looptools_bridge(interpolation='linear', cubic_strength=1, loft=True, loft_loop=False, \
    #     min_width=0, mode='shortest', remove_faces=True, reverse=False, segments=nsegs, twist=0)
    # execute_looptools_bridge_Neuromorph()  # no, use Bridge Edge Loops instead!
    bpy.ops.mesh.bridge_edge_loops(number_cuts=ncuts, interpolation="LINEAR")



class MeshFromCurves(bpy.types.Operator):
    """Combine curves into mesh object"""
    bl_idname = "mesh.curves2object"
    bl_label = "update marker radius"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        print("in MeshFromCurves(), before sort_curves()")

        # Sort curves into layers by z-value
        crvs_layers, hole_data_layers, orientation = sort_curves(self)
        if crvs_layers == []:
            return {'FINISHED'}

        print("before group_curves()")

        # Group the curves into sets that can be processed together
        crvs_grouped = group_curves(self, crvs_layers, hole_data_layers)

        # for debugging
        print("curve groups after group_curves():")
        for cg in crvs_grouped:
            print(cg)
        # end for debugging


        # Loft each curve group to separate surfaces
        surfs = []
        for grp in crvs_grouped:
            loft_curves_to_surface(grp)
            bpy.ops.object.mode_set(mode = 'OBJECT')
            obj = bpy.context.object
            surfs.append(obj)

        print("curve groups have been lofted")

        # Join all new surfaces and remove doubles
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for obj in surfs:
            obj.select = True
            bpy.context.scene.objects.active = obj
        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode = 'OBJECT')


        print("before scene and surface cleanup")

        # Delete curves:  only delete curves that are still curves!
        for clist in crvs_layers:
            if clist is not None:
                print("deleting curves")
                for crv in clist:
                    if crv is not None and crv != obj:  #crv.name != obj.name
                        # print(crv)  # are more curves than can see in object list:  possibly dangerous deletions
                        bpy.ops.object.select_all(action='DESELECT')
                        crv.select = True
                        bpy.context.scene.objects.active = crv
                        bpy.ops.object.delete()

        # Make object active
        bpy.context.scene.objects.active = obj

        # Downsample a bit (mostly just remove the very contensed points), but maintain boundary edges
        thresh = get_mesh_density_threshold()
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.remove_doubles(threshold = thresh, use_unselected = False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Smooth the final surface with the Laplacian smoothing modifier?
        # todo: this might be doing too much (shrinking the object)
        if 0:
            obj = bpy.context.object

            bpy.ops.object.modifier_add(type='LAPLACIANSMOOTH')
            obj.modifiers["Laplacian Smooth"].lambda_border = 0
            if bpy.context.scene.closed_curve:  # might still be too much
                obj.modifiers["Laplacian Smooth"].lambda_factor = 0.1  # todo:  don't hardcode?
                obj.modifiers["Laplacian Smooth"].iterations = 20
            else:
                obj.modifiers["Laplacian Smooth"].lambda_factor = 1.0  # todo:  don't hardcode?
                obj.modifiers["Laplacian Smooth"].iterations = 100
            obj.modifiers["Laplacian Smooth"].use_normalized = True


        # Return transparent mesh
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.context.object

        surf_mat_list = [mat for mat in bpy.data.materials if mat.name == "surf_material"]
        if len(surf_mat_list) == 0:
            surf_mat = bpy.data.materials.new("surf_material")
            surf_mat.diffuse_color = (0.67, 0.0, 1.0)
            surf_mat.alpha = .75
        else:
            surf_mat = surf_mat_list[0]

        obj.active_material = surf_mat
        bpy.ops.object.add_transparency()
        obj.name = obj.name = bpy.context.scene.surface_prefix  # "new_surf"

        return {'FINISHED'}


def sort_curves(self):
# extract curves, sort by z value,
# return list of curve groups to loft separately, and data about any holes

    # Extract curves
    objs = bpy.context.scene.objects
    crvs = []
    for o in objs:
        if o.select:
            if hasattr(o, 'data') and hasattr(o.data, 'vertices'):
                crvs.append(o)
            else:
                print(o.name)
                self.report({'INFO'},"Non-mesh objects cannot be combined into surface")
                return [], []

    print("there are appropriate curves to sort")

    # Determine orientation from first curve
    # If diff_z < delta_z, take curves as coming from the same layer
    xs = [pt.co[0] for pt in crvs[0].data.vertices]
    ys = [pt.co[1] for pt in crvs[0].data.vertices]
    zs = [pt.co[2] for pt in crvs[0].data.vertices]
    sd_x = np.std(xs)
    sd_y = np.std(ys)
    sd_z = np.std(zs)
    if min(sd_x, sd_y, sd_z) == sd_x:
        orientation = "X"
        z_ind = 0
        N = len(bpy.context.scene.imagefilepaths_x)
        delta_z = bpy.context.scene.x_side / N / 2
    elif min(sd_x, sd_y, sd_z) == sd_y:
        orientation = "Y"
        z_ind = 1
        N = len(bpy.context.scene.imagefilepaths_y)
        delta_z = bpy.context.scene.y_side / N / 2
    elif min(sd_x, sd_y, sd_z) == sd_z:
        orientation = "Z"
        z_ind = 2
        N = len(bpy.context.scene.imagefilepaths_z)
        delta_z = bpy.context.scene.z_side / N / 2

    # Sort curves by z value (same z-values are in arbitrary order)
    crvs = sorted(crvs, key=lambda c: c.data.vertices[0].co[z_ind])  # sort by z

    # Loop through curves, make list for each separate z-value
    # Sort curves within each z-value set, storing extreme endpts and the centerpts of each hole
    ncrvs = len(crvs)
    crvs_layers = []
    hole_data = []  # [[endpts, ctr_pts]]
    ind = 0
    while ind < ncrvs:
        crv_list = []
        ctr_pts = []
        endpts = []

        z_cur = crvs[ind].data.vertices[0].co[z_ind]

        if ind == ncrvs-1:  # no holes if no further curves to process
            z_next = z_cur + delta_z*2  # to be > delta_z
        else:
            z_next = crvs[ind+1].data.vertices[0].co[z_ind]

        if abs(z_cur - z_next) >= delta_z:  # no holes in this layer
            crvs_layers.append([crvs[ind]])
            endpts = [crvs[ind].data.vertices[0].co, crvs[ind].data.vertices[-1].co]
            hole_data.append([endpts, []])
            ind += 1

        else:  # there are >0 holes in this layer
            # determine how many segments in this layer
            ii = ind
            while ii < ncrvs-1 and abs(crvs[ii+1].data.vertices[0].co[z_ind] - z_cur) < delta_z:  # crvs[ind+1] exists, else would be in if above
                ii += 1
            crv_list_unordered = crvs[ind:(ii+1)]
            crv_list, ctr_pts, endpts = order_curves(crv_list_unordered, orientation)  # same z-value

            n_here = len(crv_list)
            crvs_layers.append(crv_list)
            hole_data.append([endpts, ctr_pts])
            ind += n_here


    print("before relative curve ordering")

    # Check for relative curve ordering in adjacent curves at the boundaries between groups
    # Re-order curves in list and hole data if necessary (not reordering points, just curves in list)
    for ii in range(len(crvs_layers)-1):
        # crvs_this is fixed, decide whether to flip next layer
        n_crvs_next = len(crvs_layers[ii+1])
        
        #if n_crvs_next > 1:  # no, need to catch case where last curve has no holes but needs to be reversed
        endpts_here = hole_data[ii][0]
        endpts_next = hole_data[ii+1][0]
        reverse_order = get_crv_order(endpts_here, endpts_next)

        if reverse_order:  # reverse order of curves_next and hole_data_next
            # for jj in range(n_crvs_next):
                # crvs_layers[ii+1][jj].reverse()
                crvs_layers[ii+1].reverse()
                hole_data[ii+1][0].reverse()
                hole_data[ii+1][1].reverse()


    print("before point reordering")

    # Now reorder the points in each curve segment to be ordered consistently.
    # Look at the distance from the endpoints of each curve to the endpoints 
    # of the layer (as these are supposedly now consistent)
    # Define order by the minimum distance of these four distances
    # todo:  change condition to be based on endpts of previous/next segments, probably better

    if not bpy.context.scene.closed_curve:  # todo:  is this correct?

        for layer_ind in range(len(crvs_layers)):
            endpt0 = hole_data[layer_ind][0][0]
            endpt1 = hole_data[layer_ind][0][1]
            endpts_layer = [endpt0, endpt1]
            for crv in crvs_layers[layer_ind]:
                crv_e0 = crv.data.vertices[0].co
                crv_e1 = crv.data.vertices[-1].co
                endpt_crv = [crv_e0, crv_e1]
                reverse_order = get_crv_order(endpts_layer, endpt_crv)

                if reverse_order:
                    # crv.data.vertices.reverse()  # no, can't reverse a bpy_prop_collection
                    
                    # Assume vertices are in order, so ordered edge list is valid
                    vert_list_orig = list(crv.data.vertices)
                    edge_list = []
                    vert_list = []
                    for ind, v in enumerate(vert_list_orig):
                        vert_list.insert(0, tuple(v.co))
                        edge_list.append((ind, ind+1))

                    # if bpy.context.scene.closed_curve:  # add closing edge; no, shouldn't be here if closed curve
                    #     edge_list.append((ind, 0))
                    #     # edge_list.append((0, ind))

                    # vert_list.reverse()  # inserting at index 0 effectively reverses the list, todo: check this
                    edge_list.pop()

                    # create mesh from python data
                    mesh = bpy.data.meshes.new(name = "mesh")
                    mesh.from_pydata(vert_list, edge_list, [])
                    crv.data = mesh
                    # crv.data.update()  # todo: is this necessary?
                    # http://blender.stackexchange.com/questions/21441/replacing-all-mesh-elements-in-a-mesh-object
                    # http://blenderscripting.blogspot.nl/2013/05/adding-geometry-to-existing-geometry.html


    print("")
    print("at end of sort_curves:")
    for crv in crvs_layers:
        print(crv)
    print(" ")

    return crvs_layers, hole_data, orientation
    # each layer contains all curves for a distinct z-value, hole_data exists for each z-value


def group_curves(self, crvs_layers, hole_data_layers):
# sort curves into groups that can be lofted together
# do everything except the actual lofting in this loop

    # For each hole, calculate its pctg along the way from endpt1 to endpt2, store as list with entry for each layer
    # hole_data = [endpts, ctr_pts]
    hole_pctgs = get_hole_pctgs(hole_data_layers)

    # Loop through layers

    crv_groups = []         # a list of lists of curves to be lofted together, 
                            # segments from a single layer will appear in different groups around its holes

    crv_groups_tmp = []     # the groups of curves that are currently being constructed around holes;  
                            # when a hole closes, the completed group will be removed and added to crv_groups
                            # [0] is list of curves, [1] is pctg

    delta_p_thresh = 0.25   # defines how different holes from two adjacent layers can be 
                            # and still be considered the same hole;  this value is very arbitrary

    print("before curve group processing")

    ind = 1  # process on layers this and prev

    while ind < len(crvs_layers):
        nholes_here = len(hole_data_layers[ind][1])

        print("processing layer", ind, "with",  nholes_here, "holes")

        # Work through all hole ctrpts in this layer or previous layer
        all_pctgs = combine_hole_data(hole_pctgs[ind], hole_pctgs[ind-1], 
                                      hole_data_layers[ind], hole_data_layers[ind-1], delta_p_thresh)

        # cannot create Blender objects from Python api, need to copy a la Blender
        crvs_here = deepcopy_blender_curve_list(crvs_layers[ind])  
        crvs_prev = deepcopy_blender_curve_list(crvs_layers[ind-1])

        # The current layer has no holes
        if nholes_here == 0:  # 

            # Exactly case 2 below, close hole in previous layer
            for pctg, owner, ctrpt in all_pctgs:
                crv_here = crvs_here[0]  # crv 0 is popped from list once it has been processed
                crv_prev = crvs_prev[0]

                # Find point in this layer closest to ctrpt_prev
                vert_ind_crv_here = get_closest_pt_ind(crv_here, ctrpt)

                # Copy crv_here, keeping keep only vertices from index 0 to vert_ind_crv_here
                crv_here_new = construct_sub_crv(crv_here, vert_ind_crv_here, 0)

                # Add new segment and crv_prev to crv_groups
                crv_groups.append([crv_prev, crv_here_new])
                del crvs_prev[0]  # delete crv_here from list

                # Delete used vertices from crv_prev
                crv_here = construct_sub_crv(crv_here, vert_ind_crv_here, 1, False)  #crv_prev=
                crvs_here[0] = crv_here  # todo:  probably not necessary
            crv_groups.append([crvs_prev[0], crvs_here[0]])

            # todo:  confirm that appending the last bit is good for all cases...

            # Don't search ahead through layers until nholes > 0, as can't guarantee 
            # z ordering this way (it will create surface of minimum surface area)
            ind = ind + 1


        # The current layer has holes, find breaking point from previous layer, maintain lists of separate surfaces being constructed
        else:
            for pctg, owner, ctrpt in all_pctgs:
                crv_here = crvs_here[0]  # crv 0 is popped from list once it has been processed
                crv_prev = crvs_prev[0]

                if owner == 1:  # Hole in this layer only

                    # print("start: ", crv_here.name, crv_prev.name, ", nverts crv_prev =", str(len(crv_prev.data.vertices)))

                    # Find point in previous layer closest to ctrpt_here
                    vert_ind_crv_prev = get_closest_pt_ind(crv_prev, ctrpt)

                    # Copy crv_prev, keeping keep only vertices from index 0 to vert_ind_crv_prev
                    crv_prev_new = construct_sub_crv(crv_prev, vert_ind_crv_prev, 0)

                    # Add new segment and crv_here to crv_groups
                    crv_groups.append([crv_prev_new, crv_here])
                    del crvs_here[0]  # delete crv_here from list

                    # Delete used vertices from crv_prev
                    crv_prev = construct_sub_crv(crv_prev, vert_ind_crv_prev, 1, False)  #crv_prev=
                    crvs_prev[0] = crv_prev  # todo:  probably not necessary


                elif owner == 2:  # Hole in prev layer only
                    
                    # crv_here = copy.deepcopy(crvs_layers[ind][0])  # only one crv here;  leave crvs_here in place to use in crvs_no_holes

                    # Find point in this layer closest to ctrpt_prev
                    vert_ind_crv_here = get_closest_pt_ind(crv_here, ctrpt)

                    # Copy crv_here, keeping keep only vertices from index 0 to vert_ind_crv_here
                    crv_here_new = construct_sub_crv(crv_here, vert_ind_crv_here, 0)

                    # Add new segment and crv_prev to crv_groups
                    crv_groups.append([crv_prev, crv_here_new])
                    del crvs_prev[0]  # delete crv_here from list

                    # Delete used vertices from crv_prev
                    crv_here = construct_sub_crv(crv_here, vert_ind_crv_here, 1, False)  #crv_prev=
                    crvs_here[0] = crv_here  # todo:  probably not necessary


                elif owner == 3:  # This hole is in both layers, don't need deep copy here
                    crv_groups.append([crvs_prev[0], crvs_here[0]])
                    del crvs_here[0]
                    del crvs_prev[0]

            # end for pctg, owner, ctrpt in all_pctgs  
            ind = ind + 1

            # Finally, outside loop across this layer of holes, add last segment of crvs_here to list containing last segment of crvs_prev
            crv_groups.append([crvs_prev[0], crvs_here[0]])

        # end else:  the current layer has holes

    return crv_groups

    # Now just need to loft, join, remove doubles, and are done?  (have completed this in the other function)



def deepcopy_blender_curve_list(crv_list):
# create a deep copy of a list of Blender curve objects
# (cannot use Python API to greate Blender objects)
    crvs_copy = []
    for crv in crv_list:
        # Unhighlight everything
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Copy curve
        crv.select = True
        bpy.context.scene.objects.active = crv
        bpy.ops.object.duplicate_move()
        crv_copy = bpy.context.object
        crvs_copy.append(crv_copy)
    return crvs_copy


def get_closest_pt_ind(crv, ctrpt):
# Return index in crv of vertex closest to ctrpt
# todo: it might be better to instead use pctg along original LoBF, find
# corresponding pt on crv's LoBF, then find closest point on crv to this pt

    # add_sphere_at_loc(ctrpt)
    mindist = sys.float_info.max
    min_ind = 0
    for ind, vrt in enumerate(crv.data.vertices):
        this_dist = get_dist(vrt.co, ctrpt)
        if this_dist < mindist:
            mindist = this_dist
            min_ind = ind
            # add_sphere_at_loc(vrt.co)

    # if closest point is the endpoint of the curve, move in by n_off vertices
    # so that there is a non-zero length edge to loft into a surface
    n_off = 1  # any bigger is arbitrary, although perhaps more realistic
    if min_ind == 0:
        min_ind = n_off
        print("warning:  min_ind was 0")
    if min_ind == len(crv.data.vertices) - 1:
        min_ind = len(crv.data.vertices) - n_off - 1
        print("warning:  min_ind was max endpt")
    # add_sphere_at_loc(crv.data.vertices[min_ind].co)

    return min_ind


def construct_sub_crv(crv_to_split, vert_ind, end_to_keep, make_copy=True):
# Copy crv_to_split, keep only vertices from vert_ind to one end
# end_to_keep = 0:  keep 0 to vert_ind
# end_to_keep = 1:  keep vert_ind to end

    # Unhighlight everything
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    # Copy vertices into new curve
    crv_to_split.select = True
    bpy.context.scene.objects.active = crv_to_split
    crv_to_split_new = crv_to_split
    if make_copy:
        bpy.ops.object.duplicate_move()
        crv_to_split_new = bpy.context.object
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # Select vertices to delete
    if end_to_keep == 0:
        nverts = len(crv_to_split_new.data.vertices)
        vert_range_to_del = range(vert_ind+1, nverts)
    else:
        vert_range_to_del = range(0, vert_ind)

    # print(crv_to_split.name, len(crv_to_split_new.data.vertices), vert_ind, end_to_keep)

    # Delete vertices
    for v in vert_range_to_del:
        crv_to_split_new.data.vertices[v].select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    return crv_to_split_new


def get_hole_pctgs(hole_data_layers):
# For each hole, calculate its pctg along the way from endpt1 to endpt2, store as list with entry for each layer
    hole_pctgs = []
    for hd in hole_data_layers:
        e1 = hd[0][0]
        e2 = hd[0][1]
        these_pctgs = []
        for hl in hd[1]:
            d1 = get_dist(hl, e1)
            d2 = get_dist(hl, e2)
            pctg = d1 / (d1 + d2)
            these_pctgs.append(pctg)
        hole_pctgs.append(these_pctgs)
    return hole_pctgs

def combine_hole_data(pctgs1, pctgs2, holedata1, holedata2, delta_p_thresh):  # todo:  check this function
# return sorted list of hole location pctgs [[p, owner]], where owner in {1,2,3=both}
# combining holes that are within delta_p_thresh of each other
    i1 = 0
    i2 = 0
    all_pctgs = []
    while i1 < len(pctgs1) and i2 < len(pctgs2):
        p1 = pctgs1[i1]
        p2 = pctgs2[i2]
        this_d = abs(p1-p2)
        if this_d < delta_p_thresh:  # same hole
            this_min = (p1+p2)/2
            owner = 3
            ctrpt = -1
            i1 += 1
            i2 += 1
        else:
            this_min = min(p1, p2)
            if this_min == p1:
                owner = 1
                ctrpt = holedata1[1][i1]
                i1 += 1
            else:
                owner = 2
                ctrpt = holedata2[1][i2]
                i2 += 1
        all_pctgs.append([this_min, owner, ctrpt])

    if i1 < len(pctgs1):
        for i1a in range(i1, len(pctgs1)):
            all_pctgs.append([pctgs1[i1a], 1, holedata1[1][i1a]])
    if i2 < len(pctgs2):
        for i2a in range(i2, len(pctgs2)):
            all_pctgs.append([pctgs2[i2a], 2, holedata2[1][i2a]])
    return all_pctgs



def get_crv_order(endpts1, endpts2):
# return boolean declaring whether or not the curves have the same orientation
# ie whether the respective endpoints are closer to each other or inversed
    d0_0 = get_dist(endpts1[0], endpts2[0])
    d0_1 = get_dist(endpts1[0], endpts2[1])
    d1_0 = get_dist(endpts1[1], endpts2[0])
    d1_1 = get_dist(endpts1[1], endpts2[1])
    the_min = min(d0_0, d0_1, d1_0, d1_1)
    reverse_order = 0
    if the_min == d0_1 or the_min == d1_0:
        reverse_order = 1
    return reverse_order


#def get_crv_order(self, c_full, c_part1, c_part2):
## determine which of c_part1, c_part2 is closer to c_full[0]:
## if n_prev == 1, project center of mass of crvs[ind] and crvs[ind+1] onto crvs[ind-1]
## to get ordering (min(CoM, endpt of crvs[ind-1]) wins, ordering propegates back)
## also figure out ordering at location above;  return order assignment with p_vals
## as 0=assigned to vertices[0,n], or 1=assigned to vertices[n+1,end]

    #CoM1 = get_CoM(c_part1)
    #CoM2 = get_CoM(c_part2)
    #endpt0 = c_full.data.vertices[0].co
    #endpt1 = c_full.data.vertices[-1].co
    #d1_0 = get_dist(CoM1, endpt0)
    #d1_1 = get_dist(CoM1, endpt1)
    #d2_0 = get_dist(CoM2, endpt0)
    #d2_1 = get_dist(CoM2, endpt1)

    #the_min = min(d1_0, d1_1, d2_0, d2_1)
    #reverse_order = 0
    #if the_min == d1_0:
        #reverse_order = 0
    #elif the_min == d1_1:
        #reverse_order = 1
    #elif the_min == d2_0:
        #reverse_order = 1
    #elif the_min == d2_1:
        #reverse_order = 0

    #if not (d1_0 < d2_0 and d2_1 < d1_1) and not (d2_0 < d1_0 and d1_1 < d2_1):
        #self.report({'INFO'},"Warning: curve ordering possibly unclear! Check results.")

    #return reverse_order


def order_curves(crv_list, orientation):
# crv_list is list of n curves with the same z-value;
# fit line through point cloud of all vertices in all curves in list;
# project center of mass of each curve onto this list for ordering;
# call get_crv_order() above to determine if need to reverse ordering
# for consistency with neighboring curves (outside this function)

    # Generate mesh line of best fit
    npts = 100000  # arbitrary, is for length of whole image, not number returned
    pts_LoBF = get_LineOfBestFit([crv_list], orientation, npts = npts)  #, add_LoBF_to_scene = True)

    # print(pts_LoBF)

    # Find closest vertex on line to center of mass of each curve
    line_indices = []
    for crv in crv_list:
        this_CoM = get_CoM(crv)
        mindist = sys.float_info.max
        min_ind = 0
        for ii, v in enumerate(pts_LoBF):
            this_dist = get_dist(this_CoM, v)
            if this_dist < mindist:
                min_ind = ii
                mindist = this_dist
        line_indices.append(min_ind)

    # Re-order curves to be in above order
    sorted_inds = sorted(line_indices)
    crvs_ordered = []
    for vert_ind in sorted_inds:
        crv_ind = line_indices.index(vert_ind)
        crvs_ordered.append(crv_list[crv_ind])

    # Find center of holes along line, return this value as a percentage
    # of the way along the line, to determine the closest point on
    # next/prev curve where surfaces should meet
    # ctr_pt_ps = []
    # for hole_id in range(len(crvs_ordered)-1):
    #     crvL = crvs_ordered[hole_id]
    #     crvR = crvs_ordered[hole_id+1]
    #     L_ind, R_ind = get_closest_endpts(crvL, crvR)
    #     Lpt = crvL.data.vertices[L_ind].co
    #     Rpt = crvR.data.vertices[R_ind].co

    #     mindistL = sys.float_info.max
    #     min_indL = 0
    #     mindistR = sys.float_info.max
    #     min_indR = 0
    #     for ii, v in enumerate(pts_LoBF):
    #         this_distL = get_dist(Lpt, v)
    #         this_distR = get_dist(Rpt, v)
    #         if this_distL < mindistL:
    #             min_indL = ii
    #             mindistL = this_distL
    #         if this_distR < mindistR:
    #             min_indR = ii
    #             mindistR = this_distR
    #     ctr_pt_ps.append(abs(min_indL - min_indR)/2 / npts)

    # Find center of each hole = average of the endpoints that define the hole
    ctr_pts = []
    for hole_id in range(len(crvs_ordered)-1):
        crvL = crvs_ordered[hole_id]
        crvR = crvs_ordered[hole_id+1]
        L_ind, R_ind = get_closest_endpts(crvL, crvR)
        Lpt = crvL.data.vertices[L_ind].co
        Rpt = crvR.data.vertices[R_ind].co
        cpt = (Lpt + Rpt) / 2
        ctr_pts.append(cpt)

    # for debugging
    add_ctrpts_to_scene = False
    if add_ctrpts_to_scene:
        me2 = bpy.data.meshes.new("ctrpt_mesh")
        ob2 = bpy.data.objects.new("ctrpt_mesh", me2)
        bpy.context.scene.objects.link(ob2)
        me2.from_pydata(ctr_pts,[],[])

    # Also return endpoints of line of best fit
    #endpts = [pts_LoBF[0], pts_LoBF[-1]]

    # Also return extreme endpoints of curve collection
    crvL = crvs_ordered[0]
    crvR = crvs_ordered[-1]
    [L_ind, R_ind] = get_closest_endpts(crvL, crvR)
    Lpt = crvL.data.vertices[-1-L_ind].co  # this assumes not too much curvature
    Rpt = crvR.data.vertices[-1-R_ind].co
    endpts = [Lpt, Rpt]

    return crvs_ordered, ctr_pts, endpts


# def crv_collection_endpts(crvs_ordered):
# # Return extreme endpoints of curve collection
#     crvL = crvs_ordered[0]
#     crvR = crvs_ordered[-1]
#     [L_ind, R_ind] = get_closest_endpts(crvL, crvR)
#     Lpt = crvL.data.vertices[-1-L_ind].co  # this assumes not too much curvature
#     Rpt = crvR.data.vertices[-1-R_ind].co
#     endpts = [Lpt, Rpt]
#     return endpts



class CloseOpenTube(bpy.types.Operator):
    """Close ends of selected open tubular surface"""
    bl_idname = "object.close_tube"
    bl_label = "Close ends of selected open tubular surface"

    def execute(self, context):
        mesh = bpy.context.object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class LineOfBestFit_button(bpy.types.Operator):
    """Create line of best fit in z-dimension through list of curves"""
    bl_idname = "object.line_of_best_fit"
    bl_label = "Create line of best fit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        objs = bpy.context.scene.objects
        crvs = [[]]
        ind = -1
        last_z = -100
        N = len(bpy.context.scene.imagefilepaths_z)
        delta_z = bpy.context.scene.z_side / N / 2
        for obj in objs:
        #for ind, obj in enumerate(objs):
            if obj.select and hasattr(obj, 'data'):
                if abs(obj.data.vertices[0].co[2] - last_z) > delta_z:
                    if ind != -1:
                        crvs.append([])
                    last_z = obj.data.vertices[0].co[2]
                    ind += 1
                crvs[ind].append(obj)
        add_LoBF_to_scene = True
        get_LineOfBestFit(crvs, "Z", add_LoBF_to_scene = True)
        return {'FINISHED'}


#def get_LineOfBestFit_old(crv_list, npts = 2000, add_LoBF_to_scene = False):
    #return get_LineOfBestFit_1(crv_list, npts, add_LoBF_to_scene)
    #return get_LineOfBestFit_2(crv_list, npts, add_LoBF_to_scene)

def get_LineOfBestFit(crv_list, orientation, npts = 5000, add_LoBF_to_scene = False):
    # here crv_list is a list of lists
    return get_LineOfBestFit_3(crv_list, npts, add_LoBF_to_scene, orientation)

# PROBLEM:  traditional LoBF isn't good.
# CURRENT SOLUTION:  use line connecting outer endpoints of layer
# A more robust option: get plane of best fit via PCA or LDA, project pts into this plane
# then find maximum margin hyperplane intersection with this plane
# PCA vs LDA in python:  http://scikit-learn.org/stable/auto_examples/decomposition/plot_pca_vs_lda.html


# def get_LineOfBestFit_1(crv_list, npts, add_LoBF_to_scene):
#     """ return a discrete mesh line of best fit through all points in crv_list
#     where all curves are assumed to have the same z-value, 
#     or the first n crvs have the same z-value and the rest have a second z-value;
#     npts is the number of points in the mesh curve when it is the 
#     length of the image (output mesh curve will contain fewer) """

#     # Assign line to average z value
#     z1 = crv_list[0].data.vertices[0].co[2]
#     z2 = crv_list[-1].data.vertices[0].co[2]
#     z = (z1+z2)/2

#     # Process in 2D
#     xs = []
#     ys = []
#     for crv in crv_list:
#         these_xs = [pt.co[0] for pt in crv.data.vertices]
#         these_ys = [pt.co[1] for pt in crv.data.vertices]
#         xs = xs + these_xs
#         ys = ys + these_ys

#     # xmin = min(xs)
#     # xmax = max(xs)
#     # ymin = min(ys)
#     # ymax = max(ys)
#     # pts_LoBF = LoBF_code(xs, ys, z, xmin, xmax, ymin, ymax, npts, add_LoBF_to_scene)
#     pts_LoBF = LoBF_code(xs, ys, z, npts, add_LoBF_to_scene)
#     return pts_LoBF


# def get_LineOfBestFit_2(crv_list, npts, add_LoBF_to_scene):
# # just connect endpoints of far ends of lines, assumes crv_list is ordered
# # consider averaging the 5 endpoints to define each "endpoint", 
# # although single point is still globally valid, so maybe don't bother;
# # This function only works for a single layer.

#     crvL = crv_list[0]
#     crvR = crv_list[-1]
#     [L_ind, R_ind] = get_closest_endpts(crvL, crvR)

#     #inds = [range(0,5), range(-5,0)]
#     #Linds = inds[-1-L_ind]
#     #Rinds = inds[-1-R_ind]
#     #Lpts = [crvL.data.vertices[n].co for n in Linds]
#     #Rpts = [crvR.data.vertices[n].co for n in Rinds]
#     #L_end = np.mean(Lpts, 0)
#     #R_end = np.mean(Rpts, 0)
#     ######## the above doesn't work, the below does

#     L_end = crvL.data.vertices[-1-L_ind].co
#     R_end = crvR.data.vertices[-1-R_ind].co
#     xs = [L_end[0], R_end[0]]
#     ys = [L_end[1], R_end[1]]
#     z = (L_end[2] + R_end[2]) / 2
#     # xs_full = [pt.co[0] for pt in crvL.data.vertices] + [pt.co[0] for pt in crvR.data.vertices]
#     # ys_full = [pt.co[1] for pt in crvL.data.vertices] + [pt.co[1] for pt in crvR.data.vertices]
#     # xmin = min(xs_full)
#     # xmax = max(xs_full)
#     # ymin = min(ys_full)
#     # ymax = max(ys_full)
#     # pts_LoBF = LoBF_code(xs, ys, z, xmin, xmax, ymin, ymax, npts, add_LoBF_to_scene)
#     pts_LoBF = LoBF_code(xs, ys, z, npts, add_LoBF_to_scene)
#     return pts_LoBF
#     #[L_ind, R_ind] = [-1,0]


def get_LineOfBestFit_3(crv_list, npts, add_LoBF_to_scene, orientation):
# connect endpoints of far ends of lines, 
# assumes crv_list is list of lists, with each list ordered internally
# if curves are from two different layers, each layer is a different list, 
# in this case, get endpts from each layer separately,
# then average the closest endpts for mean endpts, to create full line
# if only one layer, then is a list of one list

    if orientation == "Z":
        x_ind = 0; y_ind = 1; z_ind = 2
    elif orientation == "Y":
        x_ind = 0; y_ind = 2; z_ind = 1
    elif orientation == "X":
        x_ind = 1; y_ind = 2; z_ind = 0

    if len(crv_list) == 2:  # curves from two different layers, assumes sorted per layer
        crvL_a = crv_list[0][0]  # layer a
        crvR_a = crv_list[0][-1]
        crvL_b = crv_list[1][0]  # layer b
        crvR_b = crv_list[1][-1]

        [L_ind_a, R_ind_a] = get_closest_endpts(crvL_a, crvR_a)  # if crvL == crvR, return both endpts
        L_end_a = crvL_a.data.vertices[-1-L_ind_a].co
        R_end_a = crvR_a.data.vertices[-1-R_ind_a].co  # these are the same

        [L_ind_b, R_ind_b] = get_closest_endpts(crvL_b, crvR_b)
        L_end_b = crvL_b.data.vertices[-1-L_ind_b].co
        R_end_b = crvR_b.data.vertices[-1-R_ind_b].co

        # determine which endpts correspond
        crv_a_ind, crv_b_ind = get_closest_endpts_from_pts(L_end_a, R_end_a, L_end_b, R_end_b)

        layer_a_0 = L_end_a
        layer_a_1 = R_end_a
        if crv_a_ind == -1:  # reverse ordering
            layer_a_0 = R_end_a
            layer_a_1 = L_end_a
        layer_b_0 = L_end_b
        layer_b_1 = R_end_b
        if crv_b_ind == -1:  # reverse ordering
            layer_b_0 = R_end_b
            layer_b_1 = L_end_b

        # take average of endpts for final line construction
        mid_L = (layer_a_0 + layer_b_0) / 2
        mid_R = (layer_a_1 + layer_b_1) / 2
        xs = [mid_L[x_ind], mid_R[x_ind]]
        ys = [mid_L[y_ind], mid_R[y_ind]]
        z = (mid_L[z_ind] + mid_R[z_ind]) / 2
        pts_LoBF = LoBF_code(xs, ys, z, npts, add_LoBF_to_scene, orientation)
    
    elif len(crv_list) == 1:  # curves all from same layer, cannot assume curves are sorted
        [L_end, R_end] = find_furthest_endpts(crv_list[0])  # todo: check this
        xs = [L_end[x_ind], R_end[x_ind]]
        ys = [L_end[y_ind], R_end[y_ind]]
        z = (L_end[z_ind] + R_end[z_ind]) / 2
        pts_LoBF = LoBF_code(xs, ys, z, npts, add_LoBF_to_scene, orientation)

    else:
        print("No LoBF implemented for points from > 2 layers!")
        return []

    return pts_LoBF
    # todo:  check this function

   

    # xs = [L_end[0], R_end[0]]
    # ys = [L_end[1], R_end[1]]
    # z = (L_end[2] + R_end[2]) / 2
    # # xs_full = [pt.co[0] for pt in crvL.data.vertices] + [pt.co[0] for pt in crvR.data.vertices]
    # # ys_full = [pt.co[1] for pt in crvL.data.vertices] + [pt.co[1] for pt in crvR.data.vertices]
    # # xmin = min(xs_full)
    # # xmax = max(xs_full)
    # # ymin = min(ys_full)
    # # ymax = max(ys_full)
    # # pts_LoBF = LoBF_code(xs, ys, z, xmin, xmax, ymin, ymax, npts, add_LoBF_to_scene)
    # pts_LoBF = LoBF_code(xs, ys, z, npts, add_LoBF_to_scene)
    # return pts_LoBF
    # #[L_ind, R_ind] = [-1,0]


def find_furthest_endpts(crv_list):  # todo:  check this!
    p1 = crv_list[0].data.vertices[0].co
    p2 = p1
    max_dist = 0
    for c1 in crv_list:
      for e1 in [0,-1]:
        for c2 in crv_list:
          for e2 in [0,-1]:
            this_dist = get_dist(c1.data.vertices[e1].co, c2.data.vertices[e2].co)
            if this_dist > max_dist:
                max_dist = this_dist
                p1 = c1.data.vertices[e1].co
                p2 = c2.data.vertices[e2].co
    return([p1,p2])



# def LoBF_code(xs, ys, z, xmin, xmax, ymin, ymax, npts, add_LoBF_to_scene):
def LoBF_code(xs, ys, z, npts, add_LoBF_to_scene, orientation):

    # # Fit line of best fit (LoBF) through points
    # LoBF = np.poly1d(np.polyfit(np.array(xs), np.array(ys), 1))  # returns a continutous curve (-inf,inf)
    # # Sample the curve to generate discrete mesh
    # xmin_im = 0
    # xmax_im = bpy.context.scene.x_side
    # xs_line = xmin_im + (xmax_im - xmin_im)/npts * np.array(range(npts))
    # ys_line = LoBF(xs_line)
    # pts_LoBF = [[x,y,z] for [x,y] in zip(xs_line, ys_line)]

    # Generate discrete values to sample the curve to generate discrete mesh
    max_side = max(bpy.context.scene.x_side, bpy.context.scene.y_side, bpy.context.scene.z_side)
    xs_line = max_side/npts * np.array(range(npts))

    if orientation == "Z":
        x_ind = 0; y_ind = 1; z_ind = 2
        LoBF = np.poly1d(np.polyfit(np.array(xs), np.array(ys), 1))  # returns a continutous curve (-inf,inf)
        ys_line = LoBF(xs_line)
        pts_LoBF = [[x,y,z] for [x,y] in zip(xs_line, ys_line)]
    elif orientation == "Y":
        x_ind = 0; y_ind = 2; z_ind = 1
        LoBF = np.poly1d(np.polyfit(np.array(xs), 1, np.array(ys)))
        ys_line = LoBF(xs_line)
        pts_LoBF = [[x,z,y] for [x,y] in zip(xs_line, ys_line)]
    elif orientation == "X":
        x_ind = 1; y_ind = 2; z_ind = 0
        LoBF = np.poly1d(1, np.polyfit(np.array(xs), np.array(ys)))
        ys_line = LoBF(xs_line)
        pts_LoBF = [[z,x,y] for [x,y] in zip(xs_line, ys_line)]

    # Crop at bounding box
    xmin = min(xs)
    xmax = max(xs)
    ymin = min(ys)
    ymax = max(ys)
    subpts = []
    subpt_inds = []
    for ii, pt in enumerate(pts_LoBF):
        if (pt[x_ind] >= xmin and pt[x_ind] <= xmax) or (pt[y_ind] >= ymin and pt[y_ind] <= ymax):
            subpts.append(pt)
            subpt_inds.append(ii)

    # add extra points on each end, so that line is longer than curves
    n_to_add = 100  # arbitrary
    min_ind = min(subpt_inds)
    max_ind = max(subpt_inds)
    for n in range(n_to_add):
        ind_down = min_ind - n
        ind_up = max_ind + n
        if ind_down >= 0:
            subpts.append(pts_LoBF[ind_down])
        if ind_up <= len(pts_LoBF):
            subpts.append(pts_LoBF[ind_up])

    pts_LoBF = subpts

    # for debugging
    if add_LoBF_to_scene:
        me = bpy.data.meshes.new("LoBF_mesh")
        ob = bpy.data.objects.new("LoBF_mesh", me)
        bpy.context.scene.objects.link(ob)
        edges = []
        for n in range(len(pts_LoBF)-1):
            edges.append([n,n+1])
        me.from_pydata(pts_LoBF,edges,[])

    return pts_LoBF


# def get_closest_vertex(mesh, pt):
# # return index of closest mesh vertex to pt (brute force search; kd-tree not appropriate here)
# # mesh = bpy.context.object.data
#     verts = mesh.vertices
#     pt_vec = Vector(pt)
#     distances = [(v.co - pt_vec).length for v in verts]
#     val, ind = min((val, idx) for (idx, val) in enumerate(distances))
#     return ind


def get_dist(coord1, coord2):
    d = math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2 + \
        (coord1[2] - coord2[2])**2)
    return d

def get_CoM(crv):
# returns the center of mass of a mesh object
    pt_sum = Vector((0,0,0))
    for pt in crv.data.vertices:
        pt_sum += pt.co
    CoM = pt_sum / len(crv.data.vertices)
    return CoM

def get_closest_endpts(crvL, crvR):
# return indices of closest endpoints of the two curves
# if crvL == crvR, return the two distinct endpts

    if crvL == crvR:
      return 0,-1

    L1 = crvL.data.vertices[0].co
    L2 = crvL.data.vertices[-1].co
    R1 = crvR.data.vertices[0].co
    R2 = crvR.data.vertices[-1].co
    return get_closest_endpts_from_pts(L1, L2, R1, R2)


def get_closest_endpts_from_pts(L1, L2, R1, R2):
# warning:  possible bad results when single endpt of one curve
#           is the closest to both points on second curve
    dL1R1 = get_dist(L1, R1)
    dL1R2 = get_dist(L1, R2)
    dL2R1 = get_dist(L2, R1)
    dL2R2 = get_dist(L2, R2)
    the_min = min([dL1R1, dL1R2, dL2R1, dL2R2])
    if the_min == dL1R1:
        return 0,0
    elif the_min == dL1R2:
        return 0,-1
    elif the_min == dL2R1:
        return -1,0
    elif the_min == dL2R2:
        return -1,-1
    else:
        print("no matching min!")
        return 0,0



def register():
    bpy.utils.register_module(__name__)
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    kmi = km.keymap_items.new(ImageScrollOperator.bl_idname, 'X', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new(AddSphere.bl_idname, 'M', 'PRESS', alt=True)
    kmi = km.keymap_items.new(DrawCurve.bl_idname, 'D', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new(EraseCurve.bl_idname, 'E', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new(ConvertCurve.bl_idname, 'D', 'PRESS', ctrl=True, shift=True)

    # change color of wire mesh line for better visibility on image
    bpy.context.user_preferences.themes[0].view_3d.wire = (0.0, 1.0, 1.0)

    # # test using macros for grease pencil release
    # OperatorAfterGreasePencilMacro.define("OBJECT_OT_draw_curve")
    # OperatorAfterGreasePencilMacro.define("OBJECT_OT_convert_curve")

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
        name = "Source-Z",
        description = "Select location of the Z stack images (original image stack)",
        default = "/"
    )
    bpy.types.Scene.image_path_X = bpy.props.StringProperty \
    (
        name = "(Source-X)",
        description = "Select location of the X stack images (OPTIONAL)",
        default = "/"
    )
    bpy.types.Scene.image_path_Y = bpy.props.StringProperty \
    (
        name="(Source-Y)",
        description="Select location of the Y stack images (OPTIONAL)",
        default="/"
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
    bpy.types.Scene.imagefilepaths_z = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.imagefilepaths_x = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.imagefilepaths_y = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    bpy.types.Scene.shift_step = bpy.props.IntProperty \
    (
        name="Shift step",
        description="Step size for scrolling through image stack while holding shift",
        default=10
    )
    bpy.types.Scene.pt_radius = bpy.props.FloatProperty \
    (
        name = "marker radius (microns)",
        description = "Radius of sphere marking point location (microns)",
        default = 0.01,
        min = 10**-20,
    )
    bpy.types.Scene.scene_precision = bpy.props.IntProperty \
    (
        name = "drawing precision",
        description = "Adjust number of points to use when creating curves and surfaces (points per image length, eg 500)",
        default = 500,
        min = 10,
        max = 1000000,
    )
    bpy.types.Scene.coarse_marker = bpy.props.BoolProperty \
    (
        name = "Coarse Markers",
        description = "Create marker spheres with fewer vertices, keep checked if using scene with many markers",
        default = True
    )
    bpy.types.Scene.center_view = bpy.props.BoolProperty \
    (
        name = "Center to Image",
        description = "Center view to image each time a new image is added",
        default = True
    )
    bpy.types.Scene.closed_curve = bpy.props.BoolProperty \
    (
        name = "Closed Curve",
        description = "Check if curve is closed (for making tubes), leave unchecked if curve is open (for making surfaces)",
        default = False
    )
    bpy.types.Scene.convert_curve_on_release = bpy.props.BoolProperty \
    (
        name = "Convert Curve on Release",
        description = "Convert grease pencil drawing to mesh curve immediately on mouse release",
        default = True
    )

    bpy.types.Scene.marker_prefix = StringProperty(name = "Marker Prefix", default="marker")
    bpy.types.Scene.surface_prefix = StringProperty(name = "Surface Prefix", default="surface")

    bpy.types.Object.image_from_stack_notation = bpy.props.BoolProperty \
    (
        name = "Image created from Stack Notation tool", 
        description = "This tool was only relevant when images could also be created in other tools",
        default=False
    )
    bpy.types.Scene.render_images = bpy.props.BoolProperty \
    (
        name="Include images in render",
        description="Must be checked to have images rendered as visible textured planes in an animation",
        default=False,
        update=update_render_images
    )


def unregister():
    
    del bpy.types.Scene.render_images
    del bpy.types.Object.image_from_stack_notation
    del bpy.types.Scene.surface_prefix
    del bpy.types.Scene.marker_prefix
    del bpy.types.Scene.convert_curve_on_release
    del bpy.types.Scene.closed_curve
    del bpy.types.Scene.center_view
    del bpy.types.Scene.coarse_marker
    del bpy.types.Scene.scene_precision
    del bpy.types.Scene.pt_radius
    del bpy.types.Scene.shift_step
    del bpy.types.Scene.imagefilepaths_y
    del bpy.types.Scene.imagefilepaths_x
    del bpy.types.Scene.imagefilepaths_z
    del bpy.types.Scene.file_min_Y
    del bpy.types.Scene.file_min_X
    del bpy.types.Scene.file_min_Z
    del bpy.types.Scene.image_path_Y
    del bpy.types.Scene.image_path_X
    del bpy.types.Scene.image_path_Z
    del bpy.types.Scene.image_ext_Y
    del bpy.types.Scene.image_ext_X
    del bpy.types.Scene.image_ext_Z
    del bpy.types.Scene.z_side
    del bpy.types.Scene.y_side
    del bpy.types.Scene.x_side

    bpy.app.handlers.scene_update_post.remove(print_updated_objects)
    bpy.app.handlers.frame_change_post.remove(set_image_for_frame)
    bpy.app.handlers.load_post.remove(setLightLoad)
    # bpy.app.handlers.scene_update_post.remove(setLight)  # ???? why didn't this exist?

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()

