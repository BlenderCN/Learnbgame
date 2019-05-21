#!/usr/bin/env python3
# $Id: $
# 
# Praja Render Manager - Render Job Executor
# Copyright (C) 2013 Adhi Hargo <cadmus_sw at yahoo.com>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#  
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
# USA.

import optparse
import io, os, re, shutil, subprocess, sys, time

def create_bpy_config(config_dict={}, **kwargs):
    '''Turns program configuration to Blender Python script form
    injectable to running Blender process. Note that this script is
    incompatible with relatively old Blender release's Python API (e.g
    2.55 or older will fail at quit_blender).'''
    f = io.StringIO()
    config_dict.update(kwargs)
    
    # Import required modules
    f.write('''
import bpy, os, sys

scn = bpy.context.scene
srn = scn.render
''')
    
    f.write('bpy.ops.render.render(animation=True)\n')

    f.seek(0)
    return f

def exec_render_process(program_path, file_path, config_dict):
    return_code = False
    command_args = ' -b %(blend)s -P %(script)s'

    basename = os.path.basename(file_path)
    rootname = os.path.splitext(basename)[0]
    script_path = 'job_%s.py' % rootname

    config_obj = create_bpy_config(config_dict)
    with open(script_path, 'w') as script_file:
        shutil.copyfileobj(config_obj, script_file)
    config_obj.close()

    command_str = program_path + command_args % dict(blend = file_path,
                                                     script = script_path)

    try:
        proc = subprocess.Popen(command_str, shell = True,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        while True:
            try:
                proc.poll()
                if proc.returncode != None:
                    return_code = proc.returncode == 0
                    break
                time.sleep(2)
            except KeyboardInterrupt:
                pass
    finally:
        os.remove(script_path)

    return return_code

def process_args():
    parser = optparse.OptionParser()
    parser.set_defaults(program_path = 'blender',
                        render_instances = 1)
    parser.add_option('-B', '--exe', dest='program_path',
                      help='Path of Blender executable',
                      metavar='PATH')
    parser.add_option('-i', '--instances', dest='render_instances',
                      help='How many instances of Blender to run',
                      metavar='COUNT')
    

    opts, args = parser.parse_args()
    return opts, args

def main(opts, args):
    files = args
    # if files != []:
    #     for file_path in range(0, opts.render_instances):
    #         pass
    for file_path in args:
        exec_render_process(opts.program_path, file_path, {})

if __name__ == '__main__':
    opts, args = process_args()
    main(opts, args)
