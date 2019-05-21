bl_info = {
"name": "Spike Eraser",
"author": "Sebastian Koenig, Andreas Schuster",
"version": (1, 0),
"blender": (2, 7, 2),
"location": "Clip Editor > Spike Eraser",
"description": "Filter out spikes in tracker curves",
"warning": "",
"wiki_url": "",
"tracker_url": "",
"category": "Learnbgame"
}



import bpy

from bpy.props import *

from mathutils import Vector



def filter_values(threshold, context):

    scene = bpy.context.scene
    frameStart = scene.frame_start
    frameEnd = scene.frame_end
    sc = context.space_data
    clip = sc.clip

    print( frameStart, "to", frameEnd )


    clean_up_list=[]
    for i in range(frameStart,frameEnd):

        print("Frame: ", i)

        # get clean track list of valid tracks
        trackList = list(filter( lambda x: (x.markers.find_frame(i) and x.markers.find_frame(i-1)), clip.tracking.tracks))

        # get average velocity and deselect track
        averageVelocity = Vector().to_2d()
        for t in trackList:
            t.select = False
            marker = t.markers
            averageVelocity += 1000.0*(marker.find_frame(i).co - marker.find_frame(i-1).co)

        averageVelocity = averageVelocity / float(len(trackList))


        # now compare all markers with average value and store in clean_up_list
        for t in trackList:
            marker = t.markers
            # get velocity from current track
            tVelocity = 1000.0*(marker.find_frame(i).co - marker.find_frame(i-1).co)
            # create vector between current velocity and average and calc length
            distance = (averageVelocity-tVelocity).magnitude

            # if length greater than threshold add to list
            if distance > threshold and not t in clean_up_list:
                print( "Add Track:" , t.name, "Average Velocity:", averageVelocity.x, averageVelocity.y, "Distance:", distance )
                clean_up_list.append(t)


    for t in clean_up_list:
        t.select = True
    return (len(clean_up_list))


class CLIP_OT_filter_tracks(bpy.types.Operator):
    bl_idname="clip.filter_tracks"
    bl_label="Filter Tracks"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'CLIP_EDITOR') and sc.clip


    def execute(self, context):
        scn = bpy.context.scene
        tracks = filter_values(scn.track_threshold, context)
        self.report({"INFO"}, "Identified %d faulty tracks" % tracks)
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
    bpy.utils.unregister_class(CLIP_PT_filter_tracks)
    bpy.utils.unregister_class(CLIP_OT_filter_tracks)

if __name__ == "__main__":
    register()
