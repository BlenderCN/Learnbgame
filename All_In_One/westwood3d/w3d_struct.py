import struct

def b2s(str):
    return str.split(b'\0')[0].decode('utf-8')
def s2b(str, s=None):
    str = str.encode('utf-8')
    if s is not None and len(str) >= s:
        str = str[:s - 1]
    return str + b'\0'
def ver(major, minor):
    return (((major) << 16) | (minor))

w3d_keys = {
    0x00000000: 'MESH',
    0x00000002: 'VERTICES',
    0x00000003: 'VERTEX_NORMALS',
    0x0000000C: 'MESH_USER_TEXT',
    0x0000000E: 'VERTEX_INFLUENCES',
    0x0000001F: 'MESH_HEADER3',
    0x00000020: 'TRIANGLES',
    0x00000022: 'VERTEX_SHADE_INDICES',

    0x00000023: 'PRELIT_UNLIT',
    0x00000024: 'PRELIT_VERTEX',
    0x00000025: 'PRELIT_LIGHTMAP_MULTI_PASS',
    0x00000026: 'PRELIT_LIGHTMAP_MULTI_TEXTURE',

    0x00000028: 'MATERIAL_INFO',

    0x00000029: 'SHADERS',

    0x0000002A: 'VERTEX_MATERIALS',
    0x0000002B: 'VERTEX_MATERIAL',
    0x0000002C: 'VERTEX_MATERIAL_NAME',
    0x0000002D: 'VERTEX_MATERIAL_INFO',
    0x0000002E: 'VERTEX_MAPPER_ARGS0',
    0x0000002F: 'VERTEX_MAPPER_ARGS1',

    0x00000030: 'TEXTURES',
    0x00000031: 'TEXTURE',
    0x00000032: 'TEXTURE_NAME',
    0x00000033: 'TEXTURE_INFO',
        
    0x00000038: 'MATERIAL_PASS',
    0x00000039: 'VERTEX_MATERIAL_IDS',
    0x0000003A: 'SHADER_IDS',
    0x0000003B: 'DCG',
    0x0000003C: 'DIG',
    0x0000003E: 'SCG',

    0x00000048: 'TEXTURE_STAGE',
    0x00000049: 'TEXTURE_IDS',
    0x0000004A: 'STAGE_TEXCOORDS',
    0x0000004B: 'PER_FACE_TEXCOORD_IDS',


    0x00000058: 'DEFORM',
    0x00000059: 'DEFORM_SET',
    0x0000005A: 'DEFORM_KEYFRAME',
    0x0000005B: 'DEFORM_DATA',

    0x00000080: 'PS2_SHADERS',
    
    0x00000090: 'AABTREE',
    0x00000091: 'AABTREE_HEADER',
    0x00000092: 'AABTREE_POLYINDICES',
    0x00000093: 'AABTREE_NODES',

    0x00000100: 'HIERARCHY',
    0x00000101: 'HIERARCHY_HEADER',
    0x00000102: 'PIVOTS',
    0x00000103: 'PIVOT_FIXUPS',

    0x00000200: 'ANIMATION',
    0x00000201: 'ANIMATION_HEADER',       
    0x00000202: 'ANIMATION_CHANNEL',
    0x00000203: 'BIT_CHANNEL',

    0x00000280: 'COMPRESSED_ANIMATION',
    0x00000281: 'COMPRESSED_ANIMATION_HEADER',
    0x00000282: 'COMPRESSED_ANIMATION_CHANNEL',
    0x00000283: 'COMPRESSED_BIT_CHANNEL',

    0x000002C0: 'MORPH_ANIMATION',
    0x000002C1: 'MORPHANIM_HEADER',
    0x000002C2: 'MORPHANIM_CHANNEL',
    0x000002C3: 'MORPHANIM_POSENAME',
    0x000002C4: 'MORPHANIM_KEYDATA',
    0x000002C5: 'MORPHANIM_PIVOTCHANNELDATA',

    0x00000300: 'HMODEL',
    0x00000301: 'HMODEL_HEADER',
    0x00000302: 'NODE',
    0x00000303: 'COLLISION_NODE',
    0x00000304: 'SKIN_NODE',
    0x00000305: 'OBSOLETE_W3D_CHUNK_HMODEL_AUX_DATA',
    0x00000306: 'OBSOLETE_W3D_CHUNK_SHADOW_NODE',

    0x00000400: 'LODMODEL',
    0x00000401: 'LODMODEL_HEADER',
    0x00000402: 'LOD',

    0x00000420: 'COLLECTION',
    0x00000421: 'COLLECTION_HEADER',
    0x00000422: 'COLLECTION_OBJ_NAME',
    0x00000423: 'PLACEHOLDER',
    0x00000424: 'TRANSFORM_NODE',

    0x00000440: 'POINTS',

    0x00000460: 'LIGHT',
    0x00000461: 'LIGHT_INFO',
    0x00000462: 'SPOT_LIGHT_INFO',
    0x00000463: 'NEAR_ATTENUATION',
    0x00000464: 'FAR_ATTENUATION',

    0x00000500: 'EMITTER',
    0x00000501: 'EMITTER_HEADER',
    0x00000502: 'EMITTER_USER_DATA',
    0x00000503: 'EMITTER_INFO',
    0x00000504: 'EMITTER_INFOV2',
    0x00000505: 'EMITTER_PROPS',
    0x00000506: 'OBSOLETE_W3D_CHUNK_EMITTER_COLOR_KEYFRAME',
    0x00000507: 'OBSOLETE_W3D_CHUNK_EMITTER_OPACITY_KEYFRAME',
    0x00000508: 'OBSOLETE_W3D_CHUNK_EMITTER_SIZE_KEYFRAME',
    0x00000509: 'EMITTER_LINE_PROPERTIES',
    0x0000050A: 'EMITTER_ROTATION_KEYFRAMES',
    0x0000050B: 'EMITTER_FRAME_KEYFRAMES',
    0x0000050C: 'EMITTER_BLUR_TIME_KEYFRAMES',

    0x00000600: 'AGGREGATE',
    0x00000601: 'AGGREGATE_HEADER',
    0x00000602: 'AGGREGATE_INFO',
    0x00000603: 'TEXTURE_REPLACER_INFO',
    0x00000604: 'AGGREGATE_CLASS_INFO',

    0x00000700: 'HLOD',
    0x00000701: 'HLOD_HEADER',
    0x00000702: 'HLOD_LOD_ARRAY',
    0x00000703: 'HLOD_SUB_OBJECT_ARRAY_HEADER',
    0x00000704: 'HLOD_SUB_OBJECT',
    0x00000705: 'HLOD_AGGREGATE_ARRAY',
    0x00000706: 'HLOD_PROXY_ARRAY',

    0x00000740: 'BOX',
    0x00000741: 'SPHERE',
    0x00000742: 'RING',

    0x00000750: 'NULL_OBJECT',

    0x00000800: 'LIGHTSCAPE',
    0x00000801: 'LIGHTSCAPE_LIGHT',
    0x00000802: 'LIGHT_TRANSFORM',

    0x00000900: 'DAZZLE',
    0x00000901: 'DAZZLE_NAME',
    0x00000902: 'DAZZLE_TYPENAME',

    0x00000A00: 'SOUNDROBJ',
    0x00000A01: 'SOUNDROBJ_HEADER',
    0x00000A02: 'SOUNDROBJ_DEFINITION',
}

w3d_save_keys = {v:k for k, v in w3d_keys.items()}

class node:
    def __init__(self):
        self.children = []
        self.binary = None
        self.size = 0
    def read(self, file, size):
        self.children = parse_nodes(file, size)
    def write(self, file):
        file.write(struct.pack('LL',
            w3d_save_keys[self.type().upper()],
            self.size | 0x80000000
        ))
        if self.binary is not None:
            file.write(self.binary)
        for c in self.children:
            c.write(file)
    def pack(self):
        for c in self.children:
            c.pack()
            self.size += 8 + c.size
    def type(self):
        return self.__class__.__name__[5:]
    def log(self, max, indent=0):
        print(('\t'*indent) + self.type())
        
        indent += 1
        
        for key, value in self.__dict__.items():
            if key != 'children':
                print(('\t'*indent) + key + ' = ' + str(value))
        
        if indent < max:
            for n in self.children:
                n.log(max, indent)
    def add(self, type):
        c = globals()['node_' + type]()
        self.children.append(c)
        return c
    def get(self, name):
        for i in self.children:
            if i.type() == name:
                return i
        return None
    def getRec(self, name):
        for i in self.children:
            if i.type() == name:
                return i
            res = i.getRec(name)
            if res != None:
                return res
        return None
    def find(self, name):
        all = []
        for i in self.children:
            if i.type() == name:
                all.append(i)
        return all
    def findRec(self, name, all=None):
        if all == None:
            all = []
        for i in self.children:
            if i.type() == name:
                all.append(i)
            i.findRec(name, all)
        return all

class node_mesh(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_mesh_header3(node):
    def __init__(self):
        super(node_mesh_header3, self).__init__()
        self.Version = ver(4,2)
        self.Attributes = 0
        self.MeshName = 'UNTITLED'
        self.ContainerName = 'UNTITLED'
        self.NumTris = 0
        self.NumVertices = 0
        self.NumMaterials = 0
        self.NumDamageStages = 0
        self.SortLevel = 0
        self.PrelitVersion = 0
        self.FutureCounts = 0
        self.VertexChannels = 3
        self.FaceChannels = 1
        self.Min = (0,0,0)
        self.Max = (0,0,0)
        self.SphCenter = (0,0,0)
        self.SphRadius = 0
    def read(self, file, size):
        data = read_struct(file, 'LL16s16sLLLLlLLLL3f3f3ff')
        self.Version = data[0]
        self.Attributes = data[1]
        self.MeshName = b2s(data[2])
        self.ContainerName = b2s(data[3])
        self.NumTris = data[4]
        self.NumVertices = data[5]
        self.NumMaterials = data[6]
        self.NumDamageStages = data[7]
        self.SortLevel = data[8]
        self.PrelitVersion = data[9]
        self.FutureCounts = data[10]
        self.VertexChannels = data[11]
        self.FaceChannels = data[12]
        self.Min = (data[13], data[14], data[15])
        self.Max = (data[16], data[17], data[18])
        self.SphCenter = (data[19], data[20], data[21])
        self.SphRadius = data[22]
    def pack(self):
        self.binary = struct.pack('LL16s16sLLLLlLLLL3f3f3ff',
            self.Version,
            self.Attributes,
            s2b(self.MeshName, 16),
            s2b(self.ContainerName, 16),
            self.NumTris,
            self.NumVertices,
            self.NumMaterials,
            self.NumDamageStages,
            self.SortLevel,
            self.PrelitVersion,
            self.FutureCounts,
            self.VertexChannels,
            self.FaceChannels,
            self.Min[0],self.Min[1],self.Min[2],
            self.Max[0],self.Max[1],self.Max[2],
            self.SphCenter[0], self.SphCenter[1], self.SphCenter[2],
            self.SphRadius,
        )
        self.size += struct.calcsize('LL16s16sLLLLlLLLL3f3f3ff')
class node_vertices(node):
    def __init__(self):
        super(node_vertices, self).__init__()
        self.vertices = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, '3f')
            self.vertices.append((data[0], data[1], data[2]))
            size -= struct.calcsize('3f')
    def pack(self):
        self.binary = b''
        for v in self.vertices:
            self.binary += struct.pack('3f',
                v[0], v[1], v[2]
            )
            self.size += struct.calcsize('3f')
class node_vertex_normals(node):
    def __init__(self):
        super(node_vertex_normals, self).__init__()
        self.normals = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, '3f')
            self.normals.append((data[0], data[1], data[2]))
            size -= struct.calcsize('3f')
    def pack(self):
        self.binary = b''
        for v in self.normals:
            self.binary += struct.pack('3f',
                v[0], v[1], v[2]
            )
            self.size += struct.calcsize('3f')
class node_vertex_shade_indices(node):
    def __init__(self):
        super(node_vertex_shade_indices, self).__init__()
        self.ids = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, 'L')
            self.ids.append(data[0])
            size -= struct.calcsize('L')
    def pack(self):
        self.binary = b''
        for i in self.ids:
            self.binary += struct.pack('L',
                i
            )
            self.size += struct.calcsize('L')
class node_vertex_influences(node):
    def __init__(self):
        super(node_vertex_influences, self).__init__()
        self.influences = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, 'H6B')
            self.influences.append(data[0])
            size -= struct.calcsize('H6B')
    def pack(self):
        self.binary = b''
        for i in self.influences:
            self.binary += struct.pack('H6B',
                i, 0, 0, 0, 0, 0, 0
            )
            self.size += struct.calcsize('H6B')
class node_triangles(node):
    def __init__(self):
        super(node_triangles, self).__init__()
        self.triangles = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, '3LL3ff')
            self.triangles.append({
                'Vindex': (data[0], data[1], data[2]),
                'Attributes': data[3],
                'Normal': (data[4],data[5],data[6]),
                'Dist': data[7],
            })
            size -= struct.calcsize('3LL3ff')
    def pack(self):
        self.binary = b''
        for t in self.triangles:
            self.binary += struct.pack('3LL3ff',
                t['Vindex'][0], t['Vindex'][1], t['Vindex'][2],
                t['Attributes'],
                t['Normal'][0], t['Normal'][1], t['Normal'][2],
                t['Dist']
            )
            self.size += struct.calcsize('3LL3ff')
class node_vertex_materials(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_vertex_material(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_vertex_material_name(node):
    def __init__(self):
        super(node_vertex_material_name, self).__init__()
        self.name = 'UNTITLED'
    def read(self, file, size):
        self.name = b2s(file.read(size))
    def pack(self):
        self.binary = s2b(self.name)
        self.size = len(self.binary)
class node_vertex_material_info(node):
    def __init__(self):
        super(node_vertex_material_info, self).__init__()
        self.Attributes = 0
        self.Ambient = (255,255,255)
        self.Diffuse = (255,255,255)
        self.Specular = (0,0,0)
        self.Emissive = (0,0,0)
        self.Shininess = 0
        self.Opacity = 1.0
        self.Translucency = 0
    def read(self, file, size):
        data = read_struct(file, 'L4B4B4B4Bfff')
        self.Attributes = data[0]
        self.Ambient = (data[1], data[2], data[3])
        self.Diffuse = (data[5], data[6], data[7])
        self.Specular = (data[9], data[10], data[11])
        self.Emissive = (data[13], data[14], data[15])
        self.Shininess = data[17]
        self.Opacity = data[18]
        self.Translucency = data[19]
        self.Mapping0 = data[0] >> 16 & 0xFF
        self.Mapping1 = data[0] >> 8 & 0xFF
    def pack(self):
        self.binary = struct.pack('L4B4B4B4Bfff',
            self.Attributes,
            self.Ambient[0], self.Ambient[1], self.Ambient[2], 0,
            self.Diffuse[0], self.Diffuse[1], self.Diffuse[2], 0,
            self.Specular[0], self.Specular[1], self.Specular[2], 0,
            self.Emissive[0], self.Emissive[1], self.Emissive[2], 0,
            self.Shininess,
            self.Opacity,
            self.Translucency
        )
        self.size += struct.calcsize('L4B4B4B4Bfff')
class node_dcg(node):
    def read(self, file, size):
        self.dcg = []
        while size > 0:
            data = read_struct(file, '4B')
            self.dcg.append((data[0], data[1], data[2], data[3]))
            size -= struct.calcsize('4B')
    def pack(self):
        self.binary = b''
        for c in self.dcg:
            self.binary += struct.pack('4B',
                c[0], c[1], c[2], c[3]
            )
            self.size += struct.calcsize('4B')
    
class node_prelit_lightmap_multi_pass(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
    
class node_material_info(node):
    def __init__(self):
        super(node_material_info, self).__init__()
        self.PassCount = 0
        self.VertexMaterialCount = 0
        self.ShaderCount = 0
        self.TextureCount = 0
    def read(self, file, size):
        data = read_struct(file, 'LLLL')
        self.PassCount = data[0]
        self.VertexMaterialCount = data[1]
        self.ShaderCount = data[2]
        self.TextureCount = data[3]
    def pack(self):
        self.binary = struct.pack('LLLL',
            self.PassCount,
            self.VertexMaterialCount,
            self.ShaderCount,
            self.TextureCount
        )
        self.size += struct.calcsize('LLLL')
    
class node_material_pass(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_vertex_material_ids(node):
    def __init__(self):
        super(node_vertex_material_ids, self).__init__()
        self.ids = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, 'L')
            self.ids.append(data[0])
            size -= struct.calcsize('L')
    def pack(self):
        self.binary = b''
        for i in self.ids:
            self.binary += struct.pack('L',
                i
            )
            self.size += struct.calcsize('L')
class node_shader_ids(node):
    def __init__(self):
        super(node_shader_ids, self).__init__()
        self.ids = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, 'L')
            self.ids.append(data[0])
            size -= struct.calcsize('L')
    def pack(self):
        self.binary = b''
        for i in self.ids:
            self.binary += struct.pack('L',
                i
            )
            self.size += struct.calcsize('L')
class node_shaders(node):
    def __init__(self):
        super(node_shaders, self).__init__()
        self.shaders = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, '16B')
            self.shaders.append({
                'SrcBlend': data[7],
                'DestBlend': data[3],
                'DepthMask': data[1],
                'AlphaTest': data[12],
                
                'PriGradient': data[5],
                'SecGradient': data[6],
                'DepthCompare': data[0],
                'DetailColorFunc': data[9],
                'DetailAlphaFunc': data[10],            
                
                'Texturing': data[8],
                'PostDetailColorFunc': data[13],
                'PostDetailAlphaFunc': data[14]
            })
            size -= struct.calcsize('16B')
    def pack(self):
        self.binary = b''
        for s in self.shaders:
            self.binary += struct.pack('16B',
                s['DepthCompare'],
                s['DepthMask'],
                0,
                s['DestBlend'],
                0,
                s['PriGradient'],
                s['SecGradient'],
                s['SrcBlend'],
                s['Texturing'],
                s['DetailColorFunc'],
                s['DetailAlphaFunc'],
                0,
                s['AlphaTest'],
                s['PostDetailColorFunc'],
                s['PostDetailAlphaFunc'],
                0
            )
            self.size += struct.calcsize('16B')
class node_texture_stage(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_texture_ids(node):
    def __init__(self):
        super(node_texture_ids, self).__init__()
        self.ids = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, 'L')
            self.ids.append(data[0])
            size -= struct.calcsize('L')
    def pack(self):
        self.binary = b''
        for i in self.ids:
            self.binary += struct.pack('L',
                i
            )
            self.size += struct.calcsize('L')
class node_stage_texcoords(node):
    def __init__(self):
        super(node_stage_texcoords, self).__init__()
        self.texcoords = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, '2f')
            self.texcoords.append((data[0], data[1]))
            size -= struct.calcsize('2f')
    def pack(self):
        self.binary = b''
        for t in self.texcoords:
            self.binary += struct.pack('2f',
                t[0], t[1]
            )
            self.size += struct.calcsize('2f')
class node_texture_texcoords(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_textures(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_texture(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_hierarchy(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_texture_name(node):
    def __init__(self):
        super(node_texture_name, self).__init__()
        self.name = 'UNTITLED'
    def read(self, file, size):
        self.name = b2s(file.read(size))
    def pack(self):
        self.binary = s2b(self.name)
        self.size = len(self.binary)
class node_hierarchy_header(node):
    def __init__(self):
        super(node_hierarchy_header, self).__init__()
        self.Version = ver(4,1)
        self.Name = 'UNTITLED'
        self.NumPivots = 0
        self.Center = (0, 0, 0)
    def read(self, file, size):
        data = read_struct(file, 'L16sL3f')
        self.Version = data[0]
        self.Name = b2s(data[1])
        self.NumPivots = data[2]
        self.Center = (data[3], data[4], data[5])
    def pack(self):
        self.binary = struct.pack('L16sL3f',
            self.Version,
            s2b(self.Name, 16),
            self.NumPivots,
            self.Center[0],self.Center[1],self.Center[2],
        )
        self.size += struct.calcsize('L16sL3f')
class node_pivots(node):
    def __init__(self):
        super(node_pivots, self).__init__()
        self.pivots = []
    def read(self, file, size):
        while size > 0:
            data = read_struct(file, '16sL3f3f4f')
            self.pivots.append({
                'Name': b2s(data[0]),
                'ParentIdx': data[1],
                'Translation': (data[2],data[3],data[4]),
                'EulerAngles': (data[5],data[6],data[7]),
                'Rotation': (data[8],data[9],data[10],data[11])
            })
            size -= struct.calcsize('16sL3f3f4f')
    def pack(self):
        self.binary = b''
        for p in self.pivots:
            self.binary += struct.pack('16sL3f3f4f',
                s2b(p['Name'], 16),
                p['ParentIdx'],
                p['Translation'][0],p['Translation'][1],p['Translation'][2],
                p['EulerAngles'][0],p['EulerAngles'][1],p['EulerAngles'][2],
                p['Rotation'][0],p['Rotation'][1],p['Rotation'][2],p['Rotation'][3]
            )
            self.size += struct.calcsize('16sL3f3f4f')
class node_aggregate(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_aggregate_header(node):
    def read(self, file, size):
        data = read_struct(file, 'L16s')
        self.Version = data[0]
        self.Name = b2s(data[1])
    def pack(self):
        self.binary = struct.pack('L16s',
            self.Version,
            b2s(self.Name)
        )
        self.size += struct.calcsize('L16s')
class node_aggregate_info(node):
    def read(self, file, size):
        data = read_struct(file, '32sL')
        self.BaseModelName = b2s(data[0])
        self.SubobjectCount = data[1]
        size -= struct.calcsize('32sL')
        
        self.Subobjects = []
        while size > 0:
            data = read_struct(file, '32s32s')
            self.Subobjects.append({
                'SubobjectName': b2s(data[0]),
                'BoneName': b2s(data[1])
            })
            size -= struct.calcsize('32s32s')
    def pack(self):
        self.binary = struct.pack('32sL',
            b2s(self.BaseModelName),
            self.SubobjectCount
        )
        self.size = struct.calcsize('32sL')
        for s in self.Subobjects:
            self.binary += struct.pack('32s32s',
                s2b(s['SubobjectName'], 32), s2b(s['BoneName'], 32)
            )
            self.size += struct.calcsize('32s32s')
class node_aggregate_class_info(node):
    def read(self, file, size):
        data = read_struct(file, 'LL3L')
        self.OriginalClassID = data[0]
        self.Flags = data[1]
    def pack(self):
        self.binary = struct.pack('LL3L',
            self.OriginalClassID,
            self.Flags,
            0, 0, 0
        )
        self.size += struct.calcsize('LL3L')
class node_hlod(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_hlod_header(node):
    def __init__(self):
        super(node_hlod_header, self).__init__()
        self.Version = ver(1,0)
        self.LodCount = 1
        self.Name = 'UNTITLED'
        self.HierarchyName = 'UNTITLED'
    def read(self, file, size):
        data = read_struct(file, 'LL16s16s')
        self.Version = data[0]
        self.LodCount = data[1]
        self.Name = b2s(data[2])
        self.HierarchyName = b2s(data[3])
    def pack(self):
        self.binary = struct.pack('LL16s16s',
            self.Version,
            self.LodCount,
            s2b(self.Name, 16),
            s2b(self.HierarchyName, 16)
        )
        self.size += struct.calcsize('LL16s16s')
class node_hlod_lod_array(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_hlod_aggregate_array(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_hlod_proxy_array(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
class node_hlod_sub_object_array_header(node):
    def __init__(self):
        super(node_hlod_sub_object_array_header, self).__init__()
        self.ModelCount = 0
        self.MaxScreenSize = 0.0
    def read(self, file, size):
        data = read_struct(file, 'Lf')
        self.ModelCount = data[0]
        self.MaxScreenSize = data[1]
    def pack(self):
        self.binary = struct.pack('Lf',
            self.ModelCount,
            self.MaxScreenSize
        )
        self.size += struct.calcsize('Lf')
class node_hlod_sub_object(node):
    def __init__(self):
        super(node_hlod_sub_object, self).__init__()
        self.BoneIndex = 0
        self.Name = 'UNTITLED'
    def read(self, file, size):
        data = read_struct(file, 'L32s')
        self.BoneIndex = data[0]
        self.Name = b2s(data[1])
    def pack(self):
        self.binary = struct.pack('L32s',
            self.BoneIndex,
            s2b(self.Name, 32)
        )
        self.size += struct.calcsize('L32s')
class node_box(node):
    def read(self, file, size):
        data = read_struct(file, 'LL32s4B3f3f')
        self.Version = data[0]
        self.Attributes = data[1]
        self.Name = b2s(data[2])
        self.Color = (data[3], data[4], data[5])
        self.Center = (data[7], data[8], data[9])
        self.Extent = (data[10], data[11], data[12])
    def pack(self):
        self.binary = struct.pack('LL32s4B3f3f',
            self.Version,
            self.Attributes,
            s2b(self.Name, 32),
            self.Color[0], self.Color[1], self.Color[2], 0,
            self.Center[0], self.Center[1], self.Center[2],
            self.Extent[0], self.Extent[1], self.Extent[2],
        )
        self.size += struct.calcsize('LL32s4B3f3f')
class node_sphere(node):
    def read(self, file, size):
        data = read_struct(file, 'LL32s4B3f3f')
        self.Version = data[0]
        self.Attributes = data[1]
        self.Name = b2s(data[2])
        self.Color = (data[3], data[4], data[5])
        self.Center = (data[7], data[8], data[9])
        self.Extent = (data[10], data[11], data[12])
    def pack(self):
        self.binary = struct.pack('LL32s4B3f3f',
            self.Version,
            self.Attributes,
            b2s(self.Name),
            self.Color[0], self.Color[1], self.Color[2], 0,
            self.Center[0], self.Center[1], self.Center[2],
            self.Extent[0], self.Extent[1], self.Extent[2],
        )
        self.size += struct.calcsize('LL32s4B3f3f')
class node_ring(node):
    def read(self, file, size):
        data = read_struct(file, 'LL32s4B3f3f')
        self.Version = data[0]
        self.Attributes = data[1]
        self.Name = b2s(data[2])
        self.Color = (data[3], data[4], data[5])
        self.Center = (data[7], data[8], data[9])
        self.Extent = (data[10], data[11], data[12])
    def pack(self):
        self.binary = struct.pack('LL32s4B3f3f',
            self.Version,
            self.Attributes,
            b2s(self.Name),
            self.Color[0], self.Color[1], self.Color[2], 0,
            self.Center[0], self.Center[1], self.Center[2],
            self.Extent[0], self.Extent[1], self.Extent[2],
        )
        self.size += struct.calcsize('LL32s4B3f3f')
class node_(node):
    def read(self, file, size):
        self.children = parse_nodes(file, size)
        
# loading algorithm

def read_struct(file, fmt):
    binary = file.read(struct.calcsize(fmt))
    
    if binary == b'':
        return None
    
    data = struct.unpack(fmt, binary)
    return data
    
def read_header(file):
    data = read_struct(file, 'LL')
    
    if data == None:
        return None
    
    try:
        type = w3d_keys[data[0]]
    except KeyError:
        type = 'ERROR'
    
    size = data[1] & 0x7FFFFFFF
    
    return (type, size)
    
def parse_nodes(file, size=0x7FFFFFFF):
    nodes = []
    
    while size > 0:
        ci = read_header(file)
        if ci == None:
            break;
        
        # instantiate and load node
        try:
            the_node = globals()['node_' + ci[0].lower()]()
            the_node.read(file, ci[1])
            nodes.append(the_node)
        except KeyError:
            file.read(ci[1])
            print('ignored: node_' + ci[0].lower())
        
        # limit size for nested chunks
        size -= 8 + ci[1] # header size + chunk size
        
    return nodes
    
def load(filepath):
    file = open(filepath, 'rb')
    print('load: ' + filepath)
    try:
        root = node()
        root.children = parse_nodes(file)
    finally:
        file.close()
    return root
    
def save(root, filepath):
    file = open(filepath, 'wb')
    print('save: ' + filepath)
    for c in root.children:
        c.pack()
        c.write(file)
    file.close()