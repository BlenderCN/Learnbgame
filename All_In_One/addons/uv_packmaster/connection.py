
import struct
import io
import time

from .utils import in_debug_mode

class UvPackMessageCode:
    PROGRESS_REPORT = 0
    INVALID_ISLANDS = 1
    VERSION = 2
    ISLAND_FLAGS = 3
    PACK_SOLUTION = 4
    AREA = 5
    INVALID_FACES = 6


def force_read_bytes(stream, bytes_cnt):
    output = bytes()

    while len(output) != bytes_cnt:
        buf = stream.read(bytes_cnt - len(output))

        if len(buf) == 0:
            raise RuntimeError('Not enough output from the packer')

        output += buf

    return output


def force_read_int(stream):
    buf = force_read_bytes(stream, 4)
    return struct.unpack('i', buf)[0]


def force_read_float(stream):
    buf = force_read_bytes(stream, 4)
    return struct.unpack('f', buf)[0]


def force_read_ints(stream, count):
    buf = force_read_bytes(stream, 4 * count)
    return struct.unpack('i' * count, buf)


def force_read_floats(stream, count):
    buf = force_read_bytes(stream, 4 * count)
    return struct.unpack('f' * count, buf)


def read_int_array(stream):
    count = force_read_int(stream)
    return force_read_ints(stream, count)


def prepare_raw_uv_topo_data(uv_island_faces_list, face_to_verts, island_materials = None):
    prepare_start = time.time()

    raw_uv_topo_data = bytes()
    raw_uv_topo_data += struct.pack('i', len(face_to_verts))
    face_id_len_array = []
    uv_coord_array = []
    vert_idx_array = []

    for face_id, vert_array in face_to_verts.items():
        face_id_len_array.append(face_id)
        face_id_len_array.append(len(vert_array))

        for vert_id in vert_array:
            uv_coord_array.append(vert_id[0][0])
            uv_coord_array.append(vert_id[0][1])
            vert_idx_array.append(vert_id[1])

    raw_uv_topo_data += struct.pack('i' * len(face_id_len_array), *face_id_len_array)
    raw_uv_topo_data += struct.pack('i', len(vert_idx_array))
    raw_uv_topo_data += struct.pack('f' * len(uv_coord_array), *uv_coord_array)
    raw_uv_topo_data += struct.pack('i' * len(vert_idx_array), *vert_idx_array)

    raw_uv_topo_data += struct.pack('i', len(uv_island_faces_list))

    islands_array = []
    for island_idx, island in enumerate(uv_island_faces_list):
        islands_array.append(len(island))
        islands_array.append(0 if island_materials is None else island_materials[island_idx])
        for face_id in island:
            islands_array.append(face_id)

    raw_uv_topo_data += struct.pack('i' * len(islands_array), *islands_array)

    if in_debug_mode():
        print('Topo data preparing time: ' + str(time.time() - prepare_start))

    return raw_uv_topo_data


def connection_rcv_message(stream):
    msg_size = force_read_int(stream)
    msg_bytes = force_read_bytes(stream, msg_size)
    return io.BytesIO(msg_bytes)


def connection_thread_func(stream, queue):
    try:
        while True:
            queue.put(connection_rcv_message(stream))
    except Exception as ex:
        # queue.put(str(ex))
        return