import bpy
import socket
import sys

from bpy.app.handlers import persistent

def custom_metadata():
    scn=bpy.context.scene
    name = socket.gethostname()
    note = "Samples: " + str(scn.cycles.samples)
    note += ", Host: " + name
    note += ", OS: " + sys.platform
    note += ", Compute: " + scn.cycles.device
    scn.render.stamp_note_text = note
    scn.render.use_stamp_note = True

@persistent
def nd_render_handler(scene):
    custom_metadata()