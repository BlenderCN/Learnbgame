# Tag a Rig's bones as legs/body etc. for the autowalker
# Copyright (C) 2012  Bassam Kurdali
#
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

if "bpy" in locals():
    import importlib
    importlib.reload(rig)
else:
    from . import rig

import bpy
from bpy.types import PoseBone, Armature, Object
from mathutils import Vector

# Define Property Groups

class BodyFeet(bpy.types.PropertyGroup):
    '''
    The foot numbers a body depends on
    '''
    foot_number = bpy.props.IntProperty(name="", default=0)


class AutoWalkParam(bpy.types.PropertyGroup):
    '''
    Custom paramaters for autowalk
    '''
    #multiplier: multiplies the slider by the value in anim curves if true,
    #else is just statatically applied to transforms.
    multiplier = bpy.props.BoolProperty(default=True)
    tform = bpy.props.EnumProperty(
        items=[
            ("location", "location", "location", 0),
            ("rotation_euler", "rotation_euler", "rotation_euler", 2),
            ("rotation_quaternion", "rotation_quaternion",
             "rotation_quaternion", 3),
            ("scale", "scale", "scale", 4)],
        name="",
        default="location")  # specify which transform is driven by the param
    #axis flags turn an axis on or off, floats are a mul or value limit
    #(the actual parameter sliders will go from 0 to 1 or -1 to 1
    w = bpy.props.BoolProperty(default=False)
    w_mul = bpy.props.FloatProperty(default=1.0, min=-100.00, max=100.0)
    x = bpy.props.BoolProperty(default=False)
    x_mul = bpy.props.FloatProperty(default=1.0, min=-100.00, max=100.0)
    y = bpy.props.BoolProperty(default=False)
    y_mul = bpy.props.FloatProperty(default=1.0, min=-100.00, max=100.0)
    z = bpy.props.BoolProperty(default=False)
    z_mul = bpy.props.FloatProperty(default=1.0, min=-100.00, max=100.0)

# Define UI lists


class AUTOWALK_UL_Parameters(bpy.types.UIList):
    ''' New School UI List controls'''
    bl_idname = "autowalk.parameters_ui"

    def draw_item(
            self, context, layout, data, item,
            icon, active_data, active_property, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, translate=False, icon_value=icon)
            layout.prop(item, 'tform')
        else:  # 'GRID' layout
            layout.label(text=item.name, translate=False, icon_value=icon)


class BODY_UL_Feet(bpy.types.UIList):
    bl_idname = "body.feet_ui"

    def draw_item(
            self, context, layout, data, item,
            icon, active_data, active_property, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, translate=False, icon_value=icon)
            layout.prop(item, 'foot_number')
        else:  # 'GRID' layout
            layout.label(text=item.name, translate=False, icon_value=icon)

# Update Functions:


def walktype_update(self, context):
    '''
    make sure root, feet, etc. are unique
    '''
    bones = context.active_object.pose.bones
    other_things = [
        bone for bone in bones if bone.walktype == self.walktype and
        not bone == self]
    if self.walktype.startswith('foot'):
        other_feet = other_things
        other_numbers = [bone.leg_number for bone in other_feet]
        for foot in other_feet:
            if foot.leg_number == self.leg_number:
                self.leg_number = 1 + max(other_numbers)
    elif self.walktype in ['root', 'properties', 'stride', 'body']:
        for thing in other_things:
            thing.walktype = 'none'

# Operators:


class AddAutoWalkParam(bpy.types.Operator):
    '''
    Add a parameter to the control
    '''
    bl_idname = "pose.add_autowalk_param"
    bl_label = "Add Autowalk Param"

    def execute(self, context):
        bone = context.active_pose_bone
        a = bone.autowalkparams.add()
        a.name = "Param_" + str(len(bone.autowalkparams))
        bone.active_autowalk_param = len(bone.autowalkparams) - 1
        return {'FINISHED'}


class AddFootDependency(bpy.types.Operator):
    '''
    Add a Foot dependency to a body bone
    '''
    bl_idname = "pose.add_foot_dependency"
    bl_label = "Add Foot Dependency"

    def execute(self, context):
        bone = context.active_pose_bone
        a = bone.foot_depends.add()
        a.name = "foot no:"
        bone.active_foot_depend = len(bone.foot_depends) - 1
        return {'FINISHED'}


class DelAutoWalkParam(bpy.types.Operator):
    """Remove a parameter from the control"""
    bl_idname = "pose.del_autowalk_param"
    bl_label = "Del Autowalk Param"

    def execute(self, context):
        bone = context.active_pose_bone
        bone.autowalkparams.remove(bone.active_autowalk_param)
        if bone.active_autowalk_param == len(bone.autowalkparams) and\
                bone.active_autowalk_param > 0:
            bone.active_autowalk_param -= 1
        return {'FINISHED'}


class DelFootDependency(bpy.types.Operator):
    '''
    remove a foot dependency from a body
    '''
    bl_idname = "pose.del_foot_dependency"
    bl_label = "Delete Foot Dependency"

    def execute(self, context):
        bone = context.active_pose_bone
        bone.foot_depends.remove(bone.active_foot_depend)
        if bone.active_foot_depend == len(bone.foot_depends) and\
                bone.active_foot_depend > 0:
            bone.active_foot_depend -= 1
        return {'FINISHED'}

# The following class is how we read a tagged rig


class Reader():
    """Make the Current Rig Autowalkable"""

    def __init__(self, rig_object):
        # TODO raise error if object is not a rig.
        self.rig_object = rig_object
        self.rig = rig_object.data
        self.bones = self.rig_object.pose.bones
        self._set_params()
        try:
           body = self._find_uniques('body')
        except:
            pass # TODO error
        self.feet = [
            rig.Foot(
                body, [],
                [dep.foot_number for dep in self.bones[body].foot_depends],
                self.rig.up_vector, self.rig.forward_vector),]
        self._fill_feet()
        self._fill_leg_tracks()
        self.root, self.properties, self.stride = [
            self._find_uniques(unique)
            for unique in ('root', 'properties', 'stride')]
        if self.properties:
            for param in self.params:
                bones[self.properties][param] = 0

    def _set_params(self):
        ''' finds and aggregrates all the parameters on all the bones'''
        self.params = {}
        for bone in self.bones:
            for param in bone.autowalkparams:
                # there's probably a better way to introspect this:
                param_list = (
                    a for a in dir(AutoWalkParam) if not a in
                    dir(bpy.types.PropertyGroup) and
                    not a.startswith('__') and
                    not a == 'template_list_controls')                
                param_dict = {
                    pname: getattr(param, pname) for pname in param_list}
                param_dict['bone'] = bone.name
                param_effect = rig.ParameterEffect(**param_dict)
                if param.name in self.params.keys():
                    self.params[param.name].append(param_effect)
                else:
                    self.params[param.name] = [param_effect]

    def _fill_feet(self):
        """finds all the foot bones in the rig"""
        up = self.rig.up_vector
        forward = self.rig.forward_vector
        foot_props = [
            prop for prop in dir(PoseBone) if
            prop.startswith('leg_')] + ["name"]
        feet = [
            {prop: getattr(bone, prop) for prop in foot_props} for
            bone in self.bones if bone.walktype == "foot"]
        feet = sorted(feet, key=lambda foot: foot["leg_number"])
        self.feet.extend(
            rig.Foot(foot['name'], [], [], up, forward) for foot in feet)

    def _fill_leg_tracks(self):
        leg_tracks = [bone for bone in self.bones if bone.walktype == 'leg']
        foot_props = [
            prop for prop in dir(PoseBone) if
            prop.startswith('leg_')]
        for foot_no in self.feet:
            foot = self.bones[foot_no.name]
            foot_no.tracks.extend([
                bone.name for bone in leg_tracks if
                all([getattr(bone, attr) == getattr(foot, attr) for
                    attr in foot_props])])

    def _find_uniques(self, unique):
        """ Get unique bones like properties, root, and stride """
        for bone in self.bones:
            if bone.walktype == unique:
                return bone.name

    def read(self):
        """ Stupid holdover, TODO use inheritence next"""
        rig_description = Rig(
            self.rig,
            self.feet,
            self.params,
            self.properties,
            self.stride,
            self.root)
        return rig_description

# Panels:


class BoneAutoWalk(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Tag Rig for Walking"
    bl_idname = "POSEBONEWALK"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "OROX"

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE' and context.active_pose_bone

    def draw(self, context):
        layout = self.layout

        bone = context.active_pose_bone
        armature = context.active_object.data
        ob = context.active_object
        box = layout.box()
        row = box.row()
        row.label("Bone Settings:")
        # row = box.row()
        # row.prop(armature, "forward_foot", text="Foreward")
        # row.prop(armature, "up_foot", text="Up")
        row = box.row()
        split = row.split(.5)
        col = split.column()
        col.prop(bone, "walktype", text="")
        col = split.column()
        row = col.row()
        if bone.walktype in ("foot", "leg"):

            for prop in dir(bone):
                if prop.startswith("leg_"):
                    row.prop(bone, prop, text="")

        elif bone.walktype in ["root", "body"]:
            row.label("")

        else:
            row.label("")

        row = box.row()
        row.prop(bone, "walkdeform", text="deform curves")
        if bone.walktype in ("body"):
            row = box.row()
            row.label("Body Foot Dependencies:")
            row = box.row()
            split = row.split(1)
            col = split.row()
            row = col.row()
            row.template_list(
                "body.feet_ui", "",
                bone, "foot_depends", bone, "active_foot_depend",
                type='DEFAULT')
            col = row.column()
            sub = col.column(align=True)
            sub.operator("pose.add_foot_dependency", icon='ZOOMIN', text="")
            sub.operator("pose.del_foot_dependency", icon='ZOOMOUT', text="")
        row = layout.row()
        row.label("Auto Walk Custom Parameters:")
        split = layout.split(1)
        col = split.row()
        row = col.row()
        row.template_list(
            "autowalk.parameters_ui", "",
            bone, "autowalkparams", bone, "active_autowalk_param",
            type='DEFAULT')
        col = row.column()
        sub = col.column(align=True)
        sub.operator("pose.add_autowalk_param", icon='ZOOMIN', text="")
        sub.operator("pose.del_autowalk_param", icon='ZOOMOUT', text="")
        # sub.operator("pose.make_autowalk_rig", icon='ANIM_DATA', text="")
        #split = row.split(.5)
        col = split.column()
        try:
            active_param = bone.autowalkparams[bone.active_autowalk_param]
        except:
            pass
        else:
            col.prop(active_param, "name", text="")
            col.prop(
                active_param, "multiplier",
                text="animated" if active_param.multiplier else "static")
            row = col.row(align=True)
            if active_param.tform == "rotation_quaternion":
                row.prop(active_param, "w", text="")
                row.prop(active_param, "w_mul", text="w")
            else:
                row.label("")
            row = col.row(align=True)
            row.prop(active_param, "x", text="")
            row.prop(active_param, "x_mul", text="x")
            row = col.row(align=True)
            row.prop(active_param, "y", text="")
            row.prop(active_param, "y_mul", text="y")
            row = col.row(align=True)
            row.prop(active_param, "z", text="")
            row.prop(active_param, "z_mul", text="z")
        box = layout.box()
        row = box.row()
        row.label("Armature Settings:")
        row = box.row()
        row.prop(armature, "forward_vector", text="Forward")
        row.prop(armature, "up_vector", text="Up")


# Things we defined earlier that need to be registered/unregistered
custom_types = (AutoWalkParam, BodyFeet)
custom_lists = (AUTOWALK_UL_Parameters, BODY_UL_Feet)
custom_operators = (
    AddAutoWalkParam, DelAutoWalkParam,
    AddFootDependency, DelFootDependency)
custom_panels = (BoneAutoWalk,)


def register():
    for custom_type in custom_types:
        bpy.utils.register_class(custom_type)
    for custom_list in custom_lists:
        bpy.utils.register_class(custom_list)
    #custom properties
    PoseBone.autowalkparams = bpy.props.CollectionProperty(type=AutoWalkParam)
    PoseBone.active_autowalk_param = bpy.props.IntProperty(
        name="active_autowalk_param", default=0)
    PoseBone.foot_depends = bpy.props.CollectionProperty(type=BodyFeet)
    PoseBone.active_foot_depend = bpy.props.IntProperty(
        name="active_foot_depend", default=0)
    PoseBone.walkdeform = bpy.props.BoolProperty(default=False)
    PoseBone.walktype = bpy.props.EnumProperty(
        items=[
            ("foot", "foot", "foot", 0), ("root", "root", "root", 1),
            ("none", "none", "none", 2),
            ("body", "body", "body", 3), ("leg", "leg", "leg", 4),
            ("properties", "properties", "properties", 6),
            ("stride", "stride", "stride", 7)],
        name="walktype",
        default="none",
        update=walktype_update)
    PoseBone.leg_number = bpy.props.IntProperty(
        name="leg_number", default=1, min=1, max=100)
    axis_pos = [
        ("X", "X", "X", 0),
        ("Y", "Y", "Y", 1),
        ("Z", "Z", "Z", 2)]
    axis_neg = [
        ("-X", "-X", "-X", 3),
        ("-Y", "-Y", "-Y", 4),
        ("-Z", "-Z", "-Z", 5)]
    axis = axis_pos + axis_neg
    Armature.forward_vector = bpy.props.EnumProperty(
        items=axis,
        name='foward_vector',
        default="-Y")
    Armature.up_vector = bpy.props.EnumProperty(
        items=axis_pos,
        name='up_vector',
        default="Z")
    Armature.forward_foot = bpy.props.EnumProperty(
        items=axis,
        name='forward_foot',
        default="-Y")
    Armature.up_foot = bpy.props.EnumProperty(
        items=axis_pos,
        name='up_foot',
        default="Z")

    for custom_operator in custom_operators:
        bpy.utils.register_class(custom_operator)
    for custom_panel in custom_panels:
        bpy.utils.register_class(custom_panel)


def unregister():
    for custom_panel in custom_panels:
        bpy.utils.unregister_class(custom_panel)
    for custom_operator in custom_operators:
        bpy.utils.unregister_class(custom_operator)
    for custom_prop in (
            PoseBone.autowalkparams, PoseBone.active_autowalk_param,
            PoseBone.foot_depends, PoseBone.active_foot_depend,
            PoseBone.walkdeform, PoseBone.walktype,
            Armature.forward_vector, Armature.up_vector, Armature.forward_foot,
            Armature.up_foot):
        del(custom_prop)
    for custom_list in custom_lists:
        bpy.utils.unregister_class(custom_list)
    for custom_type in custom_types:
        bpy.utils.unregister_class(custom_type)

if __name__ == "__main__":
    register()
