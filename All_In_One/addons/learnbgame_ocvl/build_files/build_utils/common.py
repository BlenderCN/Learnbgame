import os
import shutil

import subprocess
import sys


def get_blender_build_path(blender_build_dir_name, cwd):
    out = True
    head, tail = os.path.split(cwd)
    while out:
        head, tail = os.path.split(head)
        if tail is '':
            raise Exception(f"Can't find '{blender_build_dir_name}' in path")
        if tail == blender_build_dir_name:
            out = False

    cwd = os.path.join(head, blender_build_dir_name)
    print(f"Current work directory: {cwd}")
    return cwd


def cmd(bash_cmd, accepted_status_code=None, stdout=None):
    accepted_status_code = accepted_status_code or [0]
    stdout = stdout or sys.stdout
    print("-----CMD-----")
    print(bash_cmd)
    process = subprocess.Popen(bash_cmd.split(), stdout=stdout, stderr=sys.stderr)
    out, err = process.communicate()
    if process.returncode not in accepted_status_code:
        raise Exception(f"Status code from command {bash_cmd}: {process.returncode}")
    print("-----SUCCESS----")
    return out, err


def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            print(f"Make dir: {dest}")
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        print(f"Override {src} -> {dest}")
        shutil.copyfile(src, dest)
