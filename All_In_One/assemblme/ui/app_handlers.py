# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# system imports
import bpy
import math
from bpy.app.handlers import persistent
from ..functions import *
from mathutils import Vector, Euler

# def isGroupVisible(scn, ag):
#     scn = bpy.context.scene
#     objectsOnActiveLayers = []
#     objects = scn.objects
#     for i in range(20):
#         # get objects on current layer if layer is active for object and scene
#         objectsOnActiveLayers += [ob for ob in objects if ob.layers[i] and scn.layers[i]]
#     for obj in objectsOnActiveLayers:
#         users_collection = obj.users_collection if b280() else obj.users_group
#         if ag.collection in users_collection:
#             return True, obj
#     return False, None


@persistent
def convert_velocity_value(scn):
    if scn is None:
        return
    for ag in scn.aglist:
        if ag.objectVelocity != -1:
            oldV = ag.objectVelocity
            targetNumFrames = 51 - oldV
            ag.velocity = 10 - (math.log(targetNumFrames, 2))
            ag.objectVelocity = -1


@persistent
def handle_upconversion(scn):
    if scn is None:
        return
    # update storage scene name
    for ag in scn.aglist:
        if createdWithUnsupportedVersion(ag):
            # convert from v1_1 to v1_2
            if int(ag.version[2]) < 2:
                if ag.collection and ag.collection.name.startswith("AssemblMe_animated_group"):
                    ag.collection.name = "AssemblMe_{}_group".format(ag.name)
            # convert from v1_2 to v1_3
            if int(ag.version[2]) < 2:
                collections = bpy.data.collections if b280() else bpy.data.groups
                ag.collection = collections.get(ag.group_name)
