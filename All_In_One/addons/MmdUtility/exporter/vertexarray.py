# coding: utf-8


class VertexAttribute(object):
    __slots__=[
            'nx', 'ny', 'nz', # normal
            'u', 'v', # uv
            ]
    def __init__(self, nx, ny, nz, u, v):
        self.nx=nx
        self.ny=ny
        self.nz=nz
        self.u=u
        self.v=v

    def __str__(self):
        return "<vkey: %f, %f, %f, %f, %f>" % (
                self.nx, self.ny, self.nz, self.u, self.v)

    def __hash__(self):
        return int(100*(self.nx + self.ny + self.nz + self.u + self.v))

    def __eq__(self, rhs):
        return self.nx==rhs.nx and self.ny==rhs.ny and self.nz==rhs.nz and self.u==rhs.u and self.v==rhs.v


class VertexKey(object):
    __slots__=[
            'obj_index', 'index',
            ]

    def __init__(self, obj_index, index):
        self.obj_index=obj_index
        self.index=index

    def __str__(self):
        return "<vkey: %d, %d>" % (self.obj_index, self.index)

    def __hash__(self):
        return self.index*100+self.obj_index

    def __eq__(self, rhs):
        return self.obj_index==rhs.obj_index and self.index==rhs.index

class ExtendedWeights:
    __slots__=[
        'entries'
    ]

    def __init__(self):
        self.entries=[]

    def each_entries(self, filter_func=lambda n, w: True):
        for ent in self.entries:
            if filter_func(*ent):
                yield ent
    
    def get_normalized(self, max_count=4, filter_func=lambda n, w: True):
        import math
        _entries=sorted(self.each_entries(filter_func), key=lambda ent: ent[1], reverse=True)
        if len(_entries) > max_count:
            _entries=_entries[0:max_count]
            print("WARNING: Too many weights!")
        total_weights=math.fsum(ent[1] for ent in _entries)
        return ( (ent[0], ent[1]/total_weights if ent[1]>0.0 else 0.0) for ent in _entries )

class VertexArray(object):
    """
    頂点配列
    """
    __slots__=[
            'indexArrays',
            'positions',
            'attributes', # normal and uv
            'b0', 'b1', 'weight',
            'ext_weight',
            'vertexMap',
            'objectMap',
            ]
    def __init__(self):
        # indexArrays split with each material
        self.indexArrays={}

        self.positions=[]
        self.attributes=[]
        self.b0=[]
        self.b1=[]
        self.weight=[]
        self.ext_weight=[]

        self.vertexMap={}
        self.objectMap={}

    def __str__(self):
        return "<VertexArray %d positions, %d indexArrays>" % (
                len(self.positions), len(self.indexArrays))

    def zip(self):
        return zip(
                self.positions, self.attributes,
                self.b0, self.b1, self.weight)

    def zip2(self):
        return zip(
                self.positions, self.attributes,
                self.b0, self.b1, self.weight, self.ext_weight)

    def each(self):
        keys=[key for key in self.indexArrays.keys()]
        keys.sort()
        for key in keys:
            yield(key, self.indexArrays[key])

    def __addOrGetIndex(self, obj_index, base_index, pos, normal, uv, b0, b1, weight0):
        key=VertexKey(obj_index, base_index)
        attribute=VertexAttribute( 
                normal[0], normal[1], normal[2],
                uv[0], uv[1])
        if key in self.vertexMap:
            if attribute in self.vertexMap[key]:
                return self.vertexMap[key][attribute]
            else:
                return self.__addVertex(self.vertexMap[key],
                        pos, attribute, b0, b1, weight0)
        else:
            vertexMapKey={}
            self.vertexMap[key]=vertexMapKey
            return self.__addVertex(vertexMapKey,
                    pos, attribute, b0, b1, weight0)

    def __addVertex(self, vertexMapKey, pos, attribute, b0, b1, weight0):
        index=len(self.positions)
        vertexMapKey[attribute]=index
        # position
        self.positions.append((pos.x, pos.y, pos.z))
        # unique attribute
        self.attributes.append(attribute)
        # shared attribute
        self.b0.append(b0)
        self.b1.append(b1)
        self.weight.append(weight0)
        self.ext_weight.append(ExtendedWeights())
        assert(index<=65535)
        return index
            
    def getMappedIndex(self, obj_name, base_index):
        return self.vertexMap[VertexKey(self.objectMap[obj_name], base_index)]

    def getMappedIndex(self, obj_name, base_index):
        key=VertexKey(self.objectMap[obj_name], base_index)
        if key not in self.vertexMap:
            return {}
        return self.vertexMap[key]

    def getMappedIndex2(self, obj_name, base_index):
        if obj_name not in self.objectMap:
            return []
        return self.vertexMap.get(VertexKey(self.objectMap[obj_name], base_index), {}).values()

    def addTriangle(self,
            object_name, material,
            base_index0, base_index1, base_index2,
            pos0, pos1, pos2,
            n0, n1, n2,
            uv0, uv1, uv2,
            b0_0, b0_1, b0_2,
            b1_0, b1_1, b1_2,
            weight0, weight1, weight2
            ):
        if object_name in self.objectMap:
            obj_index=self.objectMap[object_name]
        else:
            obj_index=len(self.objectMap)
            self.objectMap[object_name]=obj_index
        index0=self.__addOrGetIndex(obj_index, base_index0, pos0, n0, uv0, b0_0, b1_0, weight0)
        index1=self.__addOrGetIndex(obj_index, base_index1, pos1, n1, uv1, b0_1, b1_1, weight1)
        index2=self.__addOrGetIndex(obj_index, base_index2, pos2, n2, uv2, b0_2, b1_2, weight2)

        if not material in self.indexArrays:
            self.indexArrays[material]=[]
        self.indexArrays[material]+=[index0, index1, index2]

