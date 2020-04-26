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

import math
from bisect import bisect_left
import logging

import bpy
from mathutils import Vector, Matrix

from molblend.elements_default import ELEMENTS as ELEMENTS_DEFAULT

logger = logging.getLogger(__name__)

#--- Geometry functions ------------------------------------------------------#

def get_fixed_angle(context, first_loc, coord_3d, angle_list=None):
    angle_list = angle_list or []
    # get current vector between first_atom and the mouse pointer
    bond_vector = coord_3d - first_loc
    
    basis_change_matrix = context.region_data.view_matrix.to_3x3()
    basis_change_matrix.transpose()
    # bond vector in viewing coordinates
    transformed = basis_change_matrix.inverted() * bond_vector
    # projection of coordinates into screen plane
    xy_vec = Vector((transformed.x, transformed.y))
    # unambiguous angle between screen-x-axis and bond vector
    angle = math.atan2(xy_vec.y, xy_vec.x)
    
    if not angle_list:
        angles_30 = list(range(-180, 181, 30))
        angles_45 = list(range(-180, 181, 45))
        angle_list = set(angles_30 + angles_45)
    fixed_angles = sorted(list(map(math.radians, angle_list)))
    # find closest fixed angle in list
    pos = bisect_left(fixed_angles, angle)
    if pos == 0:
        fixed = fixed_angles[0]
    elif pos == len(fixed_angles):
        fixed = fixed_angles[-1]
    else:
        before = fixed_angles[pos - 1]
        after = fixed_angles[pos]
        if after - angle < angle - before:
            fixed = after
        else:
            fixed = before
    
    # get fixed angle in the screen plane with same projected length as before
    transformed.x = math.cos(fixed) * xy_vec.length
    transformed.y = math.sin(fixed) * xy_vec.length
    
    # transform back to world coordinates
    new_bond_vector = basis_change_matrix * transformed
    # calculate new coordinates of second atom
    fixed_vector = first_loc + new_bond_vector
    return fixed_vector


def get_fixed_length(context, first_atom, second_atom, coord_3d, length=-1):
    if length < 0:
        r1 = context.scene.mb.elements[first_atom.mb.element].covalent
        r2 = context.scene.mb.elements[second_atom.mb.element].covalent
        length = r1 + r2
    first_loc = first_atom.mb.world_location
    bond_vector = (coord_3d - first_loc).normalized()
    return first_loc + bond_vector * length


def get_fixed_geometry(context, first_atom, new_atom, coord_3d, geometry):
    '''
    use existing bonds of first_atom to calculate new possible bond vectors for
    new bond based on geometry return the position that is closest to the mouse
    pointer (coord_3d)
    '''
    if geometry == 'NONE':
        return coord_3d
    
    first_loc = first_atom.mb.world_location
    
    bond_vecs = []
    for bond in first_atom.mb.bonds:
        for atom in bond.mb.bonded_atoms:
            if (not atom == first_atom
                    and not atom == new_atom):
                bond_vecs.append((atom.mb.world_location
                                  - first_loc).normalized())
                break
    
    # existing number of bonds
    n_bonds = len(bond_vecs)
    
    if geometry == 'GENERAL' or n_bonds == 0:
        return get_fixed_angle(context, first_loc, coord_3d)
    
    elif geometry == 'LINEAR':
        # matrix to change between view and world coordinates
        basis_change_matrix = context.region_data.view_matrix.to_3x3()
        basis_change_matrix.transpose()
        # get all possible angles projected into the view plane
        fixed_xy = []
        for bond_vec in bond_vecs:
            # bond vector in viewing coordinates
            transformed = basis_change_matrix.inverted() * bond_vec
            # projection of point mirrored coordinates into screen plane
            fixed_xy.append(-Vector((transformed.x, transformed.y)))
        
        # get current vector between first_atom and the mouse pointer
        bond_vector = coord_3d - first_loc
        
        # bond vector in viewing coordinates
        transformed = basis_change_matrix.inverted() * bond_vector
        # projection of coordinates into screen plane
        xy_vec = Vector((transformed.x, transformed.y))
        
        # find index of closest fixed xy in list
        pos, min_angle = min(
            enumerate(xy_vec.angle(other) for other in fixed_xy),
            key=lambda p: p[1])
        
        fixed_bond_vector = -bond_vecs[pos]
        
        # calculate new coordinates of second atom
        fixed_vector = first_loc + fixed_bond_vector * xy_vec.length
        return fixed_vector

    elif geometry == 'TRIGONAL':
        basis_change_matrix = context.region_data.view_matrix.to_3x3()
        basis_change_matrix.transpose()
        
        # get current vector between first_atom and the mouse pointer
        bond_vector = coord_3d - first_loc
        
        # bond vector in viewing coordinates
        transformed = basis_change_matrix.inverted() * bond_vector
        # projection of coordinates into screen plane
        xy_vec = Vector((transformed.x, transformed.y))
        
        if n_bonds >= 2:
            # get the bisecting vectors
            fixed_xy = []
            bisect_vectors = []
            for i, b1 in enumerate(bond_vecs[:-1]):
                for b2 in bond_vecs[i+1:]:
                    bisect_vector = -(b1 + b2).normalized()
                    if (b1+b2).cross(b1).length < 1e-06:
            # if the two existing bonds are exactly linear, the new vector will
            # have zero length and the new bond can lie on a circle around the 
            # middle atom. Return the two fixed angles that are orthogonal to 
            # the two bonds and in the view plane
                        view = basis_change_matrix.col[2]
                        bisect_vector = b1.cross(view).normalized()
                        
                    bisect_vectors.append(bisect_vector)
                    transformed = (basis_change_matrix.inverted() 
                                    * bisect_vector)
                    fixed_xy.append(Vector((transformed.x, transformed.y)))
                    # ... and the other one
                    bisect_vector = -bisect_vector
                    bisect_vectors.append(bisect_vector)
                    transformed = (basis_change_matrix.inverted() 
                                    * bisect_vector)
                    fixed_xy.append(Vector((transformed.x, transformed.y)))
                
            # find index of closest fixed xy in list
            pos, min_angle = min(
                list(enumerate(xy_vec.angle(other) for other in fixed_xy)),
                key=lambda p: p[1])
           
            fixed_bond_vector = bisect_vectors[pos]
            
            # calculate new coordinates of second atom
            fixed_vector = (first_loc
                            + fixed_bond_vector * xy_vec.length)
            return fixed_vector
        
        elif n_bonds == 1:
            # Need to break ambiguity here. Pick two points as the intersection
            # of the circle of possible points with viewing plane
            
            # view vector
            N = context.region_data.view_rotation*Vector((0,0,-1))
            # distance between mouse cursor and first atom
            l = bond_vector.length
            
            vec = bond_vecs[0].cross(N).normalized()
            if vec.length == 0:
                vec = bond_vecs[0].cross(basis_change_matrix * Vector((1,0,0)))
            C0 = first_loc - 0.5 * l * bond_vecs[0]
            fixed_xy = []
            bisect_vectors = []
            for fac in (-1, 1):
                new_vec = C0 + vec*fac*math.sqrt(3./4)*l - first_loc
                bisect_vectors.append(new_vec)
                transformed = basis_change_matrix.inverted() * new_vec
                fixed_xy.append(Vector((transformed.x, transformed.y)))
                
            # find index of closest fixed xy in list
            pos, min_angle = min(
                enumerate(xy_vec.angle(other) for other in fixed_xy), 
                key=lambda p: p[1])
            
            fixed_bond_vector = bisect_vectors[pos]
            
            # calculate new coordinates of second atom
            fixed_vector = (first_loc + fixed_bond_vector)
            return fixed_vector

    # TODO implement other 3D geometries (like tetrahedral, octahedral, etc.
    else:
        logger.error("Geometry {} not implemented yet.".format(geometry))
        return coord_3d
