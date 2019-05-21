# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from mathutils import Vector
from .error import MhxError

def getOriginalName(ob):
    words = ob.name.rsplit(".",1)
    if len(words) == 1:
        return words[0]
    elif len(words[1]) == 3:    # .001
        try:
            int(words[1])
            return words[0]
        except ValueError:
            return ob.name
    else:
        return ob.name


def isBody(ob):
    name = getOriginalName(ob)
    return (name.split(":")[-1] in ["Body", "Base", "Proxy"])

def getRigName(ob):
    name = getOriginalName(ob)
    return name.split(":")[0]

def getProxyName(ob):
    name = getOriginalName(ob)
    return name.split(":")[1]

def getMaterialName(ob):
    name = getOriginalName(ob)
    return name.split(":")[2]

def getDeleteName(ob):
    return "Delete:" + getProxyName(ob)

def isDeleteVGroup(vgrp):
    return (vgrp.name[0:7] == "Delete:")

def getVGProxyName(string):
    return string.split(":",1)[1]

def getClothesName(clo):
    name = getOriginalName(clo)
    try:
        return name.split(":",1)[1]
    except IndexError:
        return None


def getArmature(ob):
    if ob.type == 'MESH':
        return ob.parent
    elif ob.type == 'ARMATURE':
        return ob


def zup(co):
    return Vector((co[0], -co[2], co[1]))

def zup2(co, s):
    return Vector((s[0]*co[0], -s[2]*co[2], s[1]*co[1]))


def multiply(list1, list2):
    [(list1[n] and list2[n]) for n in range(len(list1))]


def updateScene(context):
    scn = context.scene
    scn.frame_current = scn.frame_current

# ---------------------------------------------------------------------
#   Global variable that holds the loaded json struct for the
#   current human.
# ---------------------------------------------------------------------

def setMhHuman(human):
    global theMhHuman
    theMhHuman = human

def getMhHuman(ob=None):
    global theMhHuman
    try:
        theMhHuman
    except:
        raise MhxError("No saved human")
    if ob and theMhHuman["uuid"] != ob.MhxUuid:
        raise MhxError("Saved human:\n %s\ndoes not match current object:\n %s" % (theMhHuman["name"], ob.name))
    return theMhHuman

# ---------------------------------------------------------------------
#   Roll angle
# ---------------------------------------------------------------------

def getRoll(bone):
    import math
    quat = bone.matrix_local.to_3x3().to_quaternion()
    if abs(quat.w) < 1e-4:
        roll = math.pi
    else:
        roll = -2*math.atan(quat.y/quat.w)
    return roll


# ---------------------------------------------------------------------
#  Make sure that selecting an object really takes.
# ---------------------------------------------------------------------

def reallySelect(ob, scn):
    ob.hide = False
    visible = False
    for n,vis in enumerate(ob.layers):
        if vis and scn.layers[n]:
            visible = True
            break
    if not visible:
        for n,vis in enumerate(ob.layers):
            if vis:
                scn.layers[n] = True
                visible = True
                break
    if not visible:
        for n,vis in enumerate(scn.layers):
            if vis:
                ob.layers[n] = True
                visible = True
                break
    if not visible:
        ob.layers[0] = scn.layers[0] = True
    scn.objects.active = ob

# ---------------------------------------------------------------------
#   Debug flags
# ---------------------------------------------------------------------

AutoWeight = False
