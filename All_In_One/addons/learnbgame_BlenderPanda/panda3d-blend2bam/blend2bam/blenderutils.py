import os
import subprocess


def run_blender(args, blenderdir=''):
    os.path.join(blenderdir, 'blender')
    subprocess.check_call(['blender', '--background'] + args, stdout=subprocess.DEVNULL)


def run_blender_script(script, args, blenderdir=''):
    run_blender(
        [
            '-P', script,
            '--',
        ] + args,
        blenderdir=blenderdir
    )
