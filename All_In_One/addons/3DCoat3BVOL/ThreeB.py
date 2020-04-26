# 3D-Coat .3b file utility
import sys
import os
from struct import unpack
from array import array
from xml.etree import ElementTree

class ThreeBAABB:
    def __init__(self, datatype, minval, maxval):
        self.min = array(datatype, [maxval, maxval, maxval])
        self.max = array(datatype, [minval, minval, minval])
    
    def update(self, x, y, z):
        self.min[0] = min(self.min[0], x)
        self.min[1] = min(self.min[1], y)
        self.min[2] = min(self.min[2], z)
        self.max[0] = max(self.max[0], x)
        self.max[1] = max(self.max[1], y)
        self.max[2] = max(self.max[2], z)
    
    def union(self, aabb):
        self.min[0] = min(self.min[0], aabb.min[0])
        self.min[1] = min(self.min[1], aabb.min[1])
        self.min[2] = min(self.min[2], aabb.min[2])
        self.max[0] = max(self.max[0], aabb.max[0])
        self.max[1] = max(self.max[1], aabb.max[1])
        self.max[2] = max(self.max[2], aabb.max[2])
    
    def has_volume(self):
        ret  = self.min[0] < self.max[0]
        ret &= self.min[1] < self.max[1]
        ret &= self.min[2] < self.max[2]
        return ret
    
    def __str__(self):
        return "(min({},{},{}), max({},{},{}))".format(self.min[0], self.min[1], self.min[2], self.max[0], self.max[1], self.max[2])

# VOL3 chunk data structures
# Volume
#  cells: list of ThreeBVOL3Cell
#  representation: 0: Voxel mode, 256: Surface mode
#  cell_AABB: AABB of cells (cell needs (max - min + 1) * 8 memory area)
#  effect_AABB: AABB of cells (cell needs (max - min + 1) * 8 memory area)
#  num_vertices: number of surface vertices
#  num_vaces: number of surface triangle faces
#  num_init_vertices: number of initial surface vertices
class ThreeBVOL3Volume:
    def __init__(self, f, chunkinfo):
        tmp = unpack("<LffffffffffffffffL", f.read(18 * 4))
        self.space_ID = tmp[0]
        self.transform = array("f", tmp[1:17])
        self.volume_name = f.read(tmp[17]).decode()[:-1] # \0 terminated
        tmp = unpack("<LLLL", f.read(4 * 4))
        self.default_color = tmp[0]
        self.representation = tmp[1]
        self.hidden_index = tmp[2] - 1    # "Hide" brush's layer index + 1 or 0
        shaderinfo = f.read(tmp[3]).split(b'\0')
        self.shader_name = shaderinfo[0].decode()
        self.shader_settings = shaderinfo[1].decode()
        tmp = unpack("<LL", f.read(4 * 2))
        cellcount = tmp[0]
        self.skiped_DWORD = tmp[1]
        
        #print("--- {1}(spaceID {0}) -----".format(self.space_ID, self.volume_name))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[0], self.transform[1], self.transform[2], self.transform[3]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[4], self.transform[5], self.transform[6], self.transform[7]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[8], self.transform[9], self.transform[10], self.transform[11]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[12], self.transform[13], self.transform[14], self.transform[15]))
        #print("default color: {0:X}".format(self.default_color))
        #print("representation: {0}({1})".format(self.representation, "Surface" if self.representation == 256 else "Volume"))
        #print("hidden index: {0}".format(self.hidden_index))
        #print("shader name: {0}, (with setting info:{1} bytes)".format(self.shader_name, len(self.shader_settings)))
        #print("number of cells: {0}".format(cellcount))
        #print("skiped DWORD: 0x{0:08X}".format(self.skiped_DWORD))
        
        self.cell_AABB = ThreeBAABB("l", -sys.maxsize, sys.maxsize)
        self.effect_AABB = ThreeBAABB("l", -sys.maxsize, sys.maxsize)
        self.num_vertices = 0
        self.num_faces = 0
        self.num_init_vertices = 0
        self.cells = []
        while cellcount > 0:
            #print("--- cell[{0}/{1}] tell:{2} ---".format(len(self.cells), cellcount, f.tell()))
            tmpcell = ThreeBVOL3Cell(f, chunkinfo)
            self.cells.append(tmpcell)
            self.cell_AABB.update(tmpcell.x, tmpcell.y, tmpcell.z)
            # 3D-Coat make surfaces at volume density is 32767.5
            if tmpcell.max_cell_value > 32767:
                self.effect_AABB.update(tmpcell.x, tmpcell.y, tmpcell.z)
            if tmpcell.has_surface:
                self.num_vertices += len(tmpcell.surface_vertices) / 7
                self.num_faces += len(tmpcell.surface_indices) / 3
                self.num_init_vertices += len(tmpcell.initial_vertices) / 7
            cellcount -= 1
        #print("{} cells read".format(len(self.cells)))
        #print("cell AABB:{}".format(self.cell_AABB))
        # Uknown bytes
        if chunkinfo.version > 5:
            self.terminater_WORD = unpack("<H", f.read(2))
    

# Cell
#  x, y, z: position / 8
#  data: cell values. unsigned short array[9 * 9 * 9]
#  has_surface: bool
#  max_cell_value: max contains cell value
# when cell is surface mode
#  surface_vertices : surface vertices list. (float array[position:3 + normal:3 + unknown:1]) * n
#  surface_indices : surface triangle indices array. short * n
#  initial_vertices : surface vertices list. (float array[position:3 + normal:3 + unknown:1]) * n
class ThreeBVOL3Cell:
    def __init__(self, f, chunkinfo):
        if chunkinfo.version > 5:
            tmp = unpack("<Hlll", f.read(2 + 4 * 3))
            self.signature = tmp[0] # 0xCE11
            self.x = tmp[1]
            self.y = tmp[2]
            self.z = tmp[3]
            #print("word:0x{0:04X}, position:{1:08X},{2:08X},{3:08X}".format(self.v6WORD0, self.x, self.y, self.z))
        else:
            tmp = unpack("<hhh", f.read(2 * 3))
            self.x = tmp[0]
            self.y = tmp[1]
            self.z = tmp[2]
        
        tmp = unpack("<BBB", f.read(3))
        self.side = tmp[0]          # "Should be 9"
        self.cell_flags = tmp[1]    # 0x1: cell has at least one 0. 0x02: ... one non-zero. 0x04: hidden. 0x08: surface mode
        self.data_flags = tmp[2]    # If 0, cells are filled same value
        self.data = array('H')
        cellsize = 9 * 9 * 9
        
        self.has_surface = ((self.cell_flags & 0x08) != 0)
        
        #print("position:{0},{1},{2}".format(self.x, self.y, self.z))
        #print("side:{0}".format(self.side))
        #print("cellflag:0x{0:02X}".format(self.cell_flags))
        #print("dataflag:0x{0:02X}".format(self.data_flags))
        
        fillvalue = unpack("<H", f.read(2))[0]
        if self.data_flags == 0:
            # fill cells same value
            self.max_cell_value = fillvalue
            i = 0
            while i < cellsize:
                self.data.append(fillvalue)
                i += 1
        else:
            # unpack cell values
            preval = unpack("<H", f.read(2))[0]
            self.data.append(preval)
            i = 1
            self.max_cell_value = preval
            while i < cellsize:
                sz = unpack("<B", f.read(1))[0]
                #print("sz: {}, preval:{}".format(sz, preval))
                if sz >= 220:
                    sz = sz - 220
                    while sz > 0:
                        curval = unpack("<H", f.read(2))[0]
                        val = (preval + curval) & 65535
                        #print("[{}]:{},{},{}".format(i, preval, curval, val))
                        self.data.append(val)
                        preval = val
                        self.max_cell_value = max(preval, self.max_cell_value)
                        sz -= 1
                        i += 1
                else:
                    while sz > 0:
                        self.data.append(preval)
                        sz -= 1
                        i += 1
        
        # when surface representation
        if self.has_surface:
            #print("this cell has surfaces")
            # surface vertices. 7 floats is 1 vertex data set. (position x, y, z, normal x, y, z, unknown)
            tmp = unpack("<L", f.read(4))[0] * 7
            #print("surface vertices: {0} (tell:{1})".format(tmp, f.tell() - 4))
            self.surface_vertices = unpack("<{}f".format(tmp), f.read(tmp * 4))
            
            # face indeces.    
            tmp = unpack("<L", f.read(4))[0]
            #print("surface indices: {0}(tell:{1})".format(tmp, f.tell() - 4))
            self.surface_indices = unpack("<{}H".format(tmp), f.read(tmp * 2))            
            
            # initial surface vertices(?). 7 floats earch
            tmp = unpack("<L", f.read(4))[0] * 7
            #print("initial vertices: {0}(tell:{1})".format(tmp, f.tell() - 4))
            self.initial_vertices = unpack("<{}f".format(tmp), f.read(tmp * 4) )

# chunk data abstract class
class ThreeBChunkData:
    pass

# chunk structure
class ThreeBChunk:
    signature = None
    data_length = 0
    chunk_offset = 0
    data_offset = 0
    data = None
        
    def __init__(self, tbfile):
        self.chunk_offset = tbfile.tell()
        buf = tbfile.read(8)
        if len(buf) < 8:
            return
        tmp = unpack("<4sL", buf)
        self.signature = tmp[0][::-1].decode()
        self.data_length = tmp[1]
        self.data_offset = tbfile.tell()
        #print("{0}:{1}({2})[tell:{3}] ".format(self.signature, self.data_length, self.chunk_offset, tbfile.tell()))
        
        if self.signature == "MESH":
            self._read_MESH(tbfile)
        elif self.signature == "VOL3":
            self._read_VOL3(tbfile)
        else:
            tbfile.seek(self.data_length, os.SEEK_CUR)
    
    # MESH chunk (3b file magic signature)
    # dataLength is always 1. but no data blocks.
    def _read_MESH(self, f):
        self.data_length = 0
    
    # VOL3 chunk (Voxel data chunk)
    #  chunk.version : data version (6 or later is experimental)
    #  chunk.flags : data flags ()
    #  chunk.volumes : volume datas dictionary (key:VoxelID(string))
    #  chunk.VoxTreeXML : VoxTree info XML data
    def _read_VOL3(self, f):
        tmpdat = ThreeBChunkData()
        
        buf = f.read(8)
        tmp = unpack("<LL", buf)
        tmpdat.version = tmp[0] & 0b111111
        tmpdat.flags = tmp[0] & 0x111000000
        volume_amount = tmp[1]
        tmpdat.volumes = {}
        
        #print("VOL3 (version:{0}, volume amount:{1})".format(tmpdat.version, volume_amount))
        
        while volume_amount > 0:
            #print("read Volume[{0}]. start from {1}".format(len(tmpdat.volumes), f.tell()))
            tmpvol = ThreeBVOL3Volume(f, tmpdat)
            tmpdat.volumes.update({str(tmpvol.space_ID) : tmpvol})
            volume_amount -= 1
        
        #for k in tmpdat.volumes:
        #    tmpvol = tmpdat.volumes.get(k)
        #    print("Volume[{0}]: {1} ({2})".format(k, tmpvol.volume_name, tmpvol.space_ID))
        #print("{0} volume read".format(len(tmpdat.volumes)))
        
        tmp = unpack("<L", f.read(4))[0]
        #print("({})VoxTreeXML :{}".format(f.tell() - 4, tmp))
        tmpdat.VoxTreeXML = f.read(tmp)
        #print("VoxTreeXML: {0}...({1} bytes)".format(tmpdat.VoxTreeXML[:32], len(tmpdat.VoxTreeXML)))
        #print("--- end ---")
        
        self.data = tmpdat
        #+++++
        #f.seek( self.data_offset + self.data_length, os.SEEK_SET )

# Load 3D-Coat 3b file.
# currently supports VOL3 chunk
# return a dictionary that chunk signatures keyed.
def load_3bfile(filename):
    try:
        f = open(filename, "rb")
    except IOError as error:
        print(error)
        return {}
    else:
        filecontents = {}
        while True:
            chunk = ThreeBChunk(f)
            if chunk.signature == None:
                break
            filecontents.update({chunk.signature : chunk})
            #print("{0}:{1}".format(chunk.signature, chunk.dataLength))
        f.close()
        #for k in filecontents:
        #    tmpchunk = filecontents.get(k)
        #    print("{0}: {1} (offset:{2})".format(tmpchunk.signature, tmpchunk.data_length, tmpchunk.chunk_offset))
        #volchunk = filecontents.get("VOL3")
        #print("VoxTreeXML:\n{0}".format(volchunk.data.VoxTreeXM))
        return filecontents

# VoxTree
class VoxTreeBranch:
    transform = array('f', (1.0, 0.0, 0.0, 0.0,  0.0, 1.0, 0.0, 0.0,  0.0, 0.0, 1.0, 0.0,  0.0, 0.0, 0.0, 1.0))
    name = ""
    volume_data = None
    childs = None
    
    def __init__(self, xmlelem, chunkdata):
        if xmlelem.tag != "VoxTreeBranch":
            print("Not a voxel tree definition")
            return
        
        self.transform = array('f', (1.0, 0.0, 0.0, 0.0,  0.0, 1.0, 0.0, 0.0,  0.0, 0.0, 1.0, 0.0,  0.0, 0.0, 0.0, 1.0))
        for i in range(16):
            self.transform[i] = float(xmlelem.find( "Tr{}".format(i) ).text)
        self.name = xmlelem.find("Name").text
        self.volume_data = chunkdata.volumes.get(xmlelem.find("VobID").text, None)
        childobjs = xmlelem.find("ChildObjects")
        
        #print("{}".format(self.name))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[0], self.transform[1], self.transform[2], self.transform[3]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[4], self.transform[5], self.transform[6], self.transform[7]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[8], self.transform[9], self.transform[10], self.transform[11]))
        #print("|{0:.4f} {1:.4f} {2:.4f} {3:.4f}|".format(self.transform[12], self.transform[13], self.transform[14], self.transform[15]))
        #if self.volume_data:
        #    print("volumeID: {}".format(self.volume_data.space_ID))
        #    print("num of cells: {0}, AABB: {1}".format(len(self.volume_data.cells), self.volume_data.cell_AABB))
        #    if self.volume_data.representation == 256:
        #        print("surface vertices: {}".format(self.volume_data.num_vertices))
        #        print("surface faces: {}".format(self.volume_data.num_faces))
        #        print("initial surface vertices: {}".format(self.volume_data.num_init_vertices))
        #else:
        #    print("No Volume data")
        #print("{} childs".format(len(childobjs)))
        
        if len(childobjs) > 0:
            self.childs = []
            for childvoxelm in childobjs:
                self.childs.append(VoxTreeBranch(childvoxelm, chunkdata))
        
# Create VoxTree from loaded file's VoxTreeXML data.
def create_VoxTree(contents):
    chunkdata = contents.get("VOL3").data
    if chunkdata == None:
        return None
    
    #print(chunkdata.VoxTreeXML)
    # [Hack]. VoxTreeXML has <+></+> tag. It is a illegal tag for XML parser.
    escvoxxml = chunkdata.VoxTreeXML.replace(b"+>", b"p>")
    #print(escvoxxml)
    voxxml = ElementTree.fromstring(escvoxxml)
    
    #print("RootTag: {}".format(voxxml.tag))
    #for elm in voxxml:
    #    print(elm.tag)
    ret = VoxTreeBranch(voxxml, chunkdata)
    
    return ret
