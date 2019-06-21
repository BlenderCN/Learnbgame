import struct

DEFAULT_ENCODING = "EUC-KR"

def list_2d(width, length, default=None):
    """ Create a 2-dimensional list of width x length """
    return [[default] * width for i in range(length)]

class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vector2({},{})".format(self.x, self.y)

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "Vector3({},{},{}".format(self.x, self.y, self.z)

class Color3:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b
    
    def __repr__(self):
        return "Color({},{},{},{})".format(self.r, self.g, self.b)

class Color4:
    def __init__(self, r=0, g=0, b=0, a=0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __repr__(self):
        return "Color({},{},{},{})".format(self.r, self.g, self.b, self.a)

#-- Signed integers
def read_i8(f):
    return struct.unpack("<b", f.read(1))[0]

def read_i16(f):
    return struct.unpack("<h", f.read(2))[0]

def read_i32(f):
    return struct.unpack("<i", f.read(4))[0]

def read_i64(f):
    return struct.unpack("<q", f.read(8))[0]

#-- Unsigned integers
def read_u8(f):
    return struct.unpack("<B", f.read(1))[0]

def read_u16(f):
    return struct.unpack("<H", f.read(2))[0]

def read_u32(f):
    return struct.unpack("<I", f.read(4))[0]

def read_u64(f):
    return struct.unpack("<Q", f.read(8))[0]

#-- Floats
def read_f32(f):
    return struct.unpack("<f", f.read(4))[0]

def read_f64(f):
    return struct.unpack("<d", f.read(8))[0]

#-- Strings
def read_bstr(f, encoding=DEFAULT_ENCODING):
    """ Read byte-prefixed string """
    size = struct.unpack("B", f.read(1))[0]
    if size == 0:
        return ""

    bstring = f.read(size)
    return bstring.decode(encoding)

def read_str(f, encoding=DEFAULT_ENCODING):
    """ Read null-terminated string """
    bstring = bytes("", encoding=encoding)
    while True:
        byte = f.read(1)
        if byte == b"\x00":
            break
        else:
            bstring += byte
    return bstring.decode(encoding)

#-- Misc
def read_bool(f):
    return struct.unpack("?", f.read(1))[0]

def read_color3(f):
    r = read_f32(f)
    g = read_f32(f)
    b = read_f32(f)
    return Color3(r,g,b)

def read_color4(f):
    r = read_f32(f)
    g = read_f32(f)
    b = read_f32(f)
    a = read_f32(f)
    return Color4(r,g,b,a)

def read_list_i16(f, n):
    a = []
    for i in range(n):
        a.append(read_i16(f))
    return a

def read_list_f32(f, n):
    a = []
    for i in range(n):
        a.append(read_f32(f))
    return a

def read_vector2_f32(f):
    x = read_f32(f)
    y = read_f32(f)
    return Vector2(x, y)

def read_vector3_i16(f):
    x = read_i16(f)
    y = read_i16(f)
    z = read_i16(f)
    return Vector3(x, y, z)

def read_vector3_f32(f):
    x = read_f32(f)
    y = read_f32(f)
    z = read_f32(f)
    return Vector3(x, y, z)
