bl_info = {
    "name": "MAP 220 Geometry Import",
    "author": "nemyax",
    "version": (0, 1, 20190211),
    "blender": (2, 7, 7),
    "location": "File > Import-Export",
    "description": "Import Half-Life map editor brushes as scene geometry",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import bmesh
import math
import mathutils as mu
import re
from bpy.props import (
    StringProperty,
    EnumProperty)
from bpy_extras.io_utils import (
    ImportHelper,
    path_reference_mode)

class Plane(object):
    def __init__(self, xyz1, xyz2, xyz3, uv1, uv2, uv3, tx):
        self.xyz1 = xyz1
        self.xyz2 = xyz2
        self.xyz3 = xyz3
        self.uv1  = uv1
        self.uv2  = uv2
        self.uv3  = uv3
        self.tx   = tx

class Brush(object):
    def __init__(self):
        self.planes = []
    def add_plane(self, plane):
        self.planes.append(plane)
    def submit_to_bmesh(self, bm):
        vs = []
        for p in self.planes:
            v1 = bm.verts.new(p.xyz1)
            v2 = bm.verts.new(p.xyz2)
            v3 = bm.verts.new(p.xyz3)
            vs.extend([v1,v2,v3])
        bmesh.ops.convex_hull(bm, input=vs)
        bmesh.ops.remove_doubles(bm, verts=vs, dist=0.001)        

def do_import(path):
    brushes = read_map(path)
    make_obj(brushes)

def read_map(path):
    fh = open(path, mode="r")
    map_data = fh.readlines()
    brushes = []
    fh.close()
    plane_pattern = \
        "\(\s+(.+?)\s+(.+?)\s+(.+?)\s+\)\s+" * 3 + \
        "(.+?)\s+" + \
        "\[\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+\]\s+" * 2 + \
        "(.+?)\s+(.+?)\s+(.+?)"
    br_opened = re.compile("{")
    br_closed = re.compile("}")
    plane_re  = re.compile(plane_pattern)
    while map_data:
        planes = []
        if skip_until_noguard(br_opened, map_data):
            map_data.pop(0)
            planes.extend(gather(plane_re, br_closed, map_data))
        if len(planes) > 3:
            bo = Brush()
            for p in planes:
                coords = [float(a) for a in p[0:9]]
                po = Plane(
                    mu.Vector(coords[0:3]),
                    mu.Vector(coords[3:6]),
                    mu.Vector(coords[6:9]),
                    (0.0,0.0),
                    (0.0,0.0),
                    (0.0,0.0),
                    p[9])
                bo.add_plane(po)
            brushes.append(bo)
    return brushes

def make_obj(brushes):
    bm = bmesh.new()
    for b in brushes:
        b.submit_to_bmesh(bm)
    mesh = bpy.data.meshes.new("map_mesh")
    obj = bpy.data.objects.new("map", mesh)
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.scene.objects.link(obj)

### Regex utilities

def skip_until_noguard(regex, ls):
    while ls:
        l = ls[0]
        if regex.match(l):
            return True
        ls.pop(0)

def gather(regex, end_regex, ls):
    result = []
    while ls:
        l = ls.pop(0)
        if end_regex.match(l):
            break
        m = regex.match(l)
        if m:
            result.append(m.groups())
    return result

### Boilerplate

class ImportMap220(bpy.types.Operator, ImportHelper):
    '''Load a Half-Life map source file as a mesh'''
    bl_idname = "import_scene.map220"
    bl_label = 'Import MAP'
    bl_options = {'PRESET'}
    filename_ext = ".map"
    filter_glob = StringProperty(
            default="*.map",
            options={'HIDDEN'})
    path_mode = path_reference_mode
    check_extension = True
    def execute(self, context):
        do_import(self.filepath)
        return {'FINISHED'}

def menu_func_import_mesh(self, context):
    self.layout.operator(
        ImportMap220.bl_idname, text="MAP 220 Brushes (.map)")

def register():
    bpy.utils.register_class(ImportMap220)
    bpy.types.INFO_MT_file_import.append(menu_func_import_mesh)

def unregister():
    bpy.utils.unregister_class(ImportMap220)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_mesh)

if __name__ == "__main__":
    register()

