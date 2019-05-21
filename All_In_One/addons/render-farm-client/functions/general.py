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

# System imports
import fnmatch
import itertools
import operator
import os
import time
import subprocess
import sys
try:
    import httplib
except:
    import http.client as httplib

# Blender imports
import bpy

# Addon imports
from .setupServers import *
from .common import *

def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def bashSafeName(string):
    # protects against file names that would cause problems with bash calls
    if string.startswith(".") or string.startswith("-"):
        string = "_" + string[1:]
    # replaces problematic characters in shell with underscore '_'
    chars = "!#$&'()*,;<=>?[]^`{|}~: "
    for char in list(chars):
        string = string.replace(char, "_")
    return string

def getFrames(projectName, archiveFiles=False, frameRange=False):
    """ rsync rendered frames from host server to local machine """
    scn = bpy.context.scene
    basePath = bpy.path.abspath("//")
    dumpLocation = getRenderDumpPath()[0]
    outFilePath = None

    if archiveFiles:
        # move old render files to backup directory
        if frameRange:
            fileStrings = ""
            for frame in frameRange:
                fileStrings += "{nameOutputFiles}_{frameNum}{animExtension}\n".format(nameOutputFiles=getNameOutputFiles(), frameNum=str(frame).zfill(4), animExtension=scn.rfc_animExtension)
            outFilePath = os.path.join(dumpLocation, "includeList.txt")
            f = open(outFilePath, "w")
            f.write(fileStrings)
            includeDict = "--include-from='%(outFilePath)s'" %locals()
            f.close()
        else:
            includeDict = ""
        archiveRsyncCommand = "rsync -aqx --rsync-path='mkdir -p {dumpLocation}backups/ && rsync' --remove-source-files {includeDict} --exclude='{nameOutputFiles}_????.???' --exclude='backups/' '{dumpLocation}' '{dumpLocation}backups/';".format(includeDict=includeDict, dumpLocation=dumpLocation.replace(" ", "\\ "), nameOutputFiles=getNameOutputFiles(), imExtension=scn.rfc_imExtension)
    else:
        archiveRsyncCommand = "mkdir -p {dumpLocation};".format(dumpLocation=dumpLocation.replace(" ", "\\ "))

    # remove created 'includeList.txt' file
    if outFilePath is not None:
        os.remove(outFilePath)

    # exclude blend files, averaged files, and strange temporary files
    exclusions =  "--exclude='*.blend' --exclude='*_average.???' --exclude='*.???.*'"

    # rsync files from host server to local directory
    fetchRsyncCommand = "rsync -ax --progress --remove-source-files {exclusions} -e 'ssh -T -oCompression=no -oStrictHostKeyChecking=no -x' '{login}:{remotePath}{projectName}/results/' '{dumpLocation}';".format(exclusions=exclusions, login=bpy.props.rfc_serverPrefs["login"], remotePath=bpy.props.rfc_serverPrefs["path"], projectName=projectName, dumpLocation=dumpLocation)

    # run the above processes
    process = subprocess.Popen(archiveRsyncCommand + fetchRsyncCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return process

def buildFrameRangesString(frameRanges):
    """ builds frame range list of lists/ints from user-entered frameRanges string """
    frameRangeList = frameRanges.replace(" ", "").split(",")
    newFrameRangeList = []
    invalidDict = {"valid":False, "string":None}
    for string in frameRangeList:
        try:
            newInt = int(string)
            if newInt >= 0 and newInt <= 500000:
                newFrameRangeList.append(newInt)
            else:
                return invalidDict
        except:
            if "-" in string:
                newString = string.split("-")
                if len(newString) != 2:
                    return invalidDict
                try:
                    newInt1 = int(newString[0])
                    newInt2 = int(newString[1])
                    if newInt1 <= newInt2 and newInt2 <= 500000:
                        newFrameRangeList.append([newInt1, newInt2])
                    else:
                        return invalidDict
                except:
                    return invalidDict
            else:
                return invalidDict
    return {"valid":True, "string":str(newFrameRangeList).replace(" ", "")}

def copyProjectFile(projectName, compress):
    """ copies project file from local machine to host server """
    scn = bpy.context.scene
    saveToPath = "{tempLocalDir}{projectName}.blend".format(tempLocalDir=scn.rfc_tempLocalDir, projectName=projectName)
    if projectName == "rf_unsaved_file":
        # saves unsaved file as 'rf_unsaved_file.blend'
        bpy.ops.wm.save_mainfile(filepath="{tempLocalDir}rf_unsaved_file.blend".format(tempLocalDir=scn.rfc_tempLocalDir), compress=compress)
    else:
        bpy.ops.wm.save_as_mainfile(filepath=saveToPath, compress=compress, copy=True)

    # copies blender project file to host server
    rsyncCommand = "rsync --copy-links --progress --rsync-path='mkdir -p {remotePath}{projectName}/toRemote/ && rsync' -qazx --include={projectName}.blend --exclude='*' -e 'ssh -T -oCompression=no -oStrictHostKeyChecking=no -x' '{tempLocalDir}' '{login}:{remotePath}{projectName}/toRemote/'".format(remotePath=bpy.props.rfc_serverPrefs["path"].replace(" ", "\\ "), projectName=projectName, tempLocalDir=scn.rfc_tempLocalDir, login=bpy.props.rfc_serverPrefs["login"])
    process = subprocess.Popen(rsyncCommand, shell=True)
    return process

def copyFiles():
    """ copies necessary files to host server """
    scn = bpy.context.scene
    # write out the servers file for remote servers
    writeServersFile(bpy.props.rfc_serverPrefs["servers"], scn.rfc_serverGroups)

    # rsync setup files to host server ('servers.txt', 'blender_p.py', 'blender_task' module)
    rsyncCommand = "rsync -qax -e 'ssh -T -oCompression=no -oStrictHostKeyChecking=no -x' --exclude='*.zip' --rsync-path='mkdir -p {remotePath} && rsync' '{to_host_server}/' '{login}:{remotePath}'".format(remotePath=bpy.props.rfc_serverPrefs["path"].replace(" ", "\\ "), to_host_server=os.path.join(getLibraryPath(), "to_host_server"), login=bpy.props.rfc_serverPrefs["login"])
    process = subprocess.Popen(rsyncCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return process

def renderFrames(frameRange, projectName, jobsPerFrame=False):
    """ calls 'blender_task' on host server """
    scn = bpy.context.scene
    # defines the name of the output files generated by 'blender_task'
    n = getNameOutputFiles()
    extraFlags = " -O %(n)s" % locals()

    if jobsPerFrame:
        extraFlags += " -j {jobsPerFrame}".format(jobsPerFrame=jobsPerFrame)
        extraFlags += " -s {numImSamples}".format(numImSamples=scn.rfc_samplesPerFrame)

    # runs blender command to render given range from the remote server
    renderCommand = "ssh -T -oStrictHostKeyChecking=no -x {login} 'python {remotePath}blender_task -v -p -n {projectName} -l {frameRange} --hosts_file {remotePath}servers.txt -R {remotePath} --connection_timeout {t} --max_server_load {maxServerLoad}{extraFlags}'".format(login=bpy.props.rfc_serverPrefs["login"], remotePath=bpy.props.rfc_serverPrefs["path"], projectName=projectName, frameRange=frameRange.replace(" ", ""), t=scn.rfc_timeout, maxServerLoad=str(scn.rfc_maxServerLoad), extraFlags=extraFlags)
    process = subprocess.Popen(renderCommand, stderr=subprocess.PIPE, shell=True)
    print("Process sent to remote servers!")
    return process

def setRenderStatus(key, status):
    scn = bpy.context.scene
    if key == "image":
        scn.rfc_imageRenderStatus = status
    elif key == "animation":
        scn.rfc_animRenderStatus = status
    tag_redraw_areas()

def getRenderStatus(key):
    scn = bpy.context.scene
    if key == "image":
        return scn.rfc_imageRenderStatus
    elif key == "animation":
        return scn.rfc_animRenderStatus
    else:
        return ""

def expandFrames(frame_range):
    """ Helper function takes frame range string and returns list with frame ranges expanded """
    frames = []
    for i in frame_range:
        if type(i) == list:
            frames += range(i[0], i[1]+1)
        elif type(i) == int:
            frames.append(i)
        else:
            sys.stderr.write("Unknown type in frames list")

    return list(set(frames))

def intsToFrameRanges(intsList):
    """ turns list of ints to list of frame ranges """
    frameRangesS = ""
    i = 0
    while i < len(intsList):
        s = intsList[i] # start index
        e = s           # end index
        while i < len(intsList) - 1 and intsList[i + 1] - intsList[i] == 1:
            e += 1
            i += 1
        frameRangesS += "{s},".format(s=s) if s == e else "{s}-{e},".format(s=s, e=e)
        i += 1
    return frameRangesS[:-1]

def listMissingFiles(filename, frameRange):
    """ lists all missing files from local render dump directory """
    dumpFolder = getRenderDumpPath()[0]
    compList = expandFrames(json.loads(frameRange))
    if not os.path.exists(dumpFolder):
        errorMsg = "The folder does not exist: {path}".format(path=dumpFolder)
        sys.stderr.write(errorMsg)
        print(errorMsg)
        return str(compList)[1:-1]
    try:
        allFiles = os.listdir(dumpFolder)
    except:
        errorMsg = "Error listing directory {path}".format(path=dumpFolder)
        sys.stderr.write(errorMsg)
        print(errorMsg)
        return str(compList)[1:-1]
    imList = []
    for f in allFiles:
        if "_average." not in f and not fnmatch.fnmatch(f, "*_seed-*_????.???") and f[:len(filename)] == filename:
            imList.append(int(f[len(filename)+1:len(filename)+5]))
    # compare lists to determine which frames are missing from imlist
    missingF = [i for i in compList if i not in imList]
    # convert list of ints to string with frame ranges
    missingFR = intsToFrameRanges(missingF)
    # return the list of missing frames as string, omitting the open and close brackets
    return missingFR

def handleError(classObject, errorSource, i="Not Provided"):
    errorMessage = False
    # if error message available, print in Info window and define errorMessage string
    if i == "Not Provided":
        if classObject.process.stderr != None:
            errorMessage = "Error message available in terminal/Info window."
            for line in classObject.process.stderr.readlines():
                classObject.report({"WARNING"}, str(line, "utf-8").replace("\n", ""))
        rCode = classObject.process.returncode
    else:
        if classObject.processes[i].stderr != None:
            errorMessage = "Error message available in terminal/Info window."
            for line in classObject.processes[i].stderr.readlines():
                classObject.report({"WARNING"}, str(line, "utf-8").replace("\n", ""))
        rCode = classObject.processes[i].returncode
    if not errorMessage:
        errorMessage = "No error message to print."

    classObject.report({"ERROR"}, "%(errorSource)s gave return code %(rCode)s. %(errorMessage)s" % locals())

def handleBTError(classObject, i="Not Provided"):
    if i == "Not Provided":
        classObject.stderr = classObject.process.stderr.readlines()
    else:
        classObject.stderr = classObject.processes[i].stderr.readlines()

    print("\nERRORS:")
    for line in classObject.stderr:
        line = line.decode("ASCII").replace("\\n", "")[:-1]
        errorMessage = "blender_task error: '%(line)s'" % locals()
        classObject.report({"ERROR"}, errorMessage)
        print(errorMessage)
        sys.stderr.write(line)
    errorMsg = classObject.stderr[-1].decode("ASCII")

def setFrameRangesDict(classObject):
    scn = bpy.context.scene
    if scn.rfc_frameRanges == "":
        classObject.rfc_frameRangesDict = {"string":"[[{frameStart},{frameEnd}]]".format(frameStart=str(scn.frame_start), frameEnd=str(scn.frame_end))}
    else:
        classObject.rfc_frameRangesDict = buildFrameRangesString(scn.rfc_frameRanges)
        if not classObject.rfc_frameRangesDict["valid"]:
            classObject.report({"ERROR"}, "ERROR: Invalid frame ranges given.")
            return False
    return True

def getRenderDumpPath():
    scn = bpy.context.scene
    path = scn.rfc_renderDumpLoc
    lastSlash = path.rfind("/")
    path = path[:len(path) if lastSlash == -1 else lastSlash + 1]
    blendPath = bpy.path.abspath("//") or "/tmp/"
    blendPathSplit = blendPath[:-1].split("/")
    # if relative path, construct path from user input
    if path.startswith("//"):
        splitPath = path[2:].split("/")
        while len(splitPath) > 0 and splitPath[0] == "..":
            splitPath.pop(0)
            blendPathSplit.pop()
        newPath = "/".join(splitPath)
        fullBlendPath = "/".join(blendPathSplit) if len(blendPathSplit) > 1 else "/"
        path = os.path.join(fullBlendPath, newPath)
    # if path is blank at this point, use default render location
    if path == "":
        path = blendPath
    # ensure path has trailing '/'
    if not path.endswith("/"):
        path += "/"
    # check to make sure path exists on local machine
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except:
            return path, "The folder '%(path)s' could not be created on your local machine. Verify your input and write permissions or try another filepath." % locals()
    # ensure target folder has write permissions
    try:
        f = open(path + "test.txt", "w")
        f.close()
        os.remove(path + "test.txt")
    except PermissionError:
        return path, "Blender does not have write permissions for the following path: '%(path)s'" % locals()
    return path, None

def getNameOutputFiles():
    """return nameOutputFiles (defaults to current project name"""
    scn = bpy.context.scene
    lastSlash = scn.rfc_renderDumpLoc.rfind("/")
    filename = bpy.path.display_name_from_filepath(bpy.data.filepath)
    n = filename if lastSlash in [-1, len(scn.rfc_renderDumpLoc) - 1] else scn.rfc_renderDumpLoc[lastSlash + 1:]
    return bashSafeName(n)

def getRunningStatuses():
    return ["Rendering...", "Preparing files...", "Finishing..."]

def getNumRenderedFiles(jobType, frameRange=None, fileName=None):
    scn = bpy.context.scene
    dumpPath = getRenderDumpPath()[0]
    if jobType == "image":
        numRenderedFiles = len([f for f in os.listdir(dumpPath) if "_seed-" in f and f.endswith(str(frameRange[0]) + scn.rfc_imExtension)])
    else:
        renderedFiles = []
        for f in os.listdir(dumpPath):
            try:
                frameNum = int(f[-8:-4])
            except:
                continue
            if frameNum in frameRange and fnmatch.fnmatch(f, "{fileName}_????{extension}".format(fileName=fileName, extension=scn.rfc_animExtension)):
                renderedFiles.append(f)
        numRenderedFiles = len(renderedFiles)
    return numRenderedFiles

def cleanupCancelledRender(classObject, context, killPython=True):
    """ Kills running processes when render job cancelled """
    wm = context.window_manager
    wm.event_timer_remove(classObject._timer)
    for j in range(len(classObject.processes)):
        if classObject.processes[j]:
            try:
                classObject.processes[j].kill()
            except:
                pass
    if killPython:
        subprocess.call("ssh -T -oStrictHostKeyChecking=no -x {login} 'killall -9 python'".format(login=bpy.props.rfc_serverPrefs["login"]), shell=True)

def changeContext(context, areaType):
    """ Changes current context and returns previous area type """
    lastAreaType = context.area.type
    context.area.type = areaType
    return lastAreaType

def updateServerPrefs():
    scn = bpy.context.scene
    # verify rsync is installed on local machine
    localVerify = subprocess.call("rsync --version", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if localVerify > 0:
        return {"valid":False, "errorMessage":"rsync not installed on local machine."}

    # run setupServerPrefs() and store last results to oldServerPrefs
    oldServerPrefs = bpy.props.rfc_serverPrefs
    newServerPrefs = setupServerPrefs()
    if newServerPrefs["valid"]:
        bpy.props.rfc_serverPrefs = newServerPrefs
    else:
        return newServerPrefs

    # verify host server login, built from user entries, correspond to a responsive server, and that defined renderFarm path is writable
    checkConnectionCommand = "ssh -T -oBatchMode=yes -oStrictHostKeyChecking=no -oConnectTimeout=10 -x {login} 'mkdir -p {remotePath}; touch {remotePath}test'".format(login=bpy.props.rfc_serverPrefs["login"], remotePath=bpy.props.rfc_serverPrefs["path"].replace(" ", "\\ "))
    rc = subprocess.call(checkConnectionCommand, shell=True)
    if rc != 0:
        return {"valid":False, "errorMessage":"ssh to '{login}' failed (return code: {rc}). Check your settings, ensure ssh keys are setup, and verify your write permissions for '{remotePath}' on remote server (see error in terminal)".format(login=bpy.props.rfc_serverPrefs["login"], rc=rc, remotePath=bpy.props.rfc_serverPrefs["path"])}

    if bpy.props.rfc_serverPrefs != oldServerPrefs:
        # initialize server groups enum property
        groupNames = [("All Servers", "All Servers", "Render on all servers")]
        for groupName in bpy.props.rfc_serverPrefs["servers"]:
            tmpList = [groupName, groupName, "Render only servers in this group"]
            groupNames.append(tuple(tmpList))
        bpy.types.Scene.rfc_serverGroups = bpy.props.EnumProperty(
            attr="serverGroups",
            name="Servers",
            description="Choose which hosts to use for render processes",
            items=groupNames,
            default="All Servers")
    return {"valid":True, "errorMessage":None}


def setRemoteSettings(scn, rd=None, rt=None):
    rd = rd or scn.rfc_renderDevice
    rt = rt or list(scn.rfc_renderTiles)
    scn.cycles.device = rd
    scn.render.tile_x = rt[0]
    scn.render.tile_y = rt[1]
    return rd, rt

def render_farm_handle_exception():
    handle_exception(log_name="Render Farm Client log", report_button_loc="View 3D > Tools > Render > Render on Servers > Report Error")
