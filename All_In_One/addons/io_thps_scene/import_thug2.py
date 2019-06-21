#############################################
# THUG2 SCENE (.scn/.mdl/skin) IMPORT
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
from bpy.props import *
from . helpers import *
from . material import *


# METHODS
#############################################

def import_col(filename, directory):
    p = Printer()
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

    base_vert_offset = ((SIZEOF_SECTOR_HEADER + SIZEOF_SECTOR_OBJ * num_objects)
        + 15) & 0xFFFFFFF0
    base_intensity_offset = (base_vert_offset +
        total_large_verts * SIZEOF_FLOAT_VERT +
        total_small_verts * SIZEOF_FIXED_VERT)
    base_face_offset = ((base_intensity_offset + total_verts) + 3) & 0xFFFFFFFC

    output_vert_offset = 1

    p.on = True
    for i in range(num_objects):
        bm = bmesh.new()
        cfl = bm.faces.layers.int.new("collision_flags")
        ttl = bm.faces.layers.int.new("terrain_type")
        intensity_layer = bm.loops.layers.color.new("intensity")

        p("obj ", i)
        obj_checksum = p("  checksum: {}", to_hex_string(r.u32()))

        blender_mesh = bpy.data.meshes.new("col_mesh_" + str(obj_checksum))
        blender_object = bpy.data.objects.new("col_" + str(obj_checksum), blender_mesh)
        # blender_object["thug_checksum"] = obj_checksum

        obj_flags = p("  flags:", r.u16())

        blender_object.thug_col_obj_flags = obj_flags

        obj_num_verts = p("  num verts: {}", r.u16())
        obj_num_faces = p("  num faces: {}", r.u16())
        obj_use_small_faces = p("  use face small: {}", r.bool())
        obj_use_fixed = p("  use fixed verts: {}", r.bool())
        obj_first_face_offset = p("  first face offset: {}", r.u32())  # pointer to array of faces
        obj_bbox_min, obj_bbox_max = p("  bbox: {}", (r.read("4f"), r.read("4f")))
        obj_first_vert_offset = p("  first vert offset: {}", r.u32())  # pointer to array of vertices
        r.i32()  # pointer to head of bsp tree
        obj_intensity_offset = p("  intensities offset: {}", r.i32())  # pointer to intensity list
        r.i32()  # padding

        old_offset = r.offset

        r.offset = base_vert_offset + obj_first_vert_offset

        per_vert_data = {}
        for j in range(obj_num_verts):
            if obj_use_fixed:
                v = r.read("HHH")
                v = (obj_bbox_min[0] + v[0] * 0.0625,
                     obj_bbox_min[1] + v[1] * 0.0625,
                     obj_bbox_min[2] + v[2] * 0.0625)
            else:
                v = r.read("3f")
            # outp.write("v {} {} {}\n".format(v[0], v[1], v[2]))
            orig_offset = r.offset
            new_vert = bm.verts.new((v[0], -v[2], v[1]))
            # Grab the intensity data for this vert
            per_vert_data[new_vert] = {}
            r.offset = base_intensity_offset + obj_intensity_offset + j
            per_vert_data[new_vert]["intensity"] = r.read("B")
            r.offset = orig_offset
            # bm.verts.new(v)
            
        #outp.write("o {}\n".format(i))
        r.offset = base_face_offset + obj_first_face_offset
        for j in range(obj_num_faces):
            face_flags = r.u16()
            face_terrain_type = r.u16()
            if obj_use_small_faces:
                face_idx = r.read("3B")
                r.read("B") # padding
            else:
                face_idx = r.read("3H")

            if False and face_flags & FACE_FLAGS["mFD_INVISIBLE"]:
                blender_object.hide = True

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
                loop[intensity_layer] = (pvd["intensity"][0] / 255.0, pvd["intensity"][0] / 255.0, pvd["intensity"][0] / 255.0)
                    
        bm.to_mesh(blender_mesh)
        blender_object.thug_export_scene = False
        to_group(blender_object, "CollisionMesh")
        bpy.context.scene.objects.link(blender_object)

        output_vert_offset += obj_num_verts
        r.offset = old_offset

#----------------------------------------------------------------------------------
def import_scn_ug2(filename, directory, context, operator):
    p = Printer()
    p.on = False
    input_file = os.path.join(directory, filename)
    with open(input_file, "rb") as inp:
        r = Reader(inp.read())

    r.read("3I")

    num_materials = p("num materials: ", r.u32())
    read_materials(r, p, num_materials, directory, operator)
    num_sectors = p("num sectors: {}", r.i32())
    objects = read_sectors_ug2(r, p, num_sectors, context, operator)
    rename_imported_materials()
    
    return objects

#----------------------------------------------------------------------------------
def read_sectors_ug2(reader, printer, num_sectors, context, operator=None, output_file=None):
    r = reader
    p = printer
    outf = output_file

    vert_position_index_offset = 1
    vert_texcoord_index_offset = 1
    new_objects = []
    
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
        # context.scene.objects.active = blender_object

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

        for j in range(num_meshes):
            p("  mesh #{}", j)
            p("    center: {}", r.vec3f())
            p("    radius: {}", r.f32())
            p("    bbox: {}", (r.vec3f(), r.vec3f()))

            mesh_flags = r.u32()
            p("    flags: {} ({})".format(mesh_flags, bin(mesh_flags)), None)

            mat_checksum = p("    material checksum: {}", to_hex_string(r.u32()))
            mat_index = None
            for existing_mat_index, mat_slot in enumerate(blender_object.material_slots):
                if mat_slot.material.name == mat_checksum:
                    mat_index = existing_mat_index
                    break
            if mat_index is None:
                # bpy.ops.object.material_slot_add()
                blender_object.data.materials.append(bpy.data.materials[mat_checksum])
                new_mat_slot = blender_object.material_slots[-1]
                # new_mat_slot.material = bpy.data.materials[mat_checksum]
                mat_index = len(blender_object.material_slots) - 1

            num_lod_levels = p("    number of lod index levels: {}", r.u32())
            if num_lod_levels > 16:
                raise Exception("Bad number of lod levels!")
            # num_tc_sets = p("    number of texcoord sets: {}", num_passes) # MATERIAL_PASSES[mat_checksum])

            for k in range(num_lod_levels):
                num_indices_for_this_lod_level = r.u32()
                p("    {}", "num indices for lod level #{}: {}".format(k, num_indices_for_this_lod_level))
                vert_indices = r.read(str(num_indices_for_this_lod_level) + "H")
                num_indices_for_this_lod_level2 = r.u16()
                p("    {}", "num indices for lod level #{} (2nd round?): {}".format(k, num_indices_for_this_lod_level2))
                the_indices_for_this_lod_level2 = r.read(str(num_indices_for_this_lod_level2) + "H")
                min_index = p("    min index: {}", min(*the_indices_for_this_lod_level2))
                max_index = p("    max index: {}", max(*the_indices_for_this_lod_level2))

                """
                workspace_buffer_thing = [1] * (max_index + 1)
                for index in the_indices_for_this_lod_level2:
                    workspace_buffer_thing[index] = 0
                wasted_verts = 0
                for index in range(min_index, max_index):
                    if workspace_buffer_thing[index] != 0:
                        wasted_verts += 1
                p("    wasted verts: {}", wasted_verts)
                """

                r.read("14x") # padding?

                vertex_data_stride = p("    vertex data stride: {}", r.u8())
                amount_of_verts = p("    amount of verts: {}", r.u16())
                amount_of_vert_bufs = p("    amount of vert bufs: {}", r.u16())

                # ^ should be amount_of_verts * vertex_data_stride

                mesh_vert_positions = []
                mesh_vert_normals = []
                mesh_vert_colors = []
                mesh_vert_texcoords = []

                old_offset = r.offset

                this_mesh_verts = []
                per_vert_data = {}

                for l_2 in range(amount_of_vert_bufs):
                    if l_2 > 0:
                        r.offset += 1
                    this_buf_size = r.i32()
                    p("    vert buf #{} size (bytes): {}", l_2, this_buf_size)
                    for l in range(amount_of_verts):
                        this_stride = 0

                        vert_pos = r.read("3f")
                        vert_pos = from_thug_coords(vert_pos)
                        this_stride += 12

                        new_vert = bm.verts.new(vert_pos)
                        per_vert_data[new_vert] = {}
                        this_mesh_verts.append(new_vert)

                        if sec_flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
                            packed_weights = r.u32()
                            vert_weights = (
                                (packed_weights & 0x7FF) / 1023.0,
                                ((packed_weights >> 11) & 0x7FF) / 1023.0,
                                ((packed_weights >> 22) & 0x3FF) / 511.0,
                                0.0
                            )

                            bone_indices = r.read("4H")
                            vertex_weights[new_vert] = (vert_weights, bone_indices)
                            this_stride += 12
                            if sec_flags & SECFLAGS_HAS_VERTEX_NORMALS:
                                packed_normal = r.u32()
                                if (not operator) or operator.import_custom_normals:
                                    vertex_normal = [
                                        (packed_normal & 0x7FF) / 1023.0,
                                        ((packed_normal >> 11) & 0x7FF) / 1023.0,
                                        ((packed_normal >> 22) & 0x3FF) / 511.0
                                    ]
                                    if vertex_normal[0] > 1.0: vertex_normal[0] = -(2.0 - vertex_normal[0])
                                    if vertex_normal[1] > 1.0: vertex_normal[1] = -(2.0 - vertex_normal[1])
                                    if vertex_normal[2] > 1.0: vertex_normal[2] = -(2.0 - vertex_normal[2])
                                    vertex_normals[new_vert] = from_thug_coords(vertex_normal) # (vertex_normal[0], vertex_normal[1], vertex_normal[2])
                                this_stride += 4
                        elif sec_flags & SECFLAGS_HAS_VERTEX_NORMALS:
                            vertex_normal = r.read("3f")
                            if (not operator) or operator.import_custom_normals:
                                vertex_normals[new_vert] = from_thug_coords(vertex_normal)
                            this_stride += 12

                        if sec_flags & SECFLAGS_HAS_VERTEX_COLORS:
                            per_vert_data[new_vert]["color"] = r.read("4B")
                            this_stride += 4

                        if sec_flags & SECFLAGS_HAS_TEXCOORDS:
                            if True: # num_tc_sets:
                                texcoords_to_read = (vertex_data_stride - this_stride) // 8
                                for m in range(texcoords_to_read):
                                    texcoords = r.read("2f")
                                    per_vert_data[new_vert].setdefault("uvs", []).append(texcoords)
                                    if write_sector_to_obj and m == 0:
                                        outf.write("vt {:f} {:f}\n".format(
                                            texcoords[0],
                                            texcoords[1]))

                if True or k == 0:
                    # bm.verts.ensure_lookup_table()
                    inds = the_indices_for_this_lod_level2
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
                                        loop[color_layer] = (cr / 128.0, cg / 128.0, cb / 128.0)
                                        loop[alpha_layer] = (ca / 128.0, ca / 128.0, ca / 128.0)

                p("    offset difference: {}", r.offset - old_offset)

                vertex_shader1 = r.i32()
                p("    vertex_shader1: {} ({})", vertex_shader1, hex(vertex_shader1))
                vertex_shader2 = r.i32()
                p("    vertex_shader2: {} ({})", vertex_shader2, hex(vertex_shader2))
                p("    stuff: {}", list(map(hex, r.read("3B"))))
                has_vc_wibble_data = r.read("B")[0]
                p("    has vc wibble data?: {} ({})", has_vc_wibble_data, hex(has_vc_wibble_data))

                if has_vc_wibble_data:
                    r.offset += amount_of_verts

                p("    num index sets?: {}", r.i32())

                pixel_shader = p("    pixel shader: {}", r.i32())
                if pixel_shader == 1:
                    p("    pixel shader thing #1: {}", r.i32())
                    r.read(str(p("    pixel shader thing #2: {}", r.i32())) + "B")

        bm.verts.index_update()
        bm.to_mesh(blender_mesh)

        if vertex_weights:
            vgs = blender_object.vertex_groups
            for vert, (weights, bone_indices) in vertex_weights.items():
                for weight, bone_index in zip(weights, bone_indices):
                    vert_group = vgs.get(str(bone_index//3)) or vgs.new(str(bone_index//3))
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


        if write_sector_to_obj:
            vert_position_index_offset += num_vertices
            if sec_flags & SECFLAGS_HAS_TEXCOORDS:
                vert_texcoord_index_offset += num_vertices

        new_objects.append(blender_object)
    p("number of hierarchy objects: {}", r.i32())
    return new_objects

# OPERATORS
#############################################
class THUG2ScnToScene(bpy.types.Operator):
    bl_idname = "io.thug2_xbx_scn_to_scene"
    bl_label = "THUG2 Scene (.scn.xbx/.skin.xbx/.mdl.xbx)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.skin.xbx;*.scn.xbx;*.mdl.xbx", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    load_tex = BoolProperty(name="Load the tex file", default=True)
    import_custom_normals = BoolProperty(name="Import custom normals", default=True)

    def execute(self, context):
        filename = self.filename
        directory = self.directory

        if self.load_tex:
            import os, re
            tex_filename = re.sub(r'\.(scn|skin|mdl)\.', '.tex.', filename, flags=re.IGNORECASE)
            tex_path = os.path.join(directory, tex_filename)
            if tex_filename != filename and os.path.exists(tex_path):
                bpy.ops.io.thug2_tex("EXEC_DEFAULT", filename=tex_filename, directory=directory)

        import_scn_ug2(filename, directory, context, self)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

#----------------------------------------------------------------------------------
class THUG2ColToScene(bpy.types.Operator):
    bl_idname = "io.thug_xbx_col_to_scene"
    bl_label = "THUG1/2 Collision (.col.xbx)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.col.xbx;*.col", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")

    def execute(self, context):
        filename = self.filename
        directory = self.directory

        import_col(filename, directory)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
