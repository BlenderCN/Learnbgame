from . import iffFile
from . import vector3D

import struct

class vertex(object):
    __slots = ('vertex', 'normal', 'color', 'texs')
    def __init__(self):
        self.texs = []
        self.vertex = None
        self.normal = None
        self.color = None

class triangle(object):
    __slots__ = ('p1', 'p2', 'p3')

class mshFile(object):
    __slots__ = ('box', 'sphr', 'cyln', 'groups')
    
    def __init__(self):
        self.box = None
        self.sphr = None
        self.cyln = None
        self.groups = []
    
    def interpret_folder(self, name, size):
        pass
    
    def interpret_file(self, name, size, f):
        if name == 'BOX ':
            self.box = (iffFile.raw.read_float(f),iffFile.raw.read_float(f),iffFile.raw.read_float(f),
                        iffFile.raw.read_float(f),iffFile.raw.read_float(f),iffFile.raw.read_float(f))
        elif name == '0001SPHR':
            self.sphr = (iffFile.raw.read_float(f),iffFile.raw.read_float(f),iffFile.raw.read_float(f),\
                         iffFile.raw.read_float(f))
        elif name == '0003INFO':
            f.read(4)
            self.groups.append([[None]*iffFile.raw.read_int32(f), None, None])
        elif name == 'DATA':
            vert_count = len(self.groups[-1][0])
            bpv = ((size // vert_count) - 24)//4
            has_color = bpv % 2 == 1
            if(has_color):
                bpv -= 1
            for i in range(vert_count):
                v = vertex()
                v.vertex = vector3D.Vector3D(iffFile.raw.read_float(f), iffFile.raw.read_float(f), iffFile.raw.read_float(f))
                v.normal = vector3D.Vector3D(iffFile.raw.read_float(f), iffFile.raw.read_float(f), iffFile.raw.read_float(f))
                if(has_color):
                    v.color = f.read(4)
                for j in range(bpv//2):
                    v.texs.append((iffFile.raw.read_float(f), iffFile.raw.read_float(f)))
                self.groups[-1][0][i] = v
        elif name == 'INDX':
            indx = []
            count = iffFile.raw.read_int32(f)
            bpi = (size - 4) // count
            for i in range(count//3):
                tri = triangle()
                if(bpi == 2):
                    tri.p1 = iffFile.raw.read_int16(f)
                    tri.p2 = iffFile.raw.read_int16(f)
                    tri.p3 = iffFile.raw.read_int16(f)
                elif(bpi == 4):
                    tri.p1 = iffFile.raw.read_int32(f)
                    tri.p2 = iffFile.raw.read_int32(f)
                    tri.p3 = iffFile.raw.read_int32(f)
                indx.append(tri)
            self.groups[-1][1] = indx
        else:
            f.read(size)
    
    def _genSphereData(self):
        return struct.pack('ffff', self.sphr[0], self.sphr[1], self.sphr[2], self.sphr[3])
        
    def _genBoxData(self):
        return struct.pack('ffffff', self.box[0], self.box[1], self.box[2], self.box[3], self.box[4], self.box[5])
    
    def _genCNTData(self):
        return struct.pack('<I', len(self.groups))
    
    def _genLowInfo(self, group_id):
        return struct.pack('<II', 4357, len(self.groups[group_id][0]))
    
    def _genData(self, group_id):
        vert_data = self.groups[group_id][0]
        
        result = b''
        for vert in vert_data:
            result += struct.pack('ffffff', vert.vertex.x, vert.vertex.y, vert.vertex.z, vert.normal.x, vert.normal.y, vert.normal.z)
            if vert.color != None:
                result += vert.color
            for tex in vert.texs:
                result += struct.pack('ff', tex[0], tex[1])
        return result;
        
    def _genINDX(self, group_id):
        face_data = self.groups[group_id][1]
        
        result = struct.pack('<I', len(face_data)*3)
        
        for face in face_data:
            result += struct.pack('HHH', face[0], face[1], face[2])
            
        return result
    
    def build_tree(self):
    
        #prep the skeleton
        head = iffFile.folder_node("FORM")
        mesh_form = iffFile.folder_node("MESHFORM").parent(head)
        
        #meta complex
        meta_form = iffFile.folder_node("0005FORM").parent(mesh_form)
        appr_form = iffFile.folder_node("APPRFORM").parent(meta_form)
        
        #actual meta
        #bounding
        bounding_form = iffFile.folder_node("0003FORM").parent(appr_form)
        
        bounding_box_form = iffFile.folder_node("EXBXFORM").parent(bounding_form)
        
        if self.sphr != None:
            sphr_form_form = iffFile.folder_node("0001FORM").parent(bounding_box_form)
            sphr_form = iffFile.folder_node("EXSPFORM").parent(sphr_form_form)
            iffFile.file_node("0001SPHR", self._genSphereData()).parent(sphr_form)
        
        if self.box != None:
            iffFile.file_node("BOX ", self._genBoxData()).parent(bounding_box_form)
        
        #null
        null_form = iffFile.file_node("FORM", b'NULL').parent(appr_form)
        
        #hardpoints
        hardpoint_form = iffFile.file_node("FORM", b'HPTS').parent(appr_form)
        
        #collision
        collision_form = iffFile.folder_node("FORM").parent(appr_form)
        iffFile.file_node("FLORDATA", b'\x00').parent(collision_form)
        
        #mesh complex
        data_form_form = iffFile.folder_node("FORM").parent(mesh_form)
        data_form = iffFile.folder_node("SPS FORM").parent(data_form_form)
        
        iffFile.file_node("0001CNT ", self._genCNTData()).parent(data_form)
        
        for i in range(len(self.groups)):
        
            group = self.groups[i]
            high_form = iffFile.folder_node("FORM").parent(data_form)
            
            shader_name = ''
            iffFile.file_node("%04dNAME" % (i+1), struct.pack(str(len(shader_name)+1)+'s', shader_name.encode('ascii'))).parent(high_form)
            iffFile.file_node("INFO", b'\x01\x00\x00\x00').parent(high_form)
            
            mid_form = iffFile.folder_node("FORM").parent(high_form)
            
            iffFile.file_node("0001INFO", b'\x09\x00\x00\x00\x01\x00').parent(mid_form)
        
            low_form = iffFile.folder_node("FORM").parent(mid_form)
        
            vtxa_form = iffFile.folder_node("VTXAFORM").parent(low_form)
            
            iffFile.file_node("0003INFO", self._genLowInfo(i)).parent(vtxa_form)
            iffFile.file_node("DATA", self._genData(i)).parent(vtxa_form)
            
            if group[1] != None:
                iffFile.file_node("INDX", self._genINDX(i)).parent(mid_form)
        
            if group[2] != None:
                pass #not supported yet
        
        return head