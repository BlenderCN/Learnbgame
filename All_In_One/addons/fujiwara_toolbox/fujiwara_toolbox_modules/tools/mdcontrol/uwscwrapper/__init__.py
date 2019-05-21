import os
import subprocess

def q(text):
    return '"%s"' % str(text)

def qq(text):
    return '"%s"' % str(text)


uwsc_process = None

def call(command, *args):
    argstr = qq(command)
    for arg in args:
        argstr += " " + qq(arg)

    exedir = os.path.dirname(__file__)
    cmdstr = "%s %s" % (qq(exedir + os.sep + "uwscwrapper.exe"), argstr)
    print(cmdstr)
    global uwsc_process
    uwsc_process = subprocess.Popen(cmdstr)

def wait():
    global uwsc_process
    try:
        uwsc_process.wait(1)
    except:
        pass
    uwsc_process = None

def click_item(name):
    call("MovetoItem", name)
    wait()

def activate(name):
    call("ActivateWindow", name)
    wait()

def set_window_transform(x,y,w,h):
    call("SetWindowAbs",x,y,w,h)
    wait()
