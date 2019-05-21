# ##### BEGIN BSD LICENSE BLOCK #####
#
# Copyright 2017 Funjack
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ##### END BSD LICENSE BLOCK #####

import bpy
from itertools import islice

def insert_actions(seq, actions, offset=0):
    """Insert into seq positions from the actions dict"""
    for a in actions:
        frame = ms_to_frame(a["at"]) + offset
        insert_position(seq, a["pos"], frame)

def insert_stroke(seq, stroke, offset=0):
    """Insert into seq positions from the stroke dict"""
    frame = offset
    for i, p in enumerate(stroke):
        frame = p["frame"] + offset
        if i == 0:
            # Do not override a keyframe at the start of the insert position.
            if launch_keyframe(seq.name, frame) is not None:
                continue
        # XXX Maybe we should also remove any keyframes that already exists in
        # the frame window of the new stroke?
        insert_position(seq, p["value"], frame)
    return frame

def insert_position(seq, position, frame):
    """Inserts in seq a keyframe with value position on frame."""
    seq["launch"] = position
    seq.keyframe_insert(data_path='["launch"]', frame=frame)

def delete_position(seq, frame):
    """Deletes from seq a keyframe on frame."""
    seq.keyframe_delete(data_path='["launch"]', frame=frame)

def repeat_stroke(seq, frame_current):
    """Repeat the last stroke on the current frame"""
    stroke = last_stroke(seq, frame_current)
    if stroke is None or len(stroke) < 3:
        return
    return insert_stroke(seq, stroke, frame_current)

def repeat_fill_stroke(seq, frame_end):
    """Fill the the last stroke before end_frame until end_frame."""
    stroke = last_stroke(seq, frame_end)
    if stroke is None or len(stroke) < 3:
        return
    frame = frame_end
    keyframes = launch_keyframes(seq.name)
    for kf in reversed(keyframes):
        frame = kf.co[0]
        if frame > frame_end:
            continue
        if frame <= frame_end:
            break
    return fill_stroke(seq, stroke, frame, frame_end)

def fill_stroke(seq, stroke, frame_start, frame_end):
    """Fill between frame_start and frame_end with stroke."""
    if stroke is None or len(stroke) < 3:
        return
    frame = frame_start
    while frame + stroke[-1]["frame"] < frame_end:
        frame = insert_stroke(seq, stroke, frame)
    return frame

def last_stroke(seq, since_frame):
    """Returns the last stroke since frame."""
    keyframes = launch_keyframes(seq.name)
    if keyframes is None:
        return
    stroke = []
    for kf in reversed(keyframes):
        frame = kf.co[0]
        value = kf.co[1]
        if frame > since_frame:
            continue
        if frame <= since_frame:
            stroke.append({"frame":frame, "value":value})
        if len(stroke) == 3:
            break
    if len(stroke) < 3:
        return
    startframe = stroke[1]["frame"] - stroke[2]["frame"]
    endframe = stroke[0]["frame"] - stroke[2]["frame"]
    return [ {"frame": 0, "value": stroke[2]["value"] },
             {"frame": startframe, "value": stroke[1]["value"] },
             {"frame": endframe, "value": stroke[0]["value"] } ]

def create_funscript(keyframes, inverted, range=90):
    """Create Funscript from keyframes."""
    script = []
    for kf in keyframes:
        time = frame_to_ms(int(kf.co[0]))
        if time < 0:
            continue
        value = clamp(int(kf.co[1]))
        script.append({"at": time, "pos": value})
    return {"version": "1.0", "inverted": inverted, "range": range, "actions": script}

def clamp(value):
    return 0 if value < 0 else 100 if value > 100 else value

def invert_launch_values(keyframes):
    for kf in keyframes:
        value = clamp(int(kf.co[1]))
        kf.co[1] = 100 - value

def shift_launch_values(keyframes):
    prev = None
    for kf in keyframes:
        if prev is None:
            prev = kf.co[1]
            continue
        new = prev
        prev = kf.co[1]
        kf.co[1] = new

def selected_keyframes(keyframe_points):
    """Generator that yields selected keyframes."""
    for k in keyframe_points:
        if k.select_control_point:
            yield k

def even_keyframes(keyframe_points):
    """Generator that yields all even keyframes."""
    for k in islice(keyframe_points, 0, None, 2):
        yield k

def odd_keyframes(keyframe_points):
    """Generator that yields all odd keyframes."""
    for k in islice(keyframe_points, 1, None, 2):
        yield k

def average_even_odd_keyframes(keyframe_points):
    """Average out all the even and odd frames in given points."""
    kp = list(keyframe_points)
    even = list(even_keyframes(kp))
    odd = list(odd_keyframes(kp))
    if len(even) > 0:
        even_avg = sum(int(k.co[1]) for k in even) / len(even)
        for k in even:
            k.co[1] = int(even_avg)
    if len(odd) > 0:
        odd_avg = sum(int(k.co[1]) for k in odd) / len(odd)
        for k in odd:
            k.co[1] = int(odd_avg)

def launch_keyframes(name):
    """Return all keyframes from all actions fcurves in prop 'launch'."""
    for a in bpy.data.actions:
        for f in a.fcurves:
            if f.data_path.endswith('["%s"]["launch"]' % name):
                return f.keyframe_points

def launch_keyframe(name, frame):
    """Returns the keyframe value at frame."""
    keyframes = launch_keyframes(name)
    for kf in keyframes:
        if kf.co[0] == frame:
            return kf.co[1]
    return None

def frame_to_ms(frame):
    """Returns time position in milliseconds for the given frame number."""
    scene = bpy.context.scene
    fps = scene.render.fps
    fps_base = scene.render.fps_base
    return round((frame-1)/fps*fps_base*1000)

def ms_to_frame(time):
    """Returns frame number for the given time position in milliseconds."""
    scene = bpy.context.scene
    fps = scene.render.fps
    fps_base = scene.render.fps_base
    return round(time/1000/fps_base*fps+1)

def launch_distance(speed, duration):
    """Returns the launch movement distance for given speed and time in ms."""  
    if speed <= 0 or duration <= 0:
        return 0
    time = pow(speed/25000, -0.95)
    diff = time - duration
    return 90 - int(diff/time*90)
