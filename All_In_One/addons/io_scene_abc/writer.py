import struct
import itertools


class ModelWriter(object):
    @staticmethod
    def _string_to_bytes(string):
        return struct.pack('H{0}s'.format(len(string)), len(string), string.encode('ascii'))

    @staticmethod
    def _vector_to_bytes(vector):
        return struct.pack('3f', vector.x, vector.y, vector.z)

    @staticmethod
    def _quaternion_to_bytes(quaternion):
        return struct.pack('4f', quaternion.x, quaternion.y, quaternion.z, quaternion.w)

    def _transform_to_bytes(self, transform):
        # TODO: this if fixed size, convert to bytes instead of bytearray
        buffer = bytearray()
        buffer.extend(self._vector_to_bytes(transform.location))
        buffer.extend(self._quaternion_to_bytes(transform.rotation))
        return bytes(buffer)

    @staticmethod
    def _get_unique_strings(model):
        strings = set()
        strings.add(model.command_string)
        strings.update([node.name for node in model.nodes])
        strings.update([child_model.name for child_model in model.child_models])
        strings.update([animation.name for animation in model.animations])
        strings.update([keyframe.string for animation in model.animations for keyframe in animation.keyframes])
        strings.discard('')
        return strings

    def write(self, model, path):
        class Section(object):
            def __init__(self, name, data):
                self.name = name
                self.data = data

        sections = []

        ''' Header '''
        lod_count = 1  # TODO: incorporate LODs in a later version
        lod_distances = []

        unique_strings = self._get_unique_strings(model)

        buffer = bytearray()
        buffer.extend(struct.pack('I', 12))  # version
        buffer.extend(struct.pack('I', model.keyframe_count))
        buffer.extend(struct.pack('I', len(model.animations)))
        buffer.extend(struct.pack('I', len(model.nodes)))
        buffer.extend(struct.pack('I', len(model.pieces)))
        buffer.extend(struct.pack('I', len(model.child_models)))
        buffer.extend(struct.pack('I', model.face_count))
        buffer.extend(struct.pack('I', model.vertex_count))
        buffer.extend(struct.pack('I', model.weight_count))
        buffer.extend(struct.pack('I', model.lod_count))
        buffer.extend(struct.pack('I', len(model.sockets)))
        buffer.extend(struct.pack('I', len(model.weight_sets)))
        buffer.extend(struct.pack('I', len(unique_strings)))
        buffer.extend(struct.pack('I', sum([len(unique_string) for unique_string in unique_strings])))
        buffer.extend(self._string_to_bytes(model.command_string))
        buffer.extend(struct.pack('f', model.internal_radius))
        buffer.extend(struct.pack('I', len(lod_distances)))
        buffer.extend(bytes(bytearray(60)))

        for lod_distance in lod_distances:
            buffer.extend(struct.pack('f', lod_distance))

        sections.append(Section('Header', bytes(buffer)))

        ''' Pieces '''
        buffer = bytearray()
        buffer.extend(struct.pack('2I', model.weight_count, len(model.pieces)))

        for piece in model.pieces:
            buffer.extend(struct.pack('H', piece.material_index))
            buffer.extend(struct.pack('f', piece.specular_power))
            buffer.extend(struct.pack('f', piece.specular_scale))
            buffer.extend(struct.pack('f', piece.lod_weight))
            buffer.extend(struct.pack('H', 0))
            buffer.extend(self._string_to_bytes(piece.name))
            for lod in piece.lods:
                buffer.extend(struct.pack('I', len(lod.faces)))
                for face in lod.faces:
                    for face_vertex in face.vertices:
                        buffer.extend(struct.pack('2fH', face_vertex.texcoord.x, face_vertex.texcoord.y,
                                                  face_vertex.vertex_index))
                buffer.extend(struct.pack('I', len(lod.vertices)))
                for vertex in lod.vertices:
                    buffer.extend(struct.pack('H', len(vertex.weights)))
                    buffer.extend(struct.pack('H', vertex.sublod_vertex_index))
                    for weight in vertex.weights:
                        co = weight.location
                        buffer.extend(struct.pack('I4f', weight.node_index, co.x, co.y, co.z, weight.bias))
                    buffer.extend(struct.pack('3f', vertex.location.x, vertex.location.y, vertex.location.z))
                    buffer.extend(struct.pack('3f', vertex.normal.x, vertex.normal.y, vertex.normal.z))

        sections.append(Section('Pieces', bytes(buffer)))

        ''' Nodes '''
        buffer = bytearray()
        for node in model.nodes:
            buffer.extend(self._string_to_bytes(node.name))
            buffer.extend(struct.pack('Hb', node.index, node.flags))
            # TODO: extract this out to a function
            # TODO: not entirely surprising that this is wrong, the "bind_matrix" is probably relative to parent
            # when it needs to be in world-space? or vice versa
            for f in list(itertools.chain(*[row.to_tuple() for row in node.bind_matrix])):
                buffer.extend(struct.pack('f', f))
            buffer.extend(struct.pack('I', len(node.children)))

        buffer.extend(struct.pack('I', 0))  # TODO: weight set count, use BONE GROUPS

        sections.append(Section('Nodes', bytes(buffer)))

        ''' ChildModels '''
        buffer = bytearray()
        buffer.extend(struct.pack('H', len(model.child_models)))
        for child_model in model.child_models:
            buffer.extend(self._string_to_bytes(child_model.name))
            buffer.extend(struct.pack('I', child_model.build_number))
            for transform in child_model.transforms:
                buffer.extend(self._transform_to_bytes(transform))
        sections.append(Section('ChildModels', bytes(buffer)))

        ''' Animation '''
        buffer = bytearray()
        buffer.extend(struct.pack('I', len(model.animations)))
        for animation in model.animations:
            buffer.extend(self._vector_to_bytes(animation.extents))
            buffer.extend(self._string_to_bytes(animation.name))
            buffer.extend(struct.pack('i', animation.unknown1))
            buffer.extend(struct.pack('I', animation.interpolation_time))
            buffer.extend(struct.pack('I', len(animation.keyframes)))
            for keyframe in animation.keyframes:
                buffer.extend(struct.pack('I', keyframe.time))
                buffer.extend(self._string_to_bytes(keyframe.string))
            for node_keyframe_transform_list in animation.node_keyframe_transforms:
                for keyframe_transform in node_keyframe_transform_list:
                    buffer.extend(self._transform_to_bytes(keyframe_transform))
        sections.append(Section('Animation', bytes(buffer)))

        ''' Sockets '''
        buffer = bytearray()
        buffer.extend(struct.pack('I', len(model.sockets)))
        for socket in model.sockets:
            buffer.extend(struct.pack('I', socket.node_index))
            buffer.extend(self._string_to_bytes(socket.name))
            buffer.extend(self._quaternion_to_bytes(socket.rotation))
            buffer.extend(self._vector_to_bytes(socket.location))
        sections.append(Section('Sockets', bytes(buffer)))

        ''' AnimBindings '''
        buffer = bytearray()
        buffer.extend(struct.pack('I', len(model.anim_bindings)))
        for anim_binding in model.anim_bindings:
            buffer.extend(self._string_to_bytes(anim_binding.name))
            buffer.extend(self._vector_to_bytes(anim_binding.extents))
            buffer.extend(self._vector_to_bytes(anim_binding.origin))
        sections.append(Section('AnimBindings', bytes(buffer)))

        with open(path, 'wb') as f:
            for idx, section in enumerate(sections):
                f.write(self._string_to_bytes(section.name))
                if idx + 1 == len(sections):
                    f.write(struct.pack('i', -1))
                else:
                    f.write(struct.pack('i', len(section.data) + f.tell() + 4))
                f.write(bytes(section.data))
