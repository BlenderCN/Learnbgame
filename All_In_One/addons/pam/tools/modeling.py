"""PAM Modeling Tools"""

import logging

from .. import pam

import bpy

logger = logging.getLogger(__package__)


class PAMToolUVMapping(bpy.types.Operator):
    """Calculates neuron quantity across the active object"""

    bl_idname = "pam.map_via_uv"
    bl_label = "Deform mesh via UV overlap"
    bl_description = "Maps a mesh on the form of another mesh via UV-overlap"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if active_obj is not None:
            return active_obj.type == "MESH"
        else:
            return False

    def execute(self, context):
        target_obj = context.active_object
        if (bpy.context.selected_objects.index(target_obj) == 0):
            origin_obj = bpy.context.selected_objects[1]
        else:
            origin_obj = bpy.context.selected_objects[0]

        map_via_uv(origin_obj, target_obj)

        return {'FINISHED'}

    def invoke(self, context, event):

        return self.execute(context)


def map_via_uv(origin, target):
    """ Maps a mesh on the surface of another mesh while preserving
    its topology. The mapping uses the uv-space
    origin          : mesh to map
    target          : mesh-form that is targeted
    """
    
    if not origin.type == "MESH":
        raise Exception("Origin object is not a mesh")

    if not target.type == "MESH":
        raise Exception("Target object is not a mesh")

    o_2d = []

    for v in origin.data.vertices:
        o_2d.append(
            pam.map3dPointToUV(origin, origin, v.co)
        )

    t_3d = pam.mapUVPointTo3d(target, o_2d)

    if len(t_3d) != len(o_2d):
        raise Exception(
            "One of the points is not in the UV-grid of the target object: " + str(len(t_3d)) + '/' + str(len(o_2d))
        )

    for i in range(len(t_3d)):
        origin.data.vertices[i].co = t_3d[i]
