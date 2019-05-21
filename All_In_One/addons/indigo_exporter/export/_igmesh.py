"""
Pure igmesh implementations
"""

def make_format(letter, count):
    return '<%i%s' % (count, letter)

class igmesh():
    '''
    Reads and writes .igmesh binary files.
    
    When writing, this class ASSUMES that the data held in
    it's member vars is exactly correct. No mesh data
    validation is performed other than
    - Check magic number
    - Check num_vert_normals is either ==0 or ==num_vert_positions
    
    Example usage:
    imr = igmesh()
    imr.load('mesh.igmesh')        # Load from file
    print(imr)                     # Prints out mesh info
    
    imr.save('re-mesh.igmesh') # Save to file
    print('Wrote %s bytes' % len(imr))
    
    The calling script should handle exceptions raised by this class,
    no exception handling is done here.
    '''
    
    debug = False
    
    # I/O control vars
    bytes_read = 0
    bytes_written = 0
    data_length = 0
    file_handle = None
    
    # binary data format strings
    I1 = make_format('I', 1)
    I3 = make_format('I', 3)
    f1 = make_format('f', 1)
    f2 = make_format('f', 2)
    f3 = make_format('f', 3)
    
    # .igmesh vars
    def reset(self):
        self.magic_number = 5456751
        self.format_version = 1
        self.num_uv_mappings = 0
        self.num_used_materials = 0
        self.used_materials = []
        self.num_uv_set_expositions = 0
        self.uv_set_expositions = {}
        self.num_vert_positions = 0
        self.vert_positions = []
        self.num_vert_normals = 0
        self.vert_normals = []
        self.num_uv_pairs = 0
        self.uv_pairs = []
        self.num_triangles = 0
        self.triangles = []
    
    def __init__(self):
        from struct import calcsize, pack, unpack
        self.pack = pack
        self.unpack = unpack
        self.calcsize = calcsize
        
        self.reset()
    
    def make_format(self, letter, count):
        return '<%i%s' % (count, letter)
    
    def get_chunk(self, length):
        c = self.file_handle.read(length)
        self.bytes_read += length
        return c
    
    def decode_header(self, headerbytes):
        self.magic_number, self.format_version, self.num_uv_mappings = self.unpack(self.I3, headerbytes)
    
    def decode_string(self):
        char8_length  = self.calcsize('c')
        length = self.decode_uint32()
        strg = self.unpack(make_format('c', char8_length*length), self.get_chunk(length))
        return ''.join([c.decode() for c in strg])
    
    def decode_uint32(self):
        uint32_length = self.calcsize('I')
        int32, = self.unpack(self.I1, self.get_chunk(uint32_length))
        return int32
    
    def decode_vec3f(self):
        float_length = self.calcsize('f')
        return self.unpack(self.f3, self.get_chunk(float_length*3))
    
    def decode_vec2f(self):
        float_length = self.calcsize('f')
        return self.unpack(self.f2, self.get_chunk(float_length*2))
    
    def decode_triangle(self):
        vertex_indices = [0,0,0]
        for i in range(3):
            vertex_indices[i] = self.decode_uint32()
            
        uv_indices = [0,0,0]
        for i in range(3):
            uv_indices[i] = self.decode_uint32()
            
        mat_index = self.decode_uint32()
        
        return {
            'vertex_indices': vertex_indices,
            'uv_indices': uv_indices,
            'tri_mat_index': mat_index
        }
    
    def encode_uint32(self, val):
        self.file_handle.write( self.pack(self.I1, val) )
        self.bytes_written += self.calcsize('I')
    
    def encode_string(self, s):
        slen = len(s)
        self.encode_uint32(slen)
        cf = make_format('c', 1)
        for c in s:
            self.file_handle.write( self.pack(cf, ('%s'%c).encode()) )
        self.bytes_written += slen * self.calcsize('c')
    
    def encode_vec3f(self, vec3f):
        self.file_handle.write( self.pack(self.f3, *vec3f[:]) )
        self.bytes_written += 3 * self.calcsize('f')
    
    def encode_vec2f(self, vec2f):
        self.file_handle.write( self.pack(self.f2, *vec2f[:]) )
        self.bytes_written += 2 * self.calcsize('f')
    
    def encode_triangle(self, tri):
        self.file_handle.write( self.pack(self.I3, *tri['vertex_indices'] ))
        self.bytes_written += 3 * self.calcsize('I')
        
        self.file_handle.write( self.pack(self.I3, *tri['uv_indices'] ))
        self.bytes_written += 3 * self.calcsize('I')
        
        self.file_handle.write( self.pack(self.I1, tri['tri_mat_index'] ))
        self.bytes_written += self.calcsize('I')
    
    def save(self, filename):
        self.bytes_written = 0
        
        self.magic_number = 5456751
        self.format_version = 1
        
        self.num_vert_positions = len(self.vert_positions)
        if self.num_vert_positions == 0:
            raise Exception('No vertex data to write')
        
        self.num_vert_normals = len(self.vert_normals)
        if self.num_vert_normals != 0 and self.num_vert_normals != self.num_vert_positions:
            raise Exception('Incorrect number of vertex normals')
        
        self.file_handle = open(filename, 'wb')
        
        # Header
        self.encode_uint32(self.magic_number)
        self.encode_uint32(self.format_version)
        self.encode_uint32(self.num_uv_mappings)
        
        # Materials
        self.num_used_materials = len(self.used_materials)
        self.encode_uint32(self.num_used_materials)
        for s in self.used_materials:
            self.encode_string(s)
        
        # UV Expositions
        usei = self.uv_set_expositions.items()
        self.num_uv_set_expositions = len(usei)
        self.encode_uint32(self.num_uv_set_expositions)
        for ind,name in usei:
            self.encode_string(name)
            self.encode_uint32(ind)
        del usei
        
        # Vert Positions
        self.encode_uint32(self.num_vert_positions)
        for vp in self.vert_positions:
            self.encode_vec3f(vp)
        
        # Vert Normals
        self.encode_uint32(self.num_vert_normals)
        for vn in self.vert_normals:
            self.encode_vec3f(vn)
        
        # UV Pairs
        self.num_uv_pairs = len(self.uv_pairs)
        self.encode_uint32(self.num_uv_pairs)
        for uvp in self.uv_pairs:
            self.encode_vec2f(uvp)
        
        # Triangles
        self.num_triangles = len(self.triangles)
        self.encode_uint32(self.num_triangles)
        for tri in self.triangles:
            self.encode_triangle(tri)
        
        self.file_handle.close()
        
        # Update data_length so that len(self) is correct
        self.data_length = self.bytes_written
        
        if self.debug:
            print(self)
            #print(self.triangles)
        
        return self.bytes_written
    
    def load(self, filename):
        self.reset()
        self.bytes_read = 0
        
        from os.path import getsize
        self.data_length = getsize(filename)
        
        self.file_handle = open(filename, 'rb')
        
        # Header
        uint32_length = self.calcsize('I')
        self.decode_header(
            self.get_chunk(uint32_length*3)
        )
        
        if self.magic_number != 5456751:
            raise Exception('Invalid IGMESH File')
        
        # Materials
        self.num_used_materials = self.decode_uint32()
        for i in range(self.num_used_materials):            #@UnusedVariable
            strg = self.decode_string()
            self.used_materials.append(strg)
        
        # UV Expositions
        self.num_uv_set_expositions = self.decode_uint32()
        for i in range(self.num_uv_set_expositions):        #@UnusedVariable
            name = self.decode_string()
            ind = self.decode_uint32()
            self.uv_set_expositions[ind] = name
        
        # Vert Positions
        self.num_vert_positions = self.decode_uint32()
        for i in range(self.num_vert_positions):            #@UnusedVariable
            self.vert_positions.append(self.decode_vec3f())
        
        # Vert Normals
        self.num_vert_normals = self.decode_uint32()
        for i in range(self.num_vert_normals):                #@UnusedVariable
            self.vert_normals.append(self.decode_vec3f())
        
        # UV Pairs
        self.num_uv_pairs = self.decode_uint32()
        for i in range(self.num_uv_pairs):                    #@UnusedVariable
            self.uv_pairs.append(self.decode_vec2f())
        
        # Triangles
        self.num_triangles = self.decode_uint32()
        for i in range(self.num_triangles):                    #@UnusedVariable
            self.triangles.append(self.decode_triangle())
        
        self.file_handle.close()
        
        if not self.data_length == self.bytes_read:
            raise Exception('IGMESH data not read completely')
    
    def __len__(self):
        return int(self.data_length)
    
    def __str__(self):
        return '''<igmesh
    Magic Number:            %s
    Format Version:            %s
    Num UV Mappings:        %s
    Num Used Materials:        %s
    Used Materials:            %s
    Num UV Set Expositions:    %s
    UV Set Expositions:        %s
    Num vert positions:        %s
    Vert positions:            <list length %i>
    Num Vert Normals:        %s
    Vert Normals:            <list length %i>
    Num UV Pairs:            %s
    UV Pairs:                <list length %i>
    Num Triangles:            %s
    Triangles:                <list length %i>
    Data size:                %s bytes
>''' % (
        self.magic_number,
        self.format_version,
        self.num_uv_mappings,
        self.num_used_materials,
        self.used_materials,
        self.num_uv_set_expositions,
        self.uv_set_expositions,
        self.num_vert_positions,
        len(self.vert_positions),
        self.num_vert_normals,
        len(self.vert_normals),
        self.num_uv_pairs,
        len(self.uv_pairs),
        self.num_triangles,
        len(self.triangles),
        len(self)
        )

class igmesh_stream(igmesh):
    '''
    Version of above, but streams data to disk rather
    then storing mesh data in local object first.
    
    All methods in this object need to be called in sequence,
    and the correct number of times.
    
    SEQUENCE CHECKS ARE DISABLED FOR METHODS THAT ARE CALLED
    LARGE NUMBERS OF TIMES (UNLESS IN DEBUG MODE):
        ADD_VERT_POSITION
        ADD_VERT_NORMAL
        ADD_UV_PAIR
        ADD_TRIANGLE
    '''
    
    SEQ            = None    # current sequence number
    SEQ_MN        = 1        # magic number
    SEQ_FV        = 2        # format version
    SEQ_NUVM    = 3        # num_uv_mappings
    SEQ_NUM        = 4        # num_used_materials
    SEQ_UM        = 5        # used_materials
    SEQ_NUSE    = 6        # num_uv_set_expositions
    SEQ_USE        = 7        # uv_set_expositions
    SEQ_NVP        = 8        # num_vert_positions
    SEQ_VP        = 9        # vert_positions
    SEQ_NVN        = 10    # num_vert_normals
    SEQ_VN        = 11    # vert_normals
    SEQ_NUP        = 12    # num_uv_pairs
    SEQ_UP        = 13    # uv_pairs
    SEQ_NT        = 14    # num_triangles
    SEQ_T        = 15    # triangles
    SEQ_END        = 16    # END
    
    def __init__(self, filename):
        super().__init__()
        self.file_handle = open(filename, 'wb')
        self.add_header()
        # file is closed after last triangle written
    
    def finish(self):
        # Update data_length so that len(self) is correct
        self.data_length = self.bytes_written
        if self.debug:
            print(self) # This should output zeros and empty lists, but data_length will be correct
        self.file_handle.close()
    
    def check_sequence(self, SEQ_E):
        if self.SEQ != SEQ_E or self.SEQ >= self.SEQ_END:
            self.finish()
            raise Exception('IGMesh Stream sequence error (%i called, expected %i)' % (SEQ_E, self.SEQ))
    
    def add_header(self):
        self.encode_uint32(self.magic_number)
        self.encode_uint32(self.format_version)
        self.SEQ = self.SEQ_NUVM
    
    def add_num_uv_mappings(self, val):
        self.check_sequence(self.SEQ_NUVM)
        self.encode_uint32(val)
        self.SEQ+=1
    
    def add_num_used_materials(self, val):
        self.check_sequence(self.SEQ_NUM)
        self.encode_uint32(val)
        self.num_used_materials = val
        self.SEQ+=1
        if val == 0: self.SEQ+=1
    
    def add_used_material(self, s):
        self.check_sequence(self.SEQ_UM)
        self.encode_string(s)
        self.num_used_materials-=1
        if self.num_used_materials == 0:
            self.SEQ+=1
    
    def add_num_uv_set_expositions(self, val):
        self.check_sequence(self.SEQ_NUSE)
        self.encode_uint32(val)
        self.num_uv_set_expositions = val
        self.SEQ+=1
        if val == 0: self.SEQ+=1
    
    def add_uv_set_exposition(self, name, index):
        self.check_sequence(self.SEQ_USE)
        self.encode_string(name)
        self.encode_uint32(index)
        self.num_uv_set_expositions-=1
        if self.num_uv_set_expositions == 0:
            self.SEQ+=1
    
    def add_num_vert_positions(self, val):
        self.check_sequence(self.SEQ_NVP)
        self.encode_uint32(val)
        self.num_vert_positions = val
        self.SEQ+=1
        if val == 0: self.SEQ+=1
    
    def add_vert_position(self, vec3f):
        if self.debug: self.check_sequence(self.SEQ_VP)
        self.encode_vec3f(vec3f)
        self.num_vert_positions-=1
        if self.num_vert_positions == 0:
            self.SEQ+=1

    def add_vert_position_fast(self, vec3f):
        self.file_handle.write(self.pack(self.f3, *vec3f[:]))

    def add_num_vert_normals(self, val):
        self.check_sequence(self.SEQ_NVN)
        self.encode_uint32(val)
        self.num_vert_normals = val
        self.SEQ+=1
        if val == 0: self.SEQ+=1
    
    def add_vert_normal(self, vec3f):
        if self.debug: self.check_sequence(self.SEQ_VN)
        self.encode_vec3f(vec3f)
        self.num_vert_normals-=1
        if self.num_vert_normals == 0:
            self.SEQ+=1

    def add_vert_normal_fast(self, vec3f):
        self.file_handle.write(self.pack(self.f3, *vec3f[:]))
    
    def add_num_uv_pairs(self, val):
        self.check_sequence(self.SEQ_NUP)
        self.encode_uint32(val)
        self.num_uv_pairs = val
        self.SEQ+=1
        if val == 0: self.SEQ+=1
    
    def add_uv_pair(self, vec2f):
        if self.debug: self.check_sequence(self.SEQ_UP)
        self.encode_vec2f(vec2f)
        self.num_uv_pairs -= 1
        if self.num_uv_pairs == 0:
            self.SEQ+=1
    
    def add_uv_pair_fast(self, vec2f):
        self.file_handle.write(self.pack(self.f2, *vec2f[:]))
    
    def add_num_triangles(self, val):
        #if self.debug:
        #    print('<igmesh %i triangles>'%val)
        self.check_sequence(self.SEQ_NT)
        self.encode_uint32(val)
        self.num_triangles = val
        self.SEQ+=1
        if val == 0: self.SEQ+=1
    
    def add_triangle(self, tri):
        if self.debug: self.check_sequence(self.SEQ_T)
        self.encode_triangle(tri)
        self.num_triangles -= 1
        if self.num_triangles == 0:
            self.SEQ+=1
            self.finish()

    def add_triangle_fast(self, vert_idx, uv_idx, mat_idx):

        self.file_handle.write( self.pack(self.I3, *vert_idx ))
        self.file_handle.write( self.pack(self.I3, *uv_idx ))
        self.file_handle.write( self.pack(self.I1, mat_idx ))

        self.bytes_written += 7 * 4 #7 * self.calcsize('I')