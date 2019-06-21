
from .. import format_
from .. import read
from ... import types

try:
    from io_scene_xray import xray_io
except ImportError:
    pass


def children_l(data, visual):
    packed_reader = xray_io.PackedReader(data)
    children_count = packed_reader.getf('I')[0]
    for children_index in range(children_count):
        children = packed_reader.getf('I')[0]
        visual.children_l.append(children)


def bsphere(data, visual):
    packed_reader = xray_io.PackedReader(data)
    position = packed_reader.getf('3f')
    radius = packed_reader.getf('f')[0]


def vertices_container(data, visual):
    packed_reader = xray_io.PackedReader(data)

    vertices_buffer_index = packed_reader.getf('I')[0]
    vertices_buffer_offset = packed_reader.getf('I')[0]
    vertices_buffer_size = packed_reader.getf('I')[0]

    if not visual.gcontainer:
        visual.gcontainer = types.GeometryContainer()

    visual.gcontainer.vb_index = vertices_buffer_index
    visual.gcontainer.vb_offset = vertices_buffer_offset
    visual.gcontainer.vb_size = vertices_buffer_size


def indices_container(data, visual):
    packed_reader = xray_io.PackedReader(data)

    indices_buffer_index = packed_reader.getf('I')[0]
    indices_buffer_offset = packed_reader.getf('I')[0]
    indices_buffer_size = packed_reader.getf('I')[0]

    if not visual.gcontainer:
        visual.gcontainer = types.GeometryContainer()

    visual.gcontainer.ib_index = indices_buffer_index
    visual.gcontainer.ib_offset = indices_buffer_offset
    visual.gcontainer.ib_size = indices_buffer_size


def lod_data(data, visual):
    chunked_reader = xray_io.ChunkedReader(data)
    hoppe_chunks = format_.Chunks.Version3.Hoppe
    for chunk_id, chunk_data in chunked_reader:
        packed_reader = xray_io.PackedReader(chunk_data)
        if chunk_id == hoppe_chunks.HEADER:
            min_vertices = packed_reader.getf('I')[0]
            min_indices = packed_reader.getf('I')[0]
        elif chunk_id == hoppe_chunks.VERT_SPLITS:
            vert_splits_count = len(visual.vertices) - min_vertices
            vert_splits = []
            print(len(chunk_data), vert_splits_count * 4)
            for vertex_index in range(vert_splits_count):
                vertex = packed_reader.getf('H')[0]
                new_tris = packed_reader.getf('B')[0]
                fix_faces = packed_reader.getf('B')[0]
                vert_splits.append(fix_faces)
        elif chunk_id == hoppe_chunks.FIX_FACES:
            fix_faces_count = packed_reader.getf('I')[0]
            fix_faces = []
            for face_index in range(fix_faces_count):
                vertex_index = packed_reader.getf('H')[0]
                fix_faces.append(vertex_index)
        else:
            print('UNKNOWN HOPPE CHUNK', hex(chunk_id))

    m_ib0 = visual.indices
    fix_idx = 0
    active_vb_size = min_vertices
    p = 0
    end = len(visual.vertices) - min_vertices
    while p != end:
        end_idx = fix_idx + vert_splits[p]
        p += 1
        while fix_idx < end_idx:
            fix_face = fix_faces[fix_idx]
            m_ib0[fix_face] = active_vb_size
            fix_idx += 1
        active_vb_size += 1
    visual.indices = m_ib0


D3D_FVF_NORMAL = 0x010
D3D_FVF_DIFFUSE = 0x040    # quantized normal
D3D_FVF_TEXCOUNT_MASK = 0xf00
D3D_FVF_TEXCOUNT_SHIFT = 8
D3D_FVF_TEX1 = 0x100    # base texture
D3D_FVF_TEX2 = 0x200    # base texture + light map


def load_d3d7(visual, packed_reader, vertices_count, vertex_format):
    texture_coordinate_count = (vertex_format & D3D_FVF_TEXCOUNT_MASK) >> D3D_FVF_TEXCOUNT_SHIFT
    for vertex_index in range(vertices_count):
        location_x, location_y, location_z = packed_reader.getf('3f')
        visual.vertices.append((location_x, location_z, location_y))
        if vertex_format & D3D_FVF_NORMAL:
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            visual.normals.append((normal_x, normal_z, normal_y))
        if vertex_format & D3D_FVF_DIFFUSE:
            normal_x, normal_y, normal_z, skip = packed_reader.getf('4B')
        if (vertex_format & (D3D_FVF_TEX1 | D3D_FVF_TEX2)):
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))
        if (vertex_format & D3D_FVF_TEX2):
            lmap_coord_u, lmap_coord_v = packed_reader.getf('2f')
            visual.uvs.append((lmap_coord_u, 1 - lmap_coord_v))


def vertices(data, visual):
    packed_reader = xray_io.PackedReader(data)
    vertex_format = packed_reader.getf('I')[0]
    vertices_count = packed_reader.getf('I')[0]
    if vertex_format == 0x12071980:
        for vertex_index in range(vertices_count):
            location_x, location_y, location_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')
            influences = packed_reader.getf('I')[0]
            visual.vertices.append((location_x, location_z, location_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))
            visual.normals.append((normal_x, normal_z, normal_y))
    elif vertex_format == 0x240e3300:
        for vertex_index in range(vertices_count):
            bone_0 = packed_reader.getf('H')[0]
            bone_1 = packed_reader.getf('H')[0]
            location_x, location_y, location_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            tangent_x, tangent_y, tangent_z = packed_reader.getf('3f')
            binormal_x, binormal_y, binormal_z = packed_reader.getf('3f')
            influences = packed_reader.getf('f')[0]
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')
            visual.vertices.append((location_x, location_z, location_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))
            visual.normals.append((normal_x, normal_z, normal_y))
    else:
        load_d3d7(visual, packed_reader, vertices_count, vertex_format)


def bbox(data, visual):
    packed_reader = xray_io.PackedReader(data)
    bounding_box = packed_reader.getf('6f')


def texture_l(data, visual):
    packed_reader = xray_io.PackedReader(data)
    visual.texture_l = packed_reader.getf('I')[0]
    visual.shader_l = packed_reader.getf('I')[0]


def main(chunks, ogf=True, visual=None, child=False):
    chunks_ids = format_.Chunks.Version3
    for chunk_id, chunk_data in chunks.items():
        if chunk_id == format_.Chunks.HEADER:
            pass
        elif chunk_id == chunks_ids.TEXTURE:
            read.texture(chunk_data, visual)
        elif chunk_id == chunks_ids.TEXTURE_L:
            texture_l(chunk_data, visual)
        elif chunk_id == chunks_ids.BBOX:
            bbox(chunk_data, visual)
        elif chunk_id == chunks_ids.CHILDREN:
            chunked_reader_children = xray_io.ChunkedReader(chunk_data)
            for child_id, child_data in chunked_reader_children:
                chunked_reader = xray_io.ChunkedReader(child_data)
                chunks_children = {}
                for chunk_id_children, chunk_data_children in chunked_reader:
                    chunks_children[chunk_id_children] = chunk_data_children
                main(chunks_children, ogf=True, visual=visual, child=True)
        elif chunk_id == chunks_ids.VERTICES:
            vertices(chunk_data, visual)
        elif chunk_id == chunks_ids.INDICES:
            read.indices(chunk_data, visual)
        elif chunk_id == chunks_ids.LODDATA:
            lod_data(chunk_data, visual)
        elif chunk_id == chunks_ids.ICONTAINER:
            indices_container(chunk_data, visual)
        elif chunk_id == chunks_ids.VCONTAINER:
            vertices_container(chunk_data, visual)
        elif chunk_id == chunks_ids.BSPHERE:
            bsphere(chunk_data, visual)
        elif chunk_id == chunks_ids.CHILDREN_L:
            children_l(chunk_data, visual)
        elif chunk_id == chunks_ids.TREEDEF2:
            read.treedef2(chunk_data, visual)
        else:
            print(hex(chunk_id))
