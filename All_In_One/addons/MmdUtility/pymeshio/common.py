# coding: utf-8
"""
common utilities.
"""
import math
import struct
import sys
import io


def unicode(src):
    """
    literal to unicode for python2 and python3 compatiblity.

    in python2 str to unicode.
    in python3 str(as unicode) to str.
    """
    if sys.version_info[0]<3:
        return src.decode('utf-8')
    else:
        return src

"""
common structures.
"""
class Vector2(object):
    """
    2D coordinate for uv value
    """
    __slots__=['x', 'y']
    def __init__(self, x=0, y=0):
        self.x=x
        self.y=y

    def __str__(self):
        return "<%f %f>" % (self.x, self.y)

    def __eq__(self, rhs):
        return self.x==rhs.x and self.y==rhs.y

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y)

    def cross(self, rhs):
        """cross(outer) product"""
        return self.x*rhs.y-self.y*rhs.x


class Vector3(object):
    """
    3D coordinate for vertex position, normal direction
    """
    __slots__=['x', 'y', 'z']
    def __init__(self, x=0, y=0, z=0):
        self.x=x
        self.y=y
        self.z=z

    def __str__(self):
        return "<%f %.32f %f>" % (self.x, self.y, self.z)

    def __eq__(self, rhs):
        #return self.x==rhs.x and self.y==rhs.y and self.z==rhs.z
        return (
                abs(self.x-rhs.x)<11e-3
                and abs(self.y-rhs.y)<11e-3
                and abs(self.z-rhs.z)<11e-3
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        elif key==2:
            return self.z
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def __add__(self, r):
        return Vector3(self.x+r.x, self.y+r.y, self.z+r.z)

    def __sub__(self, rhs):
        return Vector3(self.x-rhs.x, self.y-rhs.y, self.z-rhs.z)

    def getSqNorm(self):
        return self.x*self.x + self.y*self.y + self.z*self.z

    def getNorm(self):
        return math.sqrt(self.getSqNorm())

    def normalize(self):
        factor=1.0/self.getNorm()
        self.x*=factor
        self.y*=factor
        self.z*=factor
        return self

    def to_a(self):
        return [self.x, self.y, self.z]

    def dot(self, rhs):
        """dot(inner) product"""
        return self.x*rhs.x + self.y*rhs.y + self.z*rhs.z

    def cross(self, rhs):
        """cross(outer) product"""
        return Vector3(
                self.y*rhs.z - rhs.y*self.z,
                self.z*rhs.x - rhs.z*self.x,
                self.x*rhs.y - rhs.x*self.y,
                )


class Vector4(object):
    """
    4D coordinate for vertex position, normal direction
    """
    __slots__=['x', 'y', 'z', 'w']
    def __init__(self, x=0, y=0, z=0, w=0):
        self.x=x
        self.y=y
        self.z=z
        self.w=w

    def __str__(self):
        return "<%f %.32f %f %f>" % (self.x, self.y, self.z, self.w)

    def __eq__(self, rhs):
        #return self.x==rhs.x and self.y==rhs.y and self.z==rhs.z
        return (
                abs(self.x-rhs.x)<11e-3
                and abs(self.y-rhs.y)<11e-3
                and abs(self.z-rhs.z)<11e-3
                and abs(self.w-rhs.w)<11e-3
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __neg__(self):
        return Vector4(-self.x, -self.y, -self.z, -self.w)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        elif key==2:
            return self.z
        elif key==3:
            return self.w
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y, self.z, self.w)

    def __add__(self, r):
        return Vector4(self.x+r.x, self.y+r.y, self.z+r.z, self.w+r.w)

    def __sub__(self, rhs):
        return Vector4(self.x-rhs.x, self.y-rhs.y, self.z-rhs.z, self.w-rhs.w)

    def getSqNorm(self):
        return self.x*self.x + self.y*self.y + self.z*self.z + self.w*self.w

    def getNorm(self):
        return math.sqrt(self.getSqNorm())

    def normalize(self):
        factor=1.0/self.getNorm()
        self.x*=factor
        self.y*=factor
        self.z*=factor
        self.w*=factor
        return self

    def to_a(self):
        return [self.x, self.y, self.z, self.w]

    def dot(self, rhs):
        """dot(inner) product"""
        return self.x*rhs.x + self.y*rhs.y + self.z*rhs.z + self.w*rhs.w


class Quaternion(object):
    """
    rotation representation in vmd motion
    """
    __slots__=['x', 'y', 'z', 'w']
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x=x
        self.y=y
        self.z=z
        self.w=w

    def __str__(self):
        return "<%f %f %f %f>" % (self.x, self.y, self.z, self.w)

    def __mul__(self, rhs):
        u=numpy.array([self.x, self.y, self.z], 'f')
        v=numpy.array([rhs.x, rhs.y, rhs.z], 'f')
        xyz=self.w*v+rhs.w*u+numpy.cross(u, v)
        q=Quaternion(xyz[0], xyz[1], xyz[2], self.w*rhs.w-numpy.dot(u, v))
        return q

    def dot(self, rhs):
        return self.x*rhs.x+self.y*rhs.y+self.z*rhs.z+self.w*rhs.w

    def getMatrix(self):
        sqX=self.x*self.x
        sqY=self.y*self.y
        sqZ=self.z*self.z
        xy=self.x*self.y
        xz=self.x*self.z
        yz=self.y*self.z
        wx=self.w*self.x
        wy=self.w*self.y
        wz=self.w*self.z
        return numpy.array([
                # 1
                [1-2*sqY-2*sqZ, 2*xy+2*wz, 2*xz-2*wy, 0],
                # 2
                [2*xy-2*wz, 1-2*sqX-2*sqZ, 2*yz+2*wx, 0],
                # 3
                [2*xz+2*wy, 2*yz-2*wx, 1-2*sqX-2*sqY, 0],
                # 4
                [0, 0, 0, 1]],
                'f')

    def getRHMatrix(self):
        x=-self.x
        y=-self.y
        z=self.z
        w=self.w
        sqX=x*x
        sqY=y*y
        sqZ=z*z
        xy=x*y
        xz=x*z
        yz=y*z
        wx=w*x
        wy=w*y
        wz=w*z
        return numpy.array([
                # 1
                [1-2*sqY-2*sqZ, 2*xy+2*wz, 2*xz-2*wy, 0],
                # 2
                [2*xy-2*wz, 1-2*sqX-2*sqZ, 2*yz+2*wx, 0],
                # 3
                [2*xz+2*wy, 2*yz-2*wx, 1-2*sqX-2*sqY, 0],
                # 4
                [0, 0, 0, 1]],
                'f')

    def getRollPitchYaw(self):
        m=self.getMatrix()

        roll = math.atan2(m[0, 1], m[1, 1])
        pitch = math.asin(-m[2, 1])
        yaw = math.atan2(m[2, 0], m[2, 2])

        if math.fabs(math.cos(pitch)) < 1.0e-6:
            roll += m[0, 1] > math.pi if 0.0 else -math.pi
            yaw += m[2, 0] > math.pi if 0.0 else -math.pi

        return roll, pitch, yaw

    def getSqNorm(self):
        return self.x*self.x+self.y*self.y+self.z*self.z+self.w*self.w

    def getNormalized(self):
        f=1.0/self.getSqNorm()
        q=Quaternion(self.x*f, self.y*f, self.z*f, self.w*f)
        return q

    def getRightHanded(self):
        "swap y and z axis"
        return Quaternion(-self.x, -self.z, -self.y, self.w)

    @staticmethod
    def createFromAxisAngle(axis, rad):
        q=Quaternion()
        half_rad=rad/2.0
        c=math.cos(half_rad)
        s=math.sin(half_rad)
        return Quaternion(axis[0]*s, axis[1]*s, axis[2]*s, c)


class RGB(object):
    """
    material color
    """
    __slots__=['r', 'g', 'b']
    def __init__(self, r=0, g=0, b=0):
        self.r=r
        self.g=g
        self.b=b

    def __str__(self):
        return "<%f %f %f>" % (self.r, self.g, self.b)

    def __eq__(self, rhs):
        return self.r==rhs.r and self.g==rhs.g and self.b==rhs.b

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __getitem__(self, key):
        if key==0:
            return self.r
        elif key==1:
            return self.g
        elif key==2:
            return self.b
        else:
            assert(False)


class RGBA(object):
    """
    material color
    """
    __slots__=['r', 'g', 'b', 'a']
    def __init__(self, r=0, g=0, b=0, a=1):
        self.r=r
        self.g=g
        self.b=b
        self.a=a

    def __eq__(self, rhs):
        return self.r==rhs.r and self.g==rhs.g and self.b==rhs.b and self.a==rhs.a

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __getitem__(self, key):
        if key==0:
            return self.r
        elif key==1:
            return self.g
        elif key==2:
            return self.b
        elif key==3:
            return self.a
        else:
            assert(False)


"""
utilities
"""
def radian_to_degree(x):
    """darian to deglee"""

    return x/math.pi * 180.0


class ParseException(Exception):
    """
    Exception in reader
    """
    def __init__(self, message):
        self.message=message


def readall(path):
    """read all bytes from path
    """
    with open(path, "rb") as f:
        return f.read()


class BinaryReader(object):
    """general BinaryReader
    """
    def __init__(self, ios):
        current=ios.tell()
        #ios.seek(0, io.SEEK_END)
        ios.seek(0, 2)
        self.end=ios.tell()
        ios.seek(current)
        self.ios=ios

    def __str__(self):
        return "<BinaryReader %d/%d>" % (self.ios.tell(), self.end)

    def is_end(self):
        #print(self.ios.tell(), self.end)
        return self.ios.tell()>=self.end
        #return not self.ios.readable()

    def unpack(self, fmt, size):
        result=struct.unpack(fmt, self.ios.read(size))
        return result[0]

    def read_int(self, size):
        if size==1:
            return self.unpack("b", size)
        if size==2:
            return self.unpack("h", size)
        if size==4:
            return self.unpack("i", size)
        print("not reach here")
        raise ParseException("invalid int size: "+size)

    def read_uint(self, size):
        if size==1:
            return self.unpack("B", size)
        if size==2:
            return self.unpack("H", size)
        if size==4:
            return self.unpack("I", size)
        print("not reach here")
        raise ParseException("invalid int size: "+size)

    def read_float(self):
        return self.unpack("f", 4)

    def read_vector2(self):
        return Vector2(
                self.read_float(), 
                self.read_float()
                )

    def read_vector3(self):
        return Vector3(
                self.read_float(), 
                self.read_float(), 
                self.read_float()
                )

    def read_vector4(self):
        return Vector4(
                self.read_float(), 
                self.read_float(), 
                self.read_float(),
                self.read_float()
                )

    def read_quaternion(self):
        return Quaternion(
                self.read_float(), 
                self.read_float(), 
                self.read_float(),
                self.read_float()
                )

    def read_quaternion(self):
        return Quaternion(
                self.read_float(), 
                self.read_float(), 
                self.read_float(),
                self.read_float()
                )

    def read_rgba(self):
        return RGBA(
                self.read_float(), 
                self.read_float(), 
                self.read_float(),
                self.read_float()
                )

    def read_rgb(self):
        return RGB(
                self.read_float(), 
                self.read_float(), 
                self.read_float()
                )


class WriteException(Exception):
    """
    Exception in writer
    """
    pass


class BinaryWriter(object):
    def __init__(self, ios):
        self.ios=ios

    def write_bytes(self, v, size=None):
        if size:
            self.ios.write(struct.pack("={0}s".format(size), v))
        else:
            self.ios.write(v)

    def write_float(self, v):
        self.ios.write(struct.pack("f", v))

    def write_int(self, v, size):
        if size==1:
            self.ios.write(struct.pack("b", v))
        elif size==2:
            self.ios.write(struct.pack("h", v))
        elif size==4:
            self.ios.write(struct.pack("i", v))
        else:
            raise WriteError("invalid int uint size")

    def write_uint(self, v, size):
        if v==-1:
            if size==1:
                self.ios.write(struct.pack("B", 255))
            elif size==2:
                self.ios.write(struct.pack("H", 65535))
            elif size==4:
                self.ios.write(struct.pack("I", 4294967295))
            else:
                raise WriteError("invalid int uint size")
        else:
            if size==1:
                self.ios.write(struct.pack("B", v))
            elif size==2:
                self.ios.write(struct.pack("H", v))
            elif size==4:
                self.ios.write(struct.pack("I", v))
            else:
                raise WriteError("invalid int uint size")

    def write_vector2(self, v):
        self.ios.write(struct.pack("=2f", v.x, v.y))

    def write_vector3(self, v):
        self.ios.write(struct.pack("=3f", v.x, v.y, v.z))

    def write_rgb(self, v):
        self.ios.write(struct.pack("=3f", v.r, v.g, v.b))

    def write_rgba(self, v):
        self.ios.write(struct.pack("=4f", v.r, v.g, v.b, v.a))


class DifferenceException(Exception):
    def __init__(self, message):
        self.message=message


class Diff(object):
    def _diff(self, rhs, key):
        l=getattr(self, key)
        r=getattr(rhs, key)
        if l!=r:
            raise DifferenceException("{lhs}.{key}:{lvalue} != {rhs}.{key}:{rvalue}".format(
                key=key, lhs=self, rhs=rhs, lvalue=l, rvalue=r))

    def _diff_array(self, rhs, key):
        la=getattr(self, key)
        ra=getattr(rhs, key)
        if len(la)!=len(ra):
            raise DifferenceException("%s diffrence %d with %d" % (key, len(la), len(ra)))
        for i, (l, r) in enumerate(zip(la, ra)):
            if isinstance(l, Diff):
                try:
                    l.diff(r)
                except DifferenceException as e:
                    raise DifferenceException(
                            "{lhs}.{key}[{i}] with {rhs}.{key}[{i}]: {message}".format(
                                lhs=self, rhs=rhs, key=key, i=i, message=e.message))
            else:
                if l!=r:
                    raise DifferenceException("{lhs}.{key}[{i}] != {rhs}.{key}[{i}]".format(
                        lhs=self, rhs=rhs, key=key, i=i))

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class TextReader(object):
    """ base class for text format
    """
    __slots__=[
            "eof", "ios", "lines",
            ]
    def __init__(self, ios):
        self.ios=ios
        self.eof=False
        self.lines=0

    def getline(self):
        line=self.ios.readline()
        self.lines+=1
        if line==b"":
            self.eof=True
            return None
        return line.strip()

    def printError(self, method, msg):
        print("%s:%s:%d" % (method, msg, self.lines))

