from ..io.reader import BinaryFileReader
from .rsm import Rsm
from pprint import pprint

class RsmReader(object):
    def __init__(self):
        pass

    @staticmethod
    def from_file(path) -> Rsm:
        with open(path, 'rb') as f:
            rsm = Rsm()
            reader = BinaryFileReader(f)
            magic = reader.read('4s')[0]
            if magic != b'GRSM':
                raise RuntimeError('Invalid file type')
            version_major, version_minor = reader.read('2B')
            rsm.anim_length = reader.read('I')
            rsm.shade_type = reader.read('I')
            if version_major > 1 or version_major and version_minor >= 4:
                rsm.alpha = reader.read('B')
            reader.read('16B')
            texture_count = reader.read('I')[0]
            for i in range(texture_count):
                texture = reader.read_fixed_length_null_terminated_string(40)
                rsm.textures.append(texture)
            rsm.main_node = reader.read_fixed_length_null_terminated_string(40)
            node_count = reader.read('I')[0]
            for i in range(node_count):
                node = rsm.Node()
                node.name = reader.read_fixed_length_null_terminated_string(40)
                node.parent_name = reader.read_fixed_length_null_terminated_string(40)
                node_texture_count = reader.read('I')[0]
                node.texture_indices = reader.read('{}I'.format(node_texture_count))
                node.some_matrix = reader.read('9f') # offset matrix??
                node.offset_ = reader.read('3f')
                node.offset = reader.read('3f')
                node.rotation = reader.read('4f')  # axis-angle
                node.scale = reader.read('3f')
                vertex_count = reader.read('I')[0]
                node.vertices = [reader.read('3f') for _ in range(vertex_count)]
                # Texture Coordinates
                texcoord_count = reader.read('I')[0]
                for _ in range(texcoord_count):
                    texcoord = reader.read('I2f')
                    node.texcoords.append(texcoord)
                # Faces
                face_count = reader.read('I')[0]
                for _ in range(face_count):
                    face = Rsm.Node.Face()
                    face.vertex_indices = reader.read('3H')
                    face.texcoord_indices = reader.read('3H')
                    face.texture_index = reader.read('H')[0]
                    reader.read('H') # padding
                    face.two_sided = reader.read('I')[0]
                    face.smoothing_group = reader.read('I')[0]
                    node.faces.append(face)
                rsm.nodes.append(node)
                if version_major > 1 or (version_major == 1 and version_minor >= 5):
                    location_keyframe_count = reader.read('I')[0]
                    for _ in range(location_keyframe_count):
                        location_keyframe = Rsm.Node.LocationKeyFrame()
                        location_keyframe.frame = reader.read('I')
                        location_keyframe.position = reader.read('3f')
                        node.location_keyframes.append(location_keyframe)
                rotation_keyframe_count = reader.read('I')[0]
                for _ in range(rotation_keyframe_count):
                    rotation_keyframe = Rsm.Node.RotationKeyFrame()
                    rotation_keyframe.frame = reader.read('I')
                    rotation_keyframe.rotation = reader.read('4f')
                    node.rotation_keyframes.append(rotation_keyframe)
            return rsm
