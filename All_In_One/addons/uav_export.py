bl_info = {
    "name": "UAV Export",
    "author": "Bassam Kurdali",
    "version": (0, 4),
    "blender": (2, 78, 0),
    "location": "File->Export->Export CSV UAV Data",
    "description": "Export selected object locations/frames for UAV control",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

import bpy
import csv
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportCSVLocations(Operator, ExportHelper):
    """Export Object Locations as CSV"""
    bl_idname = "object.export_csv_locations"
    bl_label = "Export CSV Locations"

    filename_ext = ".csv"

    filter_glob = StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            maxlen=255)

    def execute(self, context):
        """ build csv list based on selected object location keyframes"""
        scene = context.scene
        frames_per_second = scene.render.fps / scene.render.fps_base
        start_frame = scene.frame_start
        end_frame = scene.frame_end

        def is_location_keyed(ob):
            """ Only works on location keyframed objects """
            if not ob.animation_data or not ob.animation_data.action:
                return False
            if any(
                    fc.data_path == 'location'
                    for fc in ob.animation_data.action.fcurves):
                return True
            return False
        obs = [ob for ob in context.selected_objects if is_location_keyed(ob)]

        def get_frames(ob):
            """ returns location keyframe times """
            types = {"BEZIER":0, "LINEAR":1, "CONSTANT":2}
            frames = set()
            action = ob.animation_data.action
            fcurves = (
                fc for fc in action.fcurves if 'location' == fc.data_path)
            for fc in fcurves:
                for keyframe in fc.keyframe_points:
                    frame = keyframe.co[0]
                    if frame >= start_frame and frame <= end_frame:
                        frames.add((frame, types[keyframe.interpolation]))
            return frames

        # we want to limit number of samples, so some excess precalculations
        total_frames = set()
        ob_frames = {ob.name:None for ob in obs}
        for ob in obs:
            frames = get_frames(ob)
            ob_frames[ob.name] = sorted(frames, key=lambda x: x[0]) 
            total_frames = total_frames.union(frames)
        total_frames = sorted(total_frames, key=lambda x:x[0])
        for frame in total_frames:
            scene.frame_set(frame[0]) # slow but robust
            for ob in obs:
                if frame in ob_frames[ob.name]:
                    index = ob_frames[ob.name].index(frame)
                    ob_frames[ob.name][index] = (
                        ob.location[0],
                        ob.location[1],
                        ob.location[2],
                        (frame[0] - start_frame) / frames_per_second,
                        frame[1])
        with open(self.filepath, 'w', newline='') as csvfile:
            uavwriter = csv.writer(
                csvfile, delimiter =',', quoting=csv.QUOTE_MINIMAL)
            uavwriter.writerow(["id", "x[m]", "y[m]", "z[m]", "t[s]", "type"])
            for ob_name, ob_data in ob_frames.items():
                for datum in ob_data:
                    uavwriter.writerow(
                        [ob_name] + 
                        [d for d in datum[:3]] +
                        ["{0:.2f}".format(datum[3]),
                        datum[4]])

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(
        ExportCSVLocations.bl_idname, text="Export CSV UAV Data")


def register():
    bpy.utils.register_class(ExportCSVLocations)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportCSVLocations)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
