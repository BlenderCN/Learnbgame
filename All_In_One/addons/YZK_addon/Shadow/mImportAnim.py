#
# @file    tools/plugin/blender/Shadow/mImportAnim.py
# @author  Luke Tokheim, luke@motionshadow.com
# @version 2.5
#
# (C) Copyright Motion Workshop 2017. All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Motion Workshop, which is protected by
# US federal copyright law and by international treaties.
#
# The Data may not be disclosed or distributed to third parties, in whole
# or in part, without the prior written consent of Motion Workshop.
#
# The Data is provided "as is" without express or implied warranty, and
# with no claim as to its suitability for any purpose.
#

import bpy
import bpy_extras.io_utils


class mImportAnim:
    """
    Helper class to load our CSV stream file into animation curves. Perform
    string name matching the same as the Shadow live-streaming addon. Expects
    a preloaded scene that contains the Shadow armature.

    Loads the take data into a new armature action starting at frame 1. The
    Blender scene frame rate is not modified.
    """
    # Enum for bpy.types.Keyframe.interpolation
    KEYFRAME_INTERPOLATION = 'CONSTANT'  # or LINEAR

    def load(self, operator, context, filepath=""):
        """
        Read the Shadow Animation data file in CSV format. This expects the
        stream format which contains the local rotations in quaternion format.
        """
        fieldnames = None
        data = None
        try:
            csvfile = open(filepath)

            import csv
            reader = csv.reader(csvfile)
            fieldnames = next(reader)

            # Load all of the rows into memory. This allows us to pre-allocate
            # the animation curves. This is faster than the alternative of
            # scanning rows and inserting a frame for each row into each curve.
            data = list(reader)
        except Exception as e:
            import traceback
            traceback.print_exc()

            operator.report(
                {'ERROR'}, "Failed to open file %r (%s)" % (filepath, e))
            return {'CANCELLED'}

        num_frame = len(data)

        # Conversion factor from seconds (CSV time) to Blender frames.
        frame_time = (
            float(context.scene.render.fps) / context.scene.render.fps_base)
        # The CSV frames times are 0 based. Shift forward to match Blender.
        frame_offset = 1.0

        curve_list, time_i = self.make_curve_list(
            context, fieldnames, num_frame)

        for index in range(num_frame):
            row = data[index]
            if time_i is None:
                frame = float(index) * frame_time * 0.01 + frame_offset
            else:
                frame = float(row[time_i]) * frame_time + frame_offset

            for i in range(len(curve_list)):
                if curve_list[i] is None:
                    continue

                value = float(row[i])

                if num_frame > 0:
                    curve_list[i].keyframe_points[index].co = (frame, value)
                else:
                    curve_list[i].keyframe_points.insert(
                        frame, value, options={'FAST'}
                    ).interpolation = self.KEYFRAME_INTERPOLATION

        return {'FINISHED'}

    def make_armature_action(self, context, name):
        """
        Find the armature object either by current selection or by the canned
        name "Hips". Create a new action to store the animation curves.
        """
        armature = context.object
        if armature is None:
            armature = context.scene.objects.get(name)

        if armature is None:
            operator.report(
                {'ERROR'}, "Failed to find armature named (%s)" % name)
            return None, None

        if 'ARMATURE' != armature.type:
            operator.report(
                {'ERROR'},
                "Selected object is not an armature (%s)" % armature.name)
            return None, None

        armature.animation_data_create()
        action = bpy.data.actions.new(name="take")
        armature.animation_data.action = action

        return armature, action

    def make_curve_list(self, context, fieldnames, num_frame):
        """
        Create a flat list of animation curves, one per column in the CSV file.
        Indicate an unused column/channel with a None value. If we have a
        number of frames then preallocate the keyframes since we have a MxN
        table/matrix of key values.
        """
        channel_list = ["Lqw", "Lqz", "Lqx", "Lqy", "cz", "cx", "cy"]

        armature, action = self.make_armature_action(context, "Body")

        time_i = None
        curve_list = [None] * len(fieldnames)
        for i in range(len(fieldnames)):
            fieldname = fieldnames[i]

            if "time" == fieldname:
                time_i = i
                continue

            if "." not in fieldname:
                continue

            # Channel names in CSV are something like "Hips.Lqw".
            name, channel = fieldname.split(".", 2)

            # Skip channels that we are not going to connect to an animation
            # curve.
            if channel not in channel_list:
                continue

            # Find the bone by name in our armature.
            obj = armature.pose.bones.get(name)
            if obj is None:
                continue

            # Mapping from the channel name to the curve index within the
            # Blender curve data path. For example, Lqw is index 0:
            #   Lqw -> pose.bones['name'].rotation_quaternion[0]
            index = channel_list.index(channel)

            is_translate = index > 3
            if is_translate and not name.startswith("Hips"):
                continue

            if is_translate:
                data_path = ('pose.bones["%s"].location' % name)
                index = index - 4
            else:
                data_path = ('pose.bones["%s"].rotation_quaternion' % name)

            curve = action.fcurves.new(data_path=data_path, index=index)
            if num_frame > 0:
                curve.keyframe_points.add(num_frame)
                for keyframe in curve.keyframe_points:
                    keyframe.interpolation = self.KEYFRAME_INTERPOLATION

            curve_list[i] = curve

        return curve_list, time_i

#
# END class mImportAnim
#


class ImportAnimOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """
    Add our Shadow take importer to the File > Import Blender menu.
    """
    bl_idname = "import_anim.shadow"
    bl_label = "Import Shadow Animation"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".csv"
    filter_glob = bpy.props.StringProperty(default="*.csv", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        """
        Require that the user selects an armature before sending this command.
        """
        obj = context.object
        return obj and obj.type == 'ARMATURE'

    def execute(self, context):
        """
        Load the filepath keyword and import the CSV animation file now.
        """
        keywords = self.as_keywords(ignore=("filter_glob",))

        return mImportAnim().load(self, context, **keywords)

#
# END class ImportAnimOperator
#
