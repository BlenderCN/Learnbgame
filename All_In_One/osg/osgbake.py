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
import bisect
from .osgutils import *


def cleanAction(action):
    for fcu in action.fcurves:
        keyframe_points = fcu.keyframe_points
        i = 1
        while i < len(fcu.keyframe_points) - 1:
            val_prev = keyframe_points[i - 1].co[1]
            val_next = keyframe_points[i + 1].co[1]
            val = keyframe_points[i].co[1]

            if abs(val - val_prev) + abs(val - val_next) < 0.0001:
                keyframe_points.remove(keyframe_points[i])
            else:
                i += 1


def bakeMorphTargets(frame_start,
                     frame_end,
                     blender_object,
                     frame_step=1):

    def collectValues(morph_info, frame_range):
        'Collect shape keys factors for each frame in frame range'
        for f in frame_range:
            scene.frame_set(f)
            scene.update()
            for block in morph_info:
                morph_info[block].append(block.value)

    def evaluateActiveShapeKeys(currentFrame, keyFrames):
        ''' Get effective shapes according to current time
            and evaluate the factor for each '''
        # keyFrames is never empty here
        if currentFrame > keyFrames[-1]:  # after the last key_block frame
            previous_block = shape.key_blocks[-1]
            next_block = None
            value = 0.0
        elif currentFrame < keyFrames[0]:  # before the first key_block frame
            previous_block = None
            next_block = shape.key_blocks[0]
            value = 1.0
        else:
            # general case with index in [0:16] and blending two key_blocks
            index = bisect.bisect(keyFrames, currentFrame) - 1
            previous_block = shape.key_blocks[index]
            next_block = shape.key_blocks[index + 1]
            # TODO implement others interpolations (Cardinal, Bspline, Catmull-Rom) or find a way to
            # get the value with Blender API
            value = (currentFrame - previous_block.frame) / (next_block.frame - previous_block.frame)

        return {'previous': previous_block, 'next': next_block, 'factor': value}

    def generateFromAbsolute(shape, morph_info, frame_range):
        'Convert absolute shape keys to relative'
        # Absolute keyframe are always ordered through time
        keyFrames = [block.frame for block in shape.key_blocks]
        for f in frame_range:
            scene.frame_set(f)
            scene.update()
            values = evaluateActiveShapeKeys(shape.eval_time, keyFrames)
            for block in morph_info:
                if block == values['previous']:
                    morph_info[block].append(1 - values['factor'])
                elif block == values['next']:
                    morph_info[block].append(values['factor'])
                else:
                    morph_info[block].append(0.0)

    def setKeyframes(shape, frame_range):
        'Generate shape keys keyframes'
        atd = shape.animation_data_create()
        atd.action = new_action
        for block in morph_info:
            for (f, value) in zip(frame_range, morph_info[block]):
                block.value = value
                shape.keyframe_insert('key_blocks[\"{}\"].value'.format(block.name), -1, f)

    scene = bpy.context.scene
    shape = blender_object.data.shape_keys
    frame_back = scene.frame_current

    original_action = shape.animation_data.action if hasAction(shape) else None
    frame_range = range(frame_start, frame_end + 1, frame_step)
    morph_info = {}

    for block in shape.key_blocks:
        if block.name != block.relative_key.name:
            morph_info[block] = []  # values

    new_action = bpy.data.actions.new("MorphBake")

    if shape.use_relative:
        collectValues(morph_info, frame_range)
    else:
        generateFromAbsolute(shape, morph_info, frame_range)

    setKeyframes(shape, frame_range)
    cleanAction(new_action)
    shape.animation_data.action = original_action
    scene.frame_set(frame_back)
    scene.update()

    return new_action


# This function comes from bpy_extras.anim_utils and has been
# added here to allow more control on baking process
def bakeAction(blender_object,
               frame_start,
               frame_end,
               frame_step=1,
               only_selected=False,
               do_pose=True,
               do_object=True,
               do_visual_keying=True,
               use_quaternions=False,
               do_constraint_clear=False,
               do_parents_clear=False,
               do_clean=False,
               action=None,
               ):

    """
    Return an image from the file path with options to search multiple paths
    and return a placeholder if its not found.

    :arg frame_start: First frame to bake.
    :type frame_start: int
    :arg frame_end: Last frame to bake.
    :type frame_end: int
    :arg frame_step: Frame step.
    :type frame_step: int
    :arg only_selected: Only bake selected data.
    :type only_selected: bool
    :arg do_pose: Bake pose channels.
    :type do_pose: bool
    :arg do_object: Bake objects.
    :type do_object: bool
    :arg do_visual_keying: Use the final transformations for baking ('visual keying')
    :type do_visual_keying: bool
    :arg do_constraint_clear: Remove constraints after baking.
    :type do_constraint_clear: bool
    :arg do_parents_clear: Unparent after baking objects.
    :type do_parents_clear: bool
    :arg do_clean: Remove redundant keyframes after baking.
    :type do_clean: bool
    :arg action: An action to bake the data into, or None for a new action
       to be created.
    :type action: :class:`bpy.types.Action` or None

    :return: an action or None
    :rtype: :class:`bpy.types.Action`
    """

    # -------------------------------------------------------------------------
    # Helper Functions and vars
    def poseFrameInfo(blender_object, do_visual_keying):
        matrix = {}
        for name, pbone in blender_object.pose.bones.items():
            # As there is no similar "use_inherit_rotation" property in osg, we have to temporarily enable
            # it here to get the good baking results and the good bone transforms
            backup_rotation_inheritance = pbone.bone.use_inherit_rotation
            pbone.bone.use_inherit_rotation = True
            if do_visual_keying:
                # Get the final transform of the bone in its own local space...
                matrix[name] = blender_object.convert_space(pbone, pbone.matrix, 'POSE', 'LOCAL')
            else:
                matrix[name] = pbone.matrix_basis.copy()

            pbone.bone.use_inherit_rotation = backup_rotation_inheritance
        return matrix

    if do_parents_clear:
        def objFrameInfo(blender_object, do_visual_keying):
            parent = blender_object.parent
            matrix = blender_object.matrix_local if do_visual_keying else blender_object.matrix_local
            if parent:
                return parent.matrix_world * matrix
            else:
                return matrix.copy()
    else:
        def objFrameInfo(blender_object, do_visual_keying):
            return blender_object.matrix_local.copy() if do_visual_keying else blender_object.matrix_basis.copy()

    # -------------------------------------------------------------------------
    # Setup the Context

    # TODO, pass data rather then grabbing from the context!
    scene = bpy.context.scene
    frame_back = scene.frame_current
    bone_correction = Vector((0, 0, 0))
    if blender_object.parent_bone and blender_object.parent:
        bone_height = blender_object.parent.data.bones[blender_object.parent_bone].tail_local.z \
            - blender_object.parent.data.bones[blender_object.parent_bone].head_local.z
        bone_correction = Vector((0, bone_height, 0))

    if blender_object.pose is None:
        do_pose = False

    if not (do_pose or do_object):
        return None

    pose_info = []
    obj_info = []

    options = {'INSERTKEY_NEEDED'}

    frame_range = range(frame_start, frame_end + 1, frame_step)

    # -------------------------------------------------------------------------
    # Collect transformations
    for f in frame_range:
        scene.frame_set(f)
        scene.update()
        if do_pose:
            pose_info.append(poseFrameInfo(blender_object, do_visual_keying))
        if do_object:
            obj_info.append(objFrameInfo(blender_object, do_visual_keying))

    # -------------------------------------------------------------------------
    # Create action

    # in case animation data hasn't been created
    atd = blender_object.animation_data_create()
    if action is None:
        action = bpy.data.actions.new("BakedAction")
    atd.action = action

    # -------------------------------------------------------------------------
    # Apply transformations to action

    # pose
    if do_pose:
        for name, pbone in blender_object.pose.bones.items():
            if only_selected and not pbone.bone.select:
                continue

            # Quaternions are forced for bones
            rotation_mode_backup = pbone.rotation_mode
            if pbone.rotation_mode != 'QUATERNION':
                pbone.rotation_mode = 'QUATERNION'

            if do_constraint_clear:
                while pbone.constraints:
                    pbone.constraints.remove(pbone.constraints[0])

            # create compatible eulers
            euler_prev = None

            for (f, matrix) in zip(frame_range, pose_info):
                pbone.matrix_basis = matrix[name].copy()

                pbone.keyframe_insert("location", -1, f, name, options)

                rotation_mode = pbone.rotation_mode
                if rotation_mode == 'QUATERNION':
                    pbone.keyframe_insert("rotation_quaternion", -1, f, name, options)
                elif rotation_mode == 'AXIS_ANGLE':
                    pbone.keyframe_insert("rotation_axis_angle", -1, f, name, options)
                else:  # euler, XYZ, ZXY etc
                    if euler_prev is not None:
                        euler = pbone.rotation_euler.copy()
                        euler.make_compatible(euler_prev)
                        pbone.rotation_euler = euler
                        euler_prev = euler
                        del euler
                    else:
                        euler_prev = pbone.rotation_euler.copy()
                    pbone.keyframe_insert("rotation_euler", -1, f, name, options)

                pbone.keyframe_insert("scale", -1, f, name, options)

            # restore rotation mode
            pbone.rotation_mode = rotation_mode_backup

    # object. TODO. multiple objects
    if do_object:

        rotation_mode_backup = blender_object.rotation_mode
        # Keep the value of matrix_basis since it will be modified by the baking process
        # It is mandatory for constraint baking
        matrix_basis_backup = blender_object.matrix_basis.copy()
        matrix_local_backup = blender_object.matrix_local.copy()
        matrix_parent_inverse_backup = blender_object.matrix_parent_inverse.copy()

        # Delta rotation quaternion can break the rotation of the object
        # so we set it to default quaternion for our use and then restore its original value
        delta_rotation_backup = blender_object.delta_rotation_quaternion
        if use_quaternions and blender_object.rotation_mode != 'QUATERNION':
            blender_object.delta_rotation_quaternion = (1, 0, 0, 0)
            blender_object.rotation_mode = 'QUATERNION'

        if do_constraint_clear:
            while blender_object.constraints:
                blender_object.constraints.remove(blender_object.constraints[0])

        # create compatible eulers
        euler_prev = None

        for (f, matrix) in zip(frame_range, obj_info):
            name = "Action Bake"  # XXX: placeholder
            blender_object.matrix_basis = matrix
            # visual keying is enabled so set parent to identity
            if do_visual_keying:
                blender_object.matrix_parent_inverse.identity()
                if blender_object.parent_bone and blender_object.parent:
                    # Blender considers bone's tail instead of bone's head for parenting
                    # so we need to take to take bone's length into account
                    blender_object.location += bone_correction

            blender_object.keyframe_insert("location", -1, f, name, options)

            rotation_mode = blender_object.rotation_mode
            if rotation_mode == 'QUATERNION':
                blender_object.keyframe_insert("rotation_quaternion", -1, f, name, options)
            elif rotation_mode == 'AXIS_ANGLE':
                blender_object.keyframe_insert("rotation_axis_angle", -1, f, name, options)
            else:  # euler, XYZ, ZXY etc
                if euler_prev is not None:
                    euler = blender_object.rotation_euler.copy()
                    euler.make_compatible(euler_prev)
                    blender_object.rotation_euler = euler
                    euler_prev = euler
                    del euler
                else:
                    euler_prev = blender_object.rotation_euler.copy()
                blender_object.keyframe_insert("rotation_euler", -1, f, name, options)

            blender_object.keyframe_insert("scale", -1, f, name, options)

        # restore rotation mode
        blender_object.rotation_mode = rotation_mode_backup
        blender_object.delta_rotation_quaternion = delta_rotation_backup

        if do_parents_clear:
            blender_object.parent = None

        # restore current scene frame and original matrices for object.
        # Setting back matrices is required since baking process changes these values
        # and it can affect further constraints bakings. Note that the order is important here
        scene.frame_set(frame_back)
        scene.update()
        blender_object.matrix_parent_inverse = matrix_parent_inverse_backup
        blender_object.matrix_local = matrix_local_backup
        blender_object.matrix_basis = matrix_basis_backup
        scene.update()

    # -------------------------------------------------------------------------
    # Clean

    if do_clean:
        cleanAction(action)

    return action


# take care of restoring selection after
def bakeAnimation(scene, start, end, frame_step, blender_object, has_action=False, use_quaternions=False):
    # baking will replace the current action but we want to keep scene unchanged
    original_action = blender_object.animation_data.action if has_action else None

    # Set armatures to POSE mode before baking to bake the good transforms
    rest_armatures = setArmaturesPosePosition(scene, 'POSE')

    do_visual_keying = True  # Always, need to take bone constraints  into account

    # Baking is done on the active object
    baked_action = bakeAction(blender_object,
                              start,
                              end,
                              frame_step,
                              do_clean=True,  # clean keyframes
                              do_constraint_clear=False,
                              do_parents_clear=False,
                              do_object=True,  # bake solid animation
                              do_pose=True,  # bake skeletal animation
                              use_quaternions=use_quaternions,  # use_quaternions,
                              # visual keying bakes in worldspace, but here we want it local since we keep parenting
                              do_visual_keying=do_visual_keying)

    # restore original action and armatures' pose position
    blender_object.animation_data.action = original_action
    setArmaturesPosePosition(scene, 'REST', rest_armatures)

    return baked_action
