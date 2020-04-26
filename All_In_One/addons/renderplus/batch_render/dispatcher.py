# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#  IMPORTS
# ------------------------------------------------------------------------------

import bpy
import os
import json
import subprocess
import sys
import time
import logging

from subprocess import Popen

from renderplus import utils
from renderplus import data
from renderplus import actions
from renderplus import notifications

import renderplus.batch_render.state as state
import renderplus.batch_render.feed as feed


"""
Batch Dispatch Script

This script receives the batch data, generates the required files, runs each
render job and reports it's progress.

Read batch_notes.txt for more info.
"""
# ------------------------------------------------------------------------------
#  BATCH JOB
# ------------------------------------------------------------------------------

class RP_BatchJob(object):

    """
    Render job for Batch Rendering

    Contains all data for a single render job, as well
    as the methods to start and stop it properly.

    The class takes a data object, the file path to a state file
    and the current index (from the main loop in batch_control.py)
    """

    def __init__(self, data, pid, state_update, index, percent):
        self.data = data
        self.index = index
        self.state_update = state_update
        self.alive = True
        self.proc = None
        self.pid = pid
        self.percent = percent

        self.name = bpy.path.basename(data['blend_file'])
        self.custom_py = ''

    def start(self):
        """ Start the render job """

        if not self.data['enabled']:
            self.state_update(self.index, state.Code.DISABLED)
            self.alive = False
            return

        # Show state as running
        self.state_update(self.index, state.Code.RUNNING)

        # Generate py
        self.custom_py = self._generate_py()

        # Generate string
        command = []
        
        if data.prefs.blender_path:
            command += [utils.sane_path(data.prefs.blender_path)]
        else:
            command += [bpy.app.binary_path]
        
        command += [ 
                      '-b', self.data['blend_file'],
                      '-P', self.custom_py,
                      '-S', self.data['scene'],
                      '-nojoystick',
                      '-t', str(self.data['threads']),
                      '-x', '1',
                   ]
                   
        if self.data['format']:
            command += ['-F', self.data['format']]
            
            
        if self.data['output']:
            command += ['-o', self.data['output']]
        
        if self.data['animation']:
            command += [
                         '-s', str(self.data['frame_start']),
                         '-e', str(self.data['frame_end']),
                         '-a',
                       ]
        else:
            command += ['-f', str(self.data['frame_still'])]
        
        # File for errors
        error_path = os.path.join(
            os.path.dirname(__file__),
            'tmp',
            self.name +
            '.error')
            
        error_file = open(error_path, 'a')
        log_file = None

        # Create log file and add header
        if self.data['use_log']:
            try:
                if self.data['output']:
                    output_folder = self.data['output']
                else:
                    output_folder = utils.sane_path(self.data['blend_file'])
                    
                log_file = open(output_folder, 'w')
                
                text = 'Render job #' + str(self.index + 1) + ' from batch "'
                text += self.name + '", started on '
                text += time.strftime('%Y-%m-%d %H:%M:%S') + '\n'
                text += '-' * 80 + '\n\n'
                
                log_file.write(text)
                
                # Move stream position to the end of
                # the stream, so stdout comes below the title.
                log_file.seek(0, 2)
                
            except PermissionError:
                log.error('Couldn\'t write log for job ' + str(self.index))
                log.error('Log path is ' + output_folder)

        start_time = time.time()
        
        # Run command and wait
        self.proc = subprocess.Popen(
            command,
            shell=False,
            stderr=error_file,
            stdout=log_file,
            start_new_session=True)
        self.pid(str(self.proc.pid))
        self.proc.wait()

        log.debug('Running job #' + str(self.index))

        # Check if the process failed
        if self.proc.returncode == 0:
            result = state.Code.FINISHED
        else:
            result = state.Code.FAILED
            
        job_time = time.time() -  start_time 

        # Let the world know we're done
        self.alive = False
        self.state_update(self.index, result, job_time)

        return

    def _generate_py(self):
        """ Generate python file to modify scene data """

        # Generate file name
        file_name = os.path.join(
            os.path.dirname(__file__),
            'tmp',
            self.name + '_' + str(self.index)) + '.py'

        output = 'import bpy \n'
        output += 'sce = bpy.data.scenes["' + self.data['scene'] + '"] \n'

        # Compute Device
        if self.data['device'] != 'DEFAULT':
            
            if self.data['device'] == 'CPU':
                output += 'sce.cycles.device = \'CPU\'\n'
            else:
                output += 'prefs = bpy.context.user_preferences.system\n'
                output += 'prefs.compute_device_type = \'CUDA\'\n'
                output += 'prefs.compute_device = \''+self.data['device']+'\'\n'
                output += 'sce.cycles.device = \'GPU\'\n'
        
        
        # Size
        if self.data['size_x'] > 0:
            output += 'sce.render.resolution_x = ' + \
                str(self.data['size_x']) + '\n'

        if self.data['size_y'] > 0:
            output += 'sce.render.resolution_y = ' + \
                str(self.data['size_y']) + '\n'

        # Camera
        if 'camera' in self.data and self.data['camera'] != '':
            output += "sce.camera = bpy.data.objects['" + \
                self.data['camera'] + "'] \n"

        # World
        if self.data['world'] != '':
            output += "sce.world = bpy.data.worlds['" 
            output += self.data['world'] + "']\n"
            
        # Layers
        if 'layer' in self.data and self.data['layer'] != '':
            output += "for layer in sce.render.layers: \n"
            output += "    layer.use = False \n"
            output += "sce.render.layers['" + \
                self.data['layer'] + "'].use = True \n"

        # Set custom render percentage
        if self.percent[0]:
            output += 'sce.render.resolution_percentage = '
            output += str(self.percent[1]) + '\n'

        # Section render
        if 'use_section' in self.data:
            max_x = min(self.data['section_x'] + self.data['section_width'], 1)
            max_y = min(self.data['section_y'] + self.data['section_height'], 1)
                
            output += "sce.render.use_border = True \n"
            output += 'sce.render.border_min_x = ' + str(self.data['section_x']) + '\n'
            output += 'sce.render.border_min_y = ' + str(self.data['section_y']) + '\n'
            output += 'sce.render.border_max_x = ' + str(max_x) + '\n'
            output += 'sce.render.border_max_y = ' + str(max_y) + '\n'
                
        # Ignore border option
        if self.data['ignore_border']:
            output += "sce.render.use_border = False \n"
            
        # Cycles Samples
        if self.data['cycles_samples'] > 0:
            
            # Can't determine from here if render is using Branched or
            # simple Path tracing. So let's just set both and call it a day.
            samples =  'sce.cycles.aa_samples = {0} \n'  
            samples += 'sce.cycles.samples = {0} \n'  
            
            output += samples.format(self.data['cycles_samples'])


        # Custom overrides
        if 'custom_overrides' in self.data and self.data[
                'custom_overrides'] != '':
            for override in self.data['custom_overrides']:
                override['path'].replace('"', '\"')
                override['path'].replace("\'", "\'")

                output += 'sce.' + \
                    override['path'] + ' = ' + override['data'] + '\n'
                    
        with open(file_name, 'w') as stream:
            stream.write(output)

        log.debug('Overrides for job: ')
        log.debug(output)

        return file_name

    def stop(self):
        """ Terminate render job """

        self.proc.terminate()
        self.alive = False

        self.state_update(self.index, state.Code.FAILED)


# ------------------------------------------------------------------------------
#  SCRIPT INIT
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# LOGGING
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# DATA MANAGEMENT

# Argument number 5 (the last) should be the filepath to the
# data stream when calling this script.
with open(sys.argv[5], 'r') as stream:
    batch_data = json.load(stream)


# ------------------------------------------------------------------------------
# RSS FEED

use_feed = False

if batch_data['info']['use_rss']:
    try:
            
        feed.feed_file = batch_data['info']['rss_path']
        feed.jobs = batch_data['jobs']
        feed.setup_feed(batch_data['info']['name'], batch_data['jobs'])
        
        feed.write()
        use_feed = True
        
    except (FileNotFoundError, PermissionError):
        log.error('Could not create RSS file! Check filepath')
        feed.reset()


# ------------------------------------------------------------------------------
# TIME LOGGING

times_file = utils.path('batch_render', 'tmp', 
                         batch_data['info']['name'] + '_times.json')

times = {
            'start'     : time.time(),
            'finish'    : None,
            'jobs'      : [None] * len(batch_data['jobs']) ,   
        }


# ------------------------------------------------------------------------------
# STATE MANAGEMENT

state_data = []
state_file = utils.path('batch_render', 'tmp', 
             batch_data['info']['name'] + '_state.json')

state.from_file(state_file)

def update_state(index, status, job_time = 0):
    state.update(index, status)
    
    times['jobs'][index] = job_time
    
    if use_feed:
        feed.update(index, status)
        feed.write()


# ------------------------------------------------------------------------------
# PID UPDATE

def update_pid(pid):
    """ Write a PID file to use for terminating """

    path = utils.path('batch_render', 'tmp', batch_data['info']['name'] + '.pid')

    with open(path, 'w') as stream:
        stream.write(pid)


# ------------------------------------------------------------------------------
# PERCENTAGE

percent = (batch_data['info']['use_percentage'],
	       batch_data['info']['percentage'])


# ------------------------------------------------------------------------------
# PRE-RENDER ACTION

rp_settings = batch_data['info']['rplus_settings']
    
if 'pre_option' in rp_settings:
    if rp_settings['pre_option'] == 'command':
        Popen(rp_settings['pre'], shell = True)
    else:
        exec(rp_settings['pre'])
        

# ------------------------------------------------------------------------------
# MAIN LOOP

running = True
index = 0
job = None
    

while running:

    # No more jobs left
    # break the loop
    if not job and len(batch_data['jobs']) == index:
        running = False

    # A job has been terminated
    if job and not job.alive:
        job = None

    # Case for creating jobs
    if not job and len(batch_data['jobs']) > index:

        # Make new job
        if batch_data['jobs'][index]['enabled']:
            job = RP_BatchJob(
                batch_data['jobs'][index],
                update_pid,
                update_state,
                index,
                percent)
            job.start()
        else:
            times['jobs'][index] = -1

        # Move index
        index += 1

if not running:

    # Render+ Settings 
    # --------------------------------------------------------------------------
    if rp_settings['poweroff'] != 'DISABLED':
        actions.power_off(rp_settings['poweroff'])
    
    if rp_settings['notification_email']:
        name = batch_data['info']['name']
        subject = 'Batch {0} has finished rendering'.format(name)
        message = subject + '\n\n'
        
        notifications.mail(message, subject)
        
    if rp_settings['notification_desktop']:
        name = batch_data['info']['name']
        message = 'Batch {0} has finished rendering'.format(name)
        notifications.desktop(message)
        
    if 'post_option' in rp_settings:
        if rp_settings['post_option'] == 'command':
            Popen(rp_settings['post'], shell = True)
        else:
            exec(rp_settings['post'])
    
    # Log time
    # --------------------------------------------------------------------------
    times['finish'] = time.time()
    
    with open(times_file, 'w') as stream:
        json.dump(times, stream)
    
    
    # Quit blender
    # --------------------------------------------------------------------------
    log.info('Batch Finished.')
    bpy.ops.wm.quit_blender()
