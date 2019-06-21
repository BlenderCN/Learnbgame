import bpy
import heapq


# TODO(SK): Missing docstring
def projectTimeToFrames(t):
    op = bpy.context.scene.pam_anim_animation
    # Projection algorithm
    frame = (t - op.startTime) / (op.endTime - op.startTime) * (op.endFrame - op.startFrame) + op.startFrame
    return frame


# TODO(SK): Missing docstring
def timeToFrames(t):
    op = bpy.context.scene.pam_anim_animation
    return t * (op.endFrame - op.startFrame) / (op.endTime - op.startTime)


# TODO(SK): Missing docstring
def addObjectsToGroup(group, elements):
    if type(elements) is dict:
        elements = elements.values()
    for e in elements:
        group.objects.link(e)


# TODO(SK): Missing docstring
def getQueueValues(queue, t):
    elementsBelowThreshold = []
    while queue and queue[0][0] <= t:
        elementsBelowThreshold.append(heapq.heappop(queue))
    return elementsBelowThreshold
