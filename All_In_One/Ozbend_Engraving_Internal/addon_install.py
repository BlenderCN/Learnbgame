# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_Engraving_Internal
#
# Add-on installation script
#
# console command to install (win): "c:/Program Files/blender-2.79b-windows64/blender.exe" -b -P d:/addon_install.py -- -f d:/Ozbend_Engraving_Internal-master.zip
# console command to install (nix): blender -b -P /tmp/addon_install.py -- -f /tmp/Ozbend_Engraving_Internal-master.zip

import bpy
import sys
import argparse

__addon_name = 'Ozbend_Engraving_Internal-master'

if '--' in sys.argv:
    argv = sys.argv[sys.argv.index('--') + 1:]  # all args after '--'
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='source', metavar='FILE')
    args = parser.parse_known_args(argv)[0]
    bpy.ops.wm.addon_install(filepath=args.source, overwrite=True)
    bpy.ops.wm.addon_enable(module=__addon_name)
    # save user settings
    bpy.ops.wm.save_userpref()
