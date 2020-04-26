from mathutils import Vector, Matrix


def vector_sum(vectors):
    return sum(vectors, Vector())


def flatten_matrix(mx):
    dimension = len(mx)
    return [mx[j][i] for i in range(dimension) for j in range(dimension)]


def get_sca_matrix(vector):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = vector[i]
    return scale_mx


def get_rot_matrix(quaternion):
    return quaternion.to_matrix().to_4x4()


def get_loc_matrix(vector):
    return Matrix.Translation(vector)
