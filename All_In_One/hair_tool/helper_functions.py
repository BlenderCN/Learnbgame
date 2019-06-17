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
import math
from mathutils.bvhtree import BVHTree

def calc_power(cpow): #defined also in surface_to_splines
    if cpow < 0:  # (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        cpow = 1 + cpow * 0.8  # for negative map <-1,0> to <0.2, 1>
    else:
        cpow = 1 + 4 * cpow  # for positive map   <0, 1> to <1 , 5 >
    return cpow


def get_obj_mesh_bvht(obj, depsgraph, applyModifiers=True, world_space=True):
    if applyModifiers:
        if world_space:
            depsgraph.objects[obj.name].data.transform(obj.matrix_world)
            bvh = BVHTree.FromObject(obj, depsgraph)
            depsgraph.objects[obj.name].data.transform(obj.matrix_world.inverted())
            return bvh
        else:
            return BVHTree.FromObject(obj, depsgraph)
    else:
        if world_space:
            return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
        else:
            return BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])




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
        obj.material_slots[0].material = mat

def unlink_from_scene(obj):
    for col in obj.users_collection:
        col.objects.unlink(obj)
    if obj.name in bpy.context.scene.collection.objects.keys():
        bpy.context.scene.collection.objects.unlink(obj)
    obj.use_fake_user = True
        
def link_child_to_collection(parent_obj, clone):
    ''' Link clone to collection where parent_obj is located '''
    if parent_obj.users_collection:
        if clone.name not in parent_obj.users_collection[0].objects.keys():
            parent_obj.users_collection[0].objects.link(clone)
        else:
            return
    else:
        if clone.name not in bpy.context.scene.collection.objects.keys():
            bpy.context.scene.collection.objects.link(clone)
        else:
            return


def add_driver(
        source, target, prop, dataPath,
        index = -1, negative = False, func = ''
    ):
    ''' Add driver to source prop (at index), driven by target dataPath '''

    if index != -1:
        d = source.driver_add( prop, index ).driver
    else:
        d = source.driver_add( prop ).driver

    v = d.variables.new()
    v.name                 = prop
    v.targets[0].id        = target
    v.targets[0].data_path = dataPath

    d.expression = func + "(" + v.name + ")" if func else v.name
    d.expression = d.expression if not negative else "-1 * " + d.expression

    
def angle_signed(vA, vB, vN):
    '''angle betwen a - b, is vN space '''
    a = vA.normalized()
    b = vB.normalized()
    adotb = a.dot(b)  # not sure why but cos(x) goes above 1, and below -1   if a= -b
    if a.dot(b) > 1:
        adotb = 1
    elif a.dot(b) < -1:
        adotb = -1
    angle = math.acos(adotb)
    cross = a.cross(b)
    if vN.dot(cross) < 0:  # // Or > 0
        angle = -angle
    return angle




