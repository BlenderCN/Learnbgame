# Orox uses Animated or MoCap walkcycles to generate footstep driven walks
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
import bpy
from mathutils import Vector
from pprint import pprint, pformat


class BodyFeet(bpy.types.PropertyGroup):
    '''
    The foot numbers a body depends on
    '''
    foot_number = bpy.props.IntProperty(name="", default=0)


class ActionList(bpy.types.PropertyGroup):
    '''
    List of actions used for reference, could be later expanded
    '''
    action_name = bpy.props.StringProperty()


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

# there's probably a better way to introspect this:
param_list = [
    a for a in dir(AutoWalkParam) if not a in dir(bpy.types.PropertyGroup) and
    not a.startswith('__') and not a == 'template_list_controls']


class ACTION_UL_List(bpy.types.UIList):
    ''' Action List UI '''
    bl_idname = "autowalk.actions_ui"

    def draw_item(
            self, context, layout, data, item,
            icon, active_data, active_property, index):
        layout.label(text=item.action_name, translate=False, icon_value=icon)


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
    make sure root, feet, targets, etc. are unique
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
    elif self.walktype in ['root']:
        for thing in other_things:
            thing.walktype = 'none'


# Operators:


def scene_actions(self, context):
    '''
    dynamic list of actions from bpy.data
    '''
    return [(act.name, act.name, act.name) for act in bpy.data.actions]


class AddReferenceAction(bpy.types.Operator):
    '''
    Add a reference action to the autorig
    '''
    bl_idname = "armature.add_reference_action"
    bl_label = "Add Autowalk Reference Action"

    actions = bpy.props.EnumProperty(items=scene_actions)

    def execute(self, context):
        action = self.properties.actions
        armature = context.active_object.data

        a = armature.action_list.add()
        print(action)
        a.name = a.action_name = action
        return {'FINISHED'}


class DelReferenceAction(bpy.types.Operator):
    '''
    Add a reference action to the autorig
    '''
    bl_idname = "armature.del_reference_action"
    bl_label = "Autowalk Reference Action"

    def execute(self, context):
        armature = context.active_object.data
        armature.action_list.remove(armature.active_action_list)
        if armature.active_action_list == len(armature.action_list) and\
                armature.active_action_list > 0:
            armature.active_action_list -= 1
        return {'FINISHED'}


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


class GenerateAutoWalkRig(bpy.types.Operator):
    """Make the Current Rig Autowalkable"""
    bl_idname = "pose.make_autowalk_rig"
    bl_label = "Make autowalk Rig"

    def get_params(self, bones):
        ''' finds and aggregrates all the paramters on all the bones'''
        params = {}
        for bone in bones:
            for param in bone.autowalkparams:
                param_dict = {
                    pname: getattr(param, pname) for pname in param_list}
                param_dict['bone'] = bone.name
                if param.name in params.keys():
                    params[param.name].append(param_dict)
                else:
                    params[param.name] = [param_dict]
        return params

    def make_track(self, context, walktype):
        bpy.ops.object.editmode_toggle()
        new_bone = "automin_" + walktype
        bpy.ops.armature.bone_primitive_add(name=new_bone)
        bpy.ops.object.editmode_toggle()  # posemode for tagging new bones.
        bones = context.active_object.pose.bones
        body_name = [bone.name for bone in bones if bone.walktype == "body"][0]
        new_track = bones[new_bone]
        new_track.walktype = walktype
        bpy.ops.object.editmode_toggle()
        edit_bones = context.active_object.data.edit_bones
        # zero our new bone's location and align it to the rig.
        edit_track = edit_bones[new_bone]
        edit_track.head = Vector((0, 0, 0))
        edit_track.tail = Vector((0, 1, 0))
        edit_track.roll = 0

        if walktype == 'root':
            # find the body:
            body = edit_bones[body_name]
            for attr in ('head', 'tail', 'roll'):
                setattr(edit_track, attr, getattr(body, attr))
        bpy.ops.object.editmode_toggle()
        if context.mode != 'POSE':
            bpy.ops.object.posemode_toggle()
        return new_track

    def get_track(self, bones, context, walktype):
        ''' returns the bone with the root (aka torso root) '''
        try:
            track = [bone for bone in bones if bone.walktype == walktype][0]
        except:
            track = self.make_track(context, walktype)
        return track.name

    def get_feet(self, bones):
        """finds all the foot bones in the rig"""
        foot_props = [
            prop for prop in dir(bpy.types.PoseBone) if
            prop.startswith('leg_')] + ["name"]
        feet = [
            {prop: getattr(bone, prop) for prop in foot_props} for
            bone in bones if bone.walktype == "foot"]

        feet = sorted(feet, key=lambda foot: foot["leg_number"])
        for foot in feet:
            foot['deps'] = []

        return feet

    def make_foottars(self, context, feet, root):
        """finds or makes foot target bones needed by the autowalker"""
        bpy.ops.object.editmode_toggle()  # must be in editmode to add bones
        bones = context.active_object.data.edit_bones
        new_bones = {}  # holds information about the newbones we need to add
        #eg {'bonename': {'walktype':'foot_target','leg_number':1}}
        for foot_no in feet:
            foot = bones[foot_no["name"]]  # get the footbone
            if not "target" in foot_no:  # add a target if it doesn't exist
                new_bone = "foot_tar_{}".format(foot_no['leg_number'])
                bpy.ops.armature.bone_primitive_add(name=new_bone)
                new_bones[new_bone] = {
                    "walktype": "foot_target",
                    "leg_number": foot_no["leg_number"]}
                foot_no["target"] = new_bone
        bpy.ops.object.editmode_toggle()  # posemode for tagging new bones.
        bones = context.active_object.pose.bones
        for bone in new_bones:
            for attr in new_bones[bone]:
                setattr(bones[bone], attr, new_bones[bone][attr])
        bpy.ops.object.editmode_toggle()
        bones = context.active_object.data.edit_bones  # editmode move/parent
        for bone in new_bones:
            foot_idx = [
                foot for foot in feet if
                foot['leg_number'] == new_bones[bone]['leg_number']][0]
            foot = bones[foot_idx["name"]]  # now get it's foot.
            for attr in ("head", "tail", "roll"):  # foot to target copy
                setattr(bones[bone], attr, getattr(foot, attr))
            if new_bones[bone]["walktype"] == "foot_target":
                bones[bone].parent = bones[root]
        bpy.ops.object.editmode_toggle()  # bang out of editmode.
        if context.mode != 'POSE':
            bpy.ops.object.posemode_toggle()

    def get_foot_tars(self, context, bones, feet, root):
        ''' This actually makes the tars if they don't exist '''
        missing = False  # assume we don't need to make any
        foot_props = [
            prop for prop in dir(bpy.types.PoseBone) if
            prop.startswith('leg_')]
        for foot_no in feet:
            foot = bones[foot_no["name"]]
            foottars = {
                bone.walktype: bone for bone in bones if
                all([getattr(bone, attr) == getattr(foot, attr) for
                    attr in foot_props])}
            try:
                foot_no["target"] = foottars['foot_target'].name
            except:
                print('missing target ', foot_no)
                missing = True
            if missing:
                print("making more")
                self.make_foottars(context, feet, root)

    def get_leg_tracks(self, bones, feet):
        leg_tracks = [bone for bone in bones if bone.walktype == 'leg']
        foot_props = [
            prop for prop in dir(bpy.types.PoseBone) if
            prop.startswith('leg_')]
        for foot_no in feet:
            foot = bones[foot_no["name"]]
            foot_no['tracks'] = [
                bone.name for bone in leg_tracks if
                all([getattr(bone, attr) == getattr(foot, attr) for
                    attr in foot_props])]

    def execute(self, context):
        bones = context.active_object.pose.bones
        params = self.get_params(bones)
        armature = context.active_object.data
        active = context.active_object
        group = bpy.data.groups[active.autowalk_group]
        objects = [ob.name for ob in group.objects]

        try:
            body = [bone.name for bone in bones if bone.walktype == 'body'][0]
        except:
            self.report({"ERROR"}, "Missing Body!")
            return {'CANCELLED'}

        root = self.get_track(bones, context, 'root')
        properties = self.get_track(bones, context, 'properties')
        feet = self.get_feet(bones)
        action_list = [action.action_name for action in armature.action_list]

        if not feet:
            self.report({"ERROR"}, "Missing Feet!")
            return {'CANCELLED'}
        self.get_foot_tars(context, bones, feet, root)
        self.get_leg_tracks(bones, feet)
        for foot in feet:
            foot.pop('leg_number')
            foot['up'] = armature.up_foot
            foot['forward'] = armature.forward_foot
        main_foot = {
            "target": root,
            "name": body,
            "tracks": [],
            "deps": [dep.foot_number for dep in bones[body].foot_depends],
            "up": armature.up_vector,
            "forward": armature.forward_vector}
        feet = [main_foot] + feet

        report = [{
            "rig": context.active_object.data.name,
            "objects": objects,
            "group": group.name,
            "properties": properties,
            "feet": feet,
            "params": params,
            "actions": action_list}]

        filename = "auto_rig_desc.py"
        try:
            textblob = bpy.data.texts[filename]
        except:
            textblob = bpy.data.texts.new(name=filename)

        textblob.from_string("{} = {}".format(
            "rig_params",
            pformat(report)))
        # tag the rig properties bone with all the collected params and props.
        for param in params:
            bones[properties][param] = 0
        return {'FINISHED'}

# Panels:


class BoneAutoWalk(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Define Bones"
    bl_idname = "POSEBOENE_PT_hello"
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
        row = layout.row()
        row.prop(armature, "forward_foot", text="Foreward")
        row.prop(armature, "up_foot", text="Up")
        row = layout.row()
        split = row.split(.5)
        col = split.column()
        col.prop(bone, "walktype", text="")
        col = split.column()
        row = col.row()
        if bone.walktype in ("foot", "foot_target", "leg"):

            for prop in dir(bone):
                if prop.startswith("leg_"):
                    row.prop(bone, prop, text="")

        elif bone.walktype in ["root", "body"]:
            row.label("")

        else:
            row.label("")

        row = layout.row()
        row.prop(bone, "walkdeform", text="deform curves")
        if bone.walktype in ("body"):
            row = layout.row()
            row.label("Body Foot Dependencies:")
            row = layout.row()
            split = row.split(.6)
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
        split = layout.split(.6)
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
        sub.operator("pose.make_autowalk_rig", icon='ANIM_DATA', text="")
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


class ArmatureAutoWalk(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Define Rig"
    bl_idname = "ARMATURE_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "OROX"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return context.mode == 'POSE' and active.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        armature = context.active_object.data
        row = layout.row()
        row.prop(context.active_object, "autowalk_group", text="group")
        row = layout.row()
        row.prop(armature, "forward_vector", text="Forward")
        row.prop(armature, "up_vector", text="Up")
        row = layout.row()
        row.label("Auto Walk Reference Actions:")
        row = layout.row()
        row.template_list(
            "autowalk.actions_ui", "",
            armature, "action_list", armature, "active_action_list",
            type='DEFAULT')
        col = row.column()
        sub = col.column(align=True)
        sub.operator_menu_enum(
            "armature.add_reference_action", "actions",
            icon='ZOOMIN', text="")
        sub.operator(
            "armature.del_reference_action",
            icon='ZOOMOUT', text="")


def register():
    #custom types:
    bpy.utils.register_class(AutoWalkParam)
    bpy.utils.register_class(BodyFeet)
    bpy.utils.register_class(ActionList)
    #UI List Classes:
    bpy.utils.register_class(AUTOWALK_UL_Parameters)
    bpy.utils.register_class(BODY_UL_Feet)
    bpy.utils.register_class(ACTION_UL_List)
    #custom properties
    bpy.types.PoseBone.autowalkparams = bpy.props.CollectionProperty(
        type=AutoWalkParam)
    bpy.types.PoseBone.active_autowalk_param = bpy.props.IntProperty(
        name="active_autowalk_param", default=0)
    bpy.types.PoseBone.foot_depends = bpy.props.CollectionProperty(
        type=BodyFeet)
    bpy.types.PoseBone.active_foot_depend = bpy.props.IntProperty(
        name="active_foot_depend", default=0)
    bpy.types.PoseBone.walkdeform = bpy.props.BoolProperty(default=False)
    bpy.types.PoseBone.walktype = bpy.props.EnumProperty(
        items=[
            ("foot", "foot", "foot", 0), ("root", "root", "root", 1),
            ("none", "none", "none", 2),
            ("body", "body", "body", 3), ("leg", "leg", "leg", 4),
            ("foot_target", "foot_target", "foot_target", 5),
            ("properties", "properties", "properties", 6)],
        name="walktype",
        default="none",
        update=walktype_update)

    bpy.types.PoseBone.leg_number = bpy.props.IntProperty(
        name="leg_number", default=1, min=1, max=100)

    def get_groups(self, context):
        return [tuple([group.name]*3) for group in bpy.data.groups if self.name in group.objects]
    bpy.types.Object.autowalk_group = bpy.props.EnumProperty(
        items=get_groups)
    bpy.types.Armature.action_list = bpy.props.CollectionProperty(
        type=ActionList)
    bpy.types.Armature.active_action_list = bpy.props.IntProperty(
        name="action_action_list", default=0)
    axis_pos = [("X", "X", "X", 0), ("Y", "Y", "Y", 1), ("Z", "Z", "Z", 2)]
    axis_neg = [
        ("-X", "-X", "-X", 3), ("-Y", "-Y", "-Y", 4), ("-Z", "-Z", "-Z", 5)]
    axis = axis_pos + axis_neg
    bpy.types.Armature.forward_vector = bpy.props.EnumProperty(
        items=axis,
        name='foward_vector',
        default="-Y")
    bpy.types.Armature.up_vector = bpy.props.EnumProperty(
        items=axis_pos,
        name='up_vector',
        default="Z")
    bpy.types.Armature.forward_foot = bpy.props.EnumProperty(
        items=axis,
        name='forward_foot',
        default="-Y")
    bpy.types.Armature.up_foot = bpy.props.EnumProperty(
        items=axis_pos,
        name='up_foot',
        default="Z")

    # register some operators:
    bpy.utils.register_class(AddAutoWalkParam)
    bpy.utils.register_class(DelAutoWalkParam)
    bpy.utils.register_class(AddFootDependency)
    bpy.utils.register_class(DelFootDependency)
    bpy.utils.register_class(GenerateAutoWalkRig)
    bpy.utils.register_class(AddReferenceAction)
    bpy.utils.register_class(DelReferenceAction)

    # finally autowalk panels:
    bpy.utils.register_class(BoneAutoWalk)
    bpy.utils.register_class(ArmatureAutoWalk)


def unregister():
    # remove panels:
    bpy.utils.unregister_class(BoneAutoWalk)
    bpy.utils.unregister_class(ArmatureAutoWalk)
    # remove operators:
    bpy.utils.unregister_class(AddAutoWalkParam)
    bpy.utils.unregister_class(DelAutoWalkParam)
    bpy.utils.unregister_class(AddFootDependency)
    bpy.utils.unregister_class(DelFootDependency)
    bpy.utils.register_class(AddReferenceAction)
    bpy.utils.register_class(DelReferenceAction)
    bpy.utils.unregister_class(GenerateAutoWalkRig)
    # remove properties:
    del(bpy.types.PoseBone.autowalkparams)
    del(bpy.types.PoseBone.active_autowalk_param)
    del(bpy.types.PoseBone.foot_depends)
    del(bpy.types.PoseBone.active_foot_depend)
    del(bpy.types.PoseBone.walkdeform)
    del(bpy.types.PoseBone.walktype)
    del(bpy.types.Armature.action_list)
    del(bpy.types.Armature.active_action_list)
    del(bpy.types.Armature.forward_vector)
    del(bpy.types.Armature.up_vector)
    del(bpy.types.Armature.forward_foot)
    del(bpy.types.Armature.up_foot)
    del(bpy.types.Object.autowalk_group)
    # remove UI List Classes:
    bpy.utils.unregister_class(AUTOWALK_UL_Parameters)
    bpy.utils.unregister_class(BODY_UL_Feet)
    bpy.utils.unregister_class(ACTION_UL_List)
    # remove custom types:
    bpy.utils.unregister_class(AutoWalkParam)
    bpy.utils.unregister_class(BodyFeet)
    bpy.utils.unregister_class(ActionList)

if __name__ == "__main__":
    register()
