from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import time
import bpy

from collections import namedtuple
from bpy_extras.image_utils import load_image
from mathutils import Matrix, Vector

from .mpet import Mpet


# Attempts to find PangYa's texture_dds folder, containing DDS textures.
def find_parent_folder(dirname, folder):
    parent = os.path.dirname(dirname)
    texdir = os.path.join(dirname, folder)
    if os.path.exists(texdir):
        return texdir
    elif dirname != parent:
        return find_parent_folder(parent, folder)
    else:
        return None


def calc_bonemat(model, bone_id):
    bonemat = Matrix.Identity(4)
    boneptr = model.bones[bone_id]
    while True:
        m = boneptr.matrix
        bonemat = Matrix([
            [m[0], m[3], m[6], m[9]],
            [m[1], m[4], m[7], m[10]],
            [m[2], m[5], m[8], m[11]],
            [0, 0, 0, 1],
        ]) * bonemat
        if boneptr.parent == 255:
            break
        boneptr = model.bones[boneptr.parent]
    return bonemat


def load_mpet(scene, file, matrix):
    dirname = os.path.dirname(file.name)
    filename = os.path.basename(file.name)

    model = Mpet()
    model.load(file)

    materials = []

    # Make materials for each texture.
    for texture in model.textures:
        fn = texture.fn.decode('utf-8')
        tex = bpy.data.textures.new(fn, type='IMAGE')

        base, ext = os.path.splitext(fn)
        if ext == ".dds":
            tex.image = load_image(fn, find_parent_folder(dirname, 'texture_dds'))
        elif os.path.exists(os.path.join(dirname, fn)):
            tex.image = load_image(fn, dirname)
        else:
            tex.image = load_image(fn, find_parent_folder(dirname, 'z_common'))


        mat = bpy.data.materials.new(fn)
        mat.active_texture = tex
        mat.use_shadeless = True
        mat.use_transparency = True
        mat.alpha = 0.0 # Blender is weird
        mat.transparency_method = 'Z_TRANSPARENCY'

        mtex = mat.texture_slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'
        mtex.use_map_alpha = True

        materials.append(mat)

    # Armature
    armature = bpy.data.armatures.new(filename + " Armature")
    armature.draw_type = 'STICK' # Large bones otherwise make this a bit ridiculous.
    armature_obj = bpy.data.objects.new(filename + " Armature", armature)
    scene.objects.link(armature_obj)


    # Create bones.
    scene.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bbonemap = {}

    # Pass 1: Create bones
    for id, bone in enumerate(model.bones):
        name = bone.name.decode('utf-8')
        bbone = armature.edit_bones.new(name)
        armature.edit_bones.active = bbone

        bbone.use_deform = True
        bbone.use_connect = True
        bbone.use_inherit_rotation = True
        bbone.use_inherit_scale = True
        bbone.use_local_location = True

        bbonemap[id] = bbone

    # Pass 2: Assign parents
    for id, bone in enumerate(model.bones):
        bbone = bbonemap[id]
        armature.edit_bones.active = bbone

        bonemat = matrix * calc_bonemat(model, id)

        # todo: calculate roll?
        bbone.head = bonemat.to_translation()
        bbone.tail = bonemat.to_translation()
        bbone.roll = 0

        if bone.parent != 255:
            parent = bbonemap[bone.parent]
            bbone.parent = parent
            bbone.head = parent.tail

    bpy.ops.object.mode_set(mode='OBJECT')

    # Geometry!
    for mesh in model.meshes:
        bmesh = bpy.data.meshes.new(filename)
        obj = bpy.data.objects.new(filename, bmesh)

        # Flatten vertices down to [x,y,z,x,y,z...] array.
        verts = []
        for vert in mesh.vertices:
            vector = Vector([0, 0, 0, 0])
            vertpos = Vector([vert.x, vert.y, vert.z, 1])

            weight = vert.bone_weights[0]
            mat = calc_bonemat(model, weight.id)
            vector += mat * vertpos * (1.0 / 255 * weight.weight)

            verts.extend((
                (vector.x / vector.w),
                (vector.y / vector.w),
                (vector.z / vector.w),
            ))
        bmesh.vertices.add(len(mesh.vertices))
        bmesh.vertices.foreach_set("co", verts)

        # Polygons
        num_faces = len(mesh.polygons)
        bmesh.polygons.add(num_faces)
        bmesh.loops.add(num_faces * 3)
        faces = []
        for p in mesh.polygons:
            faces.extend((
                p.indices[0].index,
                p.indices[1].index,
                p.indices[2].index
            ))
        bmesh.polygons.foreach_set("loop_start", range(0, num_faces * 3, 3))
        bmesh.polygons.foreach_set("loop_total", (3,) * num_faces)
        bmesh.polygons.foreach_set("use_smooth", (True,) * num_faces)
        bmesh.loops.foreach_set("vertex_index", faces)

        # UV maps
        uvtex = bmesh.uv_textures.new()
        uvlayer = bmesh.uv_layers.active.data[:]
        for index, bpolygon in enumerate(bmesh.polygons):
            polygon = mesh.polygons[index]

            i = bpolygon.loop_start
            for index in polygon.indices:
                uvlayer[i].uv = index.u, 1.0 - index.v
                i += 1

        # Materials
        for material in materials:
            bmesh.materials.append(material)

        for index, material in enumerate(mesh.texmap):
            bmesh.polygons[index].material_index = material

        bmesh.validate()
        bmesh.update()

        # Vertex groups
        VertexWeight = namedtuple('VertexWeight', ['vertex', 'weight'])
        groups = {}

        # Translate weights into structure of groups.
        for id, vertex in enumerate(mesh.vertices):
            for weight in vertex.bone_weights:
                group = groups.get(weight.id, [])
                group.append(VertexWeight(id, 1.0 / 255 * weight.weight))
                groups[weight.id] = group

        # Load groups into Blender
        for id, weights in groups.items():
            group_name = model.bones[id].name.decode('utf-8')
            bgroup = obj.vertex_groups.new(group_name)
            for weight in weights:
                bgroup.add([weight.vertex], weight.weight, 'ADD')

        obj.matrix_world = obj.matrix_world * matrix
        scene.objects.link(obj)

        # Armature modifier
        bmodifier = obj.modifiers.new(armature.name, type='ARMATURE')
        bmodifier.show_expanded = False
        bmodifier.use_vertex_groups = True
        bmodifier.use_bone_envelopes = False
        bmodifier.object = armature_obj


def load(operator, context, filepath, matrix):
    time1 = time.clock()
    print('importing pangya model: %r' % (filepath))

    with open(filepath, 'rb') as file:
        load_mpet(context.scene, file, matrix)

    print('import done in %.4f sec.' % (time.clock() - time1))

    return {'FINISHED'}
