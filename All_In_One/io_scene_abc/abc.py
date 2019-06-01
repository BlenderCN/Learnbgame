import struct
from mathutils import Vector, Quaternion, Matrix

'''
REFERENCE LIST:
    http://www.fallout.bplaced.net/dedit/tutorials/dedit_docs_nolf/ModelEdit.htm
    https://web.archive.org/web/20080605043638/http://bop-mod.com:80/download/docs/ABC-Format-v6.html

TODO LIST:
    * Figure out what the [-1, 0, 18] flag is at the end of animation bounds. 
    * Add the ability to optionally merge import meshes
    * Add the ability to import textures automatically
'''


'''
This is a depth-first iterator. The weird `idx` array is used because
integers cannot be pass-by-reference.
'''
def node_iterator(nodes, nit=None, parent=None):
    if nit is None:
        nit = iter(nodes)
    node = next(nit)
    yield (node, parent)
    for i in range(node.child_count):
        yield from node_iterator(nodes, nit, node)


def build_undirected_tree(nodes):
    for (node, parent) in node_iterator(nodes):
        node.parent = parent
        node.children = []
        if parent is not None:
            parent.children.append(node)


'''
DATA BLOCKS
'''
class Weight(object):
    def __init__(self):
        self.node_index = 0
        self.location = Vector()
        self.bias = 0.0


class Vertex(object):
    def __init__(self):
        self.sublod_vertex_index = 0xCDCD
        self.weights = []
        self.location = Vector()
        self.normal = Vector()


class FaceVertex(object):
    def __init__(self):
        self.texcoord = Vector()
        self.vertex_index = 0


class Face(object):
    def __init__(self):
        self.vertices = []


class LOD(object):
    def __init__(self):
        self.faces = []
        self.vertices = []

    def get_face_vertices(self, face_index):
        return [self.vertices[vertex.vertex_index] for vertex in self.faces[face_index].vertices]


class Piece(object):
    
    @property
    def weight_count(self):
        return sum([len(vertex.weights) for lod in self.lods for vertex in lod.vertices])
    
    def __init__(self):
        self.material_index = 0
        self.specular_power = 0.0
        self.specular_scale = 0.0
        self.lod_weight = 0.0
        self.name = ''
        self.lods = []
    
class Node(object):
    
    @property
    def is_removable(self):
        return (self.flags & 1) != 0
    
    @is_removable.setter
    def is_removable(self, b):
        self.flags = (self.flags & ~1) | (1 if b else 0)

    @property
    def uses_relative_location(self):
        return (self.flags & 2) != 0
    
    def __init__(self):
        self.name = ''
        self.index = 0
        self.flags = 0
        self.bind_matrix = Matrix()
        self.child_count = 0
    
    def __repr__(self):
        return self.name


class WeightSet(object):
    def __init__(self):
        self.name = ''
        self.node_weights = []


class Socket(object):
    def __init__(self):
        self.node_index = 0
        self.name = ''
        self.rotation = Quaternion()
        self.location = Vector()


class Animation(object):
    class Keyframe(object):
        class Transform(object):
            def __init__(self):
                self.location = Vector()
                self.rotation = Quaternion((1, 0, 0, 0))
            
            @property
            def matrix(self):
                return Matrix.Translation(self.location) * self.rotation.to_matrix().to_4x4()
            
            @matrix.setter
            def matrix(self, m):
                self.location, self.rotation, _ = m.decompose()
        
        def __init__(self):
            self.time = 0
            self.string = ''

    def __init__(self):
        self.extents = Vector()
        self.name = ''
        self.unknown1 = -1
        self.interpolation_time = 200
        self.keyframes = []
        self.node_keyframe_transforms = []


class AnimBinding(object):
    def __init__(self):
        self.name = ''
        self.extents = Vector()
        self.origin = Vector()


class ChildModel(object):
    def __init__(self):
        self.name = ''
        self.build_number = 0
        self.transforms = []


class Model(object):
    def __init__(self):
        self.name = ''
        self.pieces = []
        self.nodes = []
        self.child_models = []
        self.animations = []
        self.sockets = []
        self.command_string = ''
        self.internal_radius = 0.0
        self.lod_distances = []
        self.weight_sets = []
        self.anim_bindings = []
        
    @property
    def keyframe_count(self):
        return sum([len(animation.keyframes) for animation in self.animations])

    @property
    def face_count(self): #TODO: this is actually probably per LOD as well
        return sum([len(lod.faces) for piece in self.pieces for lod in piece.lods])
    
    @property
    def vertex_count(self):
        return sum([len(lod.vertices) for piece in self.pieces for lod in piece.lods])

    @property
    def weight_count(self):
        return sum([len(vertex.weights) for piece in self.pieces for lod in piece.lods for vertex in lod.vertices])
    
    @property
    def lod_count(self):
        return len(self.pieces[0].lods)
