# Copyright (C) 2018 Christopher Gearhart
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
from .general import getRenderDumpPath

def jobIsValid(jobType, classObject):
    """ verifies that the job is valid before sending it to the host server """

    jobValidityDict = False
    scn = bpy.context.scene

    # verify that project has been saved
    if classObject.projectName == "":
        jobValidityDict = {"valid":False, "errorType":"WARNING", "errorMessage":"RENDER FAILED: You have not saved your project file. Please save it before attempting to render."}

    # verify there are no single or double quotes in project path
    projectPath = bpy.path.abspath("//")
    if "'" in projectPath or "\"" in projectPath:
        jobValidityDict = {"valid":False, "errorType":"ERROR", "errorMessage":"RENDER FAILED: Found illegal quotation in project path ({projectPath}). Please change the file/directory name before attempting to render.".format(projectPath=projectPath)}

    # verify that a camera exists in the scene
    elif scn.camera is None:
        jobValidityDict = {"valid":False, "errorType":"WARNING", "errorMessage":"RENDER FAILED: No camera in scene."}

    # verify image file format
    unsupportedFormats = ["AVI_JPEG", "AVI_RAW", "FRAMESERVER", "H264", "FFMPEG", "THEORA", "QUICKTIME", "XVID"]
    if not jobValidityDict and scn.render.image_settings.file_format in unsupportedFormats:
        jobValidityDict = {"valid":False, "errorType":"WARNING", "errorMessage":"RENDER FAILED: Output file format not supported. Supported formats: BMP, PNG, TARGA, JPEG, JPEG 2000, TIFF. (Animation only: IRIS, CINEON, HDR, DPX, OPEN_EXR, OPEN_EXR_MULTILAYER)"}

    # verify that the user input for renderDumpLoc is valid and can be created
    rdf, errorMsg = getRenderDumpPath()
    if errorMsg is not None:
        jobValidityDict = {"valid":False, "errorType":"ERROR", "errorMessage":errorMsg}

    # else, the job is valid
    if not jobValidityDict:
        jobValidityDict = {"valid":True, "errorType":None, "errorMessage":None}

    # if error detected, report error in Blender UI
    if jobValidityDict["errorType"] != None:
        classObject.report({jobValidityDict["errorType"]}, jobValidityDict["errorMessage"])
    # else alert user that render job has started
    else:
        if jobType == "image":
            classObject.report({"INFO"}, "Rendering current frame on {numAvailable} servers (Preview with 'SHIFT + P')".format(numAvailable=str(scn.rfc_availableServers)))
        else:
            classObject.report({"INFO"}, "Rendering animation on {numAvailable} servers (Check status with 'SHIFT + P')".format(numAvailable=str(scn.rfc_availableServers)))

    # if job is invalid, return false
    if not jobValidityDict["valid"]:
        return False

    # job is valid, return true
    return True
