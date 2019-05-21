bl_info = {
    "name": "Tomb Raider .SAT file importer",
    "author": "Israel Jacquez",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import .SAT file",
    "warning": "",
    "wiki_url": "https://github.com/ijacquez/trsat",
    "tracker_url": "https://github.com/ijacquez/trsat/issues",
    "category": "Import-Export"
}

import re
import os
import imp
import math
import struct

import bpy
import bmesh

from mathutils import *
from bpy_extras import io_utils
from bpy.app.handlers import persistent
from bpy.props import StringProperty, BoolProperty

ST_SOLID_RECTANGLE = 0x25
ST_SOLID_TRIANGLE = 0x24
ST_SPRITE = 0x27
ST_TRANSPARENT_RECTANGLE = 0x21
ST_INVISIBLE_RECTANGLE = 0x23
ST_INVISIBLE_TRIANGLE = 0x22

SCALE = 1/256.0

class Header(object):
    def __init__(self, header_data):
        if not isinstance(header_data, tuple):
            raise TypeError("?")
        self.ascii_string_1 = header_data[0]
        self.x = header_data[1] * SCALE
        self.z = header_data[2] * SCALE
        self.y_bottom = header_data[3]
        self.y_top = header_data[4]
        self.ascii_string_2 = header_data[5]
        self.reserved_1 = header_data[6]
        self.door_data_size = header_data[7] * 2
        self.vertex_count = header_data[8]
        self.vertices = header_data[9:9 + self.vertex_count]
        self.surface_count = header_data[9 + self.vertex_count]
        self.surface_type_count = header_data[10 + self.vertex_count]
        self.surfaces = header_data[11 + self.vertex_count:11 + self.vertex_count + self.surface_count]

class Vertex(object):
    def __init__(self, vertex_data):
        if not isinstance(vertex_data, tuple):
            raise TypeError("?")
        self.x = vertex_data[0] * SCALE
        self.y = vertex_data[1] * SCALE
        self.z = vertex_data[2] * SCALE
        self.color = vertex_data[3]

    def __str__(self):
        return "(%i,%i,%i,0x%04X)" % (self.x, self.y, self.z, self.color)

class Rectangle(object):
    def __init__(self, rectangle_data):
        if not isinstance(rectangle_data, tuple):
            raise TypeError("?")
        # Why shift by 4 if each vertex is 8 bytes?
        self.vertices = [(p >> 4) for p in rectangle_data[0:4]]
        self.texture = rectangle_data[4]

    def __str__(self):
        return "(%i,%i,%i,%i,0x%04X)" % (self.vertices[0],
                                         self.vertices[1],
                                         self.vertices[2],
                                         self.vertices[3],
                                         self.texture)

class Triangle(object):
    def __init__(self, triangle_data):
        if not isinstance(triangle_data, tuple):
            raise TypeError("?")
        # Why shift by 4 if each vertex is 8 bytes?
        self.vertices = [(p >> 4) for p in triangle_data[0:3]]
        self.texture = triangle_data[3]

    def __str__(self):
        return "(%i,%i,%i,0x%04X)" % (self.vertices[0],
                                      self.vertices[1],
                                      self.vertices[2],
                                      self.texture)

class SurfaceType(object):
    def __init__(self, surface_type_data):
        if not isinstance(surface_type_data, tuple):
            raise TypeError("?")
        self.id = surface_type_data[0]
        self.surface_count = surface_type_data[1]
        self.surfaces = surface_type_data[2:2 + self.surface_count]

    def __str__(self):
        return ""

def create_mesh(offset, fp):
    fp.seek(offset, 0)
    header_data = ()
    header_data += struct.unpack('>8s' + # ASCII string
                                 'i' +   # X-offset of room
                                 'i' +   # Z-offset of room
                                 'i' +   # Y-offset of room's floor
                                 'i' +   # Y-offset of room's ceiling
                                 '8s' +  # ASCII string
                                 'i' +   # Integer that's always 0x00000002
                                 'i' +   # Number of bytes to "DOORDATA" divided by 2
                                 'H',    # Number of vertices
                                 fp.read(42))
    vertices = []
    for vertex_id in range(header_data[8]):
        vertex_data = struct.unpack('>h' + # X-offset of vertex (local coordinates)
                                    'h' +  # Y-offset of vertex (local coordinates)
                                    'h' +  # Z-offset of vertex (local coordinates)
                                    'H',   # 16-bit BGR
                                    fp.read(8))
        vertex = Vertex(vertex_data)
        vertices.append(vertex)
    header_data += tuple(vertices)

    header_data += struct.unpack('>H' + # Total number of surfaces in the room
                                 'H',   # Total number of surface types
                                 fp.read(4))
    surfaces = []
    for surface_type_id in range(header_data[10 + header_data[8]]):
        surface_type_data = struct.unpack('>H' + # Type of surface type
                                          'H',   # Number of surfaces of this type
                                          fp.read(4))
        for surface_idx in range(surface_type_data[1]):
            surface = None
            if (surface_type_data[0] == ST_TRANSPARENT_RECTANGLE):
                surface_data = struct.unpack('>HHHH' + # Indices in the vertex list
                                             'H',      # Texture index
                                             fp.read(10))
                surface = Rectangle(surface_data)
            elif (surface_type_data[0] == ST_INVISIBLE_TRIANGLE):
                pass
            elif (surface_type_data[0] == ST_INVISIBLE_RECTANGLE):
                pass
            elif (surface_type_data[0] == ST_SOLID_TRIANGLE):
                surface_data = struct.unpack('>HHH' + # Indices in the vertex list
                                             'H',     # Texture index
                                             fp.read(8))
                surface = Triangle(surface_data)
            elif (surface_type_data[0] == ST_SOLID_RECTANGLE):
                surface_data = struct.unpack('>HHHH' + # Indices in the vertex list
                                             'H',      # Texture index
                                             fp.read(10))
                surface = Rectangle(surface_data)
            elif (surface_type_data[0] == ST_SPRITE):
                pass
            if surface is not None:
                surfaces.append(surface)
    header_data += tuple(surfaces)

    header = Header(header_data)
    print("0x%04X" % (offset))
    print("vertex count: ", header.vertex_count)
    print("surface count: ", header.surface_count)
    print("surface type count: ", header.surface_type_count)
    print("len(surfaces): ", len(header.surfaces))

    name = "o_0x%04X" % (offset)
    me = bpy.data.meshes.new(name + '_mesh')
    new_bmesh = bmesh.new()

    rotate_axis = lambda angle, axis: Matrix.Rotation(math.radians(angle), 4, axis).decompose()[1]

    rot_y = rotate_axis(180.0, 'Y')
    rot_x = rotate_axis(90.0, 'X')

    for vertex in header.vertices:
        v = Vector((vertex.x, vertex.y, vertex.z))
        pv = (rot_y * rot_x) * v
        new_bmesh.verts.new(pv[:])
    new_bmesh.verts.index_update()
    new_bmesh.verts.ensure_lookup_table()
    for surface in header.surfaces:
        indices = [new_bmesh.verts[i] for i in surface.vertices]
        new_bmesh.faces.new(indices)
    new_bmesh.to_mesh(me)
    new_bmesh.free()

    ob = bpy.data.objects.new(name, me)

    loc = (rot_y * rot_x) * Vector((header.x, 0.0, header.z))

    ob.location = loc[:]
    ob.show_name = True

    # Link object to scene and make active
    scene = bpy.context.scene
    scene.objects.link(ob)
    scene.objects.active = ob

    ob.select = True

class ImportTombRaiderSAT(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = "import_scene.tomb_raider_sat_file"
    bl_label = "Import Tomb Raider (.SAT)"
    bl_description = "Import Tomb Raider (.SAT) file"
    bl_options = {'REGISTER', 'UNDO'}

    use_filter = BoolProperty(default = True, options = {'HIDDEN'})

    # use filter to show only the SAT files in a directory
    filename_ext = ".sat"
    filter_glob = StringProperty(default = "*.sat", options = {'HIDDEN'})

    def execute(self, context):
        try:
            base_path = os.path.dirname(self.filepath)

            # Ugly, remove... this finds all the MESHPOS
            offsets = []
            first_offset = 0
            with open(self.filepath, mode = 'rb') as fp:
                data = fp.read()
                while data != []:
                    try:
                        offset = data.index(str.encode('MESHPOS '))
                        real_offset = offset + first_offset
                        offsets.append(real_offset)
                        print("==> 0x%04X" % (real_offset))
                        first_offset += offset + 8
                        data = data[offset + 8:]
                    except:
                        break

            with open(self.filepath, mode = 'rb') as fp:
                for offset in offsets:
                    create_mesh(offset, fp)
            return {'FINISHED'}
        except (ValueError, RuntimeError) as e:
            self.report({'ERROR'}, "%s" % (e))
            return {'CANCELLED'}
        return {'FINISHED'}

def menu_import_tomb_raider_sat(self, context):
    self.layout.operator(ImportTombRaiderSAT.bl_idname, text = ImportTombRaiderSAT.bl_label)

def register():
    bpy.utils.register_class(ImportTombRaiderSAT)
    bpy.types.INFO_MT_file_import.append(menu_import_tomb_raider_sat)

def unregister():
    bpy.utils.unregister_class(ImportTombRaiderSAT)
    bpy.types.INFO_MT_file_import.remove(menu_import_tomb_raider_sat)

if __name__ == '__main__':
    register()
