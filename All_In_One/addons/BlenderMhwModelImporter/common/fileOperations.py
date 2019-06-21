import binascii
import os
import struct
from io import BytesIO
from struct import pack,unpack
from os import SEEK_SET,SEEK_CUR,SEEK_END
from ..dbg import dbg,CREATE_FILE_SNAPSHOTS,SNAPSHOT_FMT
C8S = 0.0078125
SNAPSHOT_ID = 0
pos = {}
contentStreams = []
def getContentStreamValue(fl):
    return contentStreams[fl].getvalue()
def createContentStream(content):
    global contentStreams
    contentStreams.append(BytesIO(content))
    return len(contentStreams)-1
def ReadSByte(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("b",contentStream.read(1))[0]
    pos[fl]+=1
    return res
def ReadByte(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("B",contentStream.read(1))[0]
    pos[fl]+=1
    return res
def ReadBytes(fl,ln):
    global pos,contentStreams
    dbg("ReadBytes %08x %d" % (pos[fl],ln))
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("%dB" % ln,contentStream.read(ln))
    pos[fl]+=ln
    return res
def ReadLong(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("L",contentStream.read(4))[0]
    pos[fl]+=4
    return res
def ReadShort(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("H",contentStream.read(2))[0]
    pos[fl]+=2
    return res
def ReadBELong(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack(">I",contentStream.read(4))[0]
    pos[fl]+=4
    return res
def ReadBEShort(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack(">H",contentStream.read(2))[0]
    pos[fl]+=2
    return res
    
#copied this code from http://davidejones.com/blog/1413-python-precision-floating-point/
def _wrhf(float32):
    F16_EXPONENT_BITS = 0x1F
    F16_EXPONENT_SHIFT = 10
    F16_EXPONENT_BIAS = 15
    F16_MANTISSA_BITS = 0x3ff
    F16_MANTISSA_SHIFT =  (23 - F16_EXPONENT_SHIFT)
    F16_MAX_EXPONENT =  (F16_EXPONENT_BITS << F16_EXPONENT_SHIFT)

    a = pack('>f',float32)
    b = binascii.hexlify(a)

    f32 = int(b,16)
    f16 = 0
    sign = (f32 >> 16) & 0x8000
    exponent = ((f32 >> 23) & 0xff) - 127
    mantissa = f32 & 0x007fffff
            
    if exponent == 128:
        f16 = sign | F16_MAX_EXPONENT
        if mantissa:
            f16 |= (mantissa & F16_MANTISSA_BITS)
    elif exponent > 15:
        f16 = sign | F16_MAX_EXPONENT
    elif exponent > -15:
        exponent += F16_EXPONENT_BIAS
        mantissa >>= F16_MANTISSA_SHIFT
        f16 = sign | exponent << F16_EXPONENT_SHIFT | mantissa
    else:
        f16 = sign
    return f16
def _rdhf(float16):
        s = int((float16 >> 15) & 0x00000001)    # sign
        e = int((float16 >> 10) & 0x0000001f)    # exponent
        f = int(float16 & 0x000003ff)            # fraction

        if e == 0:
            if f == 0:
                return int(s << 31)
            else:
                while not (f & 0x00000400):
                    f = f << 1
                    e -= 1
                e += 1
                f &= ~0x00000400
                #print(s,e,f)
        elif e == 31:
            if f == 0:
                return int((s << 31) | 0x7f800000)
            else:
                return int((s << 31) | 0x7f800000 | (f << 13))

        e = e + (127 -15)
        f = f << 13
        return unpack('f',pack('I',int((s << 31) | (e << 23) | f)))[0]

def Read8s(fl):
    return ReadSByte(fl)*C8S
def ReadHalfFloat(fl):
    s = ReadShort(fl)
    res = _rdhf(s)
    #dbg("S: %08x R: %f" % (s,res))
    return res
def ReadFloat(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("f",contentStream.read(4))[0]
    pos[fl]+=4
    return res
def ReadBEFloat(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack(">f",contentStream.read(4))[0]
    pos[fl]+=4
    return res
def ReadPointer(fl,size):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    if(size==64):
        contentStream.seek(pos[fl])
        res = unpack("Q",contentStream.read(8))[0]
        pos[fl]+=8
        return res
    return None
    
def ReadBEVector3(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack(">fff",contentStream.read(4*3))
    pos[fl]+=4*3
    return list(res)
def ReadVector3(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("fff",contentStream.read(4*3))
    pos[fl]+=4*3
    return list(res)
    
def ReadBEVector4(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack(">ffff",contentStream.read(4*4))
    pos[fl]+=4*4
    return list(res)
def ReadVector4(fl):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("ffff",contentStream.read(4*4))
    pos[fl]+=4*4
    return list(res)
def ReadString(fl,length):
    global pos,contentStreams
    contentStream = contentStreams[fl]
    contentStream.seek(pos[fl])
    res = unpack("%ds"%length,contentStream.read(length))[0].decode("utf-8").replace("\x00","")
    pos[fl]+=length
    return res
    

def WriteHalfFloats(fl,floats32):
    global pos,contentStreams
    if(len(floats32) == 0):
        return
    contentStream = contentStreams[fl]
    p = b''
    for f in floats32:
        f16 = _wrhf(f)
        p += pack("<H",f16)
    contentStream.seek(pos[fl])
    contentStream.write(p)
    pos[fl] += 2*len(floats32)
def WriteFloats(fl,floats):
    global pos,contentStreams
    if(len(floats) == 0):
        return
    contentStream = contentStreams[fl]
    #dbg("WriteFloats at 0x%08x %s" % (pos[fl],floats))
    if pos[fl]==0:
        raise Exception("Invalid write position")
    p = pack("%df" % len(floats),*floats)
    contentStream.seek(pos[fl])
    contentStream.write(p)
    pos[fl] += len(floats)*4
def WriteBytes(fl,bytes):
    global pos,contentStreams
    if(len(bytes) == 0):
        return
    contentStream = contentStreams[fl]
    #dbg("WriteBytes at 0x%08x %s" % (pos[fl],bytes))
    if pos[fl]==0:
        raise Exception("Invalid write position")
    p = pack("%dB" % len(bytes),*bytes)
    contentStream.seek(pos[fl])
    contentStream.write(p)
    pos[fl] += len(bytes)
def WriteSBytes(fl,bytes):
    global pos,contentStreams
    if(len(bytes) == 0):
        return
    contentStream = contentStreams[fl]
    #dbg("WriteBytes at 0x%08x %s" % (pos[fl],bytes))
    if pos[fl]==0:
        raise Exception("Invalid write position")
    p = pack("%db" % len(bytes),*bytes)
    contentStream.seek(pos[fl])
    contentStream.write(p)
    pos[fl] += len(bytes)
def Write8s(fl,floats):
    global pos,contentStreams
    if(len(floats) == 0):
        return
    #contentStream = contentStreams[fl]
    #dbg("WriteBytes at 0x%08x %s" % (pos[fl],bytes))
    if pos[fl]==0:
        raise Exception("Invalid write position")
    floats = list(floats)
    for i in range(0,len(floats)):
        floats[i] = int(floats[i] / C8S)
        if floats[i]>127:
            floats[i] = 127
        if floats[i]<-128:
            floats[i] = -128
    WriteSBytes(fl,floats)
def WriteShorts(fl,shorts):
    global pos,contentStreams
    if(len(shorts) == 0):
        return
    contentStream = contentStreams[fl]
    if pos[fl]==0:
        raise Exception("Invalid write position")
    try:
        p = pack("%dH" % len(shorts),*shorts)
    except struct.error as e:
        dbg(shorts)
        raise e
    contentStream.seek(pos[fl])
    contentStream.write(p)
    pos[fl] += len(shorts)*2
def WriteLongs(fl,longs):
    global pos,contentStreams
    if(len(longs) == 0):
        return
    contentStream = contentStreams[fl]
    #dbg("WriteLongs at 0x%08x %s %d" % (pos[fl],longs,len(longs)))
    if pos[fl]<=0:
        raise Exception("Invalid write position %d" % pos[fl])
    p = pack("%dL" % len(longs),*longs)
    contentStream.seek(pos[fl])
    contentStream.write(p)
    pos[fl] += len(longs)*4
def getPos(fl):
    if pos[fl] < 0 :
        raise Exception("invalid pos detected! [%d]" % pos[fl])
    if pos[fl] > 0x100000000 :
        raise Exception("invalid pos detected! [%d]" % pos[fl])
    return pos[fl]
def InsertBytes(fl,offset,data):
    global pos,contentStreams,SNAPSHOT_ID
    contentStream = contentStreams[fl]
    dbg("InsertBytes %08x datalen:%d" % (offset,len(data)))
    if(CREATE_FILE_SNAPSHOTS):
        if(os.path.isdir(os.path.dirname(SNAPSHOT_FMT))):
            SNAPSHOT_ID += 1
            dbg("file snapshot: %s" % (SNAPSHOT_FMT % SNAPSHOT_ID))
            f = open(SNAPSHOT_FMT % SNAPSHOT_ID, "wb")
            contentStream.seek(0)
            f.write(contentStream.read())
            f.close()
    contentStream2 = BytesIO(b'')
    contentStream.seek(0)
    contentStream2.write(contentStream.read(offset))
    contentStream2.write(data)
    contentStream2.write(contentStream.read())
    contentStreams[fl] = contentStream2
    if(CREATE_FILE_SNAPSHOTS):
        if(os.path.isdir(os.path.dirname(SNAPSHOT_FMT))):
            SNAPSHOT_ID += 1
            dbg("file snapshot: %s" % (SNAPSHOT_FMT % SNAPSHOT_ID))
            f = open(SNAPSHOT_FMT % SNAPSHOT_ID, "wb")
            contentStream2.seek(0)
            f.write(contentStream2.read())
            f.close()
    contentStream2.seek(0)
def InsertEmptyBytes(fl,offset,count):
    global pos,contentStreams,SNAPSHOT_ID
    contentStream = contentStreams[fl]
    dbg("InsertEmptyBytes %08x %d" % (offset,count))
    if(CREATE_FILE_SNAPSHOTS):
        if(os.path.isdir(os.path.dirname(SNAPSHOT_FMT))):
            SNAPSHOT_ID += 1
            dbg("file snapshot: %s" % (SNAPSHOT_FMT % SNAPSHOT_ID))
            f = open(SNAPSHOT_FMT % SNAPSHOT_ID, "wb")
            contentStream.seek(0)
            f.write(contentStream.read())
            f.close()
    contentStream2 = BytesIO(b'')
    contentStream.seek(0)
    contentStream2.write(contentStream.read(offset))
    contentStream2.write(b'\0'*count)
    contentStream2.write(contentStream.read())
    contentStreams[fl] = contentStream2
    if(CREATE_FILE_SNAPSHOTS):
        if(os.path.isdir(os.path.dirname(SNAPSHOT_FMT))):
            SNAPSHOT_ID += 1
            dbg("file snapshot: %s" % (SNAPSHOT_FMT % SNAPSHOT_ID))
            f = open(SNAPSHOT_FMT % SNAPSHOT_ID, "wb")
            contentStream2.seek(0)
            f.write(contentStream2.read())
            f.close()
    contentStream2.seek(0)
def DeleteBytes(fl,offset,count):
    global pos,contentStreams,SNAPSHOT_ID
    contentStream = contentStreams[fl]
    dbg("DeleteBytes %08x %d" % (offset,count))
    if(CREATE_FILE_SNAPSHOTS):
        if(os.path.isdir(os.path.dirname(SNAPSHOT_FMT))):
            SNAPSHOT_ID += 1
            dbg("file snapshot: %s" % (SNAPSHOT_FMT % SNAPSHOT_ID))
            f = open(SNAPSHOT_FMT % SNAPSHOT_ID, "wb")
            contentStream.seek(0)
            f.write(contentStream.read())
            f.close()
    contentStream2 = BytesIO(b'')
    contentStream.seek(0)
    contentStream2.write(contentStream.read(offset))
    contentStream.seek(count, SEEK_CUR)
    contentStream2.write(contentStream.read())
    contentStreams[fl] = contentStream2
    if(CREATE_FILE_SNAPSHOTS):
        if(os.path.isdir(os.path.dirname(SNAPSHOT_FMT))):
            SNAPSHOT_ID += 1
            dbg("file snapshot: %s" % (SNAPSHOT_FMT % SNAPSHOT_ID))
            f = open(SNAPSHOT_FMT % SNAPSHOT_ID, "wb")
            contentStream2.seek(0)
            f.write(contentStream2.read())
            f.close()
    contentStream2.seek(0)
def Seek(fl,offset):
    global pos
    pos[fl]=offset
def fseek(fl,roffset):
    global pos
    pos[fl]+=roffset