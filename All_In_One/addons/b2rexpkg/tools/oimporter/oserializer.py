"""
Ogre binary format serializer.
"""
import struct

class Serializer(object):
    def __init__(self):
        self.currentChunkLength = 0
        self.ChunkOverheadSize = 6
    def IgnoreCurrentChunk(self, reader):
        reader.seek(self.currentChunkLength-self.ChunkOverheadSize, 1)
    def ReadMany(self, reader, count, reader_func):
        dest = []
        for i in range(count):
            dest.append(reader_func(reader))
        return dest
    def ReadBytes(self, reader, count):
        return self.ReadMany(reader, count, self.ReadByte)
    def ReadFloats(self, reader, count):
        return self.ReadMany(reader, count, self.ReadFloat)
    def ReadByte(self, reader):
        b = reader.read(1)
        return struct.unpack("c", b)[0]
    def ReadBool(self, reader):
        return struct.unpack("?", reader.read(1))[0]
    def ReadFloat(self, reader):
        return struct.unpack("f", reader.read(4))[0]
    def ReadInt(self, reader):
        return struct.unpack("i", reader.read(4))[0]
    def ReadUInt(self, reader):
        return struct.unpack("I", reader.read(4))[0]
    def ReadLong(self, reader):
        return struct.unpack("q", reader.read(8))[0]
    def ReadULong(self, reader):
        return struct.unpack("Q", reader.read(8))[0]
    def ReadShort(self, reader):
        d = reader.read(2)
        return struct.unpack("h", d)[0]
    def ReadUShort(self, reader):
        return struct.unpack("H", reader.read(2))[0]
    def ReadInts(self, reader, count):
        return self.ReadMany(reader, count, self.ReadInt)
    def ReadShorts(self, reader, count):
        return self.ReadMany(reader, count, self.ReadShort)
    def ReadString(self, reader, delimiter=b"\n"):
        dest = b""
        c = self.ReadByte(reader)
        while not c == delimiter:
            dest += c
            c = self.ReadByte(reader)
        return bytes.decode(dest, "latin1")
    def ReadQuat(self, reader):
        return {"x":self.ReadFloat(reader), "y":self.ReadFloat(reader),
                "z":self.ReadFloat(reader), "w":self.ReadFloat(reader)}
    def ReadVector3(self, reader):
        return {"x":self.ReadFloat(reader), "y":self.ReadFloat(reader),
                "z":self.ReadFloat(reader)}
    def ReadVector4(self, reader):
        return self.ReadQuat(reader)
    def ReadChunk(self, reader):
        id = self.ReadShort(reader)
        self.currentChunkLength = self.ReadInt(reader)
        return id
    def Seek(self, reader, length, origin=None):
        if origin:
            reader.seek(origin+length)
        else:
            reader.seek(length, 1)
    def IsEOF(self, reader):
        return reader.tell() >= len(reader.getvalue())
        



