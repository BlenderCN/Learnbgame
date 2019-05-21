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
# Created by Matti 'Menithal' Lahtinen
# 'MDD Converter Commissioned by High Fidelity

import csv
import bpy
import re
import os
import copy
from mathutils import Vector
from hifi_tools.utils import materials, mesh, bones
# This part is Based on powroupi the MMD Translation script combined with a Hogarth-MMD Translation csv that has been modified to select names as close as possible
# This instead uses a predefined list that is Hifi Compatable.

# Clone of shorthand to full
jp_half_to_full_tuples = (
    ('ｳﾞ', 'ヴ'), ('ｶﾞ', 'ガ'), ('ｷﾞ', 'ギ'), ('ｸﾞ', 'グ'), ('ｹﾞ', 'ゲ'),
    ('ｺﾞ', 'ゴ'), ('ｻﾞ', 'ザ'), ('ｼﾞ', 'ジ'), ('ｽﾞ', 'ズ'), ('ｾﾞ', 'ゼ'),
    ('ｿﾞ', 'ゾ'), ('ﾀﾞ', 'ダ'), ('ﾁﾞ', 'ヂ'), ('ﾂﾞ', 'ヅ'), ('ﾃﾞ', 'デ'),
    ('ﾄﾞ', 'ド'), ('ﾊﾞ', 'バ'), ('ﾊﾟ', 'パ'), ('ﾋﾞ', 'ビ'), ('ﾋﾟ', 'ピ'),
    ('ﾌﾞ', 'ブ'), ('ﾌﾟ', 'プ'), ('ﾍﾞ', 'ベ'), ('ﾍﾟ', 'ペ'), ('ﾎﾞ', 'ボ'),
    ('ﾎﾟ', 'ポ'), ('｡', '。'), ('｢', '「'), ('｣', '」'), ('､', '、'),
    ('･', '・'), ('ｦ', 'ヲ'), ('ｧ', 'ァ'), ('ｨ', 'ィ'), ('ｩ', 'ゥ'),
    ('ｪ', 'ェ'), ('ｫ', 'ォ'), ('ｬ', 'ャ'), ('ｭ', 'ュ'), ('ｮ', 'ョ'),
    ('ｯ', 'ッ'), ('ｰ', 'ー'), ('ｱ', 'ア'), ('ｲ', 'イ'), ('ｳ', 'ウ'),
    ('ｴ', 'エ'), ('ｵ', 'オ'), ('ｶ', 'カ'), ('ｷ', 'キ'), ('ｸ', 'ク'),
    ('ｹ', 'ケ'), ('ｺ', 'コ'), ('ｻ', 'サ'), ('ｼ', 'シ'), ('ｽ', 'ス'),
    ('ｾ', 'セ'), ('ｿ', 'ソ'), ('ﾀ', 'タ'), ('ﾁ', 'チ'), ('ﾂ', 'ツ'),
    ('ﾃ', 'テ'), ('ﾄ', 'ト'), ('ﾅ', 'ナ'), ('ﾆ', 'ニ'), ('ﾇ', 'ヌ'),
    ('ﾈ', 'ネ'), ('ﾉ', 'ノ'), ('ﾊ', 'ハ'), ('ﾋ', 'ヒ'), ('ﾌ', 'フ'),
    ('ﾍ', 'ヘ'), ('ﾎ', 'ホ'), ('ﾏ', 'マ'), ('ﾐ', 'ミ'), ('ﾑ', 'ム'),
    ('ﾒ', 'メ'), ('ﾓ', 'モ'), ('ﾔ', 'ヤ'), ('ﾕ', 'ユ'), ('ﾖ', 'ヨ'),
    ('ﾗ', 'ラ'), ('ﾘ', 'リ'), ('ﾙ', 'ル'), ('ﾚ', 'レ'), ('ﾛ', 'ロ'),
    ('ﾜ', 'ワ'), ('ﾝ', 'ン'),
)


bones_to_remove = [
    "Center",
    "Groove",
    "CenterTop",
    "ParentNode",
    "Eyes",
    "Dummy",
    "Root",
    "Base",
    "ControlNode",
    "Waist"
]

contains_to_remove = [
    "_dummy_",
    "_shadow_",
    "IK",
    "Dummy",
    "Tip",
    "Twist",
    "ShoulderP",
    "ShoulderC",
    "LegD",
    "FootD",
    "mmd_edge",
    "mmd_vertex",
    "Node",
    "Center",
    "Control",
    "Return"
]

# Simplified Translator based on powroupi MMDTranslation
class MMDTranslator:
    def __init__(self):
        self.translation_dict = []
        split_pattern = re.compile(",\s")
        remove_end = re.compile(",$")

        try:
            local = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(local, 'mmd_hifi_dict.csv')
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                try:
                    stream = csv.reader(
                        f, delimiter=',', quotechar='"', skipinitialspace=True)
                    self.translation_dict = [tuple(row)
                                             for row in stream if len(row) >= 2]
                finally:
                    f.close()
                    print("Translation File Loaded")
        except FileNotFoundError:  # Probably just developing then
            print("Reading Editor file: This only should show when developing")
            stream = bpy.data.texts["mmd_hifi_dict.csv"].lines
            for line in stream:
                body = line.body
                body = body.replace('"', '')
                body = re.sub(remove_end, "", body)

                tup = split_pattern.split(body)
                self.translation_dict.append(tuple(tup))

            print("Done Reading List")
            print("|||||||||||||||||||||||||||||||||||||||||")

    @staticmethod
    def replace_from_tuples(name, tuples):
        for pair in tuples:
            if pair[0] in name:
                updated_name = name.replace(pair[0], pair[1])
                name = updated_name
        return name

    def half_to_full(self, name):
        return self.replace_from_tuples(name, jp_half_to_full_tuples)

    def is_translated(self, name):
        try:
            name.encode('ascii', errors='strict')
        except UnicodeEncodeError:
            return False
        return True

    def translate(self, name):
        if not self.is_translated(name):
            # First Updates short hand to full
            full_name = self.half_to_full(name)

            translated_name = self.replace_from_tuples(
                full_name, self.translation_dict)

            return purge_string(translated_name)

        return name


def purge_string(string):
    try:
        str_bytes = os.fsencode(string)
        return str_bytes.decode("utf-8", "replace")
    except UnicodeEncodeError:
        print("Could not purge string", string)
        return string


def delete_self_and_children(me):

    print(bpy.context.mode)
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    me.hide = False
    me.hide_select = False
    me.select = True
    bpy.context.scene.objects.active = me

    for child in me.children:
        child.hide = False
        child.hide_select = False
        child.select = True

    bpy.ops.object.delete()


#####################################################
# Armature Fixes:                                   #
#####################################################

finger_name_correction = {
    "RightThumb0": "RightHandThumb1",
    "RightThumb1": "RightHandThumb2",
    "RightThumb2": "RightHandThumb3",
    "LeftThumb0": "LeftHandThumb1",
    "LeftThumb1": "LeftHandThumb2",
    "LeftThumb2": "LeftHandThumb3",
    "IndexFinger": "HandIndex",
    "MiddleFinger": "HandMiddle",
    "RingFinger": "HandRing",
    "LittleFinger": "HandPinky"
}


def translate_bones(Translator, bones):

    finger_keys = finger_name_correction.keys()
    hand_re = re.compile("(?:(?:Left)|(?:Right))Hand[A-Za-z]+(\d)")

    for idx, bone in enumerate(bones):
        bone.hide = False
        bone.hide_select = False

        translated = Translator.translate(bone.name)
        bone.name = translated

        if "Finger" in bone.name or "Thumb" in bone.name:
            newname = bone.name

            for finger in finger_keys:
                newname = newname.replace(
                    finger, finger_name_correction.get(finger))

            m = hand_re.search(newname)
            if m is not None:
                number = m.group(1)
                bone.name = newname.replace(number, str(int(number)+1))


def has_removable(val):
    for word in contains_to_remove:
        if word in val:
            return True
    return False


def clean_up_bones(obj):
    _to_remove = []

    pose_bones = obj.pose.bones

    bpy.ops.object.mode_set(mode='EDIT')
    updated_context = bpy.data.objects[obj.name]
    edit_bones = updated_context.data.edit_bones
    print("Cleaning up Bones")
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in obj.data.bones:
        pose_bone = pose_bones.get(bone.name)

        # Oddly needed to get the edit bone reference
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bone = edit_bones.get(bone.name)

        print(" Bone ", bone.name)

        if pose_bone is not None and edit_bone is not None:
            if (has_removable(bone.name) or bone.name in bones_to_remove or (bone.name != "Hips" and bone.parent is None)) and (bone.name != "HeadTop" and edit_bone not in _to_remove):
                _to_remove.append(edit_bone)
                print(" - Added to removal list", bone.name)
            elif (bone.parent is not None and bone.parent in _to_remove):
                _to_remove.append(edit_bone)
                print(
                    " - Added to removal list because parent is in deletion", bone.name)
            else:

                print(" + Setting Pose Mode for", pose_bone)

                print(" - Removing Constraints from", pose_bone.name)
                for constraint in pose_bone.constraints:
                    pose_bone.constraints.remove(constraint)

                print(" # Check Rotations")
                bones.correct_bone_rotations(edit_bone)

    print(" Cleaning ", len(_to_remove), " unusable bones")

    for removal_bone in _to_remove:
        if removal_bone is not None:
            print(" Remove Bone:", removal_bone)
            edit_bones.remove(removal_bone)

    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = updated_context.data.edit_bones

    print("Manipulating", obj.name)

    if edit_bones.get("Spine1") is None and edit_bones.get("Spine2") is None:
        print("Couldnt Detect Spine1, Creating Out of Spine2")
        spine = edit_bones.get("Spine")
        spine.select = True
        bpy.ops.armature.subdivide()
        spine.name = "Spine"
        spine.select = False
        spine = edit_bones.get("Spine.001")
        spine.select = True
        spine.name = "Spine2"

    if edit_bones.get("Spine1") is None:
        print("Couldnt Detect Spine1, Creating Out of Spine2")
        spine = edit_bones.get("Spine2")
        spine.select = True
        bpy.ops.armature.subdivide()
        spine.name = "Spine1"
        spine = edit_bones.get("Spine2.001")
        spine.name = "Spine2"
        spine.select = False

    edit_bones = updated_context.data.edit_bones
    bones.correct_bone_parents(edit_bones)

    bpy.ops.object.mode_set(mode='OBJECT')

    return _to_remove


def convert_bones(Translator, obj):
    bones = obj.data.bones

    print("Translating ", len(bones), " bones")
    # Translate Bones first. Have to do separate from the next loop
    translate_bones(Translator, bones)
    print("Cleaning Up Bones")
    clean_up_bones(obj)

#####################################################
# Mesh Fixes:                                       #
#####################################################


def translate_shape_keys(Translator, shape_keys):
    print(" Translating shapekeys ", shape_keys.items())
    for key in shape_keys.items():
        print(key)
        shape_key = key[1]
        shape_key.name = Translator.translate(shape_key.name)

        if shape_key.name == "GoUp":
            shape_key.name = "BrowsU_C"
        elif shape_key.name == "GoDown":
            shape_key.name = "BrowsD_C"


def fix_vertex_groups(obj):
    vertex_groups = obj.vertex_groups
    arm_re = re.compile("ArmTwist\d?$")
    hand_re = re.compile("HandTwist\d?$")

    shoulder_re = re.compile("ShoulderP|C$")
    leg_re = re.compile("LegD$")
    foot_re = re.compile("FootD$")

    remove_list = []
    for vertex_group in vertex_groups:
        if "IK" in vertex_group.name:
            remove_list.append(vertex_group)

        if "RightEyeReturn" in vertex_group.name:
            mesh.mix_weights("RightEye", "RightEyeReturn")
            remove_list.append(vertex_group)

        elif "LeftEyeReturn" in vertex_group.name:
            mesh.mix_weights("LeftEye", "LeftEyeReturn")
            remove_list.append(vertex_group)
        elif "Eyes" == vertex_group.name:
            mesh.mix_weights("Head", "Eyes")
            remove_list.append(vertex_group)

        elif "Waist" in vertex_group.name:
            mesh.mix_weights("Hips", "Waist")
            remove_list.append(vertex_group)
        elif "Head2" in vertex_group.name:
            mesh.mix_weights("Head", "Head2")
            remove_list.append(vertex_group)

        elif "ArmTwist" in vertex_group.name:
            root = re.sub(arm_re, "Arm", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mesh.mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group)
        elif re.search(shoulder_re, vertex_group.name) != None:
            root = re.sub(shoulder_re, "Shoulder", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mesh.mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group)
        elif re.search(leg_re, vertex_group.name) != None:
            root = re.sub(leg_re, "Leg", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mesh.mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group)
        elif re.search(foot_re, vertex_group.name) != None:
            root = re.sub(foot_re, "Foot", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mesh.mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group)
        elif "HandTwist" in vertex_group.name:
            root = re.sub(hand_re, "ForeArm", vertex_group.name)
            parent = vertex_groups.get(root)
            if parent is not None:
                mesh.mix_weights(root, vertex_group.name)
                remove_list.append(vertex_group)

    for group in remove_list:
        print("Removing Vertex Groups", group.name)
        vertex_groups.remove(group)


def clean_mesh(Translator, obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    print(" Converting", obj.name, "Mesh")
    translate_shape_keys(Translator, obj.data.shape_keys.key_blocks)
    fix_vertex_groups(obj)
    print(" Removing unused vertex groups")
    mesh.clean_unused_vertex_groups(obj)

# --------------------


def translate_list(Translator, list_to_translate):
    for entry in list_to_translate:
        entry.name = Translator.translate(entry.name)


def convert_mmd_avatar_hifi():

    if not bpy.data.is_saved:
        print("Select a Directory")
        bpy.ops.hifi_error.save_file('INVOKE_DEFAULT')
        return

    bpy.ops.wm.console_toggle()

    print("Converting MMD Avatar to be Blender-High Fidelity compliant")
    # Should Probably have a confirmation dialog when using this.
    original_type = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'

    Translator = MMDTranslator()
    # Change mode to object mode

    print("Translating Materials", len(bpy.data.materials))
    translate_list(Translator, list(bpy.data.materials))
    print("Translating Textures", len(bpy.data.textures))
    translate_list(Translator, list(bpy.data.textures))
    print("Translating Meshes", len(bpy.data.meshes))
    translate_list(Translator, list(bpy.data.meshes))
    print("Translating Meshes", len(bpy.data.meshes))
    translate_list(Translator, list(bpy.data.meshes))

    marked_for_purge = []
    marked_for_deletion = []

    bpy.ops.object.mode_set(mode='OBJECT')
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            if obj is not None:
                obj.select = True
                bpy.context.scene.objects.active = obj

                # Delete joints and rigid bodies items. Perhaps later convert this to flow.
                print("Reading", obj.name)
                if obj.name == "joints" or obj.name == "rigidbodies":
                    marked_for_purge.append(obj)

                elif obj.type == "EMPTY" and obj.parent is None:
                    marked_for_deletion.append(obj)

                elif obj.type == 'ARMATURE':
                    convert_bones(Translator, obj)
                    bones.scale_helper(obj)

                elif obj.type == 'MESH' and obj.parent is not None and obj.parent.type == 'ARMATURE':
                    clean_mesh(Translator, obj)
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    materials.clean_materials(obj.material_slots)

    bpy.ops.object.select_all(action='DESELECT')
    for deletion in marked_for_deletion:
        deletion.select = True
        bpy.context.scene.objects.active = deletion
        bpy.ops.object.delete()

    bpy.ops.object.select_all(action='DESELECT')
    for deletion in marked_for_purge:
        delete_self_and_children(deletion)

    materials.convert_to_png(bpy.data.images)
    materials.convert_images_to_mask(bpy.data.images)
    materials.cleanup_alpha(bpy.data.materials)
    materials.remove_materials_metallic(bpy.data.materials)

    bpy.context.area.type = original_type

    bpy.ops.file.make_paths_absolute()

    bpy.ops.wm.console_toggle()
