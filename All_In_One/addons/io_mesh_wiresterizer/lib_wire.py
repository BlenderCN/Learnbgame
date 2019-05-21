import struct

class WireOptions:

    def __init__(self):
        self.version = -1
        self.header = False
        self.text_mode = False
        self.big_endian = False
        self.triangles = False
        self.indexing = False
        self.vertex_normals = False
        self.face_normals = False
        self.n_gons = False

    def uses_normals(self):
        return self.vertex_normals or self.face_normals

    def uses_quads(self):
        return not (self.triangles or self.n_gons)


class WireVec:

    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z


class WireVertex:

    def __init__(self):
        self.pos = WireVec()
        self.norm = WireVec()


class WireFace:

    def __init__(self):
        self.verts = []
        self.norm = WireVec()


# Binary util functions
def _add_endian(options, fmt):
    if options.big_endian:
        return '>' + fmt
    else:
        return '<' + fmt

def _pack_int(options, value):
    return struct.pack(_add_endian(options, 'i'), value)

def _pack_unsigned_int(options, value):
    return struct.pack(_add_endian(options, 'I'), value)

def _pack_float(options, value):
    return struct.pack(_add_endian(options, 'f'), value)


# Text header export
def _text_write_header_magic_code(_options, file_write):
    file_write('# Wiresterizer\n')

def _text_write_header_opts(options, file_write):
    file_write('# Version %d\n' % options.version)

    if options.triangles:
        file_write('# Triangles\n')
    if options.indexing:
        file_write('# Indexing\n')
    if options.vertex_normals:
        file_write('# Vertex normals\n')
    if options.face_normals:
        file_write('# Face normals\n')


# Binary header export
# WIRE in ASCII, 1464422981 in decimal
BIN_MAGIC_CODE_LITTLE_ENDIAN = 0x57495245
BIN_MAGIC_CODE_BIG_ENDIAN = 0x45524957

# First 8 bits
BIN_VERSION_MASK = 0xFF

# 9th bit
BIN_TRIANGLES_POS = 8
BIN_TRIANGLES_BIT = 1 << BIN_TRIANGLES_POS

# 10th bit
BIN_INDEXING_POS = 9
BIN_INDEXING_BIT = 1 << BIN_INDEXING_POS

# 11th bit
BIN_VERTEX_NORMALS_POS = 10
BIN_VERTEX_NORMALS_BIT = 1 << BIN_VERTEX_NORMALS_POS

# 12th bit
BIN_FACE_NORMALS_POS = 11
BIN_FACE_NORMALS_BIT = 1 << BIN_FACE_NORMALS_POS

# 13th bit
BIN_N_GONS_POS = 11
BIN_N_GONS_BIT = 1 << BIN_N_GONS_POS

# Another 19 bits are available for later additions to the header

def _bin_write_header_magic_code(options, file_write):
    file_write(_pack_unsigned_int(options, BIN_MAGIC_CODE_BIG_ENDIAN))

def _bin_write_header_opts(options, file_write):
    if options.version > BIN_VERSION_MASK or options.version < 0:
        raise Exception('Invalid format version')

    version = options.version
    triangles_bit = options.triangles << BIN_TRIANGLES_POS
    indexing_bit = options.indexing << BIN_INDEXING_POS
    vertex_normals_bit = options.vertex_normals << BIN_VERTEX_NORMALS_POS
    face_normals_bit = options.face_normals << BIN_FACE_NORMALS_POS
    n_gons_bit = options.n_gons << BIN_N_GONS_BIT

    header_word = version |             \
                  triangles_bit |       \
                  indexing_bit |        \
                  vertex_normals_bit |  \
                  face_normals_bit |    \
                  n_gons_bit

    file_write(_pack_unsigned_int(options, header_word))


# Text face export
def _text_write_face_start(options, file_write, face):
    file_write('f')
    if options.n_gons:
        file_write(' %d' % len(face.verts))

def _text_write_face_end(_options, file_write, _face):
    file_write('\n')

def _text_write_face_norm(_options, file_write, _face, norm):
    file_write(' %.4f %.4f %.4f' % (norm.x, norm.y, norm.z))

def _text_write_face_vert(_options, file_write, _face, vert):
    file_write(' %.6f %.6f %.6f' % (vert.pos.x, vert.pos.y, vert.pos.z))


# Binary face export
def _bin_write_face_start(options, file_write, face):
    if options.n_gons:
        file_write(_pack_float(options, len(face.verts)))

def _bin_write_face_end(_options, _file_write, _face):
    pass

def _bin_write_face_norm(options, file_write, _face, norm):
    file_write(_pack_float(options, norm.x))
    file_write(_pack_float(options, norm.y))
    file_write(_pack_float(options, norm.z))

def _bin_write_face_vert(options, file_write, _face, vert):
    file_write(_pack_float(options, vert.pos.x))
    file_write(_pack_float(options, vert.pos.y))
    file_write(_pack_float(options, vert.pos.z))


# High-level logic
def open_file(options, file_path):
    if options.text_mode:
        # Open file for UTF8 writing
        return open(file_path, "w", encoding="utf8", newline="\n")

    else:
        # Open file for binary writing
        return open(file_path, "wb")

def close_file(options, file):
    file.close()

def write_header(options, file_write):
    if options.text_mode:
        # Assign text functions
        write_header_magic_code = _text_write_header_magic_code
        write_header_opts = _text_write_header_opts

    else:
        # Assign binary functions
        write_header_magic_code = _bin_write_header_magic_code
        write_header_opts = _bin_write_header_opts

    # Write header
    if options.header:
        write_header_magic_code(options, file_write)
        write_header_opts(options, file_write)

def write_face(options, file_write, face):
    if options.text_mode:
        # Assign text functions
        write_face_start = _text_write_face_start
        write_face_end = _text_write_face_end
        write_face_norm = _text_write_face_norm
        write_face_vert = _text_write_face_vert

    else:
        # Assign binary functions
        write_face_start = _bin_write_face_start
        write_face_end = _bin_write_face_end
        write_face_norm = _bin_write_face_norm
        write_face_vert = _bin_write_face_vert

    write_face_start(options, file_write, face)

    if options.indexing:
        raise Exception('Indexed mode not yet supported')
    else:
        if options.face_normals:
            write_face_norm(options, file_write, face, face.norm)

        for vert in face.verts:
            write_face_vert(options, file_write, face, vert)

            if options.vertex_normals:
                raise Exception('Vertex normals not yet supported')

    write_face_end(options, file_write, face)
