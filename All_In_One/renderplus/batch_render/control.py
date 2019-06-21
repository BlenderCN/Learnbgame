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

import logging
import json
import os

import bpy


from .. import utils
from .. import data


# ------------------------------------------------------------------------------
#  INTERNAL VARIABLES
# ------------------------------------------------------------------------------

# Are we running a batch right now?
running = False

# List of errors in this batch
errors = {}

# The batch control process
proc = {}

# Logging
log = logging.getLogger(__name__)

# Times from last batch
times = None

# ------------------------------------------------------------------------------
#  CONVENIENCE FUNCTIONS
# ------------------------------------------------------------------------------

def index():
    """ Current index for the batch list """
    
    return bpy.context.scene.renderplus.batch.index

def current_job():
    """ Get currently selected job """        

    index = bpy.context.scene.renderplus.batch.index
    return bpy.context.scene.renderplus.batch.jobs[index]


def get_temp_path(suffix):
    """ Get a path to the batch temp directory """
    
    filename = bpy.path.basename(bpy.data.filepath) + suffix
    filepath = os.path.join(
                os.path.dirname(__file__),
                'tmp', filename)
    
    return filepath


def has_jobs():
    """ Determine if the batch list has any jobs """
    
    return len(bpy.context.scene.renderplus.batch.jobs) > 0


# ------------------------------------------------------------------------------
#  BATCH PROCESSING
# ------------------------------------------------------------------------------
    
def make_output_path(job):
    """ Generate output paths """    
    
    def add_suffix(suffix_type):
        """ Add sufixes according to job data """
            
        if suffix_type == 'NONE':
            return ''
        elif suffix_type == 'SCENE':
            return '_' + job.scene
        elif suffix_type == 'CAMERA':
            return '_' + job.camera
        elif suffix_type == 'RENDERLAYER':
            return '_' + job.layer
                
    settings = bpy.context.scene.renderplus.batch_ops.output_change
    directory = settings.base_directory
            
    if settings.subdirs_scene:
        directory = os.path.join(directory, job.scene)
                
    if settings.subdirs_layer:
        directory = os.path.join(directory, job.layer)
                    
    if settings.subdirs_cam:
        directory = os.path.join(directory, job.camera)
                
    filename = settings.base_filename
    filename += add_suffix(settings.name_suffix_01)
    filename += add_suffix(settings.name_suffix_02)
    filename += add_suffix(settings.name_suffix_03)
        
    return os.path.join(directory, filename)



def fix_output_paths(jobs):
    """ Check and fix output paths from jobs """
        
    def check_collision(path, index = 1):
        """ Check and fix filepath collisions """
            
        if path in checked:
            # "extension" in this case refers to ###
            filepath, extension = os.path.splitext(path)
            new_path = '{0}_{1:0>3}_{2}'.format(filepath, index, extension)
                
            # Iterate until it collides no more
            index += 1
            check_collision(new_path, index)   
        else:
            checked.append(path)
            
    # --------------------------------------------------------------------------
    checked = []
        
    for i, job in enumerate(jobs):
        
        if not job['enabled']:
            continue
            
        # External blends use their own output path
        # by default
        if job['external'] and not job['output']:
            continue
            
        output = job['output']
        test_path = output.replace('#', '')
        test_path = os.path.dirname(utils.sane_path(test_path))
            
        # Directory checks
        # ----------------------------------------------------------------------
        if not os.path.isdir(test_path):
            if not data.prefs.batch_new_dirs:
                raise FileNotFoundError((i, test_path))
                    
            try:
                os.makedirs(test_path)
            except OSError:
                raise FileNotFoundError((i, test_path))
                
        if not os.access(test_path, os.W_OK):
            raise PermissionError((i, test_path))
        
            
        # Check Collisions
        # ----------------------------------------------------------------------
        clean_path, extension = os.path.splitext(output)
        check_collision(clean_path)
        
    return checked


def batch_control_cmd(data_file):
    """ Create command for batch control """

    use_term = bpy.context.scene.renderplus.batch.use_term    
    params = []
    default_term = {}
    default_term['Linux'] = ['xterm', '-hold', '-e']
    default_term['Windows'] = ['start ""']
    default_term['Darwin'] = ['osascript', '-e', ('\'tell application "Terminal"'
                                                  'to do script "')]
    
    command = [
                bpy.app.binary_path, '-b', 
                '-P', utils.path('batch_render', 'dispatcher.py'), 
                '--', data_file,
              ]
    
    if use_term:
        # Custom Term
        if data.prefs.term_path:
            params = data.prefs.term_path + ' "' 
            params += ' '.join(command)
            params += '"'
            
        # Default term
        else:
            params = default_term[utils.sys] + command
    # No term
    else:
        params = command

    # Opening an app from the CLI in Mac involves calling a command,
    # that runs a script, that calls the terminal app and finally runs
    # the actual app
    if utils.sys == 'Darwin' and use_term:
        if data.prefs.term_path:
            params = data.prefs.term_path
        else:
            params = 'osascript -e \' tell application "Terminal" to do script "'

        params += ( '\\"' + bpy.app.binary_path + '\\" ' +  '-b -P '
                   + '\\"' + utils.path('batch_render', 'dispatcher.py') 
                   + '\\"' + ' -- ' + '\\"' + data_file + '\\"' + '"\'')


    if utils.sys == 'Windows' and use_term:
        if data.prefs.term_path:
            params = data.prefs.term_path
        else:
            params  = 'start "" '
            
        params += ' '.join(command)


    log.debug('Batch dispatcher called with: {0}'.format(params))    
    return params



def determine_shell():
    """ Determine if the dispather popen call needs shell """
    
    use_term = bpy.context.scene.renderplus.batch.use_term    

    if utils.sys == 'Darwin' and use_term:
        return True
    elif utils.sys == 'Windows':
        return True
    else:
        return (bpy.context.scene.renderplus.batch.use_term
                and data.prefs.term_path)    
    
    

def create_job_list(batch_list):
    """ Create list of jobs to encode """
    
    jobs = []
    current_scene = bpy.context.scene
    scenes = bpy.data.scenes
    settings = bpy.context.scene.renderplus.batch

    for index, job in enumerate(batch_list):
        job_data = {}

        job_data['enabled'] = job.enabled
        job_data['name'] = job.name
        job_data['ignore_border'] = settings.ignore_border

        # ----------------------------------------------------------------------
        # Scene to use when checking
        if not job.scene or job.scene == '':
            sce = current_scene.name
        else:
            sce = job.scene

        job_data['scene'] = sce


        # ----------------------------------------------------------------------
        # Write logs
        job_data['use_log'] = settings.write_logs


        # ----------------------------------------------------------------------
        # Use external for this job
        if job.use_external:
            if job.blend_file == '':
                errors[index] = 'Job is set to external but no file is set.'
                raise ValueError()
                
            job_data['blend_file'] = bpy.path.abspath(job.blend_file)
            job_data['external'] = True
        else:
            job_data['blend_file'] = bpy.data.filepath 
            job_data['external'] = False

        # ----------------------------------------------------------------------
        # Prepare output
        job_data['output'] = utils.sane_path(job.output)
            
        # ----------------------------------------------------------------------
        # Check camera
        if job.camera and not job.use_external:
            if (job.camera in scenes[sce].objects
                    and scenes[sce].objects[job.camera].type == 'CAMERA'):
                job_data['camera'] = job.camera
            else:
                job.camera = scenes[sce].camera.name
        else:
        	job_data['camera'] = job.camera
            

        # ----------------------------------------------------------------------
        # World
        job_data['world'] = job.world


        # ----------------------------------------------------------------------
        # Render layer
        job_data['layer'] = job.layer

        # ----------------------------------------------------------------------
        # Animation data
        if job.frame_custom:
            job_data['frame_still'] = job.frame_still
            job_data['frame_start'] = job.frame_start
            job_data['frame_end'] = job.frame_end
        else:
            job_data['frame_still'] = scenes[sce].frame_current
            job_data['frame_start'] = scenes[sce].frame_start
            job_data['frame_end'] = scenes[sce].frame_end

        job_data['animation'] = job.animation


        # ----------------------------------------------------------------------
        # Custom output settings
        if job.use_custom_format:
            job_data['format'] = job.format
        elif not job.use_external:
            job_data['format'] = scenes[sce].render.image_settings.file_format
        else:
            job_data['format'] = ''

        job_data['threads'] = job.threads
        job_data['cycles_samples'] = job.cycles_samples
        job_data['device'] = job.device


        # ----------------------------------------------------------------------
        # Custom Size
        if settings.use_global_size:
            job_data['size_x'] = settings.global_size_x
            job_data['size_y'] = settings.global_size_y
        elif job.size_custom:
            job_data['size_x'] = job.size_x
            job_data['size_y'] = job.size_y
        else:
            job_data['size_x'] = 0
            job_data['size_y'] = 0

        # ----------------------------------------------------------------------
        # Section Render
        if job.use_section:
            job_data['use_section'] = True
            job_data['section_x'] = job.section_x
            job_data['section_y'] = job.section_y
            job_data['section_width'] = job.section_width
            job_data['section_height'] = job.section_height
        

        # ----------------------------------------------------------------------
        # Custom Overrides
        if len(job.custom_overrides) > 0:
            job_data['custom_overrides'] = []

            for override in job.custom_overrides:
                if not override.enabled:
                    continue
                    
                data = {'path': override.path, 'data': override.data}
                job_data['custom_overrides'].append(data)

        # // Loop End
        jobs.append(job_data)
    
    return jobs
    


def clean():
    """ Clean up the batch_tmp folder """

    name = bpy.path.basename(bpy.data.filepath)
    batch_dir = utils.path('batch_render', 'tmp')
    batch_list = bpy.context.scene.renderplus.batch.jobs
    name_list = [name]

    for job in batch_list:
        if job.use_external:
            filename = bpy.path.basename(job.blend_file)
            name_list.append(filename)

    for f in os.listdir(batch_dir):
        for name in name_list:
            if name in f:
                try:
                    os.remove(os.path.join(batch_dir, f))
                    log.debug('Cleaning: ' + str(f))
                except PermissionError:
                    log.debug(
                        'Could not clean ' +
                        str(f) +
                        '. Will try again.')
                except FileNotFoundError:
                    continue
                else:
                    continue


def get_batch_errors():
    """ Get batch errors and reference them to jobs """
    
    from . import state

    name = bpy.path.basename(bpy.data.filepath)
    error_file = get_temp_path('.error')
    error_indexes = []
    i = 0

    # Build list of index of failed jobs
    for key, job in enumerate(state.jobs):
        if job == state.Code.FAILED:
            error_indexes.append(key)  # For UI

    with open(error_file, 'r') as stream:
        for line in stream:
            log.debug('Job #' + str(i) + ' failed. Error: ' + line)

            try:
                errors[error_indexes[i]] = line
            except:
                break
            else:
                i += 1


def get_times():
    """ Get times from last batch """
    
    global times
    
    name = bpy.path.basename(bpy.data.filepath)
    times_file = get_temp_path('_times.json')
    
    try:
        with open(times_file, 'r') as stream:
            times = json.load(stream)
            
    except (PermissionError, FileNotFoundError, OSError) as e:
        msg = 'Can\'t find times file: {0}. {1}'.format(times_file, e)
        log.error(msg)
