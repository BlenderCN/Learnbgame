import os.path
import re
import bpy
import bmesh
from bpy_extras.io_utils import axis_conversion
from .skyfallen import SFGeometry


def get_texture_name(path, mat_texname):
    texnames = []
    texnames.append(mat_texname)

    if mat_texname[-4:] == '.dds':
        texnames.append(mat_texname[:-4] + '_hi.dds')
        texnames.append(mat_texname[:-4] + '.dds')

    basename = os.path.basename(path)[:-4]
    texnames.append(basename + '_hi.dds')
    texnames.append(basename + '.dds')

    if basename[-6:] == '_model':
        texnames.append(basename[:-6] + '_tex_hi.dds')
        texnames.append(basename[:-6] + '_tex.dds')

    cmntexname = re.sub(r'_\d+$', '', basename)
    if cmntexname != basename:
        texnames.append(cmntexname + '_hi.dds')
        texnames.append(cmntexname + '.dds')

    # Validate list
    dirname = os.path.dirname(path)
    for texname in texnames:
        if os.path.isfile(os.path.join(dirname, texname)):
            return texname

    return ''


def load_texture(material, texname, dirname):
    tex = bpy.data.textures.new(name=texname, type='IMAGE')
    path = os.path.join(dirname, texname)
    try:
        tex.image = bpy.data.images.load(path)
    except:
        warning = 'Cannot load the texture {}'
        print(warning.format(path))
    else:
        info = 'The texture {} has been loaded'
        print(info.format(texname))
    mtex = material.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'


def find_bone_tail(sf_bones, bone_id):
    bone = sf_bones[bone_id]

    # Try to set tail by child head
    for sf_bone in sf_bones:
        if sf_bone.parent_id == bone_id:
            print('Warning: Fixed zero-length bone \'{}\' (by child)'.format(bone.name))
            return sf_bone.pos_start

    # Fallback: copy parent bone lenght
    parent = sf_bones[bone.parent_id]
    delta_x = parent.pos_end[0] - parent.pos_start[0]
    delta_y = parent.pos_end[1] - parent.pos_start[1]
    delta_z = parent.pos_end[2] - parent.pos_start[2]

    pos = bone.pos_start
    print('Warning: Fixed zero-length bone \'{}\' (by parent)'.format(bone.name))
    return (pos[0] + delta_x, pos[1] + delta_y, pos[2] + delta_z)



def read(file, context, operation):
    del context

    amt = bpy.data.armatures.new('Skeleton')
    root_name = os.path.basename(operation.filepath)
    root = bpy.data.objects.new(root_name, amt)
    root.matrix_world = axis_conversion(from_forward='Z', from_up='Y').to_4x4()
    bpy.context.scene.objects.link(root)

    sf_geom = SFGeometry(file)

    # Process materials
    materials = []
    for sf_mat in sf_geom.materials:
        material = bpy.data.materials.new(sf_mat.name)
        texname = get_texture_name(operation.filepath, sf_mat.texture)
        if texname:
            dirname = os.path.dirname(operation.filepath)
            load_texture(material, texname, dirname)
        materials.append(material)

    # Process Bones
    if sf_geom.bones:
        bpy.context.scene.objects.active = root
        bpy.ops.object.mode_set(mode='EDIT')

        for sf_bone in sf_geom.bones:
            bone = amt.edit_bones.new(sf_bone.name)
            bone.head = sf_bone.pos_start
            bone.tail = sf_bone.pos_end
            bone.use_deform = True

            if sf_bone.parent_id >= 0:
                bone.parent = amt.edit_bones[sf_bone.parent_id]

            if sf_bone.bs_range <= 0.01:
                bone.tail = find_bone_tail(sf_geom.bones, sf_bone.id)

        bpy.ops.object.mode_set(mode='OBJECT')

    for frag in sf_geom.fragments:
        name = sf_geom.materials[frag.mat_id].name
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        obj.parent = root
        bpy.context.scene.objects.link(obj)

        # Push material
        material = materials[frag.mat_id]
        obj.data.materials.append(material)

        # Push vertices and faces to mesh
        offset = frag.facees_offset
        length = frag.facees_length
        indices = sf_geom.get_indices(offset, length)

        b_mesh = bmesh.new()
        b_mesh.from_mesh(mesh)

        # Vertices
        tex_coords = []
        for i in indices:
            sf_vertex = sf_geom.vertices[i]
            vertex = b_mesh.verts.new()
            vertex.co = sf_vertex.pos
            vertex.normal = sf_vertex.normal
            tex_coords.append(sf_vertex.tex_uv)

        b_mesh.verts.ensure_lookup_table()
        b_mesh.verts.index_update()

        # Faces
        for i in range(offset, offset+length):
            ids = sf_geom.faces[i].get_mapped_indices(indices)
            idx_1 = b_mesh.verts[ids[0]]
            idx_2 = b_mesh.verts[ids[1]]
            idx_3 = b_mesh.verts[ids[2]]
            try:
                b_mesh.faces.new((idx_1, idx_2, idx_3))
            except:
                msg = 'Warning: Skipped face for \'{}\' ({})'
                print(msg.format(name, frag.mat_id))

        # Texture coordinates
        uv_layer = b_mesh.loops.layers.uv.new()
        for face in b_mesh.faces:
            for loop in face.loops:
                loop[uv_layer].uv = tex_coords[loop.vert.index]

        b_mesh.to_mesh(mesh)
        b_mesh.free()

        # Vertices weights and armature modifier
        if not sf_geom.bones:
            continue

        for vertex_id in range(len(indices)):
            index = indices[vertex_id]
            sf_vertex = sf_geom.vertices[index]

            for i in range(frag.vertex_bones):
                local_bone_id = sf_vertex.bones[i]
                weight = sf_vertex.weights[i]
                if local_bone_id >= 254 or weight <= 0:
                    continue

                bone_id = frag.bone_remap[local_bone_id]
                bone_name = sf_geom.bones[bone_id].name

                group = obj.vertex_groups.get(bone_name)
                if not group:
                    group = obj.vertex_groups.new(bone_name)

                group.add([vertex_id], weight, 'REPLACE')

        modifier = obj.modifiers.new(type="ARMATURE", name="Armature")
        modifier.object = root
        modifier.use_bone_envelopes = False
