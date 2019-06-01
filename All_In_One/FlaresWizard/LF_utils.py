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

import bpy
from mathutils import Vector, Euler

###### Utilities ########
def add_prop(obj, name, value, min, max, description):
    obj[name] = value
    if '_RNA_UI' not in obj.keys():
        obj['_RNA_UI'] = {}
    obj['_RNA_UI'][name] = {"min": min, "max": max ,"description": description}
    
def add_prop_var(driver, name, id_type, id, path):
    var = driver.driver.variables.new()
    var.name = name
    var.type = 'SINGLE_PROP'
    var.targets[0].id_type = id_type
    var.targets[0].id = id
    var.targets[0].data_path = path
    
def add_transform_var(driver, name, id, type, space ):
    var = driver.driver.variables.new()
    var.name = name
    var.type = 'TRANSFORMS'
    var.targets[0].id = id
    var.targets[0].transform_type = type
    var.targets[0].transform_space = space
    
def add_distance_var(driver, name, target1, target2):
    var = driver.driver.variables.new()
    var.name = name
    var.type = 'LOC_DIFF'
    var.targets[0].id = target1
    var.targets[1].id = target2
    
def add_flare_object(type, name, flare, flare_name, cam, hide = True, hide_sel = True):
    if type == 'empty':
        bpy.ops.object.empty_add(type = 'SPHERE', radius = 0.03, location = cam.location, rotation = cam.rotation_euler)
    elif type == 'plane':
        bpy.ops.mesh.primitive_plane_add(radius = 0.15, location=cam.location,rotation = cam.rotation_euler)        
    ob = bpy.context.object
    if type == 'plane':
        ob.draw_type = 'WIRE'            
    ob.parent = cam
    ob.name = name
    ob.location = Vector((0, 0, 0))
    ob.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
    ob[flare] = flare_name
    ob['IS_BLF'] = ''
    ob.hide = hide
    ob.hide_select = hide_sel
    return ob
def set_ray_visibility(ob):
    ob.cycles_visibility.glossy = False
    ob.cycles_visibility.diffuse = False
    ob.cycles_visibility.shadow = False
    ob.cycles_visibility.scatter = False
    ob.cycles_visibility.transmission = False