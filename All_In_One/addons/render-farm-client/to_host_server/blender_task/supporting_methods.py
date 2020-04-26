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
import json
import numpy
import os
import re
import shlex
import sys
import subprocess

def pflush(string):
    """ Helper function that prints and flushes a string """
    print(string)
    sys.stdout.flush()

def eflush(string):
    """ Helper function that prints and flushes a string """
    sys.stderr.write(string)
    sys.stderr.flush()

def process_blender_output(hostname, line):
    """ helper function to process blender output and print helpful json object """

    status_regex = r"Fra:(\d+)\s.*Time:(\d{2}:\d{2}\.\d{2}).*Remaining:(\d{2}:\d+\.\d+)\s.*"
    hostcount = {}

    # Parsing the following output
    matches = re.finditer(status_regex, line)
    mod = 100
    for matchNum, match in enumerate(matches):
        matchNum = matchNum + 1
        frame = match.group(1)
        elapsed = match.group(2)
        remainingTime = match.group(3)
        json_obj = json.loads("{{ \"hn\" : \"{hostname}\", \"rt\" : \"{remainingTime}\", \"cf\" : \"{frame}\", \"et\" : \"{elapsed}\" }}".format(hostname=hostname, elapsed=elapsed, frame=frame, remainingTime=remainingTime))

        if hostname not in hostcount:
            hostcount[hostname] = 0

        currentCount = hostcount[hostname]
        if currentCount % mod == 99:
            # We want this to go out over stdout
            pflush("##JSON##{jsonString}##JSON##".format(jsonString=json.dumps(json_obj)))

        hostcount[hostname] += 1

def ssh_string(username, hostname, verbose=0):

    tmpStr = "ssh -oStrictHostKeyChecking=no {username}@{hostname}".format(username=username, hostname=hostname)
    if verbose >= 3:
        pflush(tmpStr)
    return tmpStr

def rsync_files_to_node_string(remoteResultsPath, projectSyncPath, username, hostname, projectPath, verbose=0):
    tmpStr = "rsync -e 'ssh -oStrictHostKeyChecking=no' --rsync-path='mkdir -p {remoteResultsPath} && rsync' -a {projectSyncPath} {username}@{hostname}:{projectPath}/".format(remoteResultsPath=remoteResultsPath.replace(" ", "\\ "), projectSyncPath=projectSyncPath, username=username, hostname=hostname, projectPath=projectPath)
    if verbose >= 3:
        pflush(tmpStr)
    return tmpStr

def rsync_files_from_node_string(username, hostname, remoteResultsPath, localResultsPath, outputName="", frameString="", verbose=0):
    tmpStr = "rsync -atu -e 'ssh -oStrictHostKeyChecking=no' --include='{outputName}{frameString}.???' --exclude='*' --remove-source-files --rsync-path='mkdir -p {localResultsPath} && rsync' {username}@{hostname}:{remoteResultsPath} {localResultsPath}".format(outputName=outputName, username=username, hostname=hostname, remoteResultsPath=remoteResultsPath, frameString=frameString, localResultsPath=localResultsPath.replace(" ", "\\ "))
    if verbose >= 3:
        pflush(tmpStr)
    return tmpStr

def start_tasks(projectName, projectPath, projectSyncPath, hostname, username, jobString, remoteResultsPath, localResultsPath, JobHostObject=None, firstTime=True, frame=False, progress=False, verbose=0):
    """ Render frame on remote server and get output file when finished """

    if verbose >= 2 and frame:
        pflush("Starting thread. Rendering frame {frame} on {hostname}".format(frame=frame, hostname=hostname))

    # get output file name
    startS = "-o //results/"
    endS = "_####."
    outputName = jobString[jobString.find(startS) + len(startS):jobString.find(endS)]
    if frame:
        frameString = "_{frame}".format(frame=str(frame).zfill(4))
    else:
        frameString = "_????"


    # First copy the files over using rsync
    rsync_to            = rsync_files_to_node_string(remoteResultsPath, projectSyncPath, username, hostname, projectPath, verbose)
    rsync_from          = rsync_files_from_node_string(username, hostname, remoteResultsPath, localResultsPath, outputName, frameString, verbose)
    ssh_c_string        = ssh_string(username, hostname, verbose)
    ssh_blender         = "{ssh_c_string} '{jobString}'".format(ssh_c_string=ssh_c_string, jobString=jobString)
    run_status          = {"p":-1, "q":-1, "r":-1}

    # only sync project files if they haven't already been synced
    if firstTime:
        if verbose >= 3:
            pflush("Syncing project file {projectName}.blend to {hostname}\nrsync command: {rsync_to}".format(projectName=projectName, hostname=hostname, rsync_to=rsync_to))
        p = subprocess.call(rsync_to, shell=True)
        if verbose >= 3:
            pflush("Finished the rsync to host {hostname} with return code {p}".format(hostname=hostname, p=p))
        if p == 0:
            run_status["p"] = 0
        else:
            run_status["p"] = 1
    else:
        run_status["p"] = 0

    # Now start the blender command
    if verbose >= 3:
        pflush("blender command: {jobString}".format(jobString=jobString))

    q = subprocess.Popen(shlex.split(ssh_blender), stdout=subprocess.PIPE)

    # This blocks til q is done
    while type(q.poll()) == type(None):
        # This blocks til there is something to read
        line = q.stdout.readline()
        if progress:
            process_blender_output(hostname, line)

    # Successful blender
    if q.returncode == 0:
        run_status["q"] = 0

        if verbose >= 2 and frame:
            pflush("Successfully completed render for frame ({frame}) on hostname {hostname}.".format(frame=frame, hostname=hostname))
    else:
        eflush("blender error: {returncode}".format(returncode=q.returncode))
        run_status["q"] = 1


    # Now rsync the files in <remoteResultsPath> back to this host.
    if verbose >= 3:
        pflush("rsync pull: {rsync_from}".format(rsync_from=rsync_from))
    r = subprocess.call(rsync_from, shell=True)

    if r == 0 and q.returncode == 0:
        run_status["r"] = 0
        if verbose >= 2 and frame:
            pflush("Render frame ({frame}) has been copied back from hostname {hostname}".format(frame=frame, hostname=hostname))
    else:
        eflush("rsync error: {r}".format(r=r))
        run_status["r"] = 1

    return run_status["p"] + run_status["q"] + run_status["r"]

def buildJobString(projectPath, projectName, nameOutputFiles, frame, seedString=""):
    builtString = "blender -b {projectPath}/{projectName}.blend -x 1 -o //results/{nameOutputFiles}{seedString}_####.png -s {frame} -e {frame} -P {projectPath}/blender_p.py -a".format(projectPath=projectPath, projectName=projectName, nameOutputFiles=nameOutputFiles, seedString=seedString, frame=str(frame))
    return builtString

def buildJobStrings(frames, projectName, projectPath, nameOutputFiles, jobsPerFrame=False, servers=1): # jobList is a list of lists containing start and end values
    """ Helper function to build Blender job strings to be sent to client servers """

    jobStrings = []
    # the following code may be used in the future, if I decide to distribute animation renders amongst multiple servers
    # if not jobsPerFrame:
    #     jobsPerFrame = servers/len(frames)
    # else:
    #     jobsPerFrame = int(jobsPerFrame)
    if jobsPerFrame:
        for i in range(jobsPerFrame):
            for frame in frames:
                seedString = "_seed-{seedNum}".format(seedNum=str(i).zfill(len(str(servers))))
                builtString = buildJobString(projectPath, projectName, nameOutputFiles, frame, seedString)
                jobStrings.append(builtString)
    else:
        for frame in frames:
            builtString = buildJobString(projectPath, projectName, nameOutputFiles, frame)
            jobStrings.append(builtString)
    return jobStrings

def readFileFor(f, flagName):
    readLines = ""

    # skip lines leading up to '### BEGIN flagName ###'
    nextLine = f.readline()
    numIters = 0
    while nextLine != "### BEGIN {flagName} ###\n".format(flagName=flagName):
        nextLine = f.readline()
        numIters += 1
        if numIters >= 250:
            eflush("Unable to read with over 250 preceeding lines.")
            break
    # read following lines leading up to '### END flagName ###'
    nextLine = f.readline()
    numIters = 0
    while nextLine != "### END {flagName} ###\n".format(flagName=flagName):
        readLines += nextLine.replace(" ", "").replace("\n", "").replace("\t", "")
        nextLine = f.readline()
        numIters += 1
        if numIters >= 200:
            eflush("Unable to read over 200 lines.")
            break
    return readLines

def setServersDict(hostDirPath=False):
    if not hostDirPath:
        serverFile = open("{path}/remoteServers.txt".format(path=os.path.dirname(os.path.abspath(__file__))), "r")
    else:
        serverFile = open(hostDirPath, "r")
    servers = json.loads(readFileFor(serverFile, "REMOTE SERVERS DICTIONARY"))
    return servers

def testHosts(host, hosts_online, hosts_offline, start_tasks, verbose=0):
    jh = JobHost(hostname=host, thread_func=start_tasks, verbose=verbose)
    if jh.is_reachable():
        hosts_online.append(str(host))
    else:
        hosts_offline.append(str(host))

def getSupportedFileTypes():
    return ["png", "tga", "tif", "jpg", "jp2", "bmp", "cin", "dpx", "exr", "hdr", "rgb"]

def listHosts(hostDict):
    if type(hostDict) == list:
        return hostDict
    return [j for i in hostDict.keys() for j in hostDict[i]]

def stopWatch(value):
    """From seconds to Days;Hours:Minutes;Seconds"""

    valueD = ((value/365)/24)/60
    Days = int(valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = int(valueS)

    Days = str(Days).zfill(2)
    Hours = str(Hours).zfill(2)
    Minutes = str(Minutes).zfill(2)
    Seconds = str(Seconds).zfill(2)

    return "{Days};{Hours}:{Minutes};{Seconds}".format(Days=Days, Hours=Hours, Minutes=Minutes, Seconds=Seconds)
