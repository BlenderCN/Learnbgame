
import bpy

progress = 0
def add(x=1):
    global progress
    progress += x
    bpy.context.window_manager.progress_update(progress)

def reset():
    global progress
    progress = 0
