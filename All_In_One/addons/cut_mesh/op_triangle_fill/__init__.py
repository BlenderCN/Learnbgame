'''
Created on Jul 12, 2016

@author: Patrick
'''
import math
import numpy as np
import time

import bpy
import bmesh
from mathutils import Vector

from bpy.props import FloatProperty, BoolProperty, IntProperty, EnumProperty
from ..bmesh_fns import edge_loops_from_bmedges, join_bmesh
from ..common.maths import delta_angles
from ..common.debug import sort_objects_by_angles

def relax_bmesh(bme, verts, exclude, iterations = 1, spring_power = .1):
    '''
    takes verts
    '''
    for j in range(0,iterations):
        deltas = dict()
        #edges as springs
        for i, bmv0 in enumerate(verts):
            
            if bmv0.index in exclude: continue
            
            avg_loc = Vector((0,0,0))           
            for ed in bmv0.link_edges:
                avg_loc += ed.other_vert(bmv0).co
            avg_loc *= 1/len(bmv0.link_edges)
                
            deltas[bmv0.index] = spring_power * (avg_loc - bmv0.co)  #todo, normalize this to average spring length?
                  
        for i in deltas:
            bme.verts[i].co += deltas[i]
                       
def collapse_short_edges(bm,boundary_edges, interior_edges,threshold=.5):
    '''
    collapses edges shorter than threshold * average_edge_length
    '''
    ### collapse short edges
    edges_len_average = sum(ed.calc_length() for ed in interior_edges)/len(interior_edges)

    boundary_verts = set()
    for ed in boundary_edges:
        boundary_verts.update([ed.verts[0], ed.verts[1]])
        
    interior_verts = set()
    for ed in interior_edges:
        interior_verts.update([ed.verts[0], ed.verts[1]])
        
    interior_verts.difference_update(boundary_verts)
    bmesh.ops.remove_doubles(bm,verts=list(interior_verts),dist=edges_len_average*threshold)

def average_edge_cuts(bm,edges_boundary, edges_interior, cuts=1):
    ### subdivide long edges
    edges_count = len(edges_boundary)
    shortest_edge = min(edges_boundary, key = lambda x: x.calc_length())
    shortest_l = shortest_edge.calc_length()
    
    edges_len_average = sum(ed.calc_length() for ed in edges_boundary)/edges_count

    spread = edges_len_average/shortest_l
    if spread > 5:
        print('seems to be a large difference in edge lenghts')
        print('going to use 1/2 average edge ength as target instead of min edge')
        target = .5 * edges_len_average
    else:
        target = shortest_l
        
    subdivide_edges = []
    for edge in edges_interior:
        cut_count = int(edge.calc_length()/target)*cuts
        if cut_count < 0:
            cut_count = 0
        if not edge.is_boundary:
            subdivide_edges.append([edge,cut_count])
    for edge in subdivide_edges:
        bmesh.ops.subdivide_edges(bm,edges=[edge[0]],cuts=edge[1]) #perhaps....bisect and triangulate
                       
def triangle_fill_loop(bm, eds):
    geom_dict = bmesh.ops.triangle_fill(bm,edges=eds,use_beauty=True)
    if geom_dict["geom"] == []:
        return False, geom_dict
    else:
        return True, geom_dict

def triangulate(bm,fs):
    new_geom = bmesh.ops.triangulate(bm,faces=fs, ngon_method = 0, quad_method = 1) 
    return new_geom

def smooth_verts(bm, verts_smooth, iters = 10):
    for i in range(iters):
        #bmesh.ops.smooth_vert(bm,verts=smooth_verts,factor=1.0,use_axis_x=True,use_axis_y=True,use_axis_z=True)    
        bmesh.ops.smooth_vert(bm,verts=verts_smooth,factor=1.0,use_axis_x=True,use_axis_y=True,use_axis_z=True)    
   
def clean_verts(bm, interior_faces):
    ### find corrupted faces
    faces = []     
    for face in interior_faces:
        i = 0
        for edge in face.edges:
            if not edge.is_manifold:
                i += 1
        if i == len(face.edges):
            faces.append(face)
    print('deleting %i lonely faces' % len(faces))                 
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
    print('collapsing %i loose or otherwise strange edges' % len(edges))
    bmesh.ops.collapse(bm,edges=edges)
            
    verts = []
    for vert in bm.verts:
        if len(vert.link_edges) in [3,4] and not vert.is_boundary:
            verts.append(vert)
            
    print('dissolving %i weird verts after collapsing edges' % len(verts))
    bmesh.ops.dissolve_verts(bm,verts=verts)

def calc_angle(v):
                
    #use link edges and non_man eds
    eds_non_man = [ed for ed in v.link_edges if len(ed.link_faces) == 1]
    if len(eds_non_man) == 0:
        print('this is not a hole perimeter vertex')
        return 2 * math.pi, None, None
        
    eds_all = [ed for ed in v.link_edges]
    
    #shift list to start with a non manifold edge if needed
    base_ind = eds_all.index(eds_non_man[0])
    eds_all = eds_all[base_ind:] + eds_all[:base_ind]
    
    #vector representation of edges
    eds_vecs = [ed.other_vert(v).co - v.co for ed in eds_all]
    
    if len(eds_non_man) != 2:
        print("more than 2 non manifold edges, loop self intersects or there is a dangling edge")
        return 2 * math.pi, None, None
    
    va = eds_non_man[0].other_vert(v)
    vb = eds_non_man[1].other_vert(v)
    
    
    
    Va = va.co - v.co
    Vb = vb.co - v.co
    
    angle = Va.angle(Vb)
    
    #check for connectivity
    if len(eds_all) == 2:
        if any([ed.other_vert(va) == vb for ed in vb.link_edges]):
            #already a tri over here
            print('va and vb connect')
            return 2 * math.pi, None, None
    
        elif any([f in eds_non_man[0].link_faces for f in eds_non_man[1].link_faces]):
            print('va and vb share face')
            return 2 * math.pi, None, None
        
        else: #completely regular situation
            
            if Va.cross(Vb).dot(v.normal) < 0:
                print('keep normals consistent reverse')
                return angle, vb, va
            else:
                return angle, va, vb
    
    elif len(eds_all) > 2:
        #sort edges ccw by normal, starting at eds_nm[0]
        eds_sorted = sort_objects_by_angles(v.normal, eds_all, eds_vecs)
        vecs_sorted = [ed.other_vert(v).co - v.co for ed in eds_sorted]
        deltas = delta_angles(v.normal, vecs_sorted)
        ed1_ind = eds_sorted.index(eds_non_man[1])
        
        #delta_forward = sum(deltas[:ed1_ind])
        #delta_reverse = sum(deltas[ed1_ind:])
        
        if Va.cross(Vb).dot(v.normal) > 0:
        
            if ed1_ind == 1:
            

                return angle, va, vb
            
            elif ed1_ind == (len(eds_sorted) - 1):
                
                return 2*math.pi - angle, vb, va
            
            else:
                #PROBLEMS!
                #print("Sorted angle is %i in the list" % ed1_ind)
                return angle, va, vb
        
        else:
                
            if ed1_ind == 1:
                return 2*math.pi - angle, va, vb
            
            elif ed1_ind == (len(eds_sorted) - 1):
                return angle, vb, va
            
            else:
                #PROBLEMS!
                print("BIG BIG PROBLEMS")
                return angle, vb, va    
class TriangleFill(bpy.types.Operator):
    bl_idname = "object.triangle_fill"
    bl_label = "Triangle Fill Hole"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    
    
    res_modes = [
    ("AVG", "Average", "", 1),
    ("MIN", "Minumum", "", 2),
    ("MIN25", "Minumum + 25%", "", 3),
    ("MAX", "Maximum", "", 4),
    ("USER", "User", "", 5),
    ]
    
    res_mode = EnumProperty(items=res_modes, default = "AVG") #default = 0?
    resolution = FloatProperty(default = 0.00, description = 'Set the target edge length in fill, used with "USER" mode')
    smooth_iters = IntProperty(default = 20, name = 'Smooth Iterations')
    
    iter_max = IntProperty(default = 10000, name = 'Max Iterations')
    
    max_hole = IntProperty(default = 150, name = 'Max hole size to fill')
                
    def triangulate_fill(self,bme,edges, max_iters, res_mode, resolution, smooth_iters = 1):
        
        ed_loops = edge_loops_from_bmedges(bme, edges, ret = {'VERTS','EDGES'})
                    
            
        for vs, eds in zip(ed_loops['VERTS'], ed_loops['EDGES']):
            if vs[0] != vs[-1]: 
                print('not a closed loop')
                continue
            
            if len(vs) > self.max_hole:
                print('hole perimeter too big long')
                continue
            
            bme.verts.ensure_lookup_table()
            bme.edges.ensure_lookup_table()
            bme.faces.ensure_lookup_table()
            
            new_fs = []
            new_vs = []
            
            #establish collapse tollerance:
            if res_mode == 'USER' and resolution != 0.0:
                res = resolution
            elif res_mode == 'AVG':
                res = np.mean([bme.edges[i].calc_length() for i in eds]) 
            elif res_mode == 'MIN':
                res = min([bme.edges[i].calc_length() for i in eds])    
            elif res_mode == 'MIN25':
                ed_ls = [bme.edges[i].calc_length() for i in eds]
                ed_mean = np.mean(ed_ls)
                res = min(ed_ls) + .5 * (ed_mean - min(ed_ls))        
            elif res_mode == 'MAX':
                res = max([bme.edges[i].calc_length() for i in eds]) 
            #initiate the front and calc angles
            angles = {}
            neighbors = {}
            verts = [bme.verts[i] for i in vs]
            for v in verts:
                ang, va, vb = calc_angle(v)
                angles[v] = ang
                neighbors[v] = (va, vb)
            front = set(verts)   
            iters = 0 
            start = time.time()
            while len(front) > 3 and iters < max_iters:
                iters += 1
                
                v_small = min(front, key = angles.get)
                smallest_angle = angles[v_small]
                
                va, vb = neighbors[v_small]
                
                vec_a = va.co - v_small.co
                vec_b = vb.co - v_small.co
                vec_ab = va.co - vb.co
                
                
                Ra, Rb = vec_a.length, vec_b.length
                
                R_13 = .67*Ra + .33*Rb
                R_12 = .5*Ra + .5*Rb
                R_23 = .33*Ra + .67*Rb

                vec_a.normalize()
                vec_b.normalize()
                v_13 = vec_a.lerp(vec_b, .33) #todo, verify lerp
                v_12 = vec_a.lerp(vec_b, .5)
                v_23 = vec_a.lerp(vec_b, .67)
                
                v_13.normalize()
                v_12.normalize()
                v_23.normalize()
                
                if smallest_angle < math.pi/180 * 75:
                    try:
                        #f = bme.faces.new((va, v_small, vb))
                        f = bme.faces.new((vb, v_small, va))
                        new_fs += [f]
                        f.normal_update()
                    
                    except ValueError:
                        print('concavity with face on back side')
                        angles[v_small] = 2*math.pi
                
                    
                elif smallest_angle < math.pi/180 * 135:
                    
                    v_new_co = v_small.co + R_12 * v_12
                    small_a = (va.co - v_new_co).length < res
                    small_b = (vb.co - v_new_co).length < res
                    
                    if vec_ab.length < res:
                        f = bme.faces.new((vb, v_small, va))
                        new_fs += [f]
                        f.normal_update()
                        
                    elif small_a or small_b:
                        f = bme.faces.new((vb, v_small, va))
                        f.normal_update()
                        new_fs += [f]
                        
                    else:
                        v_new = bme.verts.new(v_new_co)
                        new_vs += [v_new]
                        
                        f1 = bme.faces.new((v_new, v_small, va))
                        f2 = bme.faces.new((vb, v_small, v_new))
                        new_fs += [f1, f2]
                        f1.normal_update()
                        f2.normal_update()

                        front.add(v_new)                        
                        v_new.normal_update()
                        ang, v_na, v_nb = calc_angle(v_new)
                        angles[v_new] = ang
                        neighbors[v_new] = (v_na, v_nb)
                        v_new.select_set(True)
                        
        
                else:
                    v_new_co = v_small.co + R_12 * v_12
                    v_new_coa = v_small.co + R_13 * v_13
                    v_new_cob = v_small.co + R_23 * v_23
                    
                    
                    short_a = (va.co - v_new_coa).length
                    short_mid = (v_new_coa - v_new_cob).length
                    short_b = (vb.co - v_new_cob).length
                    
                    if short_a + short_mid + short_b < res:
                        f = bme.faces.new((vb, v_small, va))
                        f.normal_update()
                        new_fs += [f]
                        
                    elif short_a < res or short_b < res or short_mid < res:
                        
                        v_new = bme.verts.new(v_new_co)
                        new_vs += [v_new]
                        f1 = bme.faces.new((v_new, v_small, va))
                        f2 = bme.faces.new((vb, v_small, v_new))
                        new_fs += [f1, f2]
                        f1.normal_update()
                        f2.normal_update()

                        front.add(v_new)                        
                        v_new.normal_update()
                        ang, v_na, v_nb = calc_angle(v_new)
                        angles[v_new] = ang
                        neighbors[v_new] = (v_na, v_nb)
                        v_new.select_set(True)
                    
                    else:
                        v_new_a = bme.verts.new(v_new_coa)
                        v_new_b = bme.verts.new(v_new_cob)
                        new_vs += [v_new_a, v_new_b]
                        f1 = bme.faces.new((v_new_a, v_small, va))
                        f2 = bme.faces.new((v_new_b, v_small, v_new_a))
                        f3 = bme.faces.new((vb, v_small, v_new_b))
                        new_fs += [f1, f2, f3]
                        
                        f1.normal_update()
                        f2.normal_update()
                        f3.normal_update()
                    
                        #update the 2 newly created verts
                        front.update([v_new_a, v_new_b])
                    
                        v_new_a.normal_update()
                        ang, v_na, v_nb = calc_angle(v_new_a)
                        angles[v_new_a] = ang
                        neighbors[v_new_a] = (v_na, v_nb)
    
                        v_new_b.normal_update()
                        ang, v_na, v_nb = calc_angle(v_new_b)
                        angles[v_new_b] = ang
                        neighbors[v_new_b] = (v_na, v_nb)
                    
                    
                    
                front.remove(v_small)
                angles.pop(v_small, None)
                neighbors.pop(v_small, None)
            
                va.normal_update()
                ang, v_na, v_nb = calc_angle(va)
                angles[va] = ang
                neighbors[va] = (v_na, v_nb)

            
                vb.normal_update()
                ang, v_na, v_nb = calc_angle(vb)
                angles[vb] = ang
                neighbors[vb] = (v_na, v_nb) 
    
            print('done at %i iterations' % iters)
            finish = time.time()
            print('Took %f seconds to fill' % (finish-start))
                
            if len(front) <= 3:
                print('hooray, reached the end')
                
                if len(front) == 3:
                    face = list(front)
                    new_fs += [bme.faces.new(face)]
                
                bme.verts.ensure_lookup_table()
                bme.edges.ensure_lookup_table()
                bme.faces.ensure_lookup_table()
                
                bmesh.ops.recalc_face_normals(bme, faces = new_fs)
                
                print('smoothing %i new verts' % len(new_vs))
                
                exclude = {}
                start = time.time()
                relax_bmesh(bme, new_vs, exclude, iterations= smooth_iters, spring_power = .2)
                
                finish = time.time()
                print('Took %f seconds to smooth' % (finish-start))
                #for i in range(0, smooth_iters):
                #    bmesh.ops.smooth_vert(bme, verts = new_vs, factor = 1)
                
                
                
            
            for f in new_fs:
                f.select_set(True)
            for v in new_vs:
                v.select_set(True)
                
    def invoke(self, context, event): 
        return context.window_manager.invoke_props_dialog(self, width=300) 
    
    def execute(self,context):
        obj = context.active_object
        
        if context.mode == 'EDIT_MESH':

        
            bme = bmesh.from_edit_mesh(obj.data)
            eds = [e.index for e in bme.edges if e.select]
            for ed in bme.edges:
                ed.select_set(False)
            
            self.triangulate_fill(bme, eds, self.iter_max, self.res_mode, self.resolution, self.smooth_iters)
            
            bme.select_flush(True)
            bmesh.update_edit_mesh(obj.data)
            bpy.ops.ed.undo_push(message="Triangle Fill")
            
        elif context.mode == 'OBJECT' and obj.type == 'MESH':
            
            bme = bmesh.new()
            bme.from_mesh(obj.data)
            bme.edges.ensure_lookup_table()
            bme.verts.ensure_lookup_table()
            eds = [ed.index for ed in bme.edges if len(ed.link_faces) == 1]
            
            self.triangulate_fill(bme, eds, self.iter_max, self.res_mode, self.resolution, self.smooth_iters)
            
            bme.to_mesh(obj.data)
            obj.data.update()
            bme.free()
            
            
        return{'FINISHED'}