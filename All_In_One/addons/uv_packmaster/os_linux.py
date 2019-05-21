import os
import subprocess


def os_exec_extension():
    return ''

def os_packer_dirname():
    return 'lin'

from .utils import get_packer_path

def os_platform_check(packerPath):
    packer_path = get_packer_path()
    # os.chmod(packer_path, 0o755)
    cmd_line = 'chmod u+x "' + packer_path + '"'
    proc = subprocess.Popen(cmd_line, shell=True)

    try:
        proc.wait(5)
        if proc.returncode != 0:
            raise Exception()
    except:
        return False, 'Error: could not set executable permission on the packer binary'

    return True, ''