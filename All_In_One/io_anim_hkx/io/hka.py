#!/usr/bin/env python

"""skeleton.bin anim.bin format
"""

from struct import pack, unpack
from mathutils import Matrix, Quaternion, Vector


def read_headerstring(file):
    bytes = b''
    while True:
        c = file.read(1)
        if c == b'\x0a':  # '\n'
            break
        bytes += c
    str = bytes.decode('utf-8')
    return str


def read_cstring(file):
    bytes = b''
    while True:
        c = file.read(1)
        if c == b'\x00':
            break
        bytes += c
    str = bytes.decode('utf-8')
    return str


def read_float(file):
    return unpack('<f', file.read(4))[0]


def read_int(file):
    return unpack('<i', file.read(4))[0]


def read_short(file):
    return unpack('<h', file.read(2))[0]


def read_vector4_raw(file):
    return unpack('<4f', file.read(16))


def read_vector4(file):
    return Vector(read_vector4_raw(file))


def write_headerstring(file, value):
    bytes = value.encode('utf-8')
    file.write(bytes)
    file.write(b'\x0a')  # '\n'


def write_cstring(file, value):
    bytes = value.encode('utf-8')
    file.write(bytes)
    file.write(b'\x00')


def write_int(file, value):
    file.write(pack('<i', value))


def write_float(file, value):
    file.write(pack('<f', value))


def write_vector4_raw(file, value):
    file.write(pack('<4f', *value))


class Transform(object):
    world_scale = 0.1
    world_scale_reciprocal = 10.0  # := 1/world_scale

    def __init__(self):
        self.translation = Vector((0, 0, 0))
        self.rotation = Quaternion()
        self.scale = 1

    def read(self, file):
        v = read_vector4(file)
        q = read_vector4(file)
        scale = read_vector4(file)

        self.translation = Vector(v.xyz) * self.world_scale
        self.rotation = Quaternion(q.wxyz)
        self.scale = scale.z

    def write(self, file):
        v = self.translation * self.world_scale_reciprocal
        v = (v.x, v.y, v.z, 0)
        q = self.rotation
        q = (q.x, q.y, q.z, q.w)
        scale = (self.scale, self.scale, self.scale, 0)

        write_vector4_raw(file, v)
        write_vector4_raw(file, q)
        write_vector4_raw(file, scale)

    def __mul__(self, other):
        t = Transform()
        v = Vector(other.translation)  # dup
        v.rotate(self.rotation)
        t.translation = self.translation + v * self.scale
        t.rotation = self.rotation * other.rotation
        t.scale = self.scale * other.scale
        return t

    def to_matrix(self):
        m_rotation = self.rotation.to_matrix().to_4x4()  # 3x3 to 4x4
        m_scale = Matrix.Scale(self.scale, 4)
        m = m_rotation * m_scale
        m.translation = self.translation
        return m

    def copy(self):
        t = Transform()
        t.translation = self.translation.copy()
        t.rotation = self.rotation.copy()
        t.scale = self.scale
        return t


class hkaBone(object):

    def __init__(self):
        self.name = None

        self.parent = None
        self.local = None

    def read(self, file):
        self.name = read_cstring(file)

    def world_coordinate(self):
        node = self
        t = Transform()
        while node:
            t = node.local * t
            node = node.parent

        return t


class hkaSkeleton(object):

    def __init__(self):
        self.name = None
        self.parentIndices = []
        self.bones = []
        self.referencePose = []
        self.referenceFloats = []
        self.floatSlots = []

    def load(self, filename):
        with open(filename, 'rb') as file:
            self.load_stream(file)

    def load_stream(self, file):
        head = read_headerstring(file)
        version = read_int(file)  # TODO: unsigned int
        # should be 0x01000000

        nskeletons = read_int(file)
        # should be 1 or 2
        self.read(file)

        nanimations = read_int(file)
        # should be 0

    def read(self, file):
        # A user name to aid in identifying the skeleton
        self.name = read_cstring(file)

        # Parent relationship
        nparentIndices = read_int(file)
        del self.parentIndices[:]
        for i in range(nparentIndices):
            parent_idx = read_short(file)
            self.parentIndices.append(parent_idx)

        # Bones for this skeleton
        nbones = read_int(file)
        del self.bones[:]
        for i in range(nbones):
            bone = hkaBone()
            bone.read(file)
            self.bones.append(bone)

        for i in range(nbones):
            bone = self.bones[i]
            parent_idx = self.parentIndices[i]
            if parent_idx != -1:
                bone.parent = self.bones[parent_idx]

        # The reference pose for the bones of this skeleton. This pose is
        # stored in local space.
        nreferencePose = read_int(file)
        del self.referencePose[:]
        for i in range(nreferencePose):
            transform = Transform()
            transform.read(file)
            self.referencePose.append(transform)

        for i in range(nbones):
            bone = self.bones[i]
            bone.local = self.referencePose[i]

        # The reference values for the float slots of this skeleton. This pose
        # is stored in local space.
        nreferenceFloats = read_int(file)
        del self.referenceFloats[:]
        for i in range(nreferenceFloats):
            f = read_float(file)
            self.referenceFloats.append(f)

        # Floating point track slots. Often used for auxiliary float data or morph target parameters etc.
        # This defines the target when binding animations to a particular rig.
        nfloatSlots = read_int(file)
        del self.floatSlots[:]
        for i in range(nfloatSlots):
            name = read_cstring(file)
            self.floatSlots.append(name)


class hkaPose(object):

    def __init__(self):
        self.time = None
        self.transforms = []
        self.floats = []

    def read(self, file, numTransforms, numFloats):
        self.time = read_float(file)

        # Get a subset of the first 'maxNumTracks' transform tracks (all tracks
        # from 0 to maxNumTracks-1 inclusive), and the first
        # 'maxNumFloatTracks' float tracks of a pose at a given time.

        del self.transforms[:]
        for i in range(numTransforms):
            transform = Transform()
            transform.read(file)
            self.transforms.append(transform)

        del self.floats[:]
        for i in range(numFloats):
            f = read_float(file)
            self.floats.append(f)

    def write(self, file):
        write_float(file, self.time)
        for t in self.transforms:
            t.write(file)
        for f in self.floats:
            write_float(file, f)


class hkaAnimation(object):

    def __init__(self):
        self.numOriginalFrames = None
        self.duration = None
        self.pose = []

    # load anim.bin
    def load(self, filename):
        with open(filename, 'rb') as file:
            self.load_stream(file)

    def load_stream(self, file):
        head = read_headerstring(file)
        version = read_int(file)  # TODO: unsigned int
        if version != 0x01000000:
            raise ValueError('version mismatch!')

        nskeletons = read_int(file)
        if nskeletons != 0:
            raise ValueError(
                '#skeletons should be 0 but {0}!'.format(nskeletons))

        nanimations = read_int(file)
        if nanimations != 1:
            raise ValueError(
                '#animations should be 1 but {0}!'.format(nanimations))

        self.read(file)

    def read(self, file):
        # Returns the number of original samples / frames of animation.
        self.numOriginalFrames = read_int(file)
        # The length of the animation cycle in seconds
        self.duration = read_float(file)
        # The number of bone tracks to be animated.
        numTransforms = read_int(file)
        # The number of float tracks to be animated
        numFloats = read_int(file)

        del self.pose[:]
        for i in range(self.numOriginalFrames):
            pose = hkaPose()
            pose.read(file, numTransforms, numFloats)
            self.pose.append(pose)

    # save anim.bin
    def save(self, filename):
        with open(filename, 'wb') as file:
            self.save_stream(file)

    def save_stream(self, file):
        head = "hkdump File Format, Version 1.0.0.0"
        version = 0x01000000
        nskeletons = 0
        nanimations = 1

        write_headerstring(file, head)
        write_int(file, version)  # TODO: unsigned int
        write_int(file, nskeletons)
        write_int(file, nanimations)

        self.write(file)

    def write(self, file):
        write_int(file, self.numOriginalFrames)
        write_float(file, self.duration)
        write_int(file, len(self.pose[0].transforms))
        write_int(file, len(self.pose[0].floats))
        for p in self.pose:
            p.write(file)
