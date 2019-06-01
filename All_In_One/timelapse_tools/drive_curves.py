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
# Copyright 2014 Bassam Kurdali

import bpy
from mathutils import Vector

# ################################ Globals ###################################

# Scalar Keyframe attributes that need to be remapped
remap_keyframe_attrs = ['period']

# ###################### Animation Helper Functions ##########################


def add_driver(ob, data_path, array_index):
    ''' Tries to add a driver with array index, falls back to single prop '''
    try:
        driver = ob.driver_add(data_path, array_index)
    except TypeError:  # Silly but needed
        try:  # Now check if we really have a path
            driver = ob.driver_add(data_path)
        except:
            print("no path {} on object {}".format(data_path, ob.name))
            driver = None
    return driver


def copy_attrs(old, new, remap=lambda x: x, exclusions=[]):
    ''' Genereric copy attributes, use this instead off copy pasta '''
    for attr in (
            attr for attr in dir(old) if not attr.startswith('__')
            and 'rna' not in attr and attr not in exclusions):
        value = getattr(old, attr)
        try:
            if type(value) == Vector:
                setattr(
                    new, attr, Vector((remap(value[0]), value[1])))
            else:
                setattr(new, attr, value)
        except:
            print("Couldn't set attribute ", attr)


def copy_fcurve_modifiers(old_curve, new_curve, remap=lambda x: x):
    ''' Copy function curve modifiers from one curve to another '''
    # Remove all Modifiers:
    while new_curve.modifiers:
        new_curve.modifiers.remove(new_curve.modifiers[-1])
    for modifier in old_curve.modifiers:
        new_modifier = new_curve.modifiers.new(type=modifier.type)
        copy_attrs(modifier, new_modifier, remap)


def copy_keyframes(old_curve, new_curve, remap=lambda x: x):
    ''' Copy all keyframes from one curve to another '''
    while new_curve.keyframe_points:
        new_curve.keyframe_points.remove(new_curve.keyframe_points[-1])
    new_curve.keyframe_points.add(len(old_curve.keyframe_points))

    for old_key, new_key in zip(
            old_curve.keyframe_points, new_curve.keyframe_points):

        for attr in (
                attr for attr in dir(old_key)
                if not attr.startswith('__') and 'rna' not in attr):

            value = getattr(old_key, attr)
            try:
                if type(value) == Vector:
                    setattr(
                        new_key, attr, Vector((remap(value[0]), value[1])))
                elif attr in remap_keyframe_attrs:
                    setattr(new_key, attr, remap(value))
                else:
                    setattr(new_key, attr, value)
            except:
                print("Couldn't set attribute ", attr)
    copy_fcurve_modifiers(old_curve, new_curve)


def fixup_driver(fcurve, driver, remap, active_object, data_path):
    ''' Make all Driver Properties good '''

    driver.driver.type = 'AVERAGE'
    # Remove all Modifiers:
    while driver.modifiers:
        driver.modifiers.remove(driver.modifiers[-1])

    # Setup the variable:
    variable = driver.driver.variables.new()
    variable.type = 'SINGLE_PROP'
    variable.targets[0].id = active_object
    variable.targets[0].data_path = data_path

    # Copy the keyframes:
    copy_keyframes(fcurve, driver, remap)


def add_fcurve(fcurves, data_path, array_index, group):
    ''' Add a new FCurve unless it is already there, in which case, wipe it '''
    try:
        fcurve = fcurves.new(data_path, array_index, group)
    except RuntimeError:
        fcurves = [
            fcurve for fcurve in fcurves if fcurve.data_path == data_path]
        if len(fcurves) == 1:
            fcurve = fcurves[0]
        else:
            fcurve = [
                fcurve for fcurve in fcurves
                if fcurve.array_index == array_index][0]
        while fcurve.keyframe_points:
            fcurve.keyframe_points.remove(fcurve.keyframe_points[-1])
    return fcurve


def curve_to_driver(fcurve, ob, remap, active_object, data_path):
    ''' Convert an anim curve to a driver '''
    # Create the driver:
    driver = add_driver(ob, fcurve.data_path, fcurve.array_index)
    if driver:
        fixup_driver(fcurve, driver, remap, active_object, data_path)


def driver_to_curve(driver, ob, remap, active_object):
    ''' convert a driver back to an anim curve '''
    if not ob.animation_data.action:
        action = bpy.data.actions.new(name="{}_{}".format(ob.name, 'ACTION'))
        ob.animation_data.action = action
    else:
        action = ob.animation_data.action
    fcurve = add_fcurve(
        action.fcurves, driver.data_path, driver.array_index, "")
    copy_keyframes(driver, fcurve, remap)


def curves_to_drivers(ob, remap, active_object, data_path):
    ''' convert all animation curves on an object to drivers '''
    if ob.animation_data and ob.animation_data.action:
        for fcurve in ob.animation_data.action.fcurves:
            curve_to_driver(fcurve, ob, remap, active_object, data_path)


def drivers_to_curves(ob, remap, active_object, data_path):
    ''' convert all drivers in an object to data_path into fcurves '''

    if ob.animation_data:
        for driver in ob.animation_data.drivers:
            for variable in driver.driver.variables:
                if variable.type == 'SINGLE_PROP':
                    for target in variable.targets:
                        if target.data_path == data_path:
                            driver_to_curve(driver, ob, remap, active_object)
                        break  # we only consider the first target
                break  # we only consider the first variable


def make_map(min, max, MIN, MAX):
    ''' return a mapping function to change the timing of driver curves '''

    def temp(value):
        ''' mapping function for timing '''
        return (value - MIN) * (max - min) / (MAX - MIN) + min
    return temp


def get_materials_nodegroups(objects):
    ''' return unique materials and nodegroups from objects '''
    materials = set([
        slot.material for ob in objects for slot in ob.material_slots])
    node_materials = (mat for mat in materials if mat.use_nodes)
    node_groups = set([
        node.node_tree for mat in node_materials
        for node in mat.node_tree.nodes
        if 'node_tree' in dir(node)])
    return (materials, node_groups)


def swap_curves_drivers(prop, context, forward):
    '''
    take a bunch of objects and change their drivers to animation
    based on the min max of the driving property and the scene
    frame start and frame end
    '''

    active = context.active_object
    others = [ob for ob in context.selected_objects if ob is not active]
    pose_bone = context.active_pose_bone
    data_path = 'pose.bones["{}"]["{}"]'.format(pose_bone.name, prop)
    min = pose_bone['_RNA_UI'][prop]['min']
    max = pose_bone['_RNA_UI'][prop]['max']
    action_min = context.scene.frame_start
    action_max = context.scene.frame_end
    if forward:
        converter_function = curves_to_drivers
        remap = make_map(min, max, action_min, action_max)
    else:
        converter_function = drivers_to_curves
        remap = make_map(action_min, action_max, min, max)
    for ob in others:
        converter_function(ob, remap, active, data_path)
        if ob.data:
            converter_function(ob.data, remap, active, data_path)
            if 'shape_keys' in dir(ob.data) and ob.data.shape_keys:
                converter_function(
                    ob.data.shape_keys, remap, active, data_path)
    materials, node_groups = get_materials_nodegroups(others)
    for node_group in node_groups:
        converter_function(node_group, remap, active, data_path)
    for material in materials:
        converter_function(material, remap, active, data_path)
        if material.node_tree:
            converter_function(material.node_tree, remap, active, data_path)


def copy_fcurves(action, data_from, data_to):
    ''' make an identical fcurve for a different property '''
    source_fcurves = (
        fcurve for fcurve in action.fcurves if fcurve.data_path == data_from)
    for fcurve in source_fcurves:
        new_fcurve = add_fcurve(
            action.fcurves, data_to, fcurve.array_index,
            fcurve.group.name if fcurve.group else "")
        copy_keyframes(fcurve, new_fcurve)


def copy_drivers(ob, data_from, data_to):
    ''' make an identical driver for a different property '''
    source_drivers = (
        driver for driver in ob.animation_data.drivers
        if driver.data_path == data_from)
    for driver in source_drivers:
        new_driver = add_driver(ob, data_to, driver.array_index)
        for variable in new_driver.driver.variables: # not trusting the api
            new_driver.driver.variables.remove(variable)
        if new_driver:
            for variable in driver.driver.variables:
                new_variable = new_driver.driver.variables.new()
                for attr in (
                        attr for attr in dir(variable)
                        if not attr.startswith('__') and 'rna' not in attr):

                    try:
                        setattr(new_variable, attr, getattr(variable, attr))
                    except:
                        print("Couldn't set attribute", attr)
                    for idx, target in enumerate(variable.targets):
                        for attr in (
                                attr for attr in dir(target)
                                if not attr.startswith('__')
                                and 'rna' not in attr):
                            try:
                                setattr(
                                    new_variable.targets[idx],
                                    attr, getattr(target, attr))
                            except:
                                print("Couldn't set target attr", attr)
            new_driver.driver.type = driver.driver.type
            copy_keyframes(driver, new_driver)


def undrive_datablock(ob):
    ''' If we've got drivers on something, remove them '''
    if ob.animation_data:
        while ob.animation_data.drivers:
            driver = ob.animation_data.drivers[-1]
            try:
                ob.driver_remove(driver.data_path, driver.array_index)
            except TypeError:
                ob.driver_remove(driver.data_path)


def copy_modifier_visiblity_curves(
        curve_holder, curves, copy_function, old_string, new_string):

    ''' Copy visibility curves for modifiers from viewport <> render '''
    modifier_curves = (
        curve for curve in curves
        if curve.data_path.startswith('modifiers["')
        and curve.data_path.endswith('"]{}'.format(old_string)))
    for curve in modifier_curves:
        copy_function(
            curve_holder, curve.data_path,
            curve.data_path.replace(
                old_string, new_string))


def get_props_from_bone(self, context):
    ''' Returns all propeties in the active pose bone '''
    return [
        tuple([prop] * 3) for prop in context.active_pose_bone.keys()
        if not prop == '_RNA_UI']

# Operator Definitions:


class CopyCurvesDrivers(bpy.types.Operator):
    ''' Transform Animated Objects to Time Driven Ones '''
    bl_idname = "anim.copy_curves_drivers"
    bl_label = "Copy Curves And Drivers"
    driver = bpy.props.EnumProperty(items=get_props_from_bone, name="Driver")
    forward = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1 and\
            context.object.type == 'ARMATURE'

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        swap_curves_drivers(self.driver, context, self.forward)
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self.properties, "driver")


class HideToRender(bpy.types.Operator):
    ''' Copy Hide Animation to Render Animation '''
    bl_idname = "anim.hide_to_render"
    bl_label = "Hide to Render"

    forward = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        second = self.forward
        first = not self.forward
        visibility = ('hide', 'hide_render')
        modifiers = ('.show_viewport', '.show_render')
        for ob in context.selected_objects:
            if ob.animation_data:
                if ob.animation_data.action:
                    action = ob.animation_data.action
                    copy_fcurves(
                        action,
                        visibility[first],
                        visibility[second])
                    copy_modifier_visiblity_curves(
                        action, action.fcurves, copy_fcurves,
                        modifiers[first], modifiers[second])
                copy_drivers(ob, visibility[first], visibility[second])
                copy_modifier_visiblity_curves(
                    ob, ob.animation_data.drivers, copy_drivers,
                    modifiers[first], modifiers[second])
        return {'FINISHED'}


class UnDrive(bpy.types.Operator):
    ''' Remove Drivers from selected '''
    bl_idname = "anim.undrive"
    bl_label = "Undrive"

    @classmethod
    def poll(cls, context):
        return context.selected_objects != None

    def execute(self, context):
        for ob in context.selected_objects:
            undrive_datablock(ob)
            if ob.data:
                undrive_datablock(ob.data)
                if 'shape_keys' in dir(ob.data) and ob.data.shape_keys:
                    undrive_datablock(ob.data.shape_keys)
        materials, node_groups = get_materials_nodegroups(
            context.selected_objects)
        for material in materials:
            undrive_datablock(material.node_tree)
        for node_group in node_groups:
            undrive_datablock(node_group)
        return {'FINISHED'}


class UnCurve(bpy.types.Operator):
    ''' Unlink actions from selected '''
    bl_idname = "anim.uncurve"
    bl_label = "UnCurve"

    @classmethod
    def poll(cls, context):
        return context.selected_objects != None

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.animation_data:
                ob.animation_data.action = None
            if ob.data:
                if ob.data.animation_data:
                    ob.data.animation_data.action = None
                if 'shape_keys' in dir(ob.data) and ob.data.shape_keys and\
                        ob.data.shape_keys.animation_data:
                    ob.data.shape_keys.animation_data.action = None
        materials, node_groups = get_materials_nodegroups(
            context.selected_objects)
        for material in materials:
            if material.animation_data:
                material.animation_data.action = None
            if material.node_tree.animation_data:
                material.node_tree.animation_data.action = None
        for node_group in node_groups:
            if node_group.animation_data:
                node_group.animation_data.action = None
        return {'FINISHED'}

# Registration


def register():
    bpy.utils.register_class(HideToRender)
    bpy.utils.register_class(CopyCurvesDrivers)
    bpy.utils.register_class(UnDrive)
    bpy.utils.register_class(UnCurve)



def unregister():

    bpy.utils.unregister_class(CopyCurvesDrivers)
    bpy.utils.unregister_class(HideToRender)
    bpy.utils.unregister_class(UnDrive)
    bpy.utils.unregister_class(UnCurve)

if __name__ == "__main__":
    register()
