# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO
import bpy

def calc_power(cpow): #defined also in surface_to_splines
    if cpow < 0:  # (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        cpow = 1 + cpow * 0.8  # for negative map <-1,0> to <0.2, 1>
    else:
        cpow = 1 + 4 * cpow  # for positive map   <0, 1> to <1 , 5 >
    return cpow


def assign_material(obj, material_name, clear_materials=True):
    '''Add material to obj. If clear_material is True - reomve all slots exept first.'''
    if material_name not in  bpy.data.materials.keys():
        print('Material %s dosen\'t exist!' %(material_name))
        return
    mat =bpy.data.materials[material_name]
    if clear_materials is True:
        while len(obj.material_slots)>1:
            obj.data.materials.pop()
    if len(obj.material_slots) == 0:  #make sure first slot is assigned
        obj.data.materials.append(mat)
    else:
        obj.material_slots[0].material =mat