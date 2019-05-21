from mathutils import Vector
import bpy
import itertools
import re
from collections import defaultdict

bl_info = {
    "name": "Resolve Camera Tracks",
    "author": "Anthony Zhang",
    "category": "Animation",
    "version": (1, 1),
    "blender": (2, 75, 0),
    "location": "View3D > Object > Resolve Camera Tracks or Search > Resolve Camera Tracks",
    "description": "3D point reconstruction from multiple camera angles",
}

class ResolveCameraTracks(bpy.types.Operator):
    bl_idname = "animation.resolve_camera_tracks"
    bl_label = "Resolve Camera Tracks"
    bl_options = {"REGISTER", "UNDO"}  # enable undo for operator

    def execute(self, context):
        targets = []
        for obj in context.selected_objects:
            if obj.type == "EMPTY":
                targets.append(obj)
            else:
                self.report({"ERROR_INVALID_INPUT"}, "Non-empty object \"{}\" selected".format(obj.name))
                return {"CANCELLED"}

        # associate pairs of empties together by base name
        targets_by_track_name = defaultdict(list)
        for target in targets:
            track, _ = self.get_target_track(target)
            targets_by_track_name[track.name].append(target)
        for name, point_targets in targets_by_track_name.items():
            if len(point_targets) < 2:
                self.report({"ERROR_INVALID_INPUT"}, "At least two objects associated with tracks named \"{}\" required, only one selected".format(name))
                return {"CANCELLED"}

        # add the resolved empties
        resolved_empties = []
        for point_targets in targets_by_track_name.values():
            try:
                resolved_empties.append(self.add_resolved_empty(point_targets))
            except Exception as e:
                import traceback
                self.report({"ERROR_INVALID_INPUT"}, traceback.format_exc())
                return {"CANCELLED"}

        # select the resolved empties
        bpy.ops.object.select_all(action="DESELECT")
        for empty in resolved_empties: empty.select = True

        return {"FINISHED"}

    def get_target_track(self, target):
        """
        Returns a motion tracking track associated with object `target` and the camera associated with object `target`.
        """
        # find the follow track constraint and obtain the associated track
        for constraint in target.constraints:
            if constraint.type == "FOLLOW_TRACK":
                track_constraint = constraint
                if not track_constraint.clip:
                    raise Exception("Clip for constraint \"{}\" of \"{}\" not found".format(track_constraint, target.name))
                break
        else:
            raise Exception("Follow Track constraint for \"{}\" not found".format(target.name))

        # get the track for the track constraint on the target
        for track in track_constraint.clip.tracking.tracks:
            if track.name == track_constraint.track:
                return track, track_constraint.camera
        raise Exception("Track for constraint \"{}\" of \"{}\" not found".format(track_constraint, target.name))

    def get_target_locations(self, target):
        """
        Returns a list of positions in world space for object `target` for frames that it is animated for (and None for frames that are not), the camera associated with object `target`, the start frame, and the end frame.
        """
        track, camera = self.get_target_track(target)

        # obtain track information
        marker_frames = {marker.frame for marker in track.markers if not marker.mute} # set of frame indices for enabled markers
        start_frame, end_frame = min(marker_frames), max(marker_frames)

        original_frame = bpy.context.scene.frame_current # save the frame so we can restore it later

        # store object world locations for each frame
        locations = []
        for i in range(start_frame, end_frame + 1):
            if i in marker_frames:
                bpy.context.scene.frame_set(i)
                locations.append(target.matrix_world.to_translation())
            else:
                locations.append(None)

        bpy.context.scene.frame_set(original_frame) # move back to the original frame

        return locations, camera, start_frame, end_frame

    def add_resolved_empty(self, targets):
        """
        Adds an empty animated to be at the point closest to every target in `targets`, where each target in `targets` is animated by a Follow Track constraint.

        Returns the newly created empty.
        """

        # obtain target information
        target_points, target_cams, target_starts, target_ends = [], [], [], []
        for target in targets:
            points, cam, start, end = self.get_target_locations(target)
            target_points.append(points + [None]) # the last element must be None
            target_cams.append(cam)
            target_starts.append(start)
            target_ends.append(end)

        if len(set(target_cams)) < 2: # two camera is the minimum number of cameras
            raise Exception("At least 2 cameras need to be available")

        # add the empty object
        bpy.ops.object.add(type="EMPTY")
        resolved = bpy.context.active_object

        original_frame = bpy.context.scene.frame_current # save the frame so we can restore it later

        # set up keyframes for each location
        min_distance, min_distance_frame = float("inf"), None
        max_distance, max_distance_frame = 0, None
        for frame in range(min(target_starts), max(target_ends)):
            # clamp indices to the last value, None, if outside of range
            indices = []
            for start, end in zip(target_starts, target_ends):
                index = frame - start
                indices.append(-1 if index < 0 or index > end - start else index)

            bpy.context.scene.frame_set(frame) # move to the current frame

            # go through each possible combination of targets and find the one that gives the best result
            best_location, best_distance = None, float("inf")
            for pair in itertools.combinations(range(0, len(targets)), 2):
                first, second = pair[0], pair[1]
                cam1, cam2 = target_cams[first].location, target_cams[second].location
                location1, location2 = target_points[first][indices[first]], target_points[second][indices[second]]
                if location1 is not None and location2 is not None:
                    location, distance = closest_point(cam1, cam2, location1, location2)
                    if distance < best_distance: # better result than current best
                        best_distance = distance
                        best_location = location

            # add keyframe if possible
            if best_location != None:
                resolved.location = best_location
                resolved.keyframe_insert(data_path="location")

                if best_distance <= min_distance:
                    min_distance = best_distance
                    min_distance_frame = frame
                if best_distance >= max_distance:
                    max_distance = best_distance
                    max_distance_frame = frame

        bpy.context.scene.frame_set(original_frame) # move back to the original frame

        # make the resolved track object more identifiable
        track, _ = self.get_target_track(targets[0])
        resolved.name = "{}_tracked".format(track.name)
        resolved.empty_draw_type = "SPHERE"
        resolved.empty_draw_size = 0.1

        self.report({"INFO"}, "{}: min error {} (frame {}), max error {} (frame {})".format(resolved.name, min_distance / 2, min_distance_frame, max_distance / 2, max_distance_frame))
        return resolved

def closest_point(cam1, cam2, point1, point2):
    """
    Produces the point closest to the lines formed from `cam1` to `point1` and from `cam2` to `point2`, and the total distance between this point and the lines.

    Reference: http://www.gbuffer.net/archives/361
    """
    dir1 = point1 - cam1
    dir2 = point2 - cam2
    dir3 = cam2 - cam1
    a = dir1 * dir1
    b = -dir1 * dir2
    c = dir2 * dir2
    d = dir3 * dir1
    e = -dir3 * dir2
    if abs((c * a) - (b ** 2)) < 0.0001: # lines are nearly parallel
        raise Exception("Lines are too close to parallel")
    extent1 = ((d * c) - (e * b)) / ((c * a) - (b ** 2))
    extent2 = (e - (b * extent1)) / c
    point1 = cam1 + (extent1 * dir1)
    point2 = cam2 + (extent2 * dir2)
    return (point1 + point2) / 2, (point1 - point2).magnitude

def add_object_button(self, context):
    self.layout.operator(ResolveCameraTracks.bl_idname,
        text="Resolve Camera Tracks", icon="PLUGIN")

def register():
    bpy.utils.register_class(ResolveCameraTracks)
    bpy.types.VIEW3D_MT_object.append(add_object_button)

def unregister():
    bpy.utils.unregister_class(ResolveCameraTracks)
    bpy.types.VIEW3D_MT_object.remove(add_object_button)

if __name__ == "__main__":
    register()