GOOGOL = 1e100

import bpy, bmesh, os, struct, gzip, hashlib, random
from mathutils import *
from json import loads, dumps

from time import perf_counter
import inspect
def perf_t(last_t,p=True,message=''):
    t = perf_counter()
    linenum = inspect.stack()[1][2]
    if p:
        print(message + "{}s -> line:{}".format("%.2f" % (t-last_t), linenum))
    return t

MODE_OPS = {
    'OBJECT': lambda: None,
    'EDIT_MESH': lambda: None,
    'SCULPT': bpy.ops.sculpt.sculptmode_toggle,
    'PAINT_VERTEX':bpy.ops.paint.vertex_paint_toggle,
    'PAINT_WEIGHT':bpy.ops.paint.weight_paint_toggle,
    'PAINT_TEXTURE':bpy.ops.paint.texture_paint_toggle,
    'POSE':bpy.ops.object.posemode_toggle,
}


# For armature deformed meshes
# Assumes object is active!
def multiuser_apply_local_transform(ob):
    users = ob.data.users
    if users > 1:
        orig = ob.data
        ob.data = ob.data.copy()
        ob.data.name = orig.name
    data = ob.data
    p = ob.parent
    if p:
        mat = p.matrix_world.inverted() * ob.matrix_world
        ob.parent = None
        ob.matrix_world = mat
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if p:
        ob.parent = p
        ob.matrix_world = p.matrix_world
    if users > 1:
        for o in bpy.data.objects:
            if o.data == orig:
                o.data = data



def convert_mesh(ob, scn, file_hash, split_parts=1, sort=True, export_tangents=False):
    print("Exporting object (mesh): {} ({})".format(ob.name, ob.data.name))

    global_undo = bpy.context.user_preferences.edit.use_global_undo
    orig_mode = bpy.context.mode

    t = perf_counter()
    # TODO: very big meshes
    orig_data = ob.data
    orig_pos = ob.location.copy()
    orig_layers = ob.layers[:]
    active = scn.objects.active
    was_sel, hide, orig_ami = ob.select, ob.hide, ob.active_material_index
    scn.objects.active = ob
    ob.select, ob.hide = True, False

    ob.layers = [True]*20

    ## Make sure mesh with armature has no local transform
    ## This affects all objects with the same mesh!
    #if ob.parent and ob.parent.type=='ARMATURE' and not ob.parent_bone:
        #print (max(max(ob.matrix_world - ob.parent.matrix_world)))
        #if max(max(ob.matrix_world - ob.parent.matrix_world)) > 1.5e-7:
            #multiuser_apply_local_transform(ob)

    # Extract particle system as mesh
    ps = None
    ps_data = None
    armature = None
    has_modifiers = False
    for m in ob.modifiers:
        if (m.type=='PARTICLE_SYSTEM' and
            m.particle_system.settings.type == 'HAIR' and
            m.particle_system.settings.count == len(ob.data.vertices) and
            m.particle_system.settings.emit_from == 'VERT' and
            m.particle_system.settings.use_emit_random is False):

            ps = m.particle_system
            mat, ob.matrix_world = ob.matrix_world.copy(), Matrix()
            bpy.ops.object.modifier_convert(modifier=m.name)
            ob.matrix_world = mat
            ps_data = [v.co.copy() for v in scn.objects.active.data.vertices]
            scn.objects.unlink(scn.objects.active)
            scn.update()
            ob.data.update()
            scn.objects.active = ob
            break

        if m.show_viewport:
            has_modifiers = True
            if m.type == 'ARMATURE' and m.object and m.object == ob.parent:
                armature = m.object

    has_armature_deform = \
        armature and not ob.parent_type == 'BONE' \
            and not ob.get('apply_armature')

    if has_armature_deform:
        # THIS MODIFIES THE ORIGINAL MESH!
        parent = ob.parent
        bpy.ops.object.select_all(action='DESELECT')
        ob.select = 1
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        ob.matrix_world = parent.matrix_world.inverted() * ob.matrix_world
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        ob.matrix_parent_inverse = Matrix()
        ob.parent = parent
        scn.update()
        ob.location = orig_pos = [0,0,0]
        ob.rotation_euler = [0,0,0]
        ob.rotation_quaternion = [1,0,0,0]
        ob.scale = [1,1,1]

    is_bone_child = \
        ob.parent and ob.parent.type=='ARMATURE' and ob.parent_type == 'BONE' and ob.parent_bone

    apply_modifiers = has_modifiers and not ob.particle_systems
    can_add_lod = not ob.particle_systems
    preserve_keys = bool(ob.data.shape_keys) and bool(ob.data.shape_keys.key_blocks)

    if apply_modifiers:
        print('Applying modifiers:')
        t=perf_t(t)
        if preserve_keys:
            # To preserve keys with modifiers, we convert them in UVs
            # to take advantage of modifiers that properly handle UVs
            sizes = [0] * len(ob.data.polygons)
            ob.data.polygons.foreach_get('loop_total', sizes)
            indices = [0] * sum(sizes)
            ob.data.polygons.foreach_get('vertices', indices)
            orig_uv_len = len(ob.data.uv_layers)
            basis = ob.data.shape_keys.key_blocks[0].data
            for block in ob.data.shape_keys.key_blocks[1:]:
                bpy.ops.mesh.uv_texture_add()
                bpy.ops.mesh.uv_texture_add()
                uv1,uv2 = ob.data.uv_layers[-2:]
                data = block.data
                for i,a,b in zip(indices, uv1.data, uv2.data):
                    co = data[i].co - basis[i].co
                    a.uv = co.xy
                    b.uv = co.xz
            print('keys were stored')
            t=perf_t(t)

        mods = [0] * len(ob.modifiers)
        ob.modifiers.foreach_get('show_viewport', mods)
        for m in ob.modifiers:
            if m.type == 'ARMATURE' and has_armature_deform:
                m.show_viewport = False

        # Apply auto-smooth as a modifier
        triangulate_mod = None
        auto_smooth_mod = None
        if ob.data.use_auto_smooth:
            triangulate_mod = ob.modifiers.new('auto-smooth-tri', 'TRIANGULATE')
            triangulate_mod.quad_method = 'SHORTEST_DIAGONAL'
            auto_smooth_mod = ob.modifiers.new('auto-smooth-split', 'EDGE_SPLIT')
            auto_smooth_mod.use_edge_sharp = True
            auto_smooth_mod.split_angle = ob.data.auto_smooth_angle

        # This applies modifiers (it fails sometimes with booleans)
        ob.data = ob.to_mesh(scn, True, 'PREVIEW')

        # Remove auto_smooth_mod
        if auto_smooth_mod:
            bpy.ops.object.modifier_remove(modifier=auto_smooth_mod.name)
            bpy.ops.object.modifier_remove(modifier=triangulate_mod.name)

        ob.modifiers.foreach_set('show_viewport', mods)
        if ob.get('smooth'):
            bpy.ops.object.shade_smooth()
        t=perf_t(t)

        if preserve_keys:
            # Restore keys which were stored as UVs
            sizes = [0] * len(ob.data.polygons)
            ob.data.polygons.foreach_get('loop_total', sizes)
            indices = [0] * sum(sizes)
            ob.data.polygons.foreach_get('vertices', indices)
            bpy.ops.object.shape_key_add(from_mix=False)
            basis = ob.data.shape_keys.key_blocks[0].data
            for block in orig_data.shape_keys.key_blocks[1:]:
                bpy.ops.object.shape_key_add(from_mix=False)
                b = ob.data.shape_keys.key_blocks[-1]
                b.name = block.name
                #b.interpolation = block.interpolation
                #b.eval_time = block.eval_time
                b.slider_min = block.slider_min
                b.slider_max = block.slider_max
                b.vertex_group = block.vertex_group
                b.slider_min = block.slider_min
                rel = block.relative_key.name
                b.relative_key = ob.data.shape_keys.key_blocks[rel]
                b.value = block.value
                b.mute = block.mute
                uv1,uv2 = ob.data.uv_layers[orig_uv_len:orig_uv_len+2]
                data = b.data
                for i,a,b in zip(indices, uv1.data, uv2.data):
                    x, y = a.uv
                    bx,by,bz = basis[i].co
                    data[i].co = bx+x, by+y, bz+b.uv.y
                ob.data.uv_textures.active_index = orig_uv_len
                bpy.ops.mesh.uv_texture_remove()
                ob.data.uv_textures.active_index = orig_uv_len
                bpy.ops.mesh.uv_texture_remove()
            # remove UVs of orig data
            new_data = ob.data
            ob.data = orig_data
            while len(ob.data.uv_layers) > orig_uv_len:
                ob.data.uv_textures.active_index = orig_uv_len
                bpy.ops.mesh.uv_texture_remove()
            ob.data = new_data
            print('keys were restored')
            t=perf_t(t)
    else:
        ob.data = ob.data.copy()

    # print('Splitting non-smooth faces and converting to tris:')
    # t=perf_t(t,False)
    # Split non-smooth faces and convert to tris
    _ = [False]*max(len(ob.data.vertices), len(ob.data.edges))
    # t=perf_t(t)
    ob.data.vertices.foreach_set('hide', _)
    # t=perf_t(t)
    ob.data.vertices.foreach_set('select', _)
    # t=perf_t(t)
    ob.data.edges.foreach_set('hide', _)
    # t=perf_t(t)
    ob.data.edges.foreach_set('select', _)
    # t=perf_t(t)
    smooth = [False]*len(ob.data.polygons)
    # t=perf_t(t)
    ob.data.polygons.foreach_set('hide', smooth)
    # t=perf_t(t)
    ob.data.polygons.foreach_get('use_smooth', smooth)
    # t=perf_t(t)
    ob.data.polygons.foreach_set('select', [not x for x in smooth])
    # t=perf_t(t)
    bpy.ops.object.mode_set(mode='EDIT')
    # t=perf_t(t)
    bpy.ops.mesh.edge_split()
    # t=perf_t(t)
    bpy.ops.mesh.select_all(action='SELECT')
    # t=perf_t(t)
    # Blender uses the 'FIXED' method for quads, but
    # 'SHORTEST_DIAGONAL' works better in most cases than the default 'BEAUTY'
    bpy.ops.mesh.quads_convert_to_tris(quad_method='SHORTEST_DIAGONAL')
    # t=perf_t(t)

    # sort faces to minimize cache misses
    # (not the best way, but way better than mesh after triangulation)
    if sort:
        # t=perf_t(t,False)
        # print("sorting faces:")
        c, scn.cursor_location = list(scn.cursor_location), [100000,100000,100000]
        m, ob.matrix_world = ob.matrix_world.copy(), Matrix()
        bpy.ops.mesh.sort_elements(type='CURSOR_DISTANCE', elements={'FACE'})
        ob.matrix_world = m
        scn.cursor_location = c
        # t=perf_t(t)

    # print('Updating scene:')
    bpy.ops.object.mode_set(mode='OBJECT')
    scn.update()
    ob.data.update()
    # t=perf_t(t)

    # Save original indices, to map new vertices to original ones
    orig_indices = [0,0,0] * len(ob.data.polygons)
    ob.data.polygons.foreach_get('vertices', orig_indices)

    # print('Extracting normals:')
    # t=perf_t(t,False)
    # Extract normals (must be done before seaming)
    orig_vnormals = [0.0,0.0,0.0] * len(ob.data.vertices)
    orig_shape_vnormals = []

    if not ob.data.shape_keys:
        ob.data.vertices.foreach_get('normal', orig_vnormals)
    else:
        values = []
        modifiers = []
        for s in ob.data.shape_keys.key_blocks[1:]:
            values.append([s.value, s.slider_min, s.slider_max])
            s.value = s.slider_min = 0
            s.slider_max = 1
        for m in ob.modifiers:
            modifiers.append(m.show_viewport)
            m.show_viewport = False
        m = ob.to_mesh(scn, True, 'PREVIEW')
        m.vertices.foreach_get('normal', orig_vnormals)
        for s in ob.data.shape_keys.key_blocks[1:]:
            s.value = 1.0
            m = ob.to_mesh(scn, True, 'PREVIEW')
            vnormals = [0.0,0.0,0.0] * len(m.vertices)
            m.vertices.foreach_get('normal', vnormals)
            orig_shape_vnormals.append(vnormals)
            ## indices should be the same, uncomment this to test
            #test_indices = [0,0,0] * len(ob.data.polygons)
            #m.polygons.foreach_get('vertices', test_indices)
            #assert(test_indices == orig_indices)
            s.value = 0.0
        for s in ob.data.shape_keys.key_blocks[1:]:
            s.value, s.slider_min, s.slider_max = values.pop(0)
        for m in ob.modifiers:
            m.show_viewport = modifiers.pop(0)
    # t=perf_t(t)

    # print('Extracting tangent vectors:')
    # Tangent vectors
    # TODO: this is calculating tangents for every UV layer
    #       while there's only needed usually for one or none
    #       and the engine can only take one at the moment
    orig_face_tangents = []
    face_uv_winding = []
    verts = ob.data.vertices
    polys = ob.data.polygons
    for uv_layer in ob.data.uv_layers[-1:]:
        if not export_tangents:
            continue
        uv_data = uv_layer.data
        tangents = []
        for i in range(len(uv_layer.data)//3):
            i3 = i*3
            vi = polys[i].vertices
            v0 = verts[vi[0]].co
            v10 = verts[vi[1]].co - v0
            v20 = verts[vi[2]].co -v0
            uv0 = uv_data[i3].uv
            uv10 = uv_data[i3+1].uv - uv0
            uv20 = uv_data[i3+2].uv - uv0
            w = uv10.x * uv20.y - uv20.x * uv10.y
            w = 1 if w>=0 else -1
            v10 *= uv20.y
            v20 *= -uv10.y
            tangent = (v10 + v20) * w
            tangent.normalize()
            if tangent.length_squared == 0.0:
                tangent.x = 1
            tangents.append(tangent)
            face_uv_winding.append(w)
        orig_face_tangents.append(tangents)
    # t=perf_t(t)

    # Split faces by UV islands, material and uv winding (for tangent vectors)
    if 1:
        # TODO: add conditions for every case and for all
        # (to avoid entering edit mode if possible)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bm = bmesh.from_edit_mesh(ob.data)
        # print("Splitting faces by UV islands:")
        # t=perf_t(t,False)
        # Split faces by UV islands
        for uv_tex in ob.data.uv_textures:
            uv_tex.active = True
            bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
            bpy.ops.mesh.select_mode(type='EDGE', action='TOGGLE') # for multiple selection mode
            bpy.ops.mesh.select_mode(type='EDGE', action='ENABLE')
            bpy.ops.mesh.select_all(action='DESELECT')
            if hasattr(bm.edges, 'ensure_lookup_table'):
                bm.edges.ensure_lookup_table()
            bm.edges[0].select=1
            bpy.ops.mesh.select_similar(type='SEAM', compare='EQUAL', threshold=0.01)
            if not bm.edges[0].seam:
                bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.edge_split()
        # t=perf_t(t)

        # Split faces by material
        # print("Splitting faces by material:")
        faces = bm.faces
        if hasattr(faces, 'ensure_lookup_table'):
            faces.ensure_lookup_table()
        for i in range(len(ob.material_slots)-1):
            bpy.ops.mesh.select_all(action='DESELECT')
            ob.active_material_index = i
            # This doesn't work sometimes
            #bpy.ops.object.material_slot_select()
            for j in range(len(faces)):
                f = faces[j]
                f.select = f.material_index == i
            # Doing this instead of split() to avoid changing face order
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.edge_split()

        # t=perf_t(t)
        # print("Splitting faces by number of specified parts:("+str(split_parts)+')')
        # Split by number of parts specified
        numfaces_per_part = len(faces)//split_parts
        faces_numpart = [0] * len(faces)
        num_materials = len(ob.material_slots)
        # 0 1 2 0 1 2  <- material index for 3 materials
        # 0 0 0 1 1 1  <- split index
        # 0 1 2 3 4 5  <- numpart
        for i in range(split_parts):
            if i != 0:
                bpy.ops.mesh.select_all(action='DESELECT')
            # Select part
            if hasattr(faces, 'ensure_lookup_table'):
                faces.ensure_lookup_table()
            for f in range(numfaces_per_part * i, numfaces_per_part * (i+1)):
                face = faces[f]
                face.select = 1
                faces_numpart[f] = num_materials * i + face.material_index
            # Doing this instead of split() to avoid changing face order
            if i != 0:
                bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.edge_split()

        # t=perf_t(t)
        # print("Splitting faces by uv winding (for tangent vectors):")
        # Split faces by uv winding (for tangent vectors)
        if face_uv_winding:
            for i in range(len(faces)):
                faces[i].select = face_uv_winding[i] >= 0
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.edge_split()
        bpy.ops.object.mode_set(mode='OBJECT')
        ob.data.update()
    else:
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        ob.modifiers[-1].split_angle = 0
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=ob.modifiers[-1].name)

    # t=perf_t(t)

    # print('Getting average polygon area:')
    areas = [0] * len(ob.data.polygons)
    ob.data.polygons.foreach_get('area', areas)
    poly_len = len(ob.data.polygons)
    if poly_len:
        avg_poly_area = sum(areas)/poly_len
        # print('avg_poly_area:', avg_poly_area)
    else:
        avg_poly_area = GOOGOL
        print("WARNING: This mesh has no polygons. The avg_poly_area of this object will be estimated as 1 Googol (1e100)")



    # Make a map of vertices before and after seaming
    # TODO: use it in transfer_normals(), uv and tangents
    indices = [0,0,0] * len(ob.data.polygons)
    ob.data.polygons.foreach_get('vertices', indices)
    orig_vmap = [0] * len(ob.data.vertices)
    for i,v in enumerate(indices):
        orig_vmap[v] = orig_indices[i]

    # Extract final coordinates and indices
    basis = ob.data.vertices
    shapes = []
    if ob.data.shape_keys:
        basis = ob.data.shape_keys.key_blocks[0].data
        for kb in ob.data.shape_keys.key_blocks[1:]:
            co = [0.0,0.0,0.0] * len(kb.data)
            kb.data.foreach_get('co', co)
            shapes.append(co)
    vcoords = [0.0,0.0,0.0] * len(ob.data.vertices)
    basis.foreach_get('co', vcoords)
    min_v = [float('inf')]*3
    max_v = [float('-inf')]*3
    for i in range(0,len(vcoords),3):
        min_v[0] = min(min_v[0], vcoords[i])
        min_v[1] = min(min_v[1], vcoords[i+1])
        min_v[2] = min(min_v[2], vcoords[i+2])
        max_v[0] = max(max_v[0], vcoords[i])
        max_v[1] = max(max_v[1], vcoords[i+1])
        max_v[2] = max(max_v[2], vcoords[i+2])
    #t=perf_t(t)

    # Get normals from pre-seaming
    def transfer_normals(orig_vnormals):
        vnormals = [0.0] * len(vcoords)
        for i,v in enumerate(indices):
            v*=3
            if vnormals[v] == 0.0:
                i = orig_indices[i]*3
                vnormals[v] = orig_vnormals[i]
                vnormals[v+1] = orig_vnormals[i+1]
                vnormals[v+2] = orig_vnormals[i+2]
        return vnormals

    vnormals = transfer_normals(orig_vnormals)
    #t=perf_t(t)

    shape_vnormals = []
    for osn in orig_shape_vnormals:
        shape_vnormals.append(transfer_normals(osn))

    # TODO NOTE this is wrong when there are several UV
    # because it has to be done with the seaming of only one UV
    tangent_layers = []
    for orig in orig_face_tangents:
        tangents = [Vector() for v in ob.data.vertices]
        winding = [0] * len(ob.data.vertices)
        for i in range(len(ob.data.polygons)):
            for v in ob.data.polygons[i].vertices:
                tangents[v] += orig[i]
                winding[v] = face_uv_winding[i]
        for i in range(len(ob.data.vertices)):
            tangents[i].normalize()
        tangent_layers.append((tangents,winding))


    uvs = []
    uv_names = []
    for uv in ob.data.uv_layers:
        coords = [0,0] * len(uv.data)
        uv.data.foreach_get('uv', coords)
        # Transform from 3 coordinates per face to
        # one coordinate per vertex
        uvs_real = [None,None]*len(ob.data.vertices)
        for i,v in enumerate(indices):
            i*=2
            v*=2
            if uvs_real[v] is None:
                uvs_real[v] = coords[i]
                uvs_real[v+1] = coords[i+1]
        uvs.append(uvs_real)
        uv_names.append(uv.name)

    colors = []
    color_names = []
    for color in ob.data.vertex_colors:
        col_len = 4
        if color.data:
            col_len = len(color.data[0].color)
        coords = ([0] * col_len) * len(color.data)
        color.data.foreach_get('color', coords)
        # Transform from 3 coordinates per face to
        # one coordinate per vertex
        colors_real = [None,None,None]*len(ob.data.vertices)
        for i,v in enumerate(indices):
            i*=col_len
            v*=3
            if colors_real[v] is None:
                colors_real[v] = coords[i]
                colors_real[v+1] = coords[i+1]
                colors_real[v+2] = coords[i+2]
        colors.append(colors_real)
        color_names.append(color.name)

    #t=perf_t(t)

    # Armature deform weights and indices,
    # Max 4 per vertex, normalized
    weights = []
    bindices = []
    bindices_map = {}
    numgroups = 4
    if has_armature_deform:
        if ob.get('weights6'):
            numgroups = 6
        b_names = ob.parent.data['ordered_deform_names']
        # dict for getting deform bone index from name
        b_ids_from_name = dict(zip(b_names, range(len(b_names))))
        group_is_in_armature = [g.name in b_names for g in ob.vertex_groups]
        for v in ob.data.vertices:
            w = []
            bi = []
            groups = [g for g in v.groups
                if group_is_in_armature[g.group] and g.weight > 0.001]
            # Sort by weight to get the 4 most influential bones
            groups.sort(key=lambda x: x.weight, reverse=True)
            groups = groups[:numgroups]
            tot = sum(g.weight for g in groups) or 1
            for g in groups:
                w.append(g.weight/tot) # normalization
                bidx = b_ids_from_name[ob.vertex_groups[g.group].name]
                # remap indices (for having fewer uniforms in submeshes)
                # TODO: actually use submeshes instead of manual splits?
                if bidx not in bindices_map:
                    bindices_map[bidx] = len(bindices_map)
                bi.append(bindices_map[bidx])
            weights.append((w+[0,0,0,0,0,0])[:numgroups])
            bindices.append((bi+[0,0,0,0,0,0])[:numgroups])
    #t=perf_t(t)

    # Hair particles

    # THIS DOESN'T WORK WELL BECAUSE RECONNECTING HAIR IS TOTALLY BUGGY
    # SO JUST ADD HAIR AS A VERY FINAL STEP. We'll assume they're in order
    # Note 2: COORDINATES DON'T MAKE ANY SENSE, using modifier_convert() instead.
    #particles = ob.particle_systems.active.particles
    #par_inds = list(range(len(particles)))
    #print ([p.hair_keys[0].co for p in particles])
    #pskeys = bpy.pskeys = [min(par_inds,
         #key=lambda i: (particles[i].hair_keys[0].co-v.co).length_squared)
         #for v in ob.data.vertices]
    #print(pskeys)

    particles = []
    if ps:
        step = ps.settings.hair_step
        hair_tips = [0.0, 0.0, 0.0] * len(ob.data.vertices)
        for i in range(len(ob.data.vertices)):
            i3 = i*3
            orig_i = orig_vmap[i]
            # TODO: doesn't work with flat faces
            co = ps_data[(orig_i*step)+(step-1)]
            hair_tips[i3] = co.x
            hair_tips[i3+1] = co.y
            hair_tips[i3+2] = co.z
        particles.append(hair_tips)


    # Separate indices by material
    # And reorder vertices with v_map
    num_submeshes = num_materials * split_parts
    sep_indices = [[] for m in range(num_submeshes)] or [[]]
    v_map = {}
    vcount = 0
    icount = 0
    prev_vcount = 0
    v_offsets = [0] # later multiplied by stride
    i_offsets = [0]
    for p in ob.data.polygons:
        p.select = 0
    for i,inds in enumerate(sep_indices):
        for p in ob.data.polygons:
            if faces_numpart[p.index] == i:
                for v in p.vertices:
                    mapped = v_map.get(v, -1)
                    if mapped == -1:
                        mapped = v_map[v] = vcount
                        vcount += 1
                    inds.append(mapped - prev_vcount)
                    #if mapped - prev_vcount < 0:
                        #p.select = 1
                        # This shouldn't happen (but does when is not correctly split by material)
        prev_vcount = vcount
        icount += len(inds)
        v_offsets.append(vcount)
        i_offsets.append(icount)
    #t=perf_t(t)

    materials = list(range(num_materials)) * split_parts
    #print(len(materials), num_submeshes)
    #assert(len(materials) == num_submeshes)


    # Delete empty submeshes
    for i,inds in reversed(list(enumerate(sep_indices))):
        if not inds:
            del sep_indices[i]
            if materials:
                del materials[i]
            del v_offsets[i]
            del i_offsets[i]

    # Construct the final array interleaving all vertex data
    # All floats should be 32 bit aligned
    vformat = 'fffbbbx'
    compress_mask = '1110'
    byte_shapes = orig_data['byte_shapes'] = orig_data.get('byte_shapes', False)
    if byte_shapes:
        vformat += 'bbbxbbbx' * len(shapes)
        compress_mask += '00' * len(shapes)
    else:
        vformat += 'fffbbbx' * len(shapes)
        compress_mask += '1110' * len(shapes)
    vformat += 'bbbb' * len(tangent_layers)
    compress_mask += '0' * len(tangent_layers)
    vformat += 'fff' * len(particles)
    compress_mask += '111' * len(particles)
    uv_short = orig_data['uv_short'] = orig_data.get('uv_short', False)
    if uv_short:
        vformat += 'HH' * len(uvs)
        compress_mask += '0' * len(uvs)
    else:
        vformat += 'ff' * len(uvs)
        compress_mask += '11' * len(uvs)
    vformat += 'BBBx' * len(colors)
    compress_mask += '0' * len(colors)
    if weights:
        if numgroups == 6:
            vformat += 'ffffffBBBBBBxx'
            compress_mask += '00000000'
        else:
            vformat += 'ffffBBBB'
            compress_mask += '00000'
        # Note: the first weight can be removed,
        # calculated implicitely and the rest
        # compressed.

    # Note: This is the stride in the python list;
    #       Not the exported stride which is vertex size in bytes.
    #       (see stride_bytes usage below)
    stride = len(vformat) - vformat.count('x')

    # If we need to store all numbers as floats for debugging
    # or for compatibility (IE11?)
    all_floats = bool(ob.get('all_f'))
    if all_floats:
        vformat = 'f' * stride
        compress_mask = '1' * stride


    vertices = [0.0] * stride
    # Uncomment this line to debug vertex boundaries
    #vertices.append(7777777);stride +=1;vformat+='f';compress_mask+='0'
    vertices *= len(v_map)

    # vertex offsets are in float (4-byte) units
    stride_bytes = struct.calcsize('<'+vformat)
    v_offsets = [n*(stride_bytes//4) for n in v_offsets]
    #t=perf_t(t)

    # Find out shape multiplier
    shape_multiplier = 1
    if byte_shapes and shapes:
        shape_max = 0
        for shape in shapes:
            for vco, sco in zip(vcoords, shape):
                shape_max = max(shape_max, abs(sco-vco))
        shape_multiplier = 127/shape_max
    uv_multiplier = 1
    if uv_short:
        uv_multiplier = 65535

    for i in range(len(ob.data.vertices)):
        if not i in v_map: continue
        i2 = i * 2
        i3 = i * 3
        j = v_map[i] * stride
        x = vertices[j] = vcoords[i3]
        y = vertices[j+1] = vcoords[i3+1]
        z = vertices[j+2] = vcoords[i3+2]
        # Byte normals (-127 to 127)
        vertices[j+3] = int(round(vnormals[i3]*127))
        vertices[j+4] = int(round(vnormals[i3+1]*127))
        vertices[j+5] = int(round(vnormals[i3+2]*127))
        j += 6

        if byte_shapes:
            for shape, normals in zip(shapes, shape_vnormals):
                vertices[j] = int(round((shape[i3] - x)*shape_multiplier))
                vertices[j+1] = int(round((shape[i3+1] - y)*shape_multiplier))
                vertices[j+2] = int(round((shape[i3+2] - z)*shape_multiplier))
                vertices[j+3] = int(round(normals[i3]*127))
                vertices[j+4] = int(round(normals[i3+1]*127))
                vertices[j+5] = int(round(normals[i3+2]*127))
                j += 6
        else:
            for shape, normals in zip(shapes, shape_vnormals):
                vertices[j] = shape[i3] - x
                vertices[j+1] = shape[i3+1] - y
                vertices[j+2] = shape[i3+2] - z
                vertices[j+3] = int(round(normals[i3]*127))
                vertices[j+4] = int(round(normals[i3+1]*127))
                vertices[j+5] = int(round(normals[i3+2]*127))
                j += 6

        for tangent_layer, windings in tangent_layers:
            ta = tangent_layer[i]
            vertices[j] = int(round(ta.x*127))
            vertices[j+1] = int(round(ta.y*127))
            vertices[j+2] = int(round(ta.z*127))
            vertices[j+3] = windings[i]
            j += 4

        for p in particles:
            vertices[j] = p[i3]
            vertices[j+1] = p[i3+1]
            vertices[j+2] = p[i3+2]
            j += 3

        if uv_short:
            for uv in uvs:
                vertices[j] = int(round((uv[i2]*65535)%65536))
                vertices[j+1] = int(round((uv[i2+1]*65535)%65536))
                j += 2
        else:
            for uv in uvs:
                vertices[j] = uv[i2]
                vertices[j+1] = uv[i2+1]
                j += 2

        for color in colors:
            vertices[j] = int(round(color[i3]*255))
            vertices[j+1] = int(round(color[i3+1]*255))
            vertices[j+2] = int(round(color[i3+2]*255))
            j += 3

        if weights:
            if numgroups == 6:
                w = weights[i]
                bi = bindices[i]
                vertices[j] = w[0]
                vertices[j+1] = w[1]
                vertices[j+2] = w[2]
                vertices[j+3] = w[3]
                vertices[j+4] = w[4]
                vertices[j+5] = w[5]
                vertices[j+6] = bi[0]
                vertices[j+7] = bi[1]
                vertices[j+8] = bi[2]
                vertices[j+9] = bi[3]
                vertices[j+10] = bi[4]
                vertices[j+11] = bi[5]
                j += 12
            else:
                w = weights[i]
                bi = bindices[i]
                vertices[j] = w[0]
                vertices[j+1] = w[1]
                vertices[j+2] = w[2]
                vertices[j+3] = w[3]
                vertices[j+4] = bi[0]
                vertices[j+5] = bi[1]
                vertices[j+6] = bi[2]
                vertices[j+7] = bi[3]
                j += 8

    #t=perf_t(t)

    indices = sum(sep_indices, [])
    binv = bytearray(stride_bytes*len(v_map))
    bini = bytearray(len(indices)*2)
    #t=perf_t(t)

    try:
        struct.pack_into('<'+vformat*len(v_map), binv, 0, *vertices)
        struct.pack_into('<'+'H'*len(indices), bini, 0, *indices)
    except:
        ob.hide = hide
        ob.data = orig_data
        ob.select = was_sel
        ob.location = orig_pos
        ob.layers = orig_layers
        ob.active_material_index = orig_ami
        scn.objects.active = active
        MODE_OPS[orig_mode]()
        bpy.context.user_preferences.edit.use_global_undo = global_undo
        print('Reexporting mesh in', split_parts + 1, 'parts.')
        return False
    #t=perf_t(t)

    compress_bits = orig_data['compress_bits'] = min(orig_data.get('compress_bits', 0), 31)
    if compress_bits: #lossy compression
        fmask = list(struct.unpack('BBBB',struct.pack('<I',(2**compress_bits-1)^0xffffffff)))
        compress_mask = [fmask if n=='1' else [255,255,255,255]
                                  for n in compress_mask]
        compress_mask = struct.pack('<'+'BBBB'*len(compress_mask), *sum(compress_mask,[]))
        compress_mask *= len(v_map)
        binv = bytearray([a&b for a,b in zip(binv, compress_mask)])
    #t=perf_t(t)

    bindata = binv+bini
    mesh_file = scn['game_tmp_path'] + file_hash + '.mesh'

    # writing mesh
    open(mesh_file,'wb').write(bindata)

    # writing compressed mesh
    bingzip = gzip.compress(bindata)
    open(mesh_file+'.gz','wb').write(bingzip)

    # TODO: delete old file?
    #t=perf_t(t)

    elements = [['normal']]

    if ob.data.shape_keys:
        for shape in ob.data.shape_keys.key_blocks[1:]:
            elements.append(['shape_b' if byte_shapes else 'shape', shape.name])
    for t in tangent_layers:
        elements.append(['tangent'])
    if particles:
        elements.append(['particles', len(particles)])
    for uv_name in uv_names:
        elements.append(['uv_s' if uv_short else 'uv', uv_name])
    for color_name in color_names:
        elements.append(['color', color_name])
    if weights:
        if numgroups == 6:
            elements.append(['weights6'])
        else:
            elements.append(['weights'])

    tri_count = len(indices)/3

    bone_index_maps = [flip_map_to_list(bindices_map)] * len(v_offsets)
    print('Bones used:', len(bone_index_maps[0]))

    ob.hide = hide
    ob.data = orig_data
    ob.select = was_sel
    ob.location = orig_pos
    ob.layers = orig_layers
    ob.active_material_index = orig_ami
    scn.objects.active = active

    export_data = {
        'stride': stride_bytes,
        'elements': elements,
        'offsets': sum(map(list, zip(v_offsets, i_offsets)), []),
        'mesh_name': ob.data.name,
        'hash': file_hash,
        'all_f': all_floats,
        'shape_multiplier': 1/shape_multiplier,
        'uv_multiplier': 1/uv_multiplier,
        'avg_poly_area': avg_poly_area,
        'tri_count': tri_count,
        'center': [(min_v[0]+max_v[0])*0.5, (min_v[1]+max_v[1])*0.5, (min_v[2]+max_v[2])*0.5],
        'bbox': [min_v[0], min_v[1], min_v[2], max_v[0], max_v[1], max_v[2]],
        # properties below can be deleted before export
        'material_indices': materials,
        'can_add_lod': can_add_lod,
        'bone_index_maps': bone_index_maps,
    }

    MODE_OPS[orig_mode]()
    bpy.context.user_preferences.edit.use_global_undo = global_undo
    return export_data

def flip_map_to_list(map):
    if not map:
        return []
    r = [0] * (max(map.values())+1)
    for k,v in map.items():
        r[v] = k
    return r
