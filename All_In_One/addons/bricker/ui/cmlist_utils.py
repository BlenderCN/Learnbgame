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
from operator import itemgetter

# Blender imports
import bpy
from bpy.props import *
from bpy.types import Panel, UIList
props = bpy.props

# Addon imports
from ..functions import *
from ..buttons.bevel import *
from ..lib.background_processing.classes.JobManager import JobManager


def uniquifyName(self, context):
    """ if Brick Model exists with name, add '.###' to the end """
    scn, cm, _ = getActiveContextInfo()
    name = cm.name
    while scn.cmlist.keys().count(name) > 1:
        if name[-4] == ".":
            try:
                num = int(name[-3:])+1
            except ValueError:
                num = 1
            name = name[:-3] + "%03d" % (num)
        else:
            name = name + ".001"
    if cm.name != name:
        cm.name = name


def setDefaultObjIfEmpty(self, context):
    scn = context.scene
    last_cmlist_index = scn.cmlist_index
    cm0 = scn.cmlist[last_cmlist_index]
    # verify model doesn't exist with that name
    if cm0.source_obj is not None:
        for i, cm1 in enumerate(scn.cmlist):
            if cm1 != cm0 and cm1.source_obj is cm0.source_obj:
                cm0.source_obj = None
                scn.cmlist_index = i


def verifyCustomObject1(self, context):
    scn, cm, n = getActiveContextInfo()
    if cm.customObject1 and cm.customObject1.name.startswith("Bricker_%(n)s" % locals()):
        cm.customObject1 = None
def verifyCustomObject2(self, context):
    scn, cm, n = getActiveContextInfo()
    if cm.customObject2 and cm.customObject2.name.startswith("Bricker_%(n)s" % locals()):
        cm.customObject2 = None
def verifyCustomObject3(self, context):
    scn, cm, n = getActiveContextInfo()
    if cm.customObject3 and cm.customObject3.name.startswith("Bricker_%(n)s" % locals()):
        cm.customObject3 = None


def updateBevel(self, context):
    # get bricks to bevel
    try:
        scn, cm, n = getActiveContextInfo()
        if cm.lastBevelWidth != cm.bevelWidth or cm.lastBevelSegments != cm.bevelSegments or cm.lastBevelProfile != cm.bevelProfile:
            bricks = getBricks()
            BRICKER_OT_bevel.createBevelMods(cm, bricks)
            cm.lastBevelWidth = cm.bevelWidth
            cm.lastBevelSegments = cm.bevelSegments
            cm.lastBevelProfile = cm.bevelProfile
    except Exception as e:
        raise Exception("[Bricker] ERROR in updateBevel():", e)
        pass


def updateParentExposure(self, context):
    scn, cm, _ = getActiveContextInfo()
    if not (cm.modelCreated or cm.animated):
        return
    parentOb = cm.parent_obj
    if parentOb:
        if cm.exposeParent:
            safeLink(parentOb, protect=True)
            select(parentOb, active=True, only=True)
        else:
            try:
                safeUnlink(parentOb)
            except RuntimeError:
                pass


def updateModelScale(self, context):
    scn, cm, _ = getActiveContextInfo()
    if not (cm.modelCreated or cm.animated):
        return
    _, _, s = getTransformData(cm)
    parentOb = cm.parent_obj
    if parentOb:
        parentOb.scale = Vector(s) * cm.transformScale


def updateCircleVerts(self, context):
    scn, cm, _ = getActiveContextInfo()
    if (cm.circleVerts - 2) % 4 == 0:
        cm.circleVerts += 1
    cm.bricksAreDirty = True


def updateJobManagerProperties(self, context):
    scn, cm, _ = getActiveContextInfo()
    curJobManager = JobManager.get_instance(cm.id)
    curJobManager.timeout = cm.backProcTimeout
    curJobManager.max_workers = cm.maxWorkers


def dirtyAnim(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.animIsDirty = True


def dirtyMaterial(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.materialIsDirty = True


def dirtyModel(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.modelIsDirty = True


# NOTE: Any prop that calls this function should be added to getMatrixSettings()
def dirtyMatrix(self=None, context=None):
    scn, cm, _ = getActiveContextInfo()
    cm.matrixIsDirty = True


def dirtyInternal(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.internalIsDirty = True
    cm.buildIsDirty = True


def dirtyBuild(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.buildIsDirty = True


def dirtyBricks(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.bricksAreDirty = True


def updateBrickType(self, context):
    scn, cm, _ = getActiveContextInfo()
    cm.zStep = getZStep(cm)
    dirtyMatrix(self, context)


def updateBevelRender(self, context):
    scn, cm, _ = getActiveContextInfo()
    show_render = cm.bevelShowRender
    for brick in getBricks():
        bevel = brick.modifiers.get(brick.name + '_bvl')
        if bevel: bevel.show_render = show_render


def updateBevelViewport(self, context):
    scn, cm, _ = getActiveContextInfo()
    show_viewport = cm.bevelShowViewport
    for brick in getBricks():
        bevel = brick.modifiers.get(brick.name + '_bvl')
        if bevel: bevel.show_viewport = show_viewport


def updateBevelEditMode(self, context):
    scn, cm, _ = getActiveContextInfo()
    show_in_editmode = cm.bevelShowEditmode
    for brick in getBricks():
        bevel = brick.modifiers.get(brick.name + '_bvl')
        if bevel: bevel.show_in_editmode = show_in_editmode


def getCMProps():
    """ returns list of important cmlist properties """
    return ["shellThickness",
            "brickHeight",
            "studDetail",
            "logoType",
            "logoResolution",
            "logoDecimate",
            "logoObject",
            "logoScale",
            "logoInset",
            "hiddenUndersideDetail",
            "exposedUndersideDetail",
            "circleVerts",
            "loopCut",
            "gap",
            "mergeSeed",
            "connectThresh",
            "randomLoc",
            "randomRot",
            "brickType",
            "alignBricks",
            "offsetBrickLayers",
            "distOffset",
            "customObject1",
            "customObject2",
            "customObject3",
            "maxWidth",
            "maxDepth",
            "mergeType",
            "legalBricksOnly",
            "splitModel",
            "internalSupports",
            "matShellDepth",
            "latticeStep",
            "alternateXY",
            "colThickness",
            "colorSnap",
            "colorSnapAmount",
            "transparentWeight",
            "colStep",
            "smokeDensity",
            "smokeSaturation",
            "smokeBrightness",
            "flameColor",
            "flameIntensity",
            "materialType",
            "customMat",
            "internalMat",
            "matShellDepth",
            "randomMatSeed",
            "useUVMap",
            "uvImage",
            "useNormals",
            "verifyExposure",
            "insidenessRayCastDir",
            "castDoubleCheckRays",
            "startFrame",
            "stopFrame",
            "useAnimation",
            "autoUpdateOnDelete",
            "brickShell",
            "calculationAxes",
            "useLocalOrient",
            "brickHeight",
            "bevelWidth",
            "bevelSegments",
            "bevelProfile"]


def matchProperties(cmTo, cmFrom, overrideIdx=-1):
    scn = bpy.context.scene
    cm_attrs = getCMProps()
    # remove properties that should not be matched
    if not cmFrom.bevelAdded or not cmTo.bevelAdded:
        cm_attrs.remove("bevelWidth")
        cm_attrs.remove("bevelSegments")
        cm_attrs.remove("bevelProfile")
    # match material properties for Random/ABS Plastic Snapping
    matObjNamesFrom = ["Bricker_{}_RANDOM_mats".format(cmFrom.id), "Bricker_{}_ABS_mats".format(cmFrom.id)]
    matObjNamesTo   = ["Bricker_{}_RANDOM_mats".format(cmTo.id), "Bricker_{}_ABS_mats".format(cmTo.id)]
    for i in range(2):
        matObjFrom = bpy.data.objects.get(matObjNamesFrom[i])
        matObjTo = bpy.data.objects.get(matObjNamesTo[i])
        if matObjFrom is None or matObjTo is None:
            continue
        matObjTo.data.materials.clear(update_data=True)
        for mat in matObjFrom.data.materials:
            matObjTo.data.materials.append(mat)
    # match properties from 'cmFrom' to 'cmTo'
    if overrideIdx >= 0:
        origIdx = scn.cmlist_index
        scn.cmlist_index = overrideIdx
    for attr in cm_attrs:
        oldVal = getattr(cmFrom, attr)
        setattr(cmTo, attr, oldVal)
    if overrideIdx >= 0:
        scn.cmlist_index = origIdx
