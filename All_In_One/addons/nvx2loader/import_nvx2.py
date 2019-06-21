"""TODO: DOC"""

import os
import struct

import bpy
import bpy_extras
from bpy_extras.io_utils import unpack_list
from bpy_extras.io_utils import unpack_face_list

from . import nvx2


def fps2float(n):
    '''Convert fixed point short into a float'''
    return float(n) / 8191.0


def fpb2float(n):
    '''Convert fixed point byte into a float'''
    return float(n) / 255.0


def make_vertexformat(vertex_components):
    '''Build the struct format string to read vertices'''
    vertex_fmt = '<'
    for vcmask, vcdata in nvx2.VertexComponents.items():
        if vcmask & vertex_components:
            vertex_fmt += vcdata.format
    return vertex_fmt


def unpack_vertexdata(vertices, vertex_components):
    """TODO:Doc."""
    vertex_coords = []
    uv_layers = [[], [], [], []]
    offset = 0

    vcmask = nvx2.VertexComponentMask.Coord
    if vcmask & vertex_components:
        vertex_coords = [(v[offset+0], v[offset+1], v[offset+2])
                         for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Normal
    if vcmask & vertex_components:
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.NormalUB4N
    if vcmask & vertex_components:
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv0
    if vcmask & vertex_components:
        uv_layers[0] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv0S2
    if vcmask & vertex_components:
        uv_layers[0] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv1
    if vcmask & vertex_components:
        uv_layers[1] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv1S2
    if vcmask & vertex_components:
        uv_layers[1] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv2
    if vcmask & vertex_components:
        uv_layers[2] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv2S2
    if vcmask & vertex_components:
        uv_layers[2] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv3
    if vcmask & vertex_components:
        uv_layers[3] = [(v[offset+0], v[offset+1]) for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count
    vcmask = nvx2.VertexComponentMask.Uv3S2
    if vcmask & vertex_components:
        uv_layers[3] = [(fps2float(v[offset+0]), 1-fps2float(v[offset+1]))
                        for v in vertices]
        offset += nvx2.VertexComponents[vcmask].count

    return vertex_coords, uv_layers


def create_image(img_name, img_search=False):
    """TODO:Doc."""
    img_path = ''
    img = bpy_extras.image_utils.load_image(img_name + '.dds',
                                            img_path,
                                            recursive=img_search,
                                            place_holder=False,
                                            ncase_cmp=True)
    if (img is None):
        print('WARNING: Could not load image ' + img_name)
        img = bpy.data.images.new(img_name, 512, 512)
    else:
        img.name = img_name
    return img


def create_material(material_name):
    """TODO:Doc."""
    material = bpy.data.materials.new(material_name)
    # Add texture
    textureSlot = material.texture_slots.add()
    textureSlot.texture = bpy.data.textures.new(material.name, type='IMAGE')
    img = create_image(material.name)
    if img is not None:
        textureSlot.texture.image = img
    textureSlot.texture_coords = 'UV'
    textureSlot.use_map_color_diffuse = True
    return material


def create_mesh(nvx2_vertices, nvx2_faces, nvx2_uvlayers):
    """TODO:Doc."""
    me = bpy.data.meshes.new('nvx2_mesh')
    # Add vertices
    me.vertices.add(len(nvx2_vertices))
    me.vertices.foreach_set('co', unpack_list(nvx2_vertices))
    # Add faces
    me.tessfaces.add(len(nvx2_faces))
    # TODO: eekadoodle fix
    me.tessfaces.foreach_set('vertices_raw', unpack_face_list(nvx2_faces))
    # Add texture coordinates
    material = create_material('nvx2_material')
    me.materials.append(material)
    uv_data = nvx2_uvlayers[0]
    if (len(uv_data) > 0):
        uv = me.tessface_uv_textures.new('nvx2_uv')
        me.tessface_uv_textures.active = uv
        for i in range(len(nvx2_faces)):
            tessface = me.tessfaces[i]
            tessface.material_index = 0
            tessfaceUV = me.tessface_uv_textures[0].data[i]
            face = nvx2_faces[i]
            # BEGIN EEEKADOODLE FIX
            # BUG: Evil eekadoodle problem where faces that have
            # vert index 0 at location 3 are shuffled.
            if face[2] == 0:
                face = [face[1], face[2], face[0]]
            # END EEEKADOODLE FIX
            tessfaceUV.uv1 = uv_data[face[0]]
            tessfaceUV.uv2 = uv_data[face[1]]
            tessfaceUV.uv3 = uv_data[face[2]]
            # Apply texture to uv face
            tessfaceUV.image = material.texture_slots[0].texture.image
        """
        me.uv_textures.new('nvx2_uv')
        uv_layer = me.uv_layers[-1].data
        vert_loops = {}
        for l in me.loops:
            vert_loops.setdefault(l.vertex_index, []).append(l.index)
        for i, coord in enumerate(uv_data):
            # For every loop of a vertex
            for li in vert_loops[i]:
                uv_layer[li].uv = coord
        """
        """
        vi_uv = {i: uv for i, uv in enumerate(uv_coords)}
        per_loop_list = [0.0] * len(me.loops)
        for loop in me.loops:
            per_loop_list[loop.index] = vi_uv.get(loop.vertex_index)
        per_loop_list = [uv for pair in per_loop_list for uv in pair]
        me.uv_textures.new('nvx2_uv')
        me.uv_layers[-1].data.foreach_set("uv", per_loop_list)
        """
    me.update()
    return me


def load(context,
         filepath='',
         create_parent_empty=True,
         single_material=False,
         use_image_search=False):
    """Called by the user interface or another script."""
    with open(filepath, mode='rb') as f:
        filename = os.path.splitext(os.path.split(filepath)[1])[0]
        scene = bpy.context.scene
        # Read header
        header = nvx2.Header._make(struct.unpack('<4s6i', f.read(28)))
        vertex_fmt = make_vertexformat(header.vertex_components)
        vertex_size = struct.calcsize(vertex_fmt)
        if (vertex_size != header.vertex_width * 4):
            return {'CANCELLED'}
        # Read groups = objects
        nvx2_groups = [nvx2.Group._make(struct.unpack('<6i', f.read(24)))
                       for i in range(header.num_groups)]
        # Geometry data
        vertex_data = [struct.unpack(vertex_fmt, f.read(vertex_size))
                       for i in range(header.num_vertices)]
        nvx2_vertices, nvx2_uvlayers = \
            unpack_vertexdata(vertex_data, header.vertex_components)
        nvx2_faces = [list(struct.unpack('<3H', f.read(6)))
                      for i in range(header.num_triangles)]
        # Create objects
        parent_empty = None
        if create_parent_empty:
            parent_empty = bpy.data.objects.new(filename, None)
            parent_empty.location = (0.0, 0.0, 0.0)
            scene.objects.link(parent_empty)
        for g in nvx2_groups:
            gvf = g.vertex_first
            gtf = g.triangle_first
            gtc = g.triangle_count
            # Adjust face vertex indices
            adj_faces = [[vid-gvf for vid in f]
                         for f in nvx2_faces[gtf:gtf+gtc]]
            adj_verts = nvx2_vertices[gvf:gvf+g.vertex_count]
            adj_uvs = [uvl[gvf:gvf+g.vertex_count] for uvl in nvx2_uvlayers]
            mesh = create_mesh(adj_verts, adj_faces, adj_uvs)
            obj = bpy.data.objects.new('nvx2_object', mesh)
            if parent_empty:
                obj.parent = parent_empty
            scene.objects.link(obj)

    return {'FINISHED'}
