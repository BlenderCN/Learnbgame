import bpy
import bpy_types
from mathutils import *
from progress_report import ProgressReport, ProgressReportSubstep
import os
from . import seanim as SEAnim

# <pep8 compliant>

# TODO: Add support for defining modifier bones for Absolute anims

# This is the scale multiplier for exported anims
g_scale = 1  # TODO - Proper scaling


def get_loc_vec(bone, anim_type):
    if (anim_type == SEAnim.SEANIM_TYPE.SEANIM_TYPE_ABSOLUTE and
            bone.parent is not None):
        return bone.parent.matrix.inverted() * bone.matrix.translation
    return bone.matrix_basis.translation

# TODO: Support for SEANIM_TYPE_ADDITIVE


def get_rot_quat(bone, anim_type):
    # Absolute, Relative, and Delta all use the same rotation formula
    try:
        bone.parent.matrix
    except:
        # Lets just return the matrix as a quaternion for now - it mirrors what
        # the importer does
        return bone.matrix.to_quaternion()
    else:
        mtx = bone.parent.matrix.to_3x3()
        return (mtx.inverted() * bone.matrix.to_3x3()).to_quaternion()

# Generate a SEAnim compatible LOC keyframe from a given pose bone


def gen_loc_key(frame, pose_bone, anim_type):
    # Remove the multiplication later
    loc = get_loc_vec(pose_bone, anim_type) * g_scale
    return SEAnim.KeyFrame(frame, (loc.x, loc.y, loc.z))

# Generate a SEAnim compatible ROT keyframe from a given pose bone


def gen_rot_key(frame, pose_bone, anim_type):
    quat = get_rot_quat(pose_bone, anim_type)
    return SEAnim.KeyFrame(frame, (quat.x, quat.y, quat.z, quat.w))


def gen_scale_key(frame, pose_bone, anim_type):
    '''
    Generate an SEAnim compatible SCALE keyframe from a given pose bone
    '''
    scale = tuple(pose_bone.scale)
    return SEAnim.KeyFrame(frame, scale)


def resolve_animtype(self):
    """
    Resolve an SEAnim compatible anim_type integer from the anim_type
    EnumProperty
    """
    at = self.anim_type
    type_dict = {	'OPT_ABSOLUTE': SEAnim.SEANIM_TYPE.SEANIM_TYPE_ABSOLUTE,
                  'OPT_ADDITIVE': SEAnim.SEANIM_TYPE.SEANIM_TYPE_ADDITIVE,
                  'OPT_RELATIVE': SEAnim.SEANIM_TYPE.SEANIM_TYPE_RELATIVE,
                  'OPT_DELTA': SEAnim.SEANIM_TYPE.SEANIM_TYPE_DELTA,
                  }

    return type_dict.get(at)


def export_action(self, context, progress, action, filepath):
    # print("%s -> %s" % (action.name, filepath)) # DEBUG

    ob = bpy.context.object
    frame_original = context.scene.frame_current

    anim = SEAnim.Anim()
    anim.header.animType = resolve_animtype(self)
    if anim.header.animType is None:
        raise Exception('Could not resolve anim type', '%s' % self.anim_type)
        return  # Just to be safe

    """
        For whatever reason:
            An action with a single keyframe (ex: on frame 1)
             will have a range of (ex: Vector((1.0, 2.0)))
            However, an action with a keyframe on both frame 1 and frame 2
             will have the same frame range.

        To make up for this - we assume frame_range[1] - frame_range[0] + 1
            is the number of frames in the action
        For actions that only have keyframes on a single frame:
        this must be corrected later...
    """
    frame_start = int(action.frame_range[0])
    anim.header.frameCount = int(
        action.frame_range[1]) - int(action.frame_range[0]) + 1
    anim.header.framerate = context.scene.render.fps

    use_keys_loc = 'LOC' in self.key_types
    use_keys_rot = 'ROT' in self.key_types
    use_keys_scale = 'SCALE' in self.key_types

    anim_bones = {}

    for pose_bone in ob.pose.bones:
        anim_bone = SEAnim.Bone()
        anim_bone.name = pose_bone.name
        anim_bones[pose_bone.name] = anim_bone

    frames = {}

    # Step 1: Analyzing Keyframes
    # Resolve the relevent keyframe indices for loc, rot, and / or scale for
    # each bone
    for fc in action.fcurves:
        try:
            prop = ob.path_resolve(fc.data_path, False)  # coerce=False
            if type(prop.data) != bpy_types.PoseBone:
                raise
            pose_bone = prop.data

            if prop == pose_bone.location.owner:
                if not use_keys_loc:
                    continue
                # print("LOC")
                index = 0
            elif(prop == pose_bone.rotation_quaternion.owner or
                 prop == pose_bone.rotation_euler.owner or
                 prop == pose_bone.rotation_axis_angle.owner):
                if not use_keys_rot:
                    continue
                # print("ROT")
                index = 1
            elif owner is pose_bone.scale.owner:
                if not use_keys_scale:
                    continue
                # print("SCALE")
                index = 2
            else:  # If the fcurve isn't for a valid property, just skip it
                continue
        except Exception as e:
            # The fcurve probably isn't even for a pose bone - just skip it
            # print("skipping : %s" % e) # DEBUG
            pass
        else:
            for key in fc.keyframe_points:
                f = int(key.co[0])
                if frames.get(f) is None:
                    frames[f] = {}
                frame_bones = frames[f]
                if frame_bones.get(pose_bone.name) is None:
                    # [PoseBone, LocKey, RotKey, ScaleKey]
                    #  for each bone on the current frame
                    frame_bones[pose_bone.name] = [
                        pose_bone, False, False, False]
                # Enable the corresponding keyframe type for that bone on this
                # frame
                frame_bones[pose_bone.name][index + 1] = True

    # Set the frame_count to the the REAL number of frames in the action if
    # there is only 1
    if len(frames) == 1:
        anim.header.frameCount = 1

    # Step 2: Gathering Animation Data
    if self.every_frame:  # Export every keyframe
        progress.enter_substeps(anim.header.frameCount)
        for frame in range(anim.header.frameCount):
            context.scene.frame_set(frame + frame_start)

            for name, anim_bone in anim_bones.items():
                pose_bone = ob.pose.bones.get(name)
                if pose_bone is None:
                    continue

                if use_keys_loc:
                    anim_bone.posKeys.append(gen_loc_key(
                        frame, pose_bone, anim.header.animType))
                if use_keys_rot:
                    anim_bone.rotKeys.append(gen_rot_key(
                        frame, pose_bone, anim.header.animType))
                if use_keys_scale:
                    anim_bone.scaleKeys.append(gen_scale_key(
                        frame, pose_bone, anim.header.animType))

            progress.step()

    else:  # Only export keyed frames
        progress.enter_substeps(len(frames))

        for frame, bones in frames.items():
            context.scene.frame_set(frame)

            for name, bone_info in bones.items():
                anim_bone = anim_bones[name]
                # the first element in the bone_info array is the PoseBone
                pose_bone = bone_info[0]

                if use_keys_loc and bone_info[1]:
                    anim_bone.posKeys.append(gen_loc_key(
                        frame - frame_start, pose_bone, anim.header.animType))
                if use_keys_rot and bone_info[2]:
                    anim_bone.rotKeys.append(gen_rot_key(
                        frame - frame_start, pose_bone, anim.header.animType))
                if use_keys_scale and bone_info[3]:
                    anim_bone.scaleKeys.append(gen_scale_key(
                        frame - frame_start, pose_bone, anim.header.animType))

            progress.step()

    context.scene.frame_set(frame_original)
    progress.leave_substeps()

    # Step 3: Finalizing Data
    for name, bone in anim_bones.items():
        anim.bones.append(bone)

    for pose_marker in action.pose_markers:
        note = SEAnim.Note()
        note.frame = pose_marker.frame
        note.name = pose_marker.name
        anim.notes.append(note)

    # Step 4: Writing File
    anim.save(filepath, high_precision=self.high_precision,
              looping=self.is_looped)

    # DEBUG - Verify that the written file is valid
    # SEAnim.LOG_ANIM_HEADER = True
    # SEAnim.Anim(filepath)


def save(self, context):
    ob = bpy.context.object
    if ob.type != 'ARMATURE':
        return "An armature must be selected!"

    prefix = self.prefix  # os.path.basename(self.filepath)
    suffix = self.suffix

    path = os.path.dirname(self.filepath)
    path = os.path.normpath(path)

    # Gets automatically updated per-action if self.use_actions is true,
    # otherwise it stays the same
    filepath = self.filepath

    with ProgressReport(context.window_manager) as progress:
        actions = []
        if self.use_actions:
            actions = bpy.data.actions
        else:
            actions = [bpy.context.object.animation_data.action]

        progress.enter_substeps(len(actions))

        for action in actions:
            if self.use_actions:
                filename = prefix + action.name + suffix + ".seanim"
                filepath = os.path.normpath(os.path.join(path, filename))

            progress.enter_substeps(1, action.name)
            try:
                export_action(self, context, progress, action, filepath)
            except Exception as e:
                progress.leave_substeps("ERROR: " + repr(e))
            else:
                progress.leave_substeps()

        progress.leave_substeps("Finished!")
