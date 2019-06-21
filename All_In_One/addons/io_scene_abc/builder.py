from .abc import *


class ModelBuilder(object):
    def __init__(self):
        pass

    @staticmethod
    def from_armature(armature_object):
        assert (armature_object.type == 'ARMATURE')
        armature = armature_object.data
        mesh_objects = [child for child in armature_object.children if child.type == 'MESH']

        if not mesh_objects:
            raise Exception('{} has no children of type \'MESH\'.'.format(armature_object.name))

        model = Model()
        model.internal_radius = int(max(armature_object.dimensions))

        ''' Pieces '''
        for mesh_object in mesh_objects:
            mesh = mesh_object.data
            modifiers = [modifier for modifier in mesh_object.modifiers if
                         modifier.type == 'ARMATURE' and modifier.object == armature_object]
            ''' Ensure that the mesh object has an armature modifier. '''
            if len(modifiers) == 0:
                raise Exception(
                    '\'{}\' does not have a modifier of type \'ARMATURE\' with object {}'.format(mesh_object.name,
                                                                                                 armature_object.name))
            elif len(modifiers) > 1:
                raise Exception(
                    '\'{}\' has more than one modifier of type \'ARMATURE\' with object {}'.format(mesh_object.name,
                                                                                                   armature_object.name))

            ''' Ensure that the mesh has UV layer information. '''
            if mesh.uv_layers.active is None:
                raise Exception('\'{}\' does not have an active UV layer'.format(mesh_object.name))

            ''' Build a dictionary of vertex groups to bones. '''
            vertex_group_nodes = dict()
            for vertex_group in mesh_object.vertex_groups:
                try:
                    vertex_group_nodes[vertex_group] = armature.bones[vertex_group.name]  # okay
                except KeyError:
                    vertex_group_nodes[vertex_group] = None

            piece = Piece()
            piece.name = mesh_object.name

            # TODO: multiple LODs
            lod = LOD()

            bone_indices = dict()
            for i, bone in enumerate(armature.bones):
                bone_indices[bone] = i

            ''' Vertices '''
            for (vertex_index, vertex) in enumerate(mesh.vertices):
                weights = []
                for vertex_group in mesh_object.vertex_groups:
                    try:
                        bias = vertex_group.weight(vertex_index)
                        bone = vertex_group_nodes[vertex_group]
                        bone_matrix = armature_object.matrix_world * bone.matrix_local
                        location = (vertex.co * mesh_object.matrix_world) * bone_matrix.transposed().inverted()
                        if bias != 0.0 and bone is not None:
                            weight = Weight()
                            weight.node_index = bone_indices[bone]
                            weight.bias = bias
                            weight.location = location
                            weights.append(weight)
                    except RuntimeError:
                        pass

                v = Vertex()
                v.location = vertex.co
                v.normal = vertex.normal
                v.weights.extend(weights)
                lod.vertices.append(v)

            ''' Faces '''
            for polygon in mesh.polygons:
                if len(polygon.loop_indices) > 3:
                    raise Exception('Mesh \'{}\' is not triangulated.'.format(
                        mesh.name))  # TODO: automatically triangulate the mesh, and have this be reversible
                face = Face()
                for loop_index in polygon.loop_indices:
                    uv = mesh.uv_layers.active.data[loop_index].uv.copy()  # TODO: use "active"?
                    uv.y = 1.0 - uv.y
                    face_vertex = FaceVertex()
                    face_vertex.texcoord.x = uv.x
                    face_vertex.texcoord.y = uv.y
                    face_vertex.vertex_index = mesh.loops[loop_index].vertex_index
                    face.vertices.append(face_vertex)
                lod.faces.append(face)

            piece.lods.append(lod)

            model.pieces.append(piece)

        ''' Nodes '''
        for bone_index, bone in enumerate(armature.bones):
            node = Node()
            node.name = bone.name
            node.index = bone_index
            node.flags = 0
            if bone_index == 0:  # DEBUG: set removable?
                node.is_removable = True
            # TODO: matrix local might be relative to previous bone?
            node.bind_matrix = armature_object.matrix_world * bone.matrix_local
            node.child_count = len(bone.children)
            model.nodes.append(node)

        build_undirected_tree(model.nodes)

        ''' ChildModels '''
        child_model = ChildModel()
        for _ in model.nodes:
            child_model.transforms.append(Animation.Keyframe.Transform())
        model.child_models.append(child_model)

        ''' Animations '''
        # TODO: Until we can extract the action information out, we need to
        # make a "fake" animation with one keyframe with transforms matching
        # the "bind" pose.
        animation = Animation()
        animation.name = 'base'
        animation.extents = Vector((10, 10, 10))
        animation.keyframes.append(Animation.Keyframe())
        for node_index, (node, pose_bone) in enumerate(zip(model.nodes, armature_object.pose.bones)):
            transforms = list()
            for _ in animation.keyframes:
                transform = Animation.Keyframe.Transform()
                transform.location = pose_bone.location
                transform.rotation = pose_bone.rotation_quaternion
                transforms.append(transform)
            animation.node_keyframe_transforms.append(transforms)
        model.animations.append(animation)

        ''' AnimBindings '''
        anim_binding = AnimBinding()
        anim_binding.name = 'base'
        animation.extents = Vector((10, 10, 10))
        model.anim_bindings.append(anim_binding)

        return model