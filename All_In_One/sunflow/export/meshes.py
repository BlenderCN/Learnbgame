# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          14-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

# import os
# import time

import bpy
import math
import mathutils
# Framework libs
from extensions_framework import util as efutil
from ..outputs import sunflowLog


def MatixToString(obj_mat, duplis):
    if duplis:
        matrix_rows = [] 
        for each_mat in obj_mat:
            matrix_rows.append([ "%+0.4f" % element for rows in each_mat for element in rows ])
    else:
        matrix_rows = [ "%+0.4f" % element for rows in obj_mat for element in rows ]
    return (matrix_rows)
    
def motion_blur_object(scene , obj_name , duplis , steps):
    sunflowLog("motion_blur_object %s" % obj_name)
    current_frame , current_subframe = (scene.frame_current, scene.frame_subframe)
    mb_start = current_frame - math.ceil(steps / 2) + 1
    frame_steps = [ mb_start + n for n in range(0, steps) ]
    ref_matrix = None
    animated = False
    
    obj = scene.objects[obj_name]
    if duplis :
        obj.dupli_list_create(scene)
        len_d = len(obj.dupli_list)
        matrices = []
        base_matrix = [ obj.dupli_list[i].matrix.copy() for i  in  range(len_d) ]
        invert_matrix = [ base_matrix[i].inverted() for i  in  range(len_d) ]
        obj.dupli_list_clear()
    else:
        matrices = [] 
        base_matrix = obj.matrix_world.copy()
        invert_matrix = base_matrix.inverted()   
    inx = 0
    for sub_frame in frame_steps:
        scene.frame_set(sub_frame, current_subframe)
        if duplis :            
            obj = scene.objects[obj_name]
            obj.dupli_list_create(scene)
            sub_matrix_l = [ obj.dupli_list[i].matrix.copy() for i  in  range(len_d) ]
            sub_matrix = [ invert_matrix[i] * sub_matrix_l[i] for i  in  range(len_d) ]
            del sub_matrix_l
            obj.dupli_list_clear()
        else:
            obj = scene.objects[obj_name]
            sub_matrix = obj.matrix_world.copy()        
            sub_matrix = invert_matrix * sub_matrix      
        matrices.append(MatixToString(sub_matrix , duplis))
        inx += 1
    scene.frame_set(current_frame, current_subframe)
    del base_matrix
    return matrices

def name_compat(name):
    if name is None:
        return 'None'
    else:
        return name.replace(' ', '_')

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

# FIXME: object visible ?? hide_render ???
#===============================================================================
# write_mesh_file
#===============================================================================
def write_mesh_file(objects_namelist, scene, Donot_Allow_Instancing=True, mblurlist=[] , steps=0):
    """
    Basic Mesh Export function. This will directly write to a temp file. 
    And return a list of temp files.
    """
    
    # Flags
    EXPORT_TRI = True
    EXPORT_EDGES = True
    EXPORT_SMOOTH_GROUPS = True
    EXPORT_NORMALS = True
    EXPORT_UV = True
    # EXPORT_BEZIER_PATCHES = True
    EXPORT_APPLY_MODIFIERS = True
    EXPORT_KEEP_VERT_ORDER = False
    EXPORT_GLOBAL_MATRIX = None
    
    return_dict = {}

    if EXPORT_GLOBAL_MATRIX is None:
        EXPORT_GLOBAL_MATRIX = mathutils.Matrix()

    def veckey3d(v):
        return round(v.x, 6), round(v.y, 6), round(v.z, 6)

    def veckey2d(v):
        return round(v[0], 6), round(v[1], 6)

    # Get all meshes
    for ob_main_name in objects_namelist:

        obs = []
        ob_main = scene.objects[ob_main_name]
        is_dupli = False
        transform_matrix = []
        
        
        if Donot_Allow_Instancing:
            # ignore dupli children
            if ob_main.parent and ob_main.parent.dupli_type in {'VERTS', 'FACES'}:
                # XXX
                sunflowLog('%s is a dupli child - ignoring' % ob_main.name)
                continue

            if ob_main.dupli_type != 'NONE':
                is_dupli = True
                if ob_main_name in mblurlist: 
                    sunflowLog("No inst , duplis %s" % ob_main_name)
                    transform_matrix = motion_blur_object(scene, ob_main_name, is_dupli , steps)
                
                # XXX
                sunflowLog('creating dupli_list on %s' % ob_main.name)
                ob_main.dupli_list_create(scene)
    
                obs = [(dob.object, dob.matrix) for dob in ob_main.dupli_list]
    
                # XXX debug print
                sunflowLog('%s has %s dupli children' % (ob_main.name, len(obs)))
            else:
                if ob_main_name in mblurlist:
                    sunflowLog("No inst , normal %s" % ob_main_name)
                    transform_matrix = motion_blur_object(scene, ob_main_name, is_dupli, steps)
                obs = [(ob_main, ob_main.matrix_world)]
        
        # Allow_Instancing
        else:  
            if ob_main_name in mblurlist:
                sunflowLog("Inst , normal %s" % ob_main_name)
                transform_matrix = motion_blur_object(scene, ob_main_name, is_dupli, steps)
            obs = [(ob_main, ob_main.matrix_world)]

        item_index = 0
        for ob, ob_mat in obs:
            item_index += 1
            Object_name = ob.name
            Object_data = {}
            
            
            #===================================================================
            # # Bezier Patches supported on sunflow implement here
            # if EXPORT_BEZIER_PATCHES and test_bezier_compat(ob):
            #    ob_mat = EXPORT_GLOBAL_MATRIX * ob_mat
            #    totverts += write_bezier(fw, ob, ob_mat)
            #    continue
            # # END Bezier
            #===================================================================
            
            try:
                # me = ob.to_mesh(scene, EXPORT_APPLY_MODIFIERS, 'PREVIEW', calc_tessface=False)
                me = ob.to_mesh(scene, EXPORT_APPLY_MODIFIERS, 'RENDER', calc_tessface=False)
            except RuntimeError:
                me = None

            if me is None:
                continue
            
            if Donot_Allow_Instancing:
                me.transform(EXPORT_GLOBAL_MATRIX * ob_mat)        
            else:
                if ob.parent and ob.parent.dupli_type in ['VERTS', 'FACES']:
                    pass
                elif ob.is_duplicator and ob.dupli_type in ['FRAMES', 'GROUP']:
                    pass 
                else:
                    me.transform(EXPORT_GLOBAL_MATRIX * ob_mat)

            if EXPORT_TRI:
                # _must_ do this first since it re-allocs arrays
                mesh_triangulate(me)

            if EXPORT_UV:
                faceuv = len(me.uv_textures) > 0
                if faceuv:
                    uv_texture = me.uv_textures.active.data[:]
                    uv_layer = me.uv_layers.active.data[:]
            else:
                faceuv = False

            me_verts = me.vertices[:]

            # Make our own list so it can be sorted to reduce context switching
            face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]
            # faces = [ f for f in me.tessfaces ]

            if EXPORT_EDGES:
                edges = me.edges
            else:
                edges = []

            if not (len(face_index_pairs) + len(edges) + len(me.vertices)):  # Make sure there is somthing to write

                # clean up
                bpy.data.meshes.remove(me)

                continue  # dont bother with this mesh.

            if EXPORT_NORMALS and face_index_pairs:
                me.calc_normals()

            if EXPORT_SMOOTH_GROUPS and face_index_pairs:
                smooth_groups, smooth_groups_tot = me.calc_smooth_groups()
                if smooth_groups_tot <= 1:
                    smooth_groups, smooth_groups_tot = (), 0
            else:
                smooth_groups, smooth_groups_tot = (), 0

            materials = me.materials[:]
            material_names = [m.name if m else None for m in materials]

            # avoid bad index errors
            if not materials:
                materials = [None]
                material_names = [name_compat(None)]
                
            Object_data['material_names'] = material_names[:]

            # Sort by Material, then images
            # so we dont over context switch in the obj file.
            if EXPORT_KEEP_VERT_ORDER:
                pass
            else:
                if faceuv:
                    if smooth_groups:
                        sort_func = lambda a: (a[0].material_index,
                                               hash(uv_texture[a[1]].image),
                                               smooth_groups[a[1]] if a[0].use_smooth else False)
                    else:
                        sort_func = lambda a: (a[0].material_index,
                                               hash(uv_texture[a[1]].image),
                                               a[0].use_smooth)
                elif len(materials) > 1:
                    if smooth_groups:
                        sort_func = lambda a: (a[0].material_index,
                                               smooth_groups[a[1]] if a[0].use_smooth else False)
                    else:
                        sort_func = lambda a: (a[0].material_index,
                                               a[0].use_smooth)
                else:
                    # no materials
                    if smooth_groups:
                        sort_func = lambda a: smooth_groups[a[1] if a[0].use_smooth else False]
                    else:
                        sort_func = lambda a: a[0].use_smooth

                face_index_pairs.sort(key=sort_func)

                del sort_func

            # Export Vertex Data
            Object_data['vertices'] = []
            for v in me_verts:
                coordinate_str = [ "%+0.4f" % coordinate for coordinate in v.co[:] ]
                Object_data['vertices'].append(coordinate_str)
            
            # Export Faces Data
            Object_data['faces'] = []
            for face , f_index in face_index_pairs:
                coordinate_str = [ "%04d" % coordinate for coordinate in face.vertices[:] ]
                Object_data['faces'].append(coordinate_str)
            

            # UV
            if faceuv:
                facevarying = [None] * len(face_index_pairs)
                for f, f_index in face_index_pairs:
                    store = []
                    for dummy_index, l_index in enumerate(f.loop_indices):
                        uv = uv_layer[l_index].uv 
                        uvkey = veckey2d(uv)
                        store.append(uvkey)
                    facevarying[f_index] = store


                # Export UV coordinates 
                Object_data['uv'] = []
                for f, f_index in face_index_pairs:                    
                    coordinate_str = [ "%+0.4f" % coordinate for pair in facevarying[f_index] for coordinate in pair ]
                    Object_data['uv'].append(coordinate_str)

                         
                 
            # NORMAL, Smooth/Non smoothed.
            if EXPORT_NORMALS:
                facenormals = []
                for f, f_index in face_index_pairs:
                    if f.use_smooth:
                        face_vertex = []
                        for v_idx in f.vertices:
                            v = me_verts[v_idx]
                            noKey = veckey3d(v.normal)                            
                            face_vertex.append(noKey)                            
                        facenormals.append(face_vertex)
                    else:
                        # Hard, 1 normal from the face.
                        noKey = veckey3d(f.normal)
                        facenormals.append([noKey, noKey, noKey])
                            
                # Export Normal vector 
                Object_data['normal'] = []
                for n_index in facenormals:                    
                    coordinate_str = [ "%+0.4f" % coordinate for pair in n_index for coordinate in pair ]
                    Object_data['normal'].append(coordinate_str)
                    
                    
                    
                            
            # MATERIAL INDEX
            if len(materials) > 1:
                # Export Normal vector 
                Object_data['matindex'] = []
                for f, f_index in face_index_pairs:
                    coordinate_str = "%02d" % f.material_index 
                    Object_data['matindex'].append(coordinate_str)
                                         
            # f_images
            if not faceuv:
                f_image = None
                
                
                
                
            # clean up
            bpy.data.meshes.remove(me)
            
            # save to temp file
            
            trans_mat = []
            if is_dupli and(Object_name in mblurlist):   
                for matrix_each in range(steps):
                    trans_mat.append(transform_matrix[matrix_each][item_index - 1])
                item_name = "%s.item.%03d" % (Object_name, item_index)
            elif is_dupli :
                trans_mat = transform_matrix[:]
                item_name = "%s.item.%03d" % (Object_name, item_index)
            else:
                trans_mat = transform_matrix[:]
                item_name = Object_name
            filename = save_object_data(item_name , Object_data)
            if filename != '':
                item = {}
                item['materials'] = Object_data['material_names']
                item['modifiers'] = []
                item['objectfile'] = filename
                item['parent'] = Object_name            
                item['is_dupli'] = is_dupli    
                item['trans_mat'] = trans_mat
                return_dict[item_name] = item.copy()
                del item
                del Object_data
                
        if ob_main.dupli_type != 'NONE':
            ob_main.dupli_list_clear()

 
    # copy all collected files.
    return return_dict


def save_object_data(Object_name="", Object_data={}):    
    
    if 'vertices' in Object_data.keys() and Object_data['vertices'] != [] :
        number_of_vertices = len(Object_data['vertices'])
    else:
        # sunflowLog("Object has no vertices")
        return ''
    
    if 'faces' in Object_data.keys() and Object_data['faces'] != [] :
        number_of_faces = len(Object_data['faces'])
    else:
        # sunflowLog("Object has no faces")
        return ''
    
    if  'normal' in Object_data.keys() and Object_data['normal'] != [] :
        if len(Object_data['normal']) != number_of_faces :
            sunflowLog("Number of normal vector and faces don't match")
            return ''
        normal_type = 'facevarying'
    else:
        # sunflowLog("Object has no normal vector")
        normal_type = 'none'
    
    if 'uv' in Object_data.keys()  and Object_data['uv'] != [] :
        if len(Object_data['uv']) != number_of_faces :
            sunflowLog("Number of uv's and faces don't match")
            return ''
        uv_type = 'facevarying'
    else:
        # sunflowLog("Object has no uv's defined")
        uv_type = 'none'
    
    if 'matindex' in Object_data.keys()  and Object_data['matindex'] != [] :
        if len(Object_data['matindex']) != number_of_faces :
            sunflowLog("Number of matindex's and faces don't match")
            return ''
        matindex_type = 'face_shaders'
    else:
        # sunflowLog("Object has no face shaders's defined")
        matindex_type = ''
        
    
#------------------------------------------------------------------------------ 
    act_obj = []
    indent = 0
    space = "        "
    indent += 1
    
    
    act_obj.append("%s %s %s" % (space * indent , "points", number_of_vertices))
    indent += 1
    for item in Object_data['vertices']:
        vertstring = '  '.join(item)
        act_obj.append("%s %s %s" % (space * indent , "", vertstring))
    indent -= 1
    
    act_obj.append("%s %s %s" % (space * indent , "triangles", number_of_faces))
    indent += 1
    for item in Object_data['faces']:
        facestring = '  '.join(item)
        act_obj.append("%s %s %s" % (space * indent , "", facestring))
    indent -= 1
    

    act_obj.append("%s %s %s" % (space * indent , "normals", normal_type))
    if normal_type == 'none':        
        pass
    else:        
        indent += 1
        for item in Object_data['normal']:
            concat = ' '.join(item)
            act_obj.append("%s %s %s" % (space * indent , "", concat))
        indent -= 1    
    

    act_obj.append("%s %s %s" % (space * indent , "uvs", uv_type))
    if uv_type == 'none':        
        pass
    else:        
        indent += 1
        for item in Object_data['uv']:
            concat = ' '.join(item)
            act_obj.append("%s %s %s" % (space * indent , "", concat))
        indent -= 1


    act_obj.append("%s %s %s" % (space * indent , "", matindex_type))
    if matindex_type == '':        
        pass
    else:        
        indent += 1
        for item in Object_data['matindex']:
            act_obj.append("%s %s %s" % (space * indent , "", item))
        indent -= 1        
    indent -= 1

    tmpfile = efutil.temp_file(Object_name + ".sc")
    outfile = open(tmpfile, 'w')
    for lines in act_obj :
        outfile.write("\n%s" % lines)
    outfile.close()
    return tmpfile
