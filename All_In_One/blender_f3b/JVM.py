
import os,ssl
from . import Logger as log
import requests
import hashlib
import zipfile
import shutil,time
from . import Updater
import subprocess
VMS={
    "lin64":{
        "url":"https://bitbucket.org/alexkasko/openjdk-unofficial-builds/downloads/openjdk-1.7.0-u80-unofficial-linux-amd64-image.zip",
        "hash":"b87beb73f07af5b89b35b8656439c70fb7f46afdaa36e4a9394ad854c3a0b23d"
    },
    "win64":{
        "url":"https://bitbucket.org/alexkasko/openjdk-unofficial-builds/downloads/openjdk-1.7.0-u80-unofficial-windows-amd64-image.zip",
        "hash":"1b835601f4ae689b9271040713b01d6bdd186c6a57bb4a7c47e1f7244d5ac928"
    }

}

ADDON_ROOT = os.path.dirname(os.path.realpath(__file__))
OSV="lin64"
OSV="lin64"
if os.name=="nt":
    OSV="win64"
JVM_PATH=os.path.join(ADDON_ROOT,"bin","jvm",OSV)

INITIALIZED=False
def init():   
    global INITIALIZED
    if not INITIALIZED:
        jvm=VMS[OSV]
        Updater.updateArchive(jvm["url"],
                            JVM_PATH,
                            jvm["hash"]
        )
        INITIALIZED=True

def exec(jar,args="",vmArgs=""):
    init()
    jvm=os.path.join(JVM_PATH,"bin","java")
    if OSV == "win64":
        jvm+=".exe"    
    else:
        os.chmod(jvm, 755)
    command=[jvm]
    command.extend(vmArgs)
    command.extend(["-jar",jar])
    command.extend(args)
    log.info("Run "+str(command))
    subprocess.call(command)