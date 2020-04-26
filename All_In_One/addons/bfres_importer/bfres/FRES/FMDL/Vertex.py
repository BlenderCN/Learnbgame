import logging; log = logging.getLogger(__name__)

class TexCoord2f:
    def __init__(self, u=0, v=0):
        self.u = u
        self.v = v

    def set(self, *vals):
        if len(vals) > 0: self.u = vals[0]
        if len(vals) > 1: self.v = vals[1]


class Vec4f:
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def set(self, *vals):
        if len(vals) > 0: self.x = vals[0]
        if len(vals) > 1: self.y = vals[1]
        if len(vals) > 2: self.z = vals[2]
        if len(vals) > 3: self.w = vals[3]


class Color:
    def __init__(self, r=1, g=1, b=1, a=1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def set(self, *vals):
        if len(vals) > 0: self.r = vals[0]
        if len(vals) > 1: self.g = vals[1]
        if len(vals) > 2: self.b = vals[2]
        if len(vals) > 3: self.a = vals[3]


class Vertex:
    """A vertex in an FMDL."""

    def __init__(self):
        self.pos      = Vec4f()
        self.normal   = Vec4f()
        self.color    = Color()
        self.texcoord = TexCoord2f()
        self.idx      = [0, 0, 0, 0, 0]
        self.weight   = [1, 0, 0, 0]
        self.extra    = {} # extra attributes


    def setAttr(self, attr, val):
        if   attr.name == '_p0': self.pos.set(*val)
        elif attr.name == '_n0': self.normal.set(*val)
        elif attr.name == '_u0': self.texcoord.set(*val) # XXX cast ints

        elif attr.name == '_i0':
            for i, d in enumerate(val):
                self.idx[i] = d

        elif attr.name == '_w0':
            for i, d in enumerate(val):
                self.weight[i] = d # XXX cast ints

        # XXX _t0, _b0; both are u8 x4
        # XXX _u1 (u16 x2)

        else:
            #log.warn("Unknown attribute '%s'", attr.name)
            self.extra[attr.name] = val


    def __str__(self):
        return "<Vertex(%1.2f, %1.2f, %1.2f) at 0x%X>" % (
            self.pos.x, self.pos.y, self.pos.z,
            id(self))
