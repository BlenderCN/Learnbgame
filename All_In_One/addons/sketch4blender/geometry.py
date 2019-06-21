import mathutils
from mathutils import Vector


def hermite_interp(y, mu, tension=0, bias=0):
    if len(y) != 4:
        return 0.0

    pbias = (1.0 + bias) * (1.0 - tension) / 2.0
    mbias = (1.0 - bias) * (1.0 - tension) / 2.0

    mu2 = mu * mu
    mu3 = mu2 * mu

    m0 = (y[1] - y[0]) * pbias + (y[2] - y[1]) * mbias
    m1 = (y[2] - y[1]) * pbias + (y[3] - y[2]) * mbias

    a0 =  2.0 * mu3 - 3.0 * mu2 + 1.0
    a1 =        mu3 - 2.0 * mu2 + mu
    a2 =        mu3 -       mu2
    a3 = -2.0 * mu3 + 3.0 * mu2

    return a0 * y[1] + a1 * m0 + a2 * m1 + a3 * y[2]


class Point(Vector):
    def __init__(self, *args, **kwargs):
        pass
        #super().__init__(*args, **kwargs)


class Transform(mathutils.Matrix):
    def __init__(self, *args, **kwargs):
        pass

    def __pow__(self, exp):
        if exp < 0:
            return self.inverted() ** (-exp)
        result = self.Identity(4)
        count  = self
        while exp:
            if exp % 2 == 1:
                result = result * count
            count = count * count
            exp = exp // 2
        return result

    @classmethod
    def Scale(cls, factors):
        result = cls.Identity(4)
        result[0][0], result[1][1], result[2][2] = factors
        return result

    @classmethod
    def View(cls, eye, vd, up):
        result = cls.Identity(4)

        unit_vd = vd.normalized()
        unit_up = up.normalized()

        h = unit_vd.cross(unit_up)
        v = h.cross(unit_vd)

        result[0][:3] = h
        result[1][:3] = v
        result[2][:3] = -unit_vd

        result = result.transposed()

        if eye:
            result = result * cls.Translation(-eye)

        return result

