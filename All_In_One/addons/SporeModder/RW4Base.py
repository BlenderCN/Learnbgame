"""
This module contains:
  - FileReader, FileWriter: classes for reading/writing binary files, supporting different types (int, float, byte,...).
  - RenderWare: a class which allows parsing or creating rw4 files.
  - Classes for all supported RenderWare4 objects, as well as methods for reading/writing them.
"""
from inspect import _VAR_POSITIONAL

__author__ = 'Eric'

import struct
from sporemodder.materials import DirectXEnums
from collections import namedtuple

nameList = {
    0xC2299AA7: 'impact',
    0x9891EEC7: 'madsad',
    0x30EE8F49: 'scared',
    0x114BB90C: 'breathe',
    0x6FB760FF: 'idle',
    0xB37B55B2: 'move',
    0x0AC4AEED: 'attack',
    0x47F0B3DC: 'bend',
    0x75D4C8CD: 'point',
    0x998BBF67: 'turnon',
    0x892788C6: 'lickair',
    0xDD0DCEF4: 'unique',
    0xAEB95D4C: 'flap',
    0xAC04E296: 'tuck',
    0x2E6521F4: 'DeformAxisForward',
    0x9BFE8BF8: 'DeformAxisBack',
    0x2D3BFA19: 'DeformAxisRight',
    0x7CC96C02: 'DeformAxisLeft',
    0xD02751DE: 'DeformAxisUp',
    0xD0BE09E0: 'joint1',
    0xD0BE09E2: 'joint3',
    0xD0BE09E3: 'joint2'
}


def getHash(string):
    if string[0:2] == '0x':
        return int(string, 16)
    elif string[0] == '#':
        return int(string[1:], 16)
    else:
        string = string.lower()
        hval = 0x811c9dc5
        fnv_32_prime = 0x01000193
        uint32_max = (2 ** 32)
        for s in string:
            hval = (hval * fnv_32_prime) % uint32_max
            hval ^= ord(s)
        return hval


def getString(hashID):
    if hashID in nameList:
        return nameList[hashID]
    else:
        return format(hashID, '#10x')


class ModelError(Exception):
    def __init__(self, message, causeObject):
        super().__init__(message)
        self.causeObject = causeObject


class RWMatrix:
    def __init__(self, rows, columns):
        # we store the columns, rows is just len(self.data)
        self.columns = columns
        self.data = []
        for i in range(0, rows):
            self.data.append([None] * columns)

    def __getitem__(self, item):
        return self.data[item]

    def read(self, fileReader):
        for i in range(0, len(self.data)):
            for j in range(0, self.columns):
                self.data[i][j] = fileReader.readFloat()

    def write(self, fileWriter):
        for i in range(0, len(self.data)):
            for j in range(0, self.columns):
                fileWriter.writeFloat(self.data[i][j])


class FileReader:
    def __init__(self, fileBuffer):
        self.fileBuffer = fileBuffer

    def readByte(self, endian='<'):
        return struct.unpack(endian + 'b', self.fileBuffer.read(1))[0]

    def readUByte(self, endian='<'):
        return struct.unpack(endian + 'B', self.fileBuffer.read(1))[0]

    def readShort(self, endian='<'):
        return struct.unpack(endian + 'h', self.fileBuffer.read(2))[0]

    def readUShort(self, endian='<'):
        return struct.unpack(endian + 'H', self.fileBuffer.read(2))[0]

    def readInt(self, endian='<'):
        return struct.unpack(endian + 'i', self.fileBuffer.read(4))[0]

    def readUInt(self, endian='<'):
        return struct.unpack(endian + 'I', self.fileBuffer.read(4))[0]

    def readFloat(self, endian='<'):
        return struct.unpack(endian + 'f', self.fileBuffer.read(4))[0]

    def readBoolean(self, endian='<'):
        return struct.unpack(endian + '?', self.fileBuffer.read(1))[0]
    
    def seek(self, offset):
        self.fileBuffer.seek(offset)


class FileWriter:
    def __init__(self, fileBuffer):
        self.fileBuffer = fileBuffer

    def writeByte(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'b', value))

    def writeUByte(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'B', value))

    def writeShort(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'h', value))

    def writeUShort(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'H', value))

    def writeInt(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'i', value))

    def writeUInt(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'I', value))

    def writeFloat(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + 'f', value))

    def writeBoolean(self, value, endian='<'):
        return self.fileBuffer.write(struct.pack(endian + '?', value))
    
    def write(self, array):
        return self.fileBuffer.write(array)


class ArrayFileReader(FileReader):
    def __init__(self, data):
        super().__init__(data)
        self.offset = 0

    def readByte(self, endian='<'):
        self.offset += 1
        return struct.unpack_from(endian + 'b', self.fileBuffer, self.offset - 1)[0]

    def readUByte(self, endian='<'):
        self.offset += 1
        return struct.unpack_from(endian + 'B', self.fileBuffer, self.offset - 1)[0]

    def readShort(self, endian='<'):
        self.offset += 2
        return struct.unpack_from(endian + 'h', self.fileBuffer, self.offset - 2)[0]

    def readUShort(self, endian='<'):
        self.offset += 2
        return struct.unpack_from(endian + 'H', self.fileBuffer, self.offset - 2)[0]

    def readInt(self, endian='<'):
        self.offset += 4
        return struct.unpack_from(endian + 'i', self.fileBuffer, self.offset - 4)[0]

    def readUInt(self, endian='<'):
        self.offset += 4
        return struct.unpack_from(endian + 'I', self.fileBuffer, self.offset - 4)[0]

    def readFloat(self, endian='<'):
        self.offset += 4
        return struct.unpack_from(endian + 'f', self.fileBuffer, self.offset - 4)[0]

    def readBoolean(self, endian='<'):
        self.offset += 1
        return struct.unpack_from(endian + '?', self.fileBuffer, self.offset - 1)[0]

    def skipBytes(self, nBytes):
        self.offset += nBytes

    def read(self, nBytes):
        result = self.fileBuffer[self.offset:self.offset + nBytes]
        self.offset += nBytes
        return result


class ArrayFileWriter(FileWriter):
    def __init__(self):
        super().__init__(bytearray())

    def writeByte(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'b', value))

    def writeUByte(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'B', value))

    def writeShort(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'h', value))

    def writeUShort(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'H', value))

    def writeInt(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'i', value))

    def writeUInt(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'I', value))

    def writeFloat(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + 'f', value))

    def writeBoolean(self, value, endian='<'):
        return self.fileBuffer.extend(struct.pack(endian + '?', value))
    
    def write(self, array):
        return self.fileBuffer.extend(array)


class RWHeader:
    type_code_model = 1
    type_code_texture = 0x04000000
    type_code_special = 0xCAFED00D

    def __init__(self, renderWare, rwTypeCode=0, sub_references=None, pSubReferenceOffsets=0):
        self.renderWare = renderWare
        self.magic = None  # 28 bytes
        self.rwTypeCode = rwTypeCode
        self.pSectionInfos = 0
        self.pBufferData = 0
        self.sectionCount = 0

        self.sectionManifest = SectionManifest(
            renderWare,
            field_0=4,
            field_4=12
        )

        self.sectionTypes = SectionTypes(
            renderWare,
            field_4=12
        )

        self.sectionExternalArenas = SectionExternalArenas(
            renderWare,
            field_0=3,
            field_4=0x18,
            field_8=1,
            field_C=0xffb00000,
            field_10=1,
            field_14=0,
            field_18=0,
            field_1C=0
        )

        self.sectionSubReferences = SectionSubReferences(
            renderWare,
            sub_references=sub_references,
            field_4=0,
            field_8=0,
            pSubReferenceOffsets=pSubReferenceOffsets
        )

        self.sectionAtoms = SectionAtoms(
            renderWare,
            field_0=0,
            field_4=0
        )

    def read(self, fileReader):
        self.magic = fileReader.fileBuffer.read(28)
        self.rwTypeCode = fileReader.readInt()

        fileReader.readInt()  # this one is sectionCount too, but apparently Spore uses the second one
        self.sectionCount = fileReader.readInt()  # 24h
        fileReader.readInt()  # 0x10 if it's a model, 4 if it's a texture
        fileReader.readInt()  # always 0 ?
        self.pSectionInfos = fileReader.readInt()  # 30h
        fileReader.readInt()  # always 0x98
        fileReader.readInt()  # always 0 ?
        fileReader.readInt()  # always 0 ?
        fileReader.readInt()  # always 0 ?
        self.pBufferData = fileReader.readInt()

        # we don't need to continue, nothing important here

    def write(self, fileWriter, buffersSize):
        fileWriter.fileBuffer.write(
            b'\x89RW4w32\x00\x0D\x0A\x1A\x0A\x00\x20\x04\x00454\x00000\x00\x00\x00\x00\x00')

        fileWriter.fileBuffer.write(
            struct.pack('<iiiiiiiiiii', self.rwTypeCode, self.sectionCount, self.sectionCount, 16, 0,
                        self.pSectionInfos, 152,
                        0, 0, 0,
                        self.pBufferData))

        fileWriter.fileBuffer.write(struct.pack('<ii', 16, buffersSize))
        fileWriter.fileBuffer.write(struct.pack('<iiiii', 4, 0, 1, 0, 1))
        fileWriter.fileBuffer.write(struct.pack('<i', 0))  # 0x00C00758 ?
        fileWriter.fileBuffer.write(struct.pack('<iiiii', 4, 0, 1, 0, 1))
        fileWriter.fileBuffer.write(struct.pack('<iiiiiii', 0, 1, 0, 0, 0, 0, 0))

        pSectionManifest = fileWriter.fileBuffer.tell()
        fileWriter.writeInt(SectionManifest.type_code)
        self.sectionManifest.write(fileWriter)

        self.sectionManifest.pSectionTypes = fileWriter.fileBuffer.tell() - pSectionManifest
        fileWriter.writeInt(SectionTypes.type_code)
        self.sectionTypes.write(fileWriter)

        self.sectionManifest.pSectionExternalArenas = fileWriter.fileBuffer.tell() - pSectionManifest
        fileWriter.writeInt(SectionExternalArenas.type_code)
        self.sectionExternalArenas.write(fileWriter)

        self.sectionManifest.pSectionSubReferences = fileWriter.fileBuffer.tell() - pSectionManifest
        fileWriter.writeInt(SectionSubReferences.type_code)
        self.sectionSubReferences.write(fileWriter)

        self.sectionManifest.pSectionAtoms = fileWriter.fileBuffer.tell() - pSectionManifest
        fileWriter.writeInt(SectionAtoms.type_code)
        self.sectionAtoms.write(fileWriter)

        # write the section manifest again now we have all offsets
        previous_offset = fileWriter.fileBuffer.tell()
        fileWriter.fileBuffer.seek(pSectionManifest + 4)
        self.sectionManifest.write(fileWriter)
        fileWriter.fileBuffer.seek(previous_offset)


INDEX_OBJECT = 0
INDEX_NO_OBJECT = 1
INDEX_SUB_REFERENCE = 2

SubReference = namedtuple('SubReference', ('rwObject', 'offset'))


class RenderWare4:

    def __init__(self):
        self.objects = []
        self.header = RWHeader(self)
        self.excluded_types = []

    def getObjects(self, typeCode):
        return [x for x in self.objects if x is not None and x.type_code == typeCode]

    def getObject(self, index):
        sectionType = index >> 0x16
        if sectionType == INDEX_OBJECT:
            return self.objects[index]
        elif sectionType == INDEX_SUB_REFERENCE:
            return self.objects[self.header.sectionSubReferences.sub_references[index & 0x3FFFF].rwObject]
        elif sectionType == INDEX_NO_OBJECT and (index & 0x3FFFF) == 0:
            return None
        else:
            raise NameError("Unsupported index %x" % index)

    def getIndex(self, rwObject, sectionType=INDEX_OBJECT):
        if sectionType == INDEX_OBJECT:
            if rwObject is None:
                return -1
            return self.objects.index(rwObject)
        elif sectionType == INDEX_SUB_REFERENCE:
            index = INDEX_SUB_REFERENCE << 0x16
            for reference in self.header.sectionSubReferences.sub_references:
                if reference.rwObject == rwObject:
                    return index
                index += 1
            else:
                return -1
        elif sectionType == INDEX_NO_OBJECT and rwObject is None:
            return INDEX_NO_OBJECT << 0x16
        else:
            raise NameError("Unsupported getIndex for sectionType %x" % sectionType)

    def createObject(self, typeCode):
        for supportedObject in RWObject.__subclasses__():
            if supportedObject.type_code == typeCode:
                obj = supportedObject(self)
                self.objects.append(obj)
                return obj

        return None

    def addObject(self, obj):
        self.objects.append(obj)

    def addSubReference(self, rwObject, offset):
        reference = SubReference(rwObject=rwObject, offset=offset)
        self.header.sectionSubReferences.sub_references.append(reference)

    def read(self, fileReader):

        self.header.read(fileReader)

        fileReader.fileBuffer.seek(self.header.pSectionInfos)

        for i in range(self.header.sectionCount):
            sectionInfo = RWSectionInfo(self)
            sectionInfo.read(fileReader)
            obj = self.createObject(sectionInfo.typeCode)
            if obj is not None:
                obj.sectionInfo = sectionInfo
            else:
                # add a None object anyways so indices work correctly
                self.objects.append(None)

        for obj in self.objects:
            if obj is not None and obj.type_code not in self.excluded_types:
                fileReader.fileBuffer.seek(obj.sectionInfo.pData)
                obj.read(fileReader)

    def write(self, fileWriter):
        def write_alignment(alignment):
            file_pos = fileWriter.fileBuffer.tell()
            padding = ((file_pos + alignment-1) & ~(alignment-1)) - file_pos
            fileWriter.fileBuffer.write(bytearray(padding))

        # First we need to create the list with all the type_codes
        self.header.sectionCount = len(self.objects)

        self.header.sectionTypes.type_codes.append(0)
        self.header.sectionTypes.type_codes.append(0x10030)
        self.header.sectionTypes.type_codes.append(0x10031)
        self.header.sectionTypes.type_codes.append(0x10032)
        self.header.sectionTypes.type_codes.append(0x10010)

        # we do them in a separate list because apparently they have to be sorted
        used_type_codes = []
        for obj in self.objects:
            if obj.type_code not in used_type_codes and obj.type_code != 0x10030:
                used_type_codes.append(obj.type_code)

        self.header.sectionTypes.type_codes.extend(sorted(used_type_codes))

        # Now write the header
        self.header.write(fileWriter, 0)

        # Create section infos for every object
        for obj in self.objects:
            obj.sectionInfo = RWSectionInfo(
                self,
                field_04=0,
                alignment=obj.alignment,
                typeCodeIndex=self.header.sectionTypes.type_codes.index(obj.type_code),
                typeCode=obj.type_code
            )

        # Write all objects except BaseResources
        for obj in self.objects:
            if obj.type_code != BaseResource.type_code:
                # write padding so it is aligned
                write_alignment(obj.alignment)

                obj.sectionInfo.pData = fileWriter.fileBuffer.tell()
                obj.write(fileWriter)
                obj.sectionInfo.dataSize = fileWriter.fileBuffer.tell() - obj.sectionInfo.pData

        # Write section infos, remember the position where we write them since we will have to write them again
        self.header.pSectionInfos = fileWriter.fileBuffer.tell()
        for obj in self.objects:
            obj.sectionInfo.write(fileWriter)

        # ??
        self.header.sectionSubReferences.pSubReferenceOffsets = fileWriter.fileBuffer.tell()

        # Apparently this is necessary?
        fileWriter.fileBuffer.write(bytearray(48))

        # Now write the BaseResources
        self.header.pBufferData = fileWriter.fileBuffer.tell()
        for obj in self.objects:
            if obj.type_code == BaseResource.type_code:
                # write padding so it is aligned
                write_alignment(obj.alignment)

                start_pos = fileWriter.fileBuffer.tell()
                obj.sectionInfo.pData = start_pos - self.header.pBufferData
                obj.write(fileWriter)
                obj.sectionInfo.dataSize = fileWriter.fileBuffer.tell() - start_pos

        buffersSize = fileWriter.fileBuffer.tell() - self.header.pBufferData

        # Write the section infos again with all the correct data
        fileWriter.fileBuffer.seek(self.header.pSectionInfos)
        for obj in self.objects:
            obj.sectionInfo.write(fileWriter)

        # We write the header again with all the correct data
        fileWriter.fileBuffer.seek(0)
        self.header.write(fileWriter, buffersSize)

    def seekToData(self, fileReader, rwObject):
        if self.header is not None and rwObject is not None and rwObject.sectionInfo is not None:
            if rwObject.sectionInfo.typeCode == BaseResource.type_code:
                fileReader.fileBuffer.seek(self.header.pBufferData + rwObject.sectionInfo.pData)
            else:
                fileReader.fileBuffer.seek(rwObject.sectionInfo.pData)


class RWSectionInfo:
    def __init__(self, renderWare, pData=0, field_04=0, dataSize=0, alignment=0, typeCodeIndex=0, typeCode=0):
        self.renderWare = renderWare
        self.pData = pData  # 00h
        self.field_04 = field_04
        self.dataSize = dataSize  # 08h
        self.alignment = alignment  # 0Ch
        self.typeCodeIndex = typeCodeIndex  # 10h
        self.typeCode = typeCode  # 14h

    def read(self, fileReader):
        self.pData = fileReader.readInt()
        self.field_04 = fileReader.readInt()
        self.dataSize = fileReader.readInt()
        self.alignment = fileReader.readInt()
        self.typeCodeIndex = fileReader.readInt()
        self.typeCode = fileReader.readInt()

    def write(self, fileWriter):
        fileWriter.writeInt(self.pData)
        fileWriter.writeInt(self.field_04)
        fileWriter.writeInt(self.dataSize)
        fileWriter.writeInt(self.alignment)
        fileWriter.writeInt(self.typeCodeIndex)
        fileWriter.writeInt(self.typeCode)


class RWObject:
    type_code = 0
    alignment = 4

    def __init__(self, renderWare):
        self.renderWare = renderWare
        # self.typeCode = self.getTypeCode()
        self.sectionInfo = None

    def read(self, fileReader):
        pass

    def write(self, fileWriter):
        pass


class SectionManifest(RWObject):
    type_code = 0x10004

    def __init__(self, renderWare, field_0=4, field_4=12):
        super().__init__(renderWare)
        # all offsets are relative to the beginning of this section
        self.field_0 = field_0
        self.field_4 = field_4
        self.pSectionTypes = 0
        self.pSectionExternalArenas = 0
        self.pSectionSubReferences = 0
        self.pSectionAtoms = 0

    def read(self, fileReader):
        self.field_0 = fileReader.readInt()
        self.field_4 = fileReader.readInt()
        self.pSectionTypes = fileReader.readInt()
        self.pSectionExternalArenas = fileReader.readInt()
        self.pSectionSubReferences = fileReader.readInt()
        self.pSectionAtoms = fileReader.readInt()

    def write(self, fileWriter):
        fileWriter.writeInt(self.field_0)
        fileWriter.writeInt(self.field_4)
        fileWriter.writeInt(self.pSectionTypes)
        fileWriter.writeInt(self.pSectionExternalArenas)
        fileWriter.writeInt(self.pSectionSubReferences)
        fileWriter.writeInt(self.pSectionAtoms)


class SectionTypes(RWObject):
    type_code = 0x10005

    def __init__(self, renderWare, field_4=12):
        super().__init__(renderWare)
        self.field_4 = field_4
        self.type_codes = []

    def read(self, fileReader):
        count = fileReader.readInt()
        self.field_4 = fileReader.readInt()

        for i in range(count):
            self.type_codes.append(fileReader.readInt())

    def write(self, fileWriter):
        fileWriter.writeInt(len(self.type_codes))
        fileWriter.writeInt(self.field_4)

        for x in self.type_codes:
            fileWriter.writeInt(x)


class SectionExternalArenas(RWObject):
    type_code = 0x10006

    def __init__(self, renderWare,
                 field_0=3, field_4=0x18, field_8=1, field_C=0xffb00000,
                 field_10=1, field_14=0, field_18=0, field_1C=0):
        super().__init__(renderWare)
        self.field_0 = field_0
        self.field_4 = field_4
        self.field_8 = field_8
        self.field_C = field_C
        self.field_10 = field_10
        self.field_14 = field_14
        self.field_18 = field_18
        self.field_1C = field_1C

    def read(self, fileReader):
        self.field_0 = fileReader.readInt()
        self.field_4 = fileReader.readInt()
        self.field_8 = fileReader.readInt()
        self.field_C = fileReader.readInt()
        self.field_10 = fileReader.readInt()
        self.field_14 = fileReader.readInt()
        self.field_18 = fileReader.readInt()
        self.field_1C = fileReader.readInt()

    def write(self, fileWriter):
        fileWriter.writeInt(self.field_0)
        fileWriter.writeInt(self.field_4)
        fileWriter.writeInt(self.field_8)
        fileWriter.writeUInt(self.field_C)
        fileWriter.writeInt(self.field_10)
        fileWriter.writeInt(self.field_14)
        fileWriter.writeInt(self.field_18)
        fileWriter.writeInt(self.field_1C)


class SectionSubReferences(RWObject):
    type_code = 0x10007

    def __init__(self, renderWare, sub_references=None, field_4=0, field_8=0, pSubReferenceOffsets=0):
        super().__init__(renderWare)
        self.sub_references = sub_references
        if self.sub_references is None:
            self.sub_references = []

        self.field_4 = field_4
        self.field_8 = field_8
        self.pSubReferenceOffsets = pSubReferenceOffsets

    def read(self, fileReader):
        count = fileReader.readInt()
        self.field_4 = fileReader.readInt()
        self.field_8 = fileReader.readInt()

        # this is the end of the offsets
        fileReader.readInt()
        self.pSubReferenceOffsets = fileReader.readInt()

        # the count again
        fileReader.readInt()

        previous_position = fileReader.fileBuffer.tell()
        fileReader.fileBuffer.seek(self.pSubReferenceOffsets)

        for i in range(count):
            reference = SubReference()
            reference.rwObject = self.renderWare.getObject(fileReader.readInt())
            reference.offset = fileReader.readInt()
            self.sub_references.append(reference)

        fileReader.fileBuffer.seek(previous_position)

    def write(self, fileWriter):
        fileWriter.writeInt(len(self.sub_references))
        fileWriter.writeInt(self.field_4)
        fileWriter.writeInt(self.field_8)
        fileWriter.writeInt(self.pSubReferenceOffsets + len(self.sub_references) * 8)
        fileWriter.writeInt(self.pSubReferenceOffsets)
        fileWriter.writeInt(len(self.sub_references))

        if self.pSubReferenceOffsets != 0:
            previous_position = fileWriter.fileBuffer.tell()
            fileWriter.fileBuffer.seek(self.pSubReferenceOffsets)

            for reference in self.sub_references:
                fileWriter.writeInt(self.renderWare.getIndex(reference.rwObject))
                fileWriter.writeInt(reference.offset)

            fileWriter.fileBuffer.seek(previous_position)


class SectionAtoms(RWObject):
    type_code = 0x10008

    def __init__(self, renderWare, field_0=0, field_4=0):
        super().__init__(renderWare)
        self.field_0 = field_0
        self.field_4 = field_4

    def read(self, fileReader):
        self.field_0 = fileReader.readInt()
        self.field_4 = fileReader.readInt()

    def write(self, fileWriter):
        fileWriter.writeInt(self.field_0)
        fileWriter.writeInt(self.field_4)


class BaseResource(RWObject):
    type_code = 0x10030
    alignment = 4

    def __init__(self, renderWare, write_method=None, data=None, owner=None):
        super().__init__(renderWare)
        self.write_method = write_method
        self.data = data
        self.owner = owner

    def read(self, fileReader):
        pass

    def write(self, fileWriter):
        if self.write_method is None:
            raise NotImplementedError("No write method specified for this resource")
        else:
            self.write_method(fileWriter, self.data, self.owner)


class Raster(RWObject):
    type_code = 0x20003
    alignment = 4

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.textureFormat = 0
        self.textureFlags = 8  # 0x200 -> D3DUSAGE_AUTOGENMIPMAP, 0x10 -> D3DUSAGE_DYNAMIC
        self.volumeDepth = 0  # used in volume textures
        self.dxBaseTexture = 0  # IDirect3DBaseTexture9*, unused in the file
        self.width = 0
        self.height = 0
        self.field_10 = 8  # usually 8
        self.mipmapLevels = 0
        self.field_14 = 0
        self.field_18 = 0
        self.textureData = None

    def read(self, fileReader):
        self.textureFormat = fileReader.readInt(endian='>')  # 00h
        self.textureFlags = fileReader.readShort()  # 04h
        self.volumeDepth = fileReader.readUShort()  # 06h
        self.dxBaseTexture = fileReader.readInt()  # 08h
        self.width = fileReader.readUShort()  # 0Ch
        self.height = fileReader.readUShort()  # 0Eh
        self.field_10 = fileReader.readByte()  # 10h
        self.mipmapLevels = fileReader.readByte()  # 11h
        fileReader.readShort()
        self.field_14 = fileReader.readInt()  # 14h
        self.field_18 = fileReader.readInt()  # 18h
        self.textureData = self.renderWare.getObject(fileReader.readInt())  # 1Ch

    def write(self, fileWriter):
        fileWriter.writeInt(self.textureFormat, endian='>')
        fileWriter.writeShort(self.textureFlags)
        fileWriter.writeUShort(self.volumeDepth)
        fileWriter.writeInt(self.dxBaseTexture)
        fileWriter.writeUShort(self.width)
        fileWriter.writeUShort(self.height)
        fileWriter.writeByte(self.field_10)
        fileWriter.writeByte(self.mipmapLevels)
        fileWriter.writeShort(0)  # padding
        fileWriter.writeInt(self.field_14)
        fileWriter.writeInt(self.field_18)
        fileWriter.writeInt(self.renderWare.getIndex(self.textureData))

    def fromDDS(self, dds_texture):
        self.width = dds_texture.dwWidth
        self.height = dds_texture.dwHeight
        self.volumeDepth = dds_texture.dwDepth
        self.mipmapLevels = dds_texture.dwMipMapCount
        self.textureFormat = dds_texture.ddsPixelFormat.dwFourCC


class VertexElement:
    def __init__(self, stream=0, offset=0, elementType=0, method=0, usage=0, usageIndex=0, typeCode=0):
        self.stream = stream  # word
        self.offset = offset  # word
        self.type = elementType  # byte, DirectXEnums.D3DDECLTYPE
        self.method = method  # byte, DirectXEnums.D3DDECLMETHOD
        self.usage = usage  # byte, DirectXEnums.D3DDECLUSAGE
        self.usageIndex = usageIndex  # byte
        self.typeCode = typeCode  # DirectXEnums.RWVertexDeclUsage

    def read(self, fileReader):
        self.stream = fileReader.readShort()
        self.offset = fileReader.readShort()
        self.type = fileReader.readByte()
        self.method = fileReader.readByte()
        self.usage = fileReader.readByte()
        self.usageIndex = fileReader.readByte()
        self.typeCode = fileReader.readInt()

    def write(self, fileWriter):
        fileWriter.writeShort(self.stream)
        fileWriter.writeShort(self.offset)
        fileWriter.writeByte(self.type)
        fileWriter.writeByte(self.method)
        fileWriter.writeByte(self.usage)
        fileWriter.writeByte(self.usageIndex)
        fileWriter.writeInt(self.typeCode)

    def readData(self, fileReader):
        if self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT1:
            return fileReader.readFloat(), 0, 0, 1
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT2:
            return fileReader.readFloat(), fileReader.readFloat(), 0, 1
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT3:
            return fileReader.readFloat(), fileReader.readFloat(), fileReader.readFloat(), 1
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT4:
            return fileReader.readFloat(), fileReader.readFloat(), fileReader.readFloat(), fileReader.readFloat()
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_D3DCOLOR:
            intColor = fileReader.readInt()
            return ((intColor & 0xFF000000) >> 24) / float(255), \
                   ((intColor & 0x00FF0000) >> 16) / float(255), \
                   ((intColor & 0x0000FF00) >> 8) / float(255), \
                   (intColor & 0x000000FF) / float(255)
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4:
            return fileReader.readUByte(), fileReader.readUByte(), fileReader.readUByte(), fileReader.readUByte()
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT2:
            return fileReader.readShort(), fileReader.readShort(), 0, 1
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT4:
            return fileReader.readShort(), fileReader.readShort(), fileReader.readShort(), fileReader.readShort()
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4N:
            return fileReader.readUByte() / 255.0, \
                fileReader.readUByte() / 255.0, \
                fileReader.readUByte() / 255.0, \
                fileReader.readUByte() / 255.0
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT2N:
            return fileReader.readShort() / 32767.0, \
                fileReader.readShort() / 32767.0, \
                0, \
                1
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT4N:
            return fileReader.readShort() / 32767.0, \
                fileReader.readShort() / 32767.0, \
                fileReader.readShort() / 32767.0, \
                fileReader.readShort() / 32767.0
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_USHORT2N:
            return fileReader.readUShort() / 65535.0, \
                fileReader.readUShort() / 65535.0, \
                0, \
                1
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_USHORT4N:
            return fileReader.readUShort() / 65535.0, \
                fileReader.readUShort() / 65535.0, \
                fileReader.readUShort() / 65535.0, \
                fileReader.readUShort() / 65535.0

    def writeData(self, fileWriter, data):
        if self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT1:
            fileWriter.writeFloat(data[0])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT2:
            fileWriter.writeFloat(data[0])
            fileWriter.writeFloat(data[1])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT3:
            fileWriter.writeFloat(data[0])
            fileWriter.writeFloat(data[1])
            fileWriter.writeFloat(data[2])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_FLOAT4:
            fileWriter.writeFloat(data[0])
            fileWriter.writeFloat(data[1])
            fileWriter.writeFloat(data[2])
            fileWriter.writeFloat(data[3])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_D3DCOLOR:
            intColor = 0
            intColor |= (int(round(data[0] * 255) & 0xFF)) << 24
            intColor |= (int(round(data[1] * 255) & 0xFF)) << 16
            intColor |= (int(round(data[2] * 255) & 0xFF)) << 9
            intColor |= int(round(data[3] * 255) & 0xFF)
            fileWriter.writeInt(intColor)
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4:
            fileWriter.writeUByte(data[0])
            fileWriter.writeUByte(data[1])
            fileWriter.writeUByte(data[2])
            fileWriter.writeUByte(data[3])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT2:
            fileWriter.writeShort(data[0])
            fileWriter.writeShort(data[1])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT4:
            fileWriter.writeShort(data[0])
            fileWriter.writeShort(data[1])
            fileWriter.writeShort(data[2])
            fileWriter.writeShort(data[3])
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_UBYTE4N:
            fileWriter.writeUByte(int(round(data[0] * 255)))
            fileWriter.writeUByte(int(round(data[1] * 255)))
            fileWriter.writeUByte(int(round(data[2] * 255)))
            fileWriter.writeUByte(int(round(data[3] * 255)))
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT2N:
            fileWriter.writeShort(int(round(data[0] * 32767)))
            fileWriter.writeShort(int(round(data[1] * 32767)))
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_SHORT4N:
            fileWriter.writeShort(int(round(data[0] * 32767)))
            fileWriter.writeShort(int(round(data[1] * 32767)))
            fileWriter.writeShort(int(round(data[2] * 32767)))
            fileWriter.writeShort(int(round(data[3] * 32767)))
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_USHORT2N:
            fileWriter.writeUShort(int(round(data[0] * 65535)))
            fileWriter.writeUShort(int(round(data[1] * 65535)))
        elif self.type == DirectXEnums.D3DDECLTYPE.D3DDECLTYPE_USHORT4N:
            fileWriter.writeUShort(int(round(data[0] * 65535)))
            fileWriter.writeUShort(int(round(data[1] * 65535)))
            fileWriter.writeUShort(int(round(data[2] * 65535)))
            fileWriter.writeUShort(int(round(data[3] * 65535)))


class VertexDescription(RWObject):
    type_code = 0x20004
    alignment = 4

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.field_0 = 0
        self.field_4 = 0
        self.dxVertexDeclaration = 0  # IDirect3DVertexDeclaration9*, not used in file
        self.vertexElements = []
        # I assume vertexSize is a byte and there is another byte before; otherwise, the value would be big-endian
        self.field_0E = 0
        self.vertexSize = 0
        self.field_10 = 0
        self.field_14 = 0

    def read(self, fileReader):
        self.field_0 = fileReader.readInt()
        self.field_4 = fileReader.readInt()
        self.dxVertexDeclaration = fileReader.readInt()

        elementCount = fileReader.readShort()
        self.field_0E = fileReader.readByte()
        self.vertexSize = fileReader.readByte()
        self.field_10 = fileReader.readInt()
        self.field_14 = fileReader.readInt()

        for i in range(0, elementCount):
            element = VertexElement()
            element.read(fileReader)
            self.vertexElements.append(element)

    def write(self, fileWriter):
        fileWriter.writeInt(self.field_0)
        fileWriter.writeInt(self.field_4)
        fileWriter.writeInt(self.dxVertexDeclaration)
        fileWriter.writeShort(len(self.vertexElements))
        fileWriter.writeByte(self.field_0E)
        fileWriter.writeByte(self.vertexSize)
        fileWriter.writeInt(self.field_10)
        fileWriter.writeInt(self.field_14)

        for element in self.vertexElements:
            element.write(fileWriter)

    def getProcessedTuple(self):
        resultNames = [DirectXEnums.RWVertexDeclUsageNames[x.typeCode] for x in self.vertexElements]

        # we need it to create an instance of the namedtuple
        emtpyData = []
        for i in range(len(self.vertexElements)):
            emtpyData.append([])

        Vertices = namedtuple('Vertices', resultNames)
        vertices = Vertices(*emtpyData)

        return vertices


class VertexBuffer(RWObject):
    type_code = 0x20005
    alignment = 4

    def __init__(self, renderWare,
                 vertexDescription=None, baseVertexIndex=0, vertexCount=0, field_10=0, vertexSize=0, vertexData=None):
        super().__init__(renderWare)
        self.vertexDescription = vertexDescription
        self.field_4 = 0
        self.baseVertexIndex = baseVertexIndex
        self.vertexCount = vertexCount
        self.field_10 = field_10
        self.vertexSize = vertexSize
        self.vertexData = vertexData

    def read(self, fileReader):
        self.vertexDescription = self.renderWare.getObject(fileReader.readInt())
        self.field_4 = fileReader.readInt()
        self.baseVertexIndex = fileReader.readInt()  # 08h
        self.vertexCount = fileReader.readInt()  # 0Ch
        self.field_10 = fileReader.readInt()  # 10h
        self.vertexSize = fileReader.readInt()  # 14h
        self.vertexData = self.renderWare.getObject(fileReader.readInt())  # 18h

    def write(self, fileWriter):
        fileWriter.writeInt(self.renderWare.getIndex(self.vertexDescription))
        fileWriter.writeInt(self.field_4)
        fileWriter.writeInt(self.baseVertexIndex)
        fileWriter.writeInt(self.vertexCount)
        fileWriter.writeInt(self.field_10)
        fileWriter.writeInt(self.vertexSize)
        fileWriter.writeInt(self.renderWare.getIndex(self.vertexData))

    def processData(self, fileReader):
        if self.vertexDescription is None:
            raise ModelError("Cannot process vertices without a vertex description.", self)
        elif self.vertexData is None:
            raise ModelError("Cannot process vertices without a data buffer.", self)

        vertices = self.vertexDescription.getProcessedTuple()

        self.renderWare.seekToData(fileReader, self.vertexData)

        for vertexIndex in range(self.vertexCount):
            for i in range(len(self.vertexDescription.vertexElements)):
                vertices[i].append(self.vertexDescription.vertexElements[i].readData(fileReader))

        return vertices


class IndexBuffer(RWObject):
    type_code = 0x20007
    alignment = 4

    def __init__(self, renderWare,
                 startIndex=0, primitiveCount=0, usage=0, indexFormat=0, primitiveType=0, indexData=None):
        super().__init__(renderWare)
        self.dxIndexBuffer = 0  # IDirect3DIndexBuffer9*, not used in file
        self.startIndex = startIndex
        self.primitiveCount = primitiveCount
        self.usage = usage  # usually D3DUSAGE_WRITEONLY
        self.format = indexFormat  # D3DFMT_INDEX16 or D3DFMT_INDEX32, apparently Spore only supports the first one
        self.primitiveType = primitiveType  # usually D3DPRIMITIVETYPE.D3DPT_TRIANGLELIST
        self.indexData = indexData

    def read(self, fileReader):
        self.dxIndexBuffer = fileReader.readInt()
        # this is added to every index
        self.startIndex = fileReader.readInt()
        self.primitiveCount = fileReader.readInt()
        self.usage = fileReader.readInt()
        self.format = fileReader.readInt()
        self.primitiveType = fileReader.readInt()
        self.indexData = self.renderWare.getObject(fileReader.readInt())

    def write(self, fileWriter):
        fileWriter.writeInt(self.dxIndexBuffer)
        fileWriter.writeInt(self.startIndex)
        fileWriter.writeInt(self.primitiveCount)
        fileWriter.writeInt(self.usage)
        fileWriter.writeInt(self.format)
        fileWriter.writeInt(self.primitiveType)
        fileWriter.writeInt(self.renderWare.getIndex(self.indexData))

    def processData(self, fileReader):
        if self.indexData is None:
            raise ModelError("Cannot process indices without a data buffer.", self)

        indices = []

        self.renderWare.seekToData(fileReader, self.indexData)

        if self.format == DirectXEnums.D3DFORMAT.D3DFMT_INDEX16:
            for i in range(self.primitiveCount):
                indices.append(fileReader.readUShort())

        elif self.format == DirectXEnums.D3DFORMAT.D3DFMT_INDEX32:
            for i in range(self.primitiveCount):
                indices.append(fileReader.readUInt())

        else:
            raise ModelError("Index buffer format is not supported.", self)

        return indices


class SkinMatrixBuffer(RWObject):
    type_code = 0x7000f
    alignment = 16

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.pMatrixData = 0  # in file, offset, in the game a pointer to it
        self.data = []
        self.field_8 = 0
        self.field_C = 0

    def read(self, fileReader):
        self.pMatrixData = fileReader.readInt()
        count = fileReader.readInt()
        self.field_8 = fileReader.readInt()
        self.field_C = fileReader.readInt()

        for i in range(0, count):
            matrix = RWMatrix(3, 4)
            matrix.read(fileReader)
            self.data.append(matrix)

    def write(self, fileWriter):
        self.pMatrixData = fileWriter.fileBuffer.tell() + 16
        fileWriter.writeInt(self.pMatrixData)
        fileWriter.writeInt(len(self.data))
        fileWriter.writeInt(self.field_8)
        fileWriter.writeInt(self.field_C)

        for matrix in self.data:
            matrix.write(fileWriter)


class AnimationSkin(RWObject):
    type_code = 0x70003
    alignment = 16

    class BonePose:
        def __init__(self):
            self.absBindPose = RWMatrix(3, 3)
            self.invPoseTranslation = [0, 0, 0]

        def read(self, fileReader):
            for i in range(3):
                for j in range(3):
                    self.absBindPose[i][j] = fileReader.readFloat()

                fileReader.readInt()  # 0

            for i in range(3):
                self.invPoseTranslation[i] = fileReader.readFloat()

            fileReader.readInt()  # 0

        def write(self, fileWriter):
            for i in range(3):
                for j in range(3):
                    fileWriter.writeFloat(self.absBindPose[i][j])

                fileWriter.writeInt(0)

            for i in range(3):
                fileWriter.writeFloat(self.invPoseTranslation[i])

            fileWriter.writeInt(0)

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.pMatrixData = 0  # in file, offset, in the game a pointer to it
        self.data = []
        self.field_8 = 0
        self.field_C = 0

    def read(self, fileReader):
        self.pMatrixData = fileReader.readInt()
        count = fileReader.readInt()
        self.field_8 = fileReader.readInt()
        self.field_C = fileReader.readInt()

        for i in range(0, count):
            pose = AnimationSkin.BonePose()
            pose.read(fileReader)
            self.data.append(pose)

    def write(self, fileWriter):
        self.pMatrixData = fileWriter.fileBuffer.tell() + 16
        fileWriter.writeInt(self.pMatrixData)
        fileWriter.writeInt(len(self.data))
        fileWriter.writeInt(self.field_8)
        fileWriter.writeInt(self.field_C)

        for pose in self.data:
            pose.write(fileWriter)


class Mesh(RWObject):
    type_code = 0x20009
    alignment = 4

    def __init__(self, renderWare, field_0=0, primitiveType=0, indexBuffer=None, triangleCount=0,
                 firstIndex=0, primitiveCount=0, firstVertex=0, vertexCount=0):
        super().__init__(renderWare)
        self.field_0 = field_0
        self.primitiveType = primitiveType
        self.indexBuffer = indexBuffer
        self.triangleCount = triangleCount
        self.firstIndex = firstIndex
        self.primitiveCount = primitiveCount
        self.firstVertex = firstVertex
        self.vertexCount = vertexCount
        self.vertexBuffers = []

    def read(self, fileReader):
        self.field_0 = fileReader.readInt()
        self.primitiveType = fileReader.readInt()
        self.indexBuffer = self.renderWare.getObject(fileReader.readInt())
        self.triangleCount = fileReader.readInt()
        vertexBuffersCount = fileReader.readInt()
        self.firstIndex = fileReader.readInt()
        self.primitiveCount = fileReader.readInt()
        self.firstVertex = fileReader.readInt()
        self.vertexCount = fileReader.readInt()

        for i in range(0, vertexBuffersCount):
            self.vertexBuffers.append(self.renderWare.getObject(fileReader.readInt()))

    def write(self, fileWriter):
        fileWriter.writeInt(self.field_0)
        fileWriter.writeInt(self.primitiveType)
        fileWriter.writeInt(self.renderWare.getIndex(self.indexBuffer))
        fileWriter.writeInt(self.triangleCount)
        fileWriter.writeInt(len(self.vertexBuffers))
        fileWriter.writeInt(self.firstIndex)
        fileWriter.writeInt(self.primitiveCount)
        fileWriter.writeInt(self.firstVertex)
        fileWriter.writeInt(self.vertexCount)

        for buffer in self.vertexBuffers:
            fileWriter.writeInt(self.renderWare.getIndex(buffer))


class MeshCompiledStateLink(RWObject):
    type_code = 0x2001a
    alignment = 4

    def __init__(self, renderWare, mesh=None):
        super().__init__(renderWare)
        self.mesh = mesh
        self.compiledStates = []

    def read(self, fileReader):
        self.mesh = self.renderWare.getObject(fileReader.readInt())
        count = fileReader.readInt()

        for i in range(0, count):
            self.compiledStates.append(self.renderWare.getObject(fileReader.readInt()))

    def write(self, fileWriter):
        fileWriter.writeInt(self.renderWare.getIndex(self.mesh))
        fileWriter.writeInt(len(self.compiledStates))

        for compiledState in self.compiledStates:
            fileWriter.writeInt(self.renderWare.getIndex(compiledState))


class CompiledState(RWObject):
    type_code = 0x2000b
    alignment = 16

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.renderWare = renderWare
        self.data = bytearray()

    def read(self, fileReader):
        size = fileReader.readInt()
        self.data = fileReader.fileBuffer.read(size - 4)

    def write(self, fileWriter):
        fileWriter.writeInt(len(self.data) + 4)
        fileWriter.fileBuffer.write(self.data)


class SkinsInK(RWObject):
    type_code = 0x7000c
    alignment = 4

    def __init__(self, renderWare, field_0=None, skinMatrixBuffer=None, skeleton=None, animationSkin=None):
        super().__init__(renderWare)
        self.field_0 = field_0
        self.field_4 = 0  # this is a pointer to a function but it always gets replaced by Spore
        self.skinMatrixBuffer = skinMatrixBuffer
        self.skeleton = skeleton
        self.animationSkin = animationSkin

    def read(self, fileReader):
        self.field_0 = self.renderWare.getObject(fileReader.readInt())
        self.field_4 = fileReader.readInt()
        self.skinMatrixBuffer = self.renderWare.getObject(fileReader.readInt())
        self.skeleton = self.renderWare.getObject(fileReader.readInt())
        self.animationSkin = self.renderWare.getObject(fileReader.readInt())

    def write(self, fileWriter):
        fileWriter.writeInt(self.renderWare.getIndex(self.field_0, INDEX_NO_OBJECT))
        fileWriter.writeInt(self.field_4)
        fileWriter.writeInt(self.renderWare.getIndex(self.skinMatrixBuffer))
        fileWriter.writeInt(self.renderWare.getIndex(self.skeleton))
        fileWriter.writeInt(self.renderWare.getIndex(self.animationSkin))


class Skeleton(RWObject):
    type_code = 0x70002
    alignment = 4

    class SkeletonBone:
        def __init__(self, name, flags, parent):
            self.name = name
            self.flags = flags
            self.parent = parent

    def __init__(self, renderWare, skeletonID=0):
        super().__init__(renderWare)
        self.bones = []
        self.skeletonID = skeletonID

    def read(self, fileReader):

        pBoneFlags = fileReader.readInt()
        pBoneParents = fileReader.readInt()
        pBoneNames = fileReader.readInt()
        boneCount = fileReader.readInt()
        self.skeletonID = fileReader.readUInt()
        fileReader.readInt()  # boneCount again?

        for i in range(boneCount):
            self.bones.append(Skeleton.SkeletonBone(0, 0, None))

        fileReader.fileBuffer.seek(pBoneNames)
        for bone in self.bones:
            bone.name = fileReader.readUInt()

        fileReader.fileBuffer.seek(pBoneFlags)
        for bone in self.bones:
            bone.flags = fileReader.readInt()

        fileReader.fileBuffer.seek(pBoneParents)
        for bone in self.bones:
            index = fileReader.readInt()
            if index != -1:
                bone.parent = self.bones[index]

    def write(self, fileWriter):
        base_pos = fileWriter.fileBuffer.tell()
        # we will calculate the offsets
        fileWriter.writeInt(base_pos + 24 + len(self.bones) * 4)  # pBoneFlags
        fileWriter.writeInt(base_pos + 24 + len(self.bones) * 8)  # pBoneParents
        fileWriter.writeInt(base_pos + 24)  # pBoneNames
        fileWriter.writeInt(len(self.bones))
        fileWriter.writeUInt(self.skeletonID)
        fileWriter.writeInt(len(self.bones))

        for bone in self.bones:
            fileWriter.writeUInt(bone.name)

        for bone in self.bones:
            fileWriter.writeInt(bone.flags)

        for bone in self.bones:
            if bone.parent is None:
                fileWriter.writeInt(-1)
            else:
                fileWriter.writeInt(self.bones.index(bone.parent))


class BBox(RWObject):
    type_code = 0x80005
    alignment = 16

    def __init__(self, renderWare, bound_box=None):
        super().__init__(renderWare)
        self.bound_box = bound_box
        self.field_0C = 0
        self.field_1C = 0

    def read(self, fileReader):
        if self.bound_box is None:
            self.bound_box = []

        self.bound_box.append([fileReader.readFloat(), fileReader.readFloat(), fileReader.readFloat()])
        self.field_0C = fileReader.readInt()

        self.bound_box.append([fileReader.readFloat(), fileReader.readFloat(), fileReader.readFloat()])
        self.field_1C = fileReader.readInt()

    def write(self, fileWriter):
        fileWriter.writeFloat(self.bound_box[0][0])
        fileWriter.writeFloat(self.bound_box[0][1])
        fileWriter.writeFloat(self.bound_box[0][2])
        fileWriter.writeInt(self.field_0C)
        fileWriter.writeFloat(self.bound_box[1][0])
        fileWriter.writeFloat(self.bound_box[1][1])
        fileWriter.writeFloat(self.bound_box[1][2])
        fileWriter.writeInt(self.field_1C)
        
        
class MorphHandle(RWObject):
    type_code = 0xff0000
    alignment = 4

    def __init__(self, renderWare, handleID=0, default_frame=0.0, animation=None):
        super().__init__(renderWare)
        self.handleID = handleID
        self.field_4 = 0
        self.field_8 = 0
        self.field_C = 0.0
        self.field_10 = 0
        self.field_14 = 0.0
        self.field_18 = 0
        self.field_1C = 0.0
        self.field_20 = 0
        self.field_24 = 0.0
        self.field_28 = 0
        self.field_2C = 0.0
        self.field_30 = 0
        self.field_34 = 0.0
        self.default_frame = default_frame
        self.animation = animation

    def read(self, fileReader):
        self.handleID = fileReader.readUInt()
        self.field_4 = fileReader.readUInt()
        self.field_8 = fileReader.readUInt()
        self.field_C = fileReader.readFloat()
        self.field_10 = fileReader.readUInt()
        self.field_14 = fileReader.readFloat()
        self.field_18 = fileReader.readUInt()
        self.field_1C = fileReader.readFloat()
        self.field_20 = fileReader.readUInt()
        self.field_24 = fileReader.readFloat()
        self.field_28 = fileReader.readUInt()
        self.field_2C = fileReader.readFloat()
        self.field_30 = fileReader.readUInt()
        self.field_34 = fileReader.readFloat()
        self.default_frame = fileReader.readFloat()
        self.animation = self.renderWare.getObject(fileReader.readInt())

    def write(self, fileWriter):
        fileWriter.writeUInt(self.handleID)
        fileWriter.writeUInt(self.field_4)
        fileWriter.writeUInt(self.field_8)
        fileWriter.writeFloat(self.field_C)
        fileWriter.writeUInt(self.field_10)
        fileWriter.writeFloat(self.field_14)
        fileWriter.writeUInt(self.field_18)
        fileWriter.writeFloat(self.field_1C)
        fileWriter.writeUInt(self.field_20)
        fileWriter.writeFloat(self.field_24)
        fileWriter.writeUInt(self.field_28)
        fileWriter.writeFloat(self.field_2C)
        fileWriter.writeUInt(self.field_30)
        fileWriter.writeFloat(self.field_34)
        fileWriter.writeFloat(self.default_frame)
        fileWriter.writeInt(self.renderWare.getIndex(self.animation))
        
        
class TriangleKDTreeProcedural(RWObject):
    type_code = 0x80003
    alignment = 16

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.bound_box = None
        self.triangles = []
        self.vertices = []
        self.field_20 = 0x00D59208
        self.field_24 = 8
        # 28h: triangle_count
        self.field_2C = 0
        # 30h: vertex_count
        
        self.triangle_unknowns = []
        self.bound_box_2 = None
        self.unknown_data = []

    def read(self, fileReader):
        if self.bound_box is None:
            self.bound_box = BBox(self.renderWare)
            
        if self.bound_box_2 is None:
            self.bound_box_2 = BBox(self.renderWare)
            
        self.bound_box.read(fileReader)
        
        self.field_20 = fileReader.readInt()
        self.field_24 = fileReader.readInt()
        
        triangle_count = fileReader.readInt()
        self.field_2C = fileReader.readInt()
        vertex_count = fileReader.readInt()
        
        pTriangles = fileReader.readInt()
        pVertexOffsets = fileReader.readInt()
        p4 = fileReader.readInt()
        p3 = fileReader.readInt()
        
        
        # Read vertices
        fileReader.seek(pVertexOffsets)
        for i in range(vertex_count):
            self.vertices.append((fileReader.readFloat(), fileReader.readFloat(), fileReader.readFloat()))
            fileReader.readInt()
            
        # Read triangles
        fileReader.seek(pTriangles)
        for i in range(triangle_count):
            # it has one integer more, which is usually 0 (?)
            self.triangles.append((fileReader.readInt(), fileReader.readInt(), fileReader.readInt(), fileReader.readInt()))
            
            
        fileReader.seek(p3)
        x = 0
        for i in range(triangle_count):
            if i & 7 == 0:
                x = fileReader.readInt()
                
            self.triangle_unknowns.append((x >> ((i & 7) * 4)) & 0xf)


        fileReader.seek(p4)
        fileReader.readInt()  # self.vertexPos - 8 * 4
        unknown_count = fileReader.readInt()
        fileReader.readInt()  # self.triCount
        fileReader.readInt()  # 0
        self.bound_box_2.read(fileReader)
        for i in range(unknown_count):
            self.unknown_data.append(
                (fileReader.readInt(), fileReader.readInt(), fileReader.readInt(), fileReader.readInt(), fileReader.readInt(), fileReader.readInt(),
                 fileReader.readFloat(), fileReader.readFloat())
                )

    def write(self, fileWriter):
        self.bound_box.write(fileWriter)
        
        fileWriter.writeInt(self.field_20)
        fileWriter.writeInt(self.field_24)
        fileWriter.writeInt(len(self.triangles))
        fileWriter.writeInt(self.field_2C)
        fileWriter.writeInt(len(self.vertices))
        
        pointers_offset = fileWriter.fileBuffer.tell()
        
        pTriangles = 0
        pVertices = 0
        p4 = 0
        p3 = 0
        
        fileWriter.writeInt(pTriangles)
        fileWriter.writeInt(pVertices)
        fileWriter.writeInt(p4)
        fileWriter.writeInt(p3)

        
        # Write vertices
        pos = fileWriter.fileBuffer.tell()
        pVertices = (pos + 15) & ~15
        
        fileWriter.write(bytearray(pVertices - pos))
        
        for vertex in self.vertices:
            fileWriter.writeFloat(vertex[0])
            fileWriter.writeFloat(vertex[1])
            fileWriter.writeFloat(vertex[2])
            fileWriter.writeInt(0)
        
        # Write triangles
        pTriangles = fileWriter.fileBuffer.tell()
        for triangle in self.triangles:
            fileWriter.writeInt(triangle[0])
            fileWriter.writeInt(triangle[1])
            fileWriter.writeInt(triangle[2])
            fileWriter.writeInt(triangle[3])
        
            
        p3 = fileWriter.fileBuffer.tell()
        
        count = len(self.triangle_unknowns) // 8
        packs = []
        for i in range(count):
            packs.append(self.triangle_unknowns[i*8] + (self.triangle_unknowns[i*8+1] << 4) + (self.triangle_unknowns[i*8+2] << 8) +
                         (self.triangle_unknowns[i*8+3] << 12) + (self.triangle_unknowns[i*8+4] << 16) + (self.triangle_unknowns[i*8+5] << 20) +
                         (self.triangle_unknowns[i*8+6] << 24) + (self.triangle_unknowns[i*8+7] << 28))

        triPack = len(self.triangle_unknowns) % 8
        if triPack > 0:
            pack = 0
            for i in range(triPack):
                pack += self.triangle_unknowns[count*8+i] << (i*4)
            for i in range(8-triPack):
                pack += 15 << ((i+triPack)*4)
            packs.append(pack)

        for p in packs:
            fileWriter.write(struct.pack('I', p))


        pos = fileWriter.fileBuffer.tell()
        p4 = (pos + 15) & ~15
        fileWriter.write(bytearray(p4 - pos))
        
        fileWriter.writeInt(pVertices - 8 * 4)
        fileWriter.writeInt(len(self.unknown_data))
        fileWriter.writeInt(len(self.triangles))
        fileWriter.writeInt(0)
        
        self.bound_box_2.write(fileWriter)
        
        for i in range(len(self.unknown_data)):
            fileWriter.writeInt(self.unknown_data[i][0])
            fileWriter.writeInt(self.unknown_data[i][1])
            fileWriter.writeInt(self.unknown_data[i][2])
            fileWriter.writeInt(self.unknown_data[i][3])
            fileWriter.writeInt(self.unknown_data[i][4])
            fileWriter.writeInt(self.unknown_data[i][5])
            fileWriter.writeFloat(self.unknown_data[i][6])
            fileWriter.writeFloat(self.unknown_data[i][7])
            
            
        # Write the pointer offsets
        final_pos = fileWriter.fileBuffer.tell()
        
        fileWriter.fileBuffer.seek(pointers_offset)
        fileWriter.writeInt(pTriangles)
        fileWriter.writeInt(pVertices)
        fileWriter.writeInt(p4)
        fileWriter.writeInt(p3)
        
        fileWriter.fileBuffer.seek(final_pos)


class Animations(RWObject):
    type_code = 0xff0001
    alignment = 4

    def __init__(self, renderWare):
        super().__init__(renderWare)
        self.animations = {}

    def read(self, fileReader):
        fileReader.readInt()  # index to subreference to this object
        count = fileReader.readInt()
        for i in range(count):
            name = fileReader.readUInt()
            self.animations[name] = self.renderWare.getObject(fileReader.readInt())

    def write(self, fileWriter):
        fileWriter.writeInt(self.renderWare.getIndex(self, INDEX_SUB_REFERENCE))
        fileWriter.writeInt(len(self.animations))

        for item in self.animations.items():
            fileWriter.writeUInt(item[0])
            fileWriter.writeInt(self.renderWare.getIndex(item[1]))
            
    def add(self, nameID, keyframeAnim):
        self.animations[nameID] = keyframeAnim


class KeyframeAnim(RWObject):
    type_code = 0x70001
    alignment = 16

    frames_per_second = 24

    class Channel:
        class Keyframe:
            components = 0
            size = 0
            
            def __init__(self):
                self.time = 0.0

            def read(self, fileReader):
                pass

            def write(self, fileWriter):
                pass

        class LocRotScale(Keyframe):
            components = 0x601
            size = 48

            def __init__(self):
                super().__init__()
                self.loc = [0.0, 0.0, 0.0]
                self.rot = [0.0, 0.0, 0.0, 1.0]
                self.scale = [1.0, 1.0, 1.0]

            def read(self, fileReader):
                for i in range(4):
                    self.rot[i] = fileReader.readFloat()

                for i in range(3):
                    self.loc[i] = fileReader.readFloat()

                for i in range(3):
                    self.scale[i] = fileReader.readFloat()

                fileReader.readInt()
                self.time = fileReader.readFloat()

            def write(self, fileWriter):
                for i in range(4):
                    fileWriter.writeFloat(self.rot[i])

                for i in range(3):
                    fileWriter.writeFloat(self.loc[i])

                for i in range(3):
                    fileWriter.writeFloat(self.scale[i])

                fileWriter.writeInt(0)
                fileWriter.writeFloat(self.time)
                
            def setScale(self, scale):
                self.scale = scale
                
            def setRotation(self, quaternion):
                self.rot[0] = quaternion.x
                self.rot[1] = quaternion.y
                self.rot[2] = quaternion.z
                self.rot[3] = quaternion.w
                
            def setTranslation(self, offset):
                self.loc = offset
                
                
        class LocRot(Keyframe):
            components = 0x101
            size = 36

            def __init__(self):
                super().__init__()
                self.loc = [0.0, 0.0, 0.0]
                self.rot = [0.0, 0.0, 0.0, 1.0]

            def read(self, fileReader):
                for i in range(4):
                    self.rot[i] = fileReader.readFloat()

                for i in range(3):
                    self.loc[i] = fileReader.readFloat()

                self.time = fileReader.readFloat()

            def write(self, fileWriter):
                for i in range(4):
                    fileWriter.writeFloat(self.rot[i])

                for i in range(3):
                    fileWriter.writeFloat(self.loc[i])

                fileWriter.writeFloat(self.time)

            def setRotation(self, quaternion):
                self.rot[0] = quaternion.x
                self.rot[1] = quaternion.y
                self.rot[2] = quaternion.z
                self.rot[3] = quaternion.w
                
            def setTranslation(self, offset):
                self.loc = offset

        def __init__(self, keyframeClass=None):
            self.channelID = 0
            self.keyframeClass = keyframeClass
            self.keyframes = []

        def setKeyframeClass(self, poseComponents):
            for cls in KeyframeAnim.Channel.Keyframe.__subclasses__():
                if cls.components == poseComponents:
                    self.keyframeClass = cls

        def newKeyframe(self, time):
            keyframe = self.keyframeClass()
            keyframe.time = time
            self.keyframes.append(keyframe)
            return keyframe

        def readKeyframes(self, fileReader, count, position):
            if self.keyframeClass is not None:
                fileReader.fileBuffer.seek(position)
                for i in range(count):
                    keyframe = self.keyframeClass()
                    keyframe.read(fileReader)
                    self.keyframes.append(keyframe)

    def __init__(self, renderWare, skeletonID=0, length=0.0):
        super().__init__(renderWare)
        self.skeletonID = skeletonID
        self.field_C = 0
        self.field_1C = 0
        self.length = length
        self.field_24 = 12
        self.flags = 0
        self.channels = []

    def read(self, fileReader):
        basePos = fileReader.fileBuffer.tell()

        pChannelNames = fileReader.readInt()

        channelCount = fileReader.readInt()
        self.skeletonID = fileReader.readUInt()
        self.field_C = fileReader.readInt()

        pChannelData = fileReader.readInt()
        pPaddingEnd = fileReader.readInt()  # probably not just padding

        fileReader.readInt()  # channelCount again
        self.field_1C = fileReader.readInt()
        self.length = fileReader.readFloat()
        self.field_24 = fileReader.readInt()
        self.flags = fileReader.readInt()

        pChannelInfo = fileReader.readInt()

        for i in range(channelCount):
            self.channels.append(KeyframeAnim.Channel())

        fileReader.fileBuffer.seek(pChannelNames)
        for channel in self.channels:
            channel.channelID = fileReader.readUInt()

        channelPositions = []
        channelPoseSizes = []
        fileReader.fileBuffer.seek(pChannelInfo)
        for channel in self.channels:
            channelPositions.append(fileReader.readInt())
            channelPoseSizes.append(fileReader.readInt())

            channel.setKeyframeClass(fileReader.readInt())

        # this approach works except for the last channel
        for i in range(channelCount - 1):
            keyframeCount = (channelPositions[i+1] - channelPositions[i]) // channelPoseSizes[i]

            self.channels[i].readKeyframes(fileReader, keyframeCount, basePos + channelPositions[i])

        # now do the last channel
        if self.channels[-1].keyframeClass is not None:
            fileReader.fileBuffer.seek(basePos + channelPositions[-1])

            lastTime = 0
            while True:
                keyframe = self.channels[-1].keyframeClass()
                keyframe.read(fileReader)

                if keyframe.time < lastTime:
                    break
                else:
                    lastTime = keyframe.time
                    self.channels[-1].keyframes.append(keyframe)

    def write(self, fileWriter):
        def get_position():
            return fileWriter.fileBuffer.tell()
        
        def set_position(position):
            fileWriter.fileBuffer.seek(position)
            
        def write_offset(dst_pos, offset):
            fileWriter.fileBuffer.seek(dst_pos)
            fileWriter.writeInt(offset)
            
        base_pos = fileWriter.fileBuffer.tell()
        
        pChannelNames = 0
        pChannelData = 0
        pPaddingEnd = 0
        pChannelInfo = 0
        
        ppChannelNames = 0
        ppChannelData = 0
        ppPaddingEnd = 0
        ppChannelInfo = 0
        
        ppChannelNames = get_position()
        fileWriter.writeInt(pChannelNames)
        
        fileWriter.writeInt(len(self.channels))
        fileWriter.writeUInt(self.skeletonID)
        fileWriter.writeInt(self.field_C)
        
        ppChannelData = get_position()
        fileWriter.writeInt(pChannelData)
        
        ppPaddingEnd = get_position()
        fileWriter.writeInt(pPaddingEnd)
        
        fileWriter.writeInt(len(self.channels))
        fileWriter.writeInt(self.field_1C)
        fileWriter.writeFloat(self.length)
        fileWriter.writeInt(self.field_24)
        fileWriter.writeInt(self.flags)
        
        ppChannelInfo = get_position()
        fileWriter.writeInt(pChannelInfo)
        
        # Channel names
        pChannelNames = get_position()
        for channel in self.channels:
            fileWriter.writeUInt(channel.channelID)
            
        # Channel info
        pChannelInfo = get_position()
        for channel in self.channels:
            fileWriter.writeInt(0)  # channel data pos
            fileWriter.writeInt(channel.keyframeClass.size)
            fileWriter.writeInt(channel.keyframeClass.components)
            
        # Channel data
        channelDataOffsets = []
        pChannelData = get_position()
        
        for channel in self.channels:
            channelDataOffsets.append(get_position() - base_pos)
            
            for keyframe in channel.keyframes:
                keyframe.write(fileWriter)
                
        # Padding
        if len(self.channels) > 0:
            padding = len(self.channels) * len(self.channels[0].keyframes) * 2 * self.channels[0].keyframeClass.size
        else:
            padding = 48
            
        fileWriter.fileBuffer.write(bytearray(padding)) 
        pPaddingEnd = get_position()
        
        # write all offsets
        final_position = get_position()
        
        write_offset(ppChannelNames, pChannelNames)
        write_offset(ppChannelData, pChannelData)
        write_offset(ppPaddingEnd, pPaddingEnd)
        write_offset(ppChannelInfo, pChannelInfo)
        
        for i in range(len(self.channels)):
            write_offset(pChannelInfo + 12*i, channelDataOffsets[i])
        
        set_position(final_position)


class DDSTexture:
    DDSD_CAPS = 0x1
    DDSD_HEIGHT = 0x2
    DDSD_WIDTH = 0x4
    DDSD_PITCH = 0x8
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE = 0x80000
    DDSD_DEPTH = 0x800000

    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_MIPMAP = 0x400000
    DDSCAPS_TEXTURE = 0x1000

    DDSCAPS2_CUBEMAP = 0x200
    DDSCAPS2_POSITIVEX = 0x400
    DDSCAPS2_NEGATIVEX = 0x800
    DDSCAPS2_POSITIVEY = 0x1000
    DDSCAPS2_NEGATIVEY = 0x2000
    DDSCAPS2_POSITIVEZ = 0x4000
    DDSCAPS2_NEGATIVEZ = 0x8000
    DDSCAPS2_VOLUME = 0x200000

    class DDSPixelFormat:
        DDPF_ALPHAPIXELS = 0x1
        DDPF_ALPHA = 0x2
        DDPF_FOURCC = 0x4
        DDPF_RGB = 0x40
        DDPF_YUV = 0x200
        DDPF_LUMINANCE = 0x200000

        def __init__(self):
            self.dwSize = 32
            self.dwFlags = 0
            self.dwFourCC = 0
            self.dwRGBBitCount = 32
            self.dwRBitMask = 0x00ff0000
            self.dwGBitMask = 0x0000ff00
            self.dwBBitMask = 0x000000ff
            self.dwABitMask = 0xff000000

        def read(self, fileReader):
            self.dwSize = fileReader.readInt()
            self.dwFlags = fileReader.readInt()
            self.dwFourCC = fileReader.readInt(endian='>')
            self.dwRGBBitCount = fileReader.readInt()
            self.dwRBitMask = fileReader.readInt()
            self.dwGBitMask = fileReader.readInt()
            self.dwBBitMask = fileReader.readInt()
            self.dwABitMask = fileReader.readInt()

    def __init__(self):
        self.dwSize = 124
        self.dwFlags = 0
        self.dwHeight = 0
        self.dwWidth = 0
        self.dwPitchOrLinearSize = 0
        self.dwDepth = 0
        self.dwMipMapCount = 0
        self.ddsPixelFormat = DDSTexture.DDSPixelFormat()
        self.dwCaps = 0
        self.dwCaps2 = 0
        self.dwCaps3 = 0
        self.dwCaps4 = 0

        self.data = None

        # these are required in every .dds file
        self.dwFlags |= DDSTexture.DDSD_CAPS
        self.dwFlags |= DDSTexture.DDSD_HEIGHT
        self.dwFlags |= DDSTexture.DDSD_WIDTH
        self.dwFlags |= DDSTexture.DDSD_PIXELFORMAT

        self.dwCaps |= DDSTexture.DDSCAPS_TEXTURE

    def read(self, fileReader, readData=True):

        # magic, 0x44445320
        fileReader.readInt()

        self.dwSize = fileReader.readInt()
        self.dwFlags = fileReader.readInt()
        self.dwHeight = fileReader.readInt()
        self.dwWidth = fileReader.readInt()
        self.dwPitchOrLinearSize = fileReader.readInt()
        self.dwDepth = fileReader.readInt()
        self.dwMipMapCount = fileReader.readInt()

        # DWORD           dwReserved1[11];
        for i in range(11):
            fileReader.readInt()

        self.ddsPixelFormat.read(fileReader)

        self.dwCaps = fileReader.readInt()
        self.dwCaps2 = fileReader.readInt()
        self.dwCaps3 = fileReader.readInt()
        self.dwCaps4 = fileReader.readInt()

        # DWORD           dwReserved2;
        fileReader.readInt()

        if readData:
            if self.ddsPixelFormat.dwFourCC != DirectXEnums.D3DFORMAT.D3DFMT_DXT5:
                raise ModelError("Only DXT5 textures supported", self)

            # go to the end of the file to calculate size
            fileReader.fileBuffer.seek(0, 2)
            bufferSize = fileReader.fileBuffer.tell() - 128

            fileReader.fileBuffer.seek(128)

            self.data = fileReader.fileBuffer.read(bufferSize)