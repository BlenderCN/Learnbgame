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
from __future__ import print_function
import argparse
import fnmatch
import getpass
import json
import os
import re
import signal
import subprocess
import sys
import telnetlib
from JobHost import *
from JobHostManager import *
from VerboseAction import verbose_action

# Set up parameters
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--frame_range", action="store", default="[]", help="Pass a list of frame numbers (no spaces) to be rendered.")
# Takes a string dictionary of hosts
# If neither of these arguments are provided, then use the default hosts file to load hosts
parser.add_argument("-d", "--hosts", action="store", default=None, help="Pass a dictionary or list of hosts. Should be valid json.")
parser.add_argument("-H", "--hosts_online", action="store_true", default=None, help="Telnets to ports to find out if a host is availible to ssh into, skips everything else.")
parser.add_argument("-i", "--hosts_file", action="store", default="remoteServers.txt", help="Pass a filename from which to load hosts. Should be valid json format.")
parser.add_argument("-m", "--max_server_load", action="store", default=1, help="Max render processes to run on each server at a time.")
parser.add_argument("-a", "--average_results", action="store_true", default=None, help="Average frames when finished.")
parser.add_argument("-j", "--jobs_per_frame", action="store", default=False, help="Number of jobs to queue for each frame")
parser.add_argument("-s", "--samples", action="store", default=False, help="Number of samples to render per job")
parser.add_argument("-t", "--connection_timeout", action="store", default=.01, help="Pass a float for the timeout in seconds for telnet connections to client servers.")
# NOTE: this parameter is currently required
parser.add_argument("-n", "--project_name", action="store", default=False) # just project name. default path will be in /tmp/blenderProjects
# TODO: test this for directories other than toRemote
parser.add_argument("-S", "--local_sync", action="store", default="./toRemote", help="Pass a full or relative path to sync to the project directory on remote.")
# NOTE: remote_results_path will sync the directory at results
parser.add_argument("-r", "--remote_results_path", action="store", default="results", help="Pass a path to the directory that should be synced back.")
# NOTE: passing the contents flag will sync back the contents from the directory given in remote_results_path
parser.add_argument("-c", "--contents", action="store_true", default=False, help="Pass a path to the directory that should be synced back.")
parser.add_argument("-C", "--command", action="store", help="Run the command on the remote host.")
parser.add_argument("-v", "--verbose", action=verbose_action, nargs="?", default=0)
parser.add_argument("-p", "--progress", action="store_true", help="Prints the progress to stdout as a json object.")
parser.add_argument("-R", "--project_root", action="store", help="Root path for storing project files on host server.")
parser.add_argument("-o", "--output_file_path", action="store", default=False, help="Local folder to rsync files back into when done")
parser.add_argument("-O", "--name_output_files", action="store", default=False, help="Name to use for output files in results directory.")

def signal_handler(signal, frame):
    sys.exit(1)

def main():
    """ Main function runs when blender_task is called """

    startTime = time.time()
    args = parser.parse_args()
    verbose = args.verbose

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Getting hosts from some source
    if args.hosts_file:
        hosts = listHosts(setServersDict(args.hosts_file))
    elif args.hosts:
        hosts = listHosts(args.hosts)
    else:
        hosts = listHosts(HOSTS)

    # Test hosts to see which ones are available
    host_objects = dict()
    hosts_online = list()
    hosts_offline = list()

    max_server_load = int(args.max_server_load)
    for host in hosts:
        jh = JobHost(hostname=host, timeout=float(args.connection_timeout), thread_func=start_tasks, verbose=verbose, print_connection_issue=args.hosts_online, max_on_host=max_server_load)
        if jh.is_reachable():
            hosts_online.append(str(host))
        else:
            hosts_offline.append(str(host))
        host_objects[host] = jh
    numHosts = len(hosts_online)

    # if this parameter is passed, print number of servers online and exit
    if args.hosts_online:
        if verbose >= 2: print("Hosts Online : ")
        print(hosts_online)
        if verbose >= 2: print("Hosts Offline: ")
        print(hosts_offline)
        sys.exit(0)
    # Print the start message
    elif verbose >= 1:
        pflush("Starting distribute task...")

    # Verify there are hosts available
    if len(hosts_online) == 0:
        sys.stderr.write("No hosts available.")
        sys.exit(58)
    elif verbose >= 1:
        print("hosts available: {numHostsOnline}".format(numHostsOnline=len(hosts_online)))

    # Set up 'projectRoot' as root path for project on host and client servers
    username = getpass.getuser()
    if not args.project_root:
        projectRoot = os.path.join("/tmp", username)
    else:
        if args.project_root[-1] == "/":
            args.project_root = args.project_root[:-1]
        projectRoot = args.project_root

    # Set up 'projectName', 'projectPath', 'projectSyncPath', 'localResultsPath' & 'remoteResultsPath'
    if args.project_name:
        if not args.name_output_files:
            args.name_output_files = args.project_name

        projectName = args.project_name
        projectPath = os.path.join(projectRoot, projectName)
        # Make the <projectRoot>/<projectname> directory
        if not os.path.exists(projectPath):
            os.mkdir(projectPath)

        if not args.local_sync or args.local_sync == "./toRemote":
            workingDir = os.path.dirname(os.path.abspath(__file__))
            # Defaults to ./toRemote directory in working directory
            if os.path.exists(os.path.join(workingDir, "toRemote")):
                projectSyncPath = "{workingDir}/toRemote/".format(workingDir=workingDir)
            # Otherwise, tries to find toRemote in <projectRoot>/<projectname>/toRemote
            else:
                tmpDir = os.path.join(projectPath, "toRemote")
                # If this is the case, we literally have nothing to sync :(
                if not os.path.exists(tmpDir):
                    os.mkdir(tmpDir)
                projectSyncPath = "{tmpDir}/".format(tmpDir=tmpDir)
        else:
            projectSyncPath = args.local_sync

        if args.remote_results_path == "results":
            remoteResultsPath = os.path.join(projectPath, 'results')
        else:
            remoteResultsPath = args.remote_results_path
        if args.contents:
            remoteResultsPath = os.path.join(remoteResultsPath, "*")
        elif not remoteResultsPath.endswith("/"):
            remoteResultsPath += "/"

    else:
        pflush("sorry, please give your project a name using the -n or --project_name flags.")
        sys.exit(0)

    # Set up 'localResultsPath'
    if not args.output_file_path:
        localResultsPath = os.path.join(projectPath, 'results')
        if not os.path.exists(localResultsPath):
            os.mkdir(localResultsPath)
        for file in os.listdir(localResultsPath):
            if fnmatch.fnmatch(file, '*_seed-*') or file[-3:] in getSupportedFileTypes():
                outputFile = os.path.join(localResultsPath, file)
                if args.verbose >= 3:
                    pflush('Removing {outputFile} from project dir.'.format(outputFile=outputFile))
                os.remove(outputFile)
    else:
        if not os.path.exists(localResultsPath):
            os.mkdir(localResultsPath)
        localResultsPath = os.path.join(localResultsPath, '.')

    # Copy blender_p.py to project folder and append seed value if given
    pyFilePathDest = os.path.join(projectPath, "toRemote", "blender_p.py")
    subprocess.call("rsync -e 'ssh -oStrictHostKeyChecking=no' -a '{pyFilePathSource}' '{pyFilePathDest}'".format(pyFilePathSource=os.path.join(projectRoot, "blender_p.py"), pyFilePathDest=pyFilePathDest), shell=True)
    if args.samples:
        with open(pyFilePathDest, "a") as f:
            f.write("    scene.cycles.progressive = 'PATH'\n")
            f.write("    scene.cycles.samples = {samples}\n".format(samples=args.samples))
            f.write("    scene.cycles.use_square_samples = False\n")
            f.write("    try:\n")
            f.write("        scene.render.layers.active.cycles.use_denoising = False\n")
            f.write("    except Exception as e:\n")
            f.write("        print(e)\n")

    # Print frame range to be rendered
    frames = json.loads(args.frame_range)
    if verbose >= 1:
        pflush("{numFrames} frames queued from project '{projectName}': {frameRange}".format(numFrames=str(len(frames)), frameRange=str(frames), projectName=projectName))

    # set up variables for threads
    jobStrings = buildJobStrings(frames, projectName, projectPath, args.name_output_files, int(args.jobs_per_frame), numHosts)
    job_args = {
        "projectName":      projectName,
        "projectPath":      projectPath,
        "projectSyncPath":  projectSyncPath,
        "username":         username,
        "verbose":          verbose,
        "remoteResultsPath":remoteResultsPath,
        "localResultsPath": localResultsPath,
        "progress":         args.progress,
    }
    if len(frames) == 1:
        job_args["frame"] = frames[0]

    # Sets up kwargs, and callbacks on the hosts
    jhm = JobHostManager(jobs=jobStrings, hosts=host_objects, function_args=job_args, verbose=verbose, max_on_hosts=max_server_load)
    jhm.start()
    status = jhm.get_cumulative_status()

    if verbose >= 3:
        pflush("\nJob exit statuses:")
        jhm.print_jobs_status()

    # report on the success/failure of the tasks
    endTime = time.time()
    timer = stopWatch(endTime-startTime)
    if verbose >= 1:
        pflush("Elapsed time: {timer}".format(timer=timer))
        # TODO: Define failed earlier on... keep the strings the same to preserve render status
        failed = "?"
        if status == 0:
            pflush("Render completed successfully!")
        else:
            eflush("Render failed for {numFailed} jobs\n".format(numFailed=failed))

if __name__ == "__main__":
    main()
