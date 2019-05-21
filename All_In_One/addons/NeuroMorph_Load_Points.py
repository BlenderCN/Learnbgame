#    NeuroMorph_Load_Points.py (C) 2017,  Anne Jorstad
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
    "name": "NeuroMorph Load Points",
    "author": "Anne Jorstad",
    "version": (1, 0, 0),
    "blender": (2, 7, 9),
    "location": "View3D > NeuroMorph > Load Points",
    "description": "Load points with 3D coordinates from a Fiji XML file",
    "warning": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Learnbgame"
}  
  
import bpy
from bpy.props import *
from mathutils import Vector  
import mathutils
import math
import os
import sys
import re
from os import listdir
import copy
import numpy as np  # must have Blender > 2.7
import csv
import xml.etree.ElementTree as ET
import datetime


# Define the panel
class LoadPointsPanel(bpy.types.Panel):
    bl_label = "Load Points"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):

        self.layout.label("Image Stack Dimensions (microns):")
        row = self.layout.row()
        row.prop(context.scene , "x_microns")
        row.prop(context.scene , "y_microns")
        row.prop(context.scene , "z_microns")

        self.layout.label("Image Stack Dimensions (pixels):")
        row = self.layout.row()
        row.prop(context.scene , "x_pixels")
        row.prop(context.scene , "y_pixels")
        row.prop(context.scene , "z_pixels")

        row = self.layout.row()
        row.prop(context.scene, "pt_name")

        row = self.layout.row()
        row.operator("object.load_points", text='Load Points from XML', icon='FILESEL')  #, icon='MOD_CURVE')

        split = self.layout.row().split(percentage=0.1)
        colL = split.column()
        colR = split.column()
        colR.prop(context.scene, "ball_radius")

        split = self.layout.row().split(percentage=0.1)
        colL = split.column()
        colR = split.column()        
        colR.prop(context.scene , "coarse_sphere")

        row = self.layout.row()
        row.operator("object.pts2balls", text='Convert Points to Balls', icon='MESH_UVSPHERE')



class LoadPoints(bpy.types.Operator):
    """Load points with 3D coordinates from a Fiji XML file"""
    bl_idname = "object.load_points"
    bl_label = "Load points with 3D coordinates from a Fiji XML file"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        # activate_an_object()
        # bpy.ops.object.mode_set(mode='OBJECT')  # else is error at end

        this_filename = self.directory + self.filename

        # Load point data into mesh object
        pts = read_xml_points(this_filename)

        # Scale points
        x_scl = bpy.context.scene.x_microns / bpy.context.scene.x_pixels
        y_scl = bpy.context.scene.y_microns / bpy.context.scene.y_pixels
        z_scl = bpy.context.scene.z_microns / bpy.context.scene.z_pixels
        ave_scl = (x_scl + y_scl + z_scl) / 3  # only used for ball radius
        bpy.context.scene.ball_radius *= ave_scl

        # scl_ext = [.877, .967, 1.33]
        scl_ext = [1,1,1]
        x_scl *= scl_ext[0]
        y_scl *= scl_ext[1]
        z_scl *= scl_ext[2]

        pts_scaled = []
        for pt in pts:
            pt_sc = [pt[0]*x_scl, pt[1]*y_scl, pt[2]*z_scl]
            pts_scaled.append(pt_sc)

        # Create mesh object for each point
        make_mesh_points(pts_scaled)

        return {'FINISHED'}



# Read 3D points from XML file
def read_xml_points(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    # Get offset from transform matrix [1,0,0,1, x_off, y_off]
    ball_root = [elt for elt in root.findall('.//t2_ball')][0]
    trans_mat_str = ball_root.attrib['transform'][7:-1]  # Remove "matrix()" text
    trans_mat = trans_mat_str.split(',')
    x_off = float(trans_mat[4])
    y_off = float(trans_mat[5])

    # # width and height in t2_ball are this much greater than true bounding box in both x and y
    # other_off = 9.244877324554409
    # x_off += other_off
    # y_off += other_off

    # Loop through balls
    balls = [elt for elt in root.findall('.//t2_ball_ob')]

    rad = float(balls[0].attrib['r'])
    bpy.context.scene.ball_radius = rad

    # minx = 1000
    # maxx = -1000
    # miny = 1000
    # maxy = -1000

    pts = []
    for ball in balls:
        pts.append([float(ball.attrib['x'])+x_off, float(ball.attrib['y'])+y_off, float(ball.attrib['layer_id'])])

    #     pt = [float(ball.attrib['x']), float(ball.attrib['y'])]
    #     if pt[0] < minx:
    #         minx = pt[0]
    #     if pt[0] > maxx:
    #         maxx = pt[0]
    #     if pt[1] < miny:
    #         miny = pt[1]
    #     if pt[1] > maxy:
    #         maxy = pt[1]
    # print(minx, maxx, miny, maxy)


    return(pts)



# Create mesh object for each point
def make_mesh_points(pts):
    this_name = bpy.context.scene.pt_name

    parent_name = this_name + "_parent"
    parent_ob = bpy.data.objects.new(parent_name, None)
    bpy.context.scene.objects.link(parent_ob)

    for pt in pts:
        me = bpy.data.meshes.new(this_name)
        vscl_pt_ob = bpy.data.objects.new(this_name, me)
        bpy.context.scene.objects.link(vscl_pt_ob)
        me.from_pydata([pt], [], [])
        me.update()
        vscl_pt_ob.parent = parent_ob

    # Hide dotted line between parent and child objects
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].show_relationship_lines = False

    # Return new points as selected
    children = [ob for ob in bpy.context.scene.objects if ob.parent == parent_ob]
    bpy.ops.object.select_all(action='DESELECT')
    for ob in children:
        ob.select = True



class Pts2Balls(bpy.types.Operator):
    """Convert selected points to 3D balls"""
    bl_idname = "object.pts2balls"
    bl_label = "Convert selected points to 3D balls with defined radius"


    def execute(self, context):
        pts = [ob for ob in bpy.context.scene.objects if ob.select == True]
        rad = bpy.context.scene.ball_radius

        if bpy.context.scene.coarse_sphere:
            segs = 5
            rings = 4
        else:
            segs = 32
            rings = 16

        for pt in pts:
            vert = pt.data.vertices[0].co
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_uv_sphere_add(location = vert, size = rad, segments=segs, ring_count=rings)
            ball = bpy.context.object
            ball.parent = pt.parent

            # Delete pt object
            this_name = pt.name
            bpy.ops.object.select_all(action='DESELECT')
            pt.select = True
            bpy.ops.object.delete()

            # Give sphere same name as point
            ball.name = this_name

        return {'FINISHED'}




if __name__ == "__main__":
    register()

def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.x_microns = bpy.props.FloatProperty \
    (
        name = "x",
        description = "x-dimension of image stack (microns)",
        default = 1
    )
    bpy.types.Scene.y_microns = bpy.props.FloatProperty \
    (
        name = "y",
        description = "y-dimension of image stack (microns)",
        default = 1
    )
    bpy.types.Scene.z_microns = bpy.props.FloatProperty \
    (
        name = "z",
        description = "z-dimension of image stack (microns)",
        default = 1
    )

    bpy.types.Scene.x_pixels = bpy.props.FloatProperty \
    (
        name = "x",
        description = "x-dimension of image stack (pixels)",
        default = 1
    )
    bpy.types.Scene.y_pixels = bpy.props.FloatProperty \
    (
        name = "y",
        description = "y-dimension of image stack (pixels)",
        default = 1
    )
    bpy.types.Scene.z_pixels = bpy.props.FloatProperty \
    (
        name = "z",
        description = "z-dimension of image stack (pixels)",
        default = 1
    )

    bpy.types.Scene.pt_name = bpy.props.StringProperty \
    (
        name="Point Obj Name",
        description = "Name given to 3D point objects being loaded", 
        default="vesicle"
    )

    bpy.types.Scene.ball_radius = bpy.props.FloatProperty \
    (
        name="Ball Radius",
        description = "Radius to use when converting points to balls (registers radius from XML file if available)", 
        default=0.01
    )

    bpy.types.Scene.coarse_sphere = bpy.props.BoolProperty \
    (
        name = "Coarse Balls",
        description = "Create coarse balls with fewer vertices, keep checked if using scene with many balls",
        default = True
    )




def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.coarse_sphere
    del bpy.types.Scene.ball_radius
    del bpy.types.Scene.pt_name
    del bpy.types.Scene.z_pixels
    del bpy.types.Scene.y_pixels
    del bpy.types.Scene.x_pixels
    del bpy.types.Scene.z_microns
    del bpy.types.Scene.y_microns
    del bpy.types.Scene.x_microns
