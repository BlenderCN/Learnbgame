import json
import bpy
import os

cd =  "D:\\Emailing untitled_detailed.zip\\untitled_detailed"

def frame_to_time(frame_number):
    raw_time = (frame_number - 1) / fps
    return round(raw_time, 3)

scene = bpy.context.scene

fps = scene.render.fps
fps_base = scene.render.fps_base

data = []
for k, v in scene.timeline_markers.items():
    frame = v.frame
    frame_time = frame_to_time(frame)
    data.append({"frame": frame, "frame_time": frame_time })

with open( cd + '\\data.json', 'w') as f:
  json.dump(data, f, ensure_ascii=False)