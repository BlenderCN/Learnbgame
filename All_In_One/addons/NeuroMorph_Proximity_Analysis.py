#    NeuroMorph_Proximity_Analysis.py (C) 2015,  Anne Jorstad
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
    "name": "NeuroMorph Proximity Analysis",
    "author": "Anne Jorstad",
    "version": (1, 0, 1),
    "blender": (2, 7, 7),
    "location": "View3D > Proximity Analysis",
    "description": "Calculate regions of surface within a given distance of each other",
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

# breakpoint = bpy.types.bp.bp
# # breakpoint(locals(), True, False)

import datetime


# Define the panel
class ProximityAnalysisPanel(bpy.types.Panel):
    bl_label = "Proximity Analysis"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):

        row = self.layout.row()
        row.operator("object.set_ob1", text='Set Object 1')
        self.layout.label("Obj. 1:  " + bpy.context.scene.name1)
        row = self.layout.row()
        row.operator("object.set_ob2", text='Set Object 2')
        self.layout.label("Obj. 2:  " + bpy.context.scene.name2)

        row = self.layout.row()
        row.prop(context.scene , "dist_thresh")

        row = self.layout.row(align=True)
        row.prop(context.scene, "filename")
        row.operator("file.set_filename", text='', icon='FILESEL')

        row = self.layout.row()
        row.operator("object.get_distances", text='Compute Interactions', icon='ARROW_LEFTRIGHT')  # 'ARROW_LEFTRIGHT', 'MESH_DATA'



        self.layout.label("----- Sphere to Surface Distances -----")

        row = self.layout.row()
        row.operator("object.reduce_spheres", text='Reduce Spheres to Points')

        row = self.layout.row(align=True)
        row.prop(context.scene, "filename2")
        row.operator("file.set_filename2", text='', icon='FILESEL')

        row = self.layout.row()
        row.operator("object.get_distances2", text='Calculate Distances to Active Object')




        # self.layout.label("----------- for debugging -----------")
        # split = self.layout.row().split(percentage=0.5)
        # col1 = split.column()
        # col1.operator("object.set_pt1", text='Set Pt 1')
        # col2 = split.column()
        # col2.operator("object.set_pt2", text='Set Pt 2')
        # row = self.layout.row()
        # row.operator("object.get_dist_2pts", text='Get Dist 2 pts')

# # For debugging
# bpy.types.Scene.pt1 = bpy.props.FloatVectorProperty(name="pt1", description="asdf", default = Vector([1,0,0]))
# bpy.types.Scene.pt2 = bpy.props.FloatVectorProperty(name="pt2", description="asdf", default = Vector([1,0,0]))
# class SetPt1(bpy.types.Operator):
#     """Set point 1 for single distance calculation"""
#     bl_idname = "object.set_pt1"
#     bl_label = "set_pt1"
#     def execute(self, context):
#         bpy.ops.object.mode_set(mode='OBJECT')
#         pt1 = [p.co for p in bpy.context.object.data.vertices if p.select == True]
#         bpy.context.scene.pt1 = pt1[0]
#         bpy.ops.object.mode_set(mode='EDIT')
#         return {'FINISHED'}
# class SetPt2(bpy.types.Operator):
#     """Set point 2 for single distance calculation"""
#     bl_idname = "object.set_pt2"
#     bl_label = "set_pt2"
#     def execute(self, context):
#         bpy.ops.object.mode_set(mode='OBJECT')
#         pt2 = [p.co for p in bpy.context.object.data.vertices if p.select == True]
#         bpy.context.scene.pt2 = pt2[0]
#         bpy.ops.object.mode_set(mode='EDIT')
#         return {'FINISHED'}
# class GetDist_2pts(bpy.types.Operator):
#     """Print the distance between the two selected points on the command line."""
#     bl_idname = "object.get_dist_2pts"
#     bl_label = "Print the distance between the two selected points on the command line."
#     def execute(self, context):
#         d = get_dist(bpy.context.scene.pt1, bpy.context.scene.pt2)
#         print("distance = ", d)
#         return {'FINISHED'}


# Define file name and path for export
class DefineFile(bpy.types.Operator):
    """Define file name and path for distance measurement export"""
    bl_idname = "file.set_filename"
    bl_label = "Define file path and name"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")

    def execute(self, context):
        directory = self.directory
        filename = self.filename
        fname = filename + '.csv'
        full_filename = os.path.join(directory, fname)
        bpy.context.scene.filename = full_filename
        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


# Set the active object to be one of the chosen objects for computation
class SetObject1(bpy.types.Operator):
    """Set Object 1 to active object"""
    bl_idname = "object.set_ob1"
    bl_label = "Set Object 1 to active object"

    def execute(self, context):
        bpy.context.scene.name1 = bpy.context.object.name
        return {'FINISHED'}

class SetObject2(bpy.types.Operator):
    """Set Object 2 to active object"""
    bl_idname = "object.set_ob2"
    bl_label = "Set Object 2 to active object"

    def execute(self, context):
        bpy.context.scene.name2 = bpy.context.object.name
        return {'FINISHED'}



# Outer function organizing everything
class CalculateDistances(bpy.types.Operator):
    """Find all regions less than the threshold distance between the two defined objects"""
    bl_idname = "object.get_distances"
    bl_label = "Find all regions less than the threshold distance between the two defined objects"
    
    def execute(self, context):
        # Assumes all relevant objects are joined into a single object of each type

        t1 = datetime.datetime.now()
        bad_count = 0

        objs_start = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH']
        
        ob1 = bpy.data.objects[bpy.context.scene.name1]
        ob2 = bpy.data.objects[bpy.context.scene.name2]
        thresh = bpy.context.scene.dist_thresh

        if ob1 == ob2 or ob1.type != 'MESH' or ob2.type != 'MESH':
            self.report({'INFO'}, "Please select two distinct objects for processing.")
            return {'FINISHED'}

        # Convert to global coordinates (local coords are lost)
        for ob in [ob1, ob2]:
            bpy.context.scene.objects.active = ob
            ob.select = True  # necessary
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            # # to handle quads, add vertex in center of each quad, triangulate
            # bpy.ops.object.mode_set(mode='EDIT')
            # bpy.ops.mesh.select_all(action='SELECT')
            # bpy.ops.mesh.poke()
            # bpy.ops.object.mode_set(mode='OBJECT')

        # Get vertices on each obj that are within dist thresh from the other obj
        verts1, verts2 = get_close_verts(ob1, ob2, thresh)
        if len(verts1) == 0:
            self.report({'INFO'}, "No vertices less than Max Distance found between the selected objects.")
            return {'FINISHED'}

        # Extract contiguous regions from each object
        discontiguous_pairs = []
        make_child = True
        ob1_regions = separate_distinct_regions(ob1, verts1, make_child)
        print("# initial regions of ob1:", len(ob1_regions))

        for ob1_reg in ob1_regions:
            # get proximate verts on ob2
            print("Processing ", ob1_reg.name)
            handled1 = handle_subregion(ob1_reg, verts2, thresh, ob2, make_child, ob1, ob2, discontiguous_pairs, False)
            if not handled1[0]:
                # ob1_reg must be split into sub-regions for each corresponding ob2_regs_here
                ob2_regs_here = handled1[1]
                for ob2_reg in ob2_regs_here:
                    # print("case 2:  for each ob2_reg, proximate verts on ob1 should be strict subregion of ob1_reg")
                    ob1_reg_vert_inds = range(len(ob1_reg.data.vertices))
                    handled2 = handle_subregion(ob2_reg, ob1_reg_vert_inds, thresh, ob1_reg, make_child, ob2, ob1, discontiguous_pairs, True)
                    if not handled2[0]:
                        # ob2_reg must be split into sub-regions for each corresponding ob1_reg_sub_here
                        ob1_reg_sub_here = handled2[1]
                        for ob1_reg_sub in ob1_reg_sub_here:
                            # print("case 2b:  splitting ob1_reg into sub regions")
                            ob2_reg_vert_inds = range(len(ob2_reg.data.vertices))
                            handled3 = handle_subregion(ob1_reg_sub, ob2_reg_vert_inds, thresh, ob2_reg, make_child, ob1, ob2, discontiguous_pairs, False)
                            if not handled3[0]:
                                ob2_reg_sub_here = handled3[1]
                                print("expected single region, returned multiple, --LAYER 2-- eek!  <------------------------------------------------- BAD")
                                print("if run into this case, must call handle_subregion() for more layers")
                                self.report({'INFO'}, "Error: some regions not processed, please notify developer")
                                print(ob2_reg_sub_here)
                                print(ob1_reg_sub)
                                bad_count += 1

                        # After loop, delete object ob2_reg, as it has been split into multiple components
                        bpy.ops.object.select_all(action='DESELECT')
                        ob2_reg.select = True
                        bpy.ops.object.delete()

                # After loop, delete object ob1_reg, as it has been split into multiple components
                bpy.ops.object.select_all(action='DESELECT')
                ob1_reg.select = True
                bpy.ops.object.delete()


        # For each discontiguous vertex region pairs, calculate surface areas and centroids
        SAs = []
        for sub_ob1, sub_ob2 in discontiguous_pairs:
            SA1, SA2, ctrd = get_SAs_and_centroid(sub_ob1, sub_ob2)
            name_here1 = sub_ob1.name if hasattr(sub_ob1, 'name') else ""
            name_here2 = sub_ob2.name if hasattr(sub_ob2, 'name') else ""
            if SA1 == 0:
                name_here1 = ""
            if SA2 == 0:
                name_here2 = ""
            if SA1 != 0 or SA2 != 0:
                SAs.append([name_here1, name_here2, SA1, SA2, ctrd])

        # Remove all mesh objects without any faces
        objs_del = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH' and len(ob.data.polygons) == 0]
        for ob_i in objs_del:
            delete_object(ob_i)

        # Make all sub objects invisible, and clean extraneous edges from meshes
        objs_end = [ob for ob in bpy.context.scene.objects if ob.type == 'MESH']
        for ob_i in objs_start:
            objs_end.remove(ob_i)
        for ob_i in objs_end:
            # print(ob_i.name)
            delete_extraneous_verts(ob_i)
            ob_i.hide = True
        bpy.ops.object.select_all(action='DESELECT')  # better for user

        # Export results to csv
        write_data(SAs, self)

        print("bad count (better be 0!) = ", bad_count)
        t2 = datetime.datetime.now()
        print("Total processing time: ", t2-t1)

        return {'FINISHED'}


# Process repeated in layers, potentially indefinitely when return false (will eventually stop at mesh resolution)
def handle_subregion(ob1_reg, verts2, thresh, ob2_reg, make_child, ob1, ob2, discontiguous_pairs, reverse_obs):
    ob2_regs_here = get_close_regions_to_single_region(ob1_reg, verts2, thresh, ob2_reg, make_child)
    if len(ob2_regs_here) == 0:
        if (reverse_obs):
            discontiguous_pairs.append([[], ob1_reg])
        else:
            discontiguous_pairs.append([ob1_reg, []])
        return ([True])
    elif len(ob2_regs_here) == 1:
        if make_child:
            ob2_regs_here[0].parent = ob2
            ob1_reg.parent = ob1  # may already be the case
        if (reverse_obs):
            discontiguous_pairs.append([ob2_regs_here[0], ob1_reg])
        else:
            discontiguous_pairs.append([ob1_reg, ob2_regs_here[0]])
        return ([True])
    else:
        return ([False, ob2_regs_here])


# Return lists of vertices on each obj that are within thresh of some vertex on other obj
def get_close_verts(ob1, ob2, thresh):
    # mat1 = ob1.matrix_world  # assuming everything in global coords, from transform_apply() above
    # mat2 = ob2.matrix_world

    # Build KDTrees
    size1 = len(ob1.data.vertices)
    kd1 = mathutils.kdtree.KDTree(size1)
    for i1, v1 in enumerate(ob1.data.vertices):
        kd1.insert(v1.co, i1)
    kd1.balance()

    size2 = len(ob2.data.vertices)
    kd2 = mathutils.kdtree.KDTree(size2)
    for i2, v2 in enumerate(ob2.data.vertices):
        kd2.insert(v2.co, i2)
    kd2.balance()

    # Find closest vertices
    close_verts1 = set()
    close_verts2 = set()
    for i1, v1 in enumerate(ob1.data.vertices):
        v2co, i2, dist12 = kd2.find(v1.co)
        if dist12 < thresh:
            close_verts1.add(i1)
            close_verts2.add(i2)

    for i2, v2 in enumerate(ob2.data.vertices):
        v1co, i1, dist21 = kd1.find(v2.co)
        if dist21 < thresh:
            close_verts1.add(i1)
            close_verts2.add(i2)

    return ([close_verts1, close_verts2])


def get_close_regions_to_single_region(ob1_reg, verts2, thresh, ob2, make_child=True):  # todo: test this (seems fine)
    # Build KDTrees
    size1 = len(ob1_reg.data.vertices)
    kd1 = mathutils.kdtree.KDTree(size1)
    for i1, v1 in enumerate(ob1_reg.data.vertices):
        kd1.insert(v1.co, i1)
    kd1.balance()

    size2 = len(ob2.data.vertices)
    kd2 = mathutils.kdtree.KDTree(size2)
    for i2, v2 in enumerate(ob2.data.vertices):
        kd2.insert(v2.co, i2)
    kd2.balance()

    # Find closest vertices
    ob2_close_vert_inds = set()
    for i1, v1 in enumerate(ob1_reg.data.vertices):
        v2co, i2, dist12 = kd2.find(v1.co)
        if dist12 < thresh:
            ob2_close_vert_inds.add(i2)
    for i2, v2 in enumerate(ob2.data.vertices):
        v1co, i1, dist21 = kd1.find(v2.co)
        if dist21 < thresh:
            ob2_close_vert_inds.add(i2)

    # if ob1_reg.name == 'mitochondria.001':

    ob2_close_regs = separate_distinct_regions(ob2, ob2_close_vert_inds, make_child)
    return (ob2_close_regs)



# Returns list of new mesh objects for each distinct subregion from vert_list on ob
def separate_distinct_regions(ob1, vert_list1, make_child=True):
    # Select relevant vertices on object
    activate_an_object()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = ob1
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')  # edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in vert_list1:
        ob1.data.vertices[v].select=True

    # Duplicate selected verts (still part of original object)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
    # todo:  the above produces the "convertViewVec: called in an invalid context" warning


    # Create separate objects for each discontiguous region
    ob_list_before = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH']
    bpy.ops.mesh.separate(type='SELECTED')  # new object contains only selected vertices
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.mesh.separate(type='LOOSE')     # each discontiguous region is a separate object

    # Remove all pre-existing objects
    ob_list_after = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH']
    for ob_i in ob_list_before:
        ob_list_after.remove(ob_i)
    # now ob_list_after is now only new objects (all submeshes of ob)

    # print("\n--1:  potential new objects")
    # for ob in ob_list_after:
    #     if ob.type == 'MESH':
    #         print(ob.name, len(ob.data.polygons))
    

    # Remove meshes with zero vertices, todo: still need this?
    if False:
        ob_list_meshes = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH']
        for ob_i in ob_list_meshes:
            if len(ob_i.data.vertices) == 0:
                delete_object(ob_i)


    # Remove all pre-existing objects, again
    ob_list_after = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH']
    for ob_i in ob_list_before:
        if ob_i in ob_list_after:
            ob_list_after.remove(ob_i)
        else:
            print(ob_i.name, " not in list, cannot remove")
    # now ob_list_after is only new objects (all submeshes of ob)
    

    # Give the new submeshes meaningful names
    if make_child:
        for ob_i in ob_list_after:
            # ob_i.name = "sub-" + str(ob1.name)
            ob_i.parent = ob1

    return (ob_list_after)


def delete_extraneous_verts(ob, separate_at_end=False):
# Remove all vertices and edges from a mesh object that are not part of any faces
# Note:  may result in mesh with two discontiguous regions that had been connected
#        with a chain of edges, must discuss this in documentation  (todo)

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=3, type='GREATER')
    bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
    # this includes edges that are part of no faces if both of its vertices are parts of faces

    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in ob.data.vertices:
        v.select=True

    # separate objects again, if being added to a list for further processing, otherwise don't
    if separate_at_end:
        nobjs_before = len(bpy.data.objects)
        bpy.ops.object.mode_set(mode='EDIT')    # todo: why does separate(loose) need edit mode here, but obj mode above?
        bpy.ops.mesh.separate(type='LOOSE')     # each discontiguous region is now a separate object
        bpy.ops.object.mode_set(mode='OBJECT')


def delete_object(ob_to_delete):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = ob_to_delete
    # bpy.ops.object.select_all(action='DESELECT')  # not sure why this sometimes leaves Cube
    for ob in bpy.data.objects:
        ob.select = False
    ob_to_delete.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.delete()
    activate_an_object()


# Sometimes this is necessary before changing modes
def activate_an_object():
    ob_0 = [ob_0 for ob_0 in bpy.data.objects if ob_0.type == 'MESH' and ob_0.hide == False][0]
    bpy.context.scene.objects.active = ob_0
    ob_0.select = True


def get_SAs_and_centroid(sub_ob1, sub_ob2):
    # Calculate surface areas of sub_objects; one object might be empty list
    SA1 = 0
    if hasattr(sub_ob1, 'data'):
        # area uses local coordinates, okay as long as transform_apply()'d first
        SA1 = sum([f.area for f in sub_ob1.data.polygons])

    SA2 = 0
    if hasattr(sub_ob2, 'data'):
        SA2 = sum([f.area for f in sub_ob2.data.polygons])

    # Calculate centroid of all vertices involved in this interaction, both surfaces
    cntrd = Vector([0,0,0])
    len1 = 0
    len2 = 0
    if hasattr(sub_ob1, 'data'):
        len1 = len(sub_ob1.data.vertices)
        for v1 in sub_ob1.data.vertices:
            cntrd += v1.co
    if hasattr(sub_ob2, 'data'):
        len2 = len(sub_ob2.data.vertices)
        for v2 in sub_ob2.data.vertices:
            cntrd += v2.co
    cntrd /= (len1 + len2)
    
    return ([SA1, SA2, cntrd])



def get_total_SA(SAs):

    # Join separate surface area objects into single object
    total_SA_ob1 = []
    total_SA_ob2 = []
    for SA in SAs:
        ob1_name = SA[0]
        ob2_name = SA[1]
        if ob1_name != "":
            ob1 = [ob for ob in bpy.data.objects if ob.name == ob1_name][0]
            total_SA_ob1 = join_obs(total_SA_ob1, ob1)

        if ob2_name != "":
            ob2 = [ob for ob in bpy.data.objects if ob.name == ob2_name][0]
            total_SA_ob2 = join_obs(total_SA_ob2, ob2)

    # Remove duplicate faces
    SA1 = get_nonoverlapping_area(total_SA_ob1)
    SA2 = get_nonoverlapping_area(total_SA_ob2)

    # Delete total_SA objects
    bpy.ops.object.select_all(action='DESELECT')
    total_SA_ob1.select = True
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')
    total_SA_ob2.select = True
    bpy.ops.object.delete()

    return([SA1, SA2])



def join_obs(total_SA, ob):
    activate_an_object()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True

    # Duplicate region (bpy.ops.object.duplicate() does not return new object when run in add-on)
    ob_copy = ob.copy()
    ob_copy.data = ob.data.copy()
    bpy.context.scene.objects.link(ob_copy)
    ob_copy.hide = False

    if total_SA == []:
        return(ob_copy)
    bpy.ops.object.select_all(action='DESELECT')
    total_SA.select = True
    ob_copy.select = True
    bpy.context.scene.objects.active = total_SA
    bpy.ops.object.join()
    total_SA_ob = bpy.context.object

    return(total_SA_ob)

def get_nonoverlapping_area(total_SA):
    # Remove overlapping faces
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    total_SA.select = True
    bpy.context.scene.objects.active = total_SA
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get SA
    SA = 0
    for f in total_SA.data.polygons:
        SA += f.area
    return(SA)



# Write distances data to file 
def write_data(SAs, self):
    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    full_filename = bpy.context.scene.filename

    [total_SA1, total_SA2] = get_total_SA(SAs)

    name1 = bpy.context.scene.name1
    name2 = bpy.context.scene.name2

    f = open(full_filename, 'w')
    f.write(name1 + " name;Surface Area " + name1 + ";" + name2 + " name;Surface Area " + name2 + ";Centroid of Interaction\n\n")

    for elt in SAs:
        [name1_here, name2_here, SA1, SA2, cntrd] = elt
        coord_str = "[" + str(cntrd[0]) + "," + str(cntrd[1]) + "," + str(cntrd[2]) + "]"  # use commas
        f.write(name1_here + ";" + str(SA1) + ";" + name2_here + ";" + str(SA2) + ";" + coord_str +"\n")

    f.write("Total (non-overlapping) " + name1 + ";" + str(total_SA1) + ";" + \
            "Total (non-overlapping) " + name2 + ";" + str(total_SA2) + ";\n")
    f.close()
    self.report({'INFO'}, "Finished exporting file.")



def get_dist_sq(coord1, coord2):  # distance is monotonic, take square root at end for efficiency
    d = (coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2 + (coord1[2] - coord2[2])**2
    return d

def get_dist(coord1, coord2):
    d = math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2 + (coord1[2] - coord2[2])**2)
    return d









#######################################################################################################
################################ Sphere to Surface Distances ##########################################
#######################################################################################################


# Define file name and path for export
class DefineFile2(bpy.types.Operator):
    """Define file name and path for distance measurement export"""
    bl_idname = "file.set_filename2"
    bl_label = "Define file path and name"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")

    def execute(self, context):
        directory = self.directory
        filename = self.filename
        fname = filename + '.csv'
        full_filename = os.path.join(directory, fname)
        bpy.context.scene.filename2 = full_filename
        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


# Write distances data to file
def write_distance_data(dists, all_vesicles, synapse_name, mean_dist):
    full_filename2 = bpy.context.scene.filename2

    f = open(full_filename2, 'w')
    f.write('Vesicle Name,Distance to ' + synapse_name + '\n\n')

    for ind, d in enumerate(dists):
        f.write(all_vesicles[ind].name + "," + str(d) + '\n')

    f.write('\n')
    f.write('mean distance,' + str(mean_dist))
    f.close()


# Calculate distance from center of every child object to the active object, and write file
class CalculateVesicleDistances(bpy.types.Operator):
    """Calculate distances to the selected surface (synapse) from each of its child spheres (vesicles)"""
    bl_idname = "object.get_distances2"
    bl_label = "Calculate distances to the selected surface (synapse) from each of its child spheres (vesicles)"
    
    def execute(self, context):

        # Assign objects considered here
        the_synapse = bpy.context.object
        all_vesicles = the_synapse.children

        if all_vesicles == ():
            self.report({'ERROR'}, 'Active object has no children.')
            return {'FINISHED'}

        # Calculate center coordinates of each vesicle
        vesicle_centers = []
        for vscl in all_vesicles:
            mat_vscl = vscl.matrix_world
            these_verts = vscl.data.vertices
            nverts = len(these_verts)
            v_sum = Vector([0,0,0])
            for vert in these_verts:
                these_global_coords = mat_vscl * vert.co
                v_sum += these_global_coords
            this_mean = v_sum / nverts
            vesicle_centers.append(this_mean)

        # Calculate distance from each vesicle center to each vertex on synapse
        dists = []
        inds = []
        mat_syn = the_synapse.matrix_world
        for v_ind, v_ctr in enumerate(vesicle_centers):
            this_min = sys.maxsize
            this_ind = -1
            for s_ind, s_vrt in enumerate(the_synapse.data.vertices):
                this_dist = get_dist_sq(v_ctr, mat_syn*s_vrt.co)
                if this_dist < this_min:
                    this_min = this_dist
                    this_ind = s_ind
                    
            dists.append(math.sqrt(this_min))
            inds.append(this_ind)

        mean_dist = sum(dists) / len(dists)
        # mean_3D = [sum(col) / float(len(col)) for col in zip(*dists)]

        # Write file containing all distances and mean
        write_distance_data(dists, all_vesicles, the_synapse.name, mean_dist)

        return {'FINISHED'}


# Calculate distance from center of every child object to the active object, and write file
class Sphere2Point(bpy.types.Operator):
    """Optional: Replace each child mesh of selected object by single point at the mesh's center \n(useful for slow scenes containing many objects)"""
    bl_idname = "object.reduce_spheres"
    bl_label = "Optional: Replace each child mesh of selected object by single point at the mesh's center \n(useful for slow scenes containing many objects)"
    
    def execute(self, context):
        vscls_as_children = True
        
        # Assumes active object is parent, with many child meshes
        if vscls_as_children:
            parent_ob = bpy.context.object
            vscl_list = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH' \
                                                            and ob_i.parent == parent_ob]
            if len(vscl_list) == 0:
                self.report({'INFO'}, "Selected object has no mesh children.")

            else:
                # Convert to world coordinates
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                parent_ob.select = True
                bpy.context.scene.objects.active = parent_ob
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                for ob in vscl_list:
                    ob.select = True
                    bpy.context.scene.objects.active = ob
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                # Convert to points
                vert_ob_list = spheres2pts(vscl_list)

                # Reassign parent object
                for vert_ob in vert_ob_list:
                    vert_ob.parent = parent_ob


        # # Assumes active object is single object consisting of many joined distinct vescile meshes
        # else:
        #     vscl_ob = bpy.context.object
        #     bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        #     # Store list of already-existing objects
        #     ob_list_before = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH']

        #     # Separate into distinct sphere objects
        #     bpy.ops.object.mode_set(mode='EDIT')
        #     bpy.ops.mesh.select_all(action='SELECT')  # edit mode
        #     bpy.ops.object.mode_set(mode='OBJECT')
        #     bpy.ops.mesh.separate(type='LOOSE')     # each discontiguous region is a separate object

        #     # Get list of only new objects = the spheres
        #     ob_list_after = [ob_i for ob_i in bpy.data.objects if ob_i.type == 'MESH']
        #     for ob_i in ob_list_before:
        #         ob_list_after.remove(ob_i)

        #     ob_list_after.append(vscl_ob)  # is now just one of the spheres

        #     # Replace each sphere with only its centerpoint
        #     vert_ob_list = spheres2pts(ob_list_after)

        #     # Return new vertex objects joined into single object
        #     bpy.ops.object.mode_set(mode='OBJECT')
        #     bpy.ops.object.select_all(action='DESELECT')
        #     for vert_ob in vert_ob_list:
        #         vert_ob.select = True
        #     bpy.context.scene.objects.active = vert_ob_list[0]
        #     bpy.ops.object.join()

        return {'FINISHED'}



# Calculate center of sphere, delete sphere, add new object 
# with single vertex at center of sphere, same name as sphere
def spheres2pts(spherelist):
    vert_ob_list = []
    for vscl in spherelist:
        # Select object and all vertices
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        vscl.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        these_verts = vscl.data.vertices
        nverts = len(these_verts)
        v_sum = Vector([0,0,0])
        for vert in these_verts:
            v_sum += vert.co

        this_mean = v_sum / nverts

        # Delete vscl object
        # To delete selected vertices:  bpy.ops.mesh.delete(type='VERT')
        this_name = vscl.name
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.delete()

        # Create new single vertex object at vscl_mean
        me = bpy.data.meshes.new(this_name)
        vscl_ctr_ob = bpy.data.objects.new(this_name, me)
        bpy.context.scene.objects.link(vscl_ctr_ob)
        me.from_pydata([this_mean], [], [])
        me.update()
        vert_ob_list.append(vscl_ctr_ob)

    # Return an active object
    vert_ob_list[0].select = True
    bpy.context.scene.objects.active = vert_ob_list[0]

    return(vert_ob_list)





def register():
    bpy.utils.register_module(__name__)

    # Define scene variables
    bpy.types.Scene.filename = bpy.props.StringProperty \
    (
        name = "Output file", 
        description = "Set file name and path for output data", 
        default = "/"
    )

    bpy.types.Scene.filename2 = bpy.props.StringProperty \
    (
        name = "Output file", 
        description = "Set file name and path for output data", 
        default = "/"
    )

    bpy.types.Scene.name1 = bpy.props.StringProperty \
    (
        name = "Object 1", 
        description = "Name (prefix) of first type of object", 
        default = ""
    )
    bpy.types.Scene.name2 = bpy.props.StringProperty \
    (
        name = "Object 2", 
        description = "Name (prefix) of second type of object", 
        default = ""
    )

    bpy.types.Scene.dist_thresh = bpy.props.FloatProperty \
    (
        name = "Max Distance",
        description = "The distance threshold: find all interactions less than this distance apart",
        default = 0.1  # todo:  deal with units
    )

def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.dist_thresh
    del bpy.types.Scene.name2
    del bpy.types.Scene.name1 
    del bpy.types.Scene.filename2
    del bpy.types.Scene.filename


if __name__ == "__main__":
    register()

