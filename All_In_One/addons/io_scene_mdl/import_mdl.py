import os

import bpy
import bmesh

from .quake import mdl


def load(operator, context, filepath):
    if not mdl.is_mdlfile(filepath):
        # TODO: Error out
        return {'FINISHED'}

    mdl_file = mdl.Mdl.open(filepath)
    mdl_file.close()

    name = os.path.basename(filepath).split('.')[0]
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)

    ob.scale = mdl_file.scale
    ob.location = mdl_file.origin

    # Load skin and create a material
    first_skin = None

    for i in range(mdl_file.number_of_skins):
        image = mdl_file.image(i)
        img = bpy.data.images.new('skin%i' % i, image.width, image.height)
        pixels = list(map(lambda x: x / 255, image.pixels))

        img.pixels[:] = pixels
        img.update()
        img.pack(True)
        img.use_fake_user = True

        if not first_skin:
            first_skin = img

        tex = bpy.data.textures.new('skin%i' % i, 'IMAGE')
        tex.image = img

        mat = bpy.data.materials.new('skin%i' % i)
        mat.diffuse_color = 1,1,1

        tex_slot = mat.texture_slots.add()
        tex_slot.texture = tex
        tex_slot.texture_coords = 'UV'

        ob.data.materials.append(mat)

    # Create mesh data
    bm = bmesh.new()

    first_frame = mdl_file.frames[0] if mdl_file.frames[0].type == mdl.SINGLE else mdl_file.frames[0].frames[0]

    # Vertices
    for i, vertex in enumerate(first_frame.vertices):
        bvertex = bm.verts.new(vertex[:])
        bvertex.normal = mdl.vertex_normals[vertex.light_normal_index]

    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.new()

    # Triangles
    for triangle in mdl_file.triangles:
        face_verts = []
        face_uvs = []

        for vert_index in triangle.vertices:
            bvertex = bm.verts[vert_index]
            st_vertex = mdl_file.st_vertices[vert_index]
            s, t = st_vertex[:]

            if st_vertex.on_seam and not triangle.faces_front:
                s += mdl_file.skin_width / 2

            uv_coords = s / mdl_file.skin_width, 1 - t / mdl_file.skin_height

            face_verts.append(bvertex)
            face_uvs.append(uv_coords)

        try:
            # Mdl vertices are clockwise winding order
            face = bm.faces.new(reversed(face_verts))
            face.loops[0][uv_layer].uv = face_uvs[2]
            face.loops[1][uv_layer].uv = face_uvs[1]
            face.loops[2][uv_layer].uv = face_uvs[0]

        except ValueError:
            # Triangles are sometimes duplicated?
            pass

    bm.to_mesh(ob.data)
    bm.free()

    for texpoly in ob.data.uv_textures[0].data:
        texpoly.image = first_skin

    def add_shape_key(frame):
        """Helper function to create a shape key from an mdl.Frame"""

        shape_key = ob.shape_key_add(frame.name)
        shape_key.interpolation = 'KEY_LINEAR'
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        shape_layer = bm.verts.layers.shape[frame.name]

        for i, vertex in enumerate(frame.vertices):
            bm.verts[i][shape_layer] = vertex

        bm.to_mesh(ob.data)
        bm.free()

    # Create Shape Keys
    for frame in mdl_file.frames:
        if frame.type == mdl.SINGLE:
            add_shape_key(frame)

        elif frame.type == mdl.GROUP:
            for subframe in frame.frames:
                add_shape_key(subframe)


    ob.data.shape_keys.use_relative = False
    bpy.context.scene.objects.link(ob)

    return {'FINISHED'}
