def list_to_sls(array):
    return ''.join([element.to_sls() for element in array])


class Joint:
    def __init__(self, index, name, matrix, parent):
        self.index = index
        self.name = name
        self.matrix = matrix
        self.parent = parent

    def to_sls(self):
        quat = self.matrix.to_quaternion()
        pos = self.matrix.col[3]
        return """
  - index: %i
    parent: %i
    name: %s
    orientation: %f %f %f %f
    position: %f %f %f
""" % (
            self.index,
            self.parent.index if self.parent else -1,
            self.name,
            quat.x, quat.y, quat.z, quat.w,
            pos[0], pos[1], pos[2]
        )


class Skeleton:
    def __init__(self, name, joints):
        self.name = name
        self.joints = joints

    def to_sls(self):
        joints_str = list_to_sls(self.joints)
        return """
skeleton:
  name: %s
  joints: %s
""" % (self.name, joints_str)


class WeightVert:
    def __init__(self, start, count):
        self.start = start
        self.count = count

    def to_sls(self):
        return """
      start: %s
      count: %s
""" % (self.start, self.count)


class Vertex:
    def __init__(self, index, weights):
        self.index = index
        self.weights = weights

    def to_sls(self):
        weights_str = self.weights.to_sls()
        return """
  - index: %s
    weights: %s
""" % (self.index, weights_str)


class Face:
    def __init__(self, id0, id1, id2):
        self.id0 = id0
        self.id1 = id1
        self.id2 = id2

    def to_sls(self):
        return """
  - indices: %s %s %s
""" % (self.id0, self.id1, self.id2)


class Weight:
    def __init__(self, joint, bias, position):
        self.joint = joint
        self.bias = bias
        self.position = position

    def to_sls(self):
        return """
  - joint: %s
    bias: %s
    position: %s %s %s
""" % (
            self.joint,
            self.bias,
            self.position.x, self.position.y, self.position.z
        )


class SlsMesh:
    def __init__(self, name, vertices, faces, weights):
        self.name = name
        self.vertices = vertices
        self.faces = faces
        self.weights = weights

    def to_sls(self):
        vertices_str = list_to_sls(self.vertices)
        faces_str = list_to_sls(self.faces)
        weights_str = list_to_sls(self.weights)
        return """
mesh:
  name: %s
  vertices: %s
  faces: %s
  weights: %s
""" % (self.name, vertices_str, faces_str, weights_str)
