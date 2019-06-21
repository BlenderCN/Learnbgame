import bpy
import math

class Bone(object):
    def __init__(self):
        self.name = ""
        self.tail = []
        self.head = []
        self.parent_index = -1
        self.index = -1

class Skeleton(object):
    def __init__(self):
        self.bones = []

    def find_bone_named(self, name):
        for bone in self.bones:
            if bone.name == name:
                return bone
        return None

    def extract(self, b_armature):
        for bone_index, b_pose_bone in enumerate(b_armature.pose.bones):
            b_bone = b_pose_bone.bone

            bone = Bone()
            bone.index = bone_index
            bone.name = b_bone.name

            bone_head = b_armature.matrix_world * b_bone.head_local
            bone.tail = [tail - head for head, tail in zip(b_bone.head_local, b_bone.tail_local)]
            bone.head = [e for e in bone_head]

            if not b_pose_bone.parent is None:
                for i, parent in enumerate(b_armature.pose.bones):
                    if parent == b_pose_bone.parent:
                        bone.parent_index = i
                        break
            else:
                bone.parent_index = -1

            self.bones.append(bone)


class WeightGroup(object):
    def __init__(self):
        self.weights = []

class Weight(object):
    def __init__(self):
        self.weight = 0.0
        self.position = []
        self.bone_index = -1

class Mesh(object):
    def __init__(self):
        self.weight_groups = []
        self.normals = []
        self.tangents = []
        self.uv_channels = []

    def extract(self, b_mesh, skeleton):
        b_mesh.data.calc_tangents()

        for uv_layer in b_mesh.data.uv_layers:
            self.uv_channels.append([])

        for poly in b_mesh.data.polygons:
            for loop in [b_mesh.data.loops[i] for i in poly.loop_indices]:
                vert = b_mesh.data.vertices[loop.vertex_index]

                # normal
                self.normals.append([x for x in loop.normal])
                self.tangents.append([x for x in loop.tangent])

                # weights
                weight_group = WeightGroup()

                # normalize
                weight_length = sum([group.weight for group in vert.groups])

                epsilon = 0.00001
                for group in vert.groups:
                    if weight_length < epsilon:
                        continue

                    weight_bias = group.weight / weight_length

                    if weight_bias < epsilon:
                        continue

                    # vertex group for mesh
                    vert_group = b_mesh.vertex_groups[group.group]

                    # bone for group
                    weight_bone = skeleton.find_bone_named(vert_group.name)

                    if not weight_bone is None:
                        weight = Weight()
                        weight.bone_index = weight_bone.index
                        weight.weight = weight_bias

                        joint_position = weight_bone.head
                        pos = b_mesh.matrix_world * vert.co

                        # weight position
                        for i in range(len(vert.co)):
                            weight.position.append(pos[i] - joint_position[i])

                        weight_group.weights.append(weight)
                    else:
                        print("missing bone " + vert_group.name)

                self.weight_groups.append(weight_group)

                # uv
                for i, uv_layer in enumerate(b_mesh.data.uv_layers):
                    self.uv_channels[i].append([uv_layer.data[loop.index].uv[0], uv_layer.data[loop.index].uv[1]])


def export(b_mesh, b_armature, b_attach_points, filename):
    file_version = 4

    skeleton = Skeleton()
    skeleton.extract(b_armature)

    mesh = Mesh()
    mesh.extract(b_mesh, skeleton)

    weight_count = sum([len(group.weights) for group in mesh.weight_groups])

    file = open(filename, "w")
    file.write("# World C - SkelMesh\n")
    file.write("version: %i\n" % file_version)
    file.write("vertex_count: %i\n" % len(mesh.normals))
    file.write("bone_count: %i\n" % len(skeleton.bones))
    file.write("uv_channel_count: %i\n" % len(mesh.uv_channels))
    file.write("weight_count: %i\n" % weight_count)
    file.write("attach_point_count: %i\n" % len(b_attach_points))

    for bone in skeleton.bones:
        if bone.parent_index == -1:
            file.write("origin: [%f, %f, %f]\n" % (bone.head[0], bone.head[1], bone.head[2]))

    file.write("bones: \n")
    for bone in skeleton.bones:
        file.write("( %s ), %i, [%f, %f, %f]\n" % (bone.name, bone.parent_index, bone.tail[0], bone.tail[1], bone.tail[2]))

    file.write("attach_points: \n")
    for attach_point in b_attach_points:
        parent_bone_name = attach_point.parent_bone
        bone = skeleton.find_bone_named(parent_bone_name)

        b_bone = attach_point.parent.data.bones[parent_bone_name]

        attach_vector = attach_point.location * b_armature.matrix_world * b_bone.matrix_local
        matrix = b_armature.matrix_world * b_bone.matrix_local * attach_point.matrix_local
        attach_rotation = matrix.to_3x3().to_quaternion()

        if bone:
            arg_list = (attach_point.name,
                        bone.index,
                        attach_vector[0],
                        attach_vector[1],
                        attach_vector[2],
                        attach_rotation[0],
                        attach_rotation[1],
                        attach_rotation[2],
                        attach_rotation[3])
            file.write("( %s ), %i, [%f, %f, %f] [%f, %f, %f, %f]\n" % arg_list)

    file.write("normals: \n")
    for normal in mesh.normals:
        file.write("%f, %f, %f\n" % (normal[0], normal[1], normal[2]))

    #file.write("tangents: \n")
    #for tangent in mesh.tangents:
        #file.write("%f, %f, %f\n" % (tangent[0], tangent[1], tangent[2]))

    i = 0
    for uv_channel in mesh.uv_channels:
        file.write("uv %i: \n" % i)
        for uv in uv_channel:
            file.write("%f, %f\n" % (uv[0], uv[1]))
        i += 1

    file.write("weights: \n")
    for group in mesh.weight_groups:
        file.write("%i\n" % len(group.weights))
        for weight in group.weights:
            file.write("%i, %f, %f, %f, %f\n" % (weight.bone_index, weight.weight, weight.position[0], weight.position[1], weight.position[2]))
