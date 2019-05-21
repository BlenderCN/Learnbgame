# -*- coding: utf-8 -*-
"""
Created on Mon May 29 03:54:30 2017

Motion Capture Addon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

@author: AO Street Art
"""

bl_info = {
    "name": "blendmocap",
    "author": "AO Street Art",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "description": "Blender Add on to assist in the use of using BVH data",
    "category": "Object",
}

import bpy


# Base Functions


# Select an object and switch to pose mode
def select_and_pose(src):
    # Deselect everything
    for ob in bpy.context.selected_objects:
        ob.select = False

    # Select the source armature
    src.select = True
    bpy.context.scene.objects.active = src

    # Set pose mode and select all the bones in the armature
    bpy.ops.object.mode_set(mode='POSE')


# Transform the mocap constraints to keyframes
def create_mocap_keyframes(src, trg, keyframe_interval):
    print("Creating Motion Capture Keyframes on %s with target %s" % (src.name, trg.name))

    select_and_pose(src)
    bpy.ops.pose.select_all(action='SELECT')

    start_frame_index = bpy.context.scene.frame_start
    end_frame_index = bpy.context.scene.frame_end

    bpy.ops.nla.bake(frame_start=start_frame_index, frame_end=end_frame_index, visual_keying=True,
                     clear_constraints=True, step=keyframe_interval,only_selected=True, bake_types={'POSE'})


# Removes the mocap constraints, and ensures that if any bones were selected in pose mode, then they stay selected
def remove_mocap_constraints(src):
    print("Removing Motion Capture Constraints from %s" % src.name)

    select_and_pose(src)
    bpy.ops.pose.select_all(action='SELECT')

    # iterate over the pose bones
    for bone in bpy.context.selected_pose_bones:
        for c in bone.constraints:
            if c.type == 'COPY_ROTATION' or c.type == 'COPY_LOCATION' or c.type =='LIMIT_ROTATION':
                bone.constraints.remove(c)


# Copy the roll values for all bones in one armature to another
def copy_bone_rolls(src, trg):
    # Setup
    rolls = {}

    print("Pulling Bone Roll from Source")

    # Pull the Roll values from the source armature
    bpy.context.scene.objects.active = src
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in src.data.edit_bones:
        rolls[eb.name] = eb.roll
        bpy.ops.object.mode_set(mode='POSE')

    print("Writing Bone Roll to Target")

    # Place the Roll values in the target armature
    bpy.context.scene.objects.active = trg
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in trg.data.edit_bones:
        old_roll = eb.roll
        if eb.name in rolls:
            eb.roll = rolls[eb.name]
        print(eb.name, old_roll, eb.roll)


# Determine if a bone name is in an armature object
def is_bone_in_armature(name, armature):
    for bone in armature.pose.bones:
        if (bone.name == name):
            return True
    return False


# Copy Location Constraints
def add_location_mocap_constraints(src, trg):
    print("Adding Location Constraints to %s with target %s" % (src.name, trg.name))

    # Select the source armature and select all of the bones
    select_and_pose(src)
    bpy.ops.pose.select_all(action='SELECT')

    # iterate over the pose bones
    for bone in bpy.context.selected_pose_bones:

        # Only apply the constraints if the bone is in our target armature
        if (is_bone_in_armature(bone.name, trg)):
            # Apply a Copy Rotation Constraint to each pose bone
            new_constraint = bone.constraints.new('COPY_LOCATION')

            # Set up the constraint target and set it to copy pose data
            new_constraint.target = trg
            new_constraint.subtarget = bone.name
            new_constraint.target_space = 'POSE'
            new_constraint.owner_space = 'POSE'

# Setup Copy Rotation & Location Constraints
def add_rotation_mocap_constraints(src, trg):

    print("Adding Rotation Constraints to %s with target %s" % (src, trg))

    # Select the source armature and select all of the bones
    select_and_pose(src)
    bpy.ops.pose.select_all(action='SELECT')

    # iterate over the pose bones
    for bone in bpy.context.selected_pose_bones:

        # Only apply the constraints if the bone is in our target armature
        if (is_bone_in_armature(bone.name, trg)):

            # Apply a Copy Rotation Constraint to each pose bone
            new_constraint = bone.constraints.new('COPY_ROTATION')

            # Set up the constraint target and set it to copy pose data
            new_constraint.target = trg
            new_constraint.subtarget = bone.name
            new_constraint.target_space = 'POSE'
            new_constraint.owner_space = 'POSE'


# Core Logic


# Add a Limit Rotation Constraint to fix a twisted bone
def add_twist_fix():
    # iterate over the pose bones
    for bone in bpy.context.selected_pose_bones:

        # Apply a Limit Rotation Constraint to each pose bone
        new_constraint = bone.constraints.new('LIMIT_ROTATION')
        new_constraint.owner_space = 'POSE'


# Copy the armature with no animation
def copy_armature_without_animation():
    # Duplicate the armature
    bpy.ops.object.duplicate_move()

    # Remove the keyframes from the armature
    bpy.ops.anim.keyframe_clear_v3d()


# Copy bone roll values from one armature to another
def copy_bone_rotations():
    # Find the source and target armatures
    trg = bpy.context.scene.objects.active
    src = None
    for ob in bpy.context.selected_objects:
        if ob.name != trg.name:
            src = ob

    if src is None:
        print("No source selected")
    else:
        print("Copying Bone Rotation from %s to %s" % (src.name, trg.name))
        copy_bone_rolls(src, trg)


# Actually transfer the motion capture data
def transfer_mocap_data(interv, gen_cn, gen_kf):
    # Find the source and target armatures
    trg = bpy.context.scene.objects.active
    src = None
    for ob in bpy.context.selected_objects:
        if ob.name != trg.name:
            src = ob

    if src is None:
        print("no source selected")
    else:
        if gen_cn:
            # Set up the Motion Capture Constraints
            add_location_mocap_constraints(trg, src)
            # Turn off pose mode so that we can do basic operations
            bpy.ops.object.posemode_toggle()
            add_rotation_mocap_constraints(trg, src)
        if gen_kf:
            # Transform the constraints to keyframes
            create_mocap_keyframes(trg, src, interv)
            # Remove the Motion Capture Constraints
            remove_mocap_constraints(trg)


# Blender Operators
# Functions exposed via the Blender UI


# Copy Bone Roll from one armature to another
class CopyBoneRotations(bpy.types.Operator):
    bl_idname = "object.copy_bone_roll"
    bl_label = "Copy Bone Roll"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        copy_bone_rotations()

        # Let's blender know the operator is finished
        return {'FINISHED'}


# Fix Twisted Bones
class FixTwistedBones(bpy.types.Operator):
    bl_idname = "object.fix_twisted_bones"
    bl_label = "Fix Twisted Bones"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        add_twist_fix()

        # Let's blender know the operator is finished
        return {'FINISHED'}


# Actually transfer the mocap data from one rig to another
class TransferMoCapData(bpy.types.Operator):
    bl_idname = "object.transfer_mocap_data"
    bl_label = "Transfer MoCap Data"
    bl_options = {'REGISTER', 'UNDO'}
    generate_constraints = bpy.props.BoolProperty(name="Generate Constraints", default=True)
    generate_keyframes = bpy.props.BoolProperty(name="Generate Keyframes", default=True)
    keyframe_interval = bpy.props.IntProperty(name="KeyFrameInterval", default=5)

    # Called when operator is run
    def execute(self, context):

        transfer_mocap_data(self.keyframe_interval, self.generate_constraints,
                            self.generate_keyframes)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Copy the mocap armature without keeping the animations
class CopyArmaturewithoutAnimation(bpy.types.Operator):
    bl_idname = "object.copy_armature_without_animation"
    bl_label = "Copy Armature without Animation"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        copy_armature_without_animation()

        # Let's blender know the operator is finished
        return {'FINISHED'}


# Remove the Mocap Constraints
class RemoveMocapConstraints(bpy.types.Operator):
    bl_idname = "object.remove_mocap_constraints"
    bl_label = "Remove Motion Capture Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):
        remove_mocap_constraints(trg)

        # Let's blender know the operator is finished
        return {'FINISHED'}


# Custom UI Elements


# Armature Panel
class MocapArmaturePanel(bpy.types.Panel):
    """Create the BlendMoCap Armature Panel"""
    bl_label = "BlendMoCap"
    bl_idname = "ARMATURE_PT_BlendMoCap"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="First Bone", icon='ARMATURE_DATA')

        row = layout.row()
        row.operator("object.transfer_mocap_data")


class VIEW3D_PT_tools_blendmocap(bpy.types.Panel):
    bl_label = "BlendMoCap Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        self.layout.operator("object.copy_armature_without_animation")
        self.layout.operator("object.copy_bone_roll")
        self.layout.operator("object.fix_twisted_bones")


# Register and UnRegister functions for the blender objects


def register():
    bpy.utils.register_class(FixTwistedBones)
    bpy.utils.register_class(CopyBoneRotations)
    bpy.utils.register_class(CopyArmaturewithoutAnimation)
    bpy.utils.register_class(TransferMoCapData)
    bpy.utils.register_class(MocapArmaturePanel)
    bpy.utils.register_class(VIEW3D_PT_tools_blendmocap)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_tools_blendmocap)
    bpy.utils.unregister_class(MocapArmaturePanel)
    bpy.utils.unregister_class(TransferMoCapData)
    bpy.utils.unregister_class(CopyArmaturewithoutAnimation)
    bpy.utils.unregister_class(CopyBoneRotations)
    bpy.utils.unregister_class(FixTwistedBones)


if __name__ == "__main__":
    register()
