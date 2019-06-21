# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

# Generic helper functions, to be used by any modules.

import bmesh
import array

# method from the Print3D add-on
def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """
    Returns a transformed, triangulated copy of the mesh
    """

    assert(obj.type == 'MESH')

    if apply_modifiers and obj.modifiers:
        import bpy
        me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=False)
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        del bpy
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    # TODO. remove all customdata layers.
    # would save ram

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm

# method adapted from the Print3D add-on
def calc_area(obj):
    """
    Calculate the surface area of an object.
    """
    bm = bmesh_copy_from_object(obj, apply_modifiers=True)
    area = sum(f.calc_area() for f in bm.faces)
    bm.free()
    return area

# method adapted from the Print3D add-on
def calc_volume(obj):
    """
    Calculate the volume of an object.
    """    
    bm = bmesh_copy_from_object(obj, apply_modifiers=True)
    volume = bm.calc_volume(signed=True)
    bm.free()
    return abs(volume)

# method kept outside evertClass Room to be able to access it from operators.py 
# to udate room rt60 values prior to bge session
def getRt60Values(matDict, obj):
    """
    retun room (obj) RT60 coefficients based on room volume and area, the later 
    weighted with absorption coefs, based on Sabine formula
    WARNING: does not take scene unit.system scale into account
    """        
    bm = bmesh_copy_from_object(obj, apply_modifiers=True)
    # loop over faces, get weighted areas
    wAreas = [0,0,0,0,0,0,0,0,0,0]
    for f in bm.faces:
        # get face material name
        slot = obj.material_slots[f.material_index]
        matName = slot.material.name
        # get associated abs coefs
        if not matName in matDict: print('undefined evertims material', matName)
        absCoefs = matDict[matName]
        # get face area
        area = f.calc_area()
        # compute freq specific weighted areas (min abs coef is 0.001, to avoid div by zero)
        for i in range(len(absCoefs)): wAreas[i] += max(absCoefs[i], 0.001) * area
    bm.free()        
    # get room volume
    volume = calc_volume(obj)
    # get frequency specific RT60 from Sabine formula
    rt60Values = [ float(round(0.161 * volume / a,3)) for a in wAreas ]
    return rt60Values
