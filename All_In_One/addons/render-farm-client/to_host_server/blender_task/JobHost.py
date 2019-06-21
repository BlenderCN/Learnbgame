#!/usr/bin/env python
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
import telnetlib
import threading
import time
from supporting_methods import *  #start_tasks
# from multiprocessing import Pool
from multiprocessing import Process

class JobHost(threading.Thread):
    """ Write tooltip here """

    def __init__(self, hostname, jobs_list=None, thread_func=None, kwargs=None, callback=None, timeout=.01, print_connection_issue=False, verbose=0, error_callback=None, max_on_host=4, cleanup_when_done=False):
        super(JobHost, self).__init__()
        self.verbose = verbose
        self.rfc_timeout = timeout
        self.firstTime = True
        self.cleanup_when_done=cleanup_when_done
        self.print_connection_issue = print_connection_issue

        # The name of the host this object represents
        self.hostname = hostname
        # This is the name of the thread.
        self.name = "Thread-{hostname}".format(hostname=hostname)

        # Set until it is verified that we can reach the host.
        self.reachable = False
        # In case the status of the host changes after we have checked it once
        self.reachable_change = False
        self.is_telnetable() # Will set up self.reachable

        self.max_on_host = max_on_host
        # List of job strings. This is how jobs are initially handed over to the host
        self.jobs_list = jobs_list
        if jobs_list:
            self.job_count = len(jobs_list)
        else:
            self.job_count = 0

        self.jobs = dict() # Stores info about a job. Indexed by job string

        if not kwargs: kwargs = dict()
        self.kwargs = kwargs # Arguments to be handed over to the thread_func

        if not thread_func: thread_func = lambda x: x # Defaults to identity function
        self.thread_func = thread_func # The main function that should be run by JobHost

        if not callback: callback = lambda *x: x
        self.callback = callback # Set up callback so host can notify outside world when it finishes jobs
        self.error_callback = error_callback # If an error comes up while working on jobs

        self.killed  = False
        self.started = False
        # self.pool = Pool(processes=self.max_on_host,maxtasksperchild=1)

    def __str__(self):
        aString = threading.Thread.__str__(self)
        return aString

    def set_kwargs(self, kwargs):
        self.kwargs = kwargs

    def set_callback(self, callback):
        self.callback = callback

    def set_error_callback(self, error_callback):
        self.error_callback = error_callback

    def is_complete_without_error(self):
        for job in self.jobs:
            if not job["exit_status"] == 0:
                return False
        return True

    def get_jobs_status(self):
        return self.jobs

    def get_job_count(self):
        return self.job_count

    def get_hostname(self):
        return self.hostname

    def is_reachable(self):
        return self.reachable

    def is_started(self):
        return self.started

    def print_job_status(self, state, job=None, verbose=1):
        if self.verbose >= 2 or verbose >= 1:
            pflush("Job {state} on host {hostname}".format(state=state, hostname=self.get_hostname()))
            if self.verbose >= 2:
                pflush(job + "\n")

    def run(self):
        # checks job queue for jobs that were created on the host before the start command was issued.
        # runs host main loop
        acc = 0
        while True:
            if acc < self.max_on_host:
                job = self.get_next_job()
                # Start jobs in the pool if we are not already past the max running jobs
                if job and job not in self.jobs:
                    self.start_job(job)
                    acc += 1
            # Check on child processes
            for job_key in self.jobs.keys():
                job_process=self.jobs[job_key]['process']
                if( job_process.exitcode != None and 'printed' not in self.jobs[job_key] ):
                    acc -= 1
                    exitstatus = job_process.exitcode
                    self.jobs[job_key]['exit_status'] = exitstatus
                    self.jobs[job_key]['printed'] = True
                    if exitstatus == 0:
                        (self.get_callback())(self.hostname,job_key)
                    else:
                        (self.get_error_callback())(self.hostname,job_key)

                    self.job_complete(job=job_key)
            if self.terminate():
                break
        for job_string in self.jobs.keys():
            self.jobs[job_string]['process'].terminate()

    def terminate(self):
        return ( self.cleanup_when_done and self.started and self.all_jobs_complete() or self.jobHostKilled() )

    def jobHostKilled(self):
        return self.killed

    def kill(self):
        self.killed = True

    def all_jobs_complete(self):
        remaining_jobs = 0
        for job_string in self.jobs.keys():
            if not "exit_status" in self.jobs[job_string]:
                remaining_jobs += 1
        return remaining_jobs == 0

    def get_next_job(self):
        if self.can_start_job():
            return self.jobs_list.pop()
        return False

    def can_start_job(self):
        return (self.job_count <= self.max_on_host) and (len(self.jobs_list) > 0)

    def can_take_job(self):
        return self.job_count < self.max_on_host

    def get_callback(self):
        return self.callback

    def get_error_callback(self):
        return self.error_callback

    def start_job(self, job):
        self.started = True
        self.jobs[job] = dict()
        self.kwargs["jobString"] = job
        self.kwargs["hostname"] = self.get_hostname()
        self.kwargs["firstTime"] = self.firstTime
        job_process=Process(target=self.thread_func,kwargs=self.kwargs)
        job_process.start()
        self.jobs[job]['process'] = job_process

    def job_complete(self, job=None, exit_status=0):
        self.firstTime = False
        self.job_count -= 1

        # Call the callback
        if self.jobs[job]["exit_status"] == 0:
            self.print_job_status("finished", job)
            if "get_callback" in self.jobs[job] and self.jobs[job]["get_callback"] != None:
                callback = self.jobs[job]["get_callback"]()
                if not callback == None:
                    callback(self.hostname, job)
                elif self.verbose >= 2:
                    print("No callback specified.")
        else:
            if "error_callback" in self.jobs[job] and self.jobs[job]["error_callback"] != None:
                callback = self.jobs[job]["error_callback"]()
                if not callback == None:
                    callback(self.hostname, job)
                elif self.verbose >= 2:
                    print("No error callback specified.")

    def is_telnetable(self):
        try:
            tn = telnetlib.Telnet(self.hostname, 22, self.rfc_timeout)
            self.reachable = True
            return True
        except Exception as e:
            if self.verbose >= 1 and self.print_connection_issue:
                print("Encountered following error connecting to '" + str(self.hostname) + "': " + str(e))
            if self.reachable:
                self.reachable_change = True
            self.reachable = False
            return False

    def add_jobs(self, jobs):
        for job in jobs:
            self.add_job(job)
            self.job_count += 1

    def add_job(self, job):
        if not self.jobs_list: self.jobs_list = list()
        self.jobs_list.append(job)
        self.job_count += 1

    def print_job_list(self):
        print(self.jobs_list)

break_loop = False

def callback_func(host, job):
    global break_loop
    break_loop = True

def error_callback_func(host, job):
    pass


import json

if __name__ == "__main__":
    verbose = 0
    # self, hostname, thread_func=None, kwargs=None, callback=None, verbose=False, error_callback=None

    # testDict1 = {"username":"nwhite",
    #     "verbose":verbose, "projectPath":"/tmp/nwhite/test", "remoteSyncBack":"/tmp/nwhite/test/results", "projectName":"test", "projectSyncPath":"/tmp/nwhite/test/toRemote/", "projectOutuptFile":"/tmp/nwhite/test/"}
    # def start_tasks( hostname, jobString, remoteResultsPath, localResultsPath, JobHostObject=None, firstTime=True, frame=False, progress=False, verbose=0):
    testDict1 = {
        'projectName':'test',
        'projectSyncPath':'/tmp/renderFarm-cgearhar/test/toRemote/',
        'username':'cgearhar',
        'verbose':0,
        'projectPath':'/tmp/renderFarm-cgearhar/test',
        'remoteResultsPath':'/tmp/renderFarm-cgearhar/test/results',
        'localResultsPath':'/tmp/renderFarm-cgearhar/test/results'
    }

    projectPath = "/tmp/renderFarm-cgearhar/test"

    testFilePath = os.path.joins(projectPath, "test.blend")

    jobsList = [ "blender -b %(testFilePath)s -x 1 -o //results/test_####.png -s 1 -e 1 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/1.out.log" % locals(),
                    "blender -b %(testFilePath)s -x 1 -o //results/test_####.png -s 2 -e 2 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/2.out.log" % locals()]
    h1 = JobHost(hostname="cse21701", thread_func=start_tasks, kwargs=testDict1, verbose=verbose, callback=callback_func, jobs_list=jobsList, max_on_host=2)
    h1.add_job("blender -b %(testFilePath)s -x 1 -o //results/test_####.tga -s 3 -e 3 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/3.out.log" % locals())
    h1.add_job("blender -b %(testFilePath)s -x 1 -o //results/test_####.tga -s 4 -e 4 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/4.out.log" % locals())
    h1.add_job("blender -b %(testFilePath)s -x 1 -o //results/test_####.png -s 5 -e 5 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/5.out.log" % locals())
    h1.add_job("blender -b %(testFilePath)s -x 1 -o //results/test_####.png -s 6 -e 6 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/6.out.log" % locals())
    h1.add_job("blender -b %(testFilePath)s -x 1 -o //results/test_####.png -s 7 -e 7 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/7.out.log" % locals())
    h1.add_job("blender -b %(testFilePath)s -x 1 -o //results/test_####.png -s 8 -e 8 -P  %(projectPath)s/blender_p.py -a > %(projectPath)s/8.out.log" % locals())
    h1.print_job_list()
    h1.start()
    try:
        while not( h1.terminate() ):
            print("some jobs remaining")
            time.sleep(2)
    except KeyboardInterrupt:
        print "terminating jobs"
        h1.kill()

    tDict = h1.get_jobs_status()
    print(tDict)
    for item in tDict.keys():
        print("{} : \n \t{}\n\t{}\n\t{} ".format(item,tDict[item]['exit_status'],tDict[item]["process"],tDict[item]['printed']))

    # h1.add_job("blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 5 -e 5 -P  /tmp/nwhite/test/blender_p.py -a")
    # try:
    #     while h1.running_job():
    #         print "Remaining jobs2: ", h1.get_job_count(), "remaining"
    #         time.sleep(2)
    # except KeyboardInterrupt:
    #     print "terminating other jobs"
    #     h1.terminate(terminate_pool=True)
    #
    # h1.terminate()
    # print(h1.get_jobs_status())
