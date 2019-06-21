import sys
import os
import subprocess
FFMPEG_ROOT='../lib/ffmpeg'
def get_frame_rate(filename):
    """
    returns the exact frame rate
    requires ffprobe.exe
    author: Steven Penny
    modified by: gerard del castillo
    """
    if not os.path.exists(filename):
        sys.stderr.write("ERROR: filename %r was not found!" % (filename,))
        return -1         
    out = subprocess.check_output([FFMPEG_ROOT+'/ffprobe.exe',filename,
        "-v","0",
        "-select_streams","v",
        "-print_format","flat",
        "-show_entries",
        "stream=r_frame_rate"])
    rate = str(out).split('=')[1].split('"')[1].split('/')
    if len(rate)==1:
        return float(rate[0])
    if len(rate)==2:
        return float(rate[0])/float(rate[1])
    return -1

def get_label_names(label_groups):
    """
    returns a list of the label names
    """
    return [
        y 
        for x in label_groups 
        for y in x['label_names']
    ]

def get_group_names(label_groups):
    """
    returns a list of the group names
    """
    return [x['group_name'] for x in label_groups]