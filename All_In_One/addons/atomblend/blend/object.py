# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   blend/object.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# Blender API wrapper for object and mesh operations.
# =============================================================================

import bpy
import os
import numpy as np

from . import space

# === Object creation ===
def icosphere_add(name, size=1, origin=(0, 0, 0), smooth=True):
    """Create icosphere primitive"""
    bpy.ops.mesh.primitive_ico_sphere_add(size=size, location=origin)
    obj = bpy.context.object
    obj.name = name
    obj.show_name = True
    mesh = obj.data
    mesh.name = name+"_mesh"
    if smooth:
        bpy.ops.object.shade_smooth()
    return obj

def cube_add_from_verts(name, origin, verts):
    """Create cube with faces defined from input vertices

    verts: arraylike, must define vertices in clockwise order
           starting from bottom face -x, -y, -z point
    """
    # Verts must be defined: bottom face first clockwise, top face clockwise
    # starting from (-x, -y, -z)
    faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
    edges = []

    mesh = mesh_add_from_pydata(name, verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = origin
    return link_and_update(obj)

def object_add_from_verts(verts, name, trunc=None):
    """Draw new object defined with only vertices (no edges or faces)"""
    if trunc is not None:
        verts = verts[0:trunc]

    # Create new mesh with verts as its vertices, obj
    verts = list(verts)
    edges = []
    faces = []

    mesh = mesh_add_from_pydata(name, verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)
    return link_and_update(obj)

def pointcloud_add(verts, name, trunc=None):
    """Draw new mesh-pointcloud defined with vertices and zero length edges"""
    if trunc is not None:
        verts = verts[0:trunc]

    # Create new mesh with verts as its vertices, obj
    length = len(verts)
    verts = list(verts)+list(verts)

    edges = []

    # create edges of 0 length for pointcloud viz w/ wireframe material
    for i in range(length):
        edges.append([i, i+length])
    faces = []

    mesh = mesh_add_from_pydata(name, verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)
    return link_and_update(obj)

def object_add_from_pydata(name, verts, edges, faces):
    """Create object from vert, edge and face defs"""
    mesh = mesh_add_from_pydata(name+"_mesh", verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)
    return link_and_update(obj)

# === Mesh creation ===
def mesh_add_from_pydata(name, verts, edges, faces):
    """Create mesh from vert, edge and face definitions"""
    mesh = bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata(verts, edges, faces)
    return mesh

# === Object manipulation ===
def link_and_update(obj):
    """Link object to scene, select, make active and update"""
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.update()
    return obj

def delete(obj):
    """Remove object"""
    scene = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scene.objects.active = obj
    bpy.ops.object.delete()

def delete_children(obj):
    """Delete all children belonging to object"""
    children = obj.children
    for ch in children:
        delete(ch)
    return children

def vertices_get(obj):
    """Get list of vertex tuples for the given object"""
    verts = []
    mesh = obj.data
    for vert in mesh.vertices:
        verts.append((vert.co[0], vert.co[1], vert.co[2]))
    return verts

def modifier_add_wireframe(obj, thickness=0.2):
    """Add wireframe modifier to obj

    thickness: thickness of wireframe
    """
    mod = obj.modifiers.new("Wireframe", type='WIREFRAME')
    mod.thickness = thickness
    mod.show_in_editmode = True
    return mod

def dupli_set(obj, type):
    """Set duplication type on obj"""
    obj.dupli_type = type

def parent_set(parent, child):
    """Set parent/child pair"""
    bpy.ops.object.select_all(action='DESELECT')

    # set active object to parent
    bpy.context.scene.objects.active = parent
    child.select = True

    # sets selected object as child of active object
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    # add child object to parent object's groups
    for grp in parent.users_group:
        space.group_add_object(grp, child)

def select(obj, sel):
    """Select or deselect object. Boolean sel."""
    obj.select = sel

def active_material_delete(obj):
    """Remove active material slot of object"""
    i = obj.active_material_index
    obj.data.materials.pop(i, update_data=True)

def selected_resize():
    return bpy.ops.transform.resize('INVOKE_DEFAULT')

