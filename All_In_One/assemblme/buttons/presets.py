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
from shutil import copyfile

# Blender imports
import bpy
from bpy.props import EnumProperty

# Addon imports
from ..functions import *

class ASSEMBLME_OT_anim_presets(bpy.types.Operator):
    """Create new preset with current animation settings"""                     # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.anim_presets"                                        # unique identifier for buttons and menu items to reference.
    bl_label = "Animation Presets"                                              # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    ################################################
    # Blender Operator methods

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     if context.scene.newPresetName != "":
    #         return True
    #     return False

    def execute(self, context):
        if not self.canRun():
            return{"CANCELLED"}
        try:
            scn = bpy.context.scene
            path = get_addon_preferences().presetsFilepath
            fileNames = getFileNames(path)
            selectedPreset = "None"
            if self.action == "CREATE":
                if scn.newPresetName + ".py" in fileNames:
                    self.report({"WARNING"}, "Preset already exists with this name. Try another name!")
                    return{"CANCELLED"}
                # write new preset to file
                self.writeNewPreset(scn.newPresetName)
                fileNames.append(scn.newPresetName + ".py")
                selectedPreset = str(scn.newPresetName)
                self.report({"INFO"}, "Successfully added new preset '" + scn.newPresetName + "'")
                scn.newPresetName = ""
            elif self.action == "REMOVE":
                backupPath = os.path.join(path, "backups")
                fileName = scn.animPresetToDelete + ".py"
                filePath = os.path.join(path, fileName)
                backupFilePath = os.path.join(backupPath, fileName)
                if os.path.isfile(filePath):
                    if not os.path.exists(backupPath):
                        os.mkdir(backupPath)
                    if os.path.isfile(backupFilePath):
                        os.remove(backupFilePath)
                    os.rename(filePath, backupFilePath)
                    fileNames.remove(scn.animPresetToDelete + ".py")
                    self.report({"INFO"}, "Successfully removed preset '" + scn.animPresetToDelete + "'")
                else:
                    self.report({"WARNING"}, "Preset '" + scn.animPresetToDelete + "' does not exist.")
                    return{"CANCELLED"}

            presetNames = getPresetTuples(fileNames=fileNames)
            bpy.types.Scene.animPreset = EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=presetNames,
                update=updateAnimPreset,
                default="None")
            scn.animPreset = selectedPreset

            bpy.types.Scene.animPresetToDelete = EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=presetNames,
                default="None")
            scn.animPresetToDelete = selectedPreset
        except:
            assemblme_handle_exception()

        return{"FINISHED"}

    ###################################################
    # class variables

    action = EnumProperty(
        items=(
            ('CREATE', "Create", ""),
            ('REMOVE', "Remove", ""),
        )
    )

    ###################################################
    # class methods

    def writeNewPreset(self, presetName):
        scn, ag = getActiveContextInfo()
        presetsFilepath = get_addon_preferences().presetsFilepath
        if not os.path.exists(presetsFilepath):
            os.makedirs(presetsFilepath)
        newPresetPath = os.path.join(presetsFilepath, presetName + ".py")
        f = open(newPresetPath, "w")
        f.write("import bpy")
        f.write("\ndef execute():")
        f.write("\n    scn = bpy.context.scene")
        f.write("\n    ag = scn.aglist[scn.aglist_index]")
        f.write("\n    ag.buildSpeed = " + str(ag.buildSpeed))
        f.write("\n    ag.velocity = " + str(round(ag.velocity, 6)))
        f.write("\n    ag.xLocOffset = " + str(round(ag.xLocOffset, 6)))
        f.write("\n    ag.yLocOffset = " + str(round(ag.yLocOffset, 6)))
        f.write("\n    ag.zLocOffset = " + str(round(ag.zLocOffset, 6)))
        f.write("\n    ag.locInterpolationMode = '" + ag.locInterpolationMode + "'")
        f.write("\n    ag.locationRandom = " + str(round(ag.locationRandom, 6)))
        f.write("\n    ag.xRotOffset = " + str(ag.xRotOffset))
        f.write("\n    ag.yRotOffset = " + str(ag.yRotOffset))
        f.write("\n    ag.zRotOffset = " + str(ag.zRotOffset))
        f.write("\n    ag.rotInterpolationMode = '" + ag.rotInterpolationMode + "'")
        f.write("\n    ag.rotationRandom = " + str(round(ag.rotationRandom, 6)))
        f.write("\n    ag.xOrient = " + str(round(ag.xOrient, 6)))
        f.write("\n    ag.yOrient = " + str(round(ag.yOrient, 6)))
        f.write("\n    ag.orientRandom = " + str(round(ag.orientRandom, 6)))
        f.write("\n    ag.layerHeight = " + str(round(ag.layerHeight, 6)))
        f.write("\n    ag.buildType = '" + ag.buildType + "'")
        f.write("\n    ag.invertBuild = " + str(round(ag.invertBuild, 6)))
        f.write("\n    ag.skipEmptySelections = " + str(ag.skipEmptySelections))
        f.write("\n    ag.useGlobal = " + str(ag.useGlobal))
        f.write("\n    ag.meshOnly = " + str(ag.meshOnly))
        f.write("\n    return None")

    def canRun(self):
        scn = bpy.context.scene
        if self.action == "CREATE":
            if scn.newPresetName == "":
                self.report({"WARNING"}, "No preset name specified")
                return False
        if self.action == "REMOVE":
            if scn.animPresetToDelete == "None":
                self.report({"WARNING"}, "No preset name specified")
                return False
            # # prevent users from deleting default presets
            # elif scn.animPresetToDelete in scn.assemblme_default_presets:
            #     self.report({"WARNING"}, "Cannot delete default p")
            #     return False
        return True

    #############################################
