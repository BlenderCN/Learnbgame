import sys
import time
import os
import math
import struct
from array import array
import traceback

EndOfPatches = 97;
OO_SQRT2 = 0.7071067811865475244008443621049

ZERO_CODE = 0x0
ZERO_EOB = 0x2
POSITIVE_VALUE = 0x6
NEGATIVE_VALUE = 0x7

class BitWriter(object):
    _num_bits_in_elem = 8
    def __init__(self):
        self.data = b''
        self.nextbyte = 0
        self.bytePos = 0
        self.bitPos = 0
    def getBytes(self):
        return self.data+struct.pack("<B", self.nextbyte)
    def write(self, instructions, data):
        datatype, nbits = instructions.split(":")
        nbits = int(nbits)
        if datatype in ["uintle", "uint"]:
            self.PackUint(data, nbits)
        elif datatype in ["intle", "int"]:
            self.PackInt(data, nbits)
        elif datatype in ["floatle", "float"]:
            self.PackBits(struct.pack("<f", float(data)), int(nbits))
        else:
            raise Exception("Unsupported type!")
    def PackInt(self, data, nbits):
        if nbits <= 8:
            self.PackBits(struct.pack("<b", int(data)), int(nbits))
        elif nbits <= 16:
            self.PackBits(struct.pack("<h", int(data)), int(nbits))
        elif nbits <= 32:
            self.PackBits(struct.pack("<i", int(data)), int(nbits))
    def PackUint(self, data, nbits):
        if nbits <= 8:
            self.PackBits(struct.pack("<B", int(data)), int(nbits))
        elif nbits <= 16:
            self.PackBits(struct.pack("<H", int(data)), int(nbits))
        elif nbits <= 32:
            self.PackBits(struct.pack("<I", int(data)), int(nbits))
    def PackBits(self, data, totalCount):
        inn = totalCount
        MAX_BITS = self._num_bits_in_elem
        count = 0
        curBytePos = 0
        curBitPos = 0
        while totalCount > 0:
            if totalCount > MAX_BITS:
                count = MAX_BITS
                totalCount -= MAX_BITS
            else:
                count = totalCount
                totalCount = 0
            while count > 0:
                if (ord(data[curBytePos:curBytePos+1]) & (0x01 << (count - 1))) != 0:
                     self.nextbyte = (self.nextbyte | (0x80 >> \
                                                               self.bitPos))
                count -= 1
                self.bitPos += 1
                curBitPos += 1
                if self.bitPos >= MAX_BITS:
                    self.bitPos = 0
                    self.bytePos += 1
                    self.data += struct.pack("<B", self.nextbyte)
                    self.nextbyte = 0
                if curBitPos >= MAX_BITS:
                    curBitPos = 0
                    curBytePos += 1



class BitReader(object):
    _num_bits_in_elem = 8
    def __init__(self, data):
        self._bit_ofs = 0
        self._elem_ofs = 0
        self._data = data
        self._currbyte = struct.unpack("<B", self._data[0:1])[0]
        self.len = len(data)*8
        self.left = self.len
        self.pos = 0
    def ReadBits(self, count):
        data = [0,0,0,0]
        cur_byte = 0
        cur_bit = 0
        total_bits = min(self._num_bits_in_elem, count)
        while count > 0:
            count -= 1
            bit = self.ReadBit()
            if bit:
                newval = data[cur_byte] | (1 << (total_bits - 1 - cur_bit))
                data[cur_byte] = newval
            cur_bit += 1
            if cur_bit >= self._num_bits_in_elem:
                cur_byte += 1
                cur_bit = 0
                total_bits = min(self._num_bits_in_elem, count)
        return struct.pack("<BBBB", *data)
    def read(self, instructions):
        if instructions in ["bool"]:
            return self.ReadBit()
        datatype, nbits = instructions.split(":")
        if datatype in ["uintle", "uint"]:
            return struct.unpack("<I", self.ReadBits(int(nbits)))[0]
        if datatype in ["intle", "int"]:
            return struct.unpack("<i", self.ReadBits(int(nbits)))[0]
        elif datatype in ["floatle", "float"]:
            return struct.unpack("<f", self.ReadBits(32))[0]
    def BitsLeft(self):
        return self.left
    def ReadUint(self, nbits):
        return struct.unpack("<I", self.ReadBits(nbits))[0]
    def ReadBit(self):
        if self.BitsLeft() == 0:
            raise Exception("Out of bits!")
        bit = self._currbyte & (1 << (self._num_bits_in_elem - 1 - self._bit_ofs)) != 0
        self._bit_ofs += 1
        if self._bit_ofs >= self._num_bits_in_elem:
            self._bit_ofs = 0
            self._elem_ofs += 1
            if self.len - (self._bit_ofs + (self._elem_ofs*8)) > 0:
                self._currbyte = struct.unpack("<B",
                                  self._data[self._elem_ofs:self._elem_ofs+1])[0]
        self.pos = self._bit_ofs + (self._elem_ofs*8)
        self.left = self.len - self.pos
        return bit

class IDCTPrecomputationTables(object):
    def __init__(self, size):
        self.buildDequantizeTable(size)
        self.buildQuantizeTable(size)
        self.setupCosines(size)
        self.buildCopyMatrix(size)
    def buildDequantizeTable(self, size):
        self.dequantizeTable = array("f")
        for j in range(size):
            for i in range(size):
                self.dequantizeTable.append(1.0 + (2.0 * float(i+j)))
    def buildQuantizeTable(self, size):
        self.quantizeTable = array("f")
        for j in range(size):
            for i in range(size):
                self.quantizeTable.append(1.0 / (1.0 + (2.0 * float(i+j))))
    def setupCosines(self, size):
        hposz = (math.pi * 0.5) / float(size)
        self.cosineTable = array("f")
        for u in range(size):
            for n in range(size):
                self.cosineTable.append(math.cos((2.0*n+1) * (u*hposz)))
    def buildCopyMatrix(self, size):
        self.copyMatrix = array("I", (0,)*(size*size))
        diag = False
        right = True
        i = 0
        j = 0
        count = 0
        while i < size and j < size:
            self.copyMatrix[j * size + i] = count
            count += 1
            if not diag:
                if right:
                    if i < size-1:
                        i+=1
                    else:
                        j+=1
                    right = False
                    diag = True
                else:
                    if j < size-1:
                        j+=1
                    else:
                        i+=1
                    right = True
                    diag = True
            else:
                if right:
                    i+=1
                    j-=1
                    if i == size-1 or j == 0:
                        diag = False
                else:
                    i-=1
                    j+=1
                    if j == size-1 or i == 0:
                        diag = False


    def DCTLine16(self, linein, lineout, line):
        total = 0.0
        lineSize = line * 16
        cosineTable = self.cosineTable

        for n in range(16):
            total += linein[lineSize + n]

        lineout[lineSize] = OO_SQRT2 * total

        for u in range(1, 16):
            total = 0.0
            for n in range(16):
                total += float(linein[lineSize + n]) * cosineTable[u * 16 + n]
            lineout[lineSize + u] = total


    def DCTColumn16(self, linein, lineout, column):
        total = 0.0
        oosob = 2.0 / 16.0
        cosineTable = self.cosineTable
        copyMatrix = self.copyMatrix

        for n in range(16):
            total += linein[16*n + column]

        lineout[copyMatrix[column]] = int(OO_SQRT2 * total * oosob * self.quantizeTable[column])

        for u in range(1, 16):
            total = 0.0
            u16 = u * 16
            for n in range(16):
                total += float(linein[16*n + column]) * cosineTable[u16 + n]
            line_idx = u16 + column
            val = total * oosob * self.quantizeTable[line_idx]
            lineout[copyMatrix[line_idx]] = int(val)


    def IDCTColumn16(self, linein, lineout, column):
        total = 0.0
        cStride = 16
        start = OO_SQRT2 * linein[column]
        cosineTable = self.cosineTable
        for n in range(16):
            total = start
            for u in range(1,16):
                total += linein[u*cStride + column] * cosineTable[u*cStride + n]
            lineout[16 * n + column] = total


    def IDCTLine16(self, linein, lineout, line):
        oosob = 2.0 / 16.0
        lineSize = line * 16
        start = OO_SQRT2 * linein[lineSize]
        total = 0.0
        cosineTable = self.cosineTable
        for n in range(16):
            total = start
            for u in range(1, 16):
                total += linein[lineSize + u] * cosineTable[u *16 +  n]
            lineout[lineSize+n] = total*oosob



precompTables = IDCTPrecomputationTables(16)

class PatchHeader(object):
    def __init__(self, patchSize, data=None):
        self.patchSize = patchSize
        if data:
            self.decode(data)

    def decode(self, data):
        self.quantWBits = data.ReadUint(8)
        if self.quantWBits == EndOfPatches:
            return
        self.dcOffset = data.read("floatle:32")
        self.range = data.ReadUint(16)

        patchIDs = data.ReadUint(10)
        self.x = patchIDs >> 5
        self.y = patchIDs & 31
        self.wordBits = (self.quantWBits & 0x0f) + 2

    def encode(self, output, outblock):
        wbits = (self.quantWBits & 0x0f) + 2
        maxWbits = wbits + 5
        minWbits = wbits >> 1

        wbits = minWbits

        for i in range(len(outblock)):
            temp = outblock[i]
            if not temp == 0:
                temp = abs(temp)
                for j in range(maxWbits, minWbits, -1):
                    if (int(temp) & (1 << j)) != 0:
                        if j > wbits:
                            wbits = j
                            break
        wbits += 1

        self.quantWBits &= 0xf0

        if wbits > 17 or wbits < 2:
            logger.error("Bits needed per word in EncodePatchHeader() are \
                         outside the allowed range")

        self.quantWBits |= (wbits -2)

        output.write("uintle:8", self.quantWBits)
        output.write("floatle:32", self.dcOffset)
        output.write("uintle:16", self.range)
        output.write("uintle:10", self.patchIDs)
        return wbits


class GroupHeader(object):
    def __init__(self, stride, patchsize, layertype):
        self.stride = stride
        self.patchsize = patchsize
        self.type = layertype # LayerType.Land
    def encode(self, output):
        output.write('uintle:16', self.stride)
        output.write('uintle:8', self.patchsize)
        output.write('uintle:8', self.type)

class TerrainEncoder(object):
    patchSize = 16
    def __init__(self, data, stride, patchSize):
        self.encodePatches(data, stride, patchSize)

    def getBytes(self):
        return self.output.getBytes()

    @staticmethod
    def encode(data, stride=264, patchSize=16):
        encoder = TerrainEncoder(data, stride, patchSize)
        return encoder.getBytes()

    def encodePatches(self, data, stride, patchSize):
        self.output = BitWriter()
        groupheader = GroupHeader(stride, patchSize, 0x4C)
        groupheader.encode(self.output)

        for block, x, y in data:
            self.encodePatchFromHeightmap(block, x, y)

        self.output.write("uintle:8", EndOfPatches)

    def encodePatchFromHeightmap(self, block, x, y):
        if len(block) != 16*16:
            raise Exception("Incorrectly sized patch")
        prequant = 10
        header = self.createPatchHeader(block, x, y)
        self.prescanPatch(header, block, x, y)
        patch = self.compressPatch(block, header, prequant)
        wbits = self.encodePatchHeader(header, patch)
        self.encodePatch(patch, 0, wbits)

    def encodePatch(self, patch, postquant, wbits):
        output = self.output
        if postquant > 16*16 or postquant < 0:
            raise Exception("Postquant is outside the range of allowed values in \
                         EncodePatch()")
        if postquant != 0:
           patch[16*16 - postquant] = 0
        packuint = output.PackUint
        for i in range(16*16):
            eob = False
            temp = patch[i]
            if temp == 0:
                eob = True
                j = i
                while j < 16*16 and eob == True:
                    if patch[j] != 0:
                        eob = False
                    j+=1
                if eob:
                    packuint(ZERO_EOB, 2)
                    return
                else:
                    packuint(ZERO_CODE, 1)
            else:
                if temp < 0:
                    temp *= -1
                    if temp > (1 << wbits):
                        temp = 1 << wbits
                    packuint(NEGATIVE_VALUE, 3)
                    packuint(temp, wbits)
                else:
                    if temp > (1 << wbits):
                        temp = 1 << wbits
                    packuint(POSITIVE_VALUE, 3)
                    packuint(temp, wbits)

    def createPatchHeader(self, block, x, y):
        header = PatchHeader(self.patchSize)
        header.quantWBits = 136
        header.patchIDs = y & 0x1F
        header.patchIDs += (x << 5)
        return header

    def prescanPatch(self, header, block, x, y):
        zmin = min(block)
        zmax = max(block)
        header.dcOffset = zmin
        header.range = int(zmax-zmin + 1.0)

    def compressPatch(self, block, header, prequant):
        patchArea = self.patchSize*self.patchSize
        #outblock = list(range(patchArea))
        wordsize = prequant
        oozrange = 1.0 / float(header.range)
        orange = float(1<<prequant)
        premult = oozrange * orange
        sub = float(1 << (prequant - 1)) + header.dcOffset * premult

        header.quantWBits = wordsize - 2
        header.quantWBits |= (prequant - 2) << 4

        outblock = [block[k] * premult - sub for k in range(256)]

        ftemp = array('f',(0.0,)*patchArea)
        itemp = array('i',(0,)*patchArea)

        for o in range(self.patchSize):
            precompTables.DCTLine16(outblock, ftemp, o)
        for o in range(self.patchSize):
            precompTables.DCTColumn16(ftemp, itemp, o)
        return itemp

    def encodePatchHeader(self, header, block):
        wbits = header.encode(self.output, block)
        return wbits



class TerrainDecoder(object):
    def __init__(self, data, stride=None, patchSize=None):
        self.patches = []
        if not stride and not patchSize:
            stride = struct.unpack("<H", data[0:2])[0]
            patchSize = struct.unpack("<B", data[2:3])[0]
            layerType = struct.unpack("<B", data[3:4])[0]
            data = data[4:]
        self.decompressLand(data, stride, patchSize, layerType)

    @staticmethod
    def decode(data, stride=None, patchSize=None):
        decoder = TerrainDecoder(data, stride, patchSize)
        return decoder.getPatches()

    def getPatches(self):
        return self.patches

    def decodeTerrainPatch(self, header, data, size):
        area = size*size
        patchdata = array('f', range(area))
        readbit = data.ReadBit
        readuint = data.ReadUint
        for i in range(area):
            if data.len - data.pos <= 0:
                while i < size*size:
                    patchdata[i] = 0
                    i+=1
                return patchdata

            if not readbit():
                patchdata[i] = 0
                continue

            if not readbit():
                while i < area:
                    patchdata[i] = 0
                    i+=1
                return patchdata
            signNegative = readbit()
            dataval = readuint(header.wordBits)
            if signNegative:
                patchdata[i] = -dataval
            else:
                patchdata[i] = dataval
        return patchdata

    def decompressTerrainPatch(self, header, data):
        prequant = (header.quantWBits >> 4) +2
        quantize = 1 << prequant
        ooq = 1.0 / float(quantize)
        mult = ooq * float(header.range)
        addval = mult * float(1<<(prequant-1)) + header.dcOffset

        block = []
        if not header.patchSize == 16:
            print("TerrainDecoder:DecompressTerrainPatch: Unsupported patch size   present!")
        for n in range(16*16):
            idx = precompTables.copyMatrix[n]
            num = data[idx]
            val = num * precompTables.dequantizeTable[n]
            block.append(val)
        tempblock = list(range(16*16))
        for o in range(16):
            col = precompTables.IDCTColumn16(block, tempblock, o)
        for o in range(16):
            line = precompTables.IDCTLine16(tempblock, block, o)
        output = tempblock
        for j in range(256):
            output[j] =  (block[j] * mult) + addval
        return output

    def decompressLand(self, rawdata, stride, patchSize, layerType):
        data = BitReader(rawdata)
        cPatchesPerEdge = 16 # patchSize ?
        iter = 0
        while data.BitsLeft() > 0:
            try:
                header = PatchHeader(patchSize, data)
            except:
                traceback.print_exc()
                print("LAND:DecompressLand: Invalid header data!",
                        data.BitsLeft(), layerType, patchSize, stride, iter)
                return
            if header.quantWBits == EndOfPatches:
                #print("LAND OK", len(self.patches))
                return
            if header.x >= cPatchesPerEdge or header.y >= cPatchesPerEdge:
                print("LAND:DecompressLand: Invalid patch data!",
                      data.BitsLeft(), layerType, iter)
                return
            patch = self.decodeTerrainPatch(header, data, patchSize)
            patch = self.decompressTerrainPatch(header, patch)
            self.patches.append([header, patch])
            iter += 1


def checkbitreader():
    a = b''
    x1 = 10
    x2 = 245
    x3 = 666.0
    a = struct.pack("<f",x1)
    a += struct.pack("<f",x2)
    a += struct.pack("<f",x3)
    a += struct.pack("<I",20)
    a += struct.pack("<H",10)
    a += struct.pack("<B",255)
    a += struct.pack("<B",0)
    bits = BitReader(a)
    assert(bits.read("float:32") == x1)
    assert(bits.read("float:32") == x2)
    assert(bits.read("float:32") == x3)
    assert(bits.read("uint:32") == 20)
    assert(bits.read("uint:16") == 10)
    for i in range(8):
        assert(bits.read("bool") == True)
    for i in range(8):
        assert(bits.read("bool") == False)
    assert(bits.len == 32*4+16+16)
    assert(bits.pos == bits.len)

def checkbitwriter():
    writer = BitWriter()
    writer.write("float:32", 666.0)
    writer.write("uint:10", 23)
    writer.write("uint:10", 23)
    writer.write("uint:10", 23)
    writer.write("uint:10", 23)
    writer.PackUint(NEGATIVE_VALUE, 3)
    writer.PackUint(POSITIVE_VALUE, 3)
    writer.PackUint(ZERO_CODE, 1)
    for i in range(256*16):
        writer.write("uint:32", i)
    for i in range(1024):
        writer.write("uint:10", i)
    writer.write("float:32", 662.0)
    data = writer.getBytes()
    reader = BitReader(data)
    assert(reader.read("float:32") == 666.0)
    assert(reader.read("uint:10") == 23)
    assert(reader.read("uint:10") == 23)
    assert(reader.read("uint:10") == 23)
    assert(reader.read("uint:10") == 23)
    assert(reader.read("uint:3") == NEGATIVE_VALUE)
    assert(reader.read("uint:3") == POSITIVE_VALUE)
    assert(reader.read("uint:1") == ZERO_CODE)
    for i in range(256*16):
        assert(reader.read("uint:32") == i)
    for i in range(1024):
        assert(reader.read("uint:10") == i)
    assert(reader.read("float:32") == 662.0)

enctime = 0.0
iters = 0.0
dectime = 0.0

def drawlayer(layerdata, n, im):
    global enctime, iters, dectime
    maxfound = 0
    oldheader = layerdata[0]
    start = time.time()
    data = TerrainEncoder.encode([[layerdata[1], oldheader.x, oldheader.y]])
    enctime += time.time()-start
    start = time.time()
    layerdata = TerrainDecoder.decode(data)[0]
    dectime += time.time()-start
    iters += 1
    header = layerdata[0]
    print(header.x, header.y, len(layerdata[1]))
    assert(header.x == oldheader.x)
    print(header.quantWBits, oldheader.quantWBits)
    print(header.range, oldheader.range)
    #assert(header.quantWBits == oldheader.quantWBits)
    #assert(header.range == oldheader.range)
    off_x = (header.y)*16
    off_y = (header.x)*16
    for j in range(16):
        for i in range(16):
            val = layerdata[1][(i*16)+j]
            if val > maxfound:
                maxfound = val
            val = ((val + 10.0)/40.0)*255
            val = int(min(max(0, val), 255))
            im.putpixel((i+(off_x), j+(off_y)), val)
    return maxfound
try:
    from PIL import Image
except:
    pass
if __name__ == "__main__":
    b = os.path.dirname
    scriptdir = os.path.realpath(__file__)
    print("checking bit reader")
    checkbitreader()
    print("checking bit writer")
    checkbitwriter()
    layerfolder = os.path.join(b(b(b(b(scriptdir)))), "test", "layers")
    totalblocks = 0
    im = Image.new("L", (16*16, 16*16))
    for layer_file in os.listdir(layerfolder):
        #if not layer_file == "0.layer":
            #        continue
        f = open(os.path.join(layerfolder, layer_file), "rb")
        data = f.read()
        f.close()
        res = TerrainDecoder.decode(data)
        for layer in res:
            totalblocks += 1
            drawlayer(layer, totalblocks, im)
    im.save("/tmp/terrain/all.png")
    print("TOTAL", totalblocks)
    print("TOTAL", enctime, dectime, iters)
    print("TOTAL", enctime/float(iters), dectime/float(iters))
