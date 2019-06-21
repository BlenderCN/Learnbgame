import bpy
from mathutils import *
from progress_report import ProgressReport, ProgressReportSubstep
import os
from . import seanim as SEAnim

# <pep8 compliant>

# This is the scale multiplier for exported anims
g_scale = 1  # TODO - Proper scaling

# A list (in order of priority) of bone names to automatically search for
# when determining which bone to use as the root for delta anims
# All entries in this list should be lowercase
DeltaRootBones = ["tag_origin"]


def first(a, b):
    """
        Compare two iterable objects
        compares each element in 'a' with every element in 'b'
        (Elements in 'a' are prioritized)
        Returns None if there is no match
    """
    for elem in a:
        if elem in b:
            return a
    return None


def ResolvePotentialAnimTypeOverride(bone, boneAnimModifiers):
    """
        Attempt to resolve the animType for a bone based on
         a given list of modifier bones
        Returns None if no override is needed
    """
    # + [bone]  # Add [bone] to the parent list if the modifier affects
    # a bone and its children instead of ONLY the children
    parents = bone.parent_recursive
    if len(parents) == 0 or len(boneAnimModifiers) == 0:
        return None

    for parent in parents:
        for modBone in boneAnimModifiers:
            if parent.name == modBone.name:
                # print("'%s' is (indirect) child of '%s'" %
                #       (bone.name, modBone.name))
                return modBone.modifier

    # print("'%s' ~default" % (bone.name))
    return None


def generate_fcurves(action_fcurves, tag_name, _type, count):
    '''
        'tag_name': The name of the pose bone to generate fcurves for
        '_type': The type of fcurve to add
                ex: 'location', 'rotation_quaternion', 'scale'
        'count': Number of fcurves to generate (should match up with the
                 number of channels for a given fcurve type)
        Returns a list of the generated fcurves
    '''
    return [action_fcurves.new(data_path='pose.bones["%s"].%s' %
                               (tag_name, _type),
                               index=index,
                               action_group=tag_name)
            for index in range(count)]


def load(self, context, filepath=""):
    ob = bpy.context.object
    if ob.type != 'ARMATURE':
        return "An armature must be selected!"

    path = os.path.dirname(filepath)
    path = os.path.normpath(path)

    try:
        ob.animation_data.action
    except:
        ob.animation_data_create()

    with ProgressReport(context.window_manager) as progress:
        # Begin the progress counter with 1 step for each file
        progress.enter_substeps(len(self.files))

        # Force all bones to use quaternion rotation
        # (Must be included or bone.rotation_quaternion won't update
        #  properly when setting the matrix directly)
        for bone in ob.pose.bones.data.bones:
            bone.rotation_mode = 'QUATERNION'

        for f in self.files:
            progress.enter_substeps(1, f.name)
            try:
                anim_path = os.path.normpath(os.path.join(path, f.name))
                load_seanim(self, context, progress, anim_path)
            except Exception as e:
                progress.leave_substeps("ERROR: " + repr(e))
            else:
                progress.leave_substeps()

        # Print when all files have been imported
        progress.leave_substeps("Finished!")


def load_seanim(self, context, progress, filepath=""):
    anim = SEAnim.Anim(filepath)

    # Import the animation data
    ob = bpy.context.object

    bpy.ops.object.mode_set(mode='POSE')

    actionName = os.path.basename(os.path.splitext(filepath)[0])
    action = bpy.data.actions.new(actionName)
    ob.animation_data.action = action
    ob.animation_data.action.use_fake_user = True

    scene = bpy.context.scene
    scene.render.fps = anim.header.framerate
    scene.frame_start = 0  # bpy.context.scene.frame_current
    scene.frame_end = scene.frame_start + anim.header.frameCount - 1

    # Import the actual keyframes
    progress.enter_substeps(anim.header.boneCount)

    # Look up table that we use to get a given bone by name
    # without having to worry about casing
    bone_map = {}
    for bone in ob.pose.bones:
        name = bone.name.lower()
        if name in bone_map:
            print("Warning: Bone name conflict for '%s'\n" % name)
        bone_map[bone.name.lower()] = bone

    for i, tag in enumerate(anim.bones):
        try:
            # Attempt to resolve the root bone name (if it doesn't have one)
            # based on the prioritized DeltaRootBones array
            if(len(tag.name) == 0 and
               anim.header.animType == SEAnim.SEANIM_TYPE.SEANIM_TYPE_DELTA):
                root = first(DeltaRootBones,
                             [bone.name.lower() for bone in ob.pose.bones])
                if root is not None:
                    tag.name = root
            bone = bone_map[tag.name.lower()]
        except:
            pass
        else:
            animType = ResolvePotentialAnimTypeOverride(
                bone, anim.boneAnimModifiers)
            if animType is None:
                animType = anim.header.animType

            # Import the position keyframes
            if len(tag.posKeys):
                bone.matrix_basis.identity()

                fcurves = generate_fcurves(action.fcurves, bone.name,
                                           'location', 3)
                keyCount = len(tag.posKeys)
                for axis, fcurve in enumerate(fcurves):
                    fcurve.color_mode = 'AUTO_RGB'
                    # Add an extra keyframe for the control keyframe
                    fcurve.keyframe_points.add(keyCount + 1)
                    # Add the control keyframe # Can be changed to Vector((-1,
                    # 0)) because Location 0,0,0 is rest pos
                    fcurve.keyframe_points[0].co = Vector(
                        (-1, bone.location[axis]))

                for k, key in enumerate(tag.posKeys):
                    # Currently the conversion is only here because I never
                    # added scaling options for Blender-CoD
                    offset = Vector(key.data) * g_scale

                    # Viewanims are SEANIM_TYPE_ABSOLUTE - But all children of
                    # j_gun has a SEANIM_TYPE_RELATIVE override
                    if (animType == SEAnim.SEANIM_TYPE.SEANIM_TYPE_ABSOLUTE and
                            bone.parent is not None):
                        bone.matrix.translation = bone.parent.matrix * offset
                    else:  # Use DELTA / RELATIVE results (ADDITIVE is unknown)
                        bone.matrix_basis.translation = offset

                    # bone.keyframe_insert("location", index=-1, frame=key.frame, group=tag.name)  # nopep8
                    for axis, fcurve in enumerate(fcurves):
                        fcurve.keyframe_points[k + 1].co = Vector((key.frame, bone.location[axis]))  # nopep8
                        fcurve.keyframe_points[k + 1].interpolation = 'LINEAR'

                # Update the FCurves
                for fc in fcurves:
                    fc.update()

            # Import the rotation keyframes
            if len(tag.rotKeys):
                bone.matrix_basis.identity()

                fcurves = generate_fcurves(action.fcurves, bone.name,
                                           'rotation_quaternion', 4)
                keyCount = len(tag.rotKeys)
                for axis, fcurve in enumerate(fcurves):
                    fcurve.color_mode = 'AUTO_YRGB'
                    # Add an extra keyframe for the control keyframe
                    fcurve.keyframe_points.add(keyCount + 1)
                    fcurve.keyframe_points[0].co = Vector(
                        (-1, [1, 0, 0, 0][axis]))  # Add the control keyframe

                for k, key in enumerate(tag.rotKeys):
                    # Convert the Quaternion to WXYZ
                    quat = Quaternion(
                        (key.data[3], key.data[0], key.data[1], key.data[2]))
                    angle = quat.to_matrix().to_3x3()

                    bone.matrix_basis.identity()
                    try:
                        bone.parent.matrix
                    except:
                        # I don't actually remember why this is here - probably
                        # to set the root bone(s) to its rest pos / angle
                        bone.matrix_basis.identity()
                        mat = angle.to_4x4()
                    else:
                        mat = (bone.parent.matrix.to_3x3() * angle).to_4x4()

                    bone.matrix = mat

                    quat = bone.rotation_quaternion
                    for axis, fcurve in enumerate(fcurves):
                        # bone.rotation_quaternion[axis]
                        fcurve.keyframe_points[k + 1].co = Vector((key.frame, quat[axis]))  # nopep8
                        fcurve.keyframe_points[k + 1].interpolation = 'LINEAR'

                # Update the FCurves
                for fc in fcurves:
                    fc.update()

            # Import the scale keyframes
            if len(tag.scaleKeys):
                bone.matrix_basis.identity()

                fcurves = generate_fcurves(action.fcurves, bone.name,
                                           'scale', 3)
                keyCount = len(tag.scaleKeys)
                for axis, fcurve in enumerate(fcurves):
                    fcurve.color_mode = 'AUTO_RGB'
                    # Add an extra keyframe for the control keyframe
                    fcurve.keyframe_points.add(keyCount + 1)
                    fcurve.keyframe_points[0].co = Vector(
                        (-1, bone.scale[axis]))  # Add the control keyframe

                for k, key in enumerate(tag.scaleKeys):
                    scale = Vector(key.data)

                    for axis, fcurve in enumerate(fcurves):
                        fcurve.keyframe_points[
                            k + 1].co = Vector((key.frame, scale[axis]))
                        fcurve.keyframe_points[k + 1].interpolation = 'LINEAR'

                # Update the FCurves
                for fc in fcurves:
                    fc.update()

            frame = scene.frame_start - 1
            bone.keyframe_delete(data_path="location",
                                 frame=frame, group=tag.name)
            bone.keyframe_delete(data_path="rotation_quaternion",
                                 frame=frame, group=tag.name)
            bone.keyframe_delete(data_path="scale",
                                 frame=frame, group=tag.name)

            # Remove any leftover temporary transformations for this bone
            bone.matrix_basis.identity()

        progress.step()
    progress.leave_substeps()

    # Notetracks
    for note in anim.notes:
        notetrack = ob.animation_data.action.pose_markers.new(note.name)
        notetrack.frame = note.frame

    bpy.context.scene.update()
    bpy.ops.object.mode_set(mode='POSE')
