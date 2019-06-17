import bpy
import bmesh

from mathutils import *
from mathutils.bvhtree import BVHTree as BVH

from . import view3d

success = bool()
location = Vector()
normal = Vector()
face_index = int()


def cast(op):
    global success
    global location
    global normal
    global face_index

    matrix = op.duplicate.matrix_world.copy()

    ray_origin = matrix.inverted() @ view3d.mouse_origin(op)
    ray_direction = matrix.inverted().to_3x3() @ view3d.mouse_vector(op)

    bm = bmesh.new()
    bm.from_mesh(op.duplicate.data)

    bvh = BVH.FromBMesh(bm)

    location, normal, face_index, distance = bvh.ray_cast(ray_origin, ray_direction)

    success = location != None

    if success:
        location = op.duplicate.matrix_world @ location
        normal = op.duplicate.matrix_world.to_3x3() @ normal

    # bm.free()


def make_duplicate(op, obj):
    data = obj.to_mesh(bpy.context.depsgraph, apply_modifiers=True)
    op.duplicate = bpy.data.objects.new('KIT OPS Duplicate', data)
    op.duplicate.kitops.duplicate = True
    op.duplicate.display_type = 'BOUNDS'
    op.duplicate.matrix_world = obj.matrix_world

    bpy.data.collections['INSERTS'].objects.link(op.duplicate)

    bpy.context.view_layer.objects.active = op.duplicate
