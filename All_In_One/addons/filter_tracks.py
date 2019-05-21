bl_info = {
  "name": "Filter Tracks",
  "author": "Sebastian Koenig, Andreas Schuster",
  "version": (1, 0),
  "blender": (2, 7, 2),
  "location": "Clip Editor > Filter Tracks",
  "description": "Filter out spikes in tracker curves",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Movie Tracking"
  }

import bpy
from bpy.props import *
from mathutils import Vector

def log(*args):
  print(''.join(map(str, args)))

def get_marker_coordinates_in_pixels(context, track, frame_number):
    width, height = context.space_data.clip.size
    marker = track.markers.find_frame(frame_number)
    return Vector((marker.co[0] * width, marker.co[1] * height))

def marker_velocity(context, track, frame):
    marker_a = get_marker_coordinates_in_pixels(context, track, frame)
    marker_b = get_marker_coordinates_in_pixels(context, track, frame - 1)
    return marker_a - marker_b

def filter_values(threshold, context):
    scene = bpy.context.scene
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    clip = context.space_data.clip
    length = clip.frame_duration
    width, height = clip.size
    log('Clip size:', Vector((width, height)))
    log('Clean from frame', frame_start, 'to', frame_end, ';', length, 'frames')

    bpy.ops.clip.clean_tracks(frames=10, action='DELETE_TRACK')

    tracks_to_clean = []

    for frame in range(frame_start, frame_end):
        log('Frame: ', frame)
        # TODO(sebastian_k): What about frame_start = 0?

        # Find tracks with markers in both this frame and the previous one.
        relevant_tracks = [track for track in clip.tracking.tracks
                           if track.markers.find_frame(frame) and
                              track.markers.find_frame(frame - 1)]

        if not relevant_tracks:
            # log('Skipping frame; no tracks with markers in this and the previous frame')
            continue

        # Get average velocity and deselect track.
        average_velocity = Vector().to_2d()
        for track in relevant_tracks:
            track.select = False
            average_velocity += marker_velocity(context, track, frame)
        average_velocity = average_velocity / float(len(relevant_tracks))

        # log('Average velocity', average_velocity.magnitude)

        # Then find all markers that behave differently than the average.
        for track in relevant_tracks:
            track_velocity = marker_velocity(context, track, frame)
            distance = (average_velocity - track_velocity).magnitude

            # TODO: find a way to exclude foreground markers. something like:
            # if markers are part of the tracks_to_clean list but move very similarly,
            # they are no spikes, but fast moving foreground markers and should be excluded.

            if distance > threshold and not track in tracks_to_clean:
                log('To clean:' , track.name,
                    ', average velocity:', average_velocity.magnitude,
                    'distance:', distance)
                tracks_to_clean.append(track)

    for track in tracks_to_clean:
        track.select = True
    return len(tracks_to_clean)

class CLIP_OT_filter_tracks(bpy.types.Operator):
    bl_idname="clip.filter_tracks"
    bl_label="Filter Tracks"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'CLIP_EDITOR') and sc.clip

    def execute(self, context):
        num_tracks = filter_values(bpy.context.scene.track_threshold, context)
        self.report({"INFO"}, "Identified %d faulty tracks" % num_tracks)
        return {'FINISHED'}

class CLIP_PT_filter_tracks(bpy.types.Panel):
    bl_idname = "clip.filter_track_panel"
    bl_label = "Filter Tracks"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Track"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("clip.filter_tracks")
        layout.prop(scene, "track_threshold")

def register():
    bpy.utils.register_class(CLIP_OT_filter_tracks)
    bpy.utils.register_class(CLIP_PT_filter_tracks)
    bpy.types.Scene.track_threshold = bpy.props.FloatProperty \
      (
        name = "Track Threshold",
        description = "Filter Threshold",
        default = 5.0
      )

def unregister():
    bpy.utils.unregister_class(CLIP_OT_filter_tracks)
    bpy.utils.unregister_class(CLIP_PT_filter_tracks)

if __name__ == "__main__":
    register()
