"""
Name:    rvstruct
Purpose: Reading and writing RV files

Description:
This is a module for reading and writing Re-Volt binary files.
TODO:
- Rework representations and string representations
- Rework default values and variable names based on the game's defaults
- Check for lengths on export

Supported Formats:
- .prm / .m (PRM)
- .w (World)
- .fin (Instances)
- .pan (PosNodes)
- .ncp (Collision)
- .hul (Hull collision)
- .rim (Mirrors) TODO: to_dict()

Missing Formats:
- .fan (AiNodes)
- .taz (TrackZones)
- .fob (Objects)
- .fld (ForceFields)
- .lit (Lights)
- .tri (Triggers)
"""

import os
import struct
from math import ceil, sqrt


class World:
    """
    Reads a .w file and stores all sub-structures
    All contained objects are of a similar structure.
    Usage: Objects of this class can be created to read and store .w files.
    If an opened file is supplied, it immediately starts reading from it.
    """
    def __init__(self, file=None):
        self.mesh_count = 0             # rvlong, amount of Mesh objects
        self.meshes = []                # sequence of Mesh structures

        self.bigcube_count = 0          # rvlong, amount of BigCubes
        self.bigcubes = []              # sequence of BigCubes

        self.animation_count = 0        # rvlong, amount of Texture Animations
        self.animations = []            # sequence of TexAnimation structures

        self.env_count = 0              # amount of faces with env enabled
        self.env_list = []              # list of environment colors

        # Immediately starts reading if an opened file is supplied
        if file:
            self.read(file)

    def read(self, file):

        # Reads the mesh count (num_cubes in RVGL)
        self.mesh_count = struct.unpack("<l", file.read(4))[0]

        # Reads the meshes. Gives the meshes a reference to itself so env_count
        # can be set by the Polygon objects
        for mesh in range(self.mesh_count):
            self.meshes.append(Mesh(file, self))

        # Reads the amount of bigcubes
        self.bigcube_count = struct.unpack("<l", file.read(4))[0]

        # Reads all BigCubes
        for bcube in range(self.bigcube_count):
            self.bigcubes.append(BigCube(file))

        # Reads texture animation count
        self.animation_count = struct.unpack("<l", file.read(4))[0]

        # Reads all animations
        for anim in range(self.animation_count):
            self.animations.append(TexAnimation(file))

        # Reads the environment colors
        for col in range(self.env_count):
            self.env_list.append(Color(file=file, alpha=True))

    def write(self, file):
        # Writes the mesh count
        file.write(struct.pack("<l", self.mesh_count))

        # Writes all meshes, gives reference to self for env count
        for mesh in self.meshes:
            mesh.write(file)

        # Writes the count of BigCubes
        file.write(struct.pack("<l", self.bigcube_count))

        # Writes all BigCubes
        for bcube in self.bigcubes:
            bcube.write(file)

        # Writes the count of texture animations
        file.write(struct.pack("<l", self.animation_count))

        # Writes all texture animations
        for anim in self.animations:
            anim.write(file)

        # self.env_list.write(file)
        for col in self.env_list:
            col.write(file)

    def generate_bigcubes(self):
        bb = BoundingBox()
        for mesh in self.meshes:
            for v in mesh.vertices:
                bb.xlo = v.position.x if v.position.x < bb.xlo else bb.xlo
                bb.xhi = v.position.x if v.position.x > bb.xhi else bb.xhi
                bb.ylo = v.position.y if v.position.y < bb.ylo else bb.ylo
                bb.yhi = v.position.y if v.position.y > bb.yhi else bb.yhi
                bb.zlo = v.position.z if v.position.z < bb.zlo else bb.zlo
                bb.zhi = v.position.z if v.position.z > bb.zhi else bb.zhi

        bcube = BigCube()
        bcube.center = Vector(data=(
            (bb.xlo + bb.xhi) / 2,
            (bb.ylo + bb.yhi) / 2,
            (bb.zlo + bb.zhi) / 2)
        )
        max_vert = Vector(data=(bb.xhi, bb.yhi, bb.zhi))
        bcube.size = bcube.center.get_distance_to(max_vert)

        bcube.mesh_count = len(self.meshes)
        bcube.mesh_indices = [n for n in range(0, bcube.mesh_count)]

        self.bigcube_count = 1
        self.bigcubes = [bcube]

    def __repr__(self):
        return "World"

    def as_dict(self):
        dic = {"mesh_count": self.mesh_count,
               "meshes": self.meshes,
               "bigcube_count": self.bigcube_count,
               "bigcubes": self.bigcubes,
               "animation_count": self.animation_count,
               "animations": self.animations,
               "env_count": self.env_count,
               "env_list": self.env_list
        }
        return dic


class PRM:
    """
    Similar to Mesh, reads, stores and writes PRM files
    """
    def __init__(self, file=None):
        self.polygon_count = 0
        self.vertex_count = 0

        self.polygons = []
        self.vertices = []

        if file:
            self.read(file)

    def __repr__(self):
        return "PRM"

    def read(self, file):
        self.polygon_count = struct.unpack("<h", file.read(2))[0]
        self.vertex_count = struct.unpack("<h", file.read(2))[0]

        for polygon in range(self.polygon_count):
            self.polygons.append(Polygon(file))

        for vertex in range(self.vertex_count):
            self.vertices.append(Vertex(file))

    def write(self, file):
        # Writes amount of polygons/vertices and the structures themselves
        file.write(struct.pack("<h", self.polygon_count))
        file.write(struct.pack("<h", self.vertex_count))

        for polygon in self.polygons:
            polygon.write(file)
        for vertex in self.vertices:
            vertex.write(file)

    def as_dict(self):
        dic = { "polygon_count": self.polygon_count,
                "vertex_count": self.vertex_count,
                "polygons": self.polygons,
                "vertices": self.vertices
        }
        return dic


class Mesh:
    """
    Reads the Meshes found in .w files from an opened file
    These are different from PRM meshes since they also contain
    bounding boxes.
    """
    def __init__(self, file=None, w=None):
        self.w = w                      # World it belongs to

        self.bound_ball_center = None   # Vector
        self.bound_ball_radius = None   # rvfloat

        self.bbox = None                # BoundingBox

        self.polygon_count = None       # rvlong
        self.vertex_count = None        # rvlong

        self.polygons = []              # Sequence of Polygon objects
        self.vertices = []              # Sequence of Vertex objects

        if file:
            self.read(file)

    def __repr__(self):
        return "Mesh"

    def from_prm(self, prm):
        self.polygon_count = prm.polygon_count
        self.vertex_count = prm.vertex_count
        self.polygons = prm.polygons
        self.vertices = prm.vertices

    def read(self, file):
        # Reads bounding "ball" center and the radius
        self.bound_ball_center = Vector(file)
        self.bound_ball_radius = struct.unpack("<f", file.read(4))[0]
        self.bbox = BoundingBox(file)

        # Reads amount of polygons/vertices and the structures themselves
        self.polygon_count = struct.unpack("<h", file.read(2))[0]
        self.vertex_count = struct.unpack("<h", file.read(2))[0]

        # Also give the polygon a reference to w so it can report if env is on
        for polygon in range(self.polygon_count):
            self.polygons.append(Polygon(file, self.w))

        for vertex in range(self.vertex_count):
            self.vertices.append(Vertex(file))

    def write(self, file):
        # Writes bounding "ball" center and the radius and then the bounding box
        self.bound_ball_center.write(file)
        file.write(struct.pack("<f", self.bound_ball_radius))
        self.bbox.write(file)

        file.write(struct.pack("<h", self.polygon_count))
        file.write(struct.pack("<h", self.vertex_count))

        # Also give the polygon a reference to w so it can write the env bit
        for polygon in self.polygons:
            polygon.write(file)
        for vertex in self.vertices:
            vertex.write(file)

    def as_dict(self):
        dic = { "bound_ball_center": self.bound_ball_center,
                "bound_ball_radius": self.bound_ball_radius,
                "bbox": self.bbox,
                "polygon_count": self.polygon_count,
                "vertex_count": self.vertex_count,
                "polygons": self.polygons,
                "vertices": self.vertices,
        }
        return dic


class BoundingBox:
    """
    Reads and stores bounding boxes found in .w meshes
    They are probably used for culling optimization, similar to BigCube
    """
    def __init__(self, file=None, data=None):
        # Lower and higher boundaries for each axis
        if data is None:
            self.xlo = 0
            self.xhi = 0
            self.ylo = 0
            self.yhi = 0
            self.zlo = 0
            self.zhi = 0
        else:
            self.xlo, self.xhi, self.ylo, self.yhi, self.zlo, self.zhi = data

        if file:
            self.read(file)

    def __repr__(self):
        return "BoundingBox"

    def read(self, file):
        # Reads boundaries
        self.xlo, self.xhi = struct.unpack("<ff", file.read(8))
        self.ylo, self.yhi = struct.unpack("<ff", file.read(8))
        self.zlo, self.zhi = struct.unpack("<ff", file.read(8))

    def write(self, file):
        # Writes all boundaries
        file.write(struct.pack("<6f", self.xlo, self.xhi, self.ylo,
                        self.yhi, self.zlo, self.zhi))

    def as_dict(self):
        dic = { "xlo": self.xlo,
                "xhi": self.xhi,
                "ylo": self.ylo,
                "yhi": self.yhi,
                "zlo": self.zlo,
                "zhi": self.zhi
        }
        return dic


class Vector:
    """
    A very simple vector class
    """
    def __init__(self, file=None, data=None):
        if data:
            self.data = [data[0], data[1], data[2]]
        else:
            self.data = [0, 0, 0]

        if file:
            self.read(file)

    def read(self, file):
        # Reads the coordinates
        self.data = [c for c in struct.unpack("<3f", file.read(12))]

    def write(self, file):
        # Writes all coordinates
        file.write(struct.pack("<3f", *self.data))

    def get_distance_to(self, v):
        return sqrt((self.x - v.x)**2 + (self.y - v.y)**2 + (self.z - v.z)**2)

    def scalar(self, v):
        """ Returns the dot/scalar product with v """
        if len(v.data) != len(self.data):
            print("RVSTRUCT ERROR: Vectors are of different lengths.")
            return None
        return sum([v[x] * self[x] for x in range(len(self.data))])

    dot = scalar

    def cross(self, v):
        """ Returns the cross product with v """
        s1, s2, s3 = (
            self[1] * v[2] - self[2] * v[1],
            self[2] * v[0] - self[0] * v[2],
            self[0] * v[1] - self[1] * v[0]
        )
        return Vector(data=(s1, s2, s3))

    def scale(self, a):
        return Vector(data=(self.x * a, self.y * a, self.z * a))

    def magnitude(self):
        return sqrt(sum([self[i] * self[i] for i in range(len(self))]))

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return self
        for i in range(len(self)):
            self[i] /= mag
        return self

    def as_dict(self):
        dic = {"x": self.x,
               "y": self.y,
               "z": self.z
               }
        return dic

    def __add__(self, v):
        return Vector(data=(self[0] + v[0], self[1] + v[1], self[2] + v[2]))

    def __sub__(self, v):
        return Vector(data=(self[0] - v[0], self[1] - v[1], self[2] - v[2]))

    def __truediv__(self, a):
        return Vector(data=(self.x / a, self.y / a, self.z / a))

    def __mul__(self, a):
        return Vector(data=(self.x * a, self.y * a, self.z * a))

    __rmul__ = __mul__

    def __iter__(self):
        for elem in self.data:
            yield elem

    def __getitem__(self, i):
        return self.data[i]

    def __repr__(self):
        return "Vector"

    def __len__(self):
        return len(self.data)

    def __setitem__(self, i, value):
        self.data[i] = value

    @property
    def x(self):
        return self[0]
    @property
    def y(self):
        return self[1]
    @property
    def z(self):
        return self[2]

class Matrix:
    """
    A class for matrices mainly used for orientation and theoretically scale.
    If the matrix is bigger than 3x3, it will be truncated on export.
    """
    def __init__(self, file=None, data=None):
        self.data = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]

        if file:
            self.read(file)

    def __repr__(self):
        return "Matrix"

    def read(self, file):
        # Reads the matrix line by line
        self.data[0] = struct.unpack("<3f", file.read(12))
        self.data[1] = struct.unpack("<3f", file.read(12))
        self.data[2] = struct.unpack("<3f", file.read(12))

    def write(self, file):
        # Writes the matrix line by line (only the firs three columns and rows)
        file.write(struct.pack("<3f", *self.data[:3][0]))
        file.write(struct.pack("<3f", *self.data[:3][1]))
        file.write(struct.pack("<3f", *self.data[:3][2]))

    def as_dict(self):
        dic = {"(0, 0)": self.data[0][0],
               "(0, 1)": self.data[0][1],
               "(0, 2)": self.data[0][2],
               "(1, 0)": self.data[1][0],
               "(1, 1)": self.data[1][1],
               "(1, 2)": self.data[1][2],
               "(2, 0)": self.data[2][0],
               "(2, 1)": self.data[2][1],
               "(2, 2)": self.data[2][2],
        }
        return dic

    def __iter__(self):
        for elem in self.data:
            yield elem

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, value):
        self.data[i] = value


class Polygon:
    """
    Reads a Polygon structure and stores it.
    """
    def __init__(self, file=None, w=None):
        self.w = w                  # World it belongs to

        self.type = 0               # rvshort
        self.texture = 0            # rvshort

        self.vertex_indices = []    # 4 rvshorts
        self.colors = []            # 4 unsigned rvlongs

        self.uv = []                # UV structures (4)

        if file:
            self.read(file)

    def __repr__(self):
        return "Polygon"

    def read(self, file):
        # Reads the type bitfield and the texture index
        self.type = struct.unpack("<h", file.read(2))[0]
        self.texture = struct.unpack("<h", file.read(2))[0]

        # Reads indices of the polygon's vertices and their vertex colors
        self.vertex_indices = struct.unpack("<4H", file.read(8))
        self.colors = [
            Color(file=file, alpha=True),
            Color(file=file, alpha=True), Color(file=file, alpha=True),
            Color(file=file, alpha=True)
        ]
        # Reads the UV mapping
        for x in range(4):
            self.uv.append(UV(file))

        # Tells the .w if bit 11 (environment map) is enabled for this
        if self.w and self.type & 2048:
                self.w.env_count += 1

    def write(self, file):
        # Writes the type bitfield and the texture index
        file.write(struct.pack("<h", self.type))
        file.write(struct.pack("<h", self.texture))

        # Writes indices of the polygon's vertices and their vertex colors
        for ind in self.vertex_indices:
            file.write(struct.pack("<h", ind))
        for col in self.colors:
            col.write(file)
            # file.write(struct.pack("<L", col))

        # Writes the UV coordinates
        for uv in self.uv:
            uv.write(file)

    def as_dict(self):
        dic = { "type": self.type,
                "texture": self.texture,
                "vertex_indices": self.vertex_indices,
                "colors": self.colors,
                "uv": self.uv
        }
        return dic


class Vertex:
    """
    Reads a Polygon structure and stores it
    """
    def __init__(self, file=None):
        self.position = None    # Vector
        self.normal = None      # Vector (normalized, length 1)

        if file:
            self.read(file)

    def __repr__(self):
        return "Vertex"

    def read(self, file):
        # Stores position and normal as a vector
        self.position = Vector(file)
        self.normal = Vector(file)

    def write(self, file):
        # Writes position and normal as a vector
        self.position.write(file)
        self.normal.write(file)

    def as_dict(self):
        dic = {"position": self.position.as_dict(),
               "normal": self.normal.as_dict()
               }
        return dic


class UV:
    """
    Reads UV-map structure and stores it
    """
    def __init__(self, file=None, uv=None):
        if uv:
            self.u, self.v = uv
        else:
            self.u = 0.0     # rvfloat
            self.v = 0.0     # rvfloat

        if file:
            self.read(file)

    def __repr__(self):
        return str(self.as_dict())

    def read(self, file):
        # Reads the uv coordinates
        self.u = struct.unpack("<f", file.read(4))[0]
        self.v = struct.unpack("<f", file.read(4))[0]

    def write(self, file):
        # Writes the uv coordinates
        file.write(struct.pack("<f", self.u))
        file.write(struct.pack("<f", self.v))

    def as_dict(self):
        dic = {"u": self.u,
               "v": self.v
               }
        return dic

    def from_dict(self, dic):
        self.u = dic["u"]
        self.v = dic["v"]


class BigCube:
    """
    Reads a BigCube structure and stores it
    BigCubes are used for in-game optimization (culling)
    """
    def __init__(self, file=None):
        self.center = None      # center/position of the cube, Vector
        self.size = 0           # rvfloat, size of the cube

        self.mesh_count = 0     # rvlong, amount of meshes
        self.mesh_indices = []  # indices of meshes that belong to the cube

        if file:
            self.read(file)

    def __repr__(self):
        return "BigCube"

    def read(self, file):
        # Reads center and size of the cube
        self.center = Vector(file)
        self.size = struct.unpack("<f", file.read(4))[0]

        # Reads amount of meshes and then the indices of the meshes
        self.mesh_count = struct.unpack("<l", file.read(4))[0]
        for mesh in range(self.mesh_count):
            self.mesh_indices.append(struct.unpack("<l", file.read(4))[0])

    def write(self, file):
        # Writes center and size of the cube
        self.center.write(file)
        file.write(struct.pack("<f", self.size))

        # Writes amount of meshes and then the indices of the meshes
        file.write(struct.pack("<l", self.mesh_count))
        for mesh in self.mesh_indices:
            file.write(struct.pack("<l", mesh))

    def as_dict(self):
        dic = { "center": self.center.as_dict(),
                "size": self.size,
                "mesh_count": self.mesh_count,
                "mesh_indices": self.mesh_indices,
        }
        return dic


class TexAnimation:
    """
    Reads and stores a texture animation of a .w file
    """
    def __init__(self, file=None):
        self.frame_count = 0    # rvlong, amount of frames
        self.frames = []        # Frame objects

        if file:
            self.read(file)

    def __repr__(self):
        return "TexAnimation"

    def read(self, file):
        # Reads the amount of frames
        self.frame_count = struct.unpack("<L", file.read(4))[0]

        # Reads the frames themselves
        for frame in range(self.frame_count):
            self.frames.append(Frame(file))

    def write(self, file):
        # Writes the amount of frames
        file.write(struct.pack("<L", self.frame_count))

        # Writes the frames
        for frame in self.frames[:self.frame_count]:
            frame.write(file)

    def as_dict(self):
        dic = { "frame_count": self.frame_count,
                "frames": self.frames
        }
        return dic

    def from_dict(self, dic):
        self.frame_count = dic["frame_count"]
        for framedic in dic["frames"]:
            frame = Frame()
            frame.from_dict(framedic)
            self.frames.append(frame)


class Frame:
    """
    Reads and stores exactly one texture animation frame
    """
    def __init__(self, file=None):
        self.texture = 0                    # texture id of the animated tex
        self.delay = 0                      # delay in milliseconds
        self.uv = [UV(), UV(), UV(), UV()]  # list of 4 UV coordinates

        if file:
            self.read(file)

    def __repr__(self):
        return str(self.as_dict())

    def __str__(self):
        return str(self.as_dict())

    def read(self, file):
        # Reads the texture id
        self.texture = struct.unpack("<l", file.read(4))[0]
        # Reads the delay
        self.delay = struct.unpack("<f", file.read(4))[0]

        # Reads the UV coordinates for this frame
        for uv in range(4):
            self.uv[uv] = UV(file)

    def write(self, file):
        # Writes the texture id
        file.write(struct.pack("<l", self.texture))
        # Writes the delay
        file.write(struct.pack("<f", self.delay))

        # Writes the UV coordinates for this frame
        for uv in self.uv[:4]:
            uv.write(file)

    def as_dict(self):
        dic = { "texture": self.texture,
                "delay": self.delay,
                "uv": [uv.as_dict() for uv in self.uv]
        }
        return dic

    def from_dict(self, dic):
        self.texture = dic["texture"]
        self.delay = dic["delay"]
        uvs = []
        for x in range(0, 4):
            uvdict = dic["uv"][x]
            uv = UV()
            uv.from_dict(uvdict)
            uvs.append(uv)
        self.uv = uvs


class Color:
    """
    Stores a color with optional alpha (RGB).
    """
    def __init__(self, file=None, color=(0, 0, 0), alpha=False):
        self.color = color          # RGB color
        self.alpha = alpha          # False or int from 0 to 255

        if file:
            self.read(file)

    def read(self, file):
        cols = struct.unpack("<BBB", file.read(3))
        self.color = (cols[2], cols[1], cols[0])
        # Reads alpha only when alpha == True
        if self.alpha:
            self.alpha = 255 - struct.unpack("<B", file.read(1))[0]

    def write(self, file):
        file.write(struct.pack("<3B", self.color[2],
                               self.color[1], self.color[0]))
        # Writes only if alpha is specified
        if self.alpha is not False and self.alpha is not None:
            file.write(struct.pack("<B", 255 - self.alpha))

    def as_dict(self):
        dic = { "r": self.color[0],
                "g": self.color[1],
                "b": self.color[2],
                "alpha": self.alpha
        }
        return dic


    def __repr__(self):
        return "Color"

        def __str__(self):
            return "Color ({}, {}, {}, {})".format(*self.color, self.alpha)


class Instances:
    """
    Reads and writes a list of instance objects (takes a .fin file).
    """
    def __init__(self, file=None):
        self.instance_count = 0          # number of instance objects
        self.instances = []              # list of Instance objects

        if file:
            self.read(file)

    def __repr__(self):
        return "Instances"

    def read(self, file):
        # Reads the specified amount of instances and adds it to the list
        self.instance_count = struct.unpack("<l", file.read(4))[0]
        for instance in range(self.instance_count):
            self.instances.append(Instance(file))

    def write(self, file):
        # Writes the amount of instances
        file.write(struct.pack("<l", self.instance_count))
        # Writes all instances
        for instance in self.instances:
            instance.write(file)

    def as_dict(self):
        dic = { "instance_count": self.instance_count,
                "instances": self.instances
        }
        return dic


class Instance:
    """
    Reads and writes properties of an instanced object found in .fin files.
    """
    def __init__(self, file=None):
        self.name = ""                            # first 8 letters of file name
        self.color = (0, 0, 0)       # model % RGB color
        self.env_color = Color(color=[0, 0, 0], alpha=True) # envMap color
        self.priority = 0                         # priority for multiplayer
        self.flag = 0                             # flag with properties
        self.lod_bias = 1024                      # when to load hq-meshes
        self.position = Vector(data=(0, 0, 0))    # position of the PRM
        self.or_matrix = Matrix(data=((0, 0, 0),
                                      (0, 0, 0),
                                      (0, 0, 0))) # orientation of the PRM

        if file:
            self.read(file)

    def __repr__(self):
        return "Instance"

    def read(self, file):
        # Reads the file name and cleans it up (remove whitespace and .prm)
        self.name = struct.unpack("<9s", file.read(9))[0]
        self.name = str(self.name, encoding='ascii').split('\x00', 1)[0]
        # Reads the model color and the envMap color
        self.color = struct.unpack("<3b", file.read(3))
        self.env_color = Color(file, alpha=True)
        # Reads priority and properties flag with two padded bytes
        self.priority, self.flag = struct.unpack('<BBxx', file.read(4))
        self.lod_bias = struct.unpack("<f", file.read(4))[0]
        self.position = Vector(file)
        self.or_matrix = Matrix(file)

    def write(self, file):
        # Writes the first 8 letters of the prm file name
        name = str.encode(self.name)
        file.write(struct.pack("9s", name))
        file.write(struct.pack("<3b", *self.color))
        self.env_color.write(file)
        # Writes priority and properties flag with two padded bytes
        file.write(struct.pack('<BBxx', self.priority, self.flag))
        file.write(struct.pack('<f', self.lod_bias))
        self.position.write(file)
        self.or_matrix.write(file)

    def as_dict(self):
        dic = { "name": self.name,
                "color": self.color,
                "env_color": self.env_color,
                "priority": self.priority,
                "flag": self.flag,
                "lod_bias": self.lod_bias,
                "position": self.position,
                "or_matrix": self.or_matrix
        }
        return dic


class PosNodes:
    """
    Position nodes level file (.pan)
    """
    def __init__(self, file=None):
        self.num_nodes = 0
        self.start_node = 0
        self.total_dist = 0
        self.nodes = []

        if file:
            self.read(file)

    def read(self, file):
        self.num_nodes = struct.unpack("<l", file.read(4))[0]
        self.start_node = struct.unpack("<l", file.read(4))[0]
        self.total_dist = struct.unpack("<f", file.read(4))[0]
        self.nodes = [PosNode(file) for n in range(self.num_nodes)]

    def as_dict(self):
        dic = { "num_nodes": self.num_nodes,
                "start_node": self.start_node,
                "total_dist": self.total_dist,
                "nodes": self.nodes
        }
        return dic

    def __repr__(self):
        return "PosNodes"

class PosNode:
    """
    Single node of PosNodes file.
    """
    def __init__(self, file=None):
        self.position = Vector()
        self.distance = 0
        self.next = [-1, -1, -1, -1]
        self.prev = [-1, -1, -1, -1]

        if file:
            self.read(file)

    def read(self, file):
        # Reads position
        self.position = Vector(file)

        # Reads distance to finish line
        self.distance = struct.unpack("<f", file.read(4))[0]

        # Reads previous connections
        for x in range(4):
            self.prev[x] = struct.unpack("<l", file.read(4))[0]

        # Reads upcoming connections
        for x in range(4):
            self.next[x] = struct.unpack("<l", file.read(4))[0]

    def as_dict(self):
        dic = { "position": self.position,
                "distance": self.distance,
                "next": self.next,
                "previous": self.prev,
        }
        return dic

    def __repr__(self):
        return "PosNode"


class NCP:
    def __init__(self, file=None):
        self.polyhedron_count = 0
        self.polyhedra = []

        if not file:
            self.lookup_grid = LookupGrid()
        else:
            self.lookup_grid = None
            self.read(file)

    def read(self, file):
        # Takes note of file start and end
        file_start = file.tell()
        file.seek(0, os.SEEK_END)
        file_end = file.tell()
        file.seek(file_start, os.SEEK_SET)

        # Reads ncp information
        self.polyhedron_count = struct.unpack("<h", file.read(2))[0]
        self.polyhedra = [Polyhedron(file) for x in range(self.polyhedron_count)]

        # If file has collision grid info
        if file.tell() < file_end:
            self.lookup_grid = LookupGrid(file)
        else:
            self.lookup_grid = None

    def write(self, file):
        # Writes the polyhedron count
        file.write(struct.pack("<h", self.polyhedron_count))

        # Writes all polyhedra
        for p in range(self.polyhedron_count):
            self.polyhedra[p].write(file)

        if self.lookup_grid:
            self.lookup_grid.write(file)

    def generate_lookup_grid(self, grid_size=None):
        grid = LookupGrid()
        if grid_size is None:
            grid.size = 1024
        else:
            grid.size = grid_size

        bbox = BoundingBox(data=(
            min([poly.bbox.xlo for poly in self.polyhedra]),
            max([poly.bbox.xhi for poly in self.polyhedra]),
            0,
            0,
            min([poly.bbox.zlo for poly in self.polyhedra]),
            max([poly.bbox.zhi for poly in self.polyhedra]))
        )

        grid.xsize = ceil((bbox.xhi - bbox.xlo) / grid.size)
        grid.zsize = ceil((bbox.zhi - bbox.zlo) / grid.size)

        grid.x0 = (bbox.xlo + bbox.xhi - grid.xsize * grid.size) / 2
        grid.z0 = (bbox.zlo + bbox.zhi - grid.zsize * grid.size) / 2

        for z in range(grid.zsize):
            zlo = grid.z0 + z * grid.size - 150
            zhi = grid.z0 + (z + 1) * grid.size + 150

            for x in range(grid.xsize):
                xlo = grid.x0 + x * grid.size - 150
                xhi = grid.x0 + (x + 1) * grid.size + 150

                lookup = LookupList()
                for i, poly in enumerate(self.polyhedra):
                    if (poly.bbox.zhi > zlo and poly.bbox.zlo < zhi and
                            poly.bbox.xhi > xlo and poly.bbox.xlo < xhi):
                        lookup.polyhedron_idcs.append(i)

                lookup.length = len(lookup.polyhedron_idcs)
                grid.lists.append(lookup)

        self.lookup_grid = grid
        return self

    def as_dict(self):
        if not self.lookup_grid:
            lookup_grid = None
        else:
            lookup_grid = self.lookup_grid.as_dict()
        dic = {"polyhedron_count": self.polyhedron_count,
               "polyhedra": [p.as_dict() for p in self.polyhedra],
               "lookup_grid": lookup_grid
               }
        return dic


class Polyhedron:
    def __init__(self, file=None):
        self.type = 0
        self.material = 0
        self.planes = []
        if not file:
            self.bbox = BoundingBox()
        if file:
            self.bbox = None
            self.read(file)

    def read(self, file):
        self.type = struct.unpack("<L", file.read(4))[0]
        self.material = struct.unpack("<L", file.read(4))[0]

        self.planes = [Plane(file) for x in range(5)]

        self.bbox = BoundingBox(file)

    def write(self, file):
        # Writes the type
        file.write(struct.pack("<L", self.type))
        # Writes the surface material
        file.write(struct.pack("<L", self.material))
        # Writes the 5 planes
        [p.write(file) for p in self.planes[:5]]
        # Writes the BBOX
        self.bbox.write(file)

    def as_dict(self):
        dic = {"type": self.type,
               "material": self.material,
               "planes": [p.as_dict() for p in self.planes],
               "bbox": self.bbox.as_dict()
               }
        return dic


class Plane:
    def __init__(self, file=None, n=None, d=None):
        if n is not None:
            self.normal = n
        else:
            self.normal = Vector()

        if d is not None:
            self.distance = d
        else:
            self.distance = 0.0

        if file:
            self.read(file)

    def contains_vertex(self, vertex):
        # Get one point of the plane
        p = (-1 * self.normal.scale(self.distance)).normalize()
        result = self.normal.dot(vertex-p)

        # result = (vertex[0] - p[0]) * self.normal[0] + (vertex[1] - p[1]) * self.normal[1] + (vertex[2] - p[2]) * self.normal[2]
        #Where (x, y, z) is the point your testing, (x0, y0, z0) is the point derived from the normal and (Dx, Dy, Dz) is the normal itself

        if abs(result) < 0.5:
            return True
        else:
            print(result)
            return False

    def read(self, file):
        self.normal = Vector(file=file)
        self.distance = struct.unpack("<f", file.read(4))[0]

    def write(self, file):
        # Writes the normal vector
        self.normal.write(file)
        # Writes the plane distance
        file.write(struct.pack("<f", self.distance))

    def as_dict(self):
        dic = {"normal": self.normal.as_dict(),
               "distance": self.distance
               }
        return dic


class LookupGrid:
    def __init__(self, file=None):
        self.x0 = 0.0
        self.z0 = 0.0

        self.xsize = 0.0
        self.zsize = 0.0

        self.size = 0.0

        self.lists = []

        if file:
            self.read(file)

    def read(self, file):
        self.x0, self.z0 = struct.unpack("<ff", file.read(8))

        # Reads the size of the grid (stored as a float, hence casted)
        sizes = [int(s) for s in struct.unpack("<ff", file.read(8))]
        self.xsize, self.zsize = sizes

        self.size = struct.unpack("<f", file.read(4))[0]

        self.lists = [LookupList(file) for x in range(self.xsize * self.zsize)]

    def write(self, file):
        # Writes the lookup grid data
        file.write(struct.pack("<f", self.x0))
        file.write(struct.pack("<f", self.z0))
        file.write(struct.pack("<f", self.xsize))
        file.write(struct.pack("<f", self.zsize))
        file.write(struct.pack("<f", self.size))
        # Writes the lists
        for x in range(int(self.xsize) * int(self.zsize)):
            self.lists[x].write(file)

    def as_dict(self):
        dic = {"x0": self.x0,
               "z0": self.z0,
               "xsize": self.xsize,
               "zsize": self.zsize,
               "size": self.size,
               "lists": [l.as_dict() for l in self.lists]
               }
        return dic


class LookupList:
    def __init__(self, file=None):
        self.length = 0
        self.polyhedron_idcs = []

        if file:
            self.read(file)

    def read(self, file):
        self.length = struct.unpack("<L", file.read(4))[0]
        for x in range(self.length):
            self.polyhedron_idcs.append(struct.unpack("<L", file.read(4))[0])

    def write(self, file):
        file.write(struct.pack("<L", self.length))
        # Writes the polyhedron indices
        for x in range(self.length):
            file.write(struct.pack("<L", self.polyhedron_idcs[x]))

    def as_dict(self):
        dic = {"length": self.length,
               "polyhedron_idcs": self.polyhedron_idcs
        }
        return dic


class Hull:
    def __init__(self, file=None):
        self.chull_count = 0
        self.chulls = []  # ConvexHulls

        self.interior = Interior()

        if file:
            self.read(file)

    def read(self, file):
        self.chull_count = struct.unpack("<h", file.read(2))[0]
        self.chulls = [ConvexHull(file) for x in range(self.chull_count)]
        self.interior = Interior(file)

    def write(self, file):
        file.write(struct.pack("<h", self.chull_count))
        for x in range(self.chull_count):
            self.chulls[x].write(file)
        self.interior.write(file)

    def as_dict(self):
        dic = {"chull_count": self.chull_count,
               "chulls": [c.as_dict() for c in self.chulls],
               "interior": self.interior.as_dict()
        }
        return dic


class ConvexHull:
    """ ConvexHull used in .hul """
    def __init__(self, file=None):
        self.vertex_count = 0
        self.edge_count = 0
        self.face_count = 0

        self.bbox = BoundingBox()
        self.bbox_offset = Vector()

        self.vertices = []  # Vectors
        self.edges = []  # Edges
        self.faces = []  # Planes

        if file:
            self.read(file)

    def as_dict(self):
        dic = {"vertex_count": self.vertex_count,
               "edge_count": self.edge_count,
               "face_count": self.face_count,
               "bbox": self.bbox.as_dict(),
               "bbox_offset": self.bbox_offset.as_dict(),
               "vertices": [v.as_dict() for v in self.vertices],
               "edges": [e.as_dict() for e in self.edges],
               "faces": [f.as_dict() for f in self.faces],
        }
        return dic

    def read(self, file):
        self.vertex_count = struct.unpack("<h", file.read(2))[0]
        self.edge_count = struct.unpack("<h", file.read(2))[0]
        self.face_count = struct.unpack("<h", file.read(2))[0]

        self.bbox = BoundingBox(file)
        self.bbox_offset = Vector(file)

        self.vertices = [Vector(file) for x in range(self.vertex_count)]
        self.edges = [Edge(file) for x in range(self.edge_count)]
        self.faces = [Plane(file) for x in range(self.face_count)]

    def write(self, file):
        file.write(struct.pack("<h", self.vertex_count))
        file.write(struct.pack("<h", self.edge_count))
        file.write(struct.pack("<h", self.face_count))

        self.bbox.write(file)
        self.bbox_offset.write(file)

        for x in range(self.vertex_count):
            self.vertices[x].write(file)
        for x in range(self.edge_count):
            self.edges[x].write(file)
        for x in range(self.face_count):
            self.faces[x].write(file)


class Edge:
    """ Edge used in .hul """
    def __init__(self, file=None):
        self.vertices = []  # Integer indices

        if file:
            self.read(file)

    def read(self, file):
        self.vertices = [struct.unpack("<h", file.read(2))[0] for x in range(2)]

    def write(self, file):
        file.write(struct.pack("<hh", *self.vertices))

    def __getitem__(self, i):
        return self.vertices[i]

    def as_dict(self):
        dic = {"vertices": self.vertices}
        return dic


class Interior:
    """ Interior used in .hul """
    def __init__(self, file=None):
        self.sphere_count = 0
        self.spheres = []  # Spheres

        if file:
            self.read(file)

    def read(self, file):
        self.sphere_count = struct.unpack("<h", file.read(2))[0]
        self.spheres = [Sphere(file) for x in range(self.sphere_count)]

    def write(self, file):
        file.write(struct.pack("<h", self.sphere_count))
        for x in range(self.sphere_count):
            self.spheres[x].write(file)

    def as_dict(self):
        dic = {"sphere_count": self.sphere_count,
               "spheres": [s.as_dict() for s in self.spheres],
        }
        return dic


class Sphere:
    """ Sphere used in .hul """
    def __init__(self, file=None):
        self.center = Vector()
        self.radius = 0.0

        if file:
            self.read(file)

    def read(self, file):
        self.center = Vector(file)
        self.radius = struct.unpack("<f", file.read(4))[0]

    def write(self, file):
        self.center.write(file)
        file.write(struct.pack("<f", self.radius))

    def as_dict(self):
        dic = {"center": self.center.as_dict(),
               "radius": self.radius,
        }
        return dic


class RIM:
    """ Mirror planes """
    def __init__(self, file=None):
        self.num_mirror_planes = 0
        self.mirror_planes = []

        if file:
            self.read(file)

    def read(self, file):
        self.num_mirror_planes = struct.unpack("<h", file.read(2))[0]
        self.mirror_planes = [MirrorPlane(file) for x in range(self.num_mirror_planes)]

    def write(self, file):
        file.write(struct.pack("<h", self.num_mirror_planes))
        for x in range(self.num_mirror_planes):
            self.mirror_planes[x].write(file)

class MirrorPlane:
    """ Mirror plane """
    def __init__(self, file=None):
        self.flag = 0  # unused
        self.plane = Plane()
        self.bounding_box = BoundingBox()
        self.vertices = []

        if file:
            self.read(file)

    def read(self, file):
        self.flag = struct.unpack("<L", file.read(4))[0]
        self.plane = Plane(file)
        self.bounding_box = BoundingBox(file)
        self.vertices = [Vector(file) for x in range(4)]

    def write(self, file):
        file.write(struct.pack("<L", self.flag))
        self.plane.write(file)
        self.bounding_box.write(file)
        for v in self.vertices:
            v.write(file)