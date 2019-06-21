#############################################
# THUG1 SCENE (.scn/.mdl/skin) IMPORT
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
def import_scn_ug1(filename, directory, context, operator):
    p = Printer()
    p.on = True
    input_file = os.path.join(directory, filename)
    with open(input_file, "rb") as inp:
        r = Reader(inp.read())

    _mat_version = r.u32()
    _mesh_version = r.u32()
    _vert_version = r.u32()

    num_materials = p("num materials: {}", r.u32())
    read_materials(r, p, num_materials, directory, operator)
    num_sectors = p("num sectors: {}", r.i32())
    read_sectors_ug1(r, p, num_sectors, context, operator)
    rename_imported_materials()
    
#----------------------------------------------------------------------------------
def read_sectors_ug1(reader, printer, num_sectors, context, operator=None, output_file=None):
    r = reader
    p = printer
    outf = output_file

    vert_position_index_offset = 1
    vert_texcoord_index_offset = 1
    new_objects = []
    #p.on = False

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
            #this_stride = 0

            vert_pos = r.read("3f")
            vert_pos = from_thug_coords(vert_pos)
            #this_stride += 12

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
                    if  (not operator) or operator.import_custom_normals:
                        vertex_normals[new_vert] = from_thug_coords(vertex_normal)
            else:
                for l in range(amount_of_verts):
                    new_vert = this_mesh_verts[l]
                    vertex_normal = r.read("3f")
                    if (not operator) or operator.import_custom_normals:
                        vertex_normals[new_vert] = from_thug_coords(vertex_normal)
                
        
        if sec_flags & SECFLAGS_HAS_VERTEX_WEIGHTS:
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                packed_weights = r.u32()
                vert_weights = (
                    (packed_weights & 0x7FF) / 1023.0,
                    ((packed_weights >> 11) & 0x7FF) / 1023.0,
                    ((packed_weights >> 22) & 0x3FF) / 511.0,
                    0.0
                )
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
                #this_stride += 4
                
                
        if sec_flags & SECFLAGS_HAS_VERTEX_COLOR_WIBBLES:
            for l in range(amount_of_verts):
                new_vert = this_mesh_verts[l]
                r.u8() # We can't import this data currently, so skip past 
                #this_stride += 4

        
                
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
                #num_indices_for_this_lod_level2 = r.u16()
                #p("    {}", "num indices for lod level #{} (2nd round?): {}".format(k, num_indices_for_this_lod_level2))
                #the_indices_for_this_lod_level2 = r.read(str(num_indices_for_this_lod_level2) + "H")
                #min_index = p("    min index: {}", min(*the_indices_for_this_lod_level2))
                #max_index = p("    max index: {}", max(*the_indices_for_this_lod_level2))

                #r.read("14x") # padding?

    
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
                                loop[color_layer] = (cr / 128.0, cg / 128.0, cb / 128.0)
                                loop[alpha_layer] = (ca / 128.0, ca / 128.0, ca / 128.0)
                                
        bm.verts.index_update()
        bm.to_mesh(blender_mesh)
        
        if vertex_weights:
            vgs = blender_object.vertex_groups
            for vert, (weights, bone_indices) in vertex_weights.items():
                for weight, bone_index in zip(weights, bone_indices):
                    vert_group = vgs.get(str(bone_index)) or vgs.new(str(bone_index))
                    #print("{:2s} {:3f}".format(vert_group.name, weight), end='; ')
                    vert_group.add([vert.index], weight, "ADD")
                #print()

        if vertex_normals:
            vertex_normals = { vert.index: normal for vert, normal in vertex_normals.items() }
            new_normals = []
            for l in blender_mesh.loops:
                new_normals.append(vertex_normals[l.vertex_index])
            blender_mesh.normals_split_custom_set(new_normals)
            blender_mesh.use_auto_smooth = True

        new_objects.append(blender_object)

    #p("number of hierarchy objects: {}", r.i32())
    #print("COMPLETE!")
    return new_objects

                

# OPERATORS
#############################################
class THUG1ScnToScene(bpy.types.Operator):
    bl_idname = "io.thug1_xbx_scn_to_scene"
    bl_label = "THUG1 Scene (.scn/.skin/.mdl)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.skin.xbx;*.scn.xbx;*.mdl.xbx;*.skin;*.scn;*.mdl", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    load_tex = BoolProperty(name="Load the tex file", default=True)
    import_custom_normals = BoolProperty(name="Import custom normals", default=True)

    def execute(self, context):
        filename = self.filename
        directory = self.directory

        if self.load_tex:
            import os, re
            tex_filename = re.sub(r'\.(scn|skin|mdl)', '.tex', filename, flags=re.IGNORECASE)
            tex_path = os.path.join(directory, tex_filename)
            if tex_filename != filename and os.path.exists(tex_path):
                bpy.ops.io.thug2_tex("EXEC_DEFAULT", filename=tex_filename, directory=directory)

        import_scn_ug1(filename, directory, context, self)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}
