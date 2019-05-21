#############################################
# THPS1/2 SCENE (.psx) IMPORT
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
import numpy

VERSION_NUM_THPS2X = 0x06
VERSION_NUM_THPS2 = 0x04
VERSION_NUM_THPS1 = 0x03

# METHODS
#############################################
def ps1_to_32bpp(c):
    r = (c)&0x1F
    g = (c>>5)&0x1F
    b = (c>>10)&0x1F
    a = (c>>15)&0x1

    if((r==31 and g==0 and b==31)):
        # Fully transparent
        return [ 0.0, 0.0, 0.0, 0.0 ]
    else:
        return [ r/32.0, g/32.0, b/32.0, 1.0 ]
        
        
def import_psx_th2(filename, directory, context, operator, texlib_data):
    p = Printer()
    p.on = True
    input_file = os.path.join(directory, filename)
    version_num = VERSION_NUM_THPS2
    with open(input_file, "rb") as inp:
        r = inp

        # Read the file header and determine the number of objects, pointer to tagged chunks
        magic = r.read(4)
        assert magic == b"\x04\x00\x02\x00" or magic == b"\x03\x00\x02\x00" or magic == b"\x06\x00\x02\x00"
        
        # THPS1 psx files have some key differences, mostly in mesh definition
        if magic == b"\x03\x00\x02\x00":
            version_num = VERSION_NUM_THPS1
        elif magic == b"\x03\x00\x02\x00":
            version_num = VERSION_NUM_THPS2X
            
        ptr_meta, obj_count, = struct.unpack("<II", r.read(8))
        p("Num objects: {}", obj_count)
        
        # Read the object list
        object_list = []
        m2o_map = {}
        for i in range(obj_count):
            p("Reading object {} of {}...", i, obj_count)
            o_dat = r.read(36)
            o_flags1, o_px, o_py, o_pz, o_unk1, o_unk2, o_model_idx, o_tx, o_ty, o_unk3, o_ptr_paldata, = struct.unpack("<IiiiIHHhhII", o_dat)
            m2o_map[o_model_idx] = i
            p("POSITION: {} {} {}", o_px, o_py, o_pz)
            p("MESH INDEX: {}", o_model_idx)
            assert len(object_list) <= obj_count
            object_list.append({
                "position": from_thps_coords([o_px/4096.0, o_py/4096.0, o_pz/4096.0]),
                #"pos_x": o_px,
                #"pos_y": o_py,
                #"pos_z": o_pz,
                "o_unk1": o_unk1,
                "o_unk2": o_unk2,
                "model_idx": o_model_idx,
                "o_tx": o_tx,
                "o_ty": o_ty,
                "o_unk3": o_unk3,
                "o_ptr_paldata": o_ptr_paldata,
            })
            
        mesh_start = r.tell()
        PSX_DATA = {}
        
        # Determine number of meshes expected
        mesh_count = struct.unpack("<I", r.read(4))[0]
        p("Num meshes: {}", mesh_count)
        
        # Skip to the tagged chunks, find the textures
        r.seek(ptr_meta)
        chunk_count = -1
        # Other unknown tagged chunks
        while True:
            print("we are at: {}".format(hex(r.tell())))
            magic = r.read(4)
            chunk_count += 1
            if magic != b"\xFF\xFF\xFF\xFF":
                if magic == b"RGBs":
                    print("HAS PALETTE")
                    palette_length = struct.unpack("<I", r.read(4))[0]
                    palette_entries = int(palette_length/4)
                    print(palette_length)
                    palette_data = []
                    assert palette_length % 4 == 0
                    for i in range( palette_entries ):
                        palette_data.append(struct.unpack("<BBBB", r.read(4)))
                    PSX_DATA["palette"] = palette_data
                    
                elif magic == b"\x0A\x00\x00\x00":
                    print("HAS BLOCKMAP")
                    blockmap_length = struct.unpack("<I", r.read(4))[0]
                    r.read(blockmap_length) # Skipped for now
                    
                else:
                    p("UNKNOWN CHUNK: {}", magic)
                    unk_length = struct.unpack("<I", r.read(4))[0]
                    r.read(unk_length) # Skipped for now
                    if chunk_count > 16:
                        # There should not be this many tagged chunks, must be a file error
                        raise Exception("Unable to parse PSX texture library, cannot find texture data")
            else:
                print("END OF TAGGED CHUNKS")
                break
            
        
        # Grab the mesh names array - we can assign these checksums to the object names created in read_meshes
        mesh_names = []
        for i in range(mesh_count):
            mesh_names.append(struct.unpack("<I", r.read(4))[0])
        PSX_DATA["mesh_names"] = mesh_names
        
        # Read texture info - we need to map texture entries from the .psx file into the texlib
        print("we are at: {}".format(hex(r.tell())))
        num_tex = struct.unpack("<I", r.read(4))[0]
        p("Num textures: {}", num_tex)
        psx_tex_names = []
        for i in range(num_tex):
            psx_tex_names.append(struct.unpack("<I", r.read(4))[0])
        PSX_DATA["psx_tex_names"] = psx_tex_names
        PSX_DATA["texlib_data"] = texlib_data
        PSX_DATA["version_num"] = version_num
        
        print("we are at: {}".format(hex(r.tell())))
        # Go back to the start of mesh data, so we can generate the meshes now that we have texture info
        r.seek(mesh_start)
        mesh_list = read_meshes_thps2(r, p, obj_count, directory, operator, PSX_DATA)
    
        for obj in object_list:
            this_mesh = mesh_list[obj["model_idx"]]
            blender_object = bpy.data.objects.new("obj_{}".format(this_mesh.name), this_mesh)
            blender_object.thug_export_collision = True
            blender_object.thug_export_scene = True
            to_group(blender_object, "SceneMesh")
            context.scene.objects.link(blender_object)
            blender_object.location = obj["position"]
    

def find_texture(psx_tex_names, texlib_data, tex_index):
    # Map texture index to relevant hash
    if tex_index >= len(psx_tex_names):
        print("Error: tex index {} out of bounds".format(tex_index))
        return ""
        
    texture_hash = psx_tex_names[tex_index]
    # If using 
    #if bpy.data.materials.get("THPSMat_{}".format(hex(texture_hash))):
    #    return bpy.data.materials.get("THPSMat_{}".format(hex(texture_hash)))
        
    #print("Searching for tex hash {} in tex_names...".format(hex(texture_hash)))
    #print(tex_names)
    for i in range(len(texlib_data["tex_names"])):
        if texlib_data["tex_names"][i] == texture_hash:
            texture_idx = i
            for x in range(len(texlib_data["texinfo"])):
                if texlib_data["texinfo"][x]["index"] == texture_idx:
                    if bpy.data.materials.get("THPSMat_{}".format(hex(texlib_data["texinfo"][x]["hash"]))):
                        return bpy.data.materials.get("THPSMat_{}".format(hex(texlib_data["texinfo"][x]["hash"])))
                    
            
    #print ("NOT FOUND")
    return None
    
#----------------------------------------------------------------------------------
def read_meshes_thps2(reader, printer, num_objects, directory, operator, psx_data):
    import os
    r = reader
    p = printer

    mdl_count, = struct.unpack("<I", r.read(4))
    mdl_ptr_list = [struct.unpack("<I", r.read(4))[0] for i in range(mdl_count)]

    valid_tex_list = []
    tex_ptr_list = []
    mesh_list = []
    f = (1 << 12)
    
    for (mdl_i, ptr) in enumerate(mdl_ptr_list):
        mesh_name = "{:08x}".format(psx_data["mesh_names"][mdl_i])
        blender_mesh = bpy.data.meshes.new("0x{}".format(mesh_name))
        print("New mesh: {}".format("0x{}".format(mesh_name)))
        
        # Create new mesh
        bm = bmesh.new()
        
        vertex_normals = {}
        this_mesh_verts = []
        per_vert_data = {}
        
        # Stores all verts and faces for this mesh
        m_uvs = []
        m_faces = []
        m_matindices = []
        m_normals = []
        m_flags = []
        m_vcs = []
        
        nextptr = (mdl_ptr_list[mdl_i+1] if mdl_i+1 < mdl_count else ptr)
        delta = (mdl_ptr_list[mdl_i+1]-ptr if mdl_i+1 < mdl_count else 0)
        r.seek(ptr)
        #print("Reading new mesh at: {}".format(hex(r.tell())))
        
        # THPS1 uses uint32 for these values, THPS2 uses uint16 
        if psx_data["version_num"] == VERSION_NUM_THPS2:
            m_unk1, m_vertex_count, m_plane_count, m_face_count = struct.unpack("<HHHH", r.read(8))
        elif psx_data["version_num"] == VERSION_NUM_THPS1:
            m_unk1, m_vertex_count, m_plane_count, m_face_count = struct.unpack("<IIII", r.read(16))
            
        #p("MESH FLAGS: {}", m_unk1)
        #p("NUM VERTICES: {}", m_vertex_count)
        #p("NUM PLANES: {}", m_plane_count)
        #p("NUM FACES: {}", m_face_count)

        m_gunkl1, = struct.unpack("<I", r.read(4))
        m_xmax, m_xmin, = struct.unpack("<hh", r.read(4))
        m_ymax, m_ymin, = struct.unpack("<hh", r.read(4))
        m_zmax, m_zmin, = struct.unpack("<hh", r.read(4))
        m_gunkl2, = struct.unpack("<I", r.read(4))
        
        ptr_vertex = r.tell()
        #p("Verts are at: {}", hex(ptr_vertex))
        for i in range(m_vertex_count):
            cur_vert = struct.unpack("<hhhh", r.read(8))
            vert_pos = [ cur_vert[0] / 1.0, cur_vert[1] / 1.0, cur_vert[2] / 1.0 ]
            this_mesh_verts.append(from_thps_coords(vert_pos))
            
        ptr_planes = r.tell()
        #p("Planes are at: {}", hex(ptr_planes))
        for i in range(m_plane_count):
            plane_normal = struct.unpack("<hhh", r.read(6))
            r.read(2)
            m_normals.append(plane_normal)
            m_normals.append(plane_normal)
            m_normals.append(plane_normal)
                
        #m_plane_2d_list = list(struct.unpack("<hhhh", r.read(8)) for i in range(m_plane_count))
        ptr_faces = r.tell()
        #p("ptr to vertices: {}, planes: {}, faces: {}", ptr_vertex, ptr_planes, ptr_faces)
        
        #p("Faces are at: {}", hex(ptr_faces))
        for i in range(m_face_count):
            face_flags = struct.unpack("<H", r.read(2))[0]
            #p("face flags: {}", hex(face_flags))
            
            cur_length = 2
            face_length = struct.unpack("<H", r.read(2))
            cur_length += 2
            #p("FACE LENGTH: {}", face_length)
            
            # Vert indices are bytes in thps2, shorts in thps1
            if psx_data["version_num"] == VERSION_NUM_THPS2:
                vertex_indices = struct.unpack("<BBBB", r.read(4))
                cur_length += 4
            elif psx_data["version_num"] == VERSION_NUM_THPS1:
                vertex_indices = struct.unpack("<HHHH", r.read(8))
                cur_length += 8
            
            is_quad = False
            has_vertex_colors = False
            if not face_flags & 0x0010:
                is_quad = True
            if face_flags & 0x0800:
                has_vertex_colors = True
                
            #p("vert indices: {} {} {} {}", vertex_indices[0],vertex_indices[1],vertex_indices[2],vertex_indices[3])
            
            shade_data = struct.unpack("<BBBB", r.read(4))
            
            plane_index = struct.unpack("<H", r.read(2))
            col_flags = struct.unpack("<H", r.read(2))[0]
            m_flags.append(col_flags)
            #p("col flags: {}", hex(col_flags))
            if is_quad:
                m_flags.append(col_flags)
            cur_length += 8
            
            # Add vertex colors 
            if has_vertex_colors: # Per-vertex palette entries
                m_vcs.append(psx_data["palette"][shade_data[2]])
                m_vcs.append(psx_data["palette"][shade_data[1]])
                m_vcs.append(psx_data["palette"][shade_data[0]])
                if is_quad:
                    m_vcs.append(psx_data["palette"][shade_data[1]])
                    m_vcs.append(psx_data["palette"][shade_data[2]])
                    m_vcs.append(psx_data["palette"][shade_data[3]])
            else: # Flat shaded, one color for all verts
                m_vcs.append([ shade_data[0], shade_data[1], shade_data[2] ])
                m_vcs.append([ shade_data[0], shade_data[1], shade_data[2] ])
                m_vcs.append([ shade_data[0], shade_data[1], shade_data[2] ])
                if is_quad:
                    m_vcs.append([ shade_data[0], shade_data[1], shade_data[2] ])
                    m_vcs.append([ shade_data[0], shade_data[1], shade_data[2] ])
                    m_vcs.append([ shade_data[0], shade_data[1], shade_data[2] ])
            
                    
            is_textured = False
            mat_index = None
            if face_flags & 0x0003:
                # Read tex index and do a lookup in tex_names to find the material that should have been
                # created during the texlib import earlier
                tex_index = struct.unpack("<I", r.read(4))[0]
                
                search_mat = find_texture(psx_data["psx_tex_names"], psx_data["texlib_data"], tex_index)
                if search_mat:
                    for existing_mat_index, mat_slot in enumerate(blender_mesh.materials):
                        if mat_slot.name == search_mat.name:
                            mat_index = existing_mat_index
                            break
                    if mat_index is None:
                        blender_mesh.materials.append(search_mat)
                        mat_index = len(blender_mesh.materials) -1
                
                    
                if mat_index != None and mat_index >= 0 and hasattr(blender_mesh.materials[mat_index].texture_slots[0].texture, 'image'):
                    tex_size_x = float(blender_mesh.materials[mat_index].texture_slots[0].texture.image.size[0])
                    tex_size_y = float(blender_mesh.materials[mat_index].texture_slots[0].texture.image.size[1])
                else:
                    tex_size_x = 64.0
                    tex_size_y = 64.0
                    
                #if tex_size_x >= 128.0:
                #    tex_size_x *= 2.0
                #if tex_size_y >= 128.0:
                #    tex_size_y *= 2.0
                    
                tex_coords = [ 0, 0, 0, 0, 0, 0, 0, 0]
                for i in range(4):
                    tx = struct.unpack("<B", r.read(1))[0]
                    ty = struct.unpack("<B", r.read(1))[0]
                    tx /= tex_size_x;
                    ty /= tex_size_y;
                    ty *= -1.0
                    tex_coords[i+i] = tx
                    tex_coords[i+i+1] = ty
                    
                cur_length += 12
                is_textured = True
                
            # Extra unknown data, skip over it
            if (cur_length < face_length[0]):
                r.read(face_length[0] - cur_length)
                
            # Tri face
            if is_quad == False:
                verts = [ this_mesh_verts[vertex_indices[2]], this_mesh_verts[vertex_indices[1]],  this_mesh_verts[vertex_indices[0]] ]
                m_faces.append(verts)
                
                if is_textured:
                    m_uvs.append([ tex_coords[4], tex_coords[5] ])
                    m_uvs.append([ tex_coords[2], tex_coords[3] ])
                    m_uvs.append([ tex_coords[0], tex_coords[1] ])
                else:
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    
                if mat_index:
                    m_matindices.append(mat_index)
                else:
                    m_matindices.append(-1)
                    
            # Quad face 
            else: 
                verts = [ this_mesh_verts[vertex_indices[2]], this_mesh_verts[vertex_indices[1]], 
                    this_mesh_verts[vertex_indices[0]] ]
                verts2 = [ this_mesh_verts[vertex_indices[1]], this_mesh_verts[vertex_indices[2]], 
                    this_mesh_verts[vertex_indices[3]] ]
                m_faces.append(verts)
                m_faces.append(verts2)
                
                if is_textured:
                    m_uvs.append([ tex_coords[4], tex_coords[5] ])
                    m_uvs.append([ tex_coords[2], tex_coords[3] ])
                    m_uvs.append([ tex_coords[0], tex_coords[1] ])
                    
                    m_uvs.append([ tex_coords[2], tex_coords[3] ])
                    m_uvs.append([ tex_coords[4], tex_coords[5] ])
                    m_uvs.append([ tex_coords[6], tex_coords[7] ])
                
                else:
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    m_uvs.append([0,0])
                    
                if mat_index:
                    m_matindices.append(mat_index)
                    m_matindices.append(mat_index)
                else:
                    m_matindices.append(-1)
                    m_matindices.append(-1)
                    
        # Now build the mesh!
        face_count = -1
        for verts in m_faces:
            face_count += 1
            for i in range(3):
                bm_vert = bm.verts.new(verts[i])
        
            bm.verts.ensure_lookup_table()
            bm.verts.index_update() 
        
        for i in range(0, len(m_faces)):
            bmface = bm.faces.new([bm.verts[i*3], bm.verts[i*3+1], bm.verts[i*3+2]] )
            if m_matindices[i] != -1:
                bmface.material_index = m_matindices[i]
            #if i < len(m_normals):
            #    bmface.normal = m_normals[i]
                
        # Set UVs and collision flags
        uv_layer = bm.loops.layers.uv.new()
        color_layer = bm.loops.layers.color.new("color")
        cfl = bm.faces.layers.int.new("collision_flags")
        face_count = -1
        for face in bm.faces:
            face_count += 1
            if m_flags[face_count] & 0x0010: # Wallridable
                face[cfl] |= FACE_FLAGS["mFD_WALL_RIDABLE"]
            elif m_flags[face_count] & 0x0040: # Vert
                face[cfl] |= FACE_FLAGS["mFD_VERT"]
            elif m_flags[face_count] & 0x0100: # Not skateable (THPS1 beta considers this wallride)
                if psx_data["version_num"] == VERSION_NUM_THPS1:
                    face[cfl] |= FACE_FLAGS["mFD_WALL_RIDABLE"]
                else:
                    face[cfl] |= FACE_FLAGS["mFD_NOT_SKATABLE"]
                
            for loop in face.loops:
                loop[uv_layer].uv = m_uvs[loop.vert.index]
                if m_vcs[loop.vert.index] == -1:
                    vc = [128.0, 128.0, 128.0, 128.0]
                else:
                    vc = m_vcs[loop.vert.index]
                loop[color_layer] = (vc[0] / 128.0, vc[1] / 128.0, vc[2] / 128.0)
        
        bm.verts.index_update()
        bm.normal_update()
        bm.to_mesh(blender_mesh)
        
        #blender_mesh.normals_split_custom_set(m_normals)
        
        mesh_list.append(blender_mesh)
        
    return mesh_list


#----------------------------------------------------------------------------------
def import_texlib_th2(filename, directory, context, operator):
    p = Printer()
    p.on = True
    input_file = os.path.join(directory, filename)
    
    tex_hashes = {}
    with open(input_file, "rb") as inp:
        r = inp

        # Read the file header and determine the number of objects, pointer to tagged chunks
        magic = r.read(4)
        assert magic == b"\x04\x00\x02\x00" or magic == b"\x03\x00\x02\x00" or magic == b"\x06\x00\x02\x00"
        ptr_meta, obj_count, = struct.unpack("<II", r.read(8))
        
        TEXPSX_DATA = {}
        p("Num objects: {}", obj_count)
        for i in range(obj_count):
            # Skip over object data
            o_dat = r.read(36)
            
        # Determine number of meshes (we need to skip over the mesh name list before texture info)
        mesh_count = struct.unpack("<I", r.read(4))[0]
        p("Num meshes: {}", mesh_count)
        
        # Skip to the tagged chunks, find the textures
        r.seek(ptr_meta)
        chunk_count = -1
        while True:
            magic = r.read(4)
            chunk_count += 1
            if magic != b"\xFF\xFF\xFF\xFF":
                p("SKIPPED CHUNK: {}", magic)
                unk_length = struct.unpack("<I", r.read(4))[0]
                r.read(unk_length)
                if chunk_count > 16:
                    # There should not be this many tagged chunks, must be a file error
                    raise Exception("Unable to parse PSX texture library, cannot find texture data")
            else:
                print("END OF TAGGED CHUNKS")
                break
                
        # Now we are at the model names list - if there are any models
        for i in range(mesh_count):
            r.read(4)
            
        print("we are at: {}".format(hex(r.tell())))
        num_tex = struct.unpack("<I", r.read(4))[0]
        p("Num textures: {}", num_tex)
        TEXPSX_DATA["num_tex"] = num_tex
        
        tex_names = []
        for i in range(num_tex):
            tex_names.append(struct.unpack("<I", r.read(4))[0])
        TEXPSX_DATA["tex_names"] = tex_names
        
        #if operator.load_tex == False:
            
        # -------------------------------------------------
        # Direct reading from the PSX file - incomplete
        # -------------------------------------------------
        
        # Read 16-color palettes
        num_4bit = struct.unpack("<I", r.read(4))[0]
        p("Num 16-color tex: {}", num_4bit)
        palette_4bit = []
        for i in range(num_4bit):
            this_pal = { "texid": struct.unpack("<I", r.read(4))[0] }
            this_pal["colordata"] = struct.unpack("16H", r.read(16*2))
            palette_4bit.append(this_pal)
            
        # Read 256-color palettes
        num_8bit = struct.unpack("<I", r.read(4))[0]
        p("Num 256-color tex: {}", num_8bit)
        palette_8bit = []
        for i in range(num_8bit):
            this_pal = { "texid": struct.unpack("<I", r.read(4))[0] }
            this_pal["colordata"] = struct.unpack("256H", r.read(256*2))
            palette_8bit.append(this_pal)
        
        num_actual_tex = struct.unpack("<I", r.read(4))[0]
        p("Num actual textures: {}", num_actual_tex)
        p("I am at: {}", hex(r.tell()))
        
        for i in range(num_actual_tex):
            r.read(4) # Maybe THPS2 beta only? 4-byte blocks that seem meaningless
            
        p("I am at: {}", hex(r.tell()))
        TEXPSX_DATA["texinfo"] = []
        for i in range(num_actual_tex):
            tex_unk1 = struct.unpack("<I", r.read(4))[0]
            tex_palsize = struct.unpack("<I", r.read(4))[0]
            tex_hash = struct.unpack("<I", r.read(4))[0]
            tex_index = struct.unpack("<I", r.read(4))[0]
            tex_width = struct.unpack("<H", r.read(2))[0]
            tex_height = struct.unpack("<H", r.read(2))[0]
            p("tex index: {}, palette: {}, tex dimensions: {} {}", tex_index, tex_palsize, tex_width, tex_height)
            tex_hashes[i] = tex_names[i] #tex_hash
            TEXPSX_DATA["texinfo"].append({
                "palette": tex_palsize
                ,"hash": tex_hash
                ,"index": tex_index
                ,"width": tex_width
                ,"height": tex_height
            })
            
            # Now read the raw texture data
            raw_texdata = []
            if tex_palsize == 16:
                padwidth = (tex_width+0x3)&~0x3;
                padwidth >>= 1;
                reallen = (padwidth*tex_height)
                pal_indices = r.read(reallen) # Just read for now
                # Find the palette and build the image
                for pal in palette_4bit:
                    if pal["texid"] == tex_hash:
                        is_trans = False
                        this_palette = pal
                        blend_img = bpy.data.images.new("0x{:08x}.png".format(tex_hash), tex_width, tex_height, alpha=True)
                        pixels = [None] * (tex_width * tex_height)
                        for y in range(tex_height):
                            for x in range(tex_width):
                                v = (pal_indices[y*padwidth+(x>>1)]>>((x&0x1)*4))&0xF
                                c = pal["colordata"][v]
                                px = ps1_to_32bpp(c)
                                pixels[y*tex_width-x] = px
                                if px[3] < 1.0:
                                    is_trans = True
                        blend_img.pixels = [chan for px in list(reversed(pixels)) for chan in px]
                        blend_img.pack(as_png=True)
                        
                        # Also create the material!
                        new_mat = bpy.data.materials.new("THPSMat_{}".format(hex(tex_hash)))
                        blender_tex = bpy.data.textures.new("THPSTex_{}".format(hex(tex_hash)), "IMAGE")
                        blender_tex.image = blend_img
                        tex_slot = new_mat.texture_slots.add()
                        tex_slot.texture = blender_tex 
                        if is_trans:
                            new_mat.thug_material_props.draw_order = 1501.0
                            blender_tex.thug_material_pass_props.blend_mode = "vBLEND_MODE_BLEND"
                        break
                        
            elif tex_palsize == 256:
                padwidth = (tex_width+0x1)&~0x1;
                reallen = (padwidth*tex_height)
                pal_indices = r.read(reallen) # Just read for now
                # Find the palette and build the image
                for pal in palette_8bit:
                    if pal["texid"] == tex_hash:
                        is_trans = False
                        this_palette = pal
                        blend_img = bpy.data.images.new("0x{:08x}.png".format(tex_hash), tex_width, tex_height, alpha=True)
                        pixels = [None] * (tex_width * tex_height)
                        for y in range(tex_height):
                            for x in range(tex_width):
                                v = (pal_indices[y*padwidth+x])&0xFF
                                c = pal["colordata"][v]
                                px = ps1_to_32bpp(c)
                                pixels[y*tex_width-x] = px
                                if px[3] < 1.0:
                                    is_trans = True
                        blend_img.pixels = [chan for px in list(reversed(pixels)) for chan in px]
                        blend_img.pack(as_png=True)
                        
                        # Also create the material!
                        new_mat = bpy.data.materials.new("THPSMat_{}".format(hex(tex_hash)))
                        blender_tex = bpy.data.textures.new("THPSTex_{}".format(hex(tex_hash)), "IMAGE")
                        blender_tex.image = blend_img
                        tex_slot = new_mat.texture_slots.add()
                        tex_slot.texture = blender_tex
                        if is_trans:
                            new_mat.thug_material_props.draw_order = 1501.0
                            blender_tex.thug_material_pass_props.blend_mode = "vBLEND_MODE_BLEND"
                        break
                        
    print("Complete!")
    
    if False:
        # If we don't want to load textures from the PSX file, attempt to look for flat files in the same folder
        for tex_index, tex_hash in tex_hashes.items():
            img_hash = int.from_bytes(struct.pack('>I', tex_hash), byteorder='big', signed=False) # Image names from psxtex are in big endian
            
            if not bpy.data.materials.get("THPSMat_{}".format(hex(tex_hash))):
                new_mat = bpy.data.materials.new("THPSMat_{}".format(hex(tex_hash)))
                blender_tex = bpy.data.textures.new("THPSTex_{}".format(hex(tex_hash)), "IMAGE")
                
                print("Searching for image: {:08x}.png".format((img_hash)))
                full_path = os.path.join(directory, str("{:08x}.png".format(img_hash)))
                full_path2 = os.path.join(directory, str("{:08x}.bmp".format(img_hash)))
                if os.path.exists(full_path):
                    print("Found image: {}".format(full_path))
                    blender_tex.image = bpy.data.images.load(full_path)
                elif os.path.exists(full_path2):
                    print("Found image: {}".format(full_path2))
                    blender_tex.image = bpy.data.images.load(full_path2)
                    
                tex_slot = new_mat.texture_slots.add()
                tex_slot.texture = blender_tex
                
    return TEXPSX_DATA

                

# OPERATORS
#############################################
class THPS2PsxToScene(bpy.types.Operator):
    bl_idname = "io.th2_psx_to_scene"
    bl_label = "THPS 1st-gen Scene (.psx)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.psx", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    load_tex = BoolProperty(name="Load textures", default=True)
    #import_custom_normals = BoolProperty(name="Import custom normals", default=True)

    def execute(self, context):
        filename = self.filename
        directory = self.directory
        
        if self.load_tex:
            # Look for the texture lib file for levels, which is usually [scene]_l.psx
            # Also account for _2 scenes (usually 2-player variants of a level)
            if filename[:-4].endswith('_2'):
                tex_filename = filename[:-6] + '_l2.psx'
                tex_filename_alt = filename[:-6] + '_l.psx'
                tex_filename_alt2 = filename[:-6] + '_L2.psx'
                tex_filename_alt3 = filename[:-6] + '_L.psx'
            elif filename[:-4].endswith('_o') or filename[:-4].endswith('_O'):
                tex_filename = filename[:-6] + '_l.psx'
                tex_filename_alt = filename[:-6] + '_l2.psx'
                tex_filename_alt2 = filename[:-6] + '_L.psx'
                tex_filename_alt3 = filename[:-6] + '_L2.psx'
            elif filename[:-4].endswith('_g') or filename[:-4].endswith('_G'):
                tex_filename = filename[:-6] + '_l.psx'
                tex_filename_alt = filename[:-6] + '_l2.psx'
                tex_filename_alt2 = filename[:-6] + '_L.psx'
                tex_filename_alt3 = filename[:-6] + '_L2.psx'
            else:
                tex_filename = filename[:-4] + '_l.psx'
                tex_filename_alt = filename[:-4] + '_l2.psx'
                tex_filename_alt2 = filename[:-4] + '_L.psx'
                tex_filename_alt3 = filename[:-4] + '_L2.psx'
            tex_path = os.path.join(directory, tex_filename)
            tex_path_alt = os.path.join(directory, tex_filename_alt)
            tex_path_alt2 = os.path.join(directory, tex_filename_alt2)
            tex_path_alt3 = os.path.join(directory, tex_filename_alt3)
            
            if os.path.exists(tex_path):
                print("Using texlib: {}".format(tex_path))
                texlib_data = import_texlib_th2(tex_filename, directory, context, self)
            elif os.path.exists(tex_path_alt):
                print("Using texlib: {}".format(tex_path_alt))
                texlib_data = import_texlib_th2(tex_filename_alt, directory, context, self)
            elif os.path.exists(tex_path_alt2):
                print("Using texlib: {}".format(tex_path_alt2))
                texlib_data = import_texlib_th2(tex_filename_alt2, directory, context, self)
            elif os.path.exists(tex_path_alt3):
                print("Using texlib: {}".format(tex_path_alt3))
                texlib_data = import_texlib_th2(tex_filename_alt3, directory, context, self)
            else:
                # If there is no texture library file, then just use the psx file we are importing to find textures
                # This is the case for models/skins and some beta levels
                print("Loading textures from main PSX file")
                texlib_data = import_texlib_th2(filename, directory, context, self)
        else:
            # Not loading textures
            texlib_data = {}
            texlib_data["num_tex"] = 0
            texlib_data["tex_names"] = []
            texlib_data["texinfo"] = []
            
        import_psx_th2(filename, directory, context, self, texlib_data)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
        
        