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

# <pep8 compliant>

import bpy
from util import strhash16
from bpy.props import BoolProperty
from bpy.app.handlers import persistent
from pynodes_framework import idref


driver_prop_name = "modifier_driver_dummy"
driver_prop = BoolProperty(name="Modifier Nodes Dummy",
                           description="Dummy property to act as a driver hook for modifiers",
                           options={'HIDDEN', 'SKIP_SAVE', 'ANIMATABLE'})


def object_find_driver(ob):
    if ob.animation_data:
        for fcurve in ob.animation_data.drivers:
            if fcurve.data_path == driver_prop_name:
                return fcurve
    return None


def object_clear_driver(ob):
    fcurve = object_find_driver(ob)
    if fcurve:
        # remove all the old driver variables
        for i in range(len(fcurve.driver.variables)):
            fcurve.driver.variables.remove(fcurve.driver.variables[0])


def object_add_driver(ob, base, struct_path, prop, prop_index):
    if base == 'bdata':
        base_data = bpy.data
    elif base == 'object':
        base_data = ob

    if struct_path:
        ptr = eval("base_data.%s" % struct_path)
    else:
        ptr = base_data
    id_data = ptr.id_data

    setup_namespace()

    fcurve = object_find_driver(ob)
    if not fcurve:
        fcurve = ob.driver_add(driver_prop_name)
    fcurve.driver.expression = "modifier_nodes(%d)" % ob.as_pointer()

    var = fcurve.driver.variables.new()
    #var.name = "value" # NB: variable is unused in dummy expression, no need to choose a name
    var.type = 'SINGLE_PROP'
    target = var.targets[0]
    id_type = idref.id_data_type_identifier(ptr.id_data)
    if id_type is None:
        raise Exception("Unsupported ID type %r in driver expression" % ptr.id_data)
    target.id_type = id_type
    target.id = ptr.id_data
    target.data_path = ptr.path_from_id(prop)
    if prop_index is not None:
        target.data_path += "[%r]" % prop_index

def object_remove_driver(ob):
    ob.driver_remove(driver_prop_name)

@persistent
def objects_update_driver_on_load_post(dummy):
    for ob in bpy.data.objects:
        fcurve = object_find_driver(ob)
        if fcurve:
            fcurve.driver.expression = "modifier_nodes(%d)" % ob.as_pointer()


def find_object_by_id(ob_id):
    for ob in bpy.data.objects:
        if ob.as_pointer() == ob_id:
            return ob
    return None

def sync_object(ob_id, **kwargs):
    import database
    ob = find_object_by_id(ob_id)
    if ob is None:
        raise KeyError("Object %d not in bpy.data" % ob_id)

    database.sync_object(ob, force=True)
    return 0.0


def setup_namespace():
    if "modifier_nodes" not in bpy.app.driver_namespace:
        bpy.app.driver_namespace["modifier_nodes"] = sync_object

@persistent
def setup_namespace_on_load_post(dummy):
    bpy.app.driver_namespace["modifier_nodes"] = sync_object

def clear_namespace():
    if "modifier_nodes" in bpy.app.driver_namespace:
        del bpy.app.driver_namespace["modifier_nodes"]
   

def register():
    setattr(bpy.types.Object, driver_prop_name, driver_prop)

    setup_namespace()
    bpy.app.handlers.load_post.append(setup_namespace_on_load_post)
    bpy.app.handlers.load_post.append(objects_update_driver_on_load_post)

def unregister():
    for handler in bpy.app.handlers.load_post:
        if handler in {setup_namespace_on_load_post, objects_update_driver_on_load_post}:
            bpy.app.handlers.load_post.remove(handler)
    clear_namespace()

    if hasattr(bpy.types.Object, driver_prop_name):
        delattr(bpy.types.Object, driver_prop_name)
