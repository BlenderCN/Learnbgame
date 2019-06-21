#############################################
# THPS4 SCENE (.scn/.mdl/skin) IMPORT
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
import os, sys
from bpy.props import *
from . constants import *
from . helpers import *

# METHODS
#############################################
def import_scn_th4(filename, directory, context, operator):
    p = Printer()
    p.on = True
    input_file = os.path.join(directory, filename)
    with open(input_file, "rb") as inp:
        r = Reader(inp.read())

    _mat_version = r.u32()
    _mesh_version = r.u32()
    _vert_version = r.u32()

    num_materials = p("num materials: {}", r.u32())
    read_materials_th4(r, p, num_materials, directory, operator)
    num_sectors = p("num sectors: {}", r.i32())
    if operator.is_desa:
        read_sectors_th4(True, r, p, num_sectors, context, operator)
    else:
        read_sectors_th4(False, r, p, num_sectors, context, operator)

#----------------------------------------------------------------------------------
def read_materials_th4(reader, printer, num_materials, directory, operator, output_file=None, texture_map=None, texture_prefix=None):
    import os
    r = reader
    p = printer

    for i in range(num_materials):
        p("material {}", i)
        mat_checksum = p("  material checksum: {}", to_hex_string(r.u32()))
        blender_mat = bpy.data.materials.new(str(mat_checksum))
        ps = blender_mat.thug_material_props

        num_passes = p("  material passes: {}", r.u32())
        ps.alpha_cutoff = p("  alpha cutoff: {}", r.u32() % 256)
        ps.sorted = p("  sorted: {}", r.bool())
        ps.draw_order = p("  draw order: {}", r.f32())
        ps.single_sided = p("  single_sided: {}", r.bool())
        ps.no_backface_culling = ( ps.single_sided == False )
        ps.z_bias = 0

        grassify = p("  grassify: {}", r.bool())
        if grassify:
            p("  grass height: {}", r.f32())
            p("  grass layers: {}", r.i32())

        blender_mat.use_transparency = True
        blender_mat.diffuse_color = (1, 1, 1)
        blender_mat.diffuse_intensity = 1
        blender_mat.specular_intensity = 0
        blender_mat.alpha = 0

        for j in range(num_passes):
            blender_tex = bpy.data.textures.new("{}/{}".format(mat_checksum, j), "IMAGE")
            tex_slot = blender_mat.texture_slots.add()
            tex_slot.texture = blender_tex
            pps = blender_tex.thug_material_pass_props
            p("  pass #{}", j)
            tex_checksum = p("    pass texture checksum: {}", r.u32())
            actual_tex_checksum = to_hex_string(tex_checksum)
            image_name = str(actual_tex_checksum) #+ ".png"
            blender_tex.image = bpy.data.images.get(image_name)
            full_path = os.path.join(directory, image_name)
            full_path2 = os.path.join(directory, str("tex\\{:08x}.tga".format(tex_checksum)))
            full_path3 = os.path.join(directory, str("tex\\{:08x}.png".format(tex_checksum)))
            if not blender_tex.image:
                if os.path.exists(full_path):
                    blender_tex.image = bpy.data.images.load(full_path)
                elif os.path.exists(full_path2):
                    blender_tex.image = bpy.data.images.load(full_path2)
                elif os.path.exists(full_path3):
                    blender_tex.image = bpy.data.images.load(full_path3)
                #else:
                #    blender_tex.image = bpy.data.images.new(image_name)
            tex_slot.uv_layer = str(j)

            pass_flags = p("    pass material flags: {}", r.u32())
            p("    pass has color: {}", r.bool())
            pps.color = p("    pass color: {}", r.read("3f"))
            pps.blend_mode = p("    blend mode: {}", BLEND_MODES[r.u32()])
            pps.blend_fixed_alpha = r.u32() & 0xFF

            if j == 0:
                tex_slot.use_map_alpha = True

            tex_slot.blend_type = {
                "vBLEND_MODE_ADD": "ADD",
                "vBLEND_MODE_ADD_FIXED": "ADD",
                "vBLEND_MODE_SUBTRACT": "SUBTRACT",
                "vBLEND_MODE_SUB_FIXED": "SUBTRACT",
                "vBLEND_MODE_BRIGHTEN": "LIGHTEN",
                "vBLEND_MODE_BRIGHTEN_FIXED": "LIGHTEN",
            }.get(pps.blend_mode, "MIX")

            pps.u_addressing = "Repeat" if p("    pass u addressing: {}", r.u32()) == 0 else "Clamp"
            pps.v_addressing = "Repeat" if p("    pass v addressing: {}", r.u32()) == 0 else "Clamp"

            if blender_tex.image:
                blender_tex.image.use_clamp_x = pps.u_addressing == "Clamp"
                blender_tex.image.use_clamp_y = pps.v_addressing == "Clamp"

            pps.filtering_mode = r.u32()
            p("    pass filtering mode: {}", pps.filtering_mode)
            pps.test_passes = pass_flags
            
            # THPS4 uses diffuse, specular, and ambient RGB which don't entirely
            # translate here, so let's skip them for now
            r.read("36x")

            if pass_flags & MATFLAG_TEXTURED:
                pps.pf_textured = True
            if pass_flags & MATFLAG_TRANSPARENT:
                pps.pf_transparent = True
            else:
                pps.pf_transparent = False
            if pass_flags & MATFLAG_ENVIRONMENT:
                pps.pf_environment = True
            if pass_flags & MATFLAG_DECAL:
                pps.pf_decal = True
            if pass_flags & MATFLAG_SMOOTH:
                pps.pf_smooth = True
                
            if pass_flags & MATFLAG_PASS_IGNORE_VERTEX_ALPHA:
                pps.ignore_vertex_alpha = True

            if pass_flags & MATFLAG_UV_WIBBLE:
                p("    pass has uv wibble!", None)
                pps.has_uv_wibbles = True
                uvs = pps.uv_wibbles
                uvs.uv_velocity = r.read("2f")
                uvs.uv_frequency = r.read("2f")
                uvs.uv_amplitude = r.read("2f")
                uvs.uv_phase = r.read("2f")

            if j == 0 and pass_flags & MATFLAG_VC_WIBBLE:
                p("    pass has vc wibble!", None)
                for k in range(r.u32()):
                    num_keys = r.u32()
                    r.i32()
                    r.read(str(num_keys * 2) + "i") # sVCWibbleKeyframe

            if pass_flags & MATFLAG_PASS_TEXTURE_ANIMATES:
                p("    pass texture animates!", None)
                pps.has_animated_texture = True
                at = pps.animated_texture
                num_keyframes = r.i32()
                at.period = r.i32()
                at.iterations = r.i32()
                at.phase = r.i32()

                for k in range(num_keyframes):
                    atkf = at.keyframes.add()
                    atkf.time = r.u32()
                    atkf.image = str(r.u32())

            if tex_checksum:  # mipmap info
                p("    mmag: {}", r.u32())
                p("    mmin: {}", r.u32())
                p("    k: {}", r.f32())
                p("    l: {}", r.f32())
            else:
                r.read("4I")


#----------------------------------------------------------------------------------
def read_sectors_th4(is_desa, reader, printer, num_sectors, context, operator=None, output_file=None):
    r = reader
    p = printer
    outf = output_file

    vert_position_index_offset = 1
    vert_texcoord_index_offset = 1

    for i in range(num_sectors):
        write_sector_to_obj = False # True

        bm = bmesh.new()

        p("sector {}", i)
        sec_checksum = p("  sector checksum: {}", to_hex_string(r.u32()))

        blender_mesh = bpy.data.meshes.new("scn_mesh_" + str(sec_checksum))
        blender_object = bpy.data.objects.new("scn_" + str(sec_checksum), blender_mesh)
        blender_object.thug_export_collision = False
        to_group(blender_object, "SceneMesh")
        context.scene.objects.link(blender_object)

        bone_index = p("  bone index: {}", r.i32())
        sec_flags = p("  sector flags: {}", r.u32())
        num_meshes = p("  number of meshes: {}", r.u32())
        if num_meshes > 100000:
            raise Exception("Invalid data: more than 100k meshes.")
        p("  bbox: {}", (r.read("3f"), r.read("3f")))
        p("  bounding sphere: {}", r.read("4f"))

        if ((bone_index != -1) or
                (sec_flags & SECFLAGS_HAS_VERTEX_WEIGHTS) or
                not (sec_flags & SECFLAGS_HAS_TEXCOORDS) or
                (sec_flags & SECFLAGS_BILLBOARD_PRESENT)):
            write_sector_to_obj = False

        if sec_flags & SECFLAGS_BILLBOARD_PRESENT:
            blender_object.data.thug_billboard_props.is_billboard = True
            to_group(blender_object, "Billboards")
            billboard_type = p("  billboard type: {}", r.u32())
            if billboard_type == 1:
                blender_object.data.thug_billboard_props.type = 'SCREEN'
            elif billboard_type == 2:
                blender_object.data.thug_billboard_props.type = 'AXIS'
            else:
                raise Exception("Unknown billboard type: {}".format(billboard_type))
            blender_object.data.thug_billboard_props.pivot_origin = from_thug_coords( p("  billboard origin: {}", r.read("3f")) )
            blender_object.data.thug_billboard_props.pivot_pos = from_thug_coords( p("  billboard pivot pos: {}", r.read("3f")) )
            blender_object.data.thug_billboard_props.pivot_axis = from_thug_coords( p("  billboard pivot axis: {}", r.read("3f")) )
            blender_object.data.thug_billboard_props.custom_pos = True

        if is_desa:
            r.u64() # No idea what this is used for!
            
        if sec_flags & SECFLAGS_HAS_VERTEX_NORMALS:
            p("  sector has vertex normals!", None)

        if sec_flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
            p("  sector has vertex weights!", None)

        if sec_flags & SECFLAGS_HAS_TEXCOORDS:
            p("  sector has tc sets!", None)

        if sec_flags & SECFLAGS_HAS_VERTEX_COLORS:
            p("  sector has vertex colors!", None)
            color_layer = bm.loops.layers.color.new("color")
            alpha_layer = bm.loops.layers.color.new("alpha")

        if sec_flags & SECFLAGS_HAS_VERTEX_COLOR_WIBBLES:
            p("  sector has vertex color wibbles!", None)

        vertex_normals = {}
        vertex_weights = {}
        vertex_weight0 = {}
        vertex_bones = {}
        
        mesh_vert_positions = []
        mesh_vert_normals = []
        mesh_vert_colors = []
        mesh_vert_texcoords = []
        
        this_mesh_verts = []
        per_vert_data = {}
        
        amount_of_verts = p("  vertices: {}", r.u32())
        p("  vertex data stride: {}", r.u32())

        # Read vertex data
        for l in range(amount_of_verts):

            vert_pos = r.read("3f")
            vert_pos = from_thug_coords(vert_pos)

            new_vert = bm.verts.new(vert_pos)
            per_vert_data[new_vert] = {}
            this_mesh_verts.append(new_vert)
            
        if sec_flags & SECFLAGS_HAS_VERTEX_NORMALS:
            if sec_flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
                # Apparently, normals are supposed to be packed in weighted mesh
                # but for some reason, this never seems to be the case!
                for l in range(amount_of_verts):
                    new_vert = this_mesh_verts[l]
                    vertex_normal = r.read("3f")
                    if operator.import_custom_normals:
                        vertex_normals[new_vert] = from_thug_coords(vertex_normal)
            else:
                for l in range(amount_of_verts):
                    new_vert = this_mesh_verts[l]
                    vertex_normal = r.read("3f")
                    if operator.import_custom_normals:
                        vertex_normals[new_vert] = from_thug_coords(vertex_normal)
                
        
        if sec_flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                vert_weights = r.read("4f")
                #vert_weights = ( r.u32(), r.u32(), r.u32(), r.u32() )
                vertex_weight0[new_vert] = vert_weights

            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                bone_indices = r.read("4H")
                vertex_bones[new_vert] = bone_indices
                
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                vertex_weights[new_vert] = (vertex_weight0[new_vert], vertex_bones[new_vert])
                
        
        if sec_flags & SECFLAGS_HAS_TEXCOORDS:
            texcoords_to_read = r.u32()
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                for m in range(texcoords_to_read):
                    texcoords = r.read("2f")
                    per_vert_data[new_vert].setdefault("uvs", []).append(texcoords)
                    if write_sector_to_obj and m == 0:
                        outf.write("vt {:f} {:f}\n".format(
                            texcoords[0],
                            texcoords[1]))
                    
        
        if sec_flags & SECFLAGS_HAS_VERTEX_COLORS:
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                per_vert_data[new_vert]["color"] = r.read("4B")
                
                
        if sec_flags & SECFLAGS_HAS_VERTEX_COLOR_WIBBLES:
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                r.u8() # We can't import this data currently, so skip past 

        
                
        for j in range(num_meshes):
            p("  mesh #{}", j)
            #p("    center: {}", r.vec3f())
            #p("    radius: {}", r.f32())
            #p("    bbox: {}", (r.vec3f(), r.vec3f()))

            mesh_flags = r.u32()
            p("    flags: {} ({})".format(mesh_flags, bin(mesh_flags)), None)

            mat_checksum = p("    material checksum: {}", to_hex_string(r.u32()))
            mat_index = None
            for existing_mat_index, mat_slot in enumerate(blender_object.material_slots):
                if mat_slot.material.name == mat_checksum:
                    mat_index = existing_mat_index
                    break
            if mat_index is None:
                blender_object.data.materials.append(bpy.data.materials[mat_checksum])
                new_mat_slot = blender_object.material_slots[-1]
                mat_index = len(blender_object.material_slots) - 1

            num_lod_levels = 1
            #num_lod_levels = p("    number of lod index levels: {}", r.u32())
            if num_lod_levels > 16:
                raise Exception("Bad number of lod levels!")


            num_indices_for_this_lod_level = r.u32()
            p("    {}", "num indices for lod level #1: {}".format( num_indices_for_this_lod_level))
            vert_indices = r.read(str(num_indices_for_this_lod_level) + "H")

    
            # bm.verts.ensure_lookup_table()
            inds = vert_indices
            for l in range(2, len(inds)):
                try:
                    if l % 2 == 0:
                        verts = (this_mesh_verts[inds[l - 2]],
                                 this_mesh_verts[inds[l - 1]],
                                 this_mesh_verts[inds[l]])
                        if len(set(verts)) != 3:
                            continue # degenerate triangle
                        bmface = bm.faces.new(verts)
                    else:
                        verts = (this_mesh_verts[inds[l - 2]],
                                 this_mesh_verts[inds[l]],
                                 this_mesh_verts[inds[l - 1]],)
                        if len(set(verts)) != 3:
                            continue # degenerate triangle
                        bmface = bm.faces.new(verts)
                    if mat_index:
                        bmface.material_index = mat_index
                except IndexError as err:
                    print(err)
                except ValueError as err:
                    print(err)

            if sec_flags & SECFLAGS_HAS_TEXCOORDS:
                uv_sets = len(per_vert_data[new_vert].get("uvs", []))
                for l in range(uv_sets):
                    uv_layer = bm.loops.layers.uv.get(str(l)) or bm.loops.layers.uv.new(str(l))
                    for face in bm.faces:
                        for loop in face.loops:
                            pvd = per_vert_data.get(loop.vert)
                            if not pvd: continue
                            loop[uv_layer].uv = pvd["uvs"][l]
                            if sec_flags & SECFLAGS_HAS_VERTEX_COLORS:
                                cb, cg, cr, ca = pvd["color"]
                                loop[color_layer] = (cr / 255.0, cg / 255.0, cb / 255.0)
                                loop[alpha_layer] = (ca / 128.0, ca / 128.0, ca / 128.0)
                                
        bm.verts.index_update()
        bm.to_mesh(blender_mesh)
        
        if vertex_weights:
            vgs = blender_object.vertex_groups
            for vert, (weights, bone_indices) in vertex_weights.items():
                for weight, bone_index in zip(weights, bone_indices):
                    vert_group = vgs.get(str(bone_index)) or vgs.new(str(bone_index))
                    print("{:2s} {:3f}".format(vert_group.name, weight), end='; ')
                    vert_group.add([vert.index], weight, "ADD")
                print()

        if vertex_normals:
            vertex_normals = { vert.index: normal for vert, normal in vertex_normals.items() }
            new_normals = []
            for l in blender_mesh.loops:
                new_normals.append(vertex_normals[l.vertex_index])
            blender_mesh.normals_split_custom_set(new_normals)
            blender_mesh.use_auto_smooth = True



    #p("number of hierarchy objects: {}", r.i32())
    print("COMPLETE!")

    
    
def import_col_thps4(filename, directory):
    p = Printer()
    input_file = os.path.join(directory, filename)
    with open(input_file, "rb") as inp:
        r = Reader(inp.read())

    p("version: {}", r.i32())
    num_objects = p("num objects: {}", r.i32())
    total_verts = p("total verts: {}", r.i32())
    total_large_faces = p("total large faces: {}", r.i32())
    total_small_faces = p("total small faces: {}", r.i32())
    total_large_verts = p("total large verts: {}", r.i32())
    total_small_verts = p("total small verts: {}", r.i32())
    r.i32()  # padding

    base_vert_offset = ((SIZEOF_SECTOR_HEADER + SIZEOF_SECTOR_OBJ * num_objects)
        + 15) & 0xFFFFFFF0
    base_intensity_offset = (base_vert_offset +
        total_large_verts * SIZEOF_FLOAT_VERT_THPS4 +
        total_small_verts * SIZEOF_FIXED_VERT)
    base_face_offset = base_intensity_offset
    
    # THPS4 doesn't seem to distinguish large and small verts
    # Rather, it uses float verts for everything (maybe this wasn't fully implemented)
    if total_large_verts == 0 and total_small_verts == 0:
        base_face_offset = base_vert_offset + (total_verts * SIZEOF_FLOAT_VERT_THPS4)
        
    base_bsp_offset = base_face_offset + ( (total_large_faces * SIZEOF_LARGE_FACE_THPS4) + (total_small_faces * SIZEOF_SMALL_FACE_THPS4)  ) + 4;
    p("bsp offset: {}", base_bsp_offset)
    p("Vert offset: {}", base_vert_offset)
    p("Face offset: {}", base_face_offset)
    p.on = False
    
    output_vert_offset = 1

    for i in range(num_objects):
        bm = bmesh.new()
        cfl = bm.faces.layers.int.new("collision_flags")
        ttl = bm.faces.layers.int.new("terrain_type")
        intensity_layer = bm.loops.layers.color.new("intensity")

        p("obj ", i)
        obj_checksum = p("  checksum: {}", to_hex_string(r.u32()))

        blender_mesh = bpy.data.meshes.new("col_mesh_" + str(obj_checksum))
        blender_object = bpy.data.objects.new("col_" + str(obj_checksum), blender_mesh)

        obj_flags = p("  flags:", r.u16())

        blender_object.thug_col_obj_flags = obj_flags

        obj_num_verts = p("  num verts: {}", r.u16())
        obj_num_faces = p("  num faces: {}", r.u16())
        obj_use_small_faces = p("  use face small: {}", r.bool())
        obj_use_fixed = p("  use fixed verts: {}", r.bool())
        obj_first_face_offset = p("  first face offset: {}", r.u32())  # pointer to array of faces
        obj_bbox_min, obj_bbox_max = p("  bbox: {}", (r.read("4f"), r.read("4f")))
        obj_first_vert_offset = p("  first vert offset: {}", r.u32())  # pointer to array of vertices
        p("bsp tree: {}", r.i32())  # pointer to head of bsp tree
        p("intensity list? {}", r.i32())  # pointer to intensity list
        p("padding: {}", r.i32())  # padding

        old_offset = r.offset

        # THPS4: since all verts are floats, the 'offset' is the number of verts rather than an actual offset
        r.offset = base_vert_offset + (obj_first_vert_offset * SIZEOF_FLOAT_VERT_THPS4)
        per_vert_data = {}
        
        for j in range(obj_num_verts):
            if obj_use_fixed:
                v = r.read("HHH")
                v = (obj_bbox_min[0] + v[0] * 0.0625,
                     obj_bbox_min[1] + v[1] * 0.0625,
                     obj_bbox_min[2] + v[2] * 0.0625)
            else:
                v = r.read("3f")
                tmp_intensity = r.read("4B") # intensity data
                
            new_vert = bm.verts.new((v[0], -v[2], v[1]))
            if not obj_use_fixed:
                per_vert_data[new_vert] = {}
                per_vert_data[new_vert]["intensity"] = tmp_intensity
                
        r.offset = base_face_offset + obj_first_face_offset
        for j in range(obj_num_faces):
            face_flags = r.u16()
            face_terrain_type = r.u16()
            if obj_use_small_faces:
                face_idx = r.read("3B")
                r.read("B") # padding
            else:
                face_idx = r.read("3H")
                r.read("H") # padding?

            if hasattr(bm.verts, "ensure_lookup_table"):
                bm.verts.ensure_lookup_table()

            try:
                bm_face = bm.faces.new((
                    bm.verts[face_idx[0]],
                    bm.verts[face_idx[1]],
                    bm.verts[face_idx[2]]))
                bm_face[cfl] = face_flags
                bm_face[ttl] = face_terrain_type
            except IndexError as err:
                print(err)
            except ValueError:
                pass
            
            
        for face in bm.faces:
            for loop in face.loops:
                pvd = per_vert_data.get(loop.vert)
                if not pvd: continue
                loop[intensity_layer] = (pvd["intensity"][0] / 255.0, pvd["intensity"][1] / 255.0, pvd["intensity"][2] / 255.0)
                    
        bm.to_mesh(blender_mesh)
        blender_object.thug_export_scene = False
        to_group(blender_object, "CollisionMesh")
        bpy.context.scene.objects.link(blender_object)

        output_vert_offset += obj_num_verts
        r.offset = old_offset

# Also works but is way less restrictive - wanted the more rigid import to test out th4 col exports
def import_col_thps4_old(filename, directory):
    p = Printer()
    p.on = True
    input_file = os.path.join(directory, filename)
    with open(input_file, "rb") as inp:
        r = Reader(inp.read())

    p("version: {}", r.i32())
    num_objects = p("num objects: {}", r.i32())
    total_verts = p("total verts: {}", r.i32())
    p("total large faces: {}", r.i32())
    p("total small faces: {}", r.i32())
    total_large_verts = p("total large verts: {}", r.i32())
    total_small_verts = p("total small verts: {}", r.i32())
    r.i32()  # padding

    # Read objects
    col_objs = []
    for i in range(num_objects):
        this_obj = {}
        this_obj['checksum'] = p("  checksum: {}", to_hex_string(r.u32()))
        this_obj['flags'] = p("  flags: {}", r.u16())
        this_obj['num_verts'] = p("  num verts: {}", r.u16())
        this_obj['num_faces'] = p("  num faces: {}", r.u16())
        this_obj['use_small_faces'] = p("  use face small: {}", r.bool())
        this_obj['use_fixed'] = p("  use fixed verts: {}", r.bool())
        this_obj['first_face_offset'] = p("  first face offset: {}", r.u32())  # pointer to array of faces
        this_obj['bbox_min'] = p("  bbox min: {}", r.read("4f") )
        this_obj['bbox_max'] = p("  bbox min: {}", r.read("4f") )
        this_obj['first_vert_offset'] = p("  first vert offset: {}", r.u32())  # pointer to array of vertices
        r.i32()  # pointer to head of bsp tree
        r.i32()  # pointer to intensity list
        r.i32()  # padding
        this_obj['bm'] = bmesh.new()
        this_obj['mesh'] = bpy.data.meshes.new("col_mesh_" + this_obj['checksum'])
        this_obj['object'] = bpy.data.objects.new("col_" + this_obj['checksum'], this_obj['mesh'])
        
        col_objs.append(this_obj)
        
    # Read verts
    p("VERT POS: {}", r.offset)
    for object in col_objs:
        bm = object['bm']
        for j in range(object['num_verts']):
            if object['use_fixed']:
                v = r.read("HHH")
                v = (obj_bbox_min[0] + v[0] * 0.0625,
                     obj_bbox_min[1] + v[1] * 0.0625,
                     obj_bbox_min[2] + v[2] * 0.0625)
            else:
                v = r.read("3f")
                r.read("4B") # intensity data
                
            bm.verts.new((v[0], -v[2], v[1]))

    p("FACE POS: {}", r.offset)
    # Read faces
    for object in col_objs:
        bm = object['bm']
        cfl = bm.faces.layers.int.new("collision_flags")
        ttl = bm.faces.layers.int.new("terrain_type")
        
        for j in range(object['num_faces']):
            face_flags = r.u16()
            # Camera collision flags have opposite meanings on THPS4
            if face_flags & FACE_FLAGS['mFD_CAMERA_COLLIDABLE']:
                face_flags &= ~FACE_FLAGS['mFD_CAMERA_COLLIDABLE']
            else:
                face_flags |= FACE_FLAGS['mFD_CAMERA_COLLIDABLE']
                
            face_terrain_type = r.u16()
            if object['use_small_faces']:
                face_idx = r.read("3B")
                r.read("B") # padding
            else:
                face_idx = r.read("3H")
                r.read("H") # padding

            if hasattr(bm.verts, "ensure_lookup_table"):
                bm.verts.ensure_lookup_table()

            try:
                bm_face = bm.faces.new((
                    bm.verts[face_idx[0]],
                    bm.verts[face_idx[1]],
                    bm.verts[face_idx[2]]))
                bm_face[cfl] = face_flags
                bm_face[ttl] = face_terrain_type
            except IndexError as err:
                print(err)
            except ValueError:
                pass

        bm.to_mesh(object['mesh'])
        object['object'].thug_export_scene = False
        to_group(object['object'], "CollisionMesh")
        bpy.context.scene.objects.link(object['object'])


# OPERATORS
#############################################
class THPS4ScnToScene(bpy.types.Operator):
    bl_idname = "io.th4_xbx_scn_to_scene"
    bl_label = "THPS4 Scene (.scn/.skin/.mdl)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.skin;*.scn;*.mdl;*skin.dat;*mdl.dat;*scn.dat", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    load_tex = BoolProperty(name="Load the tex file", default=True)
    import_custom_normals = BoolProperty(name="Import custom normals", default=True)
    is_desa = BoolProperty(name="Is DESA Level", default=False, description="Use when importing scenes from DESA (the format is slightly different)")

    def execute(self, context):
        filename = self.filename
        directory = self.directory

        if self.load_tex:
            import os, re
            if filename.endswith('dat'):
                tex_filename = re.sub(r'(scn|skin|mdl)\.dat', 'tex.dat', filename, flags=re.IGNORECASE)
            else:
                tex_filename = re.sub(r'\.(scn|skin|mdl)', '.tex', filename, flags=re.IGNORECASE)
            tex_path = os.path.join(directory, tex_filename)
            if tex_filename != filename and os.path.exists(tex_path):
                bpy.ops.io.thug2_tex("EXEC_DEFAULT", filename=tex_filename, directory=directory)

        import_scn_th4(filename, directory, context, self)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
        
        
#----------------------------------------------------------------------------------
class THPS4ColToScene(bpy.types.Operator):
    bl_idname = "io.thps4_col_to_scene"
    bl_label = "THPS4 Collision (.col, col.dat)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.col;*col.dat", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")

    def execute(self, context):
        filename = self.filename
        directory = self.directory

        import_col_thps4(filename, directory)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

        