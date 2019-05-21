import numpy as np
import bpy, bmesh
from ase.io.cube import read_cube_data
from ase.io import read
import ase.neighborlist
import ase.data
from tassem_xyz.atomic_radii import *
import time
from distutils.version import LooseVersion, StrictVersion


def draw_atoms(atoms):
    cnt = 0
    start_total = time.time()
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0,0,0),segments = 16 ,ring_count = 16)
    bpy.ops.object.shade_smooth()
    sphere = bpy.context.object
    sphere.name = 'ref_sphere'
    for atom in atoms:
        start = time.time()
        ob = sphere.copy()
        ob.data = sphere.data.copy()
        ob.location = atom.position
        bpy.context.scene.objects.link(ob) 
        end = time.time()
        duration_addsphere = end - start
        start = time.time()
        bpy.context.scene.objects[0].name = 'Atom%05d' % cnt
        bpy.context.scene.objects[0].scale = (atomic_properties[atom.number-1][4]/2,)*3
        bpy.data.groups[atom.symbol].objects.link(bpy.context.scene.objects[0])
        bpy.context.scene.objects[0].data.materials.append(bpy.data.materials[atom.symbol])
        end = time.time()
        duration_rest = end - start
        cnt += 1
    bpy.context.scene.update()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['ref_sphere'].select = True
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')
    return None

def draw_bonds(atoms):
    nl = ase.neighborlist.NeighborList([atomic_properties[atomic_number-1][4]-0.2   for atomic_number in atoms.numbers], self_interaction = False)
    if LooseVersion(ase.__version__) > LooseVersion('3.15'):
        nl.update(atoms)
    else:
        nl.build(atoms)
    bpy.ops.object.select_all(action='DESELECT')
    try:
        bpy.ops.group.create(name='bonds')
    except:
        None
    bpy.ops.mesh.primitive_cylinder_add(vertices=8) 
    bpy.ops.object.shade_smooth()
    bond = bpy.context.object
    bond.name = 'ref_bond'
    cnt = 0
    for atom in atoms:
        if nl.get_neighbors(atom.index)[0].size > 0:
            for neighbor in nl.get_neighbors(atom.index)[0]:
                displacement = atoms.positions[neighbor] - atom.position 
                location = atom.position + (displacement / 2.)
                distance = atoms.get_distance(atom.index,neighbor)
                ob = bond.copy()
                ob.data = bond.data.copy()
                bpy.context.scene.objects.link(ob) 
                ob.name = 'Bond%05d' % cnt
                ob.location = location
                ob.scale = (1,1,1)
                ob.dimensions = (0.1,0.1,distance)
                phi = np.arctan2(displacement[1], displacement[0]) 
                theta = np.arccos(displacement[2] / distance) 
                ob.rotation_euler[1] = theta
                ob.rotation_euler[2] = phi
                bpy.data.groups['bonds'].objects.link(ob)
                cnt += 1
    bpy.context.scene.update()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['ref_bond'].select = True
    bpy.ops.object.delete()
    bpy.ops.object.select_all(action='DESELECT')
    return None

def group_atoms(atoms):
    atom_types = set(atoms.get_chemical_symbols())
    bpy.ops.object.select_all(action='DESELECT')
    for atom_type in atom_types:
        try:
            bpy.ops.group.create(name=atom_type)
        except:
            None
    return None
    
def setup_materials(atoms):
    atom_types = set(atoms.get_chemical_symbols())
    for atom_type in atom_types:
        try:
            bpy.data.materials.new(name = atom_type)
            bpy.data.materials[atom_type].diffuse_color = atomic_properties[ase.data.atomic_numbers[atom_type]-1][3]
        except:
            None
    return None 

def draw_cube_now(fcube):
    start = time.time()
    cube_in = read(fcube)
    end = time.time()
    duration = end - start
    print('Reading time: %10.5fs' % duration) 

  
    start = time.time()
    setup_materials(cube_in)
    end = time.time()
    duration = end - start
    print('Materials setup: %10.5fs' % duration) 


    start = time.time()
    group_atoms(cube_in)
    end = time.time()
    duration = end - start
    print('Grouping setup: %10.5fs' % duration) 

    start = time.time()
    draw_atoms(cube_in)
    end = time.time()
    duration = end - start
    print('Drawing Atoms: %10.5fs' % duration) 

    start = time.time()
    draw_bonds(cube_in)
    end = time.time()
    duration = end - start
    print('Drawing Bonds: %10.5fs' % duration) 
    return None
        
