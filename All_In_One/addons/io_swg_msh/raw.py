import struct

##int16
def read_int16(f):
    return int.from_bytes(f.read(2), 'little', signed=True)

def read_uint16(f):
    return int.from_bytes(f.read(2), 'little')

def read_net_int16(f):
    return int.from_bytes(f.read(2), 'big', signed=True)

def read_net_uint16(f):
    return int.from_bytes(f.read(2), 'big')

##int32
def read_int32(f):
    return int.from_bytes(f.read(4), 'little', signed=True)

def read_uint32(f):
    return int.from_bytes(f.read(4), 'little')

def read_net_int32(f):
    return int.from_bytes(f.read(4), 'big', signed=True)

def read_net_uint32(f):
    return int.from_bytes(f.read(4), 'big')

##int 64
def read_int64(f):
    return int.from_bytes(f.read(8), 'little', signed=True)

def read_uint64(f):
    return int.from_bytes(f.read(8), 'little')

def read_net_int64(f):
    return int.from_bytes(f.read(8), 'big', signed=True)

def read_net_uint64(f):
    return int.from_bytes(f.read(8), 'big')

##float
def read_float(f):
    return struct.unpack('f', f.read(4))[0]

def read_string(f):
    out = bytearray()
    buf = f.read(1)
    while buf:
        out.append(buf)
        buf = f.read(1)
    return out.decode('ascii')
    