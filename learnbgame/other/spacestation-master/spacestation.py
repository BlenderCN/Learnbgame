from hy.core.language import range
import bpy
import math
import random
import numpy as np

def rng_int(seed, salt, x):
    random.seed(((seed + salt) % 1024))
    return random.randint(0, x)

def rng_float(seed, salt, a, b):
    random.seed(((seed + salt) % 1024))
    return random.uniform(a, b)
obj_prefix = 'SpaceStation_'

def clear_scene():
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.name.startswith('SpaceStation'):
            o.select = True
            _hy_anon_var_1 = o.select
        else:
            _hy_anon_var_1 = None
    return bpy.ops.object.delete(use_global=False)

def join_objects():
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.name.startswith(obj_prefix):
            o.select = True
            _hy_anon_var_2 = o.select
        else:
            _hy_anon_var_2 = None
    bpy.context.scene.objects.active = bpy.context.scene.objects['SpaceStation_Beam']
    bpy.context.scene.objects.active
    bpy.ops.object.join()
    bpy.context.object.name = 'SpaceStation'
    return bpy.context.object.name

def set_material():
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.material_slot_add()
    bpy.context.object.material_slots[0].material = bpy.data.materials['SpaceStation']
    return bpy.context.object.material_slots[0].material

def rename():
    bpy.context.object.name = (obj_prefix + bpy.context.object.name)
    return bpy.context.object.name

def beam(n):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=(1 + n), location=[0, 0, 0])
    bpy.context.object.name = 'SpaceStation_Beam'
    return bpy.context.object.name

def part_torus(seed, config, z):
    mrad = rng_float(seed, 1, config['torus_major_min'], config['torus_major_max'])
    zrot = rng_float(seed, 2, 0.0, 3.1415)
    bpy.ops.mesh.primitive_torus_add(major_radius=mrad, minor_radius=rng_float(seed, 3, config['torus_minor_min'], config['torus_minor_max']), location=[0, 0, z])
    rename()
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, vertices=8, depth=(mrad * 2), rotation=[0, 1.5708, zrot], location=[0, 0, z])
    rename()
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, vertices=8, depth=(mrad * 2), rotation=[1.5708, 0, zrot], location=[0, 0, z])
    return rename()

def part_bevelbox(seed, config, z):
    bpy.ops.mesh.primitive_cube_add(radius=rng_float(seed, 1, config['bevelbox_min'], config['bevelbox_max']), rotation=[0, 0, rng_float(seed, 2, 0.0, 3.1415)], location=[0, 0, z])
    rename()
    bpy.ops.object.modifier_add(type='BEVEL')
    return bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Bevel')

def part_cylinder(seed, config, z):
    bpy.ops.mesh.primitive_cylinder_add(radius=rng_float(seed, 1, config['cylinder_min'], config['cylinder_max']), depth=rng_float(seed, 2, config['cylinder_h_min'], config['cylinder_h_max']), location=[0, 0, z], vertices=16)
    rename()
    bpy.ops.object.modifier_add(type='BEVEL')
    return bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Bevel')

def part_storagering(seed, config, z):
    bpy.ops.mesh.primitive_cube_add(location=[1, 0, z])
    bpy.ops.transform.resize(value=[0.5, 0.5, rng_float(seed, 1, config['storage_min'], config['storage_max'])])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    rename()
    bpy.ops.object.modifier_add(type='BEVEL')
    bpy.context.object.modifiers['Bevel'].width = 0.3
    bpy.context.object.modifiers['Bevel'].width
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Bevel')
    bpy.ops.object.duplicate()
    rename()
    bpy.context.object.location = [(-1), 0, z]
    bpy.context.object.location
    bpy.ops.object.duplicate()
    rename()
    bpy.context.object.location = [0, 1, z]
    bpy.context.object.location
    bpy.ops.object.duplicate()
    rename()
    bpy.context.object.location = [0, (-1), z]
    bpy.context.object.location
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, vertices=8, depth=2, rotation=[0, 1.5708, 0], location=[0, 0, z])
    rename()
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, vertices=8, depth=2, rotation=[1.5708, 0, 0], location=[0, 0, z])
    return rename()

def generate_station(seed, config):
    n = (config['min_parts'] + rng_int(seed, 1, (config['max_parts'] - config['min_parts'])))
    print(n, 'parts.')
    beam(n)
    for i in range(n):
        part = rng_int(seed, i, 3)
        z = (i - (n / 2))
        print('Part', i, 'is', part)
        (part_torus((seed + i), config, z) if (part == 0) else (part_bevelbox((seed + i), config, z) if (part == 1) else (part_cylinder((seed + i), config, z) if (part == 2) else (part_storagering((seed + i), config, z) if (part == 3) else None))))
    join_objects()
    return (set_material() if (__name__ == '__main__') else None)
if (__name__ == '__main__'):
    clear_scene()
    conf = {'min_parts': 3, 'max_parts': 8, 'torus_major_min': 2.0, 'torus_major_max': 5.0, 'torus_minor_min': 0.1, 'torus_minor_max': 0.5, 'bevelbox_min': 0.2, 'bevelbox_max': 0.5, 'cylinder_min': 0.5, 'cylinder_max': 3.0, 'cylinder_h_min': 0.3, 'cylinder_h_max': 1.0, 'storage_min': 0.5, 'storage_max': 1.0, }
    _hy_anon_var_3 = generate_station(5, conf)
else:
    _hy_anon_var_3 = None
