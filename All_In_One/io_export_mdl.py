bl_info = {
    "name":         "MDL File Format",
    "author":       "Brandon Surmanski",
    "blender":      (2,7,3),
    "version":      (0,0,1),
    "location":     "File > Import-Export",
    "description":  "Export custom MDL format",
    "category": "Learnbgame",
}

import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import *
from math import *
import struct

"""
MDL file format export

HEADER:
    3 byte: magic number (MDL)
    1 byte: version number (5)
    4 byte: number of verts
    4 byte: number of faces
    4 byte: number of edges
    1 byte: number of bones
    15 byte: name
    32

VERT:
    12 byte: position (3 * 4 byte float)
    6 byte: normal (3 * 2 byte signed short) (normalized from -32768 to 32767) #TODO implicit Z
    4 byte: uv coordinate (2 * 2 byte) (normalized from 0 to 65535)
    2 byte: material
    1 byte: boneID 1
    1 byte: boneID 2
    1 byte: bone weight 1
    1 byte: bone weight 2
    2 byte: incident edge id
    2 byte: padding         #TODO lighting properties
    32

FACE:
    6 byte: vertex indices
    2 byte: edge id
    8

EDGE:
    4 byte: vertexids * 2
    4 byte: faceids * 2
    4 byte: edgeids cw and ccw of vertex[0] * 2
    4 byte: edgeids cw and ccw of vertex[1] * 2
    16

MDL:
    HEADER,
    VERTS,
    FACES
"""

slicesUvs = True

#
# SHARELIB
#
def normalizeAll():
    for m in bpy.data.meshes:
        for v in m.vertices:
            sum = 0.0
            for i in range(0, 3):
                sum += v.co[i] * v.co[i]
            sum = sqrt(sum)
            for i in range(0, 3):
                v.co[i] = v.co[i] / sum

#sperically project onto plane z=1, produces x/y coords: {-1 <= x <= 1}
def planet_co_to_uv():
    sqrt2 = sqrt(2)
    sqrt3inv = 1/sqrt(3)
    for m in bpy.data.meshes:
        for v in m.vertices:
            ratio = 1 / v.co[2]
            for i in range(0, 3):
                v.co[i] = v.co[i] * (ratio)

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

def vec2_to_uhvec2(val):
    return tuple((float_to_ushort(val[0]), float_to_ushort(val[1])))

def vec3_to_hvec3(val):
    return tuple((float_to_short(val[0]), float_to_short(val[1]), float_to_short(val[2])))

def is_trimesh(mesh):
    for face in mesh.tessfaces:
        if len(face.vertices) > 3:
            return False
    return True

#
#
#

def uv_entry_tuple(mesh, facei, uvi, sliceUvs):
    face = mesh.tessfaces[facei]
    uv_raw = (0.0, 0.0)
    if mesh.tessface_uv_textures.active and sliceUvs:
        uvface = mesh.tessface_uv_textures.active.data[facei]
        uv_raw = (uvface.uv_raw[uvi * 2], uvface.uv_raw[uvi * 2 + 1])
    uv = vec2_to_uhvec2(uv_raw)
    entry = (face.vertices[uvi], uv[0], uv[1])
    return entry

def vert_list_entry_id(mesh, vert_list, entry):
    if(entry not in vert_list):
        vert_list.append(entry)
    return vert_list.index(entry)

def get_face_list(mesh, vert_list, sliceUvs):
    lst = list()
    for i in range(len(mesh.tessfaces)):
        faceverts = list()
        for j in range(3):
            entry = uv_entry_tuple(mesh, i, j, sliceUvs)
            faceverts.append(vert_list_entry_id(mesh, vert_list, entry))
        lst.append(faceverts)
    return lst

def bone_weight_normalize(bones):
    BONEW1 = 2; BONEW2 = 3
    b_sum = bones[BONEW1] + bones[BONEW2]
    if b_sum > 0:
        bones[BONEW1] = float_to_ubyte(bones[BONEW1] / b_sum)
        bones[BONEW2] = float_to_ubyte(bones[BONEW2] / b_sum)
    else:
        bones[BONEW1] = 0
        bones[BONEW2] = 0
    return bones

def bone_id_of_group(obj, groupid, blist):
    BONE = 3
    nm = obj.vertex_groups[groupid].name
    for i in range(0, len(blist)):
        if(nm == blist[i][BONE].name):
            print(nm + " is group " + str(i));
            return i
    return None

def vert_get_bones(obj, vert, blist):
    boneid = [255, 255]
    bonew = [0.0, 0.0]
    for group in vert.groups:
        g_boneid = bone_id_of_group(obj, group.group, blist)
        if g_boneid != None:
            if group.weight > bonew[0]:
                bonew[1] = bonew[0]
                boneid[1] = boneid[0]
                bonew[0] = group.weight
                boneid[0] = g_boneid
            elif group.weight > bonew[1]:
                bonew[1] = group.weight
                boneid[1] = g_boneid
    return bone_weight_normalize([boneid[0], boneid[1], bonew[0], bonew[1]])

def find_bone_parentid(arm, bone):
    if(bone.parent):
        for i in range(len(arm.data.bones)):
            if(arm.data.bones[i] == bone.parent):
                return i
    return 255

def get_bone_list(obj):
    armature = obj.find_armature()
    blist = []
    if(armature):
        for i in range(0, len(armature.data.bones)):
            bone = armature.data.bones[i]
            pid = find_bone_parentid(armature, bone)
            blist.append([bone.name, i, pid, bone])
    return blist

def write_mdl_header(buf, obj, vlist, flist, blist):
    hfmt = "3sBIIIB15s"

    header = struct.pack(hfmt, b"MDL", 5,
                len(vlist),
                len(flist),
                0, # number of edges (unimpl)
                len(blist),#number of bones
                bytes(obj.data.name, "UTF-8"))
    assert(len(header) == 32)
    buf.append(header)

def write_mdl_verts(buf, obj, vlist, blist):
    rows = [[1, 0, 0, 0],
            [0, 0, 1, 0],
            [0,-1, 0, 0],
            [0, 0, 0, 1]]
    tmat = Matrix(rows)#Matrix.Rotation(-pi/2.0, 3, Vector((1,0,0))) #turns verts right side up (+y)
    VERTID = 0; UV1 = 1; UV2 = 2
    BONEID1 = 0; BONEID2 = 1; BONEW1 = 2; BONEW2 = 3
    vfmt = "fffhhhHHHBBBBHxx"
    for vert in vlist:
        co = tmat * obj.data.vertices[vert[VERTID]].co
        norm = vec3_to_hvec3(tmat * obj.data.vertices[vert[VERTID]].normal)
        uv = tuple((vert[UV1], vert[UV2]))
        bones = vert_get_bones(obj, obj.data.vertices[vert[VERTID]], blist)

        vbits = struct.pack(vfmt, co[0], co[1], co[2],
                            norm[0], norm[1], norm[2],
                            uv[0], uv[1],
                            0, #material ID (unimpl)
                            bones[BONEID1], bones[BONEID2], #bone IDs
                            bones[BONEW1], bones[BONEW2], #bone weights
                            0) # incident edge (unimpl)
        buf.append(vbits)

def write_mdl_faces(buf, mesh, flist):
        ffmt = 'HHHH'
        for face in flist:
            fbits = struct.pack(ffmt, face[0], face[1], face[2], 0) # last is incident edge (unimpl)
            buf.append(fbits)

def write_mdl_edges(buf, mesh, elist):
    pass

def write_mdl_mesh(obj, settings):
    buf = []
    mesh = obj.data
    mesh.update(calc_tessface=True)
    if not is_trimesh(mesh):
        raise Exception ("Mesh is not triangulated")

    vlist = list()
    flist = get_face_list(mesh, vlist, settings['sliceUvs']) #modifies vlist (i know... bad)
    blist = get_bone_list(obj)

    write_mdl_header(buf, obj, vlist, flist, blist)
    write_mdl_verts(buf, obj, vlist, blist)
    write_mdl_faces(buf, mesh, flist)
    return b''.join(buf)


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class MdlExport(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export.mdl"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Custom Model"

    # ExportHelper mixin class uses this
    filename_ext = ".mdl"

    filter_glob = StringProperty(
            default="*.mdl",
            options={'HIDDEN'},
            )

    sliceUvs = BoolProperty(
            name="Slice UV mapping",
            description="If true, vertices will be split so there "
                        "is one vertex entry per unique UV", 
            default=True,)

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    """
    use_setting = BoolProperty(
           name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )
    """

    def execute(self, context):
        if not context.object.type == "MESH":
            raise Exception("Mesh must be selected, " + context.object.type + " was given")

        obj = context.object

        f = open(self.filepath, 'wb')
        obuf = write_mdl_mesh(obj, {'sliceUvs': self.sliceUvs})
        f.write(obuf)
        f.close()
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(MdlExport.bl_idname, text="Custom Model (.mdl)")


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
