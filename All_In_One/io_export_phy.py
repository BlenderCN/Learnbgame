bl_info = {
        "name": "PHY Physics Format",
        "author": "Brandon Surmanski",
        "blender": (2, 7, 3),
        "version": (0, 0, 1),
        "location": "File > Import-Export",
        "description": "Export custom physics format",
        "category": "Learnbgame",
}

"""
PHY file format

All transformations are relative to base object

HEADER:
    3 byte: magic number (PHY)
    1 byte: version (1)
    2 byte: number of collision spheres
    2 byte: number of collision capsule
    2 byte: number of collision boxes
    2 byte: padding
    4 byte: float, bounding sphere radius (implicitly centered relative to base object location)
    16 byte: name
    32

SPHERE:
    12 byte: position (3 * 4 byte float)
    4 byte: radius (float)
    16

CAPSULE:
    12 byte: position (3 * 4 byte float)
    4 byte: radius (float)
    4 byte: height (float)
    12 byte: rotation (3 * float, quaternion x,y,z; implicit w)
    32

BOX:
    12 byte: position (3 * 4 byte float)
    12 byte: (3 * 4 byte float; dimensions, x y z)
    12 byte: rotation (3 * float, quaternion x,y,z; implicit w)
    36
"""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import *
from math import *
import struct

if "bpy" in locals():
    import imp
    if "export_phy" in locals():
        imp.reload(export_phy)



class PhyExport(Operator, ExportHelper):
    bl_idname="export.phy"
    bl_label="Export Physics Info"
    filename_ext=".phy"
    filter_glob=StringProperty(
            default="*.phy",
            options={'HIDDEN'},
            )

    boundingRadius = 0
    spheres = []
    capsules = []
    boxes = []

    def write_phy_header(self, f, obj):
        hfmt = "3sBHHHxxf16s"
        pak = struct.pack(hfmt, b"PHY", 1,
                    len(self.spheres), len(self.capsules), len(self.boxes), self.boundingRadius,
                    obj.name.encode('UTF-8'))
        f.write(pak)

    def write_phy_spheres(self, f, obj):
        buf = []
        fmt = "3ff"
        for sphere in self.spheres:
            loc, radius = sphere # unpack tuple
            pak = struct.pack(fmt, loc[0], -loc[2], loc[1], radius)
            f.write(pak)

    def write_phy_capsules(self, f, obj):
        buf = []
        fmt = "3fff3f"
        for capsule in self.capsules:
            pass
            #TODO

    def write_phy_boxes(self, f, obj):
        buf = []
        fmt = "3f3f3f"
        for box in self.boxes:
            loc, dim, rot = box # unpack box tuple
            pak = struct.pack(fmt, loc[0], loc[2], -loc[1],
                    dim[0], dim[2], dim[1],
                    rot.x, rot.z, -rot.y)
            f.write(pak)

    def build_phy_lists(self, f, obj):
        parentLocation = obj.location
        for child in obj.children:
            relativeLocation = child.location - parentLocation
            childName = child.name.split('.')[0]
            if childName == 'sphere' or childName == 'ball':
                radius = max(child.dimensions[0], child.dimensions[1], child.dimensions[2])
                self.spheres.append([relativeLocation, radius])
                self.boundingRadius = max(relativeLocation.length + radius, self.boundingRadius)
            elif childName == 'capsule' or childName == 'pill':
                raise Exception("Capsule physics type not yet implemented")
                pass
            elif childName == 'box':
                self.boxes.append([relativeLocation, child.dimensions, child.rotation_euler.to_quaternion()])
                self.boundingRadius = max(relativeLocation.length + child.dimensions.length, self.boundingRadius)
        if len(self.spheres) == 0 and len(self.capsules) == 0 and len(self.boxes) == 0:
            loc = Vector()
            dim = Vector()
            # get location and dimension of bounding box
            for v in obj.bound_box:
                vert = Vector(v)
                loc += vert
                dim.x = max(dim.x, vert.x)
                dim.y = max(dim.y, vert.y)
                dim.z = max(dim.z, vert.z)
            loc /= 8.0
            dim -= loc
            dim *= 2

            self.boundingRadius = max(loc.length + dim.length, self.boundingRadius)
            self.boxes.append([loc, dim, Quaternion([0,0,0,1])])

    def execute(self, context):
        #if not context.object.type == 'MESH':
        #    raise Exception("Physics export only works for Mesh (for now). " + context.object.type + " was selected")
        f = open(self.filepath, 'wb')
        self.build_phy_lists(f, context.object)
        self.write_phy_header(f, context.object)
        self.write_phy_spheres(f, context.object)
        self.write_phy_capsules(f, context.object)
        self.write_phy_boxes(f, context.object)
        f.close()
        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(PhyExport.bl_idname, text="Custom Physics Object (.phy)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
