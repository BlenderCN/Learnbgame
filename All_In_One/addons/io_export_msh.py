bl_info = {
    "name":         "MSH File Format",
    "author":       "Brandon Surmanski",
    "blender":      (2,7,3),
    "version":      (0,0,2),
    "location":     "File > Import-Export",
    "description":  "Export custom MSH format",
    "category": "Learnbgame",
}

import bpy
import bmesh

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from mathutils import *
from math import *
import struct
import bisect


"""
MSH file format export

HEADER:
    3 byte: magic number (MDL)
    1 byte: version number (6)
    2 byte: number of verts
    2 byte: number of uvs
    2 byte: number of faces
    2 byte: number of edges
    2 byte: number of bones
    2 byte: padding
    15 byte: name
    1 byte: NULL
    32

VERT:
    12 byte: position (3 * 4 byte float)
    6 byte: normal (3 * signed short) (normalized from -32768 to 32767) #TODO implicit Z
    4 byte: padding (OR UV position)
    4 byte: padding (OR RGB vertex color and material index)
    1 byte: boneID 1
    1 byte: boneID 2
    1 byte: bone weight 1
    1 byte: bone weight 2
    2 byte: incident edge id
    32

UV:
    4 byte: position (2 * signed short) (normalized from 0 to 65535)
    2 byte: vertid
    2 byte: padding
    8

FACE:
    6 byte: uv indices
    2 byte: edgeid
    8

EDGE:
    4 byte: vertid * 2
    4 byte: faceid * 2 (left, then right of vert[0])
    2 byte: cw edge from vert[0]
    2 byte: ccw edge from vert[0]
    2 byte: cw edge from vert[1]
    2 byte: ccw edge from vert[1]
    16

MSH:
    HEADER
    'VERT'
    VERTS
    'UVUV'
    UV
    'FACE'
    FACES
    'EDGE'
    EDGES
    'BONE'
    BONES
"""

#
# SHARELIB
#

def float_to_ushort(val):
    if val >= 1.0:
        return 2**16-1
    if val <= 0.0:
        return 0
    return int(floor(val * (2**16-1)))

def float_to_short(val):
    if val >= 1.0:
        return 2**15-1
    if val <= -1.0:
        return -(2**15)+1
    return int(round(val * (2**15-1)))

def float_to_ubyte(val):
    if val >= 1.0:
        return 2**8-1
    if val <= 0.0:
        return 0
    return int(round(val * (2**8-1)))


class Vert(object):
    def __init__(self, bmv):
        self.bmv = bmv

    def __getattr__(self, name):
        return getattr(self.bmv, name)

    def serialize(self):
        rows = [[1, 0, 0, 0],
                [0, 0, 1, 0],
                [0,-1, 0, 0],
                [0, 0, 0, 1]]
        tmat = Matrix(rows)
        co = tmat * self.bmv.co
        normal = tmat * self.bmv.normal
        vpack = struct.pack("fffhhhHHBBBBBBBBH",
                        co.x,
                        co.y,
                        co.z,
                        float_to_short(normal.x),
                        float_to_short(normal.y),
                        float_to_short(normal.z),
                        0, 0, # padding
                        0, 0, 0, # vert color
                        0, # material id
                        0, 0, # bone ids
                        0, 0, # bone weights
                        self.bmv.link_edges[0].index)
        assert(len(vpack) == 32)
        return vpack

    
class Face(object):
    def __init__(self, bmf):
        self.bmf = bmf
        self.uvs = []

    def __getattr__(self, name):
        return getattr(self.bmf, name)

    def serialize(self):
        buf = []

        for i in range(0, 3):
            buf.append(struct.pack("H", self.uvs[i]))
        buf.append(struct.pack("H", self.bmf.edges[0].index))
        pack = b''.join(buf)
        assert(len(pack) == 8)
        return pack

    
class Edge(object):
    def __init__(self, bme):
        self.bme = bme

    def __getattr__(self, name):
        return getattr(self.bme, name)

    # vert_index, 0 or 1. first or second vert in edge
    def get_prevwingid(self, vert_index):
        loop = self.bme.link_loops[1] # its either one or the other
        if self.bme.verts[vert_index].index == self.bme.link_loops[0].vert.index:
            loop = self.bme.link_loops[0]
        return loop.link_loop_prev.edge.index

    def get_nextwingid(self, vert_index):
        loop = self.bme.link_loops[1] # its either one or the other
        if self.bme.verts[vert_index].index == self.bme.link_loops[0].vert.index:
            loop = self.bme.link_loops[0]
        return loop.link_loop_next.edge.index

    def get_vertid(self, vert_index):
        return self.bme.verts[vert_index].index

    def get_faceid(self, face_index):
        # TODO: check if this is ordered consistantly
        # I suspect bmesh makes no guarentee that faces[0] is left-wise (as i would expect)
        return self.bme.link_faces[face_index].index

    def serialize(self):
        epack = struct.pack("HHHHHHHH",
                            self.get_vertid(0),
                            self.get_vertid(1),
                            self.get_faceid(0),
                            self.get_faceid(1),
                            self.get_prevwingid(0),
                            self.get_nextwingid(0),
                            self.get_prevwingid(1),
                            self.get_nextwingid(1))
        assert(len(epack) == 16)
        return epack

    
class Uv(object):
    def __init__(self, uvx, uvy, vindex, color, material=0):
        self.uvx = float_to_ushort(uvx)
        self.uvy = float_to_ushort(uvy)
        self.vindex = vindex
        self.color = color
        self.material = material

    def __eq__(self, other):
        return self.uvx == other.uvx and self.uvy == other.uvy and self.vindex == other.vindex

    def __hash__(self):
        return self.vindex << 32 | self.uvx << 16 | self.uvy

    def __repr__(self):
        return "(Uv " + str(self.uvx) + ", " + str(self.uvy) + ", " + str(self.vindex) + ", " + str(self.color) + ")"

    def serialize(self):
        pack = struct.pack("HHHH",
                self.uvx, self.uvy, # uvs
                self.vindex, 0)
        assert(len(pack) == 8)
        return pack


class Mesh(object):
    def __init__(self, mesh, settings):
        mesh.update(calc_tessface=True)

        self.bm = bmesh.new()
        self.bm.from_mesh(mesh)
        bmesh.ops.triangulate(self.bm, faces=self.bm.faces)

        self.mesh = mesh
        self.settings = settings
        self.verts = []
        self.faces = []
        self.edges = []
        self.bones = []
        self.uvs = dict()

        self.uv_layer = self.bm.loops.layers.uv.verify()
        self.color_layer = self.bm.loops.layers.color.verify()

        for bmv in self.bm.verts:
            self.verts.append(Vert(bmv))

        for bmf in self.bm.faces:
            f = Face(bmf)

            # make set of uvs for each face
            for l in f.loops:
                uvx = l[self.uv_layer].uv.x
                uvy = l[self.uv_layer].uv.y
                color = l[self.color_layer]
                iuv = Uv(uvx, uvy, l.vert.index, color, f.material_index)
                if iuv not in self.uvs:
                    iuv.index = len(self.uvs)
                    self.uvs[iuv] = iuv
                f.uvs.append(self.uvs[iuv].index) # append UV id to face

            self.faces.append(f)

        for bme in self.bm.edges:
            self.edges.append(Edge(bme))

    def __getattr__(self, name):
        return getattr(self.bm, name)

    def serialize(self):
        buf = []
        buf.append(self.serialize_header())

        buf.append(self.serialize_label("VERT"))
        for v in self.verts:
            buf.append(v.serialize())

        buf.append(self.serialize_label("UVUV"))
        for uv in self.uvs.values():
            buf.append(uv.serialize())

        buf.append(self.serialize_label("FACE"))
        for f in self.faces:
            buf.append(f.serialize())

        buf.append(self.serialize_label("EDGE"))
        for e in self.edges:
            buf.append(e.serialize())

        buf.append(self.serialize_label("BONE"))
        # TODO bones

        return b''.join(buf)

    def serialize_label(self, label):
        fmt = "4s"
        pack = struct.pack(fmt, bytes(label, 'utf-8'))
        return pack

    def serialize_header(self):
        hfmt = "3sBHHHHHxx15sB"
        hpack = struct.pack(hfmt, b"MDL", 6,
                    len(self.verts),
                    len(self.uvs),
                    len(self.faces),
                    len(self.edges),
                    len(self.bones),
                    bytes(self.mesh.name, "UTF-8"), 0)
        assert(len(hpack) == 32)
        return hpack

def serialize_mesh(obj, settings):
    buf = []
    bpy.ops.object.mode_set(mode='OBJECT')
    print('serialize mesh...')
    mesh = Mesh(obj.data, settings)
    return mesh.serialize()


class MdlExport(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export.mdl"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Custom Model"

    # ExportHelper mixin class uses this
    filename_ext = ".msh"

    filter_glob = StringProperty(
            default="*.msh",
            options={'HIDDEN'})

    def execute(self, context):
        if not context.object.type == "MESH":
            raise Exception("Mesh must be selected, " + context.object.type + " was given")

        obj = context.object

        f = open(self.filepath, 'wb')
        obuf = serialize_mesh(obj, {})
        f.write(obuf)
        f.close()
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(MdlExport.bl_idname, text="Custom Model (.msh)")


def register():
    #bpy.utils.register_class(MdlExport)
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(MdlExport)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.export.mdl('INVOKE_DEFAULT')
