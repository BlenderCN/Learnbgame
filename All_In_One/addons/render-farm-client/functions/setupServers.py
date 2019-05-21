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
import bpy
import json
import os
from os.path import dirname, abspath

def getLibraryPath():
    # Full path to module directory
    addons = bpy.context.user_preferences.addons

    libraryPath = dirname(dirname(abspath(__file__)))

    if not os.path.exists(libraryPath):
        raise NameError("Did not find addon from path {}".format(libraryPath))
    return libraryPath

def readFileFor(f, flagName):
    readLines = ""

    # skip lines leading up to '### BEGIN flagName ###'
    nextLine = f.readline()
    numIters = 0
    while nextLine != "### BEGIN {flagName} ###\n".format(flagName=flagName):
        nextLine = f.readline()
        numIters += 1
        if numIters >= 300:
            raise ValueError("Unable to find '### BEGIN {flagName} ###' in the first 300 lines of Remote Servers file".format(flagName=flagName))

    # read the following lines leading up to '### END flagName ###'
    nextLine = f.readline()
    numIters = 0
    while nextLine != "### END " + flagName + " ###\n":
        readLines += nextLine.replace(" ", "").replace("\n", "").replace("\t", "")
        nextLine = f.readline()
        numIters += 1
        if numIters >= 250:
            print("Unable to read over 250 lines.")
            raise ValueError("'### END {flagName} ###' not found within 250 lines of '### BEGIN {flagName} ###' in the Remote Servers file".format(flagName=flagName))

    return readLines

def invalidEntry(field):
    return "Could not load '{field}'. Please read the instructions carefully to make sure you've set up your file correctly".format(field=field)

def setupServerPrefs():
    # variable definitions
    libraryServersPath = os.path.join(getLibraryPath(), "servers", "remoteServers.txt")
    serverFile = open(libraryServersPath,"r")

    # set SSH login information for host server
    try:
        username = readFileFor(serverFile, "SSH USERNAME").replace("\"", "")
        test = username[0] # fails if username is empty string
    except:
        return {"valid":False, "errorMessage":invalidEntry("SSH USERNAME")}
    try:
        hostServer = readFileFor(serverFile, "HOST SERVER").replace("\"", "")
        test = hostServer[0] # fails if hostServer is empty string
    except:
        return {"valid":False, "errorMessage":invalidEntry("HOST SERVER")}
    try:
        extension = readFileFor(serverFile, "EXTENSION").replace("\"", "")
    except:
        return {"valid":False, "errorMessage":invalidEntry("EXTENSION")}

    # build SSH login information
    login = "{username}@{hostServer}{extension}".format(username=username, hostServer=hostServer, extension=extension)
    hostConnection = "{hostServer}{extension}".format(hostServer=hostServer, extension=extension)

    # set base path for host server
    try:
        path = readFileFor(serverFile, "HOST SERVER PATH").replace("\"", "")
    except:
        return {"valid":False, "errorMessage":invalidEntry("HOST SERVER PATH")}

    # format host server path
    for char in " <>:\"\|?*.^":
        path = path.replace(char, "_")
    path = path.replace("$username$", username)
    if not path.endswith("/") and path != "":
        path += "/"

    # read file for servers dictionary
    try:
        tmpServers = readFileFor(serverFile, "REMOTE SERVERS DICTIONARY").replace("'", "\"")
    except:
        return {"valid":False, "errorMessage":invalidEntry("REMOTE SERVERS DICTIONARY")}

    # convert servers dictionary string to object
    try:
        servers = json.loads(tmpServers)
    except:
        return {"valid":False, "errorMessage":invalidEntry("dictionary")}

    return {"valid":True, "servers":servers, "login":login, "path":path, "hostConnection":hostConnection}

def writeServersFile(serverDict, serverGroups):
    f = open(os.path.join(getLibraryPath(), "to_host_server", "servers.txt"), "w")

    # define dictionary 'serversToUse'
    if serverGroups == "All Servers":
        serversToUse = serverDict
    else:
        serversToUse = {}
        serversToUse[serverGroups] = serverDict[serverGroups]

    # write dictionary 'serversToUse' to 'servers.txt'
    f.write("### BEGIN REMOTE SERVERS DICTIONARY ###\n")
    f.write(str(serversToUse).replace("'", "\"") + "\n")
    f.write("### END REMOTE SERVERS DICTIONARY ###\n")
