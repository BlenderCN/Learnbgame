import os,subprocess
from . import JVM,Updater
from . import Logger as log


DDS_DL={
    "url":"https://github.com/riccardobl/DDSWriter/releases/download/1.2.1/DDSWriter-1.2.1.jar",
    "hash":"d6ac871f4f75c1c101700d5ac3c3e9ab2eba01b4fdada400146040dac5a94fff"
}


ADDON_ROOT = os.path.dirname(os.path.realpath(__file__))
DDS_WRITER_PATH=os.path.join(ADDON_ROOT,"bin","DDSWriter.jar")

INITIALIZED=False
def init():
    global INITIALIZED
    if not INITIALIZED:
        Updater.updateFile(DDS_DL["url"],DDS_WRITER_PATH,DDS_DL["hash"])
        log.info("Use dds writer "+DDS_WRITER_PATH)
        INITIALIZED=True

def export(format_list=[],srgb_list=[],input_list=[],output_list=[],XMX=""):
    init()
    VMARGS=[]

    if XMX!="":
        VMARGS.extend(["-Xmx",XMX])

    JVM.exec(
        jar=DDS_WRITER_PATH,
        args=[
            "--use-opengl","--gen-mipmaps","--srgblist",srgb_list,"--format",format_list,"--inlist",input_list,"--outlist",output_list
        ],
        vmArgs=VMARGS
    )        