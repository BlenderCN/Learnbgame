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
import time
import os
import json

# Blender imports
import bpy
from bpy.types import Operator

# Addon imports
from ..functions import *
from ..lib.Brick import *


class BRICKER_OT_export_ldraw(Operator):
    """Export active brick model to ldraw file"""
    bl_idname = "bricker.export_ldraw"
    bl_label = "Export to Ldraw File"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns False) """
        return True

    def execute(self, context):
        try:
            self.writeLdrawFile()
        except:
            bricker_handle_exception()
        return{"FINISHED"}

    #############################################
    # class methods

    def writeLdrawFile(self):
        """ create and write Ldraw file """
        scn, cm, n = getActiveContextInfo()
        # initialize vars
        legalBricks = getLegalBricks()
        absMatProperties = bpy.props.abs_mat_properties if hasattr(bpy.props, "abs_mat_properties") else None
        transWeight = cm.transparentWeight
        for frame in range(cm.startFrame, cm.stopFrame + 1) if cm.animated else [-1]:
            path, errorMsg = getExportPath(n, ".ldr", cm.exportPath, frame=frame, subfolder=cm.animated)
            if errorMsg is not None:
                self.report({"WARNING"}, errorMsg)
                continue
            f = open(path, "w")
            # write META commands
            f.write("0 %(n)s\n" % locals())
            f.write("0 Name:\n" % locals())
            f.write("0 Unofficial model\n" % locals())
            # f.write("0 Author: Unknown\n" % locals())
            bricksDict = getBricksDict(cm, dType="ANIM" if cm.animated else "MODEL", curFrame=frame)
            # get small offset for model to get close to Ldraw units
            offset = vec_conv(bricksDict[list(bricksDict.keys())[0]]["co"], int)
            offset.x = offset.x % 10
            offset.y = offset.z % 8
            offset.z = offset.y % 10
            # get dictionary of keys based on z value
            keysDict = getKeysDict(bricksDict)
            # get sorted keys for random merging
            seedKeys = sorted(list(bricksDict.keys())) if materialType == "RANDOM" else None
            # iterate through z locations in bricksDict (bottom to top)
            for z in sorted(keysDict.keys()):
                for key in keysDict[z]:
                    # skip bricks that aren't displayed
                    if not bricksDict[key]["draw"] or bricksDict[key]["parent"] != "self":
                        continue
                    # initialize brick size and typ
                    size = bricksDict[key]["size"]
                    typ = bricksDict[key]["type"]
                    # get matrix for rotation of brick
                    matrices = [" 0 0 -1 0 1 0  1 0  0",
                                " 1 0  0 0 1 0  0 0  1",
                                " 0 0  1 0 1 0 -1 0  0",
                                "-1 0  0 0 1 0  0 0 -1"]
                    if typ == "SLOPE":
                        idx = 0
                        idx -= 2 if bricksDict[key]["flipped"] else 0
                        idx -= 1 if bricksDict[key]["rotated"] else 0
                        idx += 2 if (size[:2] in ([1, 2], [1, 3], [1, 4], [2, 3]) and not bricksDict[key]["rotated"]) or size[:2] == [2, 4] else 0
                    else:
                        idx = 1
                    idx += 1 if size[1] > size[0] else 0
                    matrix = matrices[idx]
                    # get coordinate for brick in Ldraw units
                    co = self.blendToLdrawUnits(cm, bricksDict, cm.zStep, key, idx)
                    # get color code of brick
                    mat = getMaterial(bricksDict, key, size, cm.zStep, cm.materialType, cm.customMat.name if cm.customMat is not None else "z", cm.randomMatSeed, cm.materialIsDirty or cm.matrixIsDirty or cm.buildIsDirty, seedKeys, brick_mats=getBrickMats(cm.materialType, cm.id))
                    mat_name = "" if mat is None else mat.name
                    rgba = bricksDict[key]["rgba"]
                    color = 0
                    if mat_name in getABSMatNames() and absMatProperties is not None:
                        color = absMatProperties[mat_name]["LDR Code"]
                    elif rgba not in (None, ""):
                        mat_name = findNearestBrickColorName(rgba, transWeight)
                    elif bpy.data.materials.get(mat_name) is not None:
                        rgba = getMaterialColor(mat_name)
                    # get part number and ldraw file name for brick
                    parts = legalBricks[size[2]][typ]
                    for j,part in enumerate(parts):
                        if parts[j]["s"] in (size[:2], size[1::-1]):
                            part = parts[j]["pt2" if typ == "SLOPE" and size[:2] in ([4, 2], [2, 4], [3, 2], [2, 3]) and bricksDict[key]["rotated"] else "pt"]
                            break
                    brickFile = "%(part)s.dat" % locals()
                    # offset the coordinate and round to ensure appropriate Ldraw location
                    co += offset
                    co = Vector((round_nearest(co.x, 10), round_nearest(co.y, 8), round_nearest(co.z, 10)))
                    # write line to file for brick
                    f.write("1 {color} {x} {y} {z} {matrix} {brickFile}\n".format(color=color, x=co.x, y=co.y, z=co.z, matrix=matrix, brickFile=brickFile))
                    i += 1
                f.write("0 STEP\n")
            f.close()
            if not cm.lastLegalBricksOnly:
                self.report({"WARNING"}, "Model may contain non-standard brick sizes. Enable 'Brick Types > Legal Bricks Only' to make bricks LDraw-compatible.")
            elif absMatProperties is None and brick_materials_installed:
                self.report({"WARNING"}, "Materials may not have transferred successfully – please update to the latest version of 'ABS Plastic Materials'")
            else:
                self.report({"INFO"}, "Ldraw file saved to '%(path)s'" % locals())

    def blendToLdrawUnits(self, cm, bricksDict, zStep, key, idx):
        """ convert location of brick from blender units to ldraw units """
        size = bricksDict[key]["size"]
        loc = getBrickCenter(bricksDict, key, zStep)
        dimensions = Bricks.get_dimensions(cm.brickHeight, zStep, cm.gap)
        h = 8 * zStep
        loc.x = loc.x * (20 / (dimensions["width"] + dimensions["gap"]))
        loc.y = loc.y * (20 / (dimensions["width"] + dimensions["gap"]))
        if bricksDict[key]["type"] == "SLOPE":
            if idx == 0:
                loc.x -= ((size[0] - 1) * 20) / 2
            elif idx in (1, -3):
                loc.y += ((size[1] - 1) * 20) / 2
            elif idx in (2, -2):
                loc.x += ((size[0] - 1) * 20) / 2
            elif idx in (3, -1):
                loc.y -= ((size[1] - 1) * 20) / 2
        loc.z = loc.z * (h / (dimensions["height"] + dimensions["gap"]))
        if bricksDict[key]["type"] == "SLOPE" and size == [1, 1, 3]:
            loc.z -= size[2] * 8
        if zStep == 1 and size[2] == 3:
            loc.z += 8
        # convert to right-handed co-ordinate system where -Y is "up"
        loc = Vector((loc.x, -loc.z, loc.y))
        return loc

    def rgbToHex(self, rgb):
        """ convert RGB list to HEX string """
        def clamp(x):
            return int(max(0, min(x, 255)))
        r, g, b = rgb
        return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

    #############################################
