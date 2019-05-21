from . import iffFile
from . import mshFile

import bpy
import math

def save(operator, context, filepath, gen_box, gen_sphr, gen_clyn, selected_only):
    print('\nexporting msh %r' % filepath)
    
    msh = mshFile.mshFile()
    
    scene = context.scene
    
    if selected_only:
        objects = context.selected_objects
    else:
        objects = scene.objects
    
    #gather information about extrema
    extreme_g_x = None
    extreme_g_y = None
    extreme_g_z = None
            
    extreme_l_x = None
    extreme_l_y = None
    extreme_l_z = None
    
    for ob_main in objects:
        # ignore dupli children
        if ob_main.parent and ob_main.parent.dupli_type != 'NONE':
            # XXX
            print(ob_main.name, 'is a dupli child - ignoring')
            continue

        obs = []
        if ob_main.dupli_type != 'NONE':
            # XXX
            print('creating dupli_list on', ob_main.name)
            ob_main.dupli_list_create(scene)

            obs = [(dob.object, dob.matrix) for dob in ob_main.dupli_list]

            # XXX debug print
            print(ob_main.name, 'has', len(obs), 'dupli children')
        else:
            obs = [(ob_main, ob_main.matrix_world)]
            
        for ob, ob_mat in obs:
            if ob.type != 'MESH':
                continue
            
            me = ob.to_mesh(scene, True, 'PREVIEW')
            
            me_verts = me.vertices[:]
            group = [[], [], None]
            msh.groups.append(group)
            
            face_index_pairs = [(face, index) for index, face in enumerate(me.faces)]
            
            if not (len(face_index_pairs) + len(me.vertices)):  # Make sure there is somthing to write

                # clean up
                bpy.data.meshes.remove(me)

                continue  # dont bother with this mesh.
            
            #face_index_pairs.sort(key=lambda a: a[0].use_smooth)
            
            for f, f_indx in face_index_pairs:
                f_v_orig = [(vi, me_verts[v_idx]) for vi, v_idx in enumerate(f.vertices)]

                if len(f_v_orig) == 3:
                    f_v_iter = (f_v_orig[2], f_v_orig[1], f_v_orig[0]), 
                else:
                    f_v_iter = (f_v_orig[2], f_v_orig[1], f_v_orig[0]), (f_v_orig[3], f_v_orig[2], f_v_orig[0])
            
                for f_v in f_v_iter:
                    face = []
                    for vi, v in f_v:
                        face.append(v.index)
                    group[1].append(face)
            
            for vert in me_verts:
                if extreme_g_x == None or vert.co[0] > extreme_g_x:
                    extreme_g_x = vert.co[0]
                if extreme_l_x == None or vert.co[0] < extreme_l_x:
                    extreme_l_x = vert.co[0]
                if extreme_g_y == None or vert.co[1] > extreme_g_y:
                    extreme_g_y = vert.co[1]
                if extreme_l_y == None or vert.co[1] < extreme_l_y:
                    extreme_l_y = vert.co[1]
                if extreme_g_z == None or vert.co[2] > extreme_g_z:
                    extreme_g_z = vert.co[2]
                if extreme_l_z == None or vert.co[2] < extreme_l_z:
                    extreme_l_z = vert.co[2]
            
                msh_vert = mshFile.vertex()
                msh_vert.vertex = mshFile.vector3D.Vector3D(vert.co[0], vert.co[2], vert.co[1])
                msh_vert.normal = mshFile.vector3D.Vector3D(vert.normal[0], vert.normal[2], vert.normal[1])
                #msh_vert.color = b'\x00\x00\x00\x00'
                msh_vert.texs = [(0.0, 0.0)]
                group[0].append(msh_vert)
                
           
    #get ready for box/sphr/clyn generation
    if gen_box or gen_sphr or gen_clyn:
        diff_x = math.fabs(extreme_g_x) + math.fabs(extreme_l_x)
        diff_y = math.fabs(extreme_g_y) + math.fabs(extreme_l_y)
        diff_z = math.fabs(extreme_g_z) + math.fabs(extreme_l_z)
        
        center_x = extreme_l_x + (diff_x/2)
        center_y = extreme_l_y + (diff_y/2)
        center_z = extreme_l_z + (diff_z/2)
    
    #we either want the greatest or the least. I'm not sure which.
    if gen_box: #generate the box data
        msh.box = (diff_x, diff_z, diff_y, extreme_l_x, extreme_l_z, extreme_l_y)
        print(msh.box)
    if gen_sphr: #generate the sphr data
        msh.sphr = (center_x, center_z, center_y, max(diff_x, diff_y, diff_z)/2)
        print(msh.sphr)
        
    if gen_clyn: #generate the cyln data
        pass#Not implemented for now.
    
    tree = msh.build_tree()
    #tree.console_print()
    with open(filepath, 'wb') as f:
        f.write(tree.output())