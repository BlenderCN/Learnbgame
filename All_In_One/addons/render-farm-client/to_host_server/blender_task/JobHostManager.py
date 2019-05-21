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
import time
from JobHost import *

class JobHostManager():
    """ Manages and distributes jobs for all available hosts """

    def __init__(self, jobs=None, hosts=None, max_on_hosts=1, verbose=0, function_args=None):
        self.jobs               = jobs
        self.original_jobs      = list(jobs)
        self.function_args      = function_args

        self.hosts = dict()
        if not hosts: self.hosts = dict()
        else: self.add_hosts(hosts)
        self.host_keys = sorted(self.hosts.keys(), reverse=True)

        self.hosts_with_jobs = dict()
        self.job_status      = dict()
        self.errors          = list()
        self.verbose         = verbose
        self.max_on_hosts    = max_on_hosts
        self.stop_now        = False
        if self.jobs:
            self.process_jobs()

    def start(self):
        self.process_jobs()

    # This blocks
    def process_jobs(self):
        jobAccepted = False
        try:
            while not self.jobs_complete() and not self.stop_now:
                # time.sleep(.25)
                for aHost in self.host_keys:
                    if self.jobs_complete() or self.stop_now:
                        break
                    host = self.hosts[aHost]
                    if self.host_can_take_job(host=host) and len(self.jobs) > 0:
                        # time.sleep(.1)
                        hostname = host.get_hostname()
                        job = self.jobs.pop()
                        host.add_job(job)
                        if host not in self.hosts_with_jobs:
                            self.hosts_with_jobs[hostname] = host.get_job_count()
                        if not host.is_started():
                            host.start()
                        numQueued = str(len(self.jobs))
                        if self.verbose >= 3:
                            pflush("Running job {job} on host {host}. ({numQueued} jobs remain in queue)".format(job=job, host=hostname, numQueued=numQueued))
                        elif self.verbose >= 2:
                            pflush("Job sent to host '{hostname}' ({numQueued} jobs remain in queue)".format(hostname=hostname, numQueued=numQueued))
                        # else:
                        #     pflush("Job sent to host '{hostname}' ({numRemaining} jobs left)".format(hostname=hostname, numRemaining=self.remaining_jobs()))
                        pflush("Job sent to host '{hostname}' ({numQueued} jobs remain in queue)".format(hostname=hostname, numQueued=numQueued))
            self.stop_all_threads()
        except (KeyboardInterrupt, SystemExit):
            self.stop_all_threads()

    def jobs_complete(self):
        for job in self.original_jobs:
            if job in self.job_status:
                if self.job_status[job] != 0: return False
            else:
                return False
        return True

    def remaining_jobs(self):
        remaining = len(self.original_jobs)
        for job in self.original_jobs:
            if job in self.job_status:
                if self.job_status[job] == 0: remaining -= 1
        return remaining

    def add_hosts(self, hosts):
        if type(hosts) == list:
            for host in hosts:
                self.add_host(host)
        if type(hosts) == dict:
            for key in hosts.keys():
                host = hosts[key]
                host.set_kwargs(self.function_args)
                host.set_callback(self.host_finished_job)
                host.set_error_callback(self.host_failed_job)
                hosts[key] = host
            self.hosts = hosts

    def add_host(self, host):
        host.set_callback(self.host_finished_job)
        host.set_error_callback(self.host_failed_job)
        if self.function_args:
            host.set_kwargs(self.function_args)
        self.hosts[host.get_hostname()] = host

    def host_finished_job(self, hostname, job):
        if self.verbose >= 3:
            print("Completed Job on {hostname}: {job}".format(hostname=hostname, job=job))
        self.job_status[job] = 0

    def host_failed_job(self, hostname, job):
        error_string = "Failed Job on {hostname}: {job}".format(hostname=hostname, job=job)
        # eflush(error_string)
        if self.verbose >= 3:
            print(error_string)
        # self.add_job(job)
        self.job_status[job] = 1

    def host_can_take_job(self, hostname=None, host=None):
        if not host and not hostname: return False
        if host: hostname = host.get_hostname()
        if hostname in self.hosts:
            host = self.hosts[hostname]
        else:
            return False
        if host.can_take_job() and host.is_telnetable():
            return True
        return False

    def get_cumulative_status(self):
        return self.job_status

    def print_jobs_status(self):
        if self.jobs_complete():
            if self.verbose >= 2:
                print(self.get_cumulative_status())
        else:
            print("Jobs not yet completed.")

    def stop_all_threads(self):
        for hostname in self.hosts_with_jobs.keys():
            tHost = self.hosts[hostname]
            tHost.kill()
            self.stop()

    def stop(self):
        self.stop_now = True

    def __str__(self):
        acc = ''
        for host in self.hosts:
            acc += str(host) + ' ' + str(self.hosts[host])
        return acc


if __name__ == '__main__':
    print("TESTING JobHostManager Class")
    verbose = 2
    # jhm = JobHostManager(jobs=jobStrings,hosts=host_objects,function_args=job_args)
    # jobs = ['blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 7 -e 7 -P  /tmp/nwhite/test/blender_p.py -a' ,'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 6 -e 6 -P  /tmp/nwhite/test/blender_p.py -a' ,'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 5 -e 5 -P  /tmp/nwhite/test/blender_p.py -a' ,'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 4 -e 4 -P  /tmp/nwhite/test/blender_p.py -a' , 'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 2 -e 2 -P  /tmp/nwhite/test/blender_p.py -a' , 'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 1 -e 1 -P  /tmp/nwhite/test/blender_p.py -a','blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 3 -e 3 -P  /tmp/nwhite/test/blender_p.py -a' ]
    jobs = [
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 1 -e 1 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 2 -e 2 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 3 -e 3 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 4 -e 4 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 5 -e 5 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 6 -e 6 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 7 -e 7 -P  /tmp/nwhite/test/blender_p.py -a',
        'blender -b /tmp/nwhite/test/test.blend -x 1 -o //results/test_####.png -s 8 -e 8 -P  /tmp/nwhite/test/blender_p.py -a'
        ]

    kwargs = {
        'projectName':'test',
        'projectSyncPath':'/tmp/nwhite/test/toRemote/',
        'username':'nwhite',
        'verbose':None,
        'projectPath':'/tmp/nwhite/test',
        'remoteResultsPath':'/tmp/nwhite/test/results',
        'localResultsPath':'/tmp/nwhite/test/results'
        }

    cse217Host  = JobHost(hostname='cse21701', thread_func=start_tasks, kwargs=kwargs, verbose=3 ,max_on_host=3)

    hostObjects = [cse217Host]
    jhm = JobHostManager(jobs=jobs, hosts=hostObjects)


    jhm.print_jobs_status()
