# -*- coding: utf-8 -*-

import csv
import bpy
import re
import os
from math import pi
import math
import copy
from mathutils import Vector
from hifi_tools.utils import materials, mesh, bones

bones_to_correct_spine_position = [
    ("Hips",       "tail", "Hips", "head", "y"),
    ("Spine",      "head", "Hips", "head", "y"),
    ("Spine",      "tail", "Hips", "head", "y"),
    ("Spine1",     "head", "Hips", "head", "y"),
    ("Spine1",     "tail", "Hips", "head", "y"),
    ("Spine2",     "head", "Hips", "head", "y"),
    ("Spine2",     "tail", "Hips", "head", "y"),
    ("Neck",       "head", "Hips", "head", "y"),
    ("Neck",       "tail", "Hips", "head", "y"),
    ("Head",       "head", "Hips", "head", "y"),
    ("Head",       "tail", "Hips", "head", "y"),
    ("RightUpLeg", "head", "Hips", "head", "y"),
    ("RightUpLeg", "tail", "Hips", "head", "y"),
    ("LeftUpLeg",  "head", "Hips", "head", "y"),
    ("LeftUpLeg",  "tail", "Hips", "head", "y"),
    ("RightLeg",   "head", "Hips", "head", "y"),
    ("RightLeg",   "tail", "Hips", "head", "y"),
    ("LeftLeg",    "head", "Hips", "head", "y"),
    ("LeftLeg",    "tail", "Hips", "head", "y"),
    ("LeftFoot",   "head", "Hips", "head", "y"),
    ("RightFoot",  "head", "Hips", "head", "y"),
    ("LeftShoulder",  "head", "LeftShoulder", "tail", "z"),
    ("RightShoulder",  "head", "RightShoulder", "tail", "z")
]


material_corrections = [
     # regex name, specular, hardness
    (r'.*High\-poly.*', 1.0, (1,1,1), 1.0, 400, (0, 0, 0)),   # high poly eye
    (r'.*Low\-poly.*', 1.0, (1,1,1), 1.0, 400, (0, 0, 0)),    # low poly eye
    (r'.*Teeth.*', 1.0, (1,1,1), 1.0, 10, (0, 0, 0)),
    (r'.*Tongue.*', 1.0, (0.6,0.6,0.6), 0.5, 10, (0, 0, 0)),
	(r'.*', 1.0, (1,1,1), 0, 1, (0, 0, 0))
]

#####################################################
# Armature Fixes:

def correct_bone_positions(bones):

    for dest_name, end, root_name, root_end, axis in bones_to_correct_spine_position:
        root_bone = bones.get(root_name)
        root = Vector(getattr(root_bone, root_end))
        dest = bones.get(dest_name)
        dest_head = Vector(dest.head)
        dest_tail = Vector(dest.tail)
        if end == "head":
            setattr(dest_head, axis, getattr(root, axis))
            dest.head = dest_head
        elif end == "tail":
            print("set tail")
            setattr(dest_tail, axis, getattr(root, axis))
            dest.tail = dest_tail

    # now do toes
    leftToe = bones.get("LeftToeBase")
    leftToeHead = Vector(leftToe.head)
    leftToeTail = Vector(leftToe.tail)
    leftToeTail.x = leftToeHead.x
    leftToeTail.z = leftToeHead.z
    leftToe.tail = leftToeTail

    rightToe = bones.get("RightToeBase")
    rightToeHead = Vector(rightToe.head)
    rightToeTail = Vector(rightToe.tail)
    rightToeTail.x = rightToeHead.x
    rightToeTail.z = rightToeHead.z
    rightToe.tail = rightToeTail


def clean_up_bones(obj):
    _to_remove = []

    pose_bones = obj.pose.bones

    bpy.ops.object.mode_set(mode='EDIT')
    updated_context = bpy.data.objects[obj.name]
    edit_bones = updated_context.data.edit_bones

    bpy.ops.object.mode_set(mode='EDIT')
    correct_bone_positions(updated_context.data.edit_bones)

    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in obj.data.bones:
        pose_bone = pose_bones.get(bone.name)

        # Oddly needed to get the edit bone reference
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bone = edit_bones.get(bone.name)

        print(" Bone ", bone.name)

        if pose_bone is not None and edit_bone is not None:
            print(" + Setting Pose Mode for", pose_bone)
            
            print(" - Removing Constraints from", pose_bone.name)
            for constraint in pose_bone.constraints:
            	pose_bone.constraints.remove(constraint)

            print(" # Check Rotations")
            bones.correct_bone_rotations(edit_bone)

            if "Thumb" in edit_bone.name:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.select_all(action="DESELECT")
                edit_bone.select = True
                bpy.ops.armature.calculate_roll(type="GLOBAL_NEG_Z")
                bpy.ops.armature.select_all(action="DESELECT")

    bpy.ops.object.mode_set(mode='OBJECT')

    return _to_remove


def convert_bones(obj):
    bones = obj.data.bones

    print("Cleaning Up Bones")
    clean_up_bones(obj)


def has_armature_as_child(me):
    for child in me.children:
        if child.type == "ARMATURE":
            return True
    return False


#####################################################
# Mesh Fixes:

def remove_modifier_by_type(obj, modifierType):
    for m in obj.modifiers:
        if m.type == modifierType:
            print("Removing modifier: %s" % m.type)
            obj.modifiers.remove(m)


def set_material_properties(obj):
    for correction in material_corrections:
        a = re.compile(correction[0])
        if(re.match(a, obj.name)):            
            for material_slot in obj.material_slots:
                material_slot.material.diffuse_intensity = correction[1]
                material_slot.material.diffuse_color = correction[2]
                material_slot.material.specular_intensity = correction[3]
                material_slot.material.specular_hardness = correction[4]
                material_slot.material.specular_color = correction[5]
            break


def create_blink_shapes(shapekey, armature1, armature2):

    armature = None
    old_meshes = {}
    meshes = {}

    # duplicate avatar
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            if obj is not None:
                if obj.type == 'ARMATURE':
                    obj.select = True
                elif obj.type == 'MESH':
                    obj.select = True
                    old_meshes[obj.name+".001"] = obj
    bpy.ops.object.duplicate()

    # pose eyelids
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            armature = obj
            bpy.context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode='POSE')
            pose_bones = obj.pose.bones
            bone_1 = pose_bones.get(armature1)
            bone_2 = pose_bones.get(armature2)
            bone_1.rotation_mode = 'XYZ'
            bone_1.rotation_euler.rotate_axis('X', math.radians(-33))
            bone_2.rotation_mode = 'XYZ'
            bone_2.rotation_euler.rotate_axis('X', math.radians(33))
        elif obj.type == 'MESH':
            meshes[obj.name] = obj

	# apply armature as shape and transfer to initial avatar
    for name in meshes:
        obj = meshes[name]
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier='ARMATURE')
        index = 0
        for key in bpy.data.shape_keys:
            for keyblock in key.key_blocks:
                if keyblock.name == 'ARMATURE':
                    keyblock.name = shapekey
                    index = len(obj.data.shape_keys.key_blocks)-1
                    obj.active_shape_key_index = index

        old_meshes[name].select = True
        bpy.context.scene.objects.active = old_meshes[name]
        bpy.ops.object.shape_key_transfer()

    #delete temporary avatar
    bpy.ops.object.select_all(action='DESELECT')
    for name in meshes:
        meshes[name].select = True
    armature.select = True
    bpy.ops.object.delete()

# --------------------

def convert_makehuman_avatar_hifi():
    # Should Probably have a confirmation dialog when using this.
    original_type = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'

    # Change mode to object mode

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
                    convert_bones(obj)

                elif obj.type == 'MESH' and obj.parent is not None and obj.parent.type == 'ARMATURE':
                    bpy.ops.object.mode_set(mode='OBJECT')
                    print(" Cleaning up Materials now. May take a while ")
                    materials.clean_materials(obj.material_slots)
                    set_material_properties(obj)                        
                    remove_modifier_by_type(obj, "SUBSURF")


    create_blink_shapes("EyeBlink_L", "orbicularis03.L", "orbicularis04.L")
    create_blink_shapes("EyeBlink_R", "orbicularis03.R", "orbicularis04.R")

    for deletion in marked_for_deletion:
        deletion.select = True
        bpy.context.scene.objects.active = deletion
        bpy.ops.object.delete()

    bpy.context.area.type = original_type