class Vector3D(object):
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def __neg__(self):
        return Vector3D(-self.x, -self.y, -self.z)
    def __add__(self, b):
        return Vector3D(self.x + b.x, self.y + b.y, self.z + b.z)
    def __sub__(self, b):
        return Vector3D(self.x - b.x, self.y - b.y, self.z - b.z)
    @staticmethod
    def dot(first, second):
        rx = first.x + second.x
        ry = first.y + second.y
        rz = first.z + second.z
        return rx + ry + rz
    @staticmethod
    def cross(first, second):
        return Vector3D((first.y * second.z) - (first.z * second.y),\
                        (first.z * second.x) - (first.x * second.z),\
                        (first.x * second.y) - (first.y * second.x)) 

def _calcSurfaceNormal(verts):
    result_normal = Vector3D(0.0, 0.0, 0.0)
    for i in range(len(verts)):
        current = verts[i]
        next = verts[(i+1)%len(verts)]
        result_normal.x += ((current.y - next.y) * (current.z + next.z))
        result_normal.y += ((current.z - next.z) * (current.x + next.x))
        result_normal.z += ((current.x - next.x) * (current.y + next.y))
    return result_normal