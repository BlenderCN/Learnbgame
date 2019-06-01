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

# copyright (c) 2015 urchn.org,
# Bassam Kurdali,
# get_sampled_frames() from Bill L.Nieuwendorp /GPL v2 or later

bl_info = {
    "name": "Meshcacher",
    "author": "Bassam Kurdali (see notes)",
    "version": (1, 99),
    "blender": (2, 75, 0),
    "location": "View3D > Search > Cache Groups",
    "description": "Replace linked groups with cached meshes",
    "warning": "",
    "wiki_url": "http://wiki.urchn.org/wiki/Meshcacher",
    "category": "Learnbgame",
}

"""
Recreates an animated linked group/proxy with a local copy of visible meshes
with mesh caches for the animation.

Warning: gilga must have 'Show hair' and 'Show Cornea' toggled on!!!

Some functions taken from pc2 export script by Bill L.Nieuwendorp
"""

import bpy
import math
import os
import json
import random
import re
from mathutils import Matrix
from bpy.props import IntProperty, EnumProperty, StringProperty, BoolProperty
from bpy.types import Operator
from os import path
from struct import pack

# XXX Inspect these with vigilance in case they should be configs
SUFFIX = "CACHE" # TODO search for CACHE and SUFFIX when doing cache mgmnt.
DRIVER_PROP_NAME = "frame" # note
DRIVER_PROP = '["{}"]'.format(DRIVER_PROP_NAME)
SEP = path.sep
CONFIGTEXT = "meshcacher_config.JSON"
MAX_ID = 999999 # theoretical max number of caches in a file
CONSTRUCTIVE_MODIFIERS = [
    "ARRAY", "BEVEL", "BOOLEAN", "BUILD", "DECIMATE", "MULTIRES",
    "MULTIRES", "EDGE_SPLIT", "MASK", "REMESH", "SCREW", "SKIN",
    "SOLIDIFY", "SUBSURF", "TRIANGULATE", "WIREFRAME"]

'''
Things to do


recaching:
-take an existing cache, select on any tagged object.
-I want to recache this
-Get back original animation, transforms, etc.
-Hide Caches (layer placement?)

-Allow animation

-Cache back to same ID (how?) (maybe tag the armature object earlier)
-Remove tag after caching

project mode vs. user select:
store mode in config.
project mode uses project root/non svn dir in config,
if missing, or if current file not in project root directory, non project mode
else project mode
checkbox that can be switched if possible (grey out otherwise)

non project mode allows selection of directories

'''


def abspath(path):
    return os.path.abspath(bpy.path.abspath(path))


def make_suffix(item, name, lib_path, instance):
    """ local datablocks get suffixes and tags, blender handles collisions """
    item.name = "{}_{}_{}".format(name, instance, SUFFIX)
    item["CACHE_REMOTE"] = name
    item["CACHE_LIB_PATH"] = lib_path
    item["CACHE_INSTANCE"] = instance


def check_suffix(item, name, lib_path, instance):
    """ check to see if a local datablock references a cached remote one """
    return item.name.startswith("{}_{}_{}".format(name, instance, SUFFIX)) and\
        all(prop in item.keys() for\
        prop in ("CACHE_REMOTE", "CACHE_LIB_PATH")) and\
        item["CACHE_REMOTE"] == name and\
        item["CACHE_LIB_PATH"] == lib_path and\
        item["CACHE_INSTANCE"] == instance


def find_cached(scene, ob, instance):
    """ find the local cache of an object in a group """
    if not ob.library:
        return ob # Object is already cached!
    local_objects = (
        local for local in scene.objects if check_suffix(
            local, ob.name, ob.library.filepath, instance))
    for found in local_objects:
        return found
    return None


def find_local(item, instance):
    """ find a localized version of our item """
    for subtype in dir(bpy.data):
        try:
            if item in getattr(bpy.data, subtype).values():
                local_items = (
                    local for local in getattr(bpy.data, subtype)
                    if check_suffix(
                        local, item.name, item.library.filepath, instance))
                for found in local_items:
                    return found
        except:
            pass
    return None


def find_remote(item):
    """ find the source datablock for our local cache """
    for subtype in dir(bpy.data):
        try:
            if item in getattr(bpy.data, subtype).values():
                for remote in getattr(bpy.data, subtype):
                    if remote.library and\
                            remote.library.filepath == item["CACHE_LIB_PATH"]:
                        if remote.name == item["CACHE_REMOTE"]:
                            return remote
        except:
            pass
    return None


def protected_duplicate(item, instance):
    """
    return a duplicate a remote item if it doesn't already exist, otherwise
    return the existing duplicate
    """
    new_item = find_local(item, instance)
    if not new_item:
        new_item = item.copy()
        make_suffix(
            new_item, item.name, item.library.filepath, instance)
    return new_item


def get_object_groups(ob):
    """ find the groups that ob belongs in """
    return [
        grp for grp in bpy.data.groups if ob.name in grp.objects
        and grp.library == ob.library]


def get_sampled_frames(start, end, rate):
    """ integer/ float portion of sampled frames """
    return [
        math.modf(start + x * rate)
        for x in range(int((end - start) / rate) + 1)]


def is_driver_animated(driver, proxy):
    """ return True if driver is changing over time """
    for variable in driver.driver.variables:
        for target in variable.targets:
            id_object = target.id
            if id_object.data != proxy.data:
                return False

            if proxy.animation_data and proxy.animation_data.action:
                target_action = proxy.animation_data.action
                if variable.type == 'SINGLE_PROP':
                    fcurves = [
                        f for f in target_action.fcurves
                        if target.data_path == f.data_path]
                    if fcurves: # we found our data path in the action!
                        if len(fcurves[0].keyframe_points) > 1:
                            return True
                        elif len(fcurves[0].keyframe_points) == 1:
                            for modifier in fcurves[0]:
                                if modifier.type in [
                                        "GENERATOR", "FNGENERATOR", "NOISE"]:
                                    return True
    return False


def get_visible_objects(groups, proxy):
    """ Returns a list of visible Mesh objects in a bpy group object """
    obs = set()
    for group in groups:
        for ob in group.objects:
            if ob.type == 'MESH' and any(
                    i and j for i, j in zip(ob.layers, group.layers)):
                if not ob.hide_render:
                    obs.add(ob)

                elif ob.animation_data:
                    for driver in ob.animation_data.drivers:
                        if 'hide_render' == driver.data_path:
                            if is_driver_animated(driver, proxy):
                                obs.add(ob)
    return list(obs)


def get_extra_objects(groups):
    """ Returns a list of objects preselected for caching in the asset file """
    obs = set()
    for group in groups:
        for ob in group.objects:
            if 'CASHIFY' in ob.keys():
                obs.add(ob)
    return list(obs)


def make_object(scene, name, layers, ob_data=None):
    """ Adds a new object to the current scene """
    newob = bpy.data.objects.new(name=name, object_data=ob_data)
    scene.objects.link(newob)
    newob.layers = layers
    return newob


def meshify_object(
        context, scene, ob, modifier_setting, local_groups, instance):
    """ Replace the mesh but keep edited hair alive """
    # we need to remove the non particle modifiers
    newmesh = ob.to_mesh(scene, True, modifier_setting)
    edited_hair = False
    context['object'] = ob
    if any(sys.is_edited for sys in ob.particle_systems):
        context['particle_system'] = ob.particle_systems[0]
        edited_hair = True
        # set subsurfs to render before disconnecting hair
        for modifier in ob.modifiers:
            if modifier.type == 'SUBSURF':
                modifier.levels = modifier.render_levels
                modifier.show_viewport = modifier.show_render
        bpy.ops.particle.disconnect_hair(context, all=True)
    modifier_count = len(ob.modifiers)
    for i in range(modifier_count - 1, -1, -1):
        if ob.modifiers[i].type != 'PARTICLE_SYSTEM':
            ob.modifiers.remove(ob.modifiers[i])
    ob.data = newmesh
    for particle_system in ob.particle_systems:
        particle_system.settings = particle_system.settings.copy()
        remote_group = particle_system.settings.effector_weights.group
        if remote_group:
            local_group = [
                grp for grp in local_groups if check_suffix(
                    grp, remote_group.name,
                    remote_group.library.filepath, instance)][0]
            particle_system.settings.effector_weights.group = local_group
    if edited_hair:
        bpy.ops.particle.connect_hair(context, all=True)
        if 'particle_system' in context:
            context.pop('particle_system')


def retain_driven_masks(context, newob):
    """ driven masks need to be held and retrieved because timelapse """
    pass


def group_object_from_remote(ob, newob, possible_groups, instance):
    """
    Put the local object in the localized groups of the remote, creating
    them if needed.
    """
    remote_groups = get_object_groups(ob)
    actual_remotes = [grp for grp in remote_groups if grp in possible_groups]
    local_groups = []
    for grp in actual_remotes:
        local_maybes = [
            maybe for maybe in bpy.data.groups
            if check_suffix(maybe, grp.name, grp.library.filepath, instance)]
        if local_maybes:
            local_groups.append(local_maybes[0])
        else:
            new_group = bpy.data.groups.new(name="TEMP")  # local group stuff
            make_suffix(new_group, grp.name, grp.library.filepath, instance)
            local_groups.append(new_group)
    for local_group in local_groups:
        local_group.objects.link(newob)
    return local_groups


def setup_driver(driver, target, target_path):
    """ Setup a variable to be driven by our target """
    while driver.keyframe_points:
        driver.keyframe_points.remove(driver.keyframe_points[-1], True)
    while driver.driver.variables:
        driver.driver.variables.remove(driver.driver.variables[-1])
    while driver.modifiers:
        driver.modifiers.remove(driver.modifiers[-1])
    variable = driver.driver.variables.new()
    variable.targets[0].id_type = 'OBJECT'
    variable.targets[0].id = target
    variable.targets[0].data_path = target_path
    variable.type = 'SINGLE_PROP'
    driver.driver.type = 'AVERAGE'


def remove_visiblity_drivers(ob):
    """ remove visibility drivers in an object """
    if ob.animation_data:
        for driver in ob.animation_data.drivers:
            if driver.data_path in ("hide", "hide_render"):
                ob.driver_remove(driver.data_path, -1)


def create_driver(ob, path, index, target, target_path):
    """ Add a driver to a bone with proper stuff """
    driver = ob.driver_add(path, index)
    setup_driver(driver, target, target_path)
    return driver


def fix_nodes(node_groups, node_tree, target, target_path, instance):
    """ recursively localize images and node_groups """
    if node_tree.animation_data:
        for driver in node_tree.animation_data.drivers:
            setup_driver(driver, target, DRIVER_PROP)
    for node in node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image.library:
            node.image = protected_duplicate(node.image, instance)
    for node in node_tree.nodes:
        if node.type == 'GROUP' and node.node_tree.library:
            node.node_tree = protected_duplicate(node.node_tree, instance)
            if node.node_tree not in node_groups:
                fix_nodes(
                    node_groups, node.node_tree, target, target_path, instance)
                node_groups.add(node.node_tree)


def duplicate_object(
        context, scene, target, remote_groups, ob, materials, node_groups,
        modifier_setting, apply_subsurf, instance, ob_postmods):
    """ Make a linked copy of the object in the scene """
    newob = find_cached(scene, ob, instance)
    if newob: return newob
    newob = ob.copy()                 # Let's copy our original object
    # if we don't want to cache the final subsurf, remove it
    if newob.modifiers and newob.modifiers[-1].type == 'SUBSURF':
        if not apply_subsurf:
            newob.modifiers.remove(newob.modifiers[-1])
    for mod in ob_postmods:
        if mod['name'] in newob.modifiers:
            newob.modifiers.remove(newob.modifiers[mod['name']])
    local_groups = group_object_from_remote(ob, newob, remote_groups, instance)
    retain_driven_masks(context, newob)
    meshify_object(
        context, scene, newob, modifier_setting, local_groups, instance)
    make_suffix(newob, ob.name, ob.library.filepath, instance)
    for slot in newob.material_slots:
        if slot.material and slot.material.library:
            slot.material = protected_duplicate(slot.material, instance)
            if slot.material not in materials:
                node_tree = slot.material.node_tree
                if node_tree:
                    fix_nodes(
                        node_groups, node_tree, target, DRIVER_PROP, instance)
                if slot.material.animation_data:
                    for driver in slot.material.animation_data.drivers:
                        setup_driver(driver, target, DRIVER_PROP)
                materials.add(slot.material)
    scene.objects.link(newob)
    newob.layers = scene.layers
    newob.matrix_world = ob.matrix_world
    return newob


def duplicate_helper_object(scene, remote_groups, ob, instance):
    """ Make a linked copy of a helper object in the scene """
    newob = find_cached(scene, ob, instance)
    if newob: return newob
    newob = ob.copy()
    newob.data = newob.data.copy()
    scene.objects.link(newob)
    newob.layers = scene.layers
    newob.matrix_world = ob.matrix_world
    make_suffix(newob, ob.name, ob.library.filepath, instance)
    if newob.type == 'ARMATURE':
        old_active = scene.objects.active
        scene.objects.active = newob
        newob.select = True
        bpy.ops.object.editmode_toggle()
        for bone in newob.data.edit_bones:
            if not 'CASHIFY' in bone.keys():
                newob.data.edit_bones.remove(bone)
        bpy.ops.object.editmode_toggle()
        scene.objects.active = old_active
        for bone in newob.pose.bones:
            while len(bone.constraints):
                bone.constraints.remove(bone.constraints[0])
    local_groups = group_object_from_remote(ob, newob, remote_groups, instance)
    return newob


def make_group_copy(
        context, scene, remote_groups, proxy,
        modifier_setting, apply_subsurf, instance, postmodifiers):
    """ Make a local copy of a group """
    materials, node_groups = set(), set()
    parent = make_object(
        scene,
        "{}_{}_CACHE".format(remote_groups[0].name.split('_')[0], instance),
        proxy.layers)
    target_objects = get_visible_objects(remote_groups, proxy)
    local_objects = [
        duplicate_object(
            context, scene, parent, remote_groups, group_ob,
            materials, node_groups,
            modifier_setting, apply_subsurf, instance,
            postmodifiers[group_ob.name])
        for group_ob in target_objects]

    for local_ob in local_objects:
        local_ob.parent = parent
        local_ob.layers = proxy.layers
    extra_objects = get_extra_objects(remote_groups)
    local_extra_objects = [
        duplicate_helper_object(scene, remote_groups, extra_ob, instance)
        for extra_ob in extra_objects
    ]
    for local_ob in local_extra_objects:
        for modifier in local_ob.modifiers:
            modifier.object = find_cached(scene, modifier.object, instance)
        if local_ob.parent_type == 'OBJECT' or not local_ob.parent:
            local_ob.parent = parent
        else:
            local_ob.parent = find_cached(scene, local_ob.parent, instance)
            local_ob.matrix_parent_inverse = find_remote(
                local_ob).matrix_parent_inverse.copy()
        local_ob.layers = proxy.layers
    materials, node_groups = list(materials), list(node_groups)
    return parent, local_objects, local_extra_objects, materials, node_groups


def write_cache_file(filepath, cache_lines):
    """ Actually write out a cache file """
    with open(abspath(filepath), 'wb') as pc2_file:
        for line in cache_lines:
            pc2_file.write(line)


def make_filepath(ob, cache_dir):
    """ Create the full filepath for the object's cache and return it """
    if ob.library:
        qualifier = path.split(ob.library.filepath)[-1].split('.')[0]
    else:
        qualifier = "LOCAL"
    return path.join(cache_dir, "{}_{}.pc2".format(ob.name, qualifier))


def make_header(ob, scene, rate, sample_count, modifier_setting):
    """ return the file header"""
    mesh = ob.to_mesh(scene, True, modifier_setting)
    vert_count = len(mesh.vertices)
    print(ob.name, ' header:', vert_count)
    bpy.data.meshes.remove(mesh)
    return pack(
        '<12siiffi', b'POINTCACHE2\0', 1, vert_count,
        scene.frame_start, rate, sample_count), vert_count


def get_cache_rigs(scene, parent, groups, instance):
    """ Get rigs we need to cache with their bones """
    rigs = set()
    for group in groups:
        for rig in group.objects:
            if rig.type == 'ARMATURE' and "CASHIFY" in rig.keys():
                rigs.add(rig)
    rigs = list(rigs)
    local_rigs = []
    for rig in rigs:
        local_rigs.append(find_cached(scene, rig, instance))
    rigs_bones = [
        [
            bone.name for bone in rig.pose.bones
            if "CASHIFY" in rig.data.bones[bone.name].keys()
        ] for rig in rigs]
    # create the fcurves in the drivers
    for rig, rig_bones in zip(local_rigs, rigs_bones):
        if rig.animation_data:
            rig.animation_data_clear()
        rig.animation_data_create()
        for bone_name in rig_bones:
            prefix = 'pose.bones["{}"].'.format(bone_name)
            for i in range(3):
                create_driver(
                    rig, '{}location'.format(prefix), i, parent, DRIVER_PROP)
            for i in range(4):
                create_driver(
                    rig, '{}rotation_quaternion'.format(prefix), i,
                    parent, DRIVER_PROP)
            for i in range(3):
                create_driver(
                    rig, '{}scale'.format(prefix), i, parent, DRIVER_PROP)
    return [thing for thing in zip(rigs, local_rigs, rigs_bones)]


def get_matrix(ob, source_bone, pose_bone, data_bone, ignoreparent):
    """Helper function for visual transform copy,
       gets the active transform in bone space
    """
    #all matrices are in armature space unless commented otherwise
    ob_mat = source_bone.matrix  # final 4x4 mat of target.
    rest_mat = data_bone.matrix_local.copy()  # self rest matrix
    if data_bone.parent:
        parentposemat = ob.pose.bones[data_bone.parent.name].matrix
        parentbonemat = data_bone.parent.matrix_local
    else:
        parentposemat = parentbonemat = Matrix()
    if parentbonemat == parentposemat or ignoreparent:
        newmat = rest_mat.inverted() * ob_mat
    else:
        bonemat = parentbonemat.inverted() * rest_mat
        newmat = bonemat.inverted() * parentposemat.inverted() * ob_mat
    return newmat


def bake_rig_transforms(scene, frame, ob, local_ob, bones):
    """Copy per frame transforms from a rig to an action"""
    driver_x = frame - scene.frame_start
    offset = 0
    for bone_name in bones:
        pose_bone = local_ob.pose.bones[bone_name]
        data_bone = local_ob.data.bones[bone_name]
        source_bone = ob.pose.bones[bone_name]
        mat = get_matrix(ob, source_bone, pose_bone, data_bone, False)
        loc, rot, sca = mat.decompose()
        if not data_bone.use_inherit_rotation:
            mat = get_matrix(ob, source_bone, pose_bone, data_bone, True)
            rot = mat.to_3x3().to_quaternion()
        if not data_bone.use_inherit_scale:
            mat = get_matrix(ob, source_bone, pose_bone, data_bone, True)
            sca = mat.to_scale()
        drivers = local_ob.animation_data.drivers
        for transform in (loc, rot, sca):
            for i in range(len(transform)):
                drivers[i + offset].keyframe_points.add()
                keyframe = drivers[i + offset].keyframe_points[-1]
                keyframe.co = (driver_x, transform[i])
                keyframe.handle_left_type = keyframe.handle_right_type =\
                    'AUTO_CLAMPED'
                keyframe.interpolation = 'BEZIER'
            offset += len(transform)


def generic_driven_to_curves(frame, source, target):
    """ copy driven source values to animated ones """
    if source.animation_data and target.animation_data:
        for source_driver, target_driver in zip(
                source.animation_data.drivers, target.animation_data.drivers):
            value = eval('source.{}'.format(source_driver.data_path))
            target_driver.keyframe_points.add()
            keyframe = target_driver.keyframe_points[-1]
            try:
                keyframe.co = (frame, value[source_driver.array_index])
            except:
                keyframe.co = (frame, value)
            keyframe.handle_left_type = keyframe.handle_right_type =\
                    'AUTO_CLAMPED'
            keyframe.interpolation = 'BEZIER'


def yucky_update(driven):
    """ dunno why we have to do this ... but drivers sometimes don't update """
    if driven.animation_data:
        for driver in driven.animation_data.drivers:
            driver.update()
            for variable in driver.driver.variables:
                variable.type = 'SINGLE_PROP'
            driver.driver.type = 'AVERAGE'


def find_animated_trees(node_tree, animated_trees, proxy):
    if node_tree and node_tree.animation_data:
        for driver in node_tree.animation_data.drivers:
            if is_driver_animated(driver, proxy):
                if not node_tree.name in animated_trees:
                    animated_trees[node_tree.name] = [node_tree, {}]
                animated_trees[node_tree.name][1][driver.data_path] = []
    for node in node_tree.nodes:
        if node.type == 'GROUP':
            find_animated_trees(node.node_tree, animated_trees, proxy)


def collect_data(obs, proxy, apply_subsurf):
    """ Collect postmodifier data, material data before caching """
    postmodifiers = {ob.name: [] for ob in obs}
    postmaterials = {}
    postnodetrees = {}
    postpaths = {}

    for ob in obs:
        postpaths[ob.name] = {}
        modnames = []
        if ob.animation_data:
            for driver in ob.animation_data.drivers:
                if 'modifiers[' in driver.data_path:
                    # Looking for modifiers["ANYNAME"] returns ANYNAME
                    rem = re.match(
                        '(?:modifiers\[\")(.*)(?:\"])', driver.data_path)
                    if is_driver_animated(driver, proxy):
                        if (
                                rem.group(1) in ob.modifiers and
                                ob.modifiers[rem.group(1)].type in
                                CONSTRUCTIVE_MODIFIERS):
                            modnames.append(rem.group(1))
                            postpaths[ob.name][driver.data_path] = []
                elif driver.data_path in ('hide', 'hide_render'):
                    postpaths[ob.name][driver.data_path] = []
        for slot in ob.material_slots:
            if slot.material:
                node_tree = slot.material.node_tree
                if node_tree and node_tree.animation_data:
                    for driver in node_tree.animation_data.drivers:
                        if is_driver_animated(driver, proxy):
                            if slot.material.name not in postmaterials:
                                postmaterials[slot.material.name] = [
                                    slot.material, {}]
                            postmaterials[slot.material.name][1][
                                driver.data_path] = []
                for node in node_tree.nodes:
                    if node.type == 'GROUP':
                        find_animated_trees(
                            node.node_tree, postnodetrees, proxy)
        for modifier in ob.modifiers:
            # now we can filter out our constructive modifiers:
            if (
                    modifier.type in CONSTRUCTIVE_MODIFIERS and
                    modifier.name in modnames):

                postmodifiers[ob.name].append({
                attr: getattr(modifier,attr) for attr in dir(modifier)
                if attr not in
                ('__doc__', '__module__',
                 '__slots__', 'bl_rna', 'rna_type')})
                # modifier.show_render = False #XXX might not work :/
                # modifier.show_viewport = False #XXX might not work :/
        if (
                ob.modifiers and ob.modifiers[-1].type == 'SUBSURF'
                and not apply_subsurf):
            lastmod = ob.modifiers[-1]
            postmodifiers[ob.name].append({
                attr: getattr(lastmod,attr) for attr in dir(lastmod)
                if attr not in
                ('__doc__', '__module__',
                 '__slots__', 'bl_rna', 'rna_type')})
            lastmod.show_render = False
            lastmod.show_viewport = False
    return postmodifiers, postpaths, postmaterials, postnodetrees


def make_caches(
        scene, remote_groups, samples, cache_dir, parent,
        materials, node_groups, instance, proxy,
        postmodifiers, postpaths, postmaterials, postnodetrees,
        rate=1, modifier_setting='PREVIEW', apply_subsurf=False):
    """ Create mesh caches of group objects """

    sample_count = len(samples)
    rigs = get_cache_rigs(
        scene, parent, remote_groups, instance) # XXX should have this
    obs = get_visible_objects(remote_groups, proxy) # XXX should have this

    caches = {}
    for ob in obs:
        temp_ob = ob.copy()
        for modifier in postmodifiers[ob.name]:
            temp_ob.modifiers.remove(temp_ob.modifiers[modifier['name']])
        header, vert_count = make_header(
            temp_ob, scene, rate, sample_count, modifier_setting)
        caches[ob.name] = (
            make_filepath(ob, cache_dir),
            [header],
            vert_count)
        bpy.data.objects.remove(temp_ob)

    for sample in samples:
        scene.frame_set(int(sample[1]), sample[0])
        #update materials and groups with the keyframes
        for material_name in postmaterials:
            material = postmaterials[material_name][0]
            for path in postmaterials[material_name][1]:
                postmaterials[material_name][1][path].append((
                    scene.frame_current,
                    material.node_tree.path_resolve(path)))
        for group_name in postnodetrees:
            node_tree = postnodetrees[group_name][0]
            for path in postnodetrees[group_name][1]:
                postnodetrees[group_name][1][path].append((
                    scene.frame_current,
                    node_tree.path_resolve(path)))
        #now on to our object datablocks
        for ob in obs:
            # First record all our keyframe data
            for path in postpaths[ob.name]:
                postpaths[ob.name][path].append((
                    scene.frame_current,
                    ob.path_resolve(path)))
    # Disable postmodifiers
    driver_restore = {ob.name: [] for ob in obs}
    for ob in obs:
        if postpaths[ob.name] and ob.animation_data:
            for driver in ob.animation_data.drivers:
                if driver.data_path in postpaths[ob.name].keys():
                    driver.mute = True
                    driver_restore[ob.name].append(driver.data_path)
                    driver.update()
            ob.hide = ob.hide_render = False
        for postmodifier in postmodifiers[ob.name]:
            ob.modifiers[postmodifier['name']].show_render = False
            ob.modifiers[postmodifier['name']].show_viewport = False

    #plakatau
    for sample in samples:
        scene.frame_set(int(sample[1]), sample[0])
        for ob in obs:
            # Now cache the frame data
            mesh = ob.to_mesh(scene, True, modifier_setting)
            print(
                ob.name, ' ', len(mesh.vertices),
                ' header', caches[ob.name][2], ' frame: ',
                scene.frame_current)
            if len(mesh.vertices) != caches[ob.name][2]:
                print("Vertex Count mishmach!", ob.name, scene.frame_current)
                raise ArithmeticError # TODO handle with 'sparse' caching
            for vert in mesh.vertices:
                caches[ob.name][1].append(pack(
                    '<fff',
                    float(vert.co[0]), float(vert.co[1]), float(vert.co[2])))
            bpy.data.meshes.remove(mesh)
        # Second Recursively bake the material animation
        if sample[0] <= 0.0001:
            cur_fra = int(sample[1]) - scene.frame_start
            for material in materials:
                remote = find_remote(material)
                generic_driven_to_curves(cur_fra, remote, material)
                if material.node_tree and remote.node_tree:
                    generic_driven_to_curves(
                        cur_fra, remote.node_tree, material.node_tree)
            for node_tree in node_groups:
                remote = find_remote(node_tree)
                generic_driven_to_curves(cur_fra, remote, node_tree)

            for ob, local_ob, bones in rigs:
                bake_rig_transforms(scene, int(sample[1]), ob, local_ob, bones)
    for material in materials:
        yucky_update(material)
        if material.node_tree: yucky_update(material.node_tree)
    for node_tree in node_groups:
        yucky_update(node_tree)
    for ob, local_ob, bones in rigs:
        for driver in local_ob.animation_data.drivers:
            driver.update()
    if not os.path.isdir(abspath(cache_dir)):
        os.makedirs(abspath(cache_dir))
    for ob in obs:
        write_cache_file(caches[ob.name][0], caches[ob.name][1])
        # restore disabled drivers for next round
        for driver_path in driver_restore[ob.name]:
            for driver in ob.animation_data.drivers:
                if driver.data_path == driver_path:
                    driver.mute = False
    ob_caches = {
        find_cached(scene, ob, instance).name: (
            make_filepath(ob, cache_dir),
            postmodifiers[ob.name],
            None if ob.name not in postpaths else postpaths[ob.name]
            )
        for ob in obs}

    return ob_caches


def make_modifier(ob, modifier):
    """ Make a single modifier based on a dictionary of attrs """
    mod = ob.modifiers.new(modifier['name'], modifier['type'])
    for attr in modifier:
        if attr not in ('name', 'type'):
            setattr(mod, attr, modifier[attr])
    return mod


def apply_cache(context, mesh_ob, premodifiers, filepath, postmodifiers):
    """ Apply the mesh cache to the local object """

    # everthing already here is on top and will later stay that way
    top_names = [modifier.name for modifier in mesh_ob.modifiers]

    # add any premodifiers if needed
    for modifier in premodifiers:
        make_modifier(mesh_ob, modifier)

    # mesh cache!!!
    mesh_cache = make_modifier(mesh_ob, {
        'name': 'cache',
        'type': 'MESH_CACHE',
        'cache_format': 'PC2',
        'filepath': filepath,
        'play_mode': 'CUSTOM'})

    # any postmodifiers get added on top
    for modifier in postmodifiers:
        make_modifier(mesh_ob, modifier)

    # now lets get those top names back on top by reordering
    context['object'] = mesh_ob
    for top_mod in top_names:
        while mesh_ob.modifiers.find(top_mod) < len(mesh_ob.modifiers) - 1:
            context['modifier']=mesh_ob.modifiers[top_mod]
            bpy.ops.object.modifier_move_down(context, modifier=top_mod)
    if 'modifier' in context:  context.pop('modifier')
    return mesh_cache


def apply_all_caches(context, objects, ob_caches, parent):
    """ Apply and drive all the caches to the local mesh objects """
    scene = context['scene']
    for local_ob in objects:

        # Add all the mesh caches to our local objects
        mesh_cache = apply_cache(
            context,
            local_ob,
            [],
            ob_caches[local_ob.name][0],
            ob_caches[local_ob.name][1])

        # Clear old drivers; they should be irrelevent due to caching
        local_ob.animation_data_clear()
        local_ob.data.animation_data_clear()


        # Add new single driver to cache frame evaluation
        create_driver(
            local_ob, 'modifiers["{}"].eval_frame'.format(mesh_cache.name), -1,
            parent, DRIVER_PROP)
        # Add postmodifier drivers if needed
        if ob_caches[local_ob.name][2]:
            postpaths = ob_caches[local_ob.name][2]
            for path in postpaths:
                driver = create_driver(local_ob, path, -1, parent, DRIVER_PROP)
                # now let's cram the old keyframe points in
                kp_cos = postpaths[path]
                for co in kp_cos:
                    driver.keyframe_points.add()
                    driver.keyframe_points[-1].co[0] = co[0] - 1
                    driver.keyframe_points[-1].co[1] = co[1]
            yucky_update(local_ob)


def duplify(
        context, scene, proxy, library_object, duplis, cache_data,
        rate, modifier_setting, apply_subsurf):
    """ replace group with it's duplicate """

    instance = cache_data['ID']
    cache_dir = cache_data['cache_dir']
    remote_groups = [empty.dupli_group for empty in duplis]
    obs = get_visible_objects(remote_groups, proxy)
    postmodifiers, postpaths, postmaterials, postnodetrees = collect_data(
        obs, proxy, apply_subsurf)

    # make or get local copies of everything
    parent, objects, extras, materials, node_groups = make_group_copy(
        context, scene, remote_groups, proxy,
        modifier_setting, apply_subsurf, instance, postmodifiers)
    parent['CACHE_INSTANCE'] = cache_data['ID'] # needed for recaching

    # get our local groups
    local_groups = group_object_from_remote(
        library_object, parent, remote_groups, instance)

    # attach parent similar to original rig object
    for prop in (
            'matrix_world', 'parent', 'parent_type',
            'parent_bone', 'matrix_parent_inverse'):
        setattr(parent, prop, getattr(proxy, prop))

    # setup up the parent frame driver for retiming
    for co in (
            (scene.frame_start, 0.0),
            (scene.frame_end, float(scene.frame_end - scene.frame_start))):
        parent[DRIVER_PROP_NAME] = co[1]
        parent.keyframe_insert(DRIVER_PROP, -1, co[0])
    for kp in parent.animation_data.action.fcurves[0].keyframe_points:
        kp.interpolation = 'LINEAR'

    # create and apply the caches
    samples = get_sampled_frames(scene.frame_start, scene.frame_end, rate)
    ob_caches = make_caches(
        scene, remote_groups, samples, cache_dir, parent,
        materials, node_groups, instance, proxy,
        postmodifiers, postpaths, postmaterials, postnodetrees,
        rate, modifier_setting, apply_subsurf)
    apply_all_caches(context, objects, ob_caches, parent)
    return extras # we might need to hide them per user settings


def unkeyed_transforms(item, fcurves, data_path):
    """
    Return unkeyed transforms
    unkeyed = {"data_path": {array_index: value}}

    """
    unkeyed = {}
    default = (0.0, 1.0)
    for transform in (
            'location', 'rotation_quaternion', 'rotation_euler', 'scale'):
        fc_path = data_path.format(transform)
        for idx, value in enumerate(getattr(item, transform)):
            if value != (0.0, 1.0)[
                    transform == 'scale' or
                    (transform == 'rotation_quaternion' and idx == 0)]:
                if any(fc.array_index == idx for fc in fcurves if fc.data_path == fc_path):
                    pass
                else:
                    if fc_path in unkeyed:
                        unkeyed[fc_path][idx] = value
                    else:
                        unkeyed[fc_path] = {idx: value}
    return unkeyed


def reset_transforms(item):
    default = {
        'location': (0, 0, 0), 'rotation_quaternion': (1, 0, 0, 0),
        'rotation_euler':(0, 0, 0), 'scale':(1, 1, 1)}
    for transform in default:
        setattr(item, transform, default[transform])


class CacheGroup(Operator):
    """ Creates a cached local version of an animated group """
    bl_idname = 'object.cache_group'
    bl_label = 'Cache Group'

    rate = IntProperty(default=1, min=1, max=10)
    modifier_settings = EnumProperty(items=[
        tuple(['PREVIEW'])*3, tuple(['RENDER']*3)])
    use_apply_subsurf = BoolProperty(default=False, name='Apply Subsurf')
    use_hide_extras = BoolProperty(default=True, name='Hide Extra Objects')
    use_hide_original = BoolProperty(default=True, name='Hide Original')
    use_stash = BoolProperty(default=True, name='Stash Animation')
    use_only_cache = BoolProperty(default=False, name='Only Cache')

    use_project = BoolProperty(default=True, name='Project')
    cache_dir = StringProperty(
        default='//MESHCACHES', name='directory', subtype='DIR_PATH')

    def __init__(self):
        self.cache_config = CacheConfig(bpy.context) # Can't pass init context
        self.recache = False

    @classmethod
    def poll(cls, context):
        return (
            context.object and
            context.object.type == 'ARMATURE' and
            context.object.animation_data and
            context.object.animation_data.action and
            context.object.data.library and not context.object.library)

    def _is_projectable(self, context):
        blend_path = abspath(context.blend_data.filepath)
        project_path = context.user_preferences.addons[
            __name__].preferences.project_root_full_path
        return not (
            project_path not in blend_path or not blend_path
            or not os.path.isdir(project_path))

    def invoke(self, context, event):
        if not self._is_projectable(context):
            self.properties.use_project = False
        proxy = context.object
        if 'RECACHE_ID' in proxy.keys():
            cache_id = proxy['RECACHE_ID']
            try:
                self.cache_data = [cd for cd in self.cache_config.configstruct['caches'] if cd['ID'] == cache_id][0]
            except IndexError:
                self.report({'ERROR'}, "ID Missing from Stored Caches")
                del(proxy['RECACHE_ID'])
                return {'CANCELLED'}
            if self.cache_data['rig'] != proxy.name:
                self.report({'ERROR'}, "Rig doesn't match stored cache")
                del(proxy['RECACHE_ID'])
                return {'CANCELLED'}
            # set ups
            self.recache = True
            self.properties.use_only_cache = True
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # get some things from context
        scene = context.scene
        old_frame = scene.frame_current
        proxy = context.active_object
        action = proxy.animation_data.action

        # own properties
        rate = self.properties.rate
        modifier_setting = self.properties.modifier_settings
        apply_subsurf = self.properties.use_apply_subsurf
        hide_original = self.properties.use_hide_original
        hide_extras = self.properties.use_hide_extras
        stash = self.properties.use_stash
        only_cache = self.properties.use_only_cache and self.recache

        # figure out library, dupli objects and groups
        library = proxy.data.library
        library_object = [
            libob for libob in bpy.data.objects
            if libob.data == proxy.data and not libob == proxy][0]
        duplis = [
            empty for empty in scene.objects
            if empty.dupli_type == 'GROUP' and
            empty.dupli_group and
            empty.dupli_group.library and
            empty.dupli_group.library == library and
            library_object in empty.dupli_group.objects.values()]
        try:
            rate, modifier_setting, apply_subsurf, hide_original,\
            hide_extras, stash, self.use_project = [
                self.cache_data[a] for a in (
                    'rate', 'modifier_setting', 'apply_subsurf',
                    'hide_original', 'hide_extras', 'stash', 'project')]
            self.cache_data['unkeyed'] = unkeyed_transforms(
                proxy, action.fcurves, '{}')
            print("DATR", self.cache_data)
        except AttributeError:
            print("we didn't have cache data")
            # get/set stored configs, create record, ID and path
            self.cache_data = {
                'rig': proxy.name,
                'action':action.name,
                'project':1 if self.use_project else 0,
                'unkeyed': unkeyed_transforms(proxy, action.fcurves, '{}'),
                'duplis': [dupli.name for dupli in duplis],
                'rate': rate,
                'modifier_setting': modifier_setting,
                'apply_subsurf': apply_subsurf,
                'hide_original': hide_original,
                'hide_extras': hide_extras,
                'stash': stash}
            for bone in proxy.pose.bones:
                base_path = 'pose.bones["{}"].{}'.format(bone.name, '{}')
                self.cache_data['unkeyed'].update(
                    unkeyed_transforms(bone, action.fcurves, base_path))
            self.cache_config.add_cache(self.cache_data)

        # actually do the caching
        context.window.cursor_modal_set('WAIT')

        if only_cache:
            # get back hidden stuff into visibility
            instance = self.cache_data["ID"]
            cached_objects = [
                ob for ob in scene.objects if 'CACHE_INSTANCE' in ob.keys()
                and ob['CACHE_INSTANCE'] == instance]
            for ob in cached_objects:
                ob.hide = ob.hide_render = False
                if "RECACHE_LAYERS" in ob.keys():
                    ob.layers = eval(ob["RECACHE_LAYERS"])
            cached_empties = (ob for ob in cached_objects if ob.type == 'EMPTY')
            for parent in cached_empties:
                if not parent.parent or parent.parent not in cached_objects:
                    break
            cache_dir = self.cache_data['cache_dir']
            remote_groups = [empty.dupli_group for empty in duplis]
            obs = get_visible_objects(remote_groups, proxy)
            samples = get_sampled_frames(
                scene.frame_start, scene.frame_end, rate)
            postmodifiers, postpaths, postmaterials, postnodetrees = collect_data(
                obs, proxy, apply_subsurf)
            make_caches(
                scene, remote_groups, samples, cache_dir, parent,
                [], [], instance, proxy,
                postmodifiers, postpaths, postmaterials, postnodetrees,
                rate, modifier_setting, apply_subsurf)

        else:
            extras = duplify(
                context.copy(),
                scene, proxy, library_object, duplis, self.cache_data,
                rate, modifier_setting, apply_subsurf)
            scene.frame_set(old_frame)
            # hide the extra objects:
            for extra in extras:
                remove_visiblity_drivers(extra)
                extra.hide = extra.hide_render = hide_extras

        context.window.cursor_modal_restore()
        # remove remote version - we just hide for now
        if hide_original:
            for empty in duplis:
                empty['MESHCACHED_DUPLI'] = empty.dupli_type
                empty.dupli_type = 'NONE'
                empty.hide = empty.hide_render = True
            proxy.hide = proxy.hide_render = True
        if stash:
            if 'MESHCACHES' in proxy.animation_data.nla_tracks:
                trak = proxy.animation_data.nla_tracks['MESHCACHES']
            else:
                trak = proxy.animation_data.nla_tracks.new()
                trak.name = 'MESHCACHES'
                trak.mute = True
            stash_frame = 1 + max([0] + [strip.frame_end for strip in trak.strips])
            strip = trak.strips.new(
                name=action.name, start=stash_frame, action=action)
            proxy.animation_data.action = None # unlink after 'stashing'
            reset_transforms(proxy)
            for bone in proxy.pose.bones:
                reset_transforms(bone)
        return {'FINISHED'}

    def draw(self, context):
        props = self.properties
        layout = self.layout
        if self.recache:
            row = layout.row()
            row.prop(props, 'use_only_cache')
        else:
            row = layout.row()
            row.prop(props, 'rate')
            row.prop(props, 'modifier_settings')
            row = layout.row()
            row.prop(props, 'use_apply_subsurf')
            row = layout.row()
            row.prop(props, 'use_hide_extras')
            row.prop(props, 'use_hide_original')
            row = layout.row()
            row.prop(props, 'use_stash')
            row = layout.row()
            if self._is_projectable(context):
                row.prop(props, 'use_project')
            else:
                row.label(text="Not in Project", icon='ERROR')
            if not props.use_project:
                row.prop(props, 'cache_dir')


class ReAnimateCache(Operator):
    """ Re Animate Cached Group """
    bl_idname = 'object.reanimate_cache'
    bl_label = 'ReAnimator'

    @classmethod
    def poll(cls, context):
        return context.object and 'CACHE_INSTANCE' in context.object.keys()

    def execute(self, context):
        selected = context.object
        cache_id = selected['CACHE_INSTANCE']
        for ob in context.scene.objects:
            if 'CACHE_INSTANCE' in ob.keys() and ob['CACHE_INSTANCE'] == cache_id:
                # TODO disable/enable drivers and fcurves instead
                ob.hide_render = ob.hide = True
                ob["RECACHE_LAYERS"] = [layer for layer in ob.layers].__repr__()
                ob.layers = [layer == 19 for layer in range(20)]
        cache_config = CacheConfig(context)
        try:
            cache_data = [cd for cd in cache_config.configstruct['caches'] if cd['ID'] == cache_id][0]
        except IndexError:
            return {'ERROR'}
        proxy = context.scene.objects[cache_data['rig']]
        action = bpy.data.actions[cache_data['action']]
        proxy['RECACHE_ID'] = cache_id
        if not proxy.animation_data:
            proxy.animation_data.create()
        proxy.animation_data.action = action
        if "unkeyed" in cache_data:
            for transform in cache_data["unkeyed"]:
                if not 'bone' in transform:
                    new_value = list(getattr(proxy, transform))
                    for i, value in enumerate(new_value):
                        if str(i) in cache_data["unkeyed"][transform]:
                            new_value[i] = cache_data["unkeyed"][transform][str(i)]
                    setattr(proxy, transform, new_value)
                else:
                    print(transform)
                    bone_transform = transform.split('.')[-1]
                    print(bone_transform)
                    bone_name = transform.replace('pose.bones["','').split('"].')[0]
                    print(bone_name)
                    bone = proxy.pose.bones[bone_name]
                    new_value = list(getattr(bone, bone_transform))
                    for i, value in enumerate(new_value):
                        if str(i) in cache_data["unkeyed"][transform]:
                            new_value[i] = cache_data["unkeyed"][transform][str(i)]
                    setattr(bone, bone_transform, new_value)
        proxy.hide = proxy.hide_render = False
        if "duplis" in cache_data:
            for dupli_name in cache_data["duplis"]:
                try:
                    dupli_ob = context.scene.objects[dupli_name]
                except:
                    pass
                if 'MESHCACHED_DUPLI' in dupli_ob.keys():
                    dupli_ob.dupli_type = dupli_ob['MESHCACHED_DUPLI']
                    dupli_ob.hide = dupli_ob.hide_render = False
        return {'FINISHED'}


def menu_func_export(self, context):
    """ Add the Operator to the Export Menu """
    self.layout.operator(
        CacheGroup.bl_idname, text="Cache Proxied Linked Groups")


def absolute_path(self, value):
    self.project_root_full_path = abspath(self.project_root_full_path)


class MeshcacherPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    project_root_full_path = bpy.props.StringProperty(
        name="Project Path",
        description="Top Directory of Project e.g. /home/bassam/tubeSVN",
        default="", subtype='DIR_PATH')
    cache_root_name = bpy.props.StringProperty(
        name="None SVN Name",
        description="Name of Directory of non SVN tree(caches, etc)",
        default="non_svn", set=absolute_path)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "project_root_full_path")
        layout.prop(self, "cache_root_name")


class CacheConfig(object):
    '''
    Save and Read Configs from current file
    Config Stucture
    {'root_dir': 'root directory', 'caches': [ caches ]}
    cache structure:
    {
    'ID': 'unique cache ID', # an integer
    'rig': 'rig name',
    'action': 'action name',
    'cache_dir': '', path of caches on disk

    'transform': [,,,], # matrix of rig object if not in action
    'bone_transforms': {'bone_name': [,,,]}, # unkeyed, transformed bones

    }
    '''

    def __init__(self, context):
        if CONFIGTEXT in bpy.data.texts:
            self.configtext = bpy.data.texts[CONFIGTEXT]
            self.injest()
            self._create_root_dir(self.configstruct['root_dir']) # XXX needed?
        else:
            self.configstruct = {
                'root_dir':self._set_root_dir(context), 'caches':[]}
            self.configtext = bpy.data.texts.new(name=CONFIGTEXT)
            self.configtext.from_string(json.dumps(self.configstruct))

    def injest(self):
        self.configstruct = json.loads(self.configtext.as_string())

    def add_cache(self, cache_data):
        ''' creates a new cache record, sets path and ID (before caching) '''
        while True:
            cache_id = random.randint(0, MAX_ID)
            if cache_id not in [c['ID'] for c in self.configstruct['caches']]:
                break # XXX slow if close to MAX_ID
        cache_data['ID'] = cache_id
        cache_data['cache_dir'] = bpy.path.relpath(os.path.join(
            abspath(self.configstruct['root_dir']),
            'MESHCACHES',
            str(cache_id)))
        try:
            os.makedirs(abspath(cache_data['cache_dir']))
        except FileExistsError:
            print(cache_data['cache_dir'], ' exists')
        self.configstruct['caches'].append(cache_data)
        self.configtext.from_string(json.dumps(self.configstruct))

    def get_cache(self, cache_id):
        for cache in self.configstruct['caches']:
            if cache['ID'] == cache_id:
                return cache

    def _set_root_dir(self, context):
        '''
        Create the Root of the Caches in non svn based on the current file
        '''
        # get project_root and cache_root_name from preferences
        user_prefs = context.user_preferences
        addon_prefs = user_prefs.addons[__name__].preferences
        project_root_full_path = addon_prefs.project_root_full_path
        cache_root_name = addon_prefs.cache_root_name

        # generate paths as lists of nested folders
        project_root_path = abspath(project_root_full_path).split(SEP)
        cache_root_path = project_root_path[:-1]
        cache_root_path.append(cache_root_name)

        # recreate tree down to current file (.blend to a folder name)
        blend_path = os.path.split(abspath(bpy.context.blend_data.filepath))
        current_path = os.path.join(
            blend_path[0], blend_path[-1].replace('.blend', '')).split(SEP)

        # now we need individual cache paths
        sub_paths = current_path[len(project_root_path):]
        cache_path = cache_root_path + sub_paths

        # create the cache paths
        print(cache_path, SEP)
        cache_path = bpy.path.relpath(SEP.join(cache_path))
        self._create_root_dir(cache_path)
        return cache_path

    def _create_root_dir(self, cache_path):
        try:
            os.makedirs(abspath(cache_path))
        except FileExistsError:
            print(cache_path, ' exists')


def register():
    bpy.utils.register_class(MeshcacherPreferences)
    bpy.utils.register_class(CacheGroup)
    bpy.utils.register_class(ReAnimateCache)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(CacheGroup)
    bpy.utils.unregister_class(ReAnimateCache)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(MeshcacherPreferences)

if __name__ == "__main__":
    register()
