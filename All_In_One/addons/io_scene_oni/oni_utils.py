import struct

class Object(object):
    pass

def readBytes(f, size):
    if size == 1:
        return f.read(1)
    bar = bytearray(f.read(size))
    bar.reverse()
    return bar

def readInt(f):
    return struct.unpack('i', f.read(4))[0]

def readInt8(f):
    return struct.unpack('B', f.read(1))[0]

def readShort(f):
    return struct.unpack('h', f.read(2))[0]
def readUShort(f):
    return struct.unpack('H', f.read(2))[0]

def readFloat(f):
    return struct.unpack('f', f.read(4))[0]

def readString(f, size):
    bar = bytearray(f.read(size))
    bar.reverse()
    return bar.decode('utf-8')

def readCString(f):
    bytes = bytearray()
    byte = f.read(1)
    while byte != b"\x00":
        bytes += byte
        byte = f.read(1)
    return bytes.decode('utf-8')

def readArray(f, ftype, size):
    array = []
    for i in range(size):
        array.append(readField(f, ftype))
    return array

def readField(f, ftype):    
    if isinstance(ftype, list):
        return readFields(f, Object(), ftype)

    isArray = False
    size = 1
    
    idx = ftype.find('[')    
    if idx != -1:
        size = int(ftype[idx+1 : ftype.find(']')])
        ftype = ftype[0:idx]
        isArray = True

    if ftype == 'char' : 
        return readString(f, size)
    elif ftype == 'byte' : 
        return readBytes(f, size)

    if isArray:
        return readArray(f, ftype, size)
    else:
        if ftype == 'int' : 
            return readInt(f)
        elif ftype == 'int8' : 
            return readInt8(f)
        elif ftype == 'short' : 
            return readShort(f)
        elif ftype == 'float' : 
            return readFloat(f)

def readFields(f, obj, fields):
    for x in fields:
        fname = x[0]
        ftype = x[1]
        #print('reading ' + str(x))
        
        if len(x) == 3:  
            size = x[2]
            if not isinstance(size, int):
                size = getattr(obj, size)   
            setattr(obj, fname, readArray(f, ftype, size)) 
        else:
            try:
                setattr(obj, fname, readField(f, ftype))
            except:
                print(fname + ' : ' + ftype)
                raise
        #print(' = ' + str(getattr(obj, fname) ))
    return obj
