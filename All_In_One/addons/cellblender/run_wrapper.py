#!/usr/bin/env python3

from sim_runner_queue import OutputQueue
import sys
import signal
import subprocess as sp


if __name__ == '__main__':

  wd = sys.argv[1]
  if sys.version_info.major == 3:
    cmd = input()
    args = input()
  else:
    cmd = raw_input()
    args = raw_input()

  sys.stdout.write('cmd: {0}   args: {1}   wd: {2}\n'.format(cmd, args, wd))

  cmd_list = []
  cmd_list.append(cmd)
  cmd_list.extend(args.split())

  proc = sp.Popen(cmd_list, cwd=wd, bufsize=1, shell=False, close_fds=False, stdout=sp.PIPE, stderr=sp.PIPE)

  def sig_handler(signum, frame):
    sys.stdout.write('Sending signal: {0} to child PID: {1}\n'.format(signum, proc.pid))
    sys.stdout.flush()
    proc.send_signal(signum)
    sys.stdout.write('Terminated run_wrapper.py\n')
    sys.stdout.flush()
    exit(15)

  signal.signal(signal.SIGTERM, sig_handler)

  output_q = OutputQueue() 
  rc, res = output_q.run_proc(proc,passthrough=True)

  exit(abs(rc))

