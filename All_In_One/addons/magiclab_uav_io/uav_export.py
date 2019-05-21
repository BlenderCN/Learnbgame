import bpy
import csv
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator


class ExportCSVLocations(Operator, ExportHelper):
    """Export Object Locations as CSV"""
    bl_idname = "object.magiclab_uav_export"
    bl_label = "Magiclab Export CSV Locations"

    filename_ext = ".csv"

    filter_glob = StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            maxlen=255)

    @classmethod
    def poll(cls, context):
        return True if context.selected_objects else False

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
        ob_glows = {ob.name:[] for ob in obs}
        for ob in obs:
            frames = get_frames(ob)
            glow_curves = [
                fc for fc in ob.animation_data.action.fcurves
                if fc.data_path in ('glow', '["glow"]')]
            if glow_curves:
                glow_curve = glow_curves[0]
                for keyframe in glow_curve.keyframe_points:
                    ob_glows[ob.name].append([
                    '', '', '',
                    keyframe.co[0],
                    keyframe.co[1],
                    ''])
            ob_frames[ob.name] = sorted(frames, key=lambda x: x[0])
            total_frames = total_frames.union(frames)
        total_frames = sorted(total_frames, key=lambda x:x[0])
        for frame in total_frames:
            scene.frame_set(frame[0]) # slow but robust
            for ob in obs:
                if frame in ob_frames[ob.name]:
                    index = ob_frames[ob.name].index(frame)
                    ob_frames[ob.name][index] = [
                        ob.location[0],
                        ob.location[1],
                        ob.location[2],
                        frame[0],
                        '', # will be filled with glow potentially
                        frame[1]]

        # merge ob_frames and ob_glows (location and glow keyframes)
        # ob_frames = {ob.name: [(x,y,z,frame, None, type),],}
        # ob_glows = {ob.name: [(None, None, None, frame, glow, None),])
        # ob_frames final should be {ob.name:}
        for ob in obs:
            location_frames = ob_frames[ob.name]
            glow_frames = ob_glows[ob.name]
            frames_from_locs = [f[3] for f in location_frames]
            removals = []
            for i, glow_frame in enumerate(glow_frames):
                if glow_frame[3] in frames_from_locs:
                    index = frames_from_locs.index(glow_frame[3])
                    location_frames[index][4] = glow_frame[4] # found it!!!!
                    removals.append(i)
            for i in reversed(removals):
                glow_frames.pop(i)
            location_frames.extend(glow_frames)
            location_frames.sort(key=lambda x:x[3]) # not working???
            for location_frame in location_frames:
                location_frame[3] = (
                    location_frame[3] - start_frame) / frames_per_second
            ob_frames[ob.name] = location_frames
        with open(self.filepath, 'w', newline='') as csvfile:
            uavwriter = csv.writer(
                csvfile, delimiter =',', quoting=csv.QUOTE_MINIMAL)
            uavwriter.writerow([
                "id", "x[m]", "y[m]", "z[m]", "type", "glow", "t[s]"])
            for ob_name, ob_data in ob_frames.items():
                for datum in ob_data:
                    uavwriter.writerow(
                        [ob_name] +
                        [d for d in datum[:3]] +
                        [datum[5],
                        datum[4],
                        "{0:.2f}".format(datum[3])])

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(
        ExportCSVLocations.bl_idname, text="magiclab way-point export")


def register():
    bpy.utils.register_class(ExportCSVLocations)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(ExportCSVLocations)

