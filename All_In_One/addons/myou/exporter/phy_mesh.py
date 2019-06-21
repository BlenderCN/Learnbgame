import bpy, bmesh, os, struct, gzip, hashlib, random
from mathutils import *
from json import loads, dumps

from array import array

def convert_phy_mesh(ob, scn, file_hash):
    orig_data = ob.data
    print("\n------------------------------")
    print("exporting:",ob.name)
    print("------------------------------")
    # Force mesh triangulation
    old_active_object = scn.objects.active
    scn.objects.active = ob
    bpy.ops.object.modifier_add(type='TRIANGULATE')
    ob.data = ob.to_mesh(scn, True, 'PREVIEW')  # This applies modifiers
    bpy.ops.object.modifier_remove(modifier=ob.modifiers[-1].name)

    vlen = len(ob.data.vertices)
    vertices = array('f', [0]) * (vlen*3)
    ob.data.vertices.foreach_get('co', vertices)

    #TODO: remove indices if ob.game.collision_bounds_type == "CONVEX_HULL"

    #It only works with triangulated meshes.
    num_indices = len(ob.data.polygons) * 3
    indices = array('I', [0]) * num_indices
    ob.data.polygons.foreach_get('vertices', indices)

    try:
        mesh_bytes = (
            struct.pack('<'+'fffxxxx'*vlen, *vertices) +
            struct.pack('<'+'H'*len(indices), *indices))
    except:

        #restoring original state
        ob.data = orig_data
        scn.objects.active = old_active_object

        return False

    fname = file_hash + '.mesh'
    fname = fname.replace(os.sep, '/')

    # writing mesh
    open(scn['game_tmp_path'] + fname, 'wb').write(mesh_bytes)

    # writing compressed mesh
    bingzip = gzip.compress(mesh_bytes)
    open(scn['game_tmp_path'] + fname+'.gz','wb').write(bingzip)

    tri_count = len(indices)/3

    #restoring original state
    ob.data = orig_data
    scn.objects.active = old_active_object

    return {
        'stride': 16,
        'elements': [],
        'tri_count': tri_count,
        'offsets': [0,0, vlen*4, len(indices)],
        'mesh_name': ob.data.name,
        'hash':file_hash,
        'all_f': 0,
    }
