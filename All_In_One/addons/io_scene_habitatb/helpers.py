# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import mathutils
import math
import struct
import bpy
import bmesh

scale = 10.0

def get_distance(v1, v2):
    return math.sqrt(pow(v1.x - v2.x, 2) + pow(v1.y - v2.y, 2) + pow(v1.z - v2.z, 2))

def get_texture(filename, number):
    pass

# you give texture name, it give integer, xaxaxa
def texture_to_int(string):
    num = ord(string[-5])-97

    if num > 9 or num < -1:
        return -1
    else:
        return num

def get_face_material(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0 or any([face[layer] != selected_faces[0][layer] for face in selected_faces]):
        return -1
    else:
        return selected_faces[0][layer]

def set_face_material(self, value):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("revolt_material") or bm.faces.layers.int.new("revolt_material")
    for face in bm.faces:
        if face.select:
            face[layer] = value

def get_face_texture(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("texture") or bm.faces.layers.int.new("texture")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0 or any([face[layer] != selected_faces[0][layer] for face in selected_faces]):
        return -1
    else:
        return selected_faces[0][layer]

def set_face_texture(self, value):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("texture") or bm.faces.layers.int.new("texture")
    for face in bm.faces:
        if face.select:
            face[layer] = value

def get_face_property(self):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("flags") or bm.faces.layers.int.new("flags")
    selected_faces = [face for face in bm.faces if face.select]
    if len(selected_faces) == 0:
        return 0
    output = selected_faces[0][layer]
    for face in selected_faces:
        output = output & face[layer]
    return output

def is_face_prop(self, face, prop):
    return face["flags"] & prop

def set_face_property(self, value, mask):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.faces.layers.int.get("flags") or bm.faces.layers.int.new("flags")
    for face in bm.faces:
        if face.select:
            face[layer] = face[layer] | mask if value else face[layer] & ~mask

def get_flag_long(self, start):
    return struct.unpack("=l", bytes(self.flags[start:start + 4]))[0]

def set_flag_long(self, value, start):
    for i,b in enumerate(struct.pack("=l", value), start):
        self.flags[i] = b

def get_intersection(d1, n1, d2, n2, d3, n3):
    den = n1.dot(n1.cross(n3))
    if abs(den) < 1e-100:
        return None # no intersection
    return (d1 * n1.cross(n3) + d2 * n3.cross(n1) + d3 * n1.cross(n1)) / den

def to_blender_scale(val):
    return val / scale

def to_blender_axis(val):
    return (val[0], val[2], -val[1])

# deprecated, could be useful again in the future, though
# def vc_to_bitfield(color_layer):
#     flags_b0 = int(color_layer[0] * 255.0)
#     flags_b1 = int(color_layer[2] * 255.0)
#     flags_ba = bytearray([flags_b0, flags_b1])
#     flags_int = int.from_bytes(flags_ba, byteorder='little', signed=False)
#     return flags_int

# def bitfield_to_vc(number):
#     flags_bytes = number.to_bytes(2, byteorder='little', signed=False)
#     flagR = float(flags_bytes[0]) / 255.0
#     flagB = float(flags_bytes[1]) / 255.0
#     return mathutils.Color((flagR, 1.0, flagB))

def redraw():
    # bpy.ops.wm.redraw_timer(type="DRAW", iterations=1) does not work
    bpy.context.area.tag_redraw()

# BUTTON FUNCTIONS\

def select_faces(context, prop):
    bm = bmesh.from_edit_mesh(context.object.data)
    flag_layer = bm.faces.layers.int.get("flags") or bm.faces.layers.int.new("flags")

    for face in bm.faces:
        if face[flag_layer] & prop:
            face.select = not face.select
    redraw()   

def set_vertex_color(context, number):
    print(context, number)
    bm = bmesh.from_edit_mesh(context.object.data)        
    verts = [ v for v in bm.verts if v.select ]
    if verts:
        colors = bm.loops.layers.color.get("color")   
        for v in verts:
            for loop in v.link_loops:
                loop[colors] = mathutils.Color((number/100, number/100, number/100))
                
        bmesh.update_edit_mesh(context.object.data)

def set_all_w(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.rv_type = "WORLD"
def set_all_prm(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.rv_type = "MESH"
def set_all_ncp(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.rv_type = "NCP"

def set_all_add_w(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.export_as_w = True
def set_all_add_ncp(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.export_as_ncp = True

def unset_all_add_w(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.export_as_w = False
def unset_all_add_ncp(context):
    for obj in bpy.context.selected_objects:
        obj.revolt.export_as_ncp = False

def create_color_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("color")

def create_alpha_layer(context):
    obj = context.object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.loops.layers.color.new("alpha")