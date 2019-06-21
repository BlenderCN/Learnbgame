#############################################
# THUG2 SCENE EXPORT
#############################################
import bpy
import bmesh
from bpy.props import *
from bpy_extras.io_utils import ExportHelper
import struct
import mathutils
import math
from . import helpers
from . helpers import *
from . material import *
from . prefs import *
from . autosplit import *

# METHODS
#############################################
#----------------------------------------------------------------------------------

def export_scn_sectors_ug2(output_file, operator=None, is_model=False):
    def w(fmt, *args):
        output_file.write(struct.pack(fmt, *args))

    exported_checksums = {}

    bm = bmesh.new()
    p = Printer()
    out_objects = [o for o in bpy.data.objects
                   if (o.type == "MESH"
                    and getattr(o, 'thug_export_scene', True)
                    and not o.get('thug_autosplit_object_no_export_hack', False))]

    object_counter = 0
    object_amount_offset = output_file.tell()
    w("i", 0)
    for ob in out_objects:
        LOG.debug("exporting object: {}".format(ob))
        # bpy.ops.object.mode_set(mode="OBJECT")
        original_object = ob
        original_object_name = ob.name
        is_levelobject = ob.thug_object_class == "LevelObject"
        if is_levelobject == False and original_object_name.endswith("_SCN"):
            # If using separate collision/scene mesh, check the collision mesh
            if bpy.data.objects.get(original_object_name[:-4]):
                _omgtmp = bpy.data.objects.get(original_object_name[:-4])
                if _omgtmp.thug_object_class == "LevelObject":
                    is_levelobject = True
                    
        if is_levelobject:
            lo_matrix = mathutils.Matrix.Identity(4)
            lo_matrix[0][0] = ob.scale[0]
            lo_matrix[1][1] = ob.scale[1]
            lo_matrix[2][2] = ob.scale[2]
        if not operator.speed_hack:
            ob.name = "TEMP_OBJECT___"
        try:
            if operator.speed_hack:
                final_mesh = ob.data
            else:
                final_mesh = ob.to_mesh(bpy.context.scene, True, 'PREVIEW')
                # LOG.debug("object vc layers: {}", len(ob.data.vertex_colors))
                temporary_object = helpers._make_temp_obj(final_mesh)
                temporary_object.name = original_object_name
            try:
                if operator.speed_hack:
                    object_counter += 1
                    bm.clear()
                    bm.from_mesh(final_mesh)
                else:
                    bpy.context.scene.objects.link(temporary_object)
                    temporary_object.matrix_world = ob.matrix_world

                    if helpers._need_to_flip_normals(ob):
                        helpers._flip_normals(temporary_object)

                    ob = temporary_object

                    object_counter += 1
                    final_mesh = ob.data

                    bm.clear()
                    # final_mesh.calc_normals()

                    bm.from_mesh(final_mesh)
                    bmesh.ops.triangulate(bm, faces=bm.faces)
                    bm.to_mesh(final_mesh)
                    final_mesh.calc_normals_split()
                    bm.clear()
                    bm.from_mesh(final_mesh)

                flags = 0 if not is_levelobject else SECFLAGS_HAS_VERTEX_NORMALS
                
                # Check texture passes for:
                # - Environment mapped textures (normals need to be exported)
                # - Valid UV map assignments (must be in the correct order!)
                need_vertex_normals = False
                for env_test in ob.data.materials:
                    if hasattr(env_test, 'thug_material_props') and env_test.thug_material_props.specular_power > 0.0:
                        #print("-----------------------------------------------")
                        #print("Exporting vertex normals for specular material")
                        #print("-----------------------------------------------")
                        need_vertex_normals = True
                        
                    if not hasattr(env_test, 'texture_slots'): continue
                    _tmp_passes = [tex_slot for tex_slot in env_test.texture_slots if tex_slot and tex_slot.use and tex_slot.use_map_color_diffuse][:4]
                    for _tmp_tex in _tmp_passes:
                        _pprops = _tmp_tex.texture and _tmp_tex.texture.thug_material_pass_props
                        if _pprops and (_pprops.pf_environment or _pprops.pf_bump or _pprops.pf_water or _pprops.blend_mode == 'vBLEND_MODE_GLOSS_MAP'):
                            need_vertex_normals = True
                            #break
                            
                if operator.always_export_normals:
                    need_vertex_normals = True
                if True or len(bm.loops.layers.uv):
                    flags |= SECFLAGS_HAS_TEXCOORDS
                if True or len(bm.loops.layers.color):
                    flags |= SECFLAGS_HAS_VERTEX_COLORS
                if len(original_object.vertex_groups) and is_model == True:
                    flags |= SECFLAGS_HAS_VERTEX_WEIGHTS
                if original_object.thug_is_shadow_volume:
                    flags |= SECFLAGS_SHADOW_VOLUME
                if len(original_object.vertex_groups) or need_vertex_normals:
                    flags |= SECFLAGS_HAS_VERTEX_NORMALS

                mats_to_faces = {}
                if ob.thug_material_blend and len(ob.data.materials) >= 2:
                    for i in range(len(ob.data.materials)):
                        for face in bm.faces:
                            face_list = mats_to_faces.get(i)
                            if face_list:
                                face_list.append(face)
                            else:
                                mats_to_faces[i] = [face]
                            
                else:
                    for face in bm.faces:
                        face_list = mats_to_faces.get(face.material_index)
                        if face_list:
                            face_list.append(face)
                        else:
                            mats_to_faces[face.material_index] = [face]
                    
                        
                
                clean_name = get_clean_name(ob)
                if is_hex_string(clean_name):
                    w("I", int(clean_name, 0))  # checksum
                else:
                    w("I", crc_from_string(bytes(clean_name, 'ascii')))  # checksum
                w("i", -1)  # bone index
                w("I", flags)  # flags
                w("I", len([fs for fs in mats_to_faces.values() if fs]))  # number of meshes
                if is_levelobject:
                    # bbox = get_bbox2(final_mesh.vertices, mathutils.Matrix.Identity(4))
                    bbox = get_bbox2(final_mesh.vertices, lo_matrix)
                else:
                    bbox = get_bbox2(final_mesh.vertices, ob.matrix_world)
                w("6f",
                    bbox[0][0], bbox[0][1], bbox[0][2],
                    bbox[1][0], bbox[1][1], bbox[1][2])  # bbox
                bsphere = get_sphere_from_bbox(bbox)
                w("4f", *bsphere)  # bounding sphere

                for mat_index, mat_faces in mats_to_faces.items():
                    if len(mat_faces) == 0: continue
                    # TODO fix this
                    # should recalc bbox for this mesh
                    w("4f", *bsphere)
                    w("6f",
                        bbox[0][0], bbox[0][1], bbox[0][2],
                        bbox[1][0], bbox[1][1], bbox[1][2])  # bbox
                    the_material = len(ob.material_slots) and ob.material_slots[mat_index].material
                    if not the_material:
                        the_material = bpy.data.materials["_THUG_DEFAULT_MATERIAL_"]
                    if is_hex_string(the_material.name):
                        mat_checksum = int(the_material.name, 0)
                    else:
                        mat_checksum = crc_from_string(bytes(the_material.name, 'ascii'))
                        
                    # Determine if we need to set any mesh flags
                    mesh_flags = 0
                    if the_material.thug_material_props.no_skater_shadow or original_object.thug_no_skater_shadow or (ob.thug_material_blend and mat_index == 1):
                        mesh_flags |= 0x400
                    w("I", mesh_flags)  # mesh flags
                    w("I", mat_checksum)  # material checksum
                    w("I", 1)  # num of index lod levels

                    nonsplit_verts = {vert for face in mat_faces for vert in face.verts}
                    split_verts = make_split_verts(
                        final_mesh,
                        bm,
                        flags,
                        verts=nonsplit_verts)

                    strip = get_triangle_strip(final_mesh, bm, mat_faces, split_verts, flags)
                    w("I", len(strip))
                    w(str(len(strip)) + "H", *strip)
                    w("H", len(strip))
                    w(str(len(strip)) + "H", *strip)

                    # padding?
                    w("14x")

                    passes = [tex_slot for tex_slot in the_material.texture_slots
                              if tex_slot and tex_slot.use and tex_slot.use_map_color_diffuse][:4]

                    vert_normal_offset = 0
                    vert_color_offset = 0
                    vert_texcoord_offset = 0
                    vert_data_stride = 12
                    if flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
                        vert_data_stride += 12
                        if flags & SECFLAGS_HAS_VERTEX_NORMALS:
                            vert_normal_offset = vert_data_stride
                            vert_data_stride += 4 # packed normals
                    elif flags & SECFLAGS_HAS_VERTEX_NORMALS:
                        vert_normal_offset = vert_data_stride
                        vert_data_stride += 12

                    if flags & SECFLAGS_HAS_VERTEX_COLORS:
                        vert_color_offset = vert_data_stride
                        vert_data_stride += 4

                    if flags & SECFLAGS_HAS_TEXCOORDS:
                        # FIXME?
                        vert_texcoord_offset = vert_data_stride
                        vert_data_stride += 8 * (len(passes) or 1)

                    w("B", vert_data_stride) # byte size per vertex
                    w("h", len(split_verts))
                    w("h", 1) # num vert bufs
                    vert_data_size = len(split_verts) * vert_data_stride # total array byte size
                    w("I", vert_data_size)
                    VC_MULT = 128
                    FULL_WHITE = (1.0, 1.0, 1.0, 1.0)
                    for v in split_verts.keys():
                        if is_levelobject:
                            w("3f", *to_thug_coords(lo_matrix * v.co))
                        else:
                            w("3f", *to_thug_coords(ob.matrix_world * v.co))

                        if flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
                            packed_weights = (
                                (int(v.weights[0][1] * 1023.0) & 0x7FF),
                                ((int(v.weights[1][1] * 1023.0) & 0x7FF) << 11),
                                ((int(v.weights[2][1] * 511.0) & 0x3FF) << 22))
                            packed_weights = packed_weights[0] | packed_weights[1] | packed_weights[2]
                            w("I", packed_weights)
                            for group, weight in v.weights:
                                w("H", int(original_object.vertex_groups[group].name) * 3)
                                # w("H", 29 * 3)
                            if flags & SECFLAGS_HAS_VERTEX_NORMALS:
                                packed_normal = (
                                    (int(v.normal[0] * 1023.0) & 0x7FF) |
                                    ((int(v.normal[2] * 1023.0) & 0x7FF) << 11) |
                                    ((int(-v.normal[1] * 511.0) & 0x3FF) << 22))
                                # packed_normal = (1023 & 0x7FF) << 11
                                w("I", packed_normal)
                        elif flags & SECFLAGS_HAS_VERTEX_NORMALS:
                            w("3f", *to_thug_coords_ns(v.normal)) # *to_thug_coords_rot(v.normal))
                            # w("3f", 0, 1, 0)

                        if flags & SECFLAGS_HAS_VERTEX_COLORS:
                            r, g, b, a = v.vc or FULL_WHITE
                            if is_levelobject:
                                r, g, b, a = FULL_WHITE
                            a = (int(a * VC_MULT) & 0xff) << 24
                            r = (int(r * VC_MULT) & 0xff) << 16
                            g = (int(g * VC_MULT) & 0xff) << 8
                            b = (int(b * VC_MULT) & 0xff) << 0
                            w("I", a | r | g | b)

                        # w("i", (len(passes) or 1) if flags & SECFLAGS_HAS_TEXCOORDS else 0)
                        if flags & SECFLAGS_HAS_TEXCOORDS:
                            for tex_slot in passes:
                                uv_index = 0
                                if tex_slot.uv_layer:
                                    uv_index = get_index(
                                        bm.loops.layers.uv.values(),
                                        tex_slot.uv_layer,
                                        lambda layer: layer.name)
                                w("2f", *v.uvs[uv_index])
                            if not passes:
                                w("2f", *v.uvs[0])


                    if flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
                        vertex_shader = 1 # D3DFVF_RESERVED0
                        # vertex_shader |= D3DFVF_XYZ
                    else:
                        vertex_shader = D3DFVF_XYZ
                        if flags & SECFLAGS_HAS_VERTEX_NORMALS:
                            vertex_shader |= D3DFVF_NORMAL
                        if flags & SECFLAGS_HAS_VERTEX_COLORS:
                            vertex_shader |= D3DFVF_DIFFUSE
                        if flags & SECFLAGS_HAS_TEXCOORDS:
                            vertex_shader |= {
                                0: D3DFVF_TEX0,
                                1: D3DFVF_TEX1,
                                2: D3DFVF_TEX2,
                                3: D3DFVF_TEX3,
                                4: D3DFVF_TEX4,
                            }.get(len(passes), 0)

                    w("i", vertex_shader)
                    w("i", 0) # vertex shader 2?
                    # w("B", 12) # vert normal offset
                    # w("B", 24) # vert color offset
                    # w("B", 28) # vert texcoord offset
                    w("B", vert_normal_offset) # vert normal offset
                    w("B", vert_color_offset) # vert color offset
                    w("B", vert_texcoord_offset) # vert texcoord offset
                    w("B", 0) # has color wibble data

                    w("I", 1) # num index sets

                    pixel_shader = 1
                    w("I", pixel_shader)
                    if pixel_shader == 1:
                        w("I", 0)
                        w("I", 0)
            finally:
                safe_mode_set("OBJECT")
                if not operator.speed_hack:
                    ob = temporary_object
                    ob_data = ob.data
                    bpy.context.scene.objects.unlink(ob)
                    bpy.data.objects.remove(ob)
                    bpy.data.meshes.remove(ob_data)
        finally:
            original_object.name = original_object_name
    _saved_offset = output_file.tell()
    output_file.seek(object_amount_offset)
    w("i", object_counter)
    output_file.seek(_saved_offset)
    bm.free()


