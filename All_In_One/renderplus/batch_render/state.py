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

import threading
import logging
import json

from enum import IntEnum, unique

import bpy

from .. import data
from .. import utils
from .. import notifications

from . import control


# ------------------------------------------------------------------------------
#  VARIABLES
# ------------------------------------------------------------------------------

state_file = None
jobs = []

log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#  STATE CODES
# ------------------------------------------------------------------------------

@unique
class Code(IntEnum):
    """ Codes for possible states in a render job """

    DISABLED = -1
    WAITING  = 0
    RUNNING  = 1
    FINISHED = 2
    FAILED   = 3



# ------------------------------------------------------------------------------
#  STATE MANAGEMENT
# ------------------------------------------------------------------------------

def create_file(filepath, job_list):
    """ Create a new empty state file """
    
    global state_file
    state_file = filepath
    
    # Write initial state
    for job in job_list:
        if job.enabled:
            jobs.append(Code.WAITING)
        else:
            jobs.append(Code.DISABLED)

    with open(filepath, 'w') as stream:
        json.dump(jobs, stream)
    
    
def update(index, status):
    """ Update the state file """
        
    jobs[index] = status 
    
    try:
        with open(state_file, 'w') as stream:
            json.dump(jobs, stream)
            
    except (PermissionError, FileNotFoundError, OSError) as e:
        msg = 'Can\'t write state file: {0}. {1}'.format(state_file, e)
        log.error(msg)
        


def from_file(filepath):
    """ Build up state from a state file """ 

    global state_file, jobs
    state_file = filepath
    
    with open(filepath, 'r') as stream:
        jobs = json.load(stream)


def reset():
    """ Reset the module's variables """

    global state_file
    state_file = None
    
    jobs.clear()    
    
    
# ------------------------------------------------------------------------------
# POLLING
# ------------------------------------------------------------------------------
    
def watch_file():    
    """ Watch the state file for changes """
    
    global jobs
    
    # Try to read the state file
    # --------------------------------------------------------------------------
    try:
        with open(state_file, 'r') as stream:
            jobs = json.load(stream)
            
    except (OSError, FileNotFoundError):
        log.info(('Can\'t find a state file to update the Batch UI.\n(Ignore'
                  ' this if you cancelled the batch or opened another file)'))
        return False

    # Has it finished? 
    # --------------------------------------------------------------------------
    if Code.WAITING not in jobs and Code.RUNNING not in jobs:
        control.running = False
        log.info('Cleaning up temp files and resetting the Batch UI.')
    
        if Code.FAILED in jobs:
            try:
                control.get_batch_errors()
            except FileNotFoundError:
                log.debug('State found but not error file?')
        
        
        # This should happen in Dispatcher, but Blender can't play
        # sounds from the CLI so this will have to do...
        if bpy.context.scene.renderplus.batch.use_rplus_settings:
            if bpy.context.scene.renderplus.notifications_sound:
                notifications.sound()
        
        control.get_times()
        control.clean()
        reset()
        
    # if not, keep watching 
    # --------------------------------------------------------------------------
    else:
        try:
            interval = data.prefs['batch_refresh_interval']
        except KeyError:
            interval = 1.0

        timer = threading.Timer(interval, watch_file)
        timer.daemon = True
        timer.start()
    
    
    utils.force_redraw()
