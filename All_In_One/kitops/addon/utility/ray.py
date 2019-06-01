import bpy

from mathutils import *

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

    ray_origin = matrix.inverted() * view3d.mouse_origin(op)
    ray_target = matrix.inverted() * (view3d.mouse_origin(op) + view3d.mouse_vector(op))
    ray_direction = ray_target - ray_origin

    try:
        success, location, normal, face_index = op.duplicate.ray_cast(ray_origin, ray_direction)

        location = op.duplicate.matrix_world * location
        normal = op.duplicate.matrix_world.to_3x3() * normal
    except: pass

def make_duplicate(op, object):
    data = object.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
    op.duplicate = bpy.data.objects.new('KIT OPS Duplicate', data)
    op.duplicate.kitops.duplicate = True
    op.duplicate.draw_type = 'BOUNDS'
    op.duplicate.matrix_world = object.matrix_world

    bpy.context.scene.objects.link(op.duplicate)
    bpy.context.scene.update()

    bpy.context.scene.objects.active = op.duplicate
