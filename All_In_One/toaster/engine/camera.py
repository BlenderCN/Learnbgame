from mathutils import Vector
from . ray import Ray


class Camera(object):
    def __init__(self):
        self.lower_left_corner = Vector((-2.0, -1.0, -1.0))
        self.origin = Vector((0.0, 0.0, 0.0))
        self.horizontal = Vector((4.0, 0.0, 0.0))
        self.vertical = Vector((0.0, 2.0, 0.0))

    def get_ray(self, u, v):
        return Ray(origin=self.origin, direction=self.lower_left_corner + self.horizontal * u + self.vertical * v - self.origin)
