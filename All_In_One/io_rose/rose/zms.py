from enum import IntEnum
from .utils import *

class VertexFlags(IntEnum):
    POSITION = 1 << 1,
    NORMAL = 1 << 2,
    COLOR = 1 << 3,
    BONE_WEIGHT = 1 << 4, 
    BONE_INDEX = 1 << 5, 
    TANGENT = 1 << 6,
    UV1 = 1 << 7,
    UV2 = 1 << 8,
    UV3 = 1 << 9,
    UV4 = 1 << 10,

class Vertex:
    def __init__(self):
        self.position = Vector3()
        self.normal = Vector3()
        self.color = Color4()
        self.bone_weights = []
        self.bone_indices = []
        self.tangent = Vector3()
        self.uv1 = Vector2()
        self.uv2 = Vector2()
        self.uv3 = Vector2()
        self.uv4 = Vector2()

class ZMS:
    def __init__(self, filepath=None):
        self.identifier = ""
        self.flags = 0
        self.bounding_box_min = Vector3(0, 0, 0)
        self.bounding_box_max = Vector3(0, 0, 0)
        self.vertices = []
        self.indices = []
        self.bones = []
        self.materials = []
        self.strips = []
        self.pool = 0

        if filepath:
            with open(filepath, "rb") as f:
                self.read(f)

    def positions_enabled(self):
        return (self.flags & VertexFlags.POSITION) != 0

    def normals_enabled(self):
        return (self.flags & VertexFlags.NORMAL) != 0

    def colors_enabled(self):
        return (self.flags & VertexFlags.COLOR) != 0

    def bones_enabled(self):
        bone_weights = (self.flags & VertexFlags.BONE_WEIGHT) != 0
        bone_indices = (self.flags & VertexFlags.BONE_INDEX) != 0
        return (bone_weights and bone_indices)

    def tangents_enabled(self):
        return (self.flags & VertexFlags.TANGENT) != 0

    def uv1_enabled(self):
        return (self.flags & VertexFlags.UV1) != 0

    def uv2_enabled(self):
        return (self.flags & VertexFlags.UV2) != 0

    def uv3_enabled(self):
        return (self.flags & VertexFlags.UV3) != 0

    def uv4_enabled(self):
        return (self.flags & VertexFlags.UV4) != 0

    def read(self, f):
        self.identifier = read_str(f)
        self.flags = read_i32(f)
        self.bounding_box_min = read_vector3_f32(f)
        self.bounding_box_max = read_vector3_f32(f)

        bone_count = read_i16(f)
        for i in range(bone_count):
            self.bones.append(read_i16(f))

        vert_count = read_i16(f)
        for i in range(vert_count):
            self.vertices.append(Vertex())

        if self.positions_enabled():
            for i in range(vert_count):
                self.vertices[i].position = read_vector3_f32(f)

        if self.normals_enabled():
            for i in range(vert_count):
                self.vertices[i].normal = read_vector3_f32(f)

        if self.colors_enabled():
            for i in range(vert_count):
                self.vertices[i].color = read_color4(f)

        if self.bones_enabled():
            for i in range(vert_count):
                self.vertices[i].bone_weights = read_list_f32(f,4)
                self.vertices[i].bone_indices = read_list_i16(f,4)

        if self.tangents_enabled():
            for i in range(vert_count):
                self.vertices[i].tangent = read_vector3_f32(f)

        if self.uv1_enabled():
            for i in range(vert_count):
                self.vertices[i].uv1 = read_vector2_f32(f)

        if self.uv2_enabled():
            for i in range(vert_count):
                self.vertices[i].uv2 = read_vector2_f32(f)

        if self.uv3_enabled():
            for i in range(vert_count):
                self.vertices[i].uv3 = read_vector2_f32(f)

        if self.uv4_enabled():
            for i in range(vert_count):
                self.vertices[i].uv4 = read_vector2_f32(f)

        index_count = read_i16(f)
        for i in range(index_count):
            self.indices.append(read_vector3_i16(f))

        material_count = read_i16(f)
        for i in range(material_count):
            self.materials.append(read_i16(f))

        strip_count = read_i16(f)
        for i in range(strip_count):
            self.strips.append(read_i16(f))

        if self.identifier == "ZMS0008":
            self.pool = read_i16(f)
