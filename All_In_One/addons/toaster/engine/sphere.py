from . hitable import Hitable

import math

class Sphere(Hitable):

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def hit(self, ray, t_min, t_max, hit_record):

        # return hit_record

        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius*self.radius

        discriminant = b*b - a*c
        if discriminant > 0:

            temp = (-b - math.sqrt(discriminant)) / a

            if temp < t_max and temp > t_min:
                hit_record.t = temp
                hit_record.p = ray.point_at_parameter(temp)
                hit_record.normal = (hit_record.p - self.center) / self.radius

                return True

            temp = (-b + math.sqrt(discriminant)) / a

            if temp < t_max and temp > t_min:
                hit_record.t = temp
                hit_record.p = ray.point_at_parameter(temp)
                hit_record.normal = (hit_record.p - self.center) / self.radius

                return True

        else:
            return False