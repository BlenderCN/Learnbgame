import os
from .abc import *
from .io import unpack
from mathutils import Vector, Matrix, Quaternion


class ModelReader(object):
    def __init__(self):
        self._version = 0
        self._node_count = 0
        self._lod_count = 0

    def _read_matrix(self, f):
        data = unpack('16f', f)
        rows = [data[0:4], data[4:8], data[8:12], data[12:16]]
        return Matrix(rows)

    def _read_vector(self, f):
        return Vector(unpack('3f', f))

    def _read_quaternion(self, f):
        x, y, z, w = unpack('4f', f)
        return Quaternion((w, x, y, z))

    def _read_string(self, f):
        return f.read(unpack('H', f)[0]).decode('ascii')

    def _read_weight(self, f):
        weight = Weight()
        weight.node_index = unpack('I', f)[0]
        weight.location = self._read_vector(f)
        weight.bias = unpack('f', f)[0]
        return weight

    def _read_vertex(self, f):
        vertex = Vertex()
        weight_count = unpack('H', f)[0]
        vertex.sublod_vertex_index = unpack('H', f)[0]
        vertex.weights = [self._read_weight(f) for _ in range(weight_count)]
        vertex.location = self._read_vector(f)
        vertex.normal = self._read_vector(f)
        return vertex

    def _read_face_vertex(self, f):
        face_vertex = FaceVertex()
        face_vertex.texcoord.xy = unpack('2f', f)
        face_vertex.vertex_index = unpack('H', f)[0]
        return face_vertex

    def _read_face(self, f):
        face = Face()
        face.vertices = [self._read_face_vertex(f) for _ in range(3)]
        return face

    def _read_lod(self, f):
        lod = LOD()
        face_count = unpack('I', f)[0]
        lod.faces = [self._read_face(f) for _ in range(face_count)]
        vertex_count = unpack('I', f)[0]
        lod.vertices = [self._read_vertex(f) for _ in range(vertex_count)]
        return lod

    def _read_piece(self, f):
        piece = Piece()
        piece.material_index = unpack('H', f)[0]
        piece.specular_power = unpack('f', f)[0]
        piece.specular_scale = unpack('f', f)[0]
        if self._version > 9:
            piece.lod_weight = unpack('f', f)[0]
        piece.padding = unpack('H', f)[0]
        piece.name = self._read_string(f)
        piece.lods = [self._read_lod(f) for _ in range(self._lod_count)]
        return piece

    def _read_node(self, f):
        node = Node()
        node.name = self._read_string(f)
        node.index = unpack('H', f)[0]
        node.flags = unpack('b', f)[0]
        node.bind_matrix = self._read_matrix(f)
        node.inverse_bind_matrix = node.bind_matrix.inverted()
        node.child_count = unpack('I', f)[0]
        return node

    def _read_transform(self, f):
        transform = Animation.Keyframe.Transform()
        transform.location = self._read_vector(f)
        transform.rotation = self._read_quaternion(f)
        return transform

    def _read_child_model(self, f):
        child_model = ChildModel()
        child_model.name = self._read_string(f)
        child_model.build_number = unpack('I', f)[0]
        child_model.transforms = [self._read_transform(f) for _ in range(self._node_count)]
        return child_model

    def _read_keyframe(self, f):
        keyframe = Animation.Keyframe()
        keyframe.time = unpack('I', f)[0]
        keyframe.string = self._read_string(f)
        return keyframe

    def _read_animation(self, f):
        animation = Animation()
        animation.extents = self._read_vector(f)
        animation.name = self._read_string(f)
        animation.unknown1 = unpack('i', f)[0]
        animation.interpolation_time = unpack('I', f)[0] if self._version >= 12 else 200
        animation.keyframe_count = unpack('I', f)[0]
        animation.keyframes = [self._read_keyframe(f) for _ in range(animation.keyframe_count)]
        animation.node_keyframe_transforms = []
        for _ in range(self._node_count):
            animation.node_keyframe_transforms.append(
                [self._read_transform(f) for _ in range(animation.keyframe_count)])
        return animation

    def _read_socket(self, f):
        socket = Socket()
        socket.node_index = unpack('I', f)[0]
        socket.name = self._read_string(f)
        socket.rotation = self._read_quaternion(f)
        socket.location = self._read_vector(f)
        return socket

    def _read_anim_binding(self, f):
        anim_binding = AnimBinding()
        anim_binding.name = self._read_string(f)
        anim_binding.extents = self._read_vector(f)
        anim_binding.origin = self._read_vector(f)
        return anim_binding

    def _read_weight_set(self, f):
        weight_set = WeightSet()
        weight_set.name = self._read_string(f)
        node_count = unpack('I', f)[0]
        weight_set.node_weights = [unpack('f', f)[0] for _ in range(node_count)]
        return weight_set

    def from_file(self, path):
        model = Model()
        model.name = os.path.splitext(os.path.basename(path))[0]
        with open(path, 'rb') as f:
            next_section_offset = 0
            while next_section_offset != -1:
                f.seek(next_section_offset)
                section_name = self._read_string(f)
                next_section_offset = unpack('i', f)[0]
                if section_name == 'Header':
                    self._version = unpack('I', f)[0]
                    if self._version not in [9, 10, 11, 12]:
                        raise Exception('Unsupported file version ({}).'.format(self._version))
                    f.seek(8, 1)
                    self._node_count = unpack('I', f)[0]
                    f.seek(20, 1)
                    self._lod_count = unpack('I', f)[0]
                    f.seek(4, 1)
                    self._weight_set_count = unpack('I', f)[0]
                    f.seek(8, 1)
                    model.command_string = self._read_string(f)
                    model.internal_radius = unpack('f', f)[0]
                    f.seek(64, 1)
                    model.lod_distances = [unpack('f', f)[0] for _ in range(self._lod_count)]
                elif section_name == 'Pieces':
                    weight_count, pieces_count = unpack('2I', f)
                    model.pieces = [self._read_piece(f) for _ in range(pieces_count)]
                elif section_name == 'Nodes':
                    model.nodes = [self._read_node(f) for _ in range(self._node_count)]
                    build_undirected_tree(model.nodes)
                    weight_set_count = unpack('I', f)[0]
                    model.weight_sets = [self._read_weight_set(f) for _ in range(weight_set_count)]
                elif section_name == 'ChildModels':
                    child_model_count = unpack('H', f)[0]
                    model.child_models = [self._read_child_model(f) for _ in range(child_model_count)]
                elif section_name == 'Animation':
                    animation_count = unpack('I', f)[0]
                    model.animations = [self._read_animation(f) for _ in range(animation_count)]
                elif section_name == 'Sockets':
                    socket_count = unpack('I', f)[0]
                    model.sockets = [self._read_socket(f) for _ in range(socket_count)]
                elif section_name == 'AnimBindings':
                    anim_binding_count = unpack('I', f)[0]
                    model.anim_bindings = [self._read_anim_binding(f) for _ in range(anim_binding_count)]
        return model
