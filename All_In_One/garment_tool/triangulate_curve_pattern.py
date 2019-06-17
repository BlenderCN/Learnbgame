'''
Copyright (C) 2017 JOSECONSCO
Created by JOSECONSCO

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


from collections import Counter
from copy import deepcopy
from math import ceil, floor, pow, radians, sqrt
from statistics import median
from .utils.helper_functions import find_create_collection, frange, get_scale_mat

import bmesh
import bpy
import mathutils
import numpy as np
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_tri_2d

def check_line_intersects_outline(line_to_check, border_edges_lines_co):
    for brd_ed_idx, border_edge in enumerate(border_edges_lines_co):
        if line_to_check[0] in border_edge or line_to_check[1] in border_edge: #ignore if line ends intersect
            continue
        if mathutils.geometry.intersect_line_line_2d(line_to_check[0], line_to_check[1], border_edge[0], border_edge[1]): #return vector or None
            return True
    return False
    
def do_tris_from_pointcloud(outline_points, point_cloud, pocket_verts_co, point_spacing, triangulation_method, sourceTri_BVHT):
    point_cloud = point_cloud #+ pocket_verts_co
    bm = bmesh.new()
    vert_id = 0
    border_verts = []
    border_edges_lines = []  # for excluding edges that cross with outline in check_line_intersects_outline

    vert_boundary_id = bm.verts.layers.int.new('is_boundary_v')
    vert_boundary_id = bm.verts.layers.int['is_boundary_v']

    existing_edges_list = []
    edges_centers = []
    prev_vert = None
    for point_outline in outline_points:
        new_vert = bm.verts.new(point_outline)
        new_vert.index = vert_id
        new_vert[vert_boundary_id]=1
        border_verts.append(new_vert)
        if prev_vert:
            existing_edges_list.append(bm.edges.new([prev_vert, new_vert]))
            edges_centers.append((prev_vert.co + new_vert.co)/2 )
            border_edges_lines.append([prev_vert.co, point_outline])  # border vert points N is member of border_edges [N-1] and [N]
        prev_vert = new_vert
        vert_id +=1
    bm.verts.ensure_lookup_table()
    existing_edges_list.append(bm.edges.new([bm.verts[0], new_vert]) )  # close the boundary loop connecting last and firt vert
    edges_centers.append((prev_vert.co + new_vert.co)/2 )
    border_edges_lines.append([bm.verts[0].co, new_vert.co]) 

    point_cloud_count = len(point_cloud)
    if point_cloud_count > 0:
        kd_point_cloud_verts = mathutils.kdtree.KDTree(point_cloud_count)  # for marging adding
        point_cloud_first_vert = vert_id
        p_cloud_verts = []
        for point in point_cloud:
            new_vert = bm.verts.new(point)
            new_vert.index = vert_id
            p_cloud_verts.append(new_vert)
            kd_point_cloud_verts.insert(point, vert_id)
            vert_id +=1
        kd_point_cloud_verts.balance()

        bm.verts.ensure_lookup_table()
        #conntect point coloud verts in range range
        edge_keys = set() 
        for p_vert in p_cloud_verts:
            for (co, index, dist) in kd_point_cloud_verts.find_range(p_vert.co, point_spacing*1.2):
                if (index, p_vert.index) not in edge_keys and dist>0.0001:
                    #check if edge center is not outisde mesh..... Soo stupid but works
                    intersect_outline = check_line_intersects_outline([p_vert.co, bm.verts[index].co], border_edges_lines)
                    if not intersect_outline:
                        edge_keys.add((p_vert.index, index))
        for (v1,v2) in edge_keys:
            existing_edges_list.append(bm.edges.new([bm.verts[v1], bm.verts[v2]]))  # close the boundary loop connecting last and firt vert
            edges_centers.append((bm.verts[v1].co + bm.verts[v2].co)/2)


        if triangulation_method == 'SLOW': #use all edge detec cross by kd-tree
            kd_edges_centers = mathutils.kdtree.KDTree((point_cloud_count + len(outline_points))*3)  # for marging adding
            p_cloud_verts = []
            for i, edge_center in enumerate(edges_centers):
                kd_edges_centers.insert(edge_center, i)
            kd_edges_centers.balance()
            #bridge border verts and point cloud verts with one at least edge
            for brd_idx, border_vert in enumerate(border_verts):
                local_edge_centers = []
                close_point_cloud = kd_point_cloud_verts.find_range(border_vert.co, point_spacing * 2)
                for (co, index, dist) in close_point_cloud:  # Previouly only added one, but now we do intersect_previous_border_edges check
                    can_connect_to_vert = True
                    close_edge_centers = kd_edges_centers.find_range(border_vert.co, point_spacing * 1.6)
                    for (co2, neibor_edges_id, dist2) in close_edge_centers:  # if dosent intersect any close edge
                        close_edge = existing_edges_list[neibor_edges_id]
                        intersect_neibor_edges = check_line_intersects_outline([border_vert.co, bm.verts[index].co], [[close_edge.verts[0].co, close_edge.verts[1].co]])
                        if intersect_neibor_edges: #go to next vert
                            can_connect_to_vert = False
                            continue
                    if can_connect_to_vert:
                        existing_edges_list.append(bm.edges.new([border_vert, bm.verts[index]]) )
                        local_edge_centers.append((border_vert.co + bm.verts[index].co)/2)
                        can_connect_to_vert = True
                for center in local_edge_centers:
                    i += 1
                    kd_edges_centers.insert(center, i)
                if local_edge_centers:
                    kd_edges_centers.balance()
        else:# 'FAST'  use only prewious edges and outline edges for intersection
            # bridge border verts and point cloud verts with one at least edge
            previous_bridge_edges = []
            for brd_idx, border_vert in enumerate(border_verts):
                for (co, index, dist) in kd_point_cloud_verts.find_range(border_vert.co, point_spacing * 1.4):  # Previouly only added one, but now we do intersect_previous_border_edges check
                    intersect_border = check_line_intersects_outline([border_vert.co, bm.verts[index].co], border_edges_lines)
                    if not intersect_border:
                        intersect_previous_border_edges = check_line_intersects_outline([border_vert.co, bm.verts[index].co], previous_bridge_edges)
                        if not intersect_previous_border_edges:
                            bm.edges.new([border_vert, bm.verts[index]])
                            previous_bridge_edges.append([border_vert.co, bm.verts[index].co])
        
        for e in bm.edges:
            e_face_count = len(e.link_faces)
            if e_face_count == 2:  # edges has already 2 faces connected
                continue  # so go next edge

            e_is_boundary = True if e.verts[0][vert_boundary_id] and e.verts[1][vert_boundary_id] else False
            if e_is_boundary and e_face_count >= 1:  # edges has already one and only face connected
                continue  # so go next edge

            edge_link_faces_ids = [{f.verts[0].index, f.verts[1].index, f.verts[2].index} for f in e.link_faces]

            #go one since we have at least one face to connect to edge e (it seems)
            v1 = e.verts[0]
            v2 = e.verts[1]
            v1_neighbors = [e.other_vert(v1).index for e in v1.link_edges]
            v2_neighbors = [e.other_vert(v2).index for e in v2.link_edges]
            shared_verts_ids = list(set(v1_neighbors).intersection(v2_neighbors))
            shared_verts_ids_count = len(shared_verts_ids)

            if shared_verts_ids_count == 0:  # face can't be made for any side of edge. so just mark it as hole?
                continue

            if shared_verts_ids_count == 1:  # 1 face already exist so try making +1 (but check if dosent exits)
                if {v1.index, v2.index, shared_verts_ids[0]} not in edge_link_faces_ids:
                    bm.faces.new([v1, v2, bm.verts[shared_verts_ids[0]]])
                continue

            if shared_verts_ids_count == 2 and e_face_count == 0:
                bm.faces.new([v1, v2, bm.verts[shared_verts_ids[0]]])
                bm.faces.new([v1, v2, bm.verts[shared_verts_ids[1]]])
                continue

            if shared_verts_ids_count == 2:
                if {v1.index, v2.index, shared_verts_ids[0]} not in edge_link_faces_ids:
                    bm.faces.new([v1, v2, bm.verts[shared_verts_ids[0]]])
                if {v1.index, v2.index, shared_verts_ids[1]} not in edge_link_faces_ids:
                    bm.faces.new([v1, v2, bm.verts[shared_verts_ids[1]]])

        bmesh.ops.contextual_create(bm, geom=bm.edges)
        rem_faces = [face for face in bm.faces if len(face.verts) > len(outline_points) - 5]
        if len(rem_faces) > 0:
            bm.faces.remove(rem_faces[0])
        bmesh.ops.join_triangles(bm, faces=bm.faces, cmp_seam=False, cmp_sharp=False, cmp_uvs=False, cmp_vcols=False, cmp_materials=False, angle_face_threshold=3.1, angle_shape_threshold=3.1)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')
        # bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')

    else:
        bmesh.ops.contextual_create(bm, geom = bm.edges)
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')  # here becaouse above line breaks triangulation

    mesh = bpy.data.meshes.new(name="Cloth")
    bm.to_mesh(mesh)
    bm.free()
    del bm
    return mesh


def create_pocket_verts(target_mesh, pocket_verts_co_projected, seg_len):
    # Get a BMesh representation
    if len(pocket_verts_co_projected) == 0:
        return
    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(target_mesh)   # fill it in from a Mesh

    pattern_BVHTree = BVHTree.FromBMesh(bm, epsilon=0.0)
    
    # Modify the BMesh, can do anything here...
    bm.faces.ensure_lookup_table()
    faces_to_split = {} #faces to perform poke on
    hit_faces = []
    pocket_hit_verts = []  #verts from pocket_ outline that hit target mesh
    
    #get faces that are intersecting with pocket outline verts
    for i,pocket_vert_co in enumerate(pocket_verts_co_projected):
        # somewho increasing origin Z increases accuracy... lover z gives bigger margin around shape..
        location, normal, index, dist = pattern_BVHTree.ray_cast(Vector((pocket_vert_co.x, pocket_vert_co.y, 0.01)), Vector((0, 0, -200)), 201)
        if index is not None:
            if index in faces_to_split.keys():
                faces_to_split[index].append(pocket_vert_co)
            else:
                faces_to_split[index] = [pocket_vert_co]
                hit_faces.append(bm.faces[index])

    bm.faces.ensure_lookup_table()
    new_verts = []
    for face, (face_id, face_new_verts_co) in zip(hit_faces, faces_to_split.items()):
        ver_1 = face.verts[0]
        ver_2 = face.verts[1]
        vec_1_2 = (ver_2.co - ver_1.co) #no need to normalize
        if len(face_new_verts_co)>1:
            face_new_verts_co.sort(key=lambda x: vec_1_2.dot(x))  #sort by dot product len
        # split face from its ver[0] to vert2 - by adding loop throught coos
        generated_face_loop = bmesh.utils.face_split(face, vert_a=ver_1, vert_b=ver_2, coords=face_new_verts_co,  use_exist=True)
        new_verts.extend([v for v in face.verts if v.index == -1]) #old face will be connected now to new verts (with idx==-1)
        # new_faces.append(generated_face_loop[0])
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')
    bmesh.ops.beautify_fill(bm, faces=bm.faces, edges=bm.edges, method='AREA') #TODO: maybe run this only on gererated faces. How to find them

    #WARNING! THis may remove doubles on close boudnary verts (eg. on narrow vedges)
    #remove doubles execept new pocket verts
    boundary_verts = [vert for vert in bm.verts if vert.is_boundary]
    found_doubles = bmesh.ops.find_doubles(bm, verts=bm.verts, keep_verts=new_verts+boundary_verts, dist=seg_len/3)
    bmesh.ops.weld_verts(bm, targetmap=found_doubles['targetmap'])

    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(target_mesh)
    bm.free() 



def get_lattice_transformation(align_objs):
    ''' return (center, sizex, sizey, sizez) '''
    patter_count = len(align_objs)
    if patter_count == 1: #get local space cos we will align lattice to it anyway
        points = [point.co for point in align_objs[0].data.splines[0].bezier_points]
    else:
        points = []
        for curve in align_objs:
            points.extend([curve.matrix_world@point.co for point in curve.data.splines[0].bezier_points])
    
    np_points = np.array(points)    
    max_x = np.max(np_points[:, 0])
    max_y = np.max(np_points[:, 1])
    max_z = np.max(np_points[:, 2])
    min_x = np.min(np_points[:, 0])
    min_y = np.min(np_points[:, 1])
    min_z = np.min(np_points[:, 2])
    
    # center = Vector((max_x+min_x, max_y+min_y, max_z+min_z)) * 0.5
    vec_scale = Vector((max(max_x-min_x,0.1), max(max_y-min_y, 0.1), max(max_z-min_z, 0.1) )) * 0.5
    
    mat_loc =  Matrix.Translation(( (max_x+min_x)/2, (max_y+min_y)/2, (max_z+min_z)/2 )) 
    mat_sca = get_scale_mat(vec_scale)
    # mat_rot = align_objs[0].matrix_world.to_quaternion().to_matrix().to_4x4()

    if patter_count == 1:
        out_mat = align_objs[0].matrix_world  @ mat_loc  @ mat_sca 
    else:
        out_mat =  mat_loc @ mat_sca 

    return out_mat


def get_set_lattice(context,garment, name, align_objs):
    lattice_name = 'Lattice_'+ name
    if lattice_name in bpy.data.objects.keys():
        lattice_ob = bpy.data.objects[lattice_name]
    else:
        lattice = bpy.data.lattices.new(lattice_name)
        lattice.points_u = 3
        lattice.points_v = 3
        lattice.points_w = 3
        lattice_ob = bpy.data.objects.new(lattice_name, lattice)

        output_collection = bpy.data.collections['generated_'+ garment.name]
        if lattice_ob.name not in output_collection.objects.keys():
            output_collection.objects.link(lattice_ob)

    # lattice_ob.rotation_euler = align_obj.rotation_euler
    new_mat_transform = get_lattice_transformation(align_objs)
    lattice_ob.matrix_world = new_mat_transform
    return lattice_ob


def get_set_empty(context, garment, name, align_objs):
    ''' only make sense for one object...'''
    empty_name = 'Bend_' + name
    if empty_name in bpy.data.objects.keys():
        empty_ob = bpy.data.objects[empty_name]
    else:
        empty_ob = bpy.data.objects.new(empty_name, None)  # empty cos none
        # context.collection.objects.link(empty_ob)
        output_collection = bpy.data.collections['generated_'+garment.name]
        if empty_ob.name not in output_collection.objects.keys():
            output_collection.objects.link(empty_ob)
        empty_ob.empty_display_size = 0.02
        empty_ob.empty_display_type = 'CONE'
        
    empty_ob.matrix_world = align_objs[0].matrix_world
    rotmat = Matrix.Rotation(radians(-90.0), 4, "X")
    empty_ob.matrix_world = empty_ob.matrix_world @ rotmat
    empty_ob.scale = Vector((1, 1, 1))
    facing_center_vec = -1 * align_objs[0].matrix_world.translation.xy.to_3d()  # vector to center (0- transl.x, 0-trans.y, 0 - 0)
    context.scene.update() #to refersh broken empty_matrix world. Why...
    empty_up_vec = Vector((empty_ob.matrix_world[0][1], empty_ob.matrix_world[1][1], empty_ob.matrix_world[2][1])).normalized()
    is_facing_center = facing_center_vec.dot(empty_up_vec) #if negative we should flip the Y vector direction (rotated 180 deg X)
    if is_facing_center < 0: #make bend deform empty fece inside of coordinate system
        rot_180_deg_x = Matrix.Rotation(radians(180.0), 4, 'X')
        empty_ob.matrix_world = empty_ob.matrix_world @ rot_180_deg_x
    return empty_ob




class GTOOL_OT_Triangulate(bpy.types.Operator):
    bl_idname = 'garment.garment_to_mesh'
    bl_label = 'Convert To Mesh'
    bl_description = 'Convert to simulation ready mesh. \n'\
        'If icon on this button changes to cross, then something went wrong during last conversion. Try changing triangluaton method to Slow-HQ (also increasing resolution may help)'
    bl_options = {'REGISTER', 'UNDO'}

    garment_index: bpy.props.IntProperty()

    debug_info = 'Garment triangulation finished'
    conversion_went_ok = True

    def cache_cloth_vg(self,obj_name):
        self.backup_cloth_vg = {}
        if obj_name in bpy.context.scene.objects.keys():
            obj = bpy.data.objects[obj_name]
            for mod in obj.modifiers:
                if mod.type == 'CLOTH':
                    self.backup_cloth_vg['vertex_group_mass'] = mod.settings.vertex_group_mass
                    self.backup_cloth_vg['vertex_group_structural_stiffness'] = mod.settings.vertex_group_structural_stiffness
                    self.backup_cloth_vg['vertex_group_shear_stiffness'] = mod.settings.vertex_group_shear_stiffness
                    self.backup_cloth_vg['vertex_group_bending'] = mod.settings.vertex_group_bending
                    self.backup_cloth_vg['vertex_group_shrink'] = mod.settings.vertex_group_shrink
                    return

    def restore_cloth_vg(self, obj_name):
        if len(self.backup_cloth_vg) == 0:
            return
        obj = bpy.data.objects[obj_name]
        for mod in obj.modifiers:
            if mod.type == 'CLOTH':
                if self.backup_cloth_vg['vertex_group_mass'] in obj.vertex_groups.keys():
                    mod.settings.vertex_group_mass  = self.backup_cloth_vg['vertex_group_mass']
                else:
                    mod.settings.vertex_group_mass = ''

                if self.backup_cloth_vg['vertex_group_structural_stiffness'] in obj.vertex_groups.keys():
                    mod.settings.vertex_group_structural_stiffness  = self.backup_cloth_vg['vertex_group_structural_stiffness']
                else:
                    mod.settings.vertex_group_structural_stiffness = ''

                if self.backup_cloth_vg['vertex_group_shear_stiffness'] in obj.vertex_groups.keys():
                    mod.settings.vertex_group_shear_stiffness  = self.backup_cloth_vg['vertex_group_shear_stiffness']
                else:
                    mod.settings.vertex_group_shear_stiffness = ''

                if self.backup_cloth_vg['vertex_group_bending'] in obj.vertex_groups.keys():
                    mod.settings.vertex_group_bending  = self.backup_cloth_vg['vertex_group_bending']
                else:
                    mod.settings.vertex_group_bending = ''

                if self.backup_cloth_vg['vertex_group_shrink'] in obj.vertex_groups.keys():
                    mod.settings.vertex_group_shrink = self.backup_cloth_vg['vertex_group_shrink']
                else:
                    mod.settings.vertex_group_shrink = ''
                    
                return



    @staticmethod
    def get_segments_spacing(points):
        '''Return normalized points spacing len '''
        segments_points_spacing = []
        segment_len = 0
        previous_point = points[0]
        for point in points:
            point_diff_vec = Vector(point) - Vector(previous_point)
            segment_len += point_diff_vec.length
            previous_point = point
        segments_points_spacing.append(segment_len/len(points))
        median_spacing = median(segments_points_spacing)  # for point spacing  use the line with longest spacing legnth
        return median_spacing

    def get_segment_proportions(self, splinesSegments, resolution, obj_scale= 1):
        '''Return normalized list of segment lengths * res '''
        length_of_segments = []
        segments_points_spacing = []
        for segment in splinesSegments:  # for islands
            segment_len = 0
            previous_point = segment[0]
            for point in segment:
                point_diff_vec = Vector(point) - Vector(previous_point)
                segment_len += point_diff_vec.length
                previous_point = point
            length_of_segments.append(segment_len)
            segments_points_spacing.append(segment_len/len(segment))
        max_segment_len = max(length_of_segments)
        # median_spacing = median(segments_points_spacing)  # for point spacing  use the line with longest spacing legnth
        # normalize_maxSeg_len = 1/median_spacing  # 1meter/ max_diff_len = x.
        # N = S / 1meter  * Res   # s - len of segment
        return [max(ceil(resolution * seg_len ), 2) for seg_len in length_of_segments] # /1meter  - eg 12points/meter
         

    def curve_calc_normalized_segments_res(self, curve_obj , resolution):
        '''Return list of segments lengths normalized  '''
        
        spline = curve_obj.data.splines[0]
        uniform_segments_points = []
        points_count = len(spline.bezier_points)
        mat_scale = get_scale_mat(curve_obj.matrix_world.to_scale())
        for i in range(points_count):
            knot1 = mat_scale@spline.bezier_points[i].co
            handle1 = mat_scale@spline.bezier_points[i].handle_right
            knot2 = mat_scale@spline.bezier_points[(i+1) % points_count].co
            handle2 = mat_scale@spline.bezier_points[(i+1) % points_count].handle_left
            uniform_segments_points.append(mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, resolution))
        return self.get_segment_proportions(uniform_segments_points, resolution)



    def curve_resample(self, curve_obj , resolution):
        '''Return list of points for each 2D curve segment. Assume curve obj, has segment count dict assigned '''
        
        spline = curve_obj.data.splines[0]
        points_count = len(spline.bezier_points)
        normalized_seg_res = curve_obj['normalized_seg_res']  # this data is generated after sewing normalization step
        normalized_points = []

        mat_scale = get_scale_mat(curve_obj.matrix_world.to_scale())

        for i in range(points_count):
            knot1 = mat_scale@spline.bezier_points[i].co
            handle1 = mat_scale@spline.bezier_points[i].handle_right
            knot2 = mat_scale@spline.bezier_points[(i+1) % points_count].co
            handle2 = mat_scale@spline.bezier_points[(i+1) % points_count].handle_left
            normalized_points.append(mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, normalized_seg_res[i]))
        return normalized_points

    def proces_sewing_resolution(self, context,garment, cloth_res):
        #do the sewing
        orig_pattern_seg_res = {} #store map k: garment name V: list or segments lengths
        patter_segment_sum_res = {} #store map k: garment name V: list or segments lengths
        pattern_seg_occured_count = {} #store map k: garment name V: list or segments count
        pattern_segment_to_sewing = {}  # store map k: segment_idx V: [sewing_ids]
        for sewing_idx, sewing in enumerate(garment.garment_sewings): 
            if sewing.source_obj and sewing.source_obj.name in context.view_layer.objects.keys() and sewing.target_obj and sewing.target_obj.name in context.view_layer.objects.keys():

                if sewing.source_obj.name not in orig_pattern_seg_res.keys(): #store sewing lens in original_sewing_per_pattert_res
                    segments_res = self.curve_calc_normalized_segments_res(sewing.source_obj, cloth_res)
                    orig_pattern_seg_res[sewing.source_obj.name] = segments_res
                    patter_segment_sum_res[sewing.source_obj.name] = deepcopy(orig_pattern_seg_res[sewing.source_obj.name])
                    pattern_seg_occured_count[sewing.source_obj.name] = [1]*len(segments_res)  # one time each segment was counted
                    pattern_segment_to_sewing[sewing.source_obj.name] = {i:[] for i in range(len(segments_res)) }

                if sewing.target_obj.name not in orig_pattern_seg_res.keys(): #store sewing lens in original_sewing_per_pattert_res
                    segments_res = self.curve_calc_normalized_segments_res(sewing.target_obj, cloth_res)
                    orig_pattern_seg_res[sewing.target_obj.name] = segments_res
                    patter_segment_sum_res[sewing.target_obj.name] = deepcopy(orig_pattern_seg_res[sewing.target_obj.name])
                    pattern_seg_occured_count[sewing.target_obj.name] = [1]*len(segments_res)  # one time each segment was counted
                    pattern_segment_to_sewing[sewing.target_obj.name] = {i:[] for i in range(len(segments_res)) }

                # average_sewing_len = (original_sewing_per_pattert_res[garment_sewings.source_obj][garment_sewings.segment_id_from] + original_sewing_per_pattert_res[garment_sewings.target_obj][garment_sewings.segment_id_to])/2
                from_sewing_len = orig_pattern_seg_res[sewing.source_obj.name][sewing.segment_id_from]
                to_sewing_len =   orig_pattern_seg_res[sewing.target_obj.name][sewing.segment_id_to]

                patter_segment_sum_res[sewing.source_obj.name][sewing.segment_id_from] += to_sewing_len  # add mirrored sewing len from - to
                patter_segment_sum_res[sewing.target_obj.name][sewing.segment_id_to] += from_sewing_len  # add mirrored sewing len to - from

                pattern_seg_occured_count[sewing.source_obj.name][sewing.segment_id_from] += 1
                pattern_seg_occured_count[sewing.target_obj.name][sewing.segment_id_to] += 1

                pattern_segment_to_sewing[sewing.source_obj.name][sewing.segment_id_from].append(sewing_idx)
                pattern_segment_to_sewing[sewing.target_obj.name][sewing.segment_id_to].append(sewing_idx)
                
        for garment_mesh in garment.sewing_patterns:
            if garment_mesh.pattern_obj.name in context.view_layer.objects:
                if garment_mesh.pattern_obj.name in patter_segment_sum_res.keys():  # do the patterns that have sewing connected to them
                    patter_sum_ress = patter_segment_sum_res[garment_mesh.pattern_obj.name]
                    patter_sum_ress_fixed = [int(round(length / pattern_seg_occured_count[garment_mesh.pattern_obj.name][i])) for i, length in enumerate(patter_sum_ress)]
                    garment_mesh.pattern_obj['normalized_seg_res'] = patter_sum_ress_fixed
                else:  # do the patterns that have no sewing connected to them
                    garment_mesh.pattern_obj['normalized_seg_res'] = self.curve_calc_normalized_segments_res( garment_mesh.pattern_obj, cloth_res)

        if garment.enable_pockets:
            for pocket in garment.pockets: #calc pattern without normalization (no sewing )
                pocket.pocketObj['normalized_seg_res'] = self.curve_calc_normalized_segments_res(pocket.pocketObj, cloth_res)

    def proces_sewing_resolution2(self, context, garment, cloth_res):
        #store map k: garment name V: list or segments lengths
        orig_pattern_seg_res = {garment_mesh.pattern_obj.name:self.curve_calc_normalized_segments_res(garment_mesh.pattern_obj, cloth_res) for garment_mesh in garment.sewing_patterns}

        garment_sewings = context.scene.cloth_garment_data[self.garment_index].garment_sewings
        checked_sewing = []
        sewing_count = len(garment_sewings)
        sewing_to_check = [i for i in range(sewing_count)]

        def get_connected_sewing(current_sitch_idx, search_dir):
            ''' Search remaining sewing_to_check, for sewing connected to current_sitch_idx, by socket defined by search_dir'''
            ''' Return arra of pairt (child_sewing_id, next_direction_to_serach - 'target' or 'source')'''
            current_sitch = garment_sewings[current_sitch_idx]
            # if we came from source side, then search child toward Target side os sewing
            # elif we came from Target side, then search child toward Source side os sewing
            search_matching_pattern = current_sitch.source_obj.name if search_dir == 'source' else current_sitch.target_obj.name
            search_matching_segment = current_sitch.segment_id_from if search_dir == 'source' else current_sitch.segment_id_to

            child_sewing = []
            for sewing_id in sewing_to_check: #search sewing that are matching (source/target.patter, to_s_id/from_s_id) of current parent sewing
                if sewing_id != current_sitch_idx:
                    if garment_sewings[sewing_id].target_obj.name == search_matching_pattern and garment_sewings[sewing_id].segment_id_to == search_matching_segment:
                        # add sewing matching, and direction that we should follow next when searching for next children
                        child_sewing.append((sewing_id, 'source'))
                    if garment_sewings[sewing_id].source_obj.name == search_matching_pattern and garment_sewings[sewing_id].segment_id_from == search_matching_segment:
                        # add sewing matching, and direction that we should follow next when searching for next children
                        child_sewing.append((sewing_id, 'target'))

            return child_sewing


        def sewing_get_linked_res(current_sitch_idx, search_dir, first_run=False):
            ''' Return sum of segments, and ammount of connected sewing to searched sewing'''
            ''' search_dir - in which direction we go from current sewing - coming from  ('source' or 'target' ) '''
            child_sewing = get_connected_sewing(current_sitch_idx, search_dir=search_dir)

            #get current sewing data
            sewing = garment_sewings[current_sitch_idx]
            sewing_patter_out_dir = sewing.source_obj.name if search_dir == 'source' else sewing.target_obj.name
            sewing_id_out_dir = sewing.segment_id_from if search_dir == 'source' else sewing.segment_id_to
            current_sewing_res = orig_pattern_seg_res[sewing_patter_out_dir][sewing_id_out_dir]

            if len(child_sewing) == 0:
                if not first_run:
                    checked_sewing.append(current_sitch_idx)
                    sewing_to_check.remove(current_sitch_idx)
                return (1, current_sewing_res)  # TODO: get initial seg_res from orig_pattern_seg_res
            
            sum_child_sewing_lens = current_sewing_res  # we count at least itself once + child count
            sum_chilld_sewing_count = 1   # we count at least itself res once + child reses
            for (child_sewing_id, direction_to_search) in child_sewing:
                (sewing_count, sewing_sum_len) = sewing_get_linked_res(child_sewing_id, search_dir=direction_to_search)
                sum_chilld_sewing_count += sewing_count
                sum_child_sewing_lens += sewing_sum_len
            if not first_run:
                checked_sewing.append(current_sitch_idx)
                sewing_to_check.remove(current_sitch_idx)
            return (sum_chilld_sewing_count, sum_child_sewing_lens)

        
        #calculate connected sttiches point counts (res) 
        sewing_to_res = {} # maps  sewing_id: avg_res  
        i = 0
        while len(sewing_to_check) > 0:
            sewing = sewing_to_check[0]
            (sewing_count_1, sewing_sum_len_1) = sewing_get_linked_res(sewing, search_dir='source', first_run=True)  # get sewing in direction of sewing source
            (sewing_count_2, sewing_sum_len_2) = sewing_get_linked_res(sewing, search_dir='target')  # get sewing in direction of sewing target
            for checked_sewing in checked_sewing:
                sewing_to_res[checked_sewing] = int(round( (sewing_sum_len_1 + sewing_sum_len_2) / (sewing_count_1 + sewing_count_2) ))
            checked_sewing = []
            i += 1
            if i >= sewing_count:
                print('Too many loops. Some sewing may be broken. Cancelling')
                break

        #then transfer segments  point count from sewing to pattern segmets counts
        for garment_mesh in garment.sewing_patterns:  # first use default/ original values  from curve_calc_normalized_segments_res()
            garment_mesh.pattern_obj['normalized_seg_res'] = orig_pattern_seg_res[garment_mesh.pattern_obj.name]
        for sewing_id, avg_res in sewing_to_res.items():  # then assing res from computed sewing_to_res
            sewing = garment_sewings[sewing_id]
            sewing.source_obj['normalized_seg_res'][sewing.segment_id_from] = avg_res
            sewing.target_obj['normalized_seg_res'][sewing.segment_id_to] = avg_res

        #assing default values for pocket segments
        if garment.enable_pockets:
            for pocket in garment.pockets: #calc pattern without normalization (no sewing )
                pocket.pocketObj['normalized_seg_res'] = self.curve_calc_normalized_segments_res(pocket.pocketObj, cloth_res)
                

    def execute(self, context):
        garment = context.scene.cloth_garment_data[self.garment_index]
        self.generated_garment_meshes = {}  # k: curve pattern name, value: generated mesh name
        bpy.ops.garment.cleanup(garment_index = self.garment_index)
        self.generated_garment_meshes.clear()
        sewing_objs_names = []
        self.proces_sewing_resolution2(context, garment, garment.cloth_res)
        #convert the curve patter to mesh pattern

        output_collection_name = 'generated_'+garment.name
        output_collection = find_create_collection(context.scene.collection, output_collection_name)

        if garment.enable_pockets:
            for pocket in garment.pockets:
                self.generated_garment_meshes[pocket.pocketObj.name] = self.create_mesh_cloth(context,  garment, pocket.pocketObj)
                sewing_objs_names.extend(self.create_pocket_sewing(context, pocket))

            
        for sewing_patterns in garment.sewing_patterns:
            self.generated_garment_meshes[sewing_patterns.pattern_obj.name] = self.create_mesh_cloth(context,  garment, sewing_patterns.pattern_obj)
        
        if garment.enable_pins:
            sewing_objs_names.extend(self.create_pin_sewing(context, garment.pins, garment.name))
        #do the sewing
        for garment_sewing in garment.garment_sewings:
            if garment_sewing.source_obj and garment_sewing.source_obj.name in self.generated_garment_meshes.keys() and garment_sewing.target_obj and garment_sewing.target_obj.name in self.generated_garment_meshes.keys():
                sewing_objs_names.append(self.create_mesh_sewing(context, garment_sewing, garment) )

        merged_objs = sewing_objs_names+list(self.generated_garment_meshes.values())
        for obj_name in merged_objs:
            if obj_name not in output_collection.objects.keys():
                output_collection.objects.link(bpy.data.objects[obj_name])

        self.cache_cloth_vg(garment.name)
        if garment.merge_patterns and garment.name != '':
            merged_obj = self.merge_objs(context, merged_objs, garment.smooth_strength, garment)
            self.setup_modifiers(context, merged_obj, garment)
            # setup_keyframes(context, garment)
            if len(output_collection.objects)==0:
                bpy.data.collections.remove(output_collection)
            for modifier in merged_obj.modifiers:
                if modifier.type == 'CLOTH':
                    override = {'scene': context.scene, 'active_object': merged_obj, 'point_cache': modifier.point_cache}
                    bpy.ops.ptcache.free_bake(override)
                    break
            self.restore_cloth_vg(garment.name)
        self.report({'INFO'}, self.debug_info)
        garment.tri_convert_ok = self.conversion_went_ok 
        return {'FINISHED'}

    def setup_modifiers(self, context, merged_obj, garment):
        ''' add bend, lattice modifiers. Also make sure bend is before lattice, which is before cloth'''
        CLOTH_NOT_EXIST = 55
        LATTICE_NOT_EXIST = 54
        garment_obj = merged_obj
        grouped_modifiers_stack = {} # k -> V :  mod.type -> [(idx, mod.name),...]
        modifiers_names = []
        mod_len = len(garment_obj.modifiers)
        for i,mod in enumerate(garment_obj.modifiers): #CLOTH, SIMPLE_DEFORM, LATTICE
            modifiers_names.append(mod.name)
            if mod.type not in grouped_modifiers_stack.keys():
                grouped_modifiers_stack[mod.type] = []
            grouped_modifiers_stack[mod.type].append((i,mod.name))
        
        first_cloth_idx = grouped_modifiers_stack['CLOTH'][0][0] if 'CLOTH' in grouped_modifiers_stack.keys() else CLOTH_NOT_EXIST
        first_lattice_idx = grouped_modifiers_stack['LATTICE'][0][0] if 'LATTICE' in grouped_modifiers_stack.keys() else LATTICE_NOT_EXIST

        #remove existing mods if hey are referencing groups, objects that no longer exits
        for mod_name in modifiers_names:
            mod = garment_obj.modifiers[mod_name]
            if hasattr(mod, 'vertex_group'):
                if mod.vertex_group and mod.vertex_group not in garment_obj.vertex_groups.keys():
                    garment_obj.modifiers.remove(mod)
                    mod = None
            if mod and hasattr(mod, 'object'):
                if mod.object and mod.object not in context.scene.objects.keys():
                    garment_obj.modifiers.remove(mod)
                    mod = None
            
        def check_remove_mod(name):
            if name in garment_obj.modifiers.keys():
                garment_obj.modifiers.remove(garment_obj.modifiers[name])
            if name in bpy.data.objects.keys(): #remove also empty or lattice helper
                helper_obj = bpy.data.objects[name]
                if helper_obj.type in {'LATTICE', 'EMPTY'}:
                    bpy.data.objects.remove(helper_obj)

        def set_mod(name, align_objs, mod_type):
            nonlocal mod_len, first_cloth_idx, first_lattice_idx #gives ability to update nonlacol var
            if mod_type == 'LATTICE':
                mod_name = 'Lattice_' + name
                mod_target_obj = get_set_lattice(context, garment, name=name, align_objs=align_objs)
            elif mod_type == 'SIMPLE_DEFORM':
                mod_name = 'Bend_' + name
                mod_target_obj = get_set_empty(context, garment,  name=name, align_objs=align_objs)
            modifier_exist = True if mod_name in garment_obj.modifiers.keys() else False
            if modifier_exist:
                modifier = garment_obj.modifiers[mod_name]
            else:
                modifier = garment_obj.modifiers.new(name=mod_name, type=mod_type)
                modifier.show_expanded = False
                new_mod_id = mod_len
                # move it befor cloth mods
                while (new_mod_id > first_cloth_idx and new_mod_id >= 1):
                    bpy.ops.object.modifier_move_up(modifier=modifier.name)
                    new_mod_id -= 1
                if mod_type == 'SIMPLE_DEFORM': #move before lattice mods
                    while (new_mod_id >= first_lattice_idx and new_mod_id >= 1): #move it befor lattice and cloth mods
                        bpy.ops.object.modifier_move_up(modifier=modifier.name)
                        new_mod_id -= 1
                mod_len += 1
                #move up lattice and cloth mods if they exist
                first_cloth_idx = first_cloth_idx +  1 if first_cloth_idx != CLOTH_NOT_EXIST else first_cloth_idx
                first_lattice_idx = first_lattice_idx +  1 if first_lattice_idx != LATTICE_NOT_EXIST else first_lattice_idx
            modifier.vertex_group = name
            if mod_type == 'LATTICE':
                modifier.object = mod_target_obj
            else:
                modifier.deform_method = 'BEND'
                modifier.deform_axis = 'Z'
                if not modifier_exist:
                    modifier.angle = 3.14159
                modifier.origin = mod_target_obj

        for garment_mesh in garment.sewing_patterns:
            if garment_mesh.add_bend_deform:
                set_mod(garment_mesh.pattern_obj.name, align_objs=[garment_mesh.pattern_obj], mod_type='SIMPLE_DEFORM')
            else:
                check_remove_mod('Bend_' + garment_mesh.pattern_obj.name)
                
            if garment_mesh.add_lattice:
                set_mod(garment_mesh.pattern_obj.name, align_objs=[garment_mesh.pattern_obj], mod_type='LATTICE')
            else:
                check_remove_mod('Lattice_' + garment_mesh.pattern_obj.name)

        for vert_group in garment.generated_vgroups:
            if len(vert_group.vgroups_patterns):
                if vert_group.add_bend_deform:
                    set_mod(vert_group.name,  align_objs=[bpy.data.objects[name] for name in vert_group.vgroups_patterns], mod_type='SIMPLE_DEFORM')
                else:
                    check_remove_mod('Bend_'+vert_group.name)
                if vert_group.add_lattice:
                    set_mod(vert_group.name,  align_objs=[bpy.data.objects[name] for name in vert_group.vgroups_patterns], mod_type='LATTICE')
                else:
                    check_remove_mod('Lattice_'+vert_group.name)
        return


    def merge_objs(self, context, merged_objs, cloth_smooth, garment):
        output_collection = bpy.data.collections['generated_'+garment.name]
        bpy.ops.object.select_all(action='DESELECT')
        for obj_name in merged_objs:
            obj = bpy.data.objects[obj_name]
            obj.select_set(True)
            context.view_layer.objects.active = obj
        new_cloth_obj = context.view_layer.objects.active
        new_cloth_obj.select_set(True)
        
        obj_list = [bpy.data.objects[name] for name in merged_objs]
        override = {'active_object': new_cloth_obj, 'selected_editable_objects': obj_list}
        bpy.ops.object.join(override)
        bpy.ops.object.transform_apply(override, location=True, rotation=True, scale=True)
        context.view_layer.objects.active = new_cloth_obj
        

        mesh = new_cloth_obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        wire_edges = [edge for edge in bm.edges if edge.is_wire]
        # boundary_verts = [vert for vert in bm.verts if vert.is_boundary]
        boundary_verts = [vert for vert in bm.verts if not vert.is_wire]

        kd_boundary_verts = mathutils.kdtree.KDTree(len(boundary_verts))  # for marging adding
        for point in boundary_verts:
            kd_boundary_verts.insert(point.co, point.index)
        kd_boundary_verts.balance()

        edges_to_create  = set()
        for edge in wire_edges:
            co, index1, dist = kd_boundary_verts.find(edge.verts[0].co)
            co, index2, dist = kd_boundary_verts.find(edge.verts[1].co)
            if (index2, index1) not in edges_to_create:
                edges_to_create.add((index1, index2)) #DONE: maybe check if idx2,idx1  is in edges.
        for (index1, index2) in edges_to_create:
            try:
                bm.edges.new([bm.verts[index1], bm.verts[index2]])
            except:
                print(f'Error when adding edge from verts:{index1} TO: {index2}')

        verts_from_wire_edges = [edge.verts[0] for edge in wire_edges] + [edge.verts[1] for edge in wire_edges]
        for vert in verts_from_wire_edges:
            try:
                bm.verts.remove(vert)
            except:
                print(f'Error when removing verts id: {index1}')
                self.debug_info = 'Generated mesh seems corrupted. Try Slow(HQ) triangulation method.'
                self.conversion_went_ok = False
        # bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        boundary_verts = [vert.index for vert in bm.verts if vert.is_boundary]
        non_boundary_verts = [vert.index for vert in bm.verts if not vert.is_boundary]
        # bm.verts.ensure_lookup_table()
        # b_verts1 = [edge.verts[0].index for edge in bm.edges if edge.is_wire]
        # b_verts2 = [edge.verts[1].index for edge in bm.edges if edge.is_wire]

        bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        if garment.add_border_mask:
            vg = new_cloth_obj.vertex_groups.new(name = "border_mask")
            vg.add(boundary_verts, 1, "REPLACE")
        
        if garment.add_non_border_mask:
            vg = new_cloth_obj.vertex_groups.new(name = "non_border_mask")
            vg.add(non_boundary_verts, 1, "REPLACE")

        bpy.ops.object.modifier_add(type='CLOTH')
        bpy.context.object.modifiers["Cloth"].settings.use_sewing_springs = True
        bpy.context.object.modifiers["Cloth"].settings.vertex_group_shrink = "Group"
        bpy.context.object.modifiers["Cloth"].settings.sewing_force_max = 2
        override = {'active_object': new_cloth_obj, 'selected_objects': [new_cloth_obj], 'selected_editable_objects': [new_cloth_obj]}
        if cloth_smooth > 0:
            bpy.ops.object.cloth_smooth(override, iteration_amount=cloth_smooth)
        if garment.name in bpy.data.objects.keys():  # copy data from new generated garment mesh to previously generated garment mesh
            previous_obj = bpy.data.objects[garment.name]
            previous_obj.vertex_groups.clear()
            for mat in previous_obj.data.materials:
                new_cloth_obj.data.materials.append(mat)
            old_mesh_name = previous_obj.data.name[:]
            previous_obj.data.name +='_old' #previous mesh name _old
            #vgroups would are be transfered here
            previous_obj.data = new_cloth_obj.data
            previous_obj.data.name = old_mesh_name

            #transfer ver groups, cos above wont do it.
            if previous_obj.name not in context.scene.objects.keys():
                output_collection.objects.link(previous_obj)
            override = {'active_object': previous_obj, 'selected_objects': [
                new_cloth_obj], 'selected_editable_objects': [new_cloth_obj]}
            bpy.ops.object.vertex_group_copy_to_linked(override)

            # bpy.ops.object.delete(override, use_global=False)
            bpy.data.objects.remove(new_cloth_obj)
            MergedObj =  previous_obj
        else: #use merged obj as output
            new_cloth_obj.name = garment.name
            MergedObj = new_cloth_obj

        
        if MergedObj.name not in context.scene.objects.keys(): 
            output_collection.objects.link(bpy.data.objects[MergedObj.name])
        if MergedObj.name in context.view_layer.objects.keys():
            MergedObj.select_set(True)
        context.view_layer.objects.active = MergedObj
        return MergedObj
        

    def create_mesh_sewing(self, context, garment_sewing, garment):
        obj1 = bpy.data.objects[self.generated_garment_meshes[garment_sewing.source_obj.name]]
        obj2 = bpy.data.objects[self.generated_garment_meshes[garment_sewing.target_obj.name]]

        sewing1_verts_ids = obj1['segments_verts'][garment_sewing.segment_id_from]
        sewing2_verts_ids = obj2['segments_verts'][garment_sewing.segment_id_to]

        vert_stich_01 = [obj1.matrix_world@obj1.data.vertices[sewing_vert].co for sewing_vert in sewing1_verts_ids]
        vert_stich_02 = [obj2.matrix_world@obj2.data.vertices[sewing_vert].co for sewing_vert in sewing2_verts_ids]
        if garment_sewing.flip:
            vert_stich_02 = list(reversed(vert_stich_02))

        mesh = bpy.data.meshes.new(name="Stitches")
        sewing_count = len(vert_stich_01)
        triagles = []
        edges = [(x ,sewing_count + x) for x in range(sewing_count)]
        mesh.from_pydata(vert_stich_01 + vert_stich_02 , edges, triagles)

        new_sewing_obj = bpy.data.objects.new("Stitches", mesh)  # add a new object using the mesh
        return new_sewing_obj.name

    def create_pocket_sewing(self, context, pocket_prop): 
        generated_pocket_mesh = bpy.data.objects[self.generated_garment_meshes[pocket_prop.pocketObj.name]]
        target_pattern = pocket_prop.target_pattern  # cos we don need 'segments_verts' from it
        sewing_ids = [int(i) for i in pocket_prop.pocket_sewing]
        output_sewing_names = []
        previous_sewing = sewing_ids[-1]
        for sewing_id in sewing_ids:
            sewing_count = len(generated_pocket_mesh['segments_verts'])
            #if current sewing and prevous are neibors then skip first vert\
            pocket_verts_ids = generated_pocket_mesh['segments_verts'][sewing_id][1:] if (
                sewing_id-previous_sewing == 1) or (sewing_id-previous_sewing == -1*sewing_count+1) else generated_pocket_mesh['segments_verts'][sewing_id][:]
            previous_sewing = sewing_id

            target_mat_inv = target_pattern.matrix_world.inverted()
            pocket_mat_inv = generated_pocket_mesh.matrix_world.inverted()

            pocket_verts_boundary_co = [generated_pocket_mesh.matrix_world@generated_pocket_mesh.data.vertices[sewing_vert].co for sewing_vert in pocket_verts_ids]
            target_verts_co = [target_mat_inv@generated_pocket_mesh.matrix_world@generated_pocket_mesh.data.vertices[sewing_vert].co for sewing_vert in pocket_verts_ids]
            target_verts_co_projected = [Vector((p.x, p.y, 0)) for p in target_verts_co]
            target_verts_co_transformed = [target_pattern.matrix_world @ p for p in target_verts_co_projected]

            mesh = bpy.data.meshes.new(name="pocket_sewing"+str(sewing_id))
            sewing_count = len(pocket_verts_boundary_co)
            triagles = []
            edges = [(x ,sewing_count + x) for x in range(sewing_count)]
            mesh.from_pydata(pocket_verts_boundary_co + target_verts_co_transformed, edges, triagles)

            new_sewing_obj = bpy.data.objects.new(generated_pocket_mesh.name + "Stitch"+str(sewing_id), mesh)  # add a new object using the mesh
            output_sewing_names.append(new_sewing_obj.name)
        return output_sewing_names


    def create_pin_sewing(self, context, pins_prop, garment_name): 
        pin_sewing_verts = []
        for pin in pins_prop:
            generated_patter_source = bpy.data.objects[self.generated_garment_meshes[pin.source_obj.name]]
            generated_patter_target = bpy.data.objects[self.generated_garment_meshes[pin.target_obj.name]]
            pin_sewing_verts.append(generated_patter_source.matrix_world @ Vector(pin.source_co))
            pin_sewing_verts.append(generated_patter_target.matrix_world @ Vector(pin.target_co))

        sewing_count = len(pins_prop)
        mesh = bpy.data.meshes.new(name=garment_name+"pins_sewing")
        triagles = []
        edges = [(2*x, 1 + 2*x) for x in range(sewing_count)]
        mesh.from_pydata(pin_sewing_verts, edges, triagles)

        new_sewing_obj = bpy.data.objects.new(garment_name+"pins_sewing", mesh)  #TODO: add garment name. eg: jacket_pins
        return [new_sewing_obj.name]
    

    def create_mesh_cloth(self, context, garment, pattern_curve_obj):
        used_pockets = [pocket for pocket in garment.pockets if pocket.target_pattern == pattern_curve_obj]

        mat_scale = get_scale_mat(pattern_curve_obj.matrix_world.to_scale()) #cos we have to scale up generated mesh objs

        #get verts from pockets
        target_mat_inv = pattern_curve_obj.matrix_world.inverted()
        pocket_verts_co_projected = []
        if garment.enable_pockets:
            for pocket in used_pockets: #TODO: change it to list of list of points (pocket outlines) ? NONEED
                generated_pocket_mesh_name = self.generated_garment_meshes[pocket.pocketObj.name]
                generated_pocket_mesh = bpy.data.objects[generated_pocket_mesh_name]
                pocket_sewing = [int(i) for i in pocket.pocket_sewing]
                pocket_sewing.sort()
                sewing_count = len(generated_pocket_mesh['segments_verts'])  # cos  pocket.pocket_sewing - is EnumProp with only selected items
                if sewing_count>0:
                    previous_sewing = pocket_sewing[-1]
                    for sewing_id in pocket_sewing:
                        #if current sewing and prevous are neibors then skip first vert\
                        pocket_verts_ids = generated_pocket_mesh['segments_verts'][sewing_id][1:] if (
                            sewing_id-previous_sewing == 1) or (sewing_id-previous_sewing == -1*sewing_count+1) else generated_pocket_mesh['segments_verts'][sewing_id][:]
                        target_verts_co = [mat_scale@target_mat_inv@generated_pocket_mesh.matrix_world@
                                        generated_pocket_mesh.data.vertices[sewing_vert].co for sewing_vert in pocket_verts_ids]
                        pocket_verts_co_projected.extend([Vector((p.x, p.y, 0)) for p in target_verts_co])
                        previous_sewing = sewing_id
            pocket_verts_count = len(pocket_verts_co_projected)
        
        # if pocket_verts_count > 0: #OLD: do not add point from point grid, if to close to pocket_verts
        #     kd_pocket_verts = mathutils.kdtree.KDTree(pocket_verts_count)  # for marging adding
        #     for i, point in enumerate(pocket_verts_co_projected):
        #         kd_pocket_verts.insert(point, i)
        #     kd_pocket_verts.balance()

        pin_verts_co = []
        if garment.enable_pins:
            for pin in garment.pins: #assume pins co are in obj local space...
                if pin.source_obj == pattern_curve_obj:
                    # pin_verts_co.append(mat_scale.inverted() @ pin.source_obj.matrix_world @ Vector(pin.source_co))
                    pin_verts_co.append(mat_scale @ Vector(pin.source_co))
                elif pin.target_obj == pattern_curve_obj:
                    # pin_verts_co.append(mat_scale.inverted() @ pin.target_obj.matrix_world @ Vector(pin.target_co))
                    pin_verts_co.append( mat_scale  @ Vector(pin.target_co))


        resampled_curve_segments = self.curve_resample(pattern_curve_obj, garment.cloth_res)

        segments_points_flat = []
        prev_segments_len = 0
        cache_segments_vert_ids = []
        for i,segment in enumerate(resampled_curve_segments):  #add cloth sillayette
            seg_len = len(segment)
            segments_points_flat.extend(segment[:-1])
            cache_segments_vert_ids.append([x for x in range(prev_segments_len-i,prev_segments_len+seg_len-i)])
            prev_segments_len +=seg_len
        cache_segments_vert_ids[-1][-1] = 0  #loop and close last vert

        kd_border_verts = mathutils.kdtree.KDTree(len(segments_points_flat)) #for marging adding
        for i,point in enumerate(segments_points_flat):
            kd_border_verts.insert(point, i)
        kd_border_verts.balance()

        sourceTri_BVHT = BVHTree.FromPolygons(segments_points_flat, [tuple(i for i in range(len(segments_points_flat)))], all_triangles=False)  # [0,1,2] - polygon == vert indices list
        
        # sub_segmentLen = segments_points_flat[1] -  segments_points_flat[0]
        # seg_len = sub_segmentLen.length
        seg_len = self.get_segments_spacing(segments_points_flat)

        #generate point cloud in shape of resampled curve outline
        outline_as_np = np.array(segments_points_flat)
        # outline_as_np = np.einsum('ij,aj->ai', mat, outline_as_np))  # mat times point list
        max_x = np.max(outline_as_np[:,0])
        min_x = np.min(outline_as_np[:,0])
        max_y = np.max(outline_as_np[:,1])
        min_y = np.min(outline_as_np[:,1])
        point_cloud = []
        i = 0
        # seg_len /= obj_scale
        for y in frange(min_y, max_y, seg_len):
            i += 1
            for x in frange(min_x, max_x, seg_len):  # add evenly spaced out grid of verts
                x_mod = x + seg_len / 2  if i % 2 == 0 else x
                point = Vector((x_mod,y,0))
                location, normal, index, dist = sourceTri_BVHT.ray_cast(Vector((x_mod,y,10)), Vector((0,0,-10)), 100) #somewho increasing origin Z increases accuracy... lover z gives bigger margin around shape..
                if index is not None:
                    location2, index2, dist2 = kd_border_verts.find(Vector((x_mod,y,0))) #skip points to close to border / give margin 
                    if dist2 < seg_len*2/3: # point to close to border
                        continue
                    # if pocket_verts_count>0: #do not add point from point grid, if to close to pocket_verts
                    #     location3, index3, dist3 = kd_pocket_verts.find(Vector((x_mod,y,0))) #skip points to close to border / give margin 
                    #     if dist3 < seg_len*0.75:  # point to close to border
                    #         continue
                    point_cloud.append(point)
        

        # returns face as [(x,y,z) ...] list verre x,y,z are verrt ids.
        new_mesh = do_tris_from_pointcloud(segments_points_flat, point_cloud, pocket_verts_co_projected, seg_len, garment.triangulation_method, sourceTri_BVHT)

        if garment.enable_pockets:
            create_pocket_verts(new_mesh, pocket_verts_co_projected+pin_verts_co, seg_len)

        new_mesh.transform(mat_scale.inverted())
        new_cloth_obj = bpy.data.objects.new(pattern_curve_obj.name+"_pattern", new_mesh)  # add a new object using the mesh
        vg = new_cloth_obj.vertex_groups.new( name = pattern_curve_obj.name)
        vg.add([i for i in range(len(new_mesh.vertices))], 1, "ADD")

        for new_groups in garment.generated_vgroups:
            if pattern_curve_obj.name in new_groups.vgroups_patterns:
                vg = new_cloth_obj.vertex_groups.new(name = new_groups.name)
                vg.add([i for i in range(len(new_mesh.vertices))], 1, "ADD")

        new_cloth_obj['segments_verts'] = cache_segments_vert_ids

        bpy.data.collections['generated_'+garment.name].objects.link(new_cloth_obj)  # put the object into the scene (link)
        new_cloth_obj.select_set(True)  # select object
        pattern_curve_obj.select_set(False)  # select object
        context.view_layer.objects.active = new_cloth_obj  # set as the active object in the scene
        new_cloth_obj.matrix_world = pattern_curve_obj.matrix_world
        new_cloth_obj.data.show_double_sided = True

        return new_cloth_obj.name
