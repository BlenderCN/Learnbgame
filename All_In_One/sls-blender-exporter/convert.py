from .dataTypes import *


def from_bones_to_joints(bone, parent_joint=None, joints=[]):
    # To clear the joints parameter when the script is called more than once
    if not parent_joint:
        joints = []

    joint = Joint(len(joints), bone.name, bone.matrix_local, parent_joint)
    joints.append(joint)

    for child in bone.children:
        from_bones_to_joints(child, joint, joints)

    return joints


def from_armature_to_skeleton(armature):
    root_bone = next(bone for bone in armature.data.bones if not bone.parent)
    joints = from_bones_to_joints(root_bone)

    return Skeleton(armature.name, joints)


def from_mesh_to_sls_mesh(mesh):
    mesh.data.update(calc_tessface=True)

    verts = mesh.data.vertices
    faces = [f for f in mesh.data.polygons]

    sls_vertices = []

    vertex_length = 0
    for face in faces:
        for i, _ in enumerate(face.vertices):
            vertex_id = face.vertices[i]
            vertex_face = verts[vertex_id]
            sum_weights = sum([group.weight for group in vertex_face.groups])

            vertex = Vertex(vertex_length, WeightVert(0,0))
            vertex_length += 1
            sls_vertices.append(vertex)

    return SlsMesh(mesh.name, sls_vertices, [], [])
