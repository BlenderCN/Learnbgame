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

# System imports
# NONE!

# Blender imports
import bpy

# Addon imports
from ..functions import *



def matchProperties(agNew, agOld):
    agNew.buildSpeed = agOld.buildSpeed
    agNew.velocity = agOld.velocity
    agNew.layerHeight = agOld.layerHeight
    agNew.pathObject = agOld.pathObject
    agNew.xLocOffset = agOld.xLocOffset
    agNew.yLocOffset = agOld.yLocOffset
    agNew.zLocOffset = agOld.zLocOffset
    agNew.locationRandom = agOld.locationRandom
    agNew.xRotOffset = agOld.xRotOffset
    agNew.yRotOffset = agOld.yRotOffset
    agNew.zRotOffset = agOld.zRotOffset
    agNew.rotationRandom = agOld.rotationRandom
    agNew.locInterpolationMode = agOld.locInterpolationMode
    agNew.rotInterpolationMode = agOld.rotInterpolationMode
    agNew.xOrient = agOld.xOrient
    agNew.yOrient = agOld.yOrient
    agNew.orientRandom = agOld.orientRandom
    agNew.buildType = agOld.buildType
    agNew.invertBuild = agOld.invertBuild
    agNew.useGlobal = agOld.useGlobal


def uniquifyName(self, context):
    """ if LEGO model exists with name, add '.###' to the end """
    scn, ag = getActiveContextInfo()
    name = ag.name
    while scn.aglist.keys().count(name) > 1:
        if name[-4] == ".":
            try:
                num = int(name[-3:])+1
            except:
                num = 1
            name = name[:-3] + "%03d" % (num)
        else:
            name = name + ".001"
    if ag.name != name:
        ag.name = name


def collectionUpdate(self, context):
    scn, ag0 = getActiveContextInfo()
    # get rid of unused groups created by AssemblMe
    collections = bpy.data.collections if b280() else bpy.data.groups
    for c in collections:
        if c.name.startswith("AssemblMe_"):
            success = False
            for i in range(len(scn.aglist)):
                ag0 = scn.aglist[i]
                if c.name == "AssemblMe_{}_collection".format(ag0.name):
                    success = True
            if not success:
                collections.remove(c, do_unlink=True)


def setMeshesOnly(self, context):
    scn, ag = getActiveContextInfo()
    removedObjs = []
    if ag.collection is not None and ag.meshOnly:
        for obj in ag.collection.objects:
            if obj.type != "MESH":
                ag.collection.objects.unlink(obj)
                removedObjs.append(obj)
    if ag.animated:
        # set current_frame to animation start frame
        origFrame = scn.frame_current
        scn.frame_set(ag.frameWithOrigLoc)
        # clear animation
        clearAnimation(removedObjs)
        # set current_frame back to to original frame
        scn.frame_set(origFrame)


def handleOutdatedPreset(self, context):
    scn, ag = getActiveContextInfo()
    if not ag.buildType.isupper():
        ag.buildType = str(ag.buildType).upper()
