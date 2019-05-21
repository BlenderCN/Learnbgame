import bpy
from bpy.app.handlers import persistent

bl_info = {
    "name": "Playback Once",
    "author": "Adhi Hargo",
    "version": (1, 0, 0),
    "blender": (2, 67, 3),
    "location": "",
    "description": "Playback once.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

@persistent
def stopPlaybackAtEnd(scene):
    if scene.frame_current >= scene.frame_end:
        bpy.ops.screen.animation_cancel()

def register():
    bpy.app.handlers.frame_change_pre.append(stopPlaybackAtEnd)

def unregister():
    bpy.app.handlers.frame_change_pre.remove(stopPlaybackAtEnd)
    
if __name__ == "__main__":
    register()
