import bpy
import math
import random
import BlenderManager

VERSION = 'Default'

def BaseAction(frames, armature):
    BlenderManager.insertAction('Idle', 0, len(frames))

def HeadAnimation(frames, armature):
    print(frames)
    intervals = BlenderManager.getLabelIntervals('Head', '1', frames, threshold=2)
    print(intervals)
    for (start, end) in intervals:
        BlenderManager.insertAction('MoveHead_left', start, end, smooth_frames=5)
        BlenderManager.insertAction('talking', start, end, smooth_frames=5)
        
    intervals = BlenderManager.getLabelIntervals('Head', '2', frames, threshold=2)
    print(intervals)
    for (start, end) in intervals:
        BlenderManager.insertAction('MoveHead_right', start, end, smooth_frames=5)
        BlenderManager.insertAction('talking', start, end, smooth_frames=5)

#animation passes
ANIMATIONS = [
    BaseAction,
    HeadAnimation
]