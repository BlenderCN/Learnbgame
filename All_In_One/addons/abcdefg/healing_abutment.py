'''
Created on Apr 22, 2017

@author: Patrick

make blender key map match Blue Sky Bio
http://blendervisionpro.blogspot.com/2015/03/viewport-navigation-without-middle.html

#undo, redo state etc
https://docs.blender.org/api/blender_python_api_current/bpy.types.Operator.html
https://blender.stackexchange.com/questions/7631/python-make-an-operator-update-ui-after-executed/7635#7635

'''
#Python Imports
import random
import math
import os

#Blender Python Imports
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix, Color
from mathutils.bvhtree import BVHTree
from io_scene_obj.import_obj import load as loadobj
from io_mesh_stl import blender_utils, stl_utils
from bpy.app.handlers import persistent

#ODC imports
from mesh_cut import space_evenly_on_path, grow_selection_to_find_face, edge_loops_from_bmedges,\
    point_inside_loop2d, nearest_point_to_path
from odcutils import get_settings
from bmesh_fns import join_objects, edge_loop_neighbors
import tracking
import odcutils
from common_utilities import bversion

#############################################
####### UTILITIES ###########################
#############################################

def face_neighbors_strict(bmface):
    neighbors = []
    for ed in bmface.edges:
        if not (ed.verts[0].is_manifold and ed.verts[1].is_manifold):
            if len(ed.link_faces) == 1:
                print('found an ed, with two non manifold verts')
            continue
        neighbors += [f for f in ed.link_faces if f != bmface]
        
    return neighbors

def flood_selection_by_verts(bme, selected_faces, seed_face, max_iters = 1000):
    '''
    bme - bmesh
    selected_faces - should create a closed face loop to contain "flooded" selection
    if an empty set, selection willg grow to non manifold boundaries
    seed_face - a face within/out selected_faces loop
    max_iters - maximum recursions to select_neightbors
    
    return - set of faces
    '''
    total_selection = set([f for f in selected_faces])
    levy = set([f for f in selected_faces])  #it's funny because it stops the flood :-)

    new_faces = set(face_neighbors_strict(seed_face)) - levy
    iters = 0
    while iters < max_iters and new_faces:
        iters += 1
        new_candidates = set()
        for f in new_faces:
            new_candidates.update(face_neighbors_strict(f))
            
        new_faces = new_candidates - total_selection
        
        if new_faces:
            total_selection |= new_faces    
    if iters == max_iters:
        print('max iterations reached')    
    return total_selection


#############################################
######## DATA AND DICTIONARIES ##############
#############################################


#widths dictionary
#https://www.slideshare.net/priyankachowdhary7/dental-anatomy-physiology-of-permanent-teeth
#cej_delta = difference in height of proximal CEJ to bucco-lingual CEJ
#tooth_data[tooth_number] = MD_width_cej, BL_width_cej, CEJ_delta_m, cej_delta_d

tooth_data = {}
tooth_data[8], tooth_data[9]   = (7.0, 6.0, 3.5, 2.5),  (7.0, 6.0, 3.5, 2.5)
tooth_data[7],tooth_data[10]   = (5.5, 4.9, 2.7, 2.0),  (5.5, 4.9, 2.7, 2.0)  #*I made these up
tooth_data[6],tooth_data[11]   = (5.5, 7.0, 2.5, 1.5),  (5.5, 7.0, 2.5, 1.5)
tooth_data[5],tooth_data[12]   = (5.0, 8.0, 1.0, 0.0),  (5.0, 8.0, 1.0, 0.0)
tooth_data[4],tooth_data[13]   = (5.0, 8.0, 1.0, 0.0),  (5.0, 8.0, 1.0, 0.0)
tooth_data[3],tooth_data[14]   = (8.0, 10.0, 1.0, 0.0), (8.0, 10.0, 1.0, 0.0)
tooth_data[2],tooth_data[15]   = (7.8, 9.8, 1.0, 0.0),  (7.8, 9.8, 1.0, 0.0)   #I made these up too
tooth_data[1],tooth_data[16]   = (7.8, 9.8, 1.0, 0.0),  (7.8, 9.8, 1.0, 0.0)   #I made these up too
tooth_data[25],tooth_data[24]  = (3.5, 5.3, 3.0, 2.0),  (3.5, 5.3, 3.0, 2.0)
tooth_data[26],tooth_data[23]  = (4.0, 5.8, 3.0, 2.0),  (4.0, 5.8, 3.0, 2.0)
tooth_data[27],tooth_data[22]  = (5.5, 7.0, 2.5, 1.5),  (5.5, 7.0, 2.5, 1.5)
tooth_data[28],tooth_data[21]  = (5.0, 6.5, 1.0, 0.0),  (5.0, 6.5, 1.0, 0.0) 
tooth_data[29],tooth_data[20]  = (5.2, 6.7, 1.0, 0.0),  (5.2, 6.7, 1.0, 0.0) # I made these up
tooth_data[30],tooth_data[19]  = (9.2, 9.0, 1.0, 0.0),  (9.2, 9.0, 1.0, 0.0)
tooth_data[31],tooth_data[18]  = (9.0, 8.8, 1.0, 0.0),  (9.0, 8.8, 1.0, 0.0)
tooth_data[32],tooth_data[17]  = (8.7, 8.6, 1.0, 0.0),  (9.0, 8.8, 1.0, 0.0)


tooth_to_text = {}
tooth_to_text[1] = 'UR8'
tooth_to_text[2] = 'UR7'
tooth_to_text[3] = 'UR6'
tooth_to_text[4] = 'UR5'
tooth_to_text[5] = 'UR4'
tooth_to_text[6] = 'UR3'
tooth_to_text[7] = 'UR2'
tooth_to_text[8] = 'UR1'
tooth_to_text[9] = 'UL1'
tooth_to_text[10] = 'UL2'
tooth_to_text[11] = 'UL3'
tooth_to_text[12] = 'UL4'
tooth_to_text[13] = 'UL5'
tooth_to_text[14] = 'UL6'
tooth_to_text[15] = 'UL7'
tooth_to_text[16] = 'UL8'            
tooth_to_text[17] = 'LL8'
tooth_to_text[18] = 'LL7'
tooth_to_text[19] = 'LL6'
tooth_to_text[20] = 'LL5'
tooth_to_text[21] = 'LL4'
tooth_to_text[22] = 'LL3'
tooth_to_text[23] = 'LL2'
tooth_to_text[24] = 'LL1'
tooth_to_text[25] = 'LR1'
tooth_to_text[26] = 'LR2'
tooth_to_text[27] = 'LR3'
tooth_to_text[28] = 'LR4'
tooth_to_text[29] = 'LR5'
tooth_to_text[30] = 'LR6'
tooth_to_text[31] = 'LR7'
tooth_to_text[32] = 'LR8'              

tooth_to_FDI = {}
tooth_to_FDI[1] = '18'
tooth_to_FDI[2] = '17'
tooth_to_FDI[3] = '16'
tooth_to_FDI[4] = '15'
tooth_to_FDI[5] = '14'
tooth_to_FDI[6] = '13'
tooth_to_FDI[7] = '12'
tooth_to_FDI[8] = '11'
tooth_to_FDI[9] = '21'
tooth_to_FDI[10] = '22'
tooth_to_FDI[11] = '23'
tooth_to_FDI[12] = '24'
tooth_to_FDI[13] = '25'
tooth_to_FDI[14] = '26'
tooth_to_FDI[15] = '27'
tooth_to_FDI[16] = '28'            
tooth_to_FDI[17] = '38'
tooth_to_FDI[18] = '37'
tooth_to_FDI[19] = '36'
tooth_to_FDI[20] = '35'
tooth_to_FDI[21] = '34'
tooth_to_FDI[22] = '33'
tooth_to_FDI[23] = '32'
tooth_to_FDI[24] = '31'
tooth_to_FDI[25] = '41'
tooth_to_FDI[26] = '42'
tooth_to_FDI[27] = '43'
tooth_to_FDI[28] = '44'
tooth_to_FDI[29] = '45'
tooth_to_FDI[30] = '46'
tooth_to_FDI[31] = '47'
tooth_to_FDI[32] = '48' 

tooth_mirror = {}
tooth_mirror[1] = 16
tooth_mirror[2] = 15
tooth_mirror[3] = 14
tooth_mirror[4] = 13
tooth_mirror[5] = 12
tooth_mirror[6] = 11
tooth_mirror[7] = 10
tooth_mirror[8] = 9
tooth_mirror[9] = 8
tooth_mirror[10] = 7
tooth_mirror[11] = 6
tooth_mirror[12] = 5
tooth_mirror[13] = 4
tooth_mirror[14] = 3
tooth_mirror[15] = 2
tooth_mirror[16] = 1            
tooth_mirror[17] = 32
tooth_mirror[18] = 31
tooth_mirror[19] = 30
tooth_mirror[20] = 29
tooth_mirror[21] = 28
tooth_mirror[22] = 27
tooth_mirror[23] = 26
tooth_mirror[24] = 25
tooth_mirror[25] = 24
tooth_mirror[26] = 23
tooth_mirror[27] = 22
tooth_mirror[28] = 21
tooth_mirror[29] = 20
tooth_mirror[30] = 19
tooth_mirror[31] = 18
tooth_mirror[32] = 17

################################################
########### CALLBACKS/HANDLERS  ################
################################################
#a box to hold stuff in
class Box:
    pass

__m = Box()
__m.transform_cache = {}
__m.panels = []

def detect_transforms(ob):
    
    if ob.name not in __m.transform_cache:
        __m.transform_cache[ob.name] = ob.matrix_world.copy()
        return False
    elif np.allclose(ob.matrix_world, __m.transform_cache[ob.name]): 
        return False
    else:
        return True
    
def update_transform(ob):
    __m.transform_cache[ob.name] = ob.matrix_world.copy()
    return

@persistent
def mirror_transforms(dummy):
    ob = bpy.context.object
    #bailout conditions
    if ob == None: return
    if ':CEJ' not in ob.name: return
    
    tnumber = int(ob.name.split(':')[0])
    mirror = str(tooth_mirror[tnumber]) + ":CEJ"
        
    mir_ob = bpy.data.objects.get(mirror)
    if mir_ob == None: return

    if detect_transforms(ob) == None: return
    
    #match their scale
    mir_ob.matrix_world[0][0] = ob.matrix_world[0][0]
    mir_ob.matrix_world[1][1] = ob.matrix_world[1][1]
    mir_ob.matrix_world[1][3] = ob.matrix_world[1][3]
    mir_ob.matrix_world[2][3] = ob.matrix_world[2][3]
    #invert x location
    mir_ob.matrix_world[0][3] = -1 * ob.matrix_world[0][3]
    
    update_transform(ob)
    update_transform(mir_ob)
    
    
#TODO, make this an import helper

class OPENDENTAL_OT_heal_abutment_generator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_abutment_generator"
    bl_label = "Generate Abutment"
    bl_options = {'REGISTER', 'UNDO'}
    
    width0 = bpy.props.FloatProperty(name = 'width1', default = 4.5, min = 1, max = 10)
    height0 = bpy.props.FloatProperty(name = 'height1', default = 0.0, min = -8, max = 10)
    
    width1 = bpy.props.FloatProperty(name = 'width2', default = 2.75, min = 1, max = 10)
    height1 = bpy.props.FloatProperty(name = 'height2', default = 3.5, min = -8, max = 10)
    
    width2 = bpy.props.FloatProperty(name = 'width3', default = 0.0, min = 0.0, max = 10)
    height2 = bpy.props.FloatProperty(name = 'height3', default = 0.0, min = -8, max = 10)
    
    width3 = bpy.props.FloatProperty(name = 'width4', default = 0.0, min = 0.0, max = 10)
    height3 = bpy.props.FloatProperty(name = 'height4', default = 0.0, min = -8, max = 10)
    
    width4 = bpy.props.FloatProperty(name = 'width5', default = 0.0, min = 0.0, max = 10)
    height4 = bpy.props.FloatProperty(name = 'height5', default = 0.0, min = -8, max = 10)
    
    width5 = bpy.props.FloatProperty(name = 'width6', default = 0.0, min = 0.0, max = 10)
    height5 = bpy.props.FloatProperty(name = 'height6', default = 0.0, min = -8, max = 10)
    
    width6 = bpy.props.FloatProperty(name = 'width7', default = 0.0, min = 0.0, max = 10)
    height6 = bpy.props.FloatProperty(name = 'height7', default = 0.0, min = -8, max = 10)
    
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self,context):
        
        pairs = []
        
        if self.width0**2 > .001:
            pairs.append((self.width0, self.height0))
        if self.width1**2 > .001:
            pairs.append((self.width1, self.height1))
        if self.width2**2 > .001:
            pairs.append((self.width2, self.height2))
        if self.width3**2 > .001:
            pairs.append((self.width3, self.height3))
        if self.width4**2 > .001:
            pairs.append((self.width4, self.height4))
        if self.width5**2 > .001:
            pairs.append((self.width5, self.height5))
        if self.width6**2 > .001:
            pairs.append((self.width6, self.height6))
            
        bme = bmesh.new()
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()
        
        r = pairs[0][0]
        if bversion() > "002.079.003":
            circle_data = bmesh.ops.create_circle(bme, cap_ends = True, segments = 64, radius = r/2)
        else:
            circle_data = bmesh.ops.create_circle(bme, cap_ends = True, segments = 64, diameter = r/2)
        #print(circle_data)
        
        bme.edges.ensure_lookup_table()
        new_eds = bme.edges[:]
        
        #print(pairs)
        #print(new_eds)
        for i, pair in enumerate(pairs):
            
            r = pair[0]/2
            h = pair[1]
            
            if i == 0:
                continue
            
            gdict = bmesh.ops.extrude_edge_only(bme, edges = new_eds)  
            new_eds = [ed for ed in gdict['geom'] if isinstance(ed, bmesh.types.BMEdge)]
            vs = [ele for ele in gdict['geom'] if isinstance(ele, bmesh.types.BMVert)]
            for v in vs:
                v.co[2] = -h
                
                R = Vector((v.co[0],v.co[1]))
                L = R.length
                s = r/L
            
                R_prime = s * R
            
                v.co[0], v.co[1] = R_prime[0], R_prime[1]
                
            
            
        
            bme.edges.ensure_lookup_table()
            bme.verts.ensure_lookup_table()
        
        bme.faces.ensure_lookup_table()
        bme.faces.new(vs)
        
        bmesh.ops.recalc_face_normals(bme, faces = bme.faces[:])
        abut_me = bpy.data.meshes.new('Custom Abutment')
        bme.to_mesh(abut_me)
        bme.free()
        ob = bpy.data.objects.new('Abutment:Master', abut_me)
        context.scene.objects.link(ob)
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(self, "width0")
        row.prop(self, "height0")
        
        row = layout.row()
        row.prop(self, "width1")
        row.prop(self, "height1")
        
        row = layout.row()
        row.prop(self, "width2")
        row.prop(self, "height2")
        
        row = layout.row()
        row.prop(self, "width3")
        row.prop(self, "height3")
        
        row = layout.row()
        row.prop(self, "width4")
        row.prop(self, "height4")
        
        row = layout.row()
        row.prop(self, "width5")
        row.prop(self, "height5")
        
        row = layout.row()
        row.prop(self, "width6")
        row.prop(self, "height6")
        
        
        
class OPENDENTAL_OT_heal_import_abutment(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_import_abutment"
    bl_label = "Import Abutment File"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        prefs = get_settings()
        if prefs.heal_abutment_file == '':
            return False
        if context.mode != 'OBJECT':
            return False
        return True
    
    def execute(self,context):
        prefs = get_settings()
        file_path = prefs.heal_abutment_file
        
        if not os.path.exists(file_path):
            self.report({'ERROR'}, 'Must Select File abve')
            
        file_name = os.path.basename(file_path)
        tracking.trackUsage("apgImportAbutment",file_name)
        
        suff =  file_name[len(file_name)-4:]
        if suff not in {'.stl', '.obj','.STL','.OBJ'}:
            self.report({'ERROR'}, 'Must be obj or stl format. Ply coming soon')
        
        old_obs = [ob.name for ob in bpy.data.objects]
        if suff == '.stl':
            global_matrix = Matrix.Identity(4)
            objName = bpy.path.display_name(os.path.basename(file_path))
            tris, tri_nors, pts = stl_utils.read_stl(file_path)
            tri_nors = None
            blender_utils.create_and_link_mesh(objName, tris, tri_nors, pts, global_matrix)
            
        
        elif suff == '.obj':
            loadobj(context, file_path)
            
        new_obs = [ob for ob in bpy.data.objects if ob.name not in old_obs]
        bpy.ops.object.select_all(action = 'DESELECT')
        for ob in new_obs:
            ob.select = True
            ob.name = "Abutment:Master"
            context.scene.objects.active = ob
            ob.matrix_world = Matrix.Identity(4)
        
        old_obs = [ob.name for ob in bpy.data.objects]
        bpy.ops.mesh.separate(type = 'LOOSE') 
        new_obs = [ob.name for ob in bpy.data.objects if ob.name not in old_obs]
        if len(new_obs):
            self.report({'WARNING'},'Multiple Objects imported, only "Abutment:Master" will be used')
            
            bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center = 'BOUNDS')
        
        bpy.ops.object.location_clear()
        bpy.ops.view3d.view_selected()
        
        return {'FINISHED'}

            
class OPENDENTAL_OT_heal_mark_platform(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_mark_abutment_shoulder"
    bl_label = "Mark Shoulder of Abutment"
    #bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" not in bpy.data.objects:
            return False
        return True
    
    def execute(self,context):
        
        ti_base_ob = bpy.data.objects.get('Abutment:Master')
        me = ti_base_ob.data
        
        cursor_loc = context.scene.cursor_location
        
        mx = ti_base_ob.matrix_world
        imx = mx.inverted()
        
        ok, new_loc, no, ind = ti_base_ob.closest_point_on_mesh(imx * cursor_loc)
        
        z = no
        f = ti_base_ob.data.polygons[ind]
        x = me.vertices[f.edge_keys[0][0]].co - me.vertices[f.edge_keys[0][1]].co
        x.normalize()
        y = z.cross(x)
        
        R = Matrix.Identity(3)  #make the columns of matrix U, V, W
        R[0][0], R[0][1], R[0][2]  = x[0] ,y[0],  z[0]
        R[1][0], R[1][1], R[1][2]  = x[1], y[1],  z[1]
        R[2][0] ,R[2][1], R[2][2]  = x[2], y[2],  z[2]
        T = R.to_4x4()
        T_inv = T.inverted()    
        #undo rotation
        me.transform(T_inv)
        
        #find the z height
        platform_z = me.polygons[ind].center
        
        delta = Vector((0,0,-platform_z[2]))
        
        T = Matrix.Translation(delta)
        me.transform(T)
        
        #ti_base_ob.matrix_world = Matrix.Identity(4)
        ti_base_ob.update_tag()
        context.scene.update()
        
        bb = ti_base_ob.bound_box
        
        x_c, y_c, z_c = 0, 0, 0
        
        for i in range(0,8):
            x_c += bb[i][0]
            y_c += bb[i][1]
            z_c += bb[i][2]
        x_c *= 1/8
        y_c *= 1/8
        z_c *= 1/8
        
        cent_v = Vector((-x_c, -y_c, 0))
        T = Matrix.Translation(cent_v)
        me.transform(T)
        
        ti_base_ob.matrix_world = Matrix.Identity(4)
        context.scene.cursor_location = Vector((0,0,0))
        bpy.ops.view3d.view_center_cursor()
        bpy.ops.ed.undo_push(message = "mark shoulder")
        return {'FINISHED'}

class OPENDENTAL_OT_heal_mark_timing(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_mark_abutment_timing"
    bl_label = "Mark Timing of Abutment"
    #bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" not in bpy.data.objects:
            return False
        return True
    
    def execute(self,context):
        
        ti_base_ob = bpy.data.objects.get('Abutment:Master')
        me = ti_base_ob.data
        
        cursor_loc = context.scene.cursor_location
        
        mx = ti_base_ob.matrix_world
        imx = mx.inverted()
        
        ok, new_loc, no, ind = ti_base_ob.closest_point_on_mesh(imx * cursor_loc)
        
        y = no
        z = Vector((0,0,1))
        x = y.cross(z)
        
        R = Matrix.Identity(3)  #make the columns of matrix U, V, W
        R[0][0], R[0][1], R[0][2]  = x[0] ,y[0],  z[0]
        R[1][0], R[1][1], R[1][2]  = x[1], y[1],  z[1]
        R[2][0] ,R[2][1], R[2][2]  = x[2], y[2],  z[2]
        T = R.to_4x4()
        T_inv = T.inverted()    
        #undo rotation
        me.transform(T_inv)
        bpy.ops.ed.undo_push(message = "mark timing")
        bpy.ops.view3d.viewnumpad(type = 'BACK')
        return {'FINISHED'}
    
class OPENDENTAL_OT_heal_remove_internal(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_remove_internal"
    bl_label = "Remove Internal Geometry"
    #bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" not in bpy.data.objects:
            return False
        return True
    
    def execute(self,context):
        
        ti_base_ob = bpy.data.objects.get('Abutment:Master')
        
        bme = bmesh.new()
        bme.from_mesh(ti_base_ob.data)
        
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()
        
        max_vz = max(bme.verts, key = lambda x: x.co[2])
        min_vz = min(bme.verts, key = lambda x: x.co[2])
        
        z_max = max_vz.co[2]
        z_min = min_vz.co[2]
        
        
        #remove top and bottom 0.2mm
        
        bmesh.ops.bisect_plane(bme, geom = bme.faces[:]+bme.edges[:]+bme.verts[:], 
                               plane_co = Vector((0,0,z_max - 0.2)), 
                               plane_no = Vector((0,0,1)),
                               clear_outer = True)
                               
        
        bmesh.ops.bisect_plane(bme, geom = bme.faces[:]+bme.edges[:]+bme.verts[:], 
                               plane_co = Vector((0,0,z_min + 0.2)), 
                               plane_no = Vector((0,0,-1)),
                               clear_outer = True)
        
        min_vx = min(bme.verts, key = lambda x: x.co[0]**2 + x.co[1]**2)  #smallest radii vert
        
        #todo, safety
        start_face = [f for f in min_vx.link_faces][0]
        
        interior_faces = flood_selection_by_verts(bme, set([]), start_face, 10000)
        
        if len(interior_faces) == len(bme.faces):
            err_me = bpy.data.meshes.new('Abutment:Error')
            err_ob = bpy.data.objects.new('Abutment:Error', err_me)
            
            err_ob.matrix_world = ti_base_ob.matrix_world
            bme.to_mesh(err_me)
            context.scene.objects.link(err_ob)
            
            self.report({'ERROR'},"Results attempted to delete entire object! Returning copy for inspection")
            bme.free()
            return {'CANCELLED'}
        
        bmesh.ops.delete(bme, geom = list(interior_faces), context = 5)
        
        bme.edges.ensure_lookup_table()
        bme.verts.ensure_lookup_table()
        cap_eds = [ed.index for ed in bme.edges if len(ed.link_faces) == 1]
        
        loops = edge_loops_from_bmedges(bme, cap_eds)
        
        caps = []
        for v_loop in loops:
            if v_loop[0] == v_loop[-1]:
                v_loop.pop()
            vs = [bme.verts[i] for i in v_loop]        
            
            f = bme.faces.new(vs)
            
            if f.calc_center_bounds()[2] < 0:
                print('points down')
                f.normal = Vector((0,0,-1))
            else:
                print('points up')
                f.normal = Vector((0,0,1))
            
            
            caps += [f]

        for f in caps:
            new_geom = bmesh.ops.extrude_face_region(bme, geom = [f])  
            for v in new_geom['geom']:
                if isinstance(v, bmesh.types.BMVert):
                    
                    if v.co[2] > 0:
                        v.co[2] += 0.2
                    else:
                        v.co[2] -= 0.2
        
        bmesh.ops.delete(bme, geom = caps, context = 5)                       
        #bmesh.ops.triangulate(bme, faces = caps)
        bme.faces.ensure_lookup_table()
        bmesh.ops.recalc_face_normals(bme, faces = bme.faces[:])
        
        
        bme.to_mesh(ti_base_ob.data)
        ti_base_ob.update_tag()
        context.scene.update()
        bpy.ops.ed.undo_push(message = "remove internal")
        bpy.ops.view3d.viewnumpad(type = 'TOP')
        bpy.ops.view3d.view_orbit(angle = 45, type = 'ORBITDOWN')
        return {'FINISHED'}


class OPENDENTAL_OT_ucla_remove_timing(bpy.types.Operator):
    """Cut's the abutment at the 3D Cursor and extrudes it downard.  Click above timing/hex and will be converted to cylinder"""
    bl_idname = "opendental.ucla_remove_timing"
    bl_label = "Remove Timing Geometry"
    #bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" not in bpy.data.objects:
            return False
        return True
    
    def execute(self,context):
        
        
        ti_base_ob = bpy.data.objects.get('Abutment:Master')
        mx = ti_base_ob.matrix_world
        
        imx = mx.inverted()
        cursor_loc = context.scene.cursor_location
        ok, new_loc, no, ind = ti_base_ob.closest_point_on_mesh(imx * cursor_loc)
        
        bme = bmesh.new()
        bme.from_mesh(ti_base_ob.data)
        
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        bme.faces.ensure_lookup_table()
        
        max_vz = max(bme.verts, key = lambda x: x.co[2])
        min_vz = min(bme.verts, key = lambda x: x.co[2])
        
        z_max = max_vz.co[2]
        z_min = min_vz.co[2]
        
        
        #cut at the cursor location
        gdict = bmesh.ops.bisect_plane(bme, geom = bme.faces[:]+bme.edges[:]+bme.verts[:], 
                               plane_co = new_loc, 
                               plane_no = Vector((0,0,1)),
                               clear_inner = True)
                               
   

        
       
        cut_geom = gdict['geom_cut']
        
         
        bme.edges.ensure_lookup_table()
        bme.verts.ensure_lookup_table()
        
        cap_eds = [ele for ele in cut_geom if isinstance(ele, bmesh.types.BMEdge)]
        
        gdict = bmesh.ops.extrude_edge_only(bme, edges = cap_eds)  
    
        eds = [ed.index for ed in gdict['geom'] if isinstance(ed, bmesh.types.BMEdge)]
       
        bme.verts.ensure_lookup_table()
        bme.edges.ensure_lookup_table()
        
        loops = edge_loops_from_bmedges(bme, eds)
        
        for vloop in loops:
            vloop.pop()
            vs = [bme.verts[i] for i in vloop]
            
            for v in vs:
                v.co[2] = z_min
        
            f = bme.faces.new(vs)
        
        #bmesh.ops.triangulate(bme, faces = caps)
        bme.faces.ensure_lookup_table()
        bmesh.ops.recalc_face_normals(bme, faces = bme.faces[:])
        
        
        bme.to_mesh(ti_base_ob.data)
        ti_base_ob.update_tag()
        context.scene.update()
        bpy.ops.ed.undo_push(message = "remove timing")
        bpy.ops.view3d.viewnumpad(type = 'TOP')
        bpy.ops.view3d.view_orbit(angle = 45, type = 'ORBITDOWN')
        return {'FINISHED'}

class OPENDENTAL_OT_ucla_cut_above(bpy.types.Operator):
    """Cut's the abutment at the 3D Cursor and extrudes it downard.  Click above timing/hex and will be converted to cylinder"""
    bl_idname = "opendental.heal_cut_at_cursor"
    bl_label = "Cut at Cursor"
    bl_options = {'REGISTER','UNDO'}
    #bl_options = {'REGISTER', 'UNDO'}
    
    items = [('ABOVE','ABOVE','ABOVE'),('BELOW','BELOW','BELOW')]
    cut  = bpy.props.EnumProperty(name = 'Above/Below', items = items, default = 'ABOVE')
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" not in bpy.data.objects:
            return False
        return True
    
    def execute(self,context):
        
        
        ti_base_ob = bpy.data.objects.get('Abutment:Master')
        mx = ti_base_ob.matrix_world
        
        imx = mx.inverted()
        cursor_loc = context.scene.cursor_location
        ok, new_loc, no, ind = ti_base_ob.closest_point_on_mesh(imx * cursor_loc)
        
    
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        
        if self.cut == 'ABOVE':
            bpy.ops.mesh.bisect(plane_co=new_loc, plane_no=(0,0,1), 
                           use_fill=True, 
                           clear_inner=False, 
                           clear_outer=True, 
                           threshold=0.0001, 
                           xstart=0, xend=0, ystart=0, yend=0, cursor=1002)
        
        else:
            bpy.ops.mesh.bisect(plane_co=new_loc, plane_no=(0,0,1), 
                           use_fill=True, 
                           clear_inner=True, 
                           clear_outer=False, 
                           threshold=0.0001, 
                           xstart=0, xend=0, ystart=0, yend=0, cursor=1002)
            
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return {'FINISHED'}

class OPENDENTAL_OT_heal_extend_flat_region(bpy.types.Operator):
    """Extends all flat faces at cursor by set amount"""
    bl_idname = "opendental.heal_extend_flat"
    bl_label = "Extend at Cursor"
    bl_options = {'REGISTER','UNDO'}
    #bl_options = {'REGISTER', 'UNDO'}
    
    distance = bpy.props.FloatProperty(name = 'Distance', default = 1.0, description = 'Amount to extrude faces')
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" not in bpy.data.objects:
            return False
        return True
    
    def execute(self,context):
        
        
        ti_base_ob = bpy.data.objects.get('Abutment:Master')
        mx = ti_base_ob.matrix_world
        
        imx = mx.inverted()
        cursor_loc = context.scene.cursor_location
        ok, new_loc, no, ind = ti_base_ob.closest_point_on_mesh(imx * cursor_loc)
        
    
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        context.tool_settings.mesh_select_mode = [False, False, True]
        ti_base_ob.data.polygons[ind].select = True
        no = ti_base_ob.data.polygons[ind].normal
        no = self.distance * no
        
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.faces_select_linked_flat()
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region = {"mirror":False}, TRANSFORM_OT_translate={"value":(no[0],no[1],no[2]),"constraint_axis":(False, False, False)})
            
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return {'FINISHED'}
            
class OPENDENTAL_OT_heal_generate_profiles(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_generate_profiles"
    bl_label = "Generate CEJ Profiles"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if "Abutment:Master" not in bpy.data.objects:
            return False
        
        cejs = [ob.name for ob in bpy.data.objects if ':CEJ' in ob.name]
        if len(cejs) > 0:
            return False
        
        
        return True
    

    def execute(self, context):
        prefs = get_settings()
        
        n_columns = prefs.heal_n_cols
        border_space = prefs.heal_block_border
        inter_space = prefs.heal_inter_space_x
        cyl_depth = prefs.heal_abutment_depth
        
        ti_base_obj = bpy.data.objects['Abutment:Master']
        ti_base_diameter = ti_base_obj.dimensions[0]  #needs to be oriented correctly
        
        bme = bmesh.new()
        bme.from_mesh(ti_base_obj.data)
        new_me = bpy.data.meshes.new('UCLA_dup')
        bme.to_mesh(new_me)
        bme.free()
        
        teeth = [i+1 for i in range(0,32) if prefs.heal_teeth[i]]
        
        #now sort teeth by quadrant
        UR = [i for i in teeth if i < 9]
        UL = [i for i in teeth if i > 8 and i < 17]
        LR = [i for i in teeth if i > 24]
        LL = [i for i in teeth if i > 16 and i < 25]
        
        LR.reverse()
        LL.reverse()
        
        teeth = LR + LL + UR + UL
        
        
        if len(teeth) == 0:
            self.report({'ERROR'}, 'Need to select teeth to generate template for')
            
        n_rows = math.ceil(len(teeth)/n_columns)
        print("There should be %i rows" % n_rows)
        
        prev_y = border_space #start border space above x-axis.  May add more room for text label at bottom        
        x_border = 0

        for i in range(0,n_rows):
            
            prev_width = border_space
            
            row_height = max([tooth_data[teeth[m]][1] for m in range(i*n_columns, (i+1)*n_columns) if m < len(teeth)])
            
            print(row_height)
            
            for j in range(0,n_columns):
                n = i*n_columns + j
                if n > len(teeth) - 1: continue  #reached the end of last row
            
                tooth_number = teeth[n]
                t_data = tooth_data[tooth_number]
                
                #this will build left to right, bottom to top
                x_pos = prev_width + t_data[0]/2
                
                if x_border < prev_width + t_data[0]:
                    x_border = prev_width + t_data[0]
                
                y_pos = prev_y + row_height/2
                
                prev_width += t_data[0] + inter_space
   
                md_w = t_data[0]
                bl_w = t_data[1]
                delta_m = t_data[2]
                delta_d = t_data[3]
                
                crv_data = bpy.data.curves.new(str(tooth_number) + ":CEJ", 'CURVE')
                crv_data.splines.new('BEZIER')
                crv_data.splines[0].bezier_points[0].handle_left_type = 'AUTO'
                crv_data.splines[0].bezier_points[0].handle_right_type = 'AUTO'
                crv_data.dimensions = '3D'
                crv_obj = bpy.data.objects.new(str(tooth_number) + ":CEJ",crv_data)
                bpy.context.scene.objects.link(crv_obj)
                
                crv_data.splines[0].bezier_points.add(count = 7)
                crv_data.splines[0].use_cyclic_u = True
                    
                for k in range(0,8):
                    bp = crv_data.splines[0].bezier_points[k]
                    bp.handle_right_type = 'AUTO'
                    bp.handle_left_type = 'AUTO'
                    
                    x = md_w/2 * math.cos(k * 2*  math.pi/8)
                    y = bl_w/2 * math.sin(k * 2 * math.pi/8)
                    
                    if x > 0:
                        z = delta_m * math.cos(k * 2*  math.pi/8)**3
                    else:
                        z = -delta_d * math.cos(k * 2*  math.pi/8)**3
                    
                    #this code keeps the mesials pointed to midline
                    if tooth_number > 8 and tooth_number < 25:
                        x *= -1
                    
                    #this code keeps facial toward outside of block 
                    if tooth_number > 16:
                        y *= -1
                        
                    bp.co = Vector((x,y,z))
                
                crv_obj.location = Vector((x_pos,y_pos,cyl_depth))
                
                new_ob = bpy.data.objects.new(str(tooth_number) + ":Abutment", new_me)
                context.scene.objects.link(new_ob)
                #TODO, matrix world editing
                
                if tooth_number > 16:
                    R = Matrix.Rotation(math.pi, 4, Vector((0,0,1)))
                else:
                    R = Matrix.Identity(4)
                    
                T = Matrix.Translation(Vector((x_pos, y_pos, 0)))
                new_ob.matrix_world = T * R
                
                
            prev_y += row_height + inter_space
            
            
        
        box_y = prev_y - inter_space + border_space
        box_x = x_border + border_space
        
        #print(box_y, box_x)
        
        #old_obs = [ob.name for ob in bpy.data.objects]
        #bpy.ops.mesh.primitive_cube_add(radius = 0.5)
        #cube = [ob for ob in bpy.data.objects if ob.name not in old_obs][0]
        
        #cube.scale[0] = box_x
        #cube.scale[1] = box_y
        #cube.scale[2] = cyl_depth + 2 + 2 + 2
        
        #cube.location[0] = box_x/2
        #cube.location[1] = box_y/2
        #cube.location[2] = -cyl_depth/2 + .5
        
        #cube.draw_type = 'WIRE'
        #cube.name = 'Templates Base'
        #mod = cube.modifiers.new(type = 'BEVEL', name = 'Bevel')
        #mod.width = .05
        return {'FINISHED'}
    
    
class OPENDENTAL_OT_heal_database_curve_profiles(bpy.types.Operator):
    """please draw me?"""
    bl_idname = "opendental.heal_database_curve_profiles"
    bl_label = "Database Curve CEJ Profiles"
    bl_options = {'REGISTER', 'UNDO'}
    
    inter_space_x = bpy.props.FloatProperty(name = 'horizontal', default = 2.0, min = 1.5, max = 10)
    inter_space_y = bpy.props.FloatProperty(name = 'vertical', default = 2.0, min = 1.5, max = 10)
    middle_space_x = bpy.props.FloatProperty(name = 'middle', default = 2.0, min = 1.5, max = 10)
    cyl_depth = bpy.props.FloatProperty(name = 'depth', default = 5.0, min = 2.0, max = 10)
    
    @classmethod
    def poll(cls, context):
        
        if "Abutment:Master" not in bpy.data.objects:
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Layout and Position")
        col.prop(self, "cyl_depth")
        col.prop(self, "inter_space_x")
        col.prop(self, "inter_space_y")
        col.prop(self, "middle_space_x")
        
    def invoke(self,context, event):
        prefs = get_settings()
        
        #get initial settings form preferences default
        #load them into operator settings for undo/redo
        self.inter_space_x = prefs.heal_inter_space_x
        self.inter_space_y = prefs.heal_inter_space_y
        self.middle_space_x = prefs.heal_middle_space_x
        self.cyl_depth = prefs.heal_abutment_depth
        
        
        return self.execute(context)
        
    def execute(self, context):
        
        prefs = get_settings()
        
        inter_space_x = self.inter_space_x
        inter_space_y = self.inter_space_y
        middle_space_x = self.middle_space_x
        cyl_depth = self.cyl_depth
        
        ti_base_obj = bpy.data.objects['Abutment:Master']
        
        bme = bmesh.new()
        bme.from_mesh(ti_base_obj.data)
        new_me = bpy.data.meshes.new('UCLA_dup')
        bme.to_mesh(new_me)
        bme.free()
        
        teeth = [i+1 for i in range(0,32) if prefs.heal_teeth[i]]
        
        if len(teeth) == 0:
            self.report({'ERROR'}, 'Need to select teeth to generate templates for')
            return {'CANCELLED'}
        
        if not all([str(tooth) in bpy.data.curves for tooth in teeth]):
            self.report({'ERROR'}, 'Database templates not available, generate generic templates')
            return {'CANCELLED'}
        
        print('THE PROFILES SHOULD BE SCALED by  :' + prefs.profile_scale)
        if prefs.profile_scale == 'SMALL':
            scl = .8
        elif prefs.profile_scale == 'MEDIUM':
            scl = 1
        elif prefs.profile_scale == 'LARGE':
            scl = 1.2
        else:
            scl = 1
            
        scl_mx = Matrix.Identity(4)
        scl_mx[0][0], scl_mx[1][1] = scl, scl
        print(scl_mx)
        #get all the tooth_objects into the scene
        for tooth in teeth:
            new_ob = bpy.data.objects.new(str(tooth)+":CEJ", bpy.data.curves[str(tooth)])
            new_ob.matrix_world = Matrix.Identity(4)
            context.scene.objects.link(new_ob)
            
        #sort teeth by quadrant
        UR = [i for i in teeth if i < 9]
        UL = [i for i in teeth if i > 8 and i < 17]
        LR = [i for i in teeth if i > 24]
        LL = [i for i in teeth if i > 16 and i < 25]
        
        UR.reverse() #list from midlin outward
        LL.reverse()
        
        
        for i, quad in enumerate([UR, UL, LL, LR]):
            
            if i == 0:
                x_dir = Vector((-1,0,0))
                y_dir = Vector((0,1,0))
            if i == 1:
                x_dir = Vector((1,0,0))
                y_dir = Vector((0,1,0))
            if i == 2:
                x_dir = Vector((1,0,0))
                y_dir = Vector((0,-1,0))
            if i == 3:
                x_dir = Vector((-1,0,0))
                y_dir = Vector((0,-1,0))
                
            
            if len(quad) == 0: continue
            row_height = max([bpy.data.objects.get(str(tooth) +":CEJ").dimensions[1] for tooth in quad])
                    
            y_pos = y_dir * (row_height/2 + inter_space_y)
            x_pos = x_dir * (middle_space_x/2 - inter_space_x) # middle space gets added inititally
            z_pos = Vector((0,0,cyl_depth))
            
            for tooth in quad:
                
                if tooth > 16:
                    #rotate 180
                    R = Matrix.Rotation(math.pi, 4, Vector((0,0,1)))
                    print('TBA on matrices')
                else:
                    R = Matrix.Identity(4)
        
                cej_ob = bpy.data.objects.get(str(tooth)+":CEJ")
                
                x_pos += x_dir *(inter_space_x + 0.5 * cej_ob.dimensions[0])
        
                T = Matrix.Translation(x_pos + y_pos + z_pos)
                
                cej_ob.matrix_world = T * scl_mx
        
                new_ob = bpy.data.objects.new(str(tooth) + ":Abutment", new_me)
                context.scene.objects.link(new_ob)
                
                T = Matrix.Translation(x_pos + y_pos)
                new_ob.matrix_world = T * R
                new_ob.hide_select = True
                
                x_pos += x_dir * 0.5 * cej_ob.dimensions[0]
        
        ti_base_obj.hide = True
        return {'FINISHED'}
    
class OPENDENTAL_OT_heal_database_profiles(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_database_profiles"
    bl_label = "Database CEJ Profiles"
    bl_options = {'REGISTER', 'UNDO'}
    
    inter_space_x = bpy.props.FloatProperty(name = 'horizontal', default = 2.0, min = 1.5, max = 10)
    inter_space_y = bpy.props.FloatProperty(name = 'vertical', default = 2.0, min = 1.5, max = 10)
    middle_space_x = bpy.props.FloatProperty(name = 'middle', default = 2.0, min = 1.5, max = 10)
    cyl_depth = bpy.props.FloatProperty(name = 'depth', default = 5.0, min = 2, max = 11)
    
    @classmethod
    def poll(cls, context):
        
        if "Abutment:Master" not in bpy.data.objects:
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Layout and Position")
        col.prop(self, "cyl_depth")
        col.prop(self, "inter_space_x")
        col.prop(self, "inter_space_y")
        col.prop(self, "middle_space_x")
        
    def invoke(self,context, event):
        prefs = get_settings()
        
        #get initial settings form preferences default
        #load them into operator settings for undo/redo
        self.inter_space_x = prefs.heal_inter_space_x
        self.inter_space_y = prefs.heal_inter_space_y
        self.middle_space_x = prefs.heal_middle_space_x
        self.cyl_depth = prefs.heal_abutment_depth
        
        return self.execute(context)
        
    def execute(self, context):

        prefs = get_settings()
        
        inter_space_x = self.inter_space_x
        inter_space_y = self.inter_space_y
        middle_space_x = self.middle_space_x
        cyl_depth = self.cyl_depth

        ti_base_obj = bpy.data.objects['Abutment:Master']
                
        bme = bmesh.new()
        bme.from_mesh(ti_base_obj.data)
        new_me = bpy.data.meshes.new('UCLA_dup')
        bme.to_mesh(new_me)
        bme.free()
        
        teeth = [i+1 for i in range(0,32) if prefs.heal_teeth[i]]
        
        if len(teeth) == 0:
            self.report({'ERROR'}, 'Need to select teeth to generate template for')
            return {'CANCELLED'}
        
        if not all([str(tooth) in bpy.data.meshes for tooth in teeth]):
            self.report({'ERROR'}, 'Database templates not available, generate generic templates')
            return {'CANCELLED'}
        
        print('THE PROFILES SHOULD BE SCALED by  :' + prefs.profile_scale)
        if prefs.profile_scale == 'SMALL':
            scl = .8
        elif prefs.profile_scale == 'MEDIUM':
            scl = 1
        elif prefs.profile_scale == 'LARGE':
            scl = 1.2
        else:
            scl = 5
        
        scl_mx = Matrix.Identity(4)
        scl_mx[0][0], scl_mx[1][1] = scl, scl    
        #get all the tooth_objects into the scene
        for tooth in teeth:
            new_ob = bpy.data.objects.new(str(tooth)+":CEJ", bpy.data.meshes[str(tooth)])
            #new_ob.matrix_world = scl_mx
            context.scene.objects.link(new_ob)
            
        #sort teeth by quadrant
        UR = [i for i in teeth if i < 9]
        UL = [i for i in teeth if i > 8 and i < 17]
        LR = [i for i in teeth if i > 24]
        LL = [i for i in teeth if i > 16 and i < 25]
        
        UR.reverse() #list from midlin outward
        LL.reverse()
        
        for i, quad in enumerate([UR, UL, LL, LR]):
            
            if i == 0:
                x_dir = Vector((-1,0,0))
                y_dir = Vector((0,1,0))
            if i == 1:
                x_dir = Vector((1,0,0))
                y_dir = Vector((0,1,0))
            if i == 2:
                x_dir = Vector((1,0,0))
                y_dir = Vector((0,-1,0))
            if i == 3:
                x_dir = Vector((-1,0,0))
                y_dir = Vector((0,-1,0))
                
            
        
            row_height = max([bpy.data.objects.get(str(tooth) +":CEJ").dimensions[1] for tooth in quad])
                    
            y_pos = y_dir * (row_height/2 + inter_space_y)
            x_pos = x_dir * (middle_space_x/2 - inter_space_x) # middle space gets added inititally
            z_pos = Vector((0,0,cyl_depth))
            
            for tooth in quad:
                
                if tooth > 16:
                    #rotate 180
                    R = Matrix.Rotation(math.pi, 4, Vector((0,0,1)))
                    print('TBA on matrices')
                else:
                    R = Matrix.Identity(4)
        
                cej_ob = bpy.data.objects.get(str(tooth)+":CEJ")
        
                x_pos = x_pos + x_dir *(inter_space_x + cej_ob.dimensions[0]/2)
        
                T = Matrix.Translation(x_pos + y_pos + z_pos)
                
                cej_ob.matrix_world = T * scl_mx
        
                new_ob = bpy.data.objects.new(str(tooth) + ":Abutment", new_me)
                context.scene.objects.link(new_ob)
                new_ob.hide_select = True
                
                T = Matrix.Translation(x_pos + y_pos)
                new_ob.matrix_world = T * R

                x_pos = x_pos + x_dir *cej_ob.dimensions[0]/2
        ti_base_obj.hide = True
        return {'FINISHED'}


class OPENDENTAL_OT_heal_mirror_transform(bpy.types.Operator):
    """
    Transforms will mirror to other side for symmetric editing
    """
    bl_idname = "opendental.heal_mirror_transform"
    bl_label = "Mirror Transforms"
    
    def execute(self,context):
        
        handlers = [hand.__name__ for hand in bpy.app.handlers.scene_update_post]
        prefs = get_settings()
        
        if "mirror_transforms" not in handlers:
            bpy.app.handlers.scene_update_post.append(mirror_transforms)
            
        prefs.heal_mirror_transform = True
        
        cejs = [ob for ob in bpy.data.objects if ":CEJ" in ob.name]
        for ob in cejs:
            update_transform(ob)
            
            
        return {'FINISHED'}

class OPENDENTAL_OT_heal_isolate_view(bpy.types.Operator):
    """
    Will put just the active object into local view
    """
    bl_idname = "opendental.heal_isolate_view"
    bl_label = "Isolate View"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        if context.object != None:
            return True
        else:
            return False
        
    def execute(self,context):
        
        for ob in context.scene.objects:
            ob.select = False
            ob.hide = True
            
        context.object.select = True
        context.object.hide = False
        
        bpy.ops.view3d.view_selected()
        
            
        return {'FINISHED'}
    
class OPENDENTAL_OT_heal_global_view(bpy.types.Operator):
    """
    Unhides all profiles and bases
    """
    bl_idname = "opendental.heal_global_view"
    bl_label = "Global View"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        vis_obs = [ob for ob in context.scene.objects if not ob.hide]
        
        if len(vis_obs) <= 1:
            return True
        else:
            return False
    def execute(self,context):
        
        for ob in context.scene.objects:
            
            if ":Profile" in ob.name:
                ob.hide = False
                
            if ":Abutment" in ob.name:
                ob.hide = False
        
        bpy.ops.view3d.view_all(center = True)
    
        return {'FINISHED'}
        
class OPENDENTAL_OT_heal_stop_mirror(bpy.types.Operator):
    """
    Transforms will not mirror to other side for symmetric editing
    """
    bl_idname = "opendental.heal_stop_mirror"
    bl_label = "Stop Mirror"
    
    def execute(self,context):
        
        handlers = [hand.__name__ for hand in bpy.app.handlers.scene_update_post]
        prefs = get_settings()
        
        if "mirror_transforms" in handlers:
            bpy.app.handlers.scene_update_post.remove(mirror_transforms)
            
        prefs.heal_mirror_transform = False
        
        return {'FINISHED'}

def ensure_passivity2(prof_ob):
     
    bme = bmesh.new()
    bme.from_mesh(prof_ob.data)
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.faces.ensure_lookup_table()
    
    for f in bme.faces:
        f.select = False
    for ed in bme.edges:
        ed.select = False
    for v in bme.verts:
        v.select = False
        
    top_f = bme.faces[128]
    bottom_f = bme.faces[129]
    
    center = bottom_f.calc_center_bounds()
    center2d = Vector((center[0],center[1]))
    for v in top_f.verts:
        
        ed_vertical = [ed for ed in v.link_edges if top_f not in ed.link_faces][0]
        v1 = ed_vertical.other_vert(v)
        
        iters = 0
        while ed_vertical != None and iters < 9:
            iters += 1
            r0 = v.co.to_2d() - center2d
            r1 = v1.co.to_2d() - center2d
            
            if r1.length > r0.length:
                #print('correcting a vertex')
                correction = (r0.length - r1.length) * r1.normalized()
                v1.co = v1.co + correction.to_3d()
                v1.select = True
                
            eds_vertical = [ed for ed in v1.link_edges if ed != ed_vertical and not any([f in ed_vertical.link_faces for f in ed.link_faces])]
            if len(eds_vertical) == 0:
                break
            ed_vertical = eds_vertical[0]
            v = v1
            v1 = ed_vertical.other_vert(v)
    
    for v in bottom_f.verts:
        
        ed_vertical = [ed for ed in v.link_edges if bottom_f not in ed.link_faces][0]
        v1 = ed_vertical.other_vert(v)
        
        iters = 0
        while ed_vertical != None and iters < 9:
            iters += 1
            r0 = v.co.to_2d() - center2d
            r1 = v1.co.to_2d() - center2d
            
            if r1.length < r0.length:
                #print('correcting a vertex')
                correction = (r0.length - r1.length) * r1.normalized()
                v1.co = v1.co + correction.to_3d()
                v1.select = True
                
            eds_vertical = [ed for ed in v1.link_edges if ed != ed_vertical and not any([f in ed_vertical.link_faces for f in ed.link_faces])]
            if len(eds_vertical) == 0:
                break
            ed_vertical = eds_vertical[0]
            v = v1
            v1 = ed_vertical.other_vert(v)        
        
    
    #ensure_3deg_taper
    for v in bottom_f.verts:
        
        ed_vertical = [ed for ed in v.link_edges if bottom_f not in ed.link_faces][0]
        v1 = ed_vertical.other_vert(v)
        
        iters = 0
        while ed_vertical != None and iters < 11:
            iters += 1
            r0 = v.co.to_2d() - center2d
            r1 = v1.co.to_2d() - center2d
            
            dz = v1.co[2] - v.co[2]
            dr = math.tan(3 * math.pi / 180) * dz
            if r1.length < r0.length + dr:
                #print('correcting a vertex taper')
                correction = ((r0.length + dr) - r1.length) * r1.normalized()
                v1.co = v1.co + correction.to_3d()
                v1.select = True
                
            eds_vertical = [ed for ed in v1.link_edges if ed != ed_vertical and not any([f in ed_vertical.link_faces for f in ed.link_faces])]
            if len(eds_vertical) == 0:
                break
            ed_vertical = eds_vertical[0]
            v = v1
            v1 = ed_vertical.other_vert(v)
            
                            
    bme.to_mesh(prof_ob.data)
    bme.free() 



def ensure_passivity(prof_ob):
     
    bme = bmesh.new()
    bme.from_mesh(prof_ob.data)
    bme.verts.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.faces.ensure_lookup_table()
    
    top_vs = [bme.verts[i] for i in range(128,192)]
    bottom_vs = [bme.verts[i] for i in range(192,256)]
    
    
    
    top_eds = [ed.index for ed in bme.edges if ed.verts[0] in top_vs and ed.verts[1] in top_vs]
    bottom_eds = [ed.index for ed in bme.edges if ed.verts[0] in bottom_vs and ed.verts[1] in bottom_vs]
    
    for f in bme.faces:
        f.select = False
    for ed in bme.edges:
        ed.select = False
    for v in bme.verts:
        v.select = False
    
    #for ed in top_eds:
    #    ed.select = True
    #for ed in bottom_eds:
    #    ed.select = True
    
    
    #bottom up pass
    finished_eds = set(top_eds)
    prev_loop = [v.co.to_2d() for v in top_vs]
    gdict = edge_loop_neighbors(bme, top_eds, strict = False, trim_tails = True, expansion = 'EDGES', quad_only = True)
    
    next_vloop = [bme.verts[i] for i in gdict['VERTS'][0]]
    next_ed_loop = gdict['EDGES'][0]
    
    
    
    
    for M in range(0,9):
        for v in next_vloop:
            if not point_inside_loop2d(prev_loop, v.co.to_2d()):
                
                print('correcting a point in loop %i' % M)
                v.select = True
                #v_best = min(prev_loop, key = lambda x: (x - v.co.to_2d()).length)
                #v_closest = nearest_point_to_path(v.co.to_2d(), prev_loop, cyclic = True)
                
                #v.co = Vector((v_closest[0], v_closest[1], v.co[2]))
                #v.co = Vector((v_best[0], v_best[1], v.co[2]))
        
        
        prev_loop = [v.co.to_2d() for v in next_vloop]  #record verts as vert loop        
        finished_eds.update(next_ed_loop)
        gdict = edge_loop_neighbors(bme, next_ed_loop, strict = False, trim_tails = True, expansion = 'EDGES', quad_only = True)
        
        if bme.edges[gdict['EDGES'][0][0]] in finished_eds:
            next_ed_loop = gdict['EDGES'][1]
            next_vloop = [bme.verts[i] for i in gdict['VERTS'][1]]
        else:
            next_ed_loop = gdict['EDGES'][0]
            next_vloop = [bme.verts[i] for i in gdict['VERTS'][0]]
        
        
                    
    bme.to_mesh(prof_ob.data)
    bme.free()
    
class OPENDENTAL_OT_heal_mesh_convert(bpy.types.Operator):
    """Make smooth connection between CEJ and UCLA collar"""
    bl_idname = "opendental.heal_mesh_convert"
    bl_label = "Convert CEJ Curves"
    bl_options = {'REGISTER', 'UNDO'}
    
    shape_factor = bpy.props.FloatProperty(name = "Shape Factor", default = 0.05, step = 1, min = 0, max = 3)
    
    @classmethod
    def poll(cls, context):
        
        if "Abutment:Master" not in bpy.data.objects:
            return False

        return True
    
    def execute(self, context):
        prefs = get_settings()
    
        cyl_depth = prefs.heal_abutment_depth

        cej_objects = [ob for ob in bpy.data.objects if ':CEJ' in ob.name]
        z_max = 0
        
        for ob in cej_objects:
            bb = ob.bound_box
            for v in bb:
                loc = ob.matrix_world * Vector(v)

                if loc[2] > z_max:
                    z_max = loc[2]  
            
        if len(cej_objects) == 0:
            self.report({'ERROR'},'No CEJ Profiles, generate profiles first')
            
    
        for ob in cej_objects:
            #works for curves or existing mesh
            me = ob.to_mesh(bpy.context.scene, apply_modifiers = True, settings = 'PREVIEW')
            me.transform(ob.matrix_world.to_3x3().to_4x4())  #this should handle the scaling so the circle is still circle
            
            name = ob.name.replace(":CEJ",":Abutment")
            tibase = bpy.data.objects.get(name)
            if not tibase:
                continue
            
            bme = bmesh.new()
            bme.from_mesh(me)
            bme.edges.ensure_lookup_table()
            bme.verts.ensure_lookup_table()
            
            eds = [ed.index for ed in bme.edges]
            loops = edge_loops_from_bmedges(bme, eds)
            
            loop = loops[0]
            loop.pop()
            
            locs = [bme.verts[i].co for i in loop]
            
            
            spaced_locs, eds = space_evenly_on_path(locs, [(0,1),(1,0)], 64) #TODO...increase res a little
            
            r = tibase.dimensions[0]/2
            center = tibase.location - ob.location #to
            
            center2D = Vector((center[0], center[1]))
            for i, v in enumerate(spaced_locs):
                V = Vector((v[0], v[1])) - center2D
                if V.length < r + .3:
                    correctedxy = center2D + (r + .3) * V.normalized()
                    spaced_locs[i] = Vector((correctedxy[0], correctedxy[1], v[2]))
            bme.free()
            
            bme = bmesh.new()
            bme.verts.ensure_lookup_table()
            bme.edges.ensure_lookup_table()
            new_verts = []
            for co in spaced_locs:
                new_verts += [bme.verts.new(co)]
                
            bme.verts.ensure_lookup_table()
            cej_eds = []
            for ed in eds:
                cej_eds += [bme.edges.new((new_verts[ed[0]],new_verts[ed[1]]))]
            
            if ob.matrix_world[2][2] < 1:
                ob.matrix_world[2][2] = 1
            center = ob.matrix_world.inverted() * tibase.location
            T = Matrix.Translation(center)
            if bversion() > "002.079.003":
                circle_data = bmesh.ops.create_circle(bme, cap_ends = False, segments = 64, radius = tibase.dimensions[0]/2 + .1, matrix = T)
            else:
                circle_data = bmesh.ops.create_circle(bme, cap_ends = False, segments = 64, diameter = tibase.dimensions[0]/2 + .1, matrix = T)
            #for bmv in circle_data['verts']:
                #bmv.co[2] -= cyl_depth
                
            circle_eds = [ed for ed in bme.edges if ed not in cej_eds]
            
            top_geom = bmesh.ops.extrude_edge_only(bme, edges = cej_eds)
            
            bottom_geom = bmesh.ops.extrude_edge_only(bme, edges = circle_eds)
            
            top_verts  = [v for v in top_geom['geom'] if isinstance(v, bmesh.types.BMVert)]
            for v in top_verts:
                v.co[2] = z_max + .3 - cyl_depth  #I don't understand this math completely
            
            bme.faces.new(top_verts)
            
            bottom_verts = [v for v in bottom_geom['geom'] if isinstance(v, bmesh.types.BMVert)]  
            for v in bottom_verts:
                v.co[2] -= .1
            
            bme.faces.new(bottom_verts)
            
            for ed in cej_eds:
                ed.select_set(True)
            for ed in circle_eds:
                ed.select_set(True)
            
            bme.faces.ensure_lookup_table()
            bmesh.ops.recalc_face_normals(bme, faces = bme.faces)
               
            new_me = bpy.data.meshes.new(ob.name.replace('CEJ','Profile'))
            new_ob = bpy.data.objects.new(ob.name.replace('CEJ','Profile'), new_me)
            bpy.context.scene.objects.link(new_ob)
            new_ob.matrix_world = Matrix.Translation(ob.matrix_world.to_translation())
            new_ob.lock_scale[2] = True
            
            bme.to_mesh(new_me)
            bme.free()
            
            context.scene.objects.active = new_ob
            new_ob.select = True
        
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            context.tool_settings.mesh_select_mode = [False, True, False]
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            if prefs.heal_profile == 'HOURGLASS':
                interp = 'SURFACE'
                prof_shape = 'LINEAR'
                smooth = 1
                prof_shape_factor = 0

            elif prefs.heal_profile == 'CONE':
                interp = 'LINEAR'
                prof_shape = 'LINEAR'
                smooth = 1
                prof_shape_factor = 0
                
            elif prefs.heal_profile == 'BOWL':
                interp = 'SURFACE'
                prof_shape = 'SMOOTH'
                smooth = 0.0
                prof_shape_factor = 0.1
                
            elif prefs.heal_profile == 'DEEP_BOWL':
                interp = 'PATH'
                prof_shape = 'LINEAR'
                smooth = 0.5
                prof_shape_factor = 0.2
                
            bpy.ops.mesh.bridge_edge_loops(number_cuts=8, 
                                    interpolation=interp, 
                                    smoothness=smooth,
                                    profile_shape = prof_shape,
                                    profile_shape_factor=prof_shape_factor)
                                    
            bpy.ops.object.mode_set(mode = 'OBJECT')
            ensure_passivity2(new_ob)   
        
        return {"FINISHED"}

class OPENDENTAL_OT_heal_reprofile(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_reprofile"
    bl_label = "Reshape Emergence"
    bl_options = {'REGISTER', 'UNDO'}
    
    items = ['HOURGLASS','CONE','BOWL','DEEP_BOWL']
    items_enum = []
    for index, item in enumerate(items):
        items_enum.append((item, item, item))
       
    preset = bpy.props.EnumProperty(items = items_enum, name = "Preset Shape", default = 'BOWL')
    
    smoothness = bpy.props.FloatProperty(name = 'smooth', default = 1, min = 0, max = 2)
    profile_shape_factor = bpy.props.FloatProperty(name = 'profile', default = .2, min = -.5, max = 2)
    
    
    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        if ":Profile" not in context.object.name:
            return False
        
        return True
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Adjustable Options")
        col.prop(self, "smoothness")
        col.prop(self, "profile_shape_factor")
        
    def invoke(self,context, event):
        
        if self.preset == 'HOURGLASS':
            self.smoothness = 1
            self.profile_shape_factor = 0
            #blend_surface
            #doesn't matter
        elif self.preset == 'CONE':
            self.smoothness = 1
            self.profile_shape_factor = 0
            #blend path
        elif self.preset == 'BOWL':
            self.smoothness = 0.0
            self.profile_shape_factor = 0.1
            
        elif self.preset == 'DEEP_BOWL':
            self.smoothness = 0.5
            self.profile_shape_factor = 0.2
            #blend_path
            #inverse square
        return self.execute(context)
        
    def execute(self, context):
        
        ob = context.object
        ob.select = True
        ob.update_tag()
        ob.data.update()
        context.scene.update()
        
        context.tool_settings.mesh_select_mode = [False, False, True]
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        for i in range(0,130):
            ob.data.polygons[i].select = True
        
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'INVERT')
        bpy.ops.mesh.delete(type = 'FACE')
        context.tool_settings.mesh_select_mode = [False, True, False]
        bpy.ops.mesh.select_non_manifold()
        
        
        if self.preset == 'HOURGLASS':
            interp = 'SURFACE'
            prof_shape = 'LINEAR'
            
        if self.preset == 'CONE':
            interp = 'LINEAR'
            prof_shape = 'LINEAR'
            
        if self.preset == 'BOWL':
            interp = 'SURFACE'
            prof_shape = 'SMOOTH'
            
        if self.preset == 'DEEP_BOWL':
            interp = 'PATH'
            prof_shape = 'LINEAR'
            
        bpy.ops.mesh.bridge_edge_loops(number_cuts=8, 
                                    interpolation=interp, 
                                    smoothness=self.smoothness,
                                    profile_shape = prof_shape,
                                    profile_shape_factor=self.profile_shape_factor)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        
        ensure_passivity2(ob)
        ob.update_tag()
        ob.data.update()
        context.scene.update()
        
        
        return {'FINISHED'}
        
class OPENDENTAL_OT_heal_generate_box(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "opendental.heal_generate_box"
    bl_label = "Generate Box"
    bl_options = {'REGISTER', 'UNDO'}
    
    bottom_trim = bpy.props.FloatProperty(name = "Bottom Trim", default = .1, min = .01, max = 3)
    bevel_width = bpy.props.FloatProperty(name = "Bevel Width", default = 3, min = 1, max = 5)
    
    border_x = bpy.props.FloatProperty(name = "Horizontal Border", default = 2, min = 1.5, max = 20)
    border_y = bpy.props.FloatProperty(name = "Vertical Border", default = 5, min = 1.5, max = 20)
    
    @classmethod
    def poll(cls, context):
        profs = [ob.name for ob in bpy.data.objects if 'Profile' in ob.name]
        if len(profs) == 0:
            return False
        return True
    
    def invoke(self, context, event):
        prefs = get_settings()
        
        self.bevel_width = prefs.heal_bevel_width
        self.border_x = prefs.heal_block_border_x
        self.border_y = prefs.heal_block_border_y
        self.wall_thickness = prefs.mould_wall_thickness
        return self.execute(context)
        
    def execute(self, context):
        prefs = get_settings()
        if prefs.heal_print_type == 'INVERTED':
            return self.execute_mould(context)
        else:
            return self.execute_box(context)
    def execute_mould(self, context):
        profile_obs = [ob for ob in bpy.data.objects if 'Profile' in ob.name]
        base_obs = [ob for ob in bpy.data.objects if ":Abutment" in ob.name] #notice master is TiBase:Master
        
        prefs = get_settings()
        
        start_bb = profile_obs[0].bound_box
        mx = profile_obs[0].matrix_world
        start = mx * Vector(start_bb[0])
        x_max, y_max, z_max = start[0], start[1], start[2]
        x_min, y_min, z_min = start[0], start[1], start[2]
        
        for ob in profile_obs:
            bb = ob.bound_box
            for v in bb:
                loc = ob.matrix_world * Vector(v)
                if loc[0] > x_max:
                    x_max = loc[0]
                if loc[1] > y_max:
                    y_max = loc[1]
                if loc[2] > z_max:
                    z_max = loc[2]
                    
                if loc[0] < x_min:
                    x_min = loc[0]
                if loc[1] < y_min:
                    y_min = loc[1]
                
        for ob in base_obs:
            bb = ob.bound_box
            for v in bb:
                loc = ob.matrix_world * Vector(v)
                if loc[2] < z_min:
                    z_min = loc[2]    
                    
        box_top = z_max - 0.29 #epsilon
        box_bottom = z_min + self.bottom_trim
        
        box_x = x_max + self.border_x
        box_y = y_max + self.border_y
        
        box_x_min = x_min - self.border_x
        box_y_min = y_min - self.border_y
        
        old_obs = [ob.name for ob in bpy.data.objects]
        bpy.ops.mesh.primitive_cube_add(radius = 0.5, location = Vector((0,0,0)))
        cube = [ob for ob in bpy.data.objects if ob.name not in old_obs][0]
        cube.name = "Templates Base"
        me = cube.data
        
        me.vertices[0].co = Vector((box_x_min,box_y_min, box_bottom))
        me.vertices[1].co = Vector((box_x_min,box_y_min,box_top))
        me.vertices[2].co = Vector((box_x_min, box_y,box_bottom))
        me.vertices[3].co = Vector((box_x_min ,box_y, box_top))
        me.vertices[4].co = Vector((box_x, box_y_min, box_bottom))
        me.vertices[5].co =Vector((box_x, box_y_min, box_top))
        me.vertices[6].co = Vector((box_x, box_y, box_bottom ))
        me.vertices[7].co = Vector((box_x, box_y, box_top))
        
        for v in me.vertices:
            v.select = False
        for ed in me.edges:
            ed.select = False
            
        for f in me.polygons:
            f.select = False
            
        context.tool_settings.mesh_select_mode = [False, True, False]
        
        context.tool_settings.mesh_select_mode = [False, False, True]
        me.polygons[4].select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.delete(type = 'ONLY_FACE')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        mod = cube.modifiers.new('Solid', type = 'SOLIDIFY')
        mod.offset = 1
        mod.thickness = self.wall_thickness
        cube.select = True
        context.scene.objects.active = cube
        bpy.ops.object.modifier_apply(modifier = 'Solid')
        
        inds = [2,5,8,11]
        for ind in inds:
            me.edges[ind].select = True

        context.scene.objects.active = cube
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.bevel(offset_type = "OFFSET", offset = self.bevel_width)
        
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        
        if "Box Mat" not in bpy.data.materials:
            mat = bpy.data.materials.new('Box Mat')
            mat.diffuse_color = Color((0.08, .08, .8))
        else:
            mat = bpy.data.materials.get('Box Mat')
        
        # Assign it to object
        if cube.data.materials:
            # assign to 1st material slot
            cube.data.materials[0] = mat
        else:
            # no slots
            cube.data.materials.append(mat)    
        
        mod = cube.modifiers.new('Remesh', type = 'REMESH')
        mod.octree_depth = 7
        mod.sharpness = 1
          
        return {"FINISHED"} 
    
    def execute_box(self, context):
    
        profile_obs = [ob for ob in bpy.data.objects if 'Profile' in ob.name]
        base_obs = [ob for ob in bpy.data.objects if ":Abutment" in ob.name] #notice master is TiBase:Master
        
        prefs = get_settings()
        
        start_bb = profile_obs[0].bound_box
        mx = profile_obs[0].matrix_world
        start = mx * Vector(start_bb[0])
        x_max, y_max, z_max = start[0], start[1], start[2]
        x_min, y_min, z_min = start[0], start[1], start[2]
        
        for ob in profile_obs:
            bb = ob.bound_box
            for v in bb:
                loc = ob.matrix_world * Vector(v)
                if loc[0] > x_max:
                    x_max = loc[0]
                if loc[1] > y_max:
                    y_max = loc[1]
                if loc[2] > z_max:
                    z_max = loc[2]
                    
                if loc[0] < x_min:
                    x_min = loc[0]
                if loc[1] < y_min:
                    y_min = loc[1]
                
        for ob in base_obs:
            bb = ob.bound_box
            for v in bb:
                loc = ob.matrix_world * Vector(v)
                if loc[2] < z_min:
                    z_min = loc[2]    
                    
        box_top = z_max - .09  #epsilon
        box_bottom = z_min + self.bottom_trim
        
        box_x = x_max + self.border_x
        box_y = y_max + self.border_y
        
        box_x_min = x_min - self.border_x
        box_y_min = y_min - self.border_y
        
        old_obs = [ob.name for ob in bpy.data.objects]
        bpy.ops.mesh.primitive_cube_add(radius = 0.5, location = Vector((0,0,0)))
        cube = [ob for ob in bpy.data.objects if ob.name not in old_obs][0]
        cube.name = "Templates Base"
        me = cube.data
        
        me.vertices[0].co = Vector((box_x_min,box_y_min, box_bottom))
        me.vertices[1].co = Vector((box_x_min,box_y_min,box_top))
        me.vertices[2].co = Vector((box_x_min, box_y,box_bottom))
        me.vertices[3].co = Vector((box_x_min ,box_y, box_top))
        me.vertices[4].co = Vector((box_x, box_y_min, box_bottom))
        me.vertices[5].co =Vector((box_x, box_y_min, box_top))
        me.vertices[6].co = Vector((box_x, box_y, box_bottom ))
        me.vertices[7].co = Vector((box_x, box_y, box_top))
        
        for v in me.vertices:
            v.select = False
        for ed in me.edges:
            ed.select = False
            
        for f in me.polygons:
            f.select = False
            
        context.tool_settings.mesh_select_mode = [False, True, False]
        
        inds = [0,1,3,4,6,7,9,10]
        
        for ind in inds:
            me.edges[ind].select = True

        context.scene.objects.active = cube
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.bevel(offset_type = "OFFSET", offset = self.bevel_width)
        
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if "Box Mat" not in bpy.data.materials:
            mat = bpy.data.materials.new('Box Mat')
            mat.diffuse_color = Color((0.08, .08, .8))
        else:
            mat = bpy.data.materials.get('Box Mat')
        
        # Assign it to object
        if cube.data.materials:
            # assign to 1st material slot
            cube.data.materials[0] = mat
        else:
            # no slots
            cube.data.materials.append(mat)    
        
        mod = cube.modifiers.new('Remesh', type = 'REMESH')
        mod.octree_depth = 7
        mod.sharpness = 1
          
        return {"FINISHED"}    




class OPENDENTAL_OT_heal_generate_text(bpy.types.Operator):
    """Generate Label above/below the wells"""
    bl_idname = "opendental.heal_generate_text"
    bl_label = "Generate Labels"
    bl_options = {'REGISTER', 'UNDO'}
    
    font_size = bpy.props.FloatProperty(default = 3.0, description = "Text Size", min = 1, max = 7)
     
    @classmethod
    def poll(cls, context):
        profs = [ob.name for ob in bpy.data.objects if 'Profile' in ob.name]
        if len(profs) == 0:
            return False
        return True
    

    def invoke(self, context, event):
        prefs = get_settings()
        self.font_size = prefs.default_text_size
        
        return self.execute(context)
        
    def execute(self, context):
    
        profile_obs = [ob for ob in bpy.data.objects if 'Profile' in ob.name and 'Final' not in ob.name]
        prefs = get_settings()
        #goal is 5mm x 5mm text?
        
        ys = []
        zs = []
        for ob in profile_obs:
            bb = ob.bound_box
            for v in bb:
                loc = ob.matrix_world * Vector(v)
                ys += [loc[1]]
                zs += [loc[2]]
                
        max_y = max(ys)
        min_y = min(ys)
        
        if prefs.heal_print_type == 'DIRECT':
            #find the top of the block
            t_base = bpy.data.objects.get('Templates Base')
            bb = t_base.bound_box
            for v in bb:
                loc = t_base.matrix_world * Vector(v)
                zs += [loc[2]]
            
        max_z = max(zs)
        
        for ob in profile_obs:
            a = len(ob.name) - 8
            name = ob.name[0:a]
            
            if prefs.heal_number_sys == 'UNIVERSAL':
                msg = name
                
            elif prefs.heal_number_sys == 'PALMER':
                msg = tooth_to_text[int(name)]
            else:
                msg = tooth_to_FDI[int(name)]
                
            txt_crv = bpy.data.curves.new(name + ':Label', type = 'FONT')
            txt_crv.body = msg
            txt_crv.align_x = 'CENTER'
            txt_ob = bpy.data.objects.new(name + ':Label', txt_crv)
            
            txt_crv.extrude = 1
            txt_crv.size = self.font_size
            txt_crv.resolution_u = 5
            txt_crv.offset = .02  #thicken up the letters a little
            context.scene.objects.link(txt_ob)
            txt_ob.update_tag()
            context.scene.update()
            
            #re_mesh = txt_ob.modifiers.new('REMESH', type = 'REMESH')
            #re_mesh.use_remove_disconnected = False
            #re_mesh.octree_depth = 5
                   
            if int(name) > 16:
                y = min_y - 1 - txt_ob.dimensions[1]
            else:
                y = max_y + 1
                

            txt_ob.parent = ob
            if prefs.heal_print_type == 'INVERTED':
                S = Matrix.Identity(4)
                #S[0][0] = -1
                T = Matrix.Translation(Vector((ob.location[0], y, max_z-.2)))
                txt_ob.matrix_world = T * S
            else:
                txt_ob.matrix_world = Matrix.Translation(Vector((ob.location[0], y, max_z)))
                
        return {"FINISHED"}

class OPENDENTAL_OT_heal_custom_text(bpy.types.Operator):
    """Place Custom Text at 3D Cursor on template Box"""
    bl_idname = "opendental.heal_custom_text"
    bl_label = "Custom Label"
    bl_options = {'REGISTER', 'UNDO'}
    
    font_size = bpy.props.FloatProperty(default = 3.0, description = "Text Size", min = 1, max = 7)
    
    remesh_detail = bpy.props.IntProperty(default = 5, description = "Text Size", min = 4, max = 10)
    
    align_y = ['BOTTOM', 'CENTER', 'TOP']
    items_align_y = []
    for index, item in enumerate(align_y):
        items_align_y.append((item, item, item))
       
    y_align = bpy.props.EnumProperty(items = items_align_y, name = "Vertical Alignment", default = 'BOTTOM')
    
    
    align_x = ['LEFT', 'CENTER', 'RIGHT']
    items_align_x = []
    for index, item in enumerate(align_x):
        items_align_x.append((item, item, item))
    x_align = bpy.props.EnumProperty(items = items_align_x, name = "Horizontal Alignment", default = 'LEFT')
    
    invert = bpy.props.BoolProperty(default = False, description = "Mirror text for mould pouring")
    spin = bpy.props.BoolProperty(default = False, description = "Spin text for mould pouring")
    @classmethod
    def poll(cls, context):
        
        if "Templates Base" not in bpy.data.objects:
            return False
        return True
            
    
    def invoke(self, context, event):
        prefs = get_settings()
        self.font_size = prefs.default_text_size
        
        return self.execute(context)
        
    def execute(self, context):
        context.scene.update()
        
        prefs = get_settings()
        
        t_base = bpy.data.objects.get("Templates Base")
        #t_base = context.object
        
        mx = t_base.matrix_world
        imx = t_base.matrix_world.inverted()
        mx_norm = imx.transposed().to_3x3()
        
        cursor_loc = context.scene.cursor_location
        
        ok, new_loc, no, ind = t_base.closest_point_on_mesh(imx * cursor_loc)
        
        X = Vector((1,0,0))
        Y = Vector((0,1,0))
        Z = Vector((0,0,1))
        
        #figure out which face the cursor is on
        direct = [no.dot(X), no.dot(Y), no.dot(Z)]
        
        if direct[0]**2 > 0.9:
            
            if direct[0] < 0:
                z = -X
                y = Z
                x = -Y
            else:
                z = X
                y = Z
                x = Y
        elif direct[1]**2 > 0.9:
            if direct[1] < 0:
                z = -Y
                y = Z
                x = X
            else:
                z = Y
                y = Z
                x = -X
            
        elif direct[2]**2 > 0.9:
            if direct[2] < 0:
                z = -Z
                y = -Y
                x = X
            else:
                z = Z
                y = Y
                x = X
        else:
            self.report({'ERROR'},"Text on beveled surfaces not supported")
            return {'CANCELLED'}
        #currently, the base should not be scaled or rotated...but perhaps it may be later
        x = mx_norm * x
        y = mx_norm * y
        z = mx_norm * z    
        
        if self.spin:
            x *= -1
            y *= -1
            
        txt_crv = bpy.data.curves.new('Custom:Label', type = 'FONT')
        txt_crv.body = prefs.heal_custom_text
        txt_crv.align_x = 'LEFT'
        txt_crv.align_y = 'BOTTOM'
        txt_ob = bpy.data.objects.new('Custom:Label', txt_crv)
            
        txt_crv.extrude = 1
        txt_crv.size = self.font_size
        txt_crv.resolution_u = 5
        txt_crv.offset = .02  #thicken up the letters a little
        context.scene.objects.link(txt_ob)
        txt_ob.update_tag()
        context.scene.update()
        

        #handle the alignment
        translation = mx * new_loc
        
        bb = txt_ob.bound_box
        max_b = max(bb, key = lambda x: Vector(x)[1])
        max_y = max_b[1]
        
        if self.x_align == 'CENTER':
            delta_x = 0.5 * txt_ob.dimensions[0]
            if (self.spin and self.invert) or (self.invert and not self.spin):
                translation = translation + delta_x * x
            else:
                translation = translation - delta_x * x           
        elif self.x_align == 'RIGHT':
            delta_x = txt_ob.dimensions[0]
            
            if self.invert:
                translation = translation + delta_x * x 
            else:
                translation = translation - delta_x * x 
            
        if self.y_align == 'CENTER':
            delta_y = 0.5 * max_y
            translation = translation - delta_y * y
        elif self.y_align == 'TOP':
            delta_y = max_y
            translation = translation - delta_y * y
        #build the rotation matrix which corresponds
        R = Matrix.Identity(3)  #make the columns of matrix U, V, W
        R[0][0], R[0][1], R[0][2]  = x[0] ,y[0],  z[0]
        R[1][0], R[1][1], R[1][2]  = x[1], y[1],  z[1]
        R[2][0] ,R[2][1], R[2][2]  = x[2], y[2],  z[2]
        R = R.to_4x4()

        S = Matrix.Identity(4)
        
        if self.invert:
            S[0][0] = -1
              
        T = Matrix.Translation(translation)
        
        txt_ob.matrix_world = T * R * S
        
        tracking.trackUsage("apgCustomText",prefs.heal_custom_text)
                   
        return {"FINISHED"}
    
class OPENDENTAL_OT_heal_emboss_text(bpy.types.Operator):
    """Joins all text label objects and booean subtraction from the template block"""
    bl_idname = "opendental.heal_emboss_text"
    bl_label = "Emboss Text Into Block"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if "Templates Base" not in bpy.data.objects:
            return False
        return True
    

    def execute(self, context):
        prefs = get_settings()
        t_base = bpy.data.objects.get("Templates Base")

        labels = [ob for ob in bpy.data.objects if ob.type == 'FONT']
        
        
        all_obs = [ob.name for ob in bpy.data.objects]
        
        bpy.ops.object.select_all(action = 'DESELECT')
        for ob in labels:
            
            if '6' in ob.data.body or '9' in ob.data.body:
                octree = 5
            else:
                octree = 4
            print(ob.name)
            bpy.ops.object.select_all(action = 'DESELECT')
            ob.select = True
            ob.hide = False
            context.scene.objects.active = ob
            
            
            
            old_obs = [eob.name for eob in bpy.data.objects]
            
            bpy.ops.object.convert(target='MESH', keep_original=True)
            ob.select = False
            
            
            new_ob = [eob for eob in bpy.data.objects if eob.name not in old_obs][0]
            
            print(new_ob.name)
            new_ob.select = True
            context.scene.objects.active = new_ob
            mod = new_ob.modifiers.new('REMESH', type = 'REMESH')
            mod.octree_depth = octree
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.separate(type = 'LOOSE')
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        labels_new = [ob for ob in bpy.data.objects if ob.name not in all_obs]    
        for ob in labels_new:
            ob.update_tag()
        
        context.scene.update()
        label_final = join_objects(labels_new, name = 'Text Labels')
        
        for ob in labels_new:
            bpy.ops.object.select_all(action = 'DESELECT')
            context.scene.objects.unlink(ob)
            me = ob.data
            bpy.data.objects.remove(ob)
            bpy.data.meshes.remove(me)
             
        context.scene.objects.link(label_final)
        
        label_final.select = True
        context.scene.objects.active = label_final
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        #subtract the whole thing from the template block
        mod = t_base.modifiers.new(type = 'BOOLEAN', name = 'Boolean')
        mod.solver = 'CARVE'
        if prefs.heal_print_type == 'INVERTED':
            mod.operation = 'UNION'
        else:
            mod.operation = 'DIFFERENCE'
        mod.object = label_final
        
        t_base.draw_type = 'SOLID'
        
        label_final.hide = True
            
        t_base.hide = False
        t_base.select = True
        bpy.context.scene.objects.active = t_base
           
        return {"FINISHED"} 
    
    
class OPENDENTAL_OT_heal_create_final_template(bpy.types.Operator):
    """Solidifies the template box and subtracts the abutment and emergence profiles"""
    bl_idname = "opendental.heal_create_final_template"
    bl_label = "Boolean All Objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if "Templates Base" not in bpy.data.objects:
            return False
        return True
    

    def execute(self, context):
        prefs = get_settings()
        t_base = bpy.data.objects.get("Templates Base")

        profiles = [ob for ob in bpy.data.objects if "Profile" in ob.name]
        
        base_obs = [ob for ob in bpy.data.objects if ":Abutment" in ob.name]
        
        bpy.ops.object.select_all(action = 'DESELECT')
        
        
        #if 'Final Profiles' in bpy.data.objects:
        #    ob = bpy.data.objects.get('Final Profiles')
        #    context.scene.objects.unlink(ob)
        #    bpy.data.objects.remove(ob)
        #if 'Final Bases' in bpy.data.objects:
        #    ob = bpy.data.objects.get('Final Bases')
        #    context.scene.objects.unlink(ob)
        #    bpy.data.objects.remove(ob)
            
        profiles_joined = join_objects(profiles, 'Final Profiles')
        bases_joined = join_objects(base_obs, 'Final Bases')
        
        bme = bmesh.new()
        bme.from_mesh(bases_joined.data)
        bme.faces.ensure_lookup_table()
        bmesh.ops.recalc_face_normals(bme, faces = bme.faces[:])
        bme.to_mesh(bases_joined.data)
        bme.free()
        
        context.scene.objects.link(profiles_joined)
        context.scene.objects.link(bases_joined)
        
        
        #solidify the ti_base if solid print
        
        if prefs.heal_print_type != 'INVERTED':
            mod = bases_joined.modifiers.new(type = 'SOLIDIFY', name = 'OFFSET')
            mod.offset = 1
            mod.thickness = prefs.heal_passive_offset
            
            #mod.use_even_offset = True
            #mod.use_quality_normals = True 
            mod.use_rim_only = True 
        
        #join the tibase to the profiles
        mod = profiles_joined.modifiers.new(type = 'BOOLEAN', name = 'Boolean')
        mod.operation = 'UNION'
        mod.object = bases_joined
        
        #subtract the whole thing from the template block
        mod = t_base.modifiers.new(type = 'BOOLEAN', name = 'Base Boolean')
        
        if prefs.heal_print_type == 'INVERTED':
            mod.operation = 'UNION'
        else:
            mod.operation = 'DIFFERENCE'
        
        #mod.solver = 'CARVE'    
        mod.object = profiles_joined
        
        t_base.draw_type = 'SOLID'
        
        for ob in bpy.data.objects:
            ob.hide = True
            
        t_base.hide = False
        t_base.select = True
        bpy.context.scene.objects.active = t_base
           
        return {"FINISHED"} 

class OPENDENTAL_OT_heal_boolean_nudge(bpy.types.Operator):
    """slight nudge when booleans fail, creates up to .01 mm(10 microns) intentional error in abutment placement"""
    bl_idname = "opendental.heal_boolean_nudge"
    bl_label = "Boolean Nudge"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if "Templates Base" not in bpy.data.objects:
            return False
        return True
    

    def execute(self, context):
        
        
        ob = bpy.data.objects.get('Final Profiles')
        if ob == None: return {'FINISHED'}
        
        x, y, z = 0, 0, 0
        iters = 0
        while not any([x,y,z]) and iters < 100:
            x = random.randint(-2, 2)
            y = random.randint(-2, 2)
            z = random.randint(-2, 2)
            iters += 1
        
        err = (.005**2 * (x**2 + y**2 + z**2))**.5
        
        print('nudged %f' % err)
        ob.matrix_world[2][3] += .01 * z
        ob.matrix_world[1][3] += .01 * y
        ob.matrix_world[0][3] += .01 * x
        
        return {"FINISHED"} 

class OPENDENTAL_OT_heal_boolean_nudge_block(bpy.types.Operator):
    """Use this to fix holes in bottom not cutting through"""
    bl_idname = "opendental.heal_boolean_nudge_block"
    bl_label = "Boolean Nudge Block"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if "Templates Base" not in bpy.data.objects:
            return False
        return True
    

    def execute(self, context):
        
        
        ob = bpy.data.objects.get('Templates Base')
        if ob == None: return {'FINISHED'}
        
        ob.matrix_world[2][3] += .05
        
        return {"FINISHED"}


class OPENDENTAL_OT_heal_boolean_change_solver(bpy.types.Operator):
    """Use this to fix profiles not joining/subtracting from block succesfully"""
    bl_idname = "opendental.heal_boolean_change_solver"
    bl_label = "Boolean Solver Change"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        
        if "Templates Base" not in bpy.data.objects:
            return False
        return True
    
    solver = bpy.props.EnumProperty(items = [('BMESH','BMESH','BMESH'), ('CARVE','CARVE','CARVE')], default = 'CARVE')

    def execute(self, context):
        
        
        ob = bpy.data.objects.get('Templates Base')
        if ob == None: return {'FINISHED'}
        
        for mod in ob.modifiers:
            if mod.type == 'BOOLEAN':
                mod.solver = self.solver
        
        return {"FINISHED"}

class OPENDENTAL_OT_heal_auto_generate(bpy.types.Operator):
    """Generate Complete Box Base"""
    bl_idname = "opendental.heal_auto_generate"
    bl_label = "Create Template"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if "Abutment:Master" in context.scene.objects:
            return True
        else:
            return False
        
    def invoke(self,context,event):
        
        return self.exectute(context)
    
    def exectute(self,context):
        
        prefs = get_settings()
        
        bpy.ops.opendental.heal_database_profiles('INVOKE_DEFAULT')
        bpy.ops.opendental.heal_mesh_convert('EXEC_DEFAULT')
        bpy.ops.opendental.heal_generate_box('INVOKE_DEFAULT')
        bpy.ops.opendental.heal_generate_text(font_size = prefs.default_text_size)
        
        box = bpy.data.objects.get('Templates Base')
        
        
        #find where to place the text
        old_text = prefs.heal_custom_text
        file_path = prefs.heal_abutment_file
        
        if file_path != '' and prefs.heal_block_label == '':
            name = os.path.basename(file_path).split('.')[0]
            new_name = name.replace("_",' ')
     
        elif prefs.heal_block_label != '':
            new_name = prefs.heal_block_label
        elif prefs.heal_custom_text != '':
            new_name = prefs.heal_custom_text
        else:
            new_name = 'Custom APG Block'
            
        prefs.heal_custom_text = new_name
        
        if prefs.heal_print_type == 'DIRECT':
            bb = box.bound_box
            z = max(bb, key = lambda x: x[2])
            context.scene.cursor_location = Vector((0,0,z[2]))
            bpy.ops.opendental.heal_custom_text(x_align = 'CENTER', y_align = 'CENTER', font_size = prefs.default_text_size)
        else:
            bb = box.bound_box
            z = min(bb, key = lambda x: x[2])
            context.scene.cursor_location = Vector((0,0,z[2]+.3))
            bpy.ops.opendental.heal_custom_text(x_align = 'CENTER', y_align = 'CENTER', invert = True, spin = True, font_size = prefs.default_text_size)
            
        #Do the boolean ops
        bpy.ops.opendental.heal_emboss_text()
        bpy.ops.opendental.heal_create_final_template()
        
        bpy.ops.view3d.view_all(center = True)
        prefs.heal_custom_text = old_text
        
        
        params = [prefs.heal_print_type, prefs.heal_profile, prefs.profile_scale, prefs.heal_tooth_preset, prefs.heal_number_sys]
        tracking.trackUsage("apgWizard",params)
        return {'FINISHED'}

#panels we want to keep for the user
panels_keep = {'Anatomic Profile Generator','Brush', 'Stroke', '3D Cursor', 'Symmetry/Lock', 'Symmetry', 'Brush Curves'}
           
def register():
    bpy.utils.register_class(OPENDENTAL_OT_heal_import_abutment)
    bpy.utils.register_class(OPENDENTAL_OT_heal_abutment_generator)
    bpy.utils.register_class(OPENDENTAL_OT_heal_mark_platform)
    bpy.utils.register_class(OPENDENTAL_OT_heal_mark_timing)
    bpy.utils.register_class(OPENDENTAL_OT_heal_remove_internal)
    bpy.utils.register_class(OPENDENTAL_OT_ucla_remove_timing)
    bpy.utils.register_class(OPENDENTAL_OT_ucla_cut_above)
    bpy.utils.register_class(OPENDENTAL_OT_heal_extend_flat_region)
    #bpy.utils.register_class(OPENDENTAL_OT_heal_generate_profiles)
    bpy.utils.register_class(OPENDENTAL_OT_heal_database_profiles)
    bpy.utils.register_class(OPENDENTAL_OT_heal_database_curve_profiles)
    
    
    bpy.utils.register_class(OPENDENTAL_OT_heal_mirror_transform)
    bpy.utils.register_class(OPENDENTAL_OT_heal_stop_mirror)
    bpy.utils.register_class(OPENDENTAL_OT_heal_reprofile)
    bpy.utils.register_class(OPENDENTAL_OT_heal_isolate_view)
    bpy.utils.register_class(OPENDENTAL_OT_heal_global_view)
    bpy.utils.register_class(OPENDENTAL_OT_heal_mesh_convert)
    bpy.utils.register_class(OPENDENTAL_OT_heal_generate_box)
    bpy.utils.register_class(OPENDENTAL_OT_heal_generate_text)
    bpy.utils.register_class(OPENDENTAL_OT_heal_custom_text)
    bpy.utils.register_class(OPENDENTAL_OT_heal_emboss_text)
    bpy.utils.register_class(OPENDENTAL_OT_heal_create_final_template)
    bpy.utils.register_class(OPENDENTAL_OT_heal_boolean_nudge)
    bpy.utils.register_class(OPENDENTAL_OT_heal_boolean_nudge_block)
    bpy.utils.register_class(OPENDENTAL_OT_heal_boolean_change_solver)
    bpy.utils.register_class(OPENDENTAL_OT_heal_auto_generate)
    
    #clean up all 3d tool panels
    for pt in bpy.types.Panel.__subclasses__():
        if pt.bl_space_type == 'VIEW_3D':
            if pt.bl_label in panels_keep: continue
            if "bl_rna" in pt.__dict__:   # <-- check if we already removed!
                bpy.utils.unregister_class(pt)
                __m.panels += [pt]
        #if pt.bl_space_type == 'PROPERTIES':
        #    if "bl_rna" in pt.__dict__:
                
        #        if hasattr(pt, 'bl_idname'):
        #            print(pt.bl_idname)
                    
                    
                #bpy.utils.unregister_class(pt)
                #__m.panels += [pt]
        
    #bpy.utils.register_module(__name__)
   
def unregister():
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_import_abutment)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_abutment_generator)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_mark_platform)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_mark_timing)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_remove_internal)
    bpy.utils.unregister_class(OPENDENTAL_OT_ucla_remove_timing)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_extend_flat_region)
    #bpy.utils.unregister_class(OPENDENTAL_OT_heal_generate_profiles)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_database_profiles)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_database_curve_profiles)
    bpy.utils.unregister_class(OPENDENTAL_OT_ucla_cut_above)
    
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_mirror_transform)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_stop_mirror)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_reprofile)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_isolate_view)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_global_view)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_mesh_convert)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_generate_box)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_generate_text)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_custom_text)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_emboss_text)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_create_final_template)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_boolean_nudge)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_boolean_nudge_block)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_boolean_change_solver)
    bpy.utils.unregister_class(OPENDENTAL_OT_heal_auto_generate)

    for pt in __m.panels:
        if pt.bl_space_type == 'VIEW_3D':
            if pt.bl_label in panels_keep: continue
            if "bl_rna" not in pt.__dict__:   # <-- check if we already removed!
                bpy.utils.register_class(pt)
                
        if pt.bl_space_type == 'PROPERTIES':
            if "bl_rna" not in pt.__dict__:
                bpy.utils.register_class(pt)
                
    __m.panels = []
    
if __name__ == "__main__":
    register()