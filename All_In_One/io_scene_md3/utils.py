from struct import Struct
from collections import namedtuple
from io import BytesIO


def get_index_of_tuples(ts, index, default):
    return tuple(default if len(t) <= index else t[index] for t in ts)


def noop(value):
    return value


class AnyStruct:
    def __init__(self, name, fields):
        self.ntuple_cls = namedtuple(name, [f[0] for f in fields])
        self.struct = Struct('<' + ''.join([f[1] for f in fields]))
        self.tupling = get_index_of_tuples(fields, 2, 1)
        self.frombin = get_index_of_tuples(fields, 3, noop)
        self.tobin = get_index_of_tuples(fields, 4, noop)

    @property
    def size(self):
        return self.struct.size

    def unpack(self, bs):
        pt = self.struct.unpack(bs)
        t = []
        pti = iter(pt)
        for sz, conv_func in zip(self.tupling, self.frombin):
            if sz == 1:
                value = next(pti)
            else:
                value = tuple(next(pti) for i in range(sz))
            t.append(conv_func(value))
        return self.ntuple_cls._make(t)

    def funpack(self, f):
        return self.unpack(f.read(self.size))

    def pack(self, *a, **kw):
        t = self.ntuple_cls(*a, **kw)
        pt = []
        for value, sz, conv_func in zip(t, self.tupling, self.tobin):
            value = conv_func(value)
            if sz == 1:
                pt.append(value)
            else:
                assert len(value) == sz
                pt.extend(value)
        return self.struct.pack(*pt)

    def fpack(self, f, *a, **kw):
        return f.write(self.pack(*a, **kw))


class OffsetBytesIO:
    def __init__(self, start_offset=0):
        self.shift = start_offset
        self.file = BytesIO(b'')
        self.offsets = {}

    def mark(self, name):
        self.offsets[name] = self.file.tell() + self.shift

    def write(self, data):
        self.file.write(data)

    def getvalue(self):
        return self.file.getvalue()

    def getoffsets(self):
        return self.offsets.copy()
