bl_info = {
    "name":         "SCN File Format",
    "author":       "Brandon Surmanski",
    "blender":      (2,7,3),
    "version":      (0,0,2),
    "location":     "File > Import-Export",
    "description":  "Export custom SCN format",
    "category":     "Import-Export"
}

import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import *
from math import *
import struct

"""
SCN file format export
Requirements:
    pack various datatypes
    specify transformations of entities

HEADER:
    3 byte: magic number (SCN)
    1 byte: version number (2)
    2 byte: # entities
    10 byte: padding
    16 byte: name
    32

ENT:
    2 byte: parent id (zero indexed, if top bit is '1', no parent)
    6 byte: padding
    12 byte: position
    12 byte: scale
    16 byte: quaternion rotation
    16 byte: name (trimmed blender object name)
    64


SCN:
    HEADER,
    ENT
"""

def write_scn_header(buf, scene):
    hfmt = "3sBH10x16s"
    header = struct.pack(hfmt,
                         b"SCN",
                         1,
                         len(scene.objects), # count objects in scene
                         bytes(scene.name, "UTF-8"))
    buf.append(header)

def write_scn_ent(buf, obj):
    fmt = "H6x3f3f4f16s"
    tmat = Matrix([[ 1, 0, 0, 0],
                   [ 0, 0, 1, 0],
                   [ 0,-1, 0, 0],
                   [ 0, 0, 0, 1]])
    pos = tmat * obj.location
    rot = obj.rotation_euler.to_quaternion() #needs to be rotated; done below
    eheader = struct.pack(fmt,
                          0,
                          pos.x, pos.y, pos.z,
                          obj.scale[1], obj.scale[2], obj.scale[0],
                          rot.x, rot.z, -rot.y, rot.w,
                          bytes(obj.name.split('.')[0], "UTF-8")) # splitting name to remove .001 qualifier
    buf.append(eheader)

def write_scn_ents(buf, scene):
    objs = []
    for obj in scene.objects: # build list of roots
        if not obj.parent:
            objs.append(obj)

    cnt = 0
    for obj in objs:
        cnt = write_scn_ent(buf, obj)


def write_scn_data(buf, scene):
    write_scn_ents(buf, scene)

def write_scn_scene(context, settings):
    buf = []
    write_scn_header(buf, context.scene)
    write_scn_data(buf, context.scene)

    return b''.join(buf)


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ScnExport(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export.scn"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Custom Scene"

    # ExportHelper mixin class uses this
    filename_ext = ".scn"

    filter_glob = StringProperty(
            default="*.scn",
            options={'HIDDEN'},
            )

    def execute(self, context):
        f = open(self.filepath, 'wb')
        obuf = write_scn_scene(context, None)
        f.write(obuf)
        f.close()

        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ScnExport.bl_idname, text="Custom Scene (.scn)")


def register():
    bpy.utils.register_class(ScnExport)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ScnExport)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.export.scn('INVOKE_DEFAULT')
