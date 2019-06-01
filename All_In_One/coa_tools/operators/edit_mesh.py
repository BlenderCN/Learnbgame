'''
Copyright (C) 2015 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    
import bpy
import bpy_extras
import bpy_extras.view3d_utils
from math import radians
import mathutils
from mathutils import Vector, Matrix, Quaternion, geometry
import math
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
import os
from bpy_extras.io_utils import ExportHelper, ImportHelper
import json
from bpy.app.handlers import persistent
from .. functions import *
from .. functions_draw import *
import bgl
import blf
from math import radians, degrees
import traceback


######################################################################################################################################### Grid Fill
def collapse_short_edges(bm,obj,threshold=1.0):
    ### collapse short edges
    edges_len_average = 0
    edges_count = 0
    shortest_edge = 10000
    for edge in bm.edges:
        if True:
            edges_count += 1
            length = edge.calc_length()
            edges_len_average += length
            if length < shortest_edge:
                shortest_edge = length
    edges_len_average = edges_len_average/edges_count

    verts = []
    for vert in bm.verts:
        if not vert.is_boundary:
            verts.append(vert)
    bmesh.update_edit_mesh(obj.data)
    
    bmesh.ops.remove_doubles(bm,verts=verts,dist=edges_len_average*threshold)

    bmesh.update_edit_mesh(obj.data)

def get_average_edge_length(bm,obj):
    edges_len_average = 0
    edges_count = 0
    shortest_edge = 10000
    for edge in bm.edges:
        if True:#edge.is_boundary:
            edges_count += 1
            length = edge.calc_length()
            edges_len_average += length
            if length < shortest_edge:
                shortest_edge = length
    edges_len_average = edges_len_average/edges_count
    return edges_len_average, shortest_edge

def clean_boundary_edges(bm,obj):
    edges_len_average, shortest_edge = get_average_edge_length(bm,obj)
    edges = []
    
    for edge in bm.edges:
        if edge.calc_length() < edges_len_average*.12 and not edge.tag:
            edges.append(edge)
    bmesh.ops.collapse(bm,edges=edges,uvs=False)        
    bmesh.update_edit_mesh(obj.data)        

def average_edge_cuts(bm,obj,cuts=1):
    ### collapse short edges
    edges_len_average, shortest_edge = get_average_edge_length(bm,obj)
    
    subdivide_edges = []
    for edge in bm.edges:
        cut_count = int(edge.calc_length()/shortest_edge)*cuts
        if cut_count < 0:
            cut_count = 0
        if not edge.is_boundary:
            subdivide_edges.append([edge,cut_count])
    for edge in subdivide_edges:
        bmesh.ops.subdivide_edges(bm,edges=[edge[0]],cuts=edge[1])
        bmesh.update_edit_mesh(obj.data)
                
def triangle_fill(bm,obj):
    edges = []
    for edge in bm.edges:
        if edge.select == True:
            edges.append(edge)
    triangle_fill = bmesh.ops.triangle_fill(bm,edges=edges,use_beauty=True)
    bmesh.update_edit_mesh(obj.data)
    if triangle_fill["geom"] == []:
        return False
    else:
        return True

def triangulate(bm,obj):
    bmesh.ops.triangulate(bm,faces=bm.faces) 
    bmesh.update_edit_mesh(obj.data)
    
def smooth_verts(bm,obj):
    ### smooth verts
    smooth_verts = []
    for vert in bm.verts:
        if not vert.is_boundary:
            smooth_verts.append(vert)
    for i in range(50):
        #bmesh.ops.smooth_vert(bm,verts=smooth_verts,factor=1.0,use_axis_x=True,use_axis_y=True,use_axis_z=True)    
        bmesh.ops.smooth_vert(bm,verts=smooth_verts,factor=1.0,use_axis_x=True,use_axis_y=True,use_axis_z=True)    
    bmesh.update_edit_mesh(obj.data)
    
def clean_verts(bm,obj):
    ### find corrupted faces
    faces = []     
    for face in bm.faces:
        i = 0
        for edge in face.edges:
            if not edge.is_manifold:
                i += 1
            if i == len(face.edges):
                faces.append(face)           
    bmesh.ops.delete(bm,geom=faces,context=5)

    edges = []
    for face in bm.faces:
        i = 0
        for vert in face.verts:
            if not vert.is_manifold and not vert.is_boundary:
                i+=1
            if i == len(face.verts):
                for edge in face.edges:
                    if edge not in edges:
                        edges.append(edge)
    bmesh.ops.collapse(bm,edges=edges)
    
    bmesh.update_edit_mesh(obj.data)
    for vert in bm.verts:
        if not vert.is_boundary:
            vert.select = False
            
    verts = []
    for vert in bm.verts:
        if len(vert.link_edges) in [3,4] and not vert.is_boundary:
            verts.append(vert)
    bmesh.ops.dissolve_verts(bm,verts=verts)
    bmesh.update_edit_mesh(obj.data)

def remove_doubles(obj,edge_average_len,edge_min_len):
    bm = bmesh.from_edit_mesh(obj.data)
    verts = []
    for vert in bm.verts:
        if not vert.hide:
            verts.append(vert)
    bmesh.ops.remove_doubles(bm,verts=verts,dist=0.0001)
    bmesh.update_edit_mesh(obj.data)     
        

class ReprojectSpriteTexture(bpy.types.Operator):
    bl_idname = "coa_tools.reproject_sprite_texture"
    bl_label = "Reproject Sprite Texture"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def reproject(self,context):
        ### unwrap
        obj = context.active_object
        hide_base_sprite = obj.data.coa_hide_base_sprite
        obj.data.coa_hide_base_sprite = False
        bm = bmesh.from_edit_mesh(obj.data)
        
        selected_verts = []
        for vert in bm.verts:
            if vert.select:
                selected_verts.append(vert.co)
                #vert.select = True
        
        for face in bm.faces:
            face.select = True
        for vert in bm.verts:
            vert.select = True
                        
        bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=True)        
        
        for face in bm.faces:
            face.select = False
        bmesh.update_edit_mesh(obj.data)    
        
        for vert in bm.verts:
            if vert.co in selected_verts:
                vert.select = True
            else:
                vert.select = False
                
        bmesh.update_edit_mesh(obj.data)    
        obj.data.coa_hide_base_sprite = hide_base_sprite
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        self.reproject(context)
        return {"FINISHED"}
        

class GenerateMeshFromEdgesAndVerts(bpy.types.Operator):
    bl_idname = "coa_tools.generate_mesh_from_edges_and_verts"
    bl_label = "Generate Mesh From Edges And Verts"
    bl_description = ""
    bl_options = {"REGISTER"}     

    def cleanup_and_fill_mesh(self,obj,bm):
        context = bpy.context
        wm = context.window_manager
        wm.progress_begin(0,100)
        
        def edge_is_intersecting(e2,bm):
            for e1 in bm.edges:
                edge_visible = not e1.hide
                edge_not_same = e1.verts[0] not in e2 and e1.verts[1] not in e2
                if edge_visible and edge_not_same:
                    i = geometry.intersect_line_line_2d(e1.verts[0].co.xz, e1.verts[1].co.xz, e2[0].co.xz, e2[1].co.xz)
                    if i != None:
                        return True
            return False   
        
        def get_linked_verts(vert):
            linked_verts = [vert]
            outer_verts = [vert]
            while len(outer_verts) > 0:
                new_verts = []
                for outer_vert in outer_verts:
                    for edge in outer_vert.link_edges:
                        other_vert = edge.other_vert(outer_vert)
                        if other_vert not in linked_verts:
                            linked_verts.append(other_vert)
                            new_verts.append(other_vert)
                outer_verts = new_verts
            return linked_verts

        ### delete faces
        faces = []
        for face in bm.faces:
            if not face.hide:
                face_editable = True
                for vert in face.verts:
                    if vert.hide:
                        face_editable = False
                        break
                if face_editable:    
                    faces.append(face)
                
        bmesh.ops.delete(bm,geom=faces,context=3)        
        wm.progress_update(30)
        ### delete double verts
        edges_len_average, shortest_edge = get_average_edge_length(bm,context.active_object)
        verts = []
        for edge in bm.edges:
            if not edge.hide:
                if edge.calc_length() < edges_len_average*.01:
                    if edge.verts[0] not in verts:
                        verts.append(edge.verts[0])
                    if edge.verts[1] not in verts:
                        verts.append(edge.verts[1])
        bmesh.ops.remove_doubles(bm,verts=verts,dist=0.01)            
        
        ### delete intersecting lines and add vertices at intersectionpoints
        intersection_points = []
        to_be_deleted = []
        for e1 in bm.edges:
            for e2 in bm.edges:
                edges_not_visible = not e1.hide and not e2.hide
                
                edges_share_points = e1.verts[0].co.xz in [e2.verts[0].co.xz, e2.verts[1].co.xz] or e1.verts[1].co.xz in [e2.verts[0].co.xz, e2.verts[1].co.xz]
                
                if e1 != e2 and not edges_share_points and edges_not_visible:
                    i = geometry.intersect_line_line_2d(e1.verts[0].co.xz, e1.verts[1].co.xz, e2.verts[0].co.xz, e2.verts[1].co.xz)
                    
                    if i != None:
                        i_3d = Vector((i[0],e1.verts[0].co[1],i[1]))
                        if e1 not in to_be_deleted:
                            to_be_deleted.append(e1)
                        if e2 not in to_be_deleted:
                            to_be_deleted.append(e2)
                        if i_3d not in intersection_points:
                            intersection_points.append(i_3d)
        for edge in to_be_deleted:
            bm.edges.remove(edge)
        for p in intersection_points:
            bm.verts.new(p)
    
        def get_vertex_loops(bm):
            ### find single vertex loops
            all_verts = []
            vert_loops = []
            for vert in bm.verts:
                if not vert.hide:
                    if vert not in all_verts:
                        loop_list = get_linked_verts(vert)
                        vert_loops.append(loop_list)
                        all_verts += loop_list
            return vert_loops            
        ### connect loose verts
        connected_edges = []
        for vert in bm.verts:
            if not vert.hide and len(vert.link_edges) == 0:
                distance = 1000000000000000
                vert_a = None
                vert_b = None
                for vert2 in bm.verts:
                    edge_center = (vert.co+vert2.co)*.5
                    if vert != vert2 and vert2.co != vert.co:# and edge_center not in connected_edges:
                        if (vert.co - vert2.co).magnitude < distance:
                            distance = (vert.co - vert2.co).magnitude
                            vert_a = vert
                            vert_b = vert2
                if vert_a != None and vert_b != None:
                    edge_center = (vert_a.co+vert_b.co)*.5
                    if edge_center not in connected_edges:
                        bm.edges.new([vert_a,vert_b])
                        connected_edges.append(edge_center) 
                        
        ### connect loose edges
        vert_loops = get_vertex_loops(bm)
        connected_edges = []
        if len(vert_loops) > 0:
            for i,loop in enumerate(vert_loops):
                for vert in loop:
                    exclude_verts = [vert.link_edges[0].other_vert(vert), vert] if len(vert.link_edges) > 0 else [vert]
                    distance = 1000000000000000
                    vert_a = None
                    vert_b = None
                    if len(vert.link_edges) == 1:
                        for j,loop_next in enumerate(vert_loops):
                            for vert2 in loop_next:
                                if vert2 != vert:
                                    edge1 = (vert.co - vert.link_edges[0].other_vert(vert).co).normalized()
                                    edge2 = (vert.co - vert2.co).normalized()
                                    if edge1.length > 0 and edge2.length > 0:
                                        angle = degrees(edge1.angle(edge2))
                                        
                                        if (vert.co - vert2.co).magnitude < distance and vert2 not in exclude_verts and abs(angle) > 30 and not edge_is_intersecting([vert,vert2],bm):
                                            
                                            distance = (vert.co - vert2.co).magnitude
                                            vert_a = vert
                                            vert_b = vert2
                                
                    ### connect nearest points and check 
                    ### if they haven't been connected yet by finding the edge center
                    if vert_a != None and vert_b != None:
                        edge_center = (vert_a.co+vert_b.co)*.5
                        if edge_center not in connected_edges:
                            bm.edges.new([vert_a,vert_b])
                            connected_edges.append(edge_center)                    
                            
        wm.progress_update(100)
        ### find nearest vertex of different loops and connect
        vert_loops = get_vertex_loops(bm)
        connected_edges = []
        if len(vert_loops) > 1:
            ### loop over all edge loops and find nearest vertex points of two loops to connect
            for i,loop in enumerate(vert_loops):
                
                distance = 1000000000000000
                vert_a = None
                vert_b = None
                
                for j,loop_next in enumerate(vert_loops):
                    if j != i:
                        for vert in loop:
                            for vert2 in loop_next:
                                if (vert.co - vert2.co).magnitude < distance:
                                    distance = (vert.co - vert2.co).magnitude
                                    vert_a = vert
                                    vert_b = vert2
                        
                ### connect nearest points and check 
                ### if they haven't been connected yet by finding the edge center
                if vert_a != None and vert_b != None:
                    edge_center = (vert_a.co+vert_b.co)*.5
                    if edge_center not in connected_edges:
                        bm.edges.new([vert_a,vert_b])
                        connected_edges.append(edge_center)             


        ### store existing edges center
        edges_center = []
        for edge in bm.edges:
            edges_center.append((edge.verts[0].co + edge.verts[1].co)*.5)

        ### fill edges
        edges = []
        for edge in bm.edges:
            if not edge.hide:
                edges.append(edge)
        bmesh.ops.triangle_fill(bm,use_beauty=True,use_dissolve=True,edges=edges)

        ### delete newly created edges after using the triangle fill operator
        delete_edges = []
        for edge in bm.edges:
            if not edge.hide and not edge.verts[0].hide and not edge.verts[1].hide:
                edge_center = (edge.verts[0].co + edge.verts[1].co)*.5
                if edge_center not in edges_center and edge.is_boundary:
                    delete_edges.append(edge)
        bmesh.ops.delete(bm,geom=delete_edges,context=2)

        delete_edges = []       
        for edge in bm.edges:
            if not edge.hide and edge.is_wire and not edge.verts[0].hide and not edge.verts[1].hide:
                delete_edges.append(edge)
        bmesh.ops.delete(bm,geom=delete_edges,context=2)        


        ### triangulate mesh
        faces = []
        for face in bm.faces:
            if not face.hide:
                face_editable = True
                for vert in face.verts:
                    if vert.hide:
                        face_editable = False
                        break
                if face_editable:    
                    faces.append(face)
        bmesh.ops.triangulate(bm,faces=faces)   
                    
        ### update mesh            
        bmesh.update_edit_mesh(obj.data)
        wm.progress_end()
        
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        obj = bpy.context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        self.cleanup_and_fill_mesh(obj,bm)
        bpy.ops.coa_tools.reproject_sprite_texture()
        
        return {"FINISHED"}
        

class Fill(bpy.types.Operator):
    bl_idname = "coa_tools.fill_edge_loop"
    bl_label = "Triangle Fill"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    detail = FloatProperty(name="Detail",default=.3,min=0,max=1.0)
    triangulate = BoolProperty(default=False)
    
    def __init__(self):
        self.tiles_x = 1
        self.tiles_y = 1
        self.sprite_frame = 0

    
    def get_img(self,context,obj):
        bpy.ops.object.mode_set(mode="OBJECT")
        img = obj.data.uv_textures.active.data[0].image    
        bpy.ops.object.mode_set(mode="EDIT")
        return img
        
        
    def selection_closed(self,context,bm):
        for vert in bm.verts:
            if vert.select and len(vert.link_edges) == 1:
                return False
        return True    
            
        
    def triangulate_fill(self,context):
        selected_objects = []
        for obj in context.selected_objects:
            if obj != context.active_object:
                selected_objects.append(obj)
                obj.select = False

        start_obj = context.active_object
        
        bm = bmesh.from_edit_mesh(start_obj.data)
        selected = False
        select_count = 0
        for vert in bm.verts:
            if vert.select:
                select_count += 1
                selected = True
        
        if select_count in [1]:
            self.report({'WARNING'},"Select a full loop to fill.")
            return{'CANCELLED'}    
        
        if not selected:
            self.report({'WARNING'},"No vertex selected.")
            return{'CANCELLED'}
        
        if not self.selection_closed(context,bm):
            self.report({'WARNING'},"Selection needs to be a loop. Close the loop first.")
            return{'CANCELLED'}    
            
        
        bpy.ops.mesh.separate(type="SELECTED")
        bpy.ops.object.mode_set(mode="OBJECT")
        context.scene.objects.active = context.selected_objects[0]
        obj = context.selected_objects[0]
        obj.coa_slot_index = start_obj.coa_slot_index
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        
        ### get edge lenght
        bm = bmesh.from_edit_mesh(context.active_object.data)
        edges_len_average, shortest_edge = get_average_edge_length(bm,context.active_object)

        ### grid fill start
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.index_update()
        
            
        fill_ok = triangle_fill(bm,obj)
        
        if fill_ok:
            ### remove short edges
            clean_boundary_edges(bm,obj)
            
            average_edge_cuts(bm,obj)
            triangulate(bm,obj)
            smooth_verts(bm,obj)
            collapse_short_edges(bm,obj)
            smooth_verts(bm,obj)
            clean_verts(bm,obj)
            smooth_verts(bm,obj)
            triangulate(bm,obj)
            smooth_verts(bm,obj)
            
            bm.verts.index_update()
            bmesh.update_edit_mesh(obj.data) 
            bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
            bmesh.update_edit_mesh(obj.data)
                
            for vert in bm.verts:
                vert.select = True
        bmesh.update_edit_mesh(obj.data)
        if not fill_ok:
            return fill_ok 
        
        
        ### grid fill end
        
        bpy.ops.object.mode_set(mode="OBJECT")
        context.scene.objects.active = start_obj
        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode="EDIT")
        #bpy.ops.mesh.remove_doubles(use_unselected=True)
        remove_doubles(context.active_object,edges_len_average, shortest_edge)
        
        
        ### create uv map
        bm = bmesh.from_edit_mesh(start_obj.data)
        filled_contour = []
        for vert in bm.verts:
            if vert.select:
                filled_contour.append(vert)
            vert.select = True
        
        not_selected_faces = []
        for face in bm.faces:
            if face.select == False:
                not_selected_faces.append(face)
            face.select = True
        bmesh.update_edit_mesh(start_obj.data)
        
        for vert in bm.verts:
            if vert not in filled_contour:
                vert.select = False     
        for face in not_selected_faces:
            face.select = False
        bmesh.update_edit_mesh(start_obj.data)
        
        ### unwrap
        obj = context.active_object
        if obj.coa_type == "MESH":
            self.reset_spritesheet(context,start_obj)
        bm = bmesh.from_edit_mesh(obj.data)
        unselected_verts = []
        for vert in bm.verts:
            if not vert.select:
                unselected_verts.append(vert)
                vert.select = True
        unselected_faces = []
        for face in bm.faces:
            if not face.select:
                unselected_faces.append(face)
                face.select = True        
        bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=True)        
        
        for vert in unselected_verts:
            vert.select = False
        for face in unselected_faces:
            face.select = False
        
        if obj.coa_type == "MESH":    
            self.revert_rest_spritesheet(context,start_obj)

        for obj in selected_objects:
            obj.select = True
        return fill_ok
    
    def reset_spritesheet(self,context,obj):
        selected_verts = []
        bpy.ops.object.mode_set(mode="OBJECT")
        
        handle_uv_items(context,obj)
        
        self.tiles_x = obj.coa_tiles_x
        self.tiles_y = obj.coa_tiles_y
        self.sprite_frame = obj.coa_sprite_frame
        obj.coa_sprite_frame = 0
        obj.coa_tiles_x = 1
        obj.coa_tiles_y = 1
        
        bpy.ops.object.mode_set(mode="EDIT")
    
    def revert_rest_spritesheet(self,context,obj):
        bpy.ops.object.mode_set(mode="OBJECT")
        set_uv_default_coords(context,obj)
        obj.coa_tiles_x = self.tiles_x
        obj.coa_tiles_y = self.tiles_y
        obj.coa_sprite_frame = self.sprite_frame
        bpy.ops.object.mode_set(mode="EDIT")
        
    def normal_fill(self,context):
        obj = context.active_object
        
        bpy.ops.mesh.edge_face_add()
        bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=True)
        
        self.reset_spritesheet(context,obj)
        
        
        bm = bmesh.from_edit_mesh(obj.data)
        unselected_faces = []
        for face in bm.faces:
            if face.select == False:
                unselected_faces.append(face)
            face.select = True    
            
            
        bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=True)
        
        
        for face in unselected_faces:
            face.select = False
            
        bmesh.update_edit_mesh(obj.data)
        
        self.revert_rest_spritesheet(context,obj)
    
    def execute(self,context):
        start_obj = context.active_object
        img = self.get_img(context,start_obj)
        
        hide_sprite = start_obj.data.coa_hide_base_sprite
        start_obj.data.coa_hide_base_sprite = False
        
        if self.triangulate:
            if not self.triangulate_fill(context):
                bpy.ops.object.mode_set(mode="OBJECT")
                context.scene.objects.active = start_obj
                bpy.ops.object.join()
                bpy.ops.object.mode_set(mode="EDIT")
                self.report({"WARNING"},"Please select a closed vertex loop.")
        else:
            self.normal_fill(context)
        
        ### assign texture to uv map
        if img != None:
            bpy.ops.object.mode_set(mode="OBJECT")
            assign_tex_to_uv(img,start_obj.data.uv_textures.active)
            bpy.ops.object.mode_set(mode="EDIT")
        
        start_obj.data.coa_hide_base_sprite = hide_sprite
        
        bpy.ops.ed.undo_push(message="Grid Fill")
        return{'FINISHED'}

######################################################################################################################################### Draw Contours
''' scene.ray_cast return values for Blender 2.77
Return (hit, hit_location,hit_normal,?,hit_object,matrix)
'''

''' scene.ray_cast return values for Blender 2.76
Return (hit, hit_object,matrix,hit_location,hit_normal)

result = bpy.context.scene.ray_cast(start,end)
result = [result[0],result[4],result[5],result[1],result[2]]
'''

class DrawContour(bpy.types.Operator):
    bl_idname = "object.coa_edit_mesh" 
    bl_label = "Edit Mesh"
    
    mode = StringProperty(default="EDIT_MESH")
    new_shape_name = StringProperty()
    
    def __init__(self):
        self.type = ""
        self.value = ""
        self.ctrl = False
        self.alt = False
        self.shift = False
        self.distance = .1
        self.cur_distance = 0
        self.draw_dir = Vector((0,0,0))
        self.old_coord = Vector((0,0,0))
        self.mouse_press = False
        self.mouse_press_hist = False
        self.mouse_pos_3d = Vector((0,0,0))
        self.mouse_2d_x = 0
        self.mouse_2d_y = 0
        self.inside_area = False
        self.show_manipulator = False
        self.cursor_pos_hist = Vector((1000000000,0,1000000))
        self.sprite_object = None
        self.in_view_3d = False
        self.nearest_vertex_co = Vector((0,0,0))
        self.contour_length = 0
        
        self.selected_verts_count = 0
        self.selected_vert_coord = None
        self.visible_verts = []
        self.visible_edges = []
        self.intersection_points = []
        self.edge_slide_points = []
        self.new_added_edges = []
        self.cut_edge = False
        
        self.edit_object = None
        self.texture_preview_object = None
        
        self.bone = None
        self.bone_shape = None
        self.draw_bounds = False
        self.draw_type = ""
        self.draw_handler_removed = False
        self.bounds = []
        self.type_prev = ""
        self.value_prev = ""
        self.prev_coa_view = ""
        
        self.armature = None
        self.armature_pose_mode = ""
        
        self.snapped_vert_coord, self.point_type, self.bm_obj, self.verts_edges_data = [Vector((0,0,0)),None,None,None]
        
        self.click_drag = False
        self.first_added_vert = None
        self.delete_stroke_points = []
    
    def project_cursor(self, event):
        coord = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
        transform = bpy_extras.view3d_utils.region_2d_to_location_3d
        region = bpy.context.region
        rv3d = bpy.context.space_data.region_3d
        #### cursor used for the depth location of the mouse
        #depth_location = bpy.context.scene.cursor_location
        depth_location = bpy.context.active_object.location
        ### creating 3d vector from the cursor
        end = transform(region, rv3d, coord, depth_location)
        #end = transform(region, rv3d, coord, bpy.context.space_data.region_3d.view_location)
        ### Viewport origin
        start = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        
        ### Cast ray from view to mouselocation
        if b_version_bigger_than((2,76,0)):
            ray = bpy.context.scene.ray_cast(start, (start+(end-start)*2000)-start )
        else:    
            ray = bpy.context.scene.ray_cast(start, start+(end-start)*2000)
        
        ### ray_cast return values have changed after blender 2.67.0 
        if b_version_bigger_than((2,76,0)):
            ray = [ray[0],ray[4],ray[5],ray[1],ray[2]]
        return start, end, ray

    def set_paint_distance(self,context,ray):
        ob = context.active_object
        scene = context.scene
        
        bpy.ops.object.mode_set(mode='OBJECT')
        if len(ob.data.vertices)==0:
            bpy.ops.object.mode_set(mode='EDIT')
            return 0.0
        
        vert_loc = ob.data.vertices[len(ob.data.vertices)-1].co
        distance = (ray - vert_loc - ob.location).magnitude
        bpy.ops.object.mode_set(mode='EDIT')
        return distance
    
    def limit_value(self,value,minn,maxn):
        return max(min(maxn,value),minn)
    
    def limit_cursor_by_bounds(self,context,location):
        if self.mode == "EDIT_MESH":
            obj = context.active_object
            bounds = []
            for point in self.bounds:
                bounds.append(obj.matrix_world.inverted() * point)
            location = obj.matrix_world.inverted() * location
            
            location[0] = self.limit_value(location[0], bounds[1][0], bounds[2][0])
            location[2] = self.limit_value(location[2], bounds[0][2], bounds[1][2])
            location = obj.matrix_world * location
        return location
    
    
    def clean_mesh(self,obj):
        bm = bmesh.from_edit_mesh(obj.data)
        
        faces = []
        for face in bm.faces:
            if not face.hide:
                face_ok = False
                invalid_edges = 0
                for edge in face.edges:
                    if not edge.is_manifold and not edge.is_wire and not edge.is_boundary:
                        invalid_edges += 1
                        
                if invalid_edges == len(face.edges):
                    faces.append(face)
        bmesh.ops.delete(bm,geom=faces,context=3)
        bmesh.update_edit_mesh(obj.data)
        
    def draw_verts(self,context,obj,bm,position,use_snap=False):
        scene = context.scene
        obj_matrix = obj.matrix_world
        if scene.coa_surface_snap:
            snapped_pos, type, bm_ob = self.snapped_vert_coord , self.point_type , self.bm_objs
        else:
            snapped_pos, type, bm_ob = [self.mouse_pos_3d,None,None]
        if not use_snap:
            snapped_pos = position
        
        snapped_pos = self.limit_cursor_by_bounds(context,snapped_pos)
        
        for edge in bm.edges:
            edge.select = False
        for vert in bm.verts:
            vert.select = False
        for face in bm.faces:
            face.select = False     
        
        intersect_prev_vert = bm.select_history[0] if len(bm.select_history) > 0 else None
        for i,p in enumerate(self.intersection_points):
            for edge in bm.edges:
                sub_edge = None
                c = self.get_projected_point(edge,custom_pos=p,disable_edge_threshold=True)
                if (c - p).magnitude < 0.001:
                    sub_edge = edge
                    break
            if sub_edge != None:
                divider = (obj.matrix_world*sub_edge.verts[0].co - obj.matrix_world*sub_edge.verts[1].co).magnitude
                if divider != 0:
                    percentage = (obj.matrix_world*sub_edge.verts[0].co - c).magnitude / (obj.matrix_world*sub_edge.verts[0].co - obj.matrix_world*sub_edge.verts[1].co).magnitude
                    new_edge,new_vert = bmesh.utils.edge_split(sub_edge,sub_edge.verts[0],percentage)
                    
                    bm.select_history = [new_vert]
                    try:
                        edge = bm.edges.new([intersect_prev_vert,new_vert])
                        self.new_added_edges.append(edge)
                    except:
                        print("Edge already exists.")
                    intersect_prev_vert = new_vert
        
        if type == "VERT" and use_snap:
            if self.contour_length > 0 and len(bm.select_history) > 0:
                new_vert = bm_ob
                try:
                    edge = bm.edges.new([bm.select_history[0],new_vert])
                    self.new_added_edges.append(edge)
                except:    
                    print("Edge already exists.")
                bm.select_history = [new_vert]
                self.selected_vert_coord = obj_matrix * new_vert.co
                new_vert.select = True
            else:
                new_vert = bm_ob
                bm.select_history = [new_vert]
                self.selected_vert_coord = obj_matrix * new_vert.co
                new_vert.select = True
                
            
            if self.contour_length == 0:    
                self.contour_length += 1
                
        elif type == "EDGE" and use_snap:
            sub_edge = bm_ob
            if sub_edge != None:
                c = self.get_projected_point(sub_edge)
                divider = (obj.matrix_world*sub_edge.verts[0].co - obj.matrix_world*sub_edge.verts[1].co).magnitude
                if divider != 0:
                    percentage = (obj.matrix_world*sub_edge.verts[0].co - c).magnitude / (obj.matrix_world*sub_edge.verts[0].co - obj.matrix_world*sub_edge.verts[1].co).magnitude
                    new_edge,new_vert = bmesh.utils.edge_split(sub_edge,sub_edge.verts[0],percentage)
                    if sub_edge in self.new_added_edges:
                        self.new_added_edges.append(new_edge)
                    bm.select_history = [new_vert]
                    new_vert.select = True
                    self.first_added_vert = Vector(new_vert.co)
                    self.selected_vert_coord = obj_matrix * new_vert.co
                    try:
                        pass
                        if self.contour_length > 0:
                            edge = bm.edges.new([intersect_prev_vert,new_vert])
                            self.new_added_edges.append(edge)
                            #edge.select = True
                    except:
                        print("Edge already exists.")
                
                if self.contour_length == 0:    
                    self.contour_length += 1
                    self.selected_vert_coord = obj_matrix * new_vert.co
                    
        else:
            new_vert = bm.verts.new(obj_matrix.inverted() * snapped_pos)
            self.first_added_vert = Vector(new_vert.co)
                
            bmesh.update_edit_mesh(obj.data)
            
            if self.contour_length > 0 and len(bm.select_history) > 0:
                edge = bm.edges.new([bm.select_history[0],new_vert])
                self.new_added_edges.append(edge)
                
            self.selected_vert_coord = obj_matrix * new_vert.co
            new_vert.select = True
            bm.select_history = [new_vert]
            
            self.contour_length += 1
            
        bmesh.update_edit_mesh(obj.data)
    
    def set_bone_shape_color_and_wireframe(self,context,obj):
        if self.bone.bone_group != None:
            bone_group_name = self.bone.bone_group.name
            bone_group_color = self.bone.bone_group.colors.normal
            suffix = "_group_color"
            if (bone_group_name+suffix) not in bpy.data.materials:
                material = bpy.data.materials.new(bone_group_name+suffix)
            else:
                material = bpy.data.materials[bone_group_name+suffix]
            
            material.diffuse_color = bone_group_color
            material.use_shadeless = True
            
            if len(obj.material_slots) == 0:
                obj.data.materials.append(material)
            else:
                obj.material_slots[0].material = material
        else:
            if len(obj.material_slots) > 0:
                obj.material_slots[0].material = None
                      
        bm = bmesh.from_edit_mesh(obj.data)
        if len(bm.faces) > 0:
            self.armature.data.bones[self.bone.name].show_wire = False
        else:
            self.armature.data.bones[self.bone.name].show_wire = True
        bm.free()    
    
    def check_verts(self,context,event):
        verts = []
        bm = bmesh.from_edit_mesh(context.active_object.data)
        for vert in bm.verts:
            if vert.select:
                verts.append(vert)
        for vert in verts:
            vert.co = context.active_object.matrix_world.inverted() * self.limit_cursor_by_bounds(context,context.active_object.matrix_world * vert.co)
        bmesh.update_edit_mesh(context.active_object.data)
    
    
    def get_selected_vert_pos(self,context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        for vert in bm.verts:
            if vert.select == True:
                bmesh.update_edit_mesh(context.active_object.data)
                return vert.co
        bmesh.update_edit_mesh(context.active_object.data)
        return None
        
    def check_selected_verts(self,context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return bm.select_history
    
    
    def get_projected_point(self,edge,custom_pos=None,disable_edge_threshold=False):
        context = bpy.context
        obj = context.active_object
        mouse_pos = custom_pos if custom_pos != None else self.mouse_pos_3d
        if type(edge) == bmesh.types.BMEdge:
            v1 = obj.matrix_world * edge.verts[0].co
            v2 = obj.matrix_world * edge.verts[1].co
        elif type(edge) == list:
            v1 = obj.matrix_world * edge[0]
            v2 = obj.matrix_world * edge[1]
        
        dist = min((v1-v2).magnitude*.5 , context.scene.coa_snap_distance * context.space_data.region_3d.view_distance)
        if disable_edge_threshold:
            dist = 0
        
        p1 = (v1 - v2).normalized()
        p2 = mouse_pos - v2
        l = max(min(p2.dot(p1), (v1 - v2).magnitude - dist),0 + dist)
        c = (v2 +  l * p1)
        return c
    
    def get_edge_slide_points(self,context,bm):
        obj = context.active_object
        
        snap_distance = context.scene.coa_snap_distance * context.space_data.region_3d.view_distance
        
        edge_slide_points = []
        for edge in bm.edges:
            bm.edges.ensure_lookup_table()
            if not edge.hide:
                vert_1 = obj.matrix_world * edge.verts[0].co
                vert_2 = obj.matrix_world * edge.verts[1].co
                
                left = min(vert_1.x , vert_2.x) - snap_distance
                right = max(vert_1.x , vert_2.x) + snap_distance
                top = max(vert_1.z , vert_2.z) + snap_distance
                bottom = min(vert_1.z , vert_2.z) - snap_distance
                
                if self.mouse_pos_3d.x > left and self.mouse_pos_3d.x < right and self.mouse_pos_3d.z < top and self.mouse_pos_3d.z > bottom: 
                    c = self.get_projected_point(edge)
                    edge_slide_points.append([c,edge])
                
        return edge_slide_points
    
    def get_visible_verts(self,context,bm):
        obj = context.active_object
        visible_verts = []
        self.selected_verts_count = 0
        
        
        active_vert = None
        if len(bm.select_history)>0 and type(bm.select_history[0]) == bmesh.types.BMVert:
            active_vert = bm.select_history[0]
        for vert in bm.verts:
            if not vert.hide and vert.select:
                self.selected_verts_count += 1
            if not vert.hide:
                visible_verts.append([obj.matrix_world * vert.co , vert])
        return visible_verts
    
    def snap_to_edge_or_vert(self,coord, get_bm_obj = False):
        obj = bpy.context.active_object
        context = bpy.context
        scene = bpy.context.scene
        distance = scene.coa_snap_distance * bpy.context.space_data.region_3d.view_distance
        snap_coord = coord
        point_type = None
        bm_obj2 = None
        verts_edges_data = None
        
        points = []
        for e,edge in self.edge_slide_points:
            points.append([e,"EDGE",edge])
            
        for p,vert in self.visible_verts:
            points.append([p,"VERT",vert])
        
        for vert,type,bm_obj in points:
            
            if (vert - coord).magnitude < distance:
                if type == "VERT":
                    distance = (vert - coord).magnitude
                snap_coord = vert
                point_type = type
                
                bm_obj2 = bm_obj
                if "Vert" in str(bm_obj):
                    verts_edges_data = [bm_obj.co]
                elif "Edge" in str(bm_obj):
                    verts_edges_data = [bm_obj.verts[0].co,bm_obj.verts[1].co]
        return [snap_coord , point_type , bm_obj2 , verts_edges_data]
        
    def get_intersecting_lines(self,coord,bm):
        scene = bpy.context.scene
        
        if scene.coa_surface_snap:
            coord, point_type, bm_ob = self.snapped_vert_coord , self.point_type , self.bm_objs
        else:    
            coord, point_type, bm_ob = [None,None,None]
            
        coord = self.limit_cursor_by_bounds(bpy.context,coord)
        
        intersection_points = []
        if self.selected_vert_coord != None and coord != None:
            obj = bpy.context.active_object
            e1 = [self.selected_vert_coord.xz,coord.xz]
            for edge in bm.edges:
                if not edge.hide:# and (edge.is_wire or edge.is_boundary):
                    e2 = [(obj.matrix_world * edge.verts[0].co).xz , (obj.matrix_world * edge.verts[1].co).xz ]
                    ip = geometry.intersect_line_line_2d(e1[0],e1[1],e2[0],e2[1])
                    if ip != None:
                        ip = Vector((ip[0],self.selected_vert_coord[1],ip[1]))
                        if (ip - self.selected_vert_coord).magnitude > 0.001 and (ip - coord).magnitude > 0.001:
                            intersection_points.append(ip)
        intersection_points.sort(key=lambda x: (self.selected_vert_coord - x).magnitude)
        return intersection_points         
    
    def delete_geometry(self,context,bm,position,single_vert=False):
        obj = context.active_object
        snapped_vert_coord , point_type , bm_ob = self.snapped_vert_coord , self.point_type , self.bm_objs
        if point_type == "VERT":
            vert = bm_ob
            
            delete_verts = [vert]
            for edge in vert.link_edges:
                other_vert = edge.other_vert(vert)
                if len(other_vert.link_edges) == 1:
                    delete_verts.append(other_vert)
            for vert in delete_verts        :
                bm.verts.remove(vert)
                    
        elif point_type == "EDGE":
            edge = bm_ob
            
            verts = []
            for vert in edge.verts:
                verts.append(vert)
                
                
            delete_edges = [edge]
            for edge in delete_edges:
                bm.edges.remove(edge)    
            
            for vert in verts:
                if len(vert.link_edges) == 0:
                    bm.verts.remove(vert)
            
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
            
        bmesh.update_edit_mesh(obj.data)                  
    
    def modal(self, context, event):
        try:
            ### set variables
            self.mouse_2d_x = event.mouse_region_x
            self.mouse_2d_y = event.mouse_region_y
            obj = context.active_object
            self.type = str(event.type)
            self.value = str(event.value)
            self.ctrl = bool(event.ctrl)
            self.alt = bool(event.alt)
            self.shift = bool(event.shift)
            self.in_view_3d = check_region(context,event)
            scene = context.scene
            
            ### map mouse button
            click_button = None
            select_button = None
            if context.user_preferences.inputs.select_mouse == "RIGHT":
                click_button = 'LEFTMOUSE'
                select_button = 'RIGHTMOUSE'
                
            else:
                click_button = 'RIGHTMOUSE'
                select_button = 'LEFTMOUSE'
            
            
            ### leave edit mode
            if context.active_object == None or (context.active_object != None and context.active_object.type == "MESH" and context.active_object.mode != "EDIT" and not self.draw_handler_removed) or self.sprite_object.coa_edit_mesh == False or context.active_object.type != "MESH":
                return self.exit_edit_mode(context,event)
            self.obj = bpy.context.active_object
            ### create bmesh object
            bm = bmesh.from_edit_mesh(obj.data)
            
            ### limit verts within bounds -> resets vertex positions to stay within bounds
            if self.type_prev in ["G","S","R"]:
                self.check_verts(context,event)
            
            
            if self.in_view_3d and context.active_object != None and self.type not in ["MIDDLEMOUSE"] and self.sprite_object.coa_edit_mesh and click_button not in [select_button]:
        
                ### set click drag    
                if self.type == click_button:
                    self.click_drag = True
                if self.click_drag and self.value == "RELEASE":
                    self.click_drag = False
                    if event.ctrl:
                        bpy.ops.ed.undo_push(message="Delete Contour")
                    else:
                        bpy.ops.ed.undo_push(message="Draw Contour")    

                ### set mouse press history
                self.mouse_press_hist = self.mouse_press
                
                ### Cast Ray from mousePosition and set Cursor to hitPoint
                rayStart,rayEnd, ray = self.project_cursor(event)
                
                
                if rayEnd != None:
                    pos = rayEnd
                    pos[1] = obj.matrix_world.to_translation()[1]-0.00001
                    bpy.context.scene.cursor_location = rayEnd
                    self.mouse_pos_3d = rayEnd
                if scene.coa_lock_to_bounds and self.mode == "EDIT_MESH":
                    bpy.context.scene.cursor_location = self.limit_cursor_by_bounds(context,scene.cursor_location)   
                
                ### get visible verts in list | get intersecting points | get edge slide points  -> add everything in separate lists
                self.visible_verts = self.get_visible_verts(context,bm)
                if scene.coa_surface_snap:
                    self.edge_slide_points = self.get_edge_slide_points(context,bm)
                    
                    self.snapped_vert_coord, self.point_type, self.bm_objs, self.verts_edges_data = self.snap_to_edge_or_vert(self.mouse_pos_3d)
                else:
                    self.snapped_vert_coord, self.point_type, self.bm_objs, self.verts_edges_data = [self.mouse_pos_3d,None,None,None]
                
                if self.contour_length > 0 and not self.alt:
                    self.intersection_points = self.get_intersecting_lines(self.mouse_pos_3d,bm)
                else:
                    self.intersection_points = []
                
                self.snapped_vert_coord = self.limit_cursor_by_bounds(context,self.snapped_vert_coord)
                
                    
                ### check if mouse is in 3d View
                coord = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
                
                if coord[0] < 0 or coord[0] > bpy.context.area.width:
                    self.inside_area = False
                    bpy.context.window.cursor_set("DEFAULT")
                elif coord[1] < 0 or coord[1] > bpy.context.area.height:
                    self.inside_area = False
                    bpy.context.window.cursor_set("DEFAULT")
                else:
                    self.inside_area = True
                    
                    if self.alt:
                        bpy.context.window.cursor_set("CROSSHAIR")
                    else:        
                        if self.point_type == "EDGE":
                            bpy.context.window.cursor_set("KNIFE")
                        else:
                            bpy.context.window.cursor_set("PAINT_BRUSH")
                  
                    
                ### Set Mouse click
                
                if (event.value == 'PRESS' or event.value == 'CLICK') and event.type == click_button and self.mouse_press == False and not self.ctrl and not self.shift:
                    if not self.alt:
                        self.mouse_press = True
                        
                        ### add vert on first mouse press
                        self.cursor_pos_hist = Vector(context.scene.cursor_location)
                        
                        self.draw_verts(context,obj,bm,self.cursor_pos_hist,use_snap=True)
                    return{'RUNNING_MODAL'}
                    
                if (event.value == 'RELEASE' and event.type == 'MOUSEMOVE'):
                    self.mouse_press = False    
                
                
                self.cur_distance = (context.scene.cursor_location - self.cursor_pos_hist).magnitude
                self.draw_dir = (context.scene.cursor_location - self.cursor_pos_hist).normalized()
                
                
                ### add verts while mouse is pressed and moved
                mult = 1.0
                if not self.ctrl:
                    if self.mouse_press and self.inside_area:
                        if self.cur_distance > context.scene.coa_distance*mult:
                            i = int(self.cur_distance / (context.scene.coa_distance*mult))
                            
                            for j in range(i):
                                new_vertex_pos = (self.cursor_pos_hist + (self.draw_dir*context.scene.coa_distance*mult))
                                self.draw_verts(context,obj,bm,new_vertex_pos,use_snap=False)

                                self.cursor_pos_hist = Vector(new_vertex_pos)
                    else:
                        self.old_coord = Vector((100000,100000,100000))

                ### check selected verts
                select_history = self.check_selected_verts(context)
                    
                    
                if self.type_prev in ["G"] and self.contour_length > 0:
                    if len(select_history) > 0 and type(select_history[0]) == bmesh.types.BMVert:
                        self.selected_vert_coord = obj.matrix_world* select_history[0].co
                
                ### finishing edge drawing
                if self.contour_length == 0 and len(self.new_added_edges) > 0:                
                    self.new_added_edges = []
                
                scene.tool_settings.double_threshold = scene.coa_snap_distance
                ### delete verts
                if self.alt and (self.click_drag or self.type == click_button) and not self.type in ["MIDDLEMOUSE"]:
                    self.selected_vert_coord = None
                    self.contour_length = 0
                    self.delete_geometry(context,bm,self.mouse_pos_3d)
                if self.contour_length == 1 and self.type in ["ESC"]:
                    bm = bmesh.from_edit_mesh(context.active_object.data)
                    if self.first_added_vert != None:
                        for vert in bm.verts:
                            if vert.co == self.first_added_vert:
                                self.first_added_vert = None
                                bmesh.ops.dissolve_verts(bm,verts=[vert])
                                bmesh.update_edit_mesh(obj.data)
                                break
                
                ### pick edge length
                if self.shift and self.point_type == "EDGE":
                    bpy.context.window.cursor_set("EYEDROPPER")
                    if self.type == click_button:
                        
                        p1 = obj.matrix_world * self.verts_edges_data[0]
                        p2 = obj.matrix_world * self.verts_edges_data[1]
                        length = (p1-p2).magnitude
                        scene.coa_distance = length
                        
                        text = "Stroke Distance set to "+str(round(length,2))
                        self.report({"INFO"},text)
                
                ### remove last selected vert coord if nothing is selected
                if (self.selected_verts_count == 0 and self.selected_vert_coord != None) or self.type in [select_button] or (self.ctrl and self.type in ["Z"]):# or self.type_prev in ["G"]:
                    self.selected_vert_coord = None
                    self.contour_length = 0
                
                ### deselect verts
                if event.type in ["ESC","RET"]:
                    bm = bmesh.from_edit_mesh(context.active_object.data)
                    bm.select_history = []
                    for vert in bm.verts:
                        vert.select = False
                    for edge in bm.edges:
                        edge.select = False        
                    for face in bm.faces:
                        face.select = False    
                        
                
                if (event.type in {'TAB'} and not event.ctrl):
                    self.sprite_object.coa_edit_mesh = False
                    bpy.ops.object.mode_set(mode='OBJECT')
            
            self.type_prev = str(event.type)
            self.value_prev = str(event.value)
        except Exception as e:
            traceback.print_exc()
            self.report({"ERROR"},"An Error occured, please check console for more Information.")
            self.exit_edit_mode(context,event)
        return {'PASS_THROUGH'}
    
    def exit_edit_mode(self,context,event):
        self.finish_edit_object(context)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler2, "WINDOW")
        
        self.draw_handler_removed = True
        self.sprite_object.coa_edit_mesh = False
        self.sprite_object.coa_edit_mode = "OBJECT"
        
        bpy.context.space_data.show_manipulator = self.show_manipulator
        bpy.context.window.cursor_set("CROSSHAIR")
        bpy.ops.object.mode_set(mode="OBJECT")
        self.sprite_object.coa_edit_mesh = False
        set_local_view(False)
        
        obj = context.active_object
        context.scene.objects.active = self.edit_object
        context.screen.coa_view = self.prev_coa_view
        bpy.ops.object.mode_set(mode="EDIT")
        if self.mode == "DRAW_BONE_SHAPE":
            self.set_bone_shape_color_and_wireframe(context,self.bone_shape)
            
        bpy.context.space_data.show_manipulator = self.show_manipulator
        bpy.context.window.cursor_set("CROSSHAIR")
        bpy.ops.object.mode_set(mode="OBJECT")
        
        
        
        self.sprite_object.coa_edit_mesh = False
        set_local_view(False)
        
        if self.armature !=  None:
            self.armature.data.pose_position = self.armature_pose_mode
            
        if self.mode == "DRAW_BONE_SHAPE":            
            self.armature.draw_type = self.draw_type
            context.scene.coa_lock_to_bounds = self.draw_bounds
            if self.armature != None:
                context.scene.objects.active = self.armature
            if len(self.bone_shape.data.vertices) > 1:
                self.bone.custom_shape = self.bone_shape
                self.bone.use_custom_shape_bone_size = False
            else:
                self.bone.custom_shape = None    
            
            self.bone_shape.select = False
            self.bone_shape.parent = None
            context.scene.objects.unlink(self.bone_shape)
            bpy.ops.object.mode_set(mode="POSE")    
        else:
            if len(self.obj.data.vertices) > 4:
                self.obj.data.coa_hide_base_sprite = True
            bpy.ops.object.mode_set(mode="OBJECT")    
        context.scene.objects.active = obj
        return{'FINISHED'}
    
    _timer = 0

    def prepare_edit_object(self, context):
        original_object = context.active_object

        keep_vert_index = []
        v_group = original_object.vertex_groups["coa_base_sprite"]
        for i,vert in enumerate(original_object.data.vertices):
            try:
                if v_group.weight(i) > 0:
                    keep_vert_index.append(i)
            except:
                pass

        texture_preview_object = original_object.copy()
        texture_preview_object.data = original_object.data.copy()
        texture_preview_object.name = "TEXTURE PREVIEW"
        for mod in texture_preview_object.modifiers:
            if mod.name == "coa_base_sprite":
                texture_preview_object.modifiers.remove(mod)
        context.scene.objects.link(texture_preview_object)
        context.scene.objects.active = texture_preview_object
        bpy.ops.object.mode_set(mode="EDIT")
        if "coa_base_sprite" in texture_preview_object.vertex_groups:
            bm = bmesh.from_edit_mesh(texture_preview_object.data)
            for vert in bm.verts:
                vert.hide = False
                if vert.index not in keep_vert_index:
                    bm.verts.remove(vert)
        bpy.ops.object.mode_set(mode="OBJECT")

        context.scene.objects.active = original_object
        edit_object = context.active_object
        edit_object.select = True
        edit_object.draw_type = "WIRE"
        texture_preview_object.select = True
        texture_preview_object.location[1] += .1

        return edit_object, texture_preview_object

    def finish_edit_object(self, context):
        if self.texture_preview_object != None:
            bpy.data.objects.remove(self.texture_preview_object)
            context.scene.objects.active = self.edit_object
            self.edit_object.draw_type = "TEXTURED"
            if len(self.edit_object.data.vertices) > 4:
                self.edit_object.data.coa_hide_base_sprite = True
            else:
                self.edit_object.data.coa_hide_base_sprite = False
            bpy.ops.coa_tools.reproject_sprite_texture()



    def execute(self, context):
        if context.active_object == None or (context.active_object.type != "MESH" and self.mode != "DRAW_BONE_SHAPE"):
            self.report({"ERROR"},"Sprite is hidden or not selected. Cannot go in Edit Mode.")
            return{"CANCELLED"}

        if self.mode == "EDIT_MESH":
            self.edit_object, self.texture_preview_object = self.prepare_edit_object(context)

        #bpy.ops.wm.coa_modal() ### start coa modal mode if not running
        self.sprite_object = get_sprite_object(context.active_object)
        if self.sprite_object != None:
            self.sprite_object = bpy.data.objects[self.sprite_object.name]
            
            
            self.armature = get_armature(self.sprite_object)
            if self.armature != None:
                self.armature_pose_mode = self.armature.data.pose_position
                if self.mode == "EDIT_MESH":
                    self.armature.data.pose_position = "REST"
                
        
        ### get Sprite Boundaries
        if self.texture_preview_object != None and self.texture_preview_object.type == "MESH":
            self.texture_preview_object.active_shape_key_index = 0
            self.texture_preview_object.data.coa_hide_base_sprite = False
            self.mesh_center , self.bounds = get_bounds_and_center(self.texture_preview_object)
        
        if self.mode == "EDIT_MESH":
            #hide_base_sprite(bpy.context.active_object)
            self.edit_object.data.coa_hide_base_sprite = True
            self.edit_object.active_shape_key_index = 0
            
        
        if self.mode == "DRAW_BONE_SHAPE":
            self.draw_bounds = context.scene.coa_lock_to_bounds
            context.scene.coa_lock_to_bounds = False
            
            bone = bpy.context.active_pose_bone
            bone.use_custom_shape_bone_size = False
            armature = bpy.context.active_object
            #bone_mat = armature.matrix_world * bone.matrix * bone.matrix_basis.inverted()
            bone_mat = armature.matrix_local * bone.matrix
            bone_loc, bone_rot, bone_scale = bone_mat.decompose()
            
            if bone.custom_shape != None and bone.custom_shape.name in bpy.data.objects:
                shape_name = bone.custom_shape.name
            else:    
                shape_name = bone.name+"_custom_shape"    
                
            if self.new_shape_name != "":
                obj = bpy.data.objects[self.new_shape_name]
                me = obj.data.copy()
            else:    
                if shape_name in bpy.data.meshes:
                    me = bpy.data.meshes[shape_name]
                else:    
                    me = bpy.data.meshes.new(shape_name)
            me.show_double_sided = True
            if shape_name in bpy.data.objects and self.new_shape_name == shape_name:
                bone_shape = bpy.data.objects[shape_name]
            else:
                if shape_name in bpy.data.objects:
                    bone_shape = bpy.data.objects[shape_name]
                    bone_shape.data = me
                else:    
                    bone_shape = bpy.data.objects.new(shape_name,me)
            self.edit_object = bone_shape
            
            bone_shape["coa_bone_shape"] = True
            context.scene.objects.link(bone_shape)
            context.scene.objects.active = bone_shape
            bone_shape.select = True
            bone_shape.parent = self.sprite_object
            bone_shape.name = bone.name+"_custom_shape"
            me.name = bone.name+"_custom_shape"
            
            bone_shape.name = bone.name+"_custom_shape"
            bone_shape.matrix_local = bone_mat
#            scale = 1/bone_shape.dimensions.y
#            bone_shape.scale = Vector((scale,scale,scale))
            bone_shape.show_x_ray = True
            self.bone_shape = bone_shape
            self.bone = bone
            self.armature = armature
            bone.custom_shape = None#self.bone_shape
            self.draw_type = self.armature.draw_type
            self.armature.draw_type = "WIRE"

        if self.sprite_object != None:
            self.sprite_object.coa_edit_mode = "MESH"
            self.sprite_object.coa_edit_mesh = True
        
        wm = context.window_manager
        
        if self.mode == "EDIT_MESH":
            set_local_view(True)
        self.prev_coa_view = str(context.screen.coa_view)
        context.screen.coa_view = "2D"

        self.show_manipulator = bpy.context.space_data.show_manipulator
        bpy.context.space_data.show_manipulator = False
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_VIEW")
        self.draw_handler2 = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, "WINDOW", "POST_PIXEL")
                
        bpy.ops.view3d.viewnumpad(type="FRONT")        
        #self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)        
        #context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        bpy.context.space_data.show_manipulator = self.show_manipulator
        bpy.context.window_manager.sketch_assets_enabled = False
        return {'CANCELLED'}
    
    def draw_circle(self,pos,color,size=8):
        pos = pos + Vector((0,-.1,0))
        bgl.glColor4f(color[0], color[1], color[2], 1.0)
        bgl.glPointSize(size)
        bgl.glBegin(bgl.GL_POINTS)
        bgl.glVertex3f(pos[0],pos[1],pos[2])
        bgl.glEnd()
    
    def draw_callback_text(self):
        obj = bpy.context.active_object
        ### draw text for edge length detection
        if self.shift and self.point_type == "EDGE":
            p1 = obj.matrix_world * self.verts_edges_data[0]
            p2 = obj.matrix_world * self.verts_edges_data[1]
            length = (p1-p2).magnitude

            font_id = 0
            line = str(round(length,2))
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(1,1,1,1)

            blf.position(font_id, self.mouse_2d_x-15, self.mouse_2d_y+30, 0)
            blf.size(font_id, 20, 72)
            blf.draw(font_id, line)

        if self.mode == "EDIT_MESH":
            draw_edit_mode(self,bpy.context,color=[1.0, 0.39, 0.41, 1.0],text="Edit Mesh Mode",offset=-20)
        elif self.mode == "DRAW_BONE_SHAPE":
            draw_edit_mode(self,bpy.context,color=[1.0, 0.39, 0.41, 1.0],text="Draw Bone Shape",offset=-20)
               
    
    def draw_callback_px(self):
        obj = bpy.context.active_object
        
        green = [0,1,.5]
        blue = [.25,.2,1]
        red = [1,0,0]
        yellow = [1,1,0]
        
        if obj.mode == "EDIT":
            
            y_offset = Vector((0,-0.0001,0))
            
            vertex_vec_new = self.mouse_pos_3d
            
            if len(self.bounds) > 3:
                vec1 = Vector(self.bounds[0]) + y_offset
                vec2 = Vector(self.bounds[1]) + y_offset
                vec3 = Vector(self.bounds[3]) + y_offset
                vec4 = Vector(self.bounds[2]) + y_offset
                
                color = [1,.7,.5]
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glColor4f(color[0], color[1], color[2], 1.0)
                bgl.glLineWidth(1)
                
                bgl.glEnable(bgl.GL_LINE_SMOOTH)
                
                bgl.glBegin(bgl.GL_LINE_STRIP)
                bgl.glVertex3f(vec1[0],vec1[1],vec1[2])
                bgl.glVertex3f(vec2[0],vec2[1],vec2[2])
                bgl.glVertex3f(vec3[0],vec3[1],vec3[2])
                bgl.glVertex3f(vec4[0],vec4[1],vec4[2])
                bgl.glVertex3f(vec1[0],vec1[1],vec1[2])
                bgl.glEnd()
            
            
            ### draw lines and dots
            #mouse_pos_in_bounds = self.limit_cursor_by_bounds(bpy.context,self.mouse_pos_3d)
            if self.type not in ["K","C","B","R","G","S"] and self.in_view_3d:
                vertex_vec_new = self.limit_cursor_by_bounds(bpy.context,self.mouse_pos_3d)
                vertex_vec_new =  self.snapped_vert_coord + y_offset
                
                color = green
                bgl.glLineWidth(2)
                
                if self.selected_vert_coord != None:
                    bgl.glEnable(bgl.GL_LINE_SMOOTH)
                    vertex_vec = self.selected_vert_coord + y_offset
                    if self.point_type == "VERT":
                        color = green
                    elif self.point_type == "EDGE":
                        color = blue
                    
                    if not self.alt:
                        bgl.glColor4f(color[0], color[1], color[2], 1.0)
                        
                        bgl.glLineStipple(3, 0x9999)
                        bgl.glEnable(bgl.GL_LINE_STIPPLE)
                        
                        bgl.glBegin(bgl.GL_LINE_STRIP)
                        bgl.glVertex3f(vertex_vec[0],vertex_vec[1],vertex_vec[2])
                        bgl.glVertex3f(vertex_vec_new[0],vertex_vec_new[1],vertex_vec_new[2])
                        bgl.glEnd()
                        bgl.glDisable(bgl.GL_LINE_STIPPLE)
                
                if self.point_type == "VERT":
                    if self.alt:
                        color = red
                    else:    
                        color = green
                elif self.point_type == "EDGE":
                    color = blue
                    if self.alt:
                        color = red
                    
                    bgl.glColor4f(color[0], color[1], color[2], 1.0)
                    bgl.glBegin(bgl.GL_LINE_STRIP)
                    p1 = obj.matrix_world * self.verts_edges_data[0] + y_offset
                    p2 = obj.matrix_world * self.verts_edges_data[1] + y_offset
                    bgl.glVertex3f(p1[0],p1[1],p1[2])
                    bgl.glVertex3f(p2[0],p2[1],p2[2])
                    bgl.glEnd()
                else:
                    color = yellow
                
                ### draw point
                self.draw_circle(vertex_vec_new,color,size=8)
                
                ### draw intersecting edge points
                color = yellow
                bgl.glColor4f(color[0], color[1], color[2], 1.0)
                for point in self.intersection_points:
                    self.draw_circle(point,[0,0,0],size=8)
                    self.draw_circle(point,[1,0,.5],size=6)   
                    #self.draw_circle(point,[1,0,.5],size=5)
                
            ### draw single vertices
            bm = bmesh.from_edit_mesh(obj.data)
            for vert in bm.verts:
                if not vert.hide:
                    if not vert.select:
                        self.draw_circle(obj.matrix_world * vert.co,[0,0,0],size=4)
                        self.draw_circle(obj.matrix_world * vert.co,[1,0,.5],size=2)
                    else:
                        self.draw_circle(obj.matrix_world * vert.co,[0,0,0],size=6)
                        self.draw_circle(obj.matrix_world * vert.co,[0,1.0,.5],size=4)    
                
                if not vert.hide:
                    if len(vert.link_edges) == 0:
                        if vert.select:
                            if self.contour_length == 0:
                                self.draw_circle(obj.matrix_world * vert.co,[1,.8,.8],size=8)
                        else:
                            self.draw_circle(obj.matrix_world * vert.co,[1,0,0],size=8)
                    
                    
            
            
                
            # restore opengl defaults
            bgl.glLineWidth(1)
            bgl.glDisable(bgl.GL_BLEND)
            bgl.glDisable(bgl.GL_LINE_SMOOTH)
            bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
            

class PickEdgeLength(bpy.types.Operator):
    bl_idname = "coa_tools.pick_edge_length"
    bl_label = "Pick Edge Length"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        mult = 1
#        if context.scene.coa_distance_constraint:
#            mult = bpy.context.space_data.region_3d.view_distance*.05
        
        for edge in bm.edges:
            if edge.select:
                #scene.coa_distance = (obj.matrix_world * (edge.verts[0].co - edge.verts[1].co)).magnitude/mult# edge.calc_length()/mult        
                scene.coa_distance = ((edge.verts[0].co - edge.verts[1].co)).magnitude/mult# edge.calc_length()/mult        
        bmesh.update_edit_mesh(obj.data)    
        return {"FINISHED"}
        