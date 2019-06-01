
from . import import_audiocarver
import mathutils
import bmesh
import bpy
from math import *


def float_to_string(number):
    string = "%.3f" % number
    if string == "-0.000":
        string = "0.000"
    return string


def trace_bmesh(bmesh):
    print("")
    print("Vertices ...")
    print("")
    verts = bmesh.verts
    for vert in verts:
        print(vert.index, " (", float_to_string(vert.co.x), " ", float_to_string(vert.co.y), " ", float_to_string(vert.co.z), ")", sep='')

    print("")
    print("Edges ...")
    print("")
    edges = bmesh.edges
    for edge in edges:
        print(edge.verts[0].index, edge.verts[1].index, sep=', ')

    print("")
    print("Faces ...")
    print("")
    faces = bmesh.faces
    for face in faces:
        print(face.index, ".", sep='')
        face_verts = face.verts
        for face_vert in face_verts:
            print("  ", face_vert.index)


def audiocarver_test_01():
    # Create a bmesh from the note template object's mesh data.
    note_bmesh = bmesh.new()
    note_template_object = bpy.data.objects["Note.0"]
    note_mesh = note_template_object.data
    note_bmesh.from_mesh(note_mesh)

    # Do something with the note bmesh.
    trace_bmesh(note_bmesh)

    # Assign the bmesh back to the note template object's mesh data.
    note_bmesh.to_mesh(note_mesh)

    return {'FINISHED'}


def audiocarver_test_02():
    # Create a square 4-sided face.    
    square_bmesh = bmesh.new()
    verts = square_bmesh.verts
    verts.new((-1, -1, 0))
    verts.new((-1,  1, 0))
    verts.new(( 1,  1, 0))
    verts.new(( 1, -1, 0))
    square_bmesh_faces = square_bmesh.faces
    square_bmesh_faces.new(verts)
    square_bmesh.to_mesh(bpy.data.objects["Note.0"].data)


def audiocarver_test_03():
    # Create a test note.
    start_time = 0
    end_time = 10
    pitch = 60
    verts_per_second = 10
    verts_per_ring = 16
    radius = 0.025
    note_mesh = bmesh.new();
    note_verts = note_mesh.verts
    note_faces = note_mesh.faces
    x_increment = 1.0 / verts_per_second
    angle_increment = 2 * pi / verts_per_ring
    x1 = start_time
    while (x1 < end_time):
        x2 = x1 + x_increment
        angle = 0
        while (angle < (2 * pi)):
            y1 = sin(angle) * radius
            z1 = cos(angle) * radius
            angle_next = angle + angle_increment
            y2 = sin(angle_next) * radius
            z2 = cos(angle_next) * radius
            angle = angle_next
            v1 = note_verts.new((x1, y1, z1))
            v2 = note_verts.new((x2, y1, z1))
            v3 = note_verts.new((x2, y2, z2))
            v4 = note_verts.new((x1, y2, z2))
            note_faces.new((v1, v2, v3, v4))
        x1 = x2
    note_mesh.to_mesh(bpy.data.objects["Note.0"].data)


class AudioCarverTest(bpy.types.Operator):
    '''Run the AudioCarver test function.'''
    bl_idname = "object.test"
    bl_label = "AudioCarver Test"

    @classmethod
    def poll(cls, context):
        return True;

    def execute(self, context):
        audiocarver_test_03()
        return {'FINISHED'}
