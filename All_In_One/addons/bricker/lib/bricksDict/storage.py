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
import json

# Blender imports
import bpy

# Addon imports
from .generate import *
from .modify import *
from .functions import *
from ..caches import bricker_bfm_cache, cacheExists
from ...functions import *

def getBricksDict(cm, dType="MODEL", curFrame=None):
    """ retrieve bricksDict from cache if possible, else create a new one """
    scn = bpy.context.scene
    # if bricksDict can be pulled from cache
    if not matrixReallyIsDirty(cm) and cacheExists(cm) and not (cm.animIsDirty and "ANIM" in dType):
        # try getting bricksDict from light cache, then deep cache
        bricksDict = bricker_bfm_cache.get(cm.id) or json.loads(decompress_str(cm.BFMCache))
        # if animated, index into that dict
        if "ANIM" in dType:
            adjusted_frame_current = getAnimAdjustedFrame(curFrame, cm.lastStartFrame, cm.lastStopFrame)
            bricksDict = bricksDict[str(adjusted_frame_current)]
        return bricksDict
    # else, return nothing
    return None

def lightToDeepCache(bricker_bfm_cache):
    """ send bricksDict from blender cache to python cache for quick access """
    scn = bpy.context.scene
    numPushedIDs = 0
    for cm_id in bricker_bfm_cache.keys():
        # get cmlist item referred to by object
        cm = getItemByID(scn.cmlist, cm_id)
        if not cm:
            continue
        # save last cache to cm.BFMCache
        cm.BFMCache = compress_str(json.dumps(bricker_bfm_cache[cm_id]))
        numPushedIDs += 1
    if numPushedIDs > 0:
        print("[Bricker] pushed {numKeys} {pluralized_dicts} from light cache to deep cache".format(numKeys=numPushedIDs, pluralized_dicts="dict" if numPushedIDs == 1 else "dicts"))

def deepToLightCache(bricker_bfm_cache):
    """ send bricksDict from python cache to blender cache for saving to file """
    scn = bpy.context.scene
    numPulledIDs = 0
    for cm in scn.cmlist:
        # make sure there is something to store to light cache
        if cm.BFMCache == "":
            continue
        try:
            bricksDict = json.loads(decompress_str(cm.BFMCache))
            bricker_bfm_cache[cm.id] = bricksDict
            numPulledIDs += 1
        except Exception as e:
            print("ERROR in deepToLightCache:", e)
            cm.BFMCache = ""
    if numPulledIDs > 0:
        print("[Bricker] pulled {numKeys} {pluralized_dicts} from deep cache to light cache".format(numKeys=numPulledIDs, pluralized_dicts="dict" if numPulledIDs == 1 else "dicts"))

def cacheBricksDict(action, cm, bricksDict, curFrame=None):
    """ store bricksDict in light python cache for future access """
    scn = bpy.context.scene
    if action in ("CREATE", "UPDATE_MODEL"):
        bricker_bfm_cache[cm.id] = bricksDict
    elif action in ("ANIMATE", "UPDATE_ANIM"):
        if (cm.id not in bricker_bfm_cache.keys() or
           type(bricker_bfm_cache[cm.id]) != dict):
            bricker_bfm_cache[cm.id] = {}
        bricker_bfm_cache[cm.id][str(curFrame)] = bricksDict
