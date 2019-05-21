import bpy
from console_python import add_scrollback

import os
import sys
import subprocess
import threading


def make_animated_gif(m):
    if not os.path.exists(m):
        add_scrollback('{0} does not exist'.format(m), 'ERROR')

    initial_location = os.getcwd()
    try:
        os.chdir(m)
        f = "convert -delay 10 -loop 0 *png animated.gif"
        subprocess.Popen(f.split())
    except:
        add_scrollback('failed.. - with errors', 'ERROR')

    os.chdir(initial_location)


def make_optimized_animated_gif(m):

    try:
        temp_root = os.path.dirname(__file__)
        fp = os.path.join(temp_root, 'tmp', 'gifbatch.sh')
        print(fp)
        f2 = 'bash {0} {1}'.format(fp, m)
        print(f2)
        subprocess.Popen(f2.split())
    except:
        add_scrollback('failed.. - with errors', 'ERROR')


class Controller_Thread(threading.Thread):
    def __init__(self, commands):
        self.commands = commands
        threading.Thread.__init__(self)

    def run(self):
        print("starting controlled thread")
        print(__file__)
        subprocess.Popen(self.commands)
        print("ended controlled thread")


def cmd_controller(m):
    ''' this may need to do os checking, but i can only test on linux atm '''
    th = Controller_Thread(m.split())
    th.start()
