import os
import struct

import bpy
import bmesh
from mathutils import Matrix, Vector

from .quake2 import md2, pcx


def reload():
    """Reload any modules that may have changed"""
    import importlib
    importlib.reload(md2)

def load(operator, context, filepath):
    if not md2.is_md2file(filepath):
        operator.report(
            {'ERROR'},
            '{} is not a recognized MD2 file'.format(filepath)
        )
        return {'CANCELLED'}

    md2_file = md2.Md2.open(filepath)
    md2_file.close

    # Images
    for skin in md2_file.skins:
        image_file = os.path.basename(skin)
        image_path = os.path.dirname(filepath)
        image_path = os.path.join(image_path, image_file)
        with open(image_path, 'rb') as file:
            image = pcx.Pcx.read(file)

        format = '<{}B'.format(len(image.pixels))
        pixels = struct.unpack(format, image.pixels)
        palette = tuple(struct.iter_unpack('<BBB', image.palette))
        palette = [(p[0] / 255, p[1]/ 255, p[2] / 255, 1) for p in palette]

        pixels = [r for p in pixels for r in palette[p]]

        bimage = bpy.data.images.new('skin', image.width, image.height)
        bimage.pixels = pixels
        #bimage.pack = True
        #bimage.use_fake_user = True

    # Meshes
    me = bpy.data.meshes.new('mesh')
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    w, h = md2_file.skin_width, md2_file.skin_height

    def st_to_uv(st_vertex):
        s, t = st_vertex[:]
        return s / w, 1 - (t / h)

    frame = md2_file.frames[0]
    sx, sy, sz = frame.scale
    tx, ty, tz = frame.translate

    frame_matrix = Matrix([
        [sx,  0,  0, tx],
        [ 0, sy,  0, ty],
        [ 0,  0, sz, tz],
        [ 0,  0,  0,  1]
    ])

    # Vertices
    for vertex in frame.vertexes:
        v0 = bm.verts.new(vertex[:])
        v0.co = frame_matrix * v0.co

    bm.verts.ensure_lookup_table()

    # Triangles
    for triangle in md2_file.triangles:
        vertexes = [bm.verts[i] for i in reversed(triangle.vertexes)]
        try:
            # TODO: Blender raises a face already exists exception, but from
            # what I can tell this is not correct.
            # monsters/berserk is a good use case
            print('processing triangle: {}'.format(md2_file.triangles.index(triangle)))
            print('   vertexes: {}'.format(tuple(reversed(triangle.vertexes))))
            face = bm.faces.new(vertexes)
        except ValueError as ve:
            print(ve)

        st_vertexes = [md2_file.st_vertexes[i] for i in reversed(triangle.st_vertexes)]
        uv_coords = list(map(st_to_uv, st_vertexes[:]))

        for loop, uv in zip(face.loops, uv_coords):
            loop[uv_layer].uv = uv

    bm.faces.ensure_lookup_table()
    object_name = os.path.basename(os.path.dirname(filepath))
    ob = bpy.data.objects.new(object_name, me)
    bm.to_mesh(me)
    bm.free()

    # Frames
    for frame in md2_file.frames:
        shape_key = ob.shape_key_add(frame.name)
        shape_key.interpolation = 'KEY_LINEAR'
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()

        shape_layer = bm.verts.layers.shape[frame.name]

        sx, sy, sz = frame.scale
        tx, ty, tz = frame.translate

        frame_matrix = Matrix([
            [sx, 0, 0, tx],
            [0, sy, 0, ty],
            [0, 0, sz, tz],
            [0, 0, 0, 1]
        ])

        for bvert, frame_vert in zip(bm.verts, frame.vertexes):
            bvert[shape_layer][:] = frame_matrix * Vector(frame_vert[:])

        bm.to_mesh(ob.data)
        bm.free()

    ob.data.shape_keys.use_relative = False
    bpy.context.scene.objects.link(ob)

    return {'FINISHED'}