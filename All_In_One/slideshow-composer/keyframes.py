import bpy
import re

def get_fcurves_for_sequence(sequence):
    """ Gets all fcurves associated with the given sequence

    This function can be very slow since it iterates over all fcurves of every sequence.
    :param sequence: Sequence for which the fcurves will be looked up
    :return: List of found fcurves. The list will be empty if no fcurves were found
    """
    fcurves = []
    sequence_name = sequence.name

    if bpy.context.scene.animation_data is None:
        return fcurves

    if bpy.context.scene.animation_data.action is None:
        return fcurves

    # example fcurve data_path: 'sequence_editor.sequences_all["Transform"].scale_start_x'
    # we want to extract the sequence name - 'Transform'
    regex = re.compile(pattern=".*\[\"{}\"\]".format(sequence_name))
    for fcurve in bpy.context.scene.animation_data.action.fcurves:
        if regex.match(fcurve.data_path):
            fcurves.append(fcurve)

    return fcurves

def get_fcurve_data_path_property(fcurve):
    """ Gets fcurve's data path property

    Example fcurve's data_path: 'sequence_editor.sequences_all["Transform"].scale_start_x'
    For that example path this function will return 'scale_start_x'
    :param fcurve: Fcurve instance to get data path from
    :return: The last component of data path defining actual property name
    """

    # we want to extract last part - data path
    data_path_full = fcurve.data_path
    last_dot_index = data_path_full.rfind(".")
    return data_path_full[(last_dot_index+1):]

def get_frame_number(keyframe_point):
    return keyframe_point.co[0]

def delete_keyframes(sequence, group=None):
    """ Deletes all keyframes associated with the given sequence

    :param sequence: Sequence to remove keyframes for
    :param group: Delete only keyframes of fcurves with the specified group name
    """
    fcurves = get_fcurves_for_sequence(sequence)

    for fcurve in fcurves:
        if group is not None:
            if fcurve.group.name != group:
                print("Skipping fcurve with group:{}".format(fcurve.group))
                continue

        fcurve_data_path = get_fcurve_data_path_property(fcurve)
        while len(fcurve.keyframe_points) > 0:
            keyframe_point = fcurve.keyframe_points[0]
            frame_number = get_frame_number(keyframe_point)
            result = sequence.keyframe_delete(fcurve_data_path, frame=frame_number)
            print("Removing keyframe at frame:{} data_path:{} result:{}".format(frame_number, fcurve_data_path, result))