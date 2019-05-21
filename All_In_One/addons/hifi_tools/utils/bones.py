# -*- coding: utf-8 -*-
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
# Created by Matti "Menithal" Lahtinen

import bpy
import re

from math import pi
from mathutils import Quaternion, Matrix, Vector, Euler
from hifi_tools.utils import mesh, helpers

from hifi_tools.armature.skeleton import structure as base_armature


corrected_axis = {
    "GLOBAL_NEG_Z": ["Shoulder", "Arm", "Hand", "Thumb"],
    "GLOBAL_NEG_Y": ["Eye", "Spine", "Neck", "Head", "Leg", "Foot", "Toe", "Hips"]
}

bone_parent_structure = {
    "LeftToe": "LeftFoot",
    "RightToe": "RightFoot",
    "LeftFoot": "LeftLeg",
    "RightFoot": "RightLeg",
    "LeftLeg": "LeftUpLeg",
    "RightLeg": "RightUpLeg",
    "LeftUpLeg": "Hips",
    "RightUpLeg": "Hips",
    "Spine1": "Spine",
    "Spine2": "Spine1",
    "Spine": "Hips",
    "Neck": "Spine2",
    "Head": "Neck",
    "LeftShoulder": "Spine2",
    "RightShoulder": "Spine2",
    "LeftArm": "LeftShoulder",
    "RightArm": "RightShoulder",
    "LeftForeArm": "LeftArm",
    "RightForeArm": "RightArm",
    "LeftHand": "LeftForeArm",
    "RightHand": "RightForeArm",
    "RightEye": "Head",
    "LeftEye": "Head"
}


class RotationTheta():
    theta = 0
    axis = ""
    direction = ""
    connect = False

    def __init__(self, theta, axis, direction, connect):
        self.theta = theta
        self.axis = axis
        self.direction = direction
        self.connect = connect


posterior_chain_correction = {
    'Hips': RotationTheta(0, 'x', 'z', False),
    'Spine': RotationTheta(0, 'x', 'z', True),
    'Spine1': RotationTheta(0, 'x', 'z', True),
    'Spine2': RotationTheta(0, 'x', 'z', True),
    'Neck': RotationTheta(0, 'x',  'z', False),
    'Head': RotationTheta(0, 'x',  'z', True),
    'LeftFoot': RotationTheta(0.673764040485057, 'x', '-y-z-x', True),
    'RightFoot': RotationTheta(0.673764040485057, 'x',  '-y-z-x', True),
    'LeftShoulder': RotationTheta(0, 'x',  'x', False),
    'RightShoulder': RotationTheta(0, 'x',  '-x', False)
}


physical_re = re.compile("^sim")
number_end_re = re.compile(r"(\d+)$")
number_re = re.compile("\\d+")
number_text_re = re.compile(".+(\\d+).*")
blender_copy_re = re.compile("\.001$")
end_re = re.compile("_end$")
mixamorif_prefix = "Mixamorig:"
mixamo_prefix = "mixamo:"

side_front_re = re.compile(r"^(l|r|L|R)")
side_end_re = re.compile(r"(l|r|L|R)$")


class BoneInfo():
    side = ""
    mirror = ""
    name = ""
    mirror_name = ""
    index = None

    def __init__(self, side, mirror, name, mirror_name):
        self.side = side
        self.mirror = mirror
        self.name = name

        m = number_end_re.search(clean_up_bone_name(name))
        if m is not None:
            self.index = m.group(0)
        else:
            self.index = None

        self.mirror_name = mirror_name

    def dump(self):
        if self is not None:
            if self.index is not None:
                return self.side + " - " + self.mirror + " - " + self.name + ' - ' + self.mirror_name + ' - ' + self.index
            return self.side + " - " + self.mirror + " - " + self.name + ' - ' + self.mirror_name

        return None


def nuke_mixamo_prefix(edit_bones):
    print("Show. No. Mercy to mixamo. Remove All as a prelim")

    found = False
    for bone in edit_bones:
        if "mixamo" in bone.name.lower():
            found = True
            bone.name = bone.name.replace(
                mixamorif_prefix, "").replace(mixamo_prefix, "")

    if found:
        print("Mixamo Purge Complete")

    return found


def combine_bones(selected_bones, active_bone, active_object, use_connect=True):
    print("----------------------")
    print("Combining Bones", len(selected_bones),
          "-", active_bone, "-", active_object)
    meshes = mesh.get_mesh_from(active_object.children)
    names_to_combine = []
    active_bone_name = active_bone.name

    bpy.ops.object.mode_set(mode="EDIT")
    for bone in selected_bones:
        if bone.name != active_bone.name:
            print("Now Removing ", bone.name)
            children = list(bone.children)
            names_to_combine.append(bone.name)
            active_object.data.edit_bones.remove(bone)
            # TODO: Removal is broken :(
            for child in children:
                child.use_connect = use_connect

    print("Combining weights.", meshes)
    bpy.ops.object.mode_set(mode="OBJECT")
    for name in names_to_combine:
        if name != active_bone_name:
            for me in meshes:
                print("Mesh: ", me.name)
                bpy.context.scene.objects.active = me

                vertex_group_b = me.vertex_groups.get(name)
                vertex_group_a = me.vertex_groups.get(active_bone_name)

                print("A", vertex_group_a, name)
                print("B", vertex_group_b, active_bone_name)

                if vertex_group_b is not None and vertex_group_a is not None:
                    mesh.mix_weights(active_bone_name, name)
                    me.vertex_groups.remove(me.vertex_groups.get(name))

    bpy.context.scene.objects.active = active_object
    bpy.ops.object.mode_set(mode="EDIT")
    print("Done")


def bone_connection(selected_bones, mode=False):
    for bone in selected_bones:
        bone.use_connect = mode


def scale_helper(obj):
    if obj.dimensions.y > 2.4:
        print("Avatar too large > 2.4m, maybe incorrect? setting height to 1.9m. You can scale avatar inworld, instead")

        bpy.ops.object.mode_set(mode='OBJECT')
        scale = 1.9/obj.dimensions.y
        obj.dimensions = obj.dimensions * scale
        bpy.context.scene.objects.active = obj
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True)

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        bpy.ops.object.mode_set(mode='OBJECT')


def remove_all_actions():
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)


def find_armatures(selection):
    armatures = []
    for selected in selection:
        if selected.type == "ARMATURE":
            armatures.append(selected)

    return armatures


def find_armature(selection):
    for selected in selection:
        if selected.type == "ARMATURE":
            return selected
    return None


def camel_case_split(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return re.sub('(.)(\d+)', r'\1_\2', s2)


def clean_ends(obj):
    if obj.type == "ARMATURE":
        bpy.ops.object.mode_set(mode='EDIT')
        print("Cleaning Armature")
        
        bpy.ops.object.mode_set(mode='OBJECT')


def pin_common_bones(obj, fix_rolls = True):
    # Edit Bones

    bpy.ops.object.mode_set(mode='OBJECT')
    reset_scale_rotation(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = obj.data.edit_bones
    
    print("Pinning Common Bones")
    for ebone in edit_bones:
        corrector = posterior_chain_correction.get(ebone.name)

        if corrector is not None:
            ebone.use_connect = corrector.connect
            print(" - ", ebone.name, " axis",
                  corrector.axis, "dir", corrector.direction)
            y_dir = 1
            if "-y" in corrector.direction:
                y_dir = -1

            x_dir = 1
            if "-x" in corrector.direction:
                x_dir = -1

            z_dir = 1
            if "-z" in corrector.direction:
                z_dir = -1

            if corrector.theta < 0.001:
                d = helpers.bone_length(ebone)

                if corrector.direction == "-y":
                    ebone.tail = Vector([ebone.head.x, ebone.head.y - d, ebone.head.z])
                elif corrector.direction == "y":
                    ebone.tail = Vector([ebone.head.x, ebone.head.y + d, ebone.head.z])

                if corrector.direction == "-x":
                    ebone.tail = Vector([ebone.head.x - d , ebone.head.y, ebone.head.z])
                elif corrector.direction == "x":
                    ebone.tail = Vector([ebone.head.x + d, ebone.head.y, ebone.head.z])
                
                if corrector.direction == "-z":
                    ebone.tail = Vector([ebone.head.x, ebone.head.y, ebone.head.z - d])
                elif corrector.direction == "z":
                    ebone.tail = Vector([ebone.head.x, ebone.head.y, ebone.head.z + d])
                    

            else:
                sides = helpers.get_sides(ebone, corrector.theta)
                h = sides[0]
                a = sides[1]
                o = sides[2]

                print(sides, corrector.axis, corrector.direction)
                if corrector.axis == 'x':
                    ebone.tail = Vector(
                        [ebone.head.x, ebone.head.y + a * y_dir, ebone.head.z + o * z_dir])
                elif corrector.axis == 'y':
                    ebone.tail = Vector(
                        [ebone.head.x + a * x_dir, ebone.head.y, ebone.head.z + o * z_dir])
                elif corrector.axis == 'z':
                    ebone.tail = Vector(
                        [ebone.head.x + a * x_dir, ebone.head.y + o * y_dir, ebone.head.z])

            # H, A, O
        if fix_rolls:
            correct_bone_rotations(ebone)

    correct_scale_rotation(obj, True)

def get_bone_side_and_mirrored(bone_name):
    cleaned_bones = camel_case_split(bone_name)
    cleaned_bones = bone_name.replace(".", "_").replace(" ", "_")
    split = cleaned_bones.split("_")
    length = len(split)
    if length == 1:
        if "left" in split[0].lower():
            return BoneInfo("Left", "Right", bone_name, bone_name.replace("Left", "Right").replace('left', 'Right'))
        elif "right" in split[0].lower():
            return BoneInfo("Right", "Left", bone_name, bone_name.replace("Right", "Left").replace('right', 'Left'))
    else:
        if "left" in split or "Left" in split or "LEFT" in split:
            return BoneInfo("Left", "Right", bone_name, bone_name.replace("Left", "Right").replace('left', 'Right'))
        elif "right" in split or "Right" in split or "RIGHT" in split:
            return BoneInfo("Right", "Left", bone_name, bone_name.replace("Right", "Left").replace('right', 'Left'))
        elif "r" in split:
            index = split.index('r')
            if index == 0:
                return BoneInfo("Right", "Left", bone_name, side_front_re.sub('l', bone_name))
            return BoneInfo("Right", "Left", bone_name, side_end_re.sub('l', bone_name))
        elif "l" in split:
            index = split.index('l')
            if index == 0:
                return BoneInfo("Left", "Right", bone_name,  side_front_re.sub('r', bone_name))
            return BoneInfo("Left", "Right", bone_name, side_end_re.sub('r', bone_name))
        elif "R" in split:
            index = split.index('R')
            if index == 0:
                return BoneInfo("Right", "Left", bone_name, side_front_re.sub('L', bone_name))
            return BoneInfo("Right", "Left", bone_name, side_end_re.sub('L', bone_name))
        elif "L" in split:
            index = split.index('L')
            if index == 0:
                return BoneInfo("Left", "Right", bone_name, side_front_re.sub('R', bone_name))
            return BoneInfo("Left", "Right", bone_name, side_end_re.sub('R', bone_name))

    return None


def clean_up_bone_name(bone_name, remove_clones=True):

    cleaned_bones = camel_case_split(
        bone_name).replace(".", "_").replace(" ", "_")
    split = cleaned_bones.split("_")

    # Remove .001 blender suffic First remove every dot with _ to remove confusion
    # bone_name = end_re.sub("", bone_name)

    if "end" in split:
        end = True
    else:
        end = False

    length = len(split)
    last = None
    new_bone_split = []

    if length == 1:
        new_bone_split.append(bone_name)
    else:
        for idx, val in enumerate(split):
            if val.lower() == "r" or val.lower() == "right":
                new_bone_split.insert(0, "Right")
            elif val.lower() == "l" or val.lower() == "left":
                new_bone_split.insert(0, "Left")
            elif number_text_re.match(val):
                nr = number_text_re.match(val)
                group = nr.groups()
                if end:
                    last = str(int(group[0]) + 1).capitalize()
                else:
                    last = group[0].capitalize()
            elif number_re.match(val):  # value is a number, before the last
                if idx < length:
                    last = val.capitalize()
            else:
                new_bone_split.append(val.capitalize())

    if last is not None:
        if end:
            new_bone_split.append(str(int(last) + 1))
        else:
            new_bone_split.append(last)

    return "".join(new_bone_split)


def set_selected_bones_physical(bones):
    for bone in bones:
        if physical_re.search(bone.name) is None:
            bone.name = "sim" + clean_up_bone_name(bone.name)


def remove_selected_bones_physical(bones):
    for bone in bones:
        if physical_re.search(bone.name) is not None:
            bone.name = physical_re.sub("", bone.name)


def correct_bone(bone, bones):
    if bone.name == "Hips":
        bone.parent = None
    else:
        parent = bone_parent_structure.get(bone.name)
        if parent is not None:
            parent_bone = bones.get(parent)
            if parent_bone is not None:
                bone.parent = parent_bone


def correct_bone_parents(bones):
    for bone in bones:
        correct_bone(bone, bones)


def correct_bone_rotations(ebone):
    
    bpy.ops.object.mode_set(mode="EDIT")
    name = ebone.name

    print("correcting bone rotation for", name)
    if "Eye" in name:
        bone_head = Vector(ebone.head)
        bone_head.z += 0.05
        ebone.tail = bone_head
        ebone.roll = 0
    else:
        axises = corrected_axis.keys()
        correction = None
        found = False
        for axis in axises:
            corrections = corrected_axis.get(axis)
            for correction in corrections:
                if correction in name:
                    bpy.ops.armature.select_all(action="DESELECT")
                    ebone.select = True
                    bpy.ops.armature.calculate_roll(type=axis)
                    print(" pointing towards", axis)

                    bpy.ops.armature.select_all(action="DESELECT")
                    return


def has_armature_as_child(me):
    for child in me.children:
        if child.type == "ARMATURE":
            return True
    return False


def translate_bones(Translator, bones):
    for idx, bone in enumerate(bones):
        bone.hide = False
        bone.hide_select = False

        translated = Translator.translate(bone.name)
        bone.name = translated


def delete_bones(edit_bones, bones_to_remove):
    for removal_bone in bones_to_remove:
        if removal_bone is not None:
            print(" Remove Bone:", removal_bone)
            edit_bones.remove(removal_bone)


def build_armature_structure(data, current_node, parent):

    name = current_node["name"]
    bpy.ops.armature.bone_primitive_add(name=name)

    current_bone_index = data.edit_bones.find(name)
    current_bone = data.edit_bones[current_bone_index]

    current_bone.parent = parent

    current_bone.head = current_node["head"]
    current_bone.tail = current_node["tail"]
    mat = current_node["matrix"]
    current_bone.matrix = mat

    if current_node["connect"]:
        current_bone.use_connect = True

    for child in current_node["children"]:
        build_armature_structure(data, child, current_bone)

    return current_bone


def build_skeleton():
    current_view = bpy.context.area.type

    try:
        bpy.context.area.type = "VIEW_3D"
        # set context to 3D View and set Cursor
        bpy.context.space_data.cursor_location[0] = 0.0
        bpy.context.space_data.cursor_location[1] = 0.0
        bpy.context.space_data.cursor_location[2] = 0.0

        print("----------------------")
        print("Creating Base Armature")
        print("----------------------")
        # Reset mode to Object, just to be sure

        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.object.add(type="ARMATURE", enter_editmode=True)

        current_armature = bpy.context.active_object

        current_armature.name = "HifiArmature"

        for root_bone in base_armature:
            build_armature_structure(current_armature.data, root_bone, None)

        correct_scale_rotation(bpy.context.active_object, True)

    except Exception as detail:
        print("Error", detail)

    finally:
        bpy.context.area.type = current_view


def reset_scale_rotation(obj):
    current_context = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    # set context to 3D View and set Cursor
    bpy.context.space_data.cursor_location[0] = 0.0
    bpy.context.space_data.cursor_location[1] = 0.0
    bpy.context.space_data.cursor_location[2] = 0.0
    bpy.context.area.type = current_context
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

def correct_scale_rotation(obj, rotation):
    reset_scale_rotation(obj)
    obj.scale = Vector((100, 100, 100))
    str_angle = -90 * pi/180
    if rotation:
        obj.rotation_euler = Euler((str_angle, 0, 0), "XYZ")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.scale = Vector((0.01, 0.01, 0.01))
    if rotation:
        obj.rotation_euler = Euler((-str_angle, 0, 0), "XYZ")


def navigate_armature(data, current_rest_node, world_matrix, parent, parent_node):
    name = current_rest_node["name"]
    bone = data.get(name)
    if(bone):
        bone.rotation_mode = "QUATERNION"
        destination_matrix = current_rest_node["matrix_local"].copy()
        inv_destination_matrix = destination_matrix.inverted()
        matrix = bone.matrix
        if parent:
            parent_matrix = parent.matrix.copy()
            parent_inverted = parent_matrix.inverted()
            parent_destination = parent_node["matrix_local"].copy()
        else:
            parent_matrix = Matrix()
            parent_inverted = Matrix()
            parent_destination = Matrix()
        smat = inv_destination_matrix * \
            (parent_destination * (parent_inverted * matrix))
        bone.rotation_quaternion = smat.to_quaternion().inverted()
        for child in current_rest_node["children"]:
            navigate_armature(data, child, world_matrix,
                              bone, current_rest_node)
    else:
        bone = parent
        for child in current_rest_node["children"]:
            navigate_armature(data, child, world_matrix, bone, parent_node)

# Simple function to clear pose, since some dont know where to find it in blender


def clear_pose(selected):
    armature = find_armature(selected)
    if armature is not None:
        mode = "OBJECT"
        if bpy.context.mode != "OBJECT":
            mode = bpy.context.mode
            bpy.ops.object.mode_set(mode="OBJECT")

        print("Deselect all")
        bpy.ops.object.select_all(action="DESELECT")
        print("Selected")

        bpy.context.scene.objects.active = armature
        armature.select = True
        bpy.context.object.data.pose_position = 'POSE'

        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action="DESELECT")

        bpy.ops.object.mode_set(mode=mode)


def retarget_armature(options, selected, selected_only=False):

    armature = find_armature(selected)
    if armature is not None:
        # Center Children First
        print(bpy.context.mode, armature)
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        print("Deselect all")
        bpy.ops.object.select_all(action="DESELECT")
        print("Selected")

        bpy.context.scene.objects.active = armature
        armature.select = True
        bpy.context.object.data.pose_position = 'POSE'

        # Make sure to reset the bones first.
        bpy.ops.object.transform_apply(
            location=False, rotation=True, scale=True)
        print("Selecting Bones")

        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action="DESELECT")

        print("---")

        # Now lets do the repose to rest
        world_matrix = armature.matrix_world
        bones = armature.pose.bones

        for bone in base_armature:
            print("Iterating Bones", bone["name"])
            navigate_armature(bones, bone, world_matrix, None, None)

        print("Moving Next")
        # Then apply everything
        if options["apply"]:

            print("Applying Scale")
            if bpy.context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")

            print("Correcting Scale and Rotations")
            correct_scale_rotation(armature, True)

            print(" Correcting child rotations and scale")
            for child in armature.children:
                if selected_only is False or child.select:
                    correct_scale_rotation(child, False)

            bpy.context.scene.objects.active = armature

        armature.select = True

        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        print("Done")
    else:
        # Judas proofing:
        print("No Armature, select, throw an exception")
        raise Exception("You must have an armature to continue")
