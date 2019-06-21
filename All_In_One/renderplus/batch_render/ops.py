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
import signal
import os
import json
import subprocess as sp

import bpy

from bpy.props import (IntProperty, 
                       StringProperty,
                       BoolProperty,
                       EnumProperty)


from .. import utils
from .. import data
from .. import ui

from . import control
from . import state


# ------------------------------------------------------------------------------
#  VARIABLES
# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
#  OPEN RENDER FOLDER
# ------------------------------------------------------------------------------

class RP_OT_OpenRenderFolder(bpy.types.Operator):

    """ Open output folder in file browser """

    bl_idname = 'renderplus.batch_open_render_folder'
    bl_label = 'Show output folder'

    @classmethod
    def poll(self, context):
        return control.has_jobs()

    def execute(self, context):
        
        command = {}
        command['Linux'] = 'xdg-open {0}'
        command['Windows'] = 'explorer {0}'
        command['Darwin'] = 'open {0}'
        
        output = control.current_job().output
        
        if not output:
            output =  context.scene.render.filepath
        
        output_folder = utils.sane_path(output)
        
        if not os.path.isdir(output_folder):
            output_folder = os.path.dirname(output_folder)
            
        open_cmd = command[utils.sys].format(output_folder)    
            
        try:
            print(sp.run(open_cmd, shell = True, check=True))
        except sp.CalledProcessError:
            self.report({'ERROR'}, ('Couldn\'t open render folder.'
                                    ' Please check output path'))

        return {'FINISHED'}

# ------------------------------------------------------------------------------
#  GET SECTION FROM VIEWPORT
# ------------------------------------------------------------------------------

class RP_OT_GetBorderRenderFromViewport(bpy.types.Operator):

    """ Get border render coordinates set in viewport """

    bl_idname = 'renderplus.batch_get_from_viewport'
    bl_label = 'Set section coordinates from viewport'

    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running

    def execute(self, context):
        job = control.current_job()
        settings = context.scene.render

        job.section_x = settings.border_min_x
        job.section_y = settings.border_min_y
        
        job.section_width = settings.border_max_x - settings.border_min_x
        job.section_height = settings.border_max_y - settings.border_min_y

        return {'FINISHED'}


# ------------------------------------------------------------------------------
#  CHANGE OUTPUTS
# ------------------------------------------------------------------------------

class RP_OT_ChangeOutputs(bpy.types.Operator):
    """ Change output paths across all render jobs"""

    bl_idname = 'renderplus.batch_change_outputs'
    bl_label = 'Change outputs in render jobs'
    bl_options = {"UNDO"}


    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running
        
    def execute(self, context):
        
        batch_list = context.scene.renderplus.batch.jobs

        for job in batch_list:
            job.output = control.make_output_path(job)
            ui.mode = 'NORMAL'
        
        return {'FINISHED'}
        


# ------------------------------------------------------------------------------
#  TOGGLE SETTINGS
# ------------------------------------------------------------------------------
class RP_OT_ToggleBatchMode(bpy.types.Operator):

    """ Toggle settings in Batch panel """

    bl_idname = 'renderplus.batch_toggle_mode'
    bl_label = 'Toggle the Batch panel ui mode'
    
    mode = EnumProperty(
        items=(
            ('NORMAL', 'Normal', ""),
            ('SETTINGS', 'Settings', ""),
            ('LOG', 'Log', ""),
            ('OUTPUT_CHANGE', 'Output Changer', ""),
            ('QUICK_LARGE', 'Quick Batch Large', ""),
            ('QUICK_COLORS', 'Quick Batch Colors', ""),
            ('QUICK_MARKERS', 'Quick Batch Markers', ""),
            ('QUICK_CAMERAS', 'Quick Batch Markers', ""),
            ('QUICK_RLAYERS', 'Quick Batch Markers', ""),
        ),
        default = 'NORMAL'
    )

    @classmethod
    def poll(self, context):
        return not control.running

    def execute(self, context):
            
        if ui.mode != self.mode:
            ui.mode = self.mode
        else:
            ui.mode = 'NORMAL'
            
        # Init for color looks quick batch
        if self.mode == 'QUICK_COLORS':
            settings = context.scene.renderplus.batch_ops.quick_batch
            
            if settings.size_x == 1:
                settings.size_x = context.scene.render.resolution_x
                
            if settings.size_y == 1:
                settings.size_y = context.scene.render.resolution_y
                
                
        return {'FINISHED'}
        
        

# ------------------------------------------------------------------------------
#  CUSTOM OVERRIDES
# ------------------------------------------------------------------------------

class RP_OT_AddCustomOverride(bpy.types.Operator):

    """ Add a custom override for a render job """

    bl_idname = 'renderplus.batch_add_custom_override'
    bl_label = 'Add a Custom Override'

    @classmethod
    def poll(self, context):
        return control.has_jobs()

    def execute(self, context):
        customs = control.current_job().custom_overrides

        customs.add()

        return {'FINISHED'}


class RP_OT_RemoveCustomOverride(bpy.types.Operator):

    """ Remove a custom override from a render job """

    bl_idname = 'renderplus.batch_remove_custom_override'
    bl_label = 'Remove a Custom Override'

    @classmethod
    def poll(self, context):
        return control.has_jobs()

    def execute(self, context):
        customs = control.current_job().custom_overrides
        index = control.current_job().custom_overrides_index

        customs.remove(index)
        
        return {'FINISHED'}


class RP_OT_CloneOverride(bpy.types.Operator):

    """ Duplicate override on all render jobs """

    bl_idname = 'renderplus.batch_clone_override'
    bl_label = 'Clone custom override for all jobs'

    @classmethod
    def poll(self, context):
        return control.has_jobs()

    def execute(self, context):
        customs = control.current_job().custom_overrides
        index = control.current_job().custom_overrides_index
        batch_list = context.scene.renderplus.batch.jobs

        path = customs[index].path
        data = customs[index].data
        name = customs[index].name
        enabled = customs[index].enabled

        for job in batch_list:
            found = False

            # We don't have overrides
            if len(job.custom_overrides) == 0:
                job.custom_overrides.add()
                job.custom_overrides[0]['name'] = name
                job.custom_overrides[0]['enabled'] = enabled
                job.custom_overrides[0]['path'] = path
                job.custom_overrides[0]['data'] = data

                found = True
            else:
                # Loop through overrides to find the one
                for override in job.custom_overrides:
                    if 'path' in override:
                        if override['path'] != path:
                            continue
                        else:
                            override['data'] = data
                            found = True

                # We didn't find the key
                if not found:
                    new_index = len(job.custom_overrides)
                    job.custom_overrides.add()
                    job.custom_overrides[new_index]['name'] = name
                    job.custom_overrides[new_index]['enabled'] = enabled
                    job.custom_overrides[new_index]['path'] = path
                    job.custom_overrides[new_index]['data'] = data

        self.report({'INFO'}, 'Copied {0} to all render jobs'.format(name))
        return {'FINISHED'}


# ------------------------------------------------------------------------------
#  LIST MANIPULATION
# ------------------------------------------------------------------------------


class RP_OT_NewRenderJob(bpy.types.Operator):

    """ Add a new Render job to the batch list """

    bl_idname = "renderplus.new_render_job"
    bl_label = "Add a new Render job to the batch list"

    duplicate = BoolProperty(default=False)

    def execute(self, context):
        batch_list = context.scene.renderplus.batch.jobs
        index = context.scene.renderplus.batch.index
        new_index = len(batch_list)
        scene = context.scene
        
        batch_list.add()
        batch_list[new_index].name = data.check_job_name(scene.name)
        
        if self.duplicate:
            dupe = batch_list[new_index]
            original = control.current_job()

            for key, value in original.items():
                dupe[key] = value
            
            dupe['name'] = data.check_job_name(original['name'] + '_duplicate')
        else:
            # Move index to the new job
            context.scene.renderplus.batch.index = new_index
            
            # Use scene updater to auto-populate settings
            batch_list[new_index].scene = context.scene.name
            batch_list[new_index].frame_start = scene.frame_start
            batch_list[new_index].frame_end = scene.frame_end
            
            try:
                output = '//{0}_{1}'.format(scene.name, scene.camera.name)
            except AttributeError:
                output = '//{0}'.format(scene.name)
                
            batch_list[new_index].output = output
            
        return{'FINISHED'}


class RP_OT_ToggleJobs(bpy.types.Operator):

    """ Disable/Enable render jobs """

    bl_idname = "renderplus.batch_toggle"
    bl_label = "Toggle Render jobs"
    bl_options = {"UNDO"}

    enable = BoolProperty(default=True)

    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running

    def execute(self, context):
        batch_list = context.scene.renderplus.batch.jobs

        for job in batch_list:
            job.enabled = self.enable

        return {'FINISHED'}


class RP_OT_DeleteRenderJob(bpy.types.Operator):

    """ Removes a Render job in the batch list """

    bl_idname = "renderplus.delete_render_job"
    bl_label = "Remove Render jobs"

    clear = BoolProperty(default=False)

    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running

    def execute(self, context):
        batch_list = context.scene.renderplus.batch.jobs
        index = control.index()

        if self.clear:
            batch_list.clear()
            return{'FINISHED'}

        if index >= 0:
            batch_list.remove(index)

            if index > 0:
                context.scene.renderplus.batch.index -= 1

            return{'FINISHED'}
        else:
            return{'CANCELLED'}

    def draw(self, context):
        layout = self.layout

        layout.label('Are you sure you want to remove ALL render jobs?',
                     icon='ERROR')

    def invoke(self, context, event):
        if self.clear:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            return self.execute(context)


class RP_ToggleJobType(bpy.types.Operator):

    """ Toggle job type between still and animation """

    bl_idname = "renderplus.toggle_render_job"
    bl_label = "Toggle render job type"

    index = IntProperty(min=0)

    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running

    def execute(self, context):
        batch_list = context.scene.renderplus.batch.jobs
        job = batch_list[self.index]

        job.animation = not job.animation

        return {'FINISHED'}


class RP_OT_MoveRenderJob(bpy.types.Operator):

    """ Move a Render job up or down in the batch list """

    bl_idname = "renderplus.move_render_job"
    bl_label = "Removes a Render job from the batch list"

    direction = EnumProperty(
        items=(
            ('UP', 'Up', ""),
            ('DOWN', 'Down', ""),
            ('TOP', 'Top', ""),
            ('BOTTOM', 'Bottom', ""),
        )
    )

    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running

    def move_index(self):
        """ Moves index of a render job while clamping it """

        list_length = len(bpy.context.scene.renderplus.batch.jobs) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = control.index() - 1
        elif self.direction == 'DOWN':
            new_index = control.index() + 1
        elif self.direction == 'TOP':
            new_index = 0
        elif self.direction == 'BOTTOM':
            new_index = list_length

        new_index = max(0, min(new_index, list_length))
        bpy.context.scene.renderplus.batch.index = new_index

    def execute(self, context):
        batch_list = context.scene.renderplus.batch.jobs

        if control.index() >= 0:
            if self.direction == 'DOWN':
                neighbor = control.index() + 1
                batch_list.move(control.index(), neighbor)
                self.move_index()

            elif self.direction == 'UP':
                neighbor = control.index() - 1
                batch_list.move(neighbor, control.index())
                self.move_index()

            elif self.direction == 'BOTTOM':
                neighbor = len(batch_list) - 1
                batch_list.move(control.index(), neighbor)
                self.move_index()

            elif self.direction == 'TOP':
                neighbor = 0
                batch_list.move(control.index(), neighbor)
                self.move_index()

            else:
                return{'CANCELLED'}

            return{'FINISHED'}
        else:
            return{'CANCELLED'}


# ------------------------------------------------------------------------------
#  START AND CANCEL
# ------------------------------------------------------------------------------


class RP_OT_cancelBatch(bpy.types.Operator):

    """ Cancel a running batch """

    bl_idname = 'renderplus.cancel_batch'
    bl_label = 'Cancel Batch Rendering'

    @classmethod
    def poll(self, context):
        return control.running

    def execute(self, context):

        try:
            # Try to get PID of currently running job
            filename = control.get_temp_path('.pid')

            stream = open(filename, 'r')
            pid = stream.read()

        except FileNotFoundError:
            log.error('Couldn\'t find process to cancel yet')
            return {'CANCELLED'}

        # Notify that batch is off
        control.running = False

        # Kill main batch process
        if utils.sys == 'Windows':
            try:
                sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=batch.proc.pid))
            except AttributeError:
                log.error('Tried to cancel batch, but proc is a dict.')
                pass
        else:
            control.proc.terminate()

        # Kill any remaining process
        if utils.sys == 'Windows':
            sp.Popen("TASKKILL /F /PID {pid} /T".format(pid=pid))
        else:
            os.killpg(int(pid), signal.SIGTERM)

        # Clean up and return
        control.clean()

        log.info('Batch Rendering was CANCELLED\n')
        self.report({'WARNING'}, 'Batch Render Cancelled')
        return {'FINISHED'}


class RP_OT_processBatch(bpy.types.Operator):

    """ Process render jobs list """

    bl_idname = "renderplus.process_render_batch"
    bl_label = "Start Batch Rendering"

    @classmethod
    def poll(self, context):
        return control.has_jobs() and not control.running

        
    def write_datafile(self, context):
        """ Generate JSON data file in temp folder, returns filepath """

        rp = context.scene.renderplus
        settings = rp.batch
        batch_list = settings.jobs
        data_filepath = control.get_temp_path('_data.json')

        info = {
            'name': bpy.path.basename(bpy.data.filepath),
            'version': 1.0,
            'use_rss': settings.use_rss,
            'rss_path': bpy.path.abspath(settings.rss_path),
            'use_percentage': settings.use_global_percentage,
            'percentage': settings.global_percentage,
            'use_rplus_settings' : settings.use_rplus_settings,
            'rplus_settings' : {
                             'poweroff'             : rp.off_options,
                             'notification_sound'   : rp.notifications_sound,
                             'notification_desktop' : rp.notifications_desktop,
                             'notification_email'   : rp.notifications_mail,
                               },
        }

        
        # ----------------------------------------------------------------------
        # Pre/Post Render actions
        if settings.use_rplus_settings:
            if rp.pre_enabled:
                info['rplus_settings']['pre_option'] = rp.pre_settings.option
                
                if rp.pre_settings.option == 'command':
                    info['rplus_settings']['pre'] = rp.pre_settings.command
                else:
                    script = bpy.data.texts[rp.pre_settings.script].as_string()
                    info['rplus_settings']['pre'] = script
                    
            if rp.post_enabled:
                info['rplus_settings']['post_option'] = rp.post_settings.option
                
                if rp.post_settings.option == 'command':
                    info['rplus_settings']['post'] = rp.post_settings.command
                else:
                    script = bpy.data.texts[rp.post_settings.script].as_string()
                    info['rplus_settings']['post'] = script
                    


        try:
            jobs = control.create_job_list(batch_list)
        except ValueError:
            return False

        # ----------------------------------------------------------------------
        # Check outputs
        
        try:
            sane_output = control.fix_output_paths(jobs)
        
        except PermissionError as e:
            args = e.args[0]
            control.errors[args[0]] = ('Not enough permissions to write ' 
                                 'in folder: {0} '.format(args[1]))
            return False
        
        except FileNotFoundError as e:
            args = e.args[0]
            control.errors[args[0]] = ('Directory "{0}" doesn\'t exist ' 
                               'or could not be created.'.format(args[1]))
            return False
            
        
        for i, path in enumerate(sane_output):
            jobs[i]['output'] = path
            

        # ----------------------------------------------------------------------
        # Write Datafile
        for i in range(2):
            try:
                stream = open(data_filepath, 'w')
                json.dump({'jobs': jobs, 'info': info}, stream, indent=4)
                stream.close()

                break

            # ------------------------------------------------------------------
            # Permission denied or something even worse
            except PermissionError:

                text = ('Can\'t write batch data file. Check permissions '
                        'in ' + utils.path('batch_render', 'tmp') +
                        '. Make sure your user has permissions to write'
                        ' in that folder.')

                utils.show_message(text)
                log.error(text)

                return False

            # ------------------------------------------------------------------
            # Batch_tmp isn't there
            except FileNotFoundError:

                # Let's try to create it
                try:
                    log.warn('Can\'t find batch temporary directory.'
                             ' Attempting to create it.')
                    path = utils.path('batch_render', 'tmp')
                    os.makedirs(path, exist_ok=True)

                    continue

                # Can't create batch temp folder. We're all doomed.
                except OSError:
                    text = ('Can\'t create batch temporary folder. '
                            'Please check permissions in '
                            + os.path.dirname(__file__) +
                            '. Make sure your user can write to this folder')

                    utils.show_message(text)
                    log.error(text)

                    return False

        return data_filepath

    def execute(self, context):

        # ----------------------------------------------------------------------
        # Check that the file has been saved

        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'Please save before starting a batch')
            log.info('Please save this file before starting a batch\n')

            return {'CANCELLED'}

        elif bpy.data.is_dirty:
            bpy.ops.wm.save_mainfile()
            log.info('Autosaved blend file before starting batch.')

        # ----------------------------------------------------------------------
        # Write data and start

        control.errors.clear()

        data_file = self.write_datafile(context)

        if not data_file:
            return {'CANCELLED'}

        command = control.batch_control_cmd(data_file)

        try:
            control.proc = sp.Popen(command, shell = control.determine_shell())
        except OSError as e:
            log.error('Couldn\'t find Blender executable. ' + repr(e))
        except ValueError as e:
            log.error('Bad parameters ' + repr(e))

        control.running = True

        # ----------------------------------------------------------------------
        # State


        try:
            batch_list = context.scene.renderplus.batch.jobs
            state_file = control.get_temp_path('_state.json')
            state.create_file(state_file, batch_list)
            
        except (FileNotFoundError, PermissionError) as e:
            log.error('Couldn\'t create state file!')
            return {'CANCELLED'}


        # ----------------------------------------------------------------------
        # Start watching file and report

        state.watch_file()

        print('\n')
        print('-' * 80)
        log.info('Batch Rendering has started\n')
        self.report({'INFO'}, 'Batch Render Started')

        return {'FINISHED'}
