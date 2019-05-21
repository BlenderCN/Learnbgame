# -*- python-indent: 4; mode: python -*-
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2008-2012 Cedric Pinson
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#  Cedric Pinson <cedric@plopbyte.com>
#  Jeremy Moles <jeremy@emperorlinux.com>
#  Aurélien Chatelain <chatelain.aurelien@gmail.com>


import bpy
import math
from .osgobject import *


# IMAGES HELPERS
# ----------------------------
def createImageFilename(texturePath, image):
    fn = bpy.path.basename(bpy.path.display_name_from_filepath(image.filepath))

    # for packed file, fallback to image name
    if not fn:
        fn = image.name

    i = fn.rfind(".")
    if i != -1:
        name = fn[0:i]
    else:
        name = fn
    # [BMP, IRIS, PNG, JPEG, TARGA, TARGA_RAW, AVI_JPEG, AVI_RAW, FRAMESERVER]
    if image.file_format == 'PNG':
        ext = "png"
    elif image.file_format == 'HDR':
        ext = "hdr"
    elif image.file_format == 'JPEG':
        ext = "jpg"
    elif image.file_format == 'TARGA' or image.file_format == 'TARGA_RAW':
        ext = "tga"
    elif image.file_format == 'BMP':
        ext = "bmp"
    elif image.file_format == 'AVI_JPEG' or image.file_format == 'AVI_RAW':
        ext = "avi"
    else:
        ext = "unknown"
    name = name + "." + ext
    print("create Image Filename " + name)
    if texturePath != "" and not texturePath.endswith("/"):
        texturePath = texturePath + "/"
    return texturePath + name


def getImageFilesFromStateSet(stateset):
    images = []
    if stateset is not None and len(stateset.texture_attributes) > 0:
        for unit, attributes in stateset.texture_attributes.items():
            for a in attributes:
                if a.className() == "Texture2D":
                    images.append(a.source_image)
    return images


# ARMATURE AND ANIMATION HELPERS
# ----------------------------
def findBoneInHierarchy(scene, bonename):
    if scene.name == bonename and (type(scene) == type(Bone()) or type(scene) == type(Skeleton())):
        return scene

    if isinstance(scene, Group) is False:
        return None

    for child in scene.children:
        result = findBoneInHierarchy(child, bonename)
        if result is not None:
            return result
    return None


def getRootBonesList(armature):
    bones = []
    for bone in armature.bones:
        if bone.parent is None:
            bones.append(bone)
    return bones


def truncateFloat(value, digit=5):
    if math.isnan(value):
        return 0
    return round(value, digit)


def truncateVector(vector, digit=5):
    for i in range(0, len(vector)):
        vector[i] = truncateFloat(vector[i], digit)
    return vector


def getTransform(matrix):
    return (matrix.translationPart(),
            matrix.scalePart(),
            matrix.toQuat())


def getDeltaMatrixFrom(parent, child):
    if parent is None:
        return child.matrix_world

    return getDeltaMatrixFromMatrix(parent.matrix_world,
                                    child.matrix_world)


def getWidestActionDuration(scene, clamp_with_scene=True):
    start = []
    end = []

    # Check duration in actions and nla tracks
    for obj in scene.objects:
        if hasAction(obj):
            start.append(obj.animation_data.action.frame_range[0])
            end.append(obj.animation_data.action.frame_range[1])
        if hasNLATracks(obj):
            for nla_tracks in obj.animation_data.nla_tracks:
                start.extend([strip.frame_start for strip in nla_tracks.strips])
                end.extend([strip.frame_end for strip in nla_tracks.strips])

    if clamp_with_scene and start and end:
        start = int(min(start))
        end = int(max(end))

        start = max(start, scene.frame_start)
        end = min(end, scene.frame_end)
    else:
        start.append(int(scene.frame_start))
        end.append(int(scene.frame_end))
        # If scene frame range is wider, use it
        start = int(min(start))
        end = int(max(end))

    return (start, end)


def hasExternalBoneConstraints(blender_object):
    if blender_object.type != 'ARMATURE' or not blender_object.pose:
        return False

    for bone in blender_object.pose.bones:
        for cons in bone.constraints:
            if hasattr(cons, 'target') and cons.target is not None and cons.target != blender_object:
                return True

    return False


def hasSolidConstraints(blender_object):
    return hasattr(blender_object, "constraints") and (len(blender_object.constraints) > 0)


def hasAction(blender_object):
    return hasattr(blender_object, "animation_data") and \
        hasattr(blender_object.animation_data, "action") and \
        blender_object.animation_data.action is not None


def hasNLATracks(blender_object):
    return hasattr(blender_object, "animation_data") and \
        hasattr(blender_object.animation_data, "nla_tracks") and \
        blender_object.animation_data.nla_tracks


def isRigAction(action):
    for curve in action.fcurves:
        if 'pose.bones' in curve.data_path:
            return True

    return False


def isSolidOrRigAction(action):
    for curve in action.fcurves:
        if 'key_block' in curve.data_path or 'eval_time' in curve.data_path:
            return False

    return True


def hasShapeKeys(blender_object):
    return hasattr(blender_object.data, "shape_keys") and \
        blender_object.data.shape_keys is not None and \
        len(blender_object.data.shape_keys.key_blocks) > 0


def hasShapeKeysAnimation(blender_object):
    # Animation can be either on the shape_keys object
    # or the object having shape_keys
    if hasShapeKeys(blender_object):
        shape = blender_object.data.shape_keys
        if shape.animation_data and \
           shape.animation_data.action:
            return True

    if hasAction(blender_object) and not isSolidOrRigAction(blender_object.animation_data.action):
        return True

    return False


def isMorphAction(action):
    for curve in action.fcurves:
        if 'key_blocks' in curve.data_path or 'eval_time' in curve.data_path:
            return True

    return False


def isObjectMorphAction(action):
    for curve in action.fcurves:
        if 'data.shape_keys' in curve.data_path:
            return True

    return False


# OBJECTS HELPERS
# ------------------------------
def getDeltaMatrixFromMatrix(parent, child):
    p = parent
    bi = p.copy()
    bi.invert()
    return bi * child


def getChildrenOf(scene, object):
    children = []
    for obj in scene.objects:
        if obj.parent == object:
            children.append(obj)
    return children


def isActionLinkedToObject(action, objects_name):
    action_fcurves = action.fcurves

    for fcurve in action_fcurves:
        path = fcurve.data_path.split("\"")
        if objects_name in path:
            return True
    return False


def unselectAllObjects():
    for obj in bpy.context.selected_objects:
        obj.select = False


def selectObjects(object_list):
    for obj in object_list:
        obj.select = True


def spaceSafe(bonename):
    return bonename.replace(' ', '_')


def setArmaturesPosePosition(scene, pose_position, armatures=[]):
    if pose_position not in ['POSE', 'REST']:
        return

    # If no armature specified, take all scene armatures
    if not armatures:
        armatures = [obj for obj in scene.objects if obj.type == 'ARMATURE']

    modified = []
    for armature in armatures:
        arm_data = armature.data
        if not hasattr(arm_data, 'pose_position'):
            continue
        if arm_data.pose_position != pose_position:
            arm_data.pose_position = pose_position
            modified.append(armature)

    scene.update()
    return modified
