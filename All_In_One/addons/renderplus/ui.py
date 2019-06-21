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
from datetime import datetime
 
import bpy

from enum import IntEnum, unique

from . import utils
from . import data
from . import stats
from . import notifications

import renderplus.batch_render.control as batch_control
import renderplus.batch_render.state   as batch_state



# ------------------------------------------------------------------------------
#  INTERNAL VARIABLES
# ------------------------------------------------------------------------------

# Logging
log = logging.getLogger(__name__)

mode = 'NORMAL'

show_opengl_settings = False

# ------------------------------------------------------------------------------
#  HELPERS
# ------------------------------------------------------------------------------

def mode_buttons(layout, op, text):
    """ Confirmation/Cancel buttons for Batch modes """

    row = layout.row()
    split = row.split(0.85, align=True)
    col = split.column(align=True)
    col.scale_y = 1.2
    op = col.operator(op,text=text)
    
    col = split.column(align=True)
    col.scale_y = 1.2
    col.operator('renderplus.batch_toggle_mode', text='', icon='CANCEL')
                         
    layout.separator()
    
    return op


def mode_title(layout, title, icon):
    """ Title layout for Batch modes """
    
    layout.separator()
    row = layout.row()
    box = row.box()
    box.label(text=title, icon=icon)
    layout.separator()


# ------------------------------------------------------------------------------
#  HELP
# ------------------------------------------------------------------------------

class RP_OT_ShowHelp(bpy.types.Operator):

    """ Call a popup with tips and help"""

    bl_idname = 'renderplus.help'
    bl_label = 'Render+ Help'

    section = bpy.props.EnumProperty(
        items=(
            ('ACTIONS', '', ""),
            ('CUSTOM_OVERRIDES', '', ""),
        )
    )

    def execute(self, context):
        if self.section == 'ACTIONS':
            message = ('Settings can be found in bpy.context.scene.renderplus.'
                       ' Actions will be disabled when opening a file for'
                       'security reasons. Use Absolute Paths and remember to'
                       ' be careful :)')

        elif self.section == 'CUSTOM_OVERRIDES':
            message = ('You can use this section to override any data'
                       'in the scene. Add the full datapath below (starting'
                       'from bpy.context.scene), and the value to it change'
                       'to.Note that Render+ does not check types or bounds'
                       'on custom values, it will simply use it. Double check'
                       'these values before rendering!')

        utils.show_message(message, wrap=70, pop_type='HELP')
        return {'FINISHED'}


# ------------------------------------------------------------------------------
#  SLOTS
# ------------------------------------------------------------------------------

class RP_MT_Slots(bpy.types.Menu):

    """ Render Slots menu """

    bl_label = ""
    bl_idname = "renderplus.menus.render_slots"

    def draw(self, context):
        layout = self.layout
        slots = context.scene.renderplus.slots
        i = 0

        for slot in slots:
            title = str(i + 1) + '. ' + slot.name

            if slot.is_used:
                icon = 'RESTRICT_RENDER_OFF'
            else:
                icon = 'RESTRICT_RENDER_ON'

            layout.operator('renderplus.change_slot',
                            text=title, icon=icon).index = i

            i += 1


# ------------------------------------------------------------------------------
#  BATCH
# ------------------------------------------------------------------------------

class RP_LT_Batch(bpy.types.UIList):

    """ Custom UI list for batch panel"""

    def draw_item(
            self,
            context,
            layout,
            data,
            item,
            icon,
            active_data,
            active_propname,
            index):

        global current

        if item.animation:
            job_icon = 'RENDER_ANIMATION'
        else:
            job_icon = 'RENDER_STILL'

        layout.operator('renderplus.toggle_render_job', emboss=False, text='',
                        icon=job_icon).index = index
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if index in batch_control.errors:
                icon = 'ERROR'
            else:
                icon = 'NONE'
                
            layout.prop(item, 'name', text='', emboss=False, icon = icon)

            if item.use_external:
                layout.label(text='', icon='FILE_BLEND')

            if not batch_control.running:
                layout.prop(item, "enabled", text="", index=index)
            else:
                state = batch_state.jobs[index]

                if state == batch_state.Code.WAITING:
                    layout.label(text='', icon='TIME')
                elif state == batch_state.Code.FINISHED:
                    layout.label(text='', icon='FILE_TICK')
                elif state == batch_state.Code.RUNNING:
                    layout.label(text='', icon='SCRIPT')
                elif state == batch_state.Code.FAILED:
                    layout.label(text='', icon='ERROR')
                elif state == batch_state.Code.DISABLED:
                    layout.label(text='', icon='ZOOMOUT')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon=job_icon)


class RP_LT_BatchLogs(bpy.types.UIList):

    """ UI list for logs """

    def draw_item(
            self,
            context,
            layout,
            data,
            item,
            icon,
            active_data,
            active_propname,
            index):

        if item.animation:
            job_icon = 'RENDER_ANIMATION'
        else:
            job_icon = 'RENDER_STILL'

        job = context.scene.renderplus.batch.jobs[index]
        layout.label(job.name, icon=job_icon)
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if index in batch_control.errors:
                icon = 'ERROR'
            else:
                icon = 'NONE'
            
        job_time = batch_control.times['jobs'][index]
        
        if job_time == -1:
            text = '(Disabled)'
            icon = 'ZOOMOUT'
        else:
            text = utils.time_format(job_time)
            icon = 'TIME'
        
        layout.label(text, icon=icon)    
        
                


class RP_LT_Batch_Custom_Overrides(bpy.types.UIList):

    """ Custom UI list for custom overrides"""

    def draw_item(
            self,
            context,
            layout,
            data,
            item,
            icon,
            active_data,
            active_propname,
            index):
        
            layout.prop(item, 'name', text='', emboss=False)
            layout.prop(item, 'enabled', text='', index=index)


class RP_MT_BatchOps(bpy.types.Menu):

    """ Menu for extra options in Batch Rendering"""

    bl_label = ""
    bl_idname = "renderplus.menus.batch_options"

    def draw(self, context):
        layout = self.layout

        layout.operator('renderplus.new_render_job',
                        icon='GHOST', text='Duplicate').duplicate = True
                        
        layout.separator()

        layout.operator('renderplus.move_render_job', icon='TRIA_UP_BAR',
                        text='Move to Top').direction = 'TOP'
        layout.operator('renderplus.move_render_job', icon='TRIA_DOWN_BAR',
                        text='Move to Bottom').direction = 'BOTTOM'
        layout.separator()

        layout.operator('renderplus.batch_toggle', icon='RESTRICT_VIEW_OFF',
                        text='Enable All').enable = True
        layout.operator('renderplus.batch_toggle', icon='RESTRICT_VIEW_ON',
                        text='Disable All').enable = False
        layout.separator()

        layout.operator('renderplus.delete_render_job', icon='ZOOMOUT',
                        text='Remove all render jobs').clear = True
                        
        layout.separator()
        layout.operator('renderplus.batch_toggle_mode', icon='NLA', 
                        text='Change output paths').mode = 'OUTPUT_CHANGE'

                        
                        

class RenderPlus_Batch_panel(bpy.types.Panel):

    """ Panel for batch rendering"""

    bl_label = 'Render+ Batch'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return data.prefs.show_batch

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.renderplus

        # Empty State
        # ----------------------------------------------------------------------
        if not batch_control.has_jobs() and mode == 'NORMAL':
            layout.separator()
            row = layout.row()
            row.enabled = False
            row.operator('renderplus.new_render_job', 
                         text='The batch list is empty', emboss=False)
            layout.separator()
            
            row = layout.row()
            row.scale_y = 1.2
            row.operator('renderplus.new_render_job',
                         text='Add a new render job').duplicate = False
                         
            row = layout.row()
            row.scale_y = 1.2
            row.menu('renderplus.menus.batch_quick', icon='PARTICLES',
                     text='Or use a Quick Batch')
            
            layout.separator()
            return
            
            
        # Quick batch: Large Renders
        # ----------------------------------------------------------------------
        if mode == 'QUICK_LARGE' and not batch_control.running:
            mode_title(layout, 'Large Render', 'IMGDISPLAY')
            
            settings = settings.batch_ops.quick_batch
            
            size_x = context.scene.render.resolution_x
            size_y = context.scene.render.resolution_y

            split = layout.split()
            col = split.column(align=True)
            col.prop(settings, 'tiles_x')
            col.prop(settings, 'tiles_y')
            
            col = split.column(align=True)
            col.label('Tile width: {0} px'.format(size_x//settings.tiles_x))
            col.label('Tile height: {0} px'.format(size_y//settings.tiles_y))
            
            row = layout.row(align=True)
            total = settings.tiles_x * settings.tiles_y
            row.label('{0} Render jobs will be created'.format(total), 
                      icon='RENDER_STILL')
            
            layout.separator()
            row = layout.row(align=True)
            row.prop(settings, 'output_path')
            
            layout.separator()
            mode_buttons(layout, 'renderplus.batch_quick_large_render', 
                         text='Create a large render')
                         
            return
            
            
        # Quick batch: Color Looks
        # ----------------------------------------------------------------------
        if mode == 'QUICK_COLORS' and not batch_control.running:
            mode_title(layout, 'Color Looks', 'COLOR')
            
            settings = settings.batch_ops.quick_batch
            
            split = layout.split()
            col = split.column(align=True)
            col.prop(settings, 'size_x')
            col.prop(settings, 'size_y')
            
            col = split.column(align=True)
            col.label('Output path', icon='FILESEL')
            col.prop(settings, 'output_path', text='')
            
            layout.separator()
            layout.separator()
            
            mode_buttons(layout, 'renderplus.batch_quick_looks', 
                        'Create color look jobs')
            return 
            
            
        # Quick batch: Markers
        # ----------------------------------------------------------------------
        quick_by_property = ('QUICK_MARKERS', 'QUICK_CAMERAS', 'QUICK_RLAYERS')
        
        if mode in quick_by_property and not batch_control.running:
            settings = settings.batch_ops.quick_batch
            
            if mode == 'QUICK_MARKERS':
                text = 'Markers'
                icon = 'MARKER_HLT'
                
            if mode == 'QUICK_CAMERAS':
                text = 'Cameras'
                icon = 'CAMERA_DATA'
                
            if mode == 'QUICK_RLAYERS':
                text = 'Render Layers'
                icon = 'RENDERLAYERS'
            
            mode_title(layout, text, icon)
            layout.separator()
            
            row = layout.row()
            row.prop_search(settings, "scene", bpy.data, "scenes")
            row.enabled = not settings.all_scenes

            row = layout.row()
            row.prop(settings, "all_scenes")

            layout.separator()
            
            if mode == 'QUICK_MARKERS':
                row = layout.row()
                row.prop(settings, 'use_animation')
                row = layout.row()
                row.prop(settings, 'no_camera', text='Don\'t set cameras')
                
                layout.separator()
                
                
            
            op = mode_buttons(layout, 'renderplus.batch_quick', 
                              'Create render jobs')
            
            op.prop_type = mode
                        
            return 
            
            
        # Output Change
        # ----------------------------------------------------------------------
        if mode == 'LOG' and not batch_control.running:
            
            mode_title(layout, 'Previous batch results', 'PREVIEW_RANGE')
            layout.separator()
            
            row = layout.row()
            row.template_list('RP_LT_BatchLogs', 'RP_Batch_list', settings.batch,
                              'jobs', settings.batch, 'index')
            
            batch_start = datetime.fromtimestamp(batch_control.times['start'])
            batch_start = batch_start.strftime('%H:%M:%S - %d/%m/%Y')    
            
            batch_end = datetime.fromtimestamp(batch_control.times['finish'])
            batch_end = batch_end.strftime('%H:%M:%S - %d/%m/%Y')    
    
            row = layout.row(align=True)
            row.label('Batch Started at {0}'.format(batch_start), icon='PLAY')
            
            row = layout.row(align=True)
            row.label('Batch Finished at {0}'.format(batch_end), icon='MATPLANE')
            
            layout.separator()
            row = layout.row(align=True)
            row.scale_y = 1.2
            row.operator('renderplus.batch_toggle_mode', 
                         text='Show batch list', icon='LOOP_BACK')
                         
            layout.separator()
            
            return
            
            
            
        # Output Change
        # ----------------------------------------------------------------------
        if mode == 'OUTPUT_CHANGE' and not batch_control.running:
            
            output_settings = settings.batch_ops.output_change
            
            mode_title(layout,'Change output paths', 'NLA')
            
            row = layout.row()
            row.label('Base directory', icon='FILE_FOLDER')
            row = layout.row()
            row.prop(output_settings, 'base_directory', text='')
            
            layout.separator()
            row = layout.row()
            row.label('Create subdirectories', icon='NEWFOLDER')
            row = layout.row(align=True)
            row.prop(output_settings, 'subdirs_scene', toggle=True)
            row.prop(output_settings, 'subdirs_cam', toggle=True)
            row.prop(output_settings, 'subdirs_layer', toggle=True)
            layout.separator()
            
            row = layout.row()
            row.label('File name', icon='FILE_BLANK')
            row = layout.row()
            row.prop(output_settings, 'base_filename', text='')
            row = layout.row(align=True)
            row.label('Suffixes')
            row.prop(output_settings, 'name_suffix_01', text='')
            row.prop(output_settings, 'name_suffix_02', text='')
            row.prop(output_settings, 'name_suffix_03', text='')
            
            layout.separator()
            layout.separator()
            row = layout.row()
            row.label('Sample (from first job):', icon='SYNTAX_OFF')
            
            job = bpy.context.scene.renderplus.batch.jobs[0]
            sample = batch_control.make_output_path(job)
            row = layout.row()
            row.label(sample)
            row.scale_y = 0.4
            
            layout.separator()
            layout.separator()
    
            mode_buttons(layout, 'renderplus.batch_change_outputs',
                         text='Change outputs')
            return
            
            
        # Batch Settings
        # ----------------------------------------------------------------------
        if mode == 'SETTINGS' and not batch_control.running:
            
            row = layout.row()
            box = row.box()
            box.label( text='Batch Settings', icon='SEQ_SEQUENCER')
            layout.separator()
            layout.separator()
            
            
            split = layout.split(0.5)
            col = split.column(align=False)
            
            col.prop(settings.batch, 'use_global_size')
            col.prop(settings.batch, 'use_global_percentage')
            col.prop(settings.batch, 'ignore_border')
            
            col.separator()
            
            col.prop(settings.batch, 'write_logs')
            col.prop(settings.batch, 'use_rss')
            
            col.separator()
            col.prop(settings.batch, 'use_term')
            col.prop(settings.batch, 'use_rplus_settings')
            
            col = split.column(align=True)
            row = col.row(align=True)
            row.enabled = settings.batch.use_global_size
            row.prop(settings.batch, 'global_size_x')
            row = col.row(align=True)
            row.enabled = settings.batch.use_global_size
            row.prop(settings.batch, 'global_size_y')
            
            row = col.row(align=True)
            row.enabled = settings.batch.use_global_percentage
            row.scale_y = 1.1
            row.prop(settings.batch, 'global_percentage', text='')
            
            # ¯\_(ツ)_/¯
            col.separator()
            col.separator()
            col.separator()
            col.separator()
            col.separator()
            col.separator()
            
            row = col.row(align=True)
            row.enabled = settings.batch.use_rss
            row.prop(settings.batch, 'rss_path', text='')
            
            layout.separator()
            layout.separator()
            row = layout.row()
            row.scale_y = 1.1
            row.operator('renderplus.batch_toggle_mode', 
                         text='Show batch list', icon='LOOP_BACK')
                         
        else:
            # ------------------------------------------------------------------
            # Regular panel
            
            row = layout.row()
            row.menu('renderplus.menus.batch_quick')
                
            layout.separator()
                
            row = layout.row()
            row.template_list('RP_LT_Batch', 'RP_Batch_list', settings.batch,
                              'jobs', settings.batch, 'index')

            col = row.column(align=True)
            col.operator('renderplus.new_render_job', icon='ZOOMIN',
                         text="").duplicate = False
            col.operator('renderplus.delete_render_job',
                         icon='ZOOMOUT', text="").clear = False

            if len(settings.batch.jobs) > 0:
                col.separator()
                col.separator()
                col.operator('renderplus.move_render_job', icon='TRIA_UP',
                             text="").direction = 'UP'
                col.operator('renderplus.move_render_job', icon='TRIA_DOWN',
                             text="").direction = 'DOWN'

            col.separator()
            col.separator()

            col.menu(
                'renderplus.menus.batch_options',
                icon='COLLAPSEMENU',
                text="")
                
            if batch_control.times:
                col.separator()
                col.separator()
                col.separator()
                col.operator('renderplus.batch_toggle_mode', 
                            icon='PREVIEW_RANGE', 
                            text='').mode = 'LOG'

            if settings.batch.index >= 0 and len(settings.batch.jobs) > 0:
                job = settings.batch.jobs[settings.batch.index]

                layout.separator()
                row = layout.row()
                row.prop(settings.batch, 'ui_job_tab', expand=True)
                layout.separator()

                # --------------------------------------------------------------
                # Scene Tab

                if settings.batch.ui_job_tab == 'SCENE':
                    row = layout.row()
                    row.prop(job, 'name')

                    if job.use_external:
                        row = layout.row()
                        row.prop(job, 'blend_file')

                    row = layout.row()
                    if job.use_external:
                        row.prop(job, 'scene')
                    else:
                        row.prop_search(job, "scene", bpy.data, "scenes")

                    if job.scene or job.use_external:
                        row = layout.row()

                        if job.use_external:
                            row.prop(job, 'camera')
                        else:
                            row.prop_search(job, "camera",
                                            bpy.data.scenes[job.scene], "objects",
                                            icon="CAMERA_DATA")
                                            
                        row = layout.row()
                        if job.use_external:
                            row.prop(job, 'world')
                        else:
                            row.prop_search(job, "world",
                                            bpy.data, "worlds",
                                            icon="WORLD")


                        row = layout.row()
                        if job.use_external:
                            row.prop(job, 'layer')
                        else:
                            row.prop_search(job, "layer",
                                            bpy.data.scenes[job.scene].render,
                                            "layers", icon="RENDERLAYERS")


                    layout.separator()

                    split = layout.split()
                    col = split.column()
                    col.prop(job, 'animation')

                    if job.animation:
                        frame_text = "Custom frame range"
                    else:
                        frame_text = "Custom frame"

                    col.prop(job, 'frame_custom', text=frame_text)
                    col.separator()
                    col.prop(job, 'use_external', 'Use external file')
                    
                    col = split.column()
                    col.enabled = job.frame_custom

                    if job.animation:
                        col.prop(job, 'frame_start')
                        col.prop(job, 'frame_end')
                    elif job.frame_custom:
                        col.prop(job, 'frame_still')

                # --------------------------------------------------------------
                # Render Tab

                elif settings.batch.ui_job_tab == 'RENDER':
                    
                    split = layout.split(0.25)
                    
                    col = split.column() 
                    col.label('Output:')
                    
                    col = split.column(align=True) 
                    col.prop(job, 'output', text='')
                    col.operator('renderplus.batch_open_render_folder')

                    layout.separator()
                    
                    split = layout.split(0.4)
                    col = split.column()
                    col.prop(job, 'use_custom_format')
                    col.prop(job, 'size_custom')
                    col.prop(job, 'use_section')
                    col.separator()
                    
                    
                    col = split.column(align=True)
                    if job.use_custom_format:
                        row = col.row()
                        row.prop(job, 'format', text='')
                        row.enabled = job.use_custom_format

                    if job.size_custom:
                        if not job.use_custom_format:
                            col.separator()
                            col.separator()
                            col.separator()
                        
                        col.separator()
                        col.prop(job, 'size_x')
                        col.prop(job, 'size_y')
                    
                    if settings.batch.use_global_size and job.size_custom:
                        col.label('Global size is enabled', icon='INFO')
                        
                    if job.use_section:
                        if not job.size_custom:
                            col.separator()
                            col.separator()
                            col.separator()
                            col.separator()
                            col.separator()
                            col.separator()
                            col.separator()
                            
                        col.separator()
                        row = col.row(align=True)
                        row.prop(job, 'section_x')
                        row.prop(job, 'section_width')
                        row = col.row(align=True)
                        row.prop(job, 'section_y')
                        row.prop(job, 'section_height')
                        row = col.row(align=True)
                        row.operator('renderplus.batch_get_from_viewport', 
                                     text='Get from viewport')
                        layout.separator()
                           
                    if (context.scene.render.engine == 'CYCLES' and 
                        data.prefs.batch_cuda_devices > -1):
                        layout.separator()
                        row = layout.row(align=True)
                        row.prop(job, 'device', text='Render device', 
                                 icon='DISK_DRIVE')    
                        
                    layout.separator()
                    row = layout.row(align=True)
                    row.prop(job, 'threads')
                    layout.separator()
                    
                    if context.scene.render.engine == 'CYCLES':
                        if context.scene.cycles.progressive == 'BRANCHED_PATH':
                            text = 'AA Samples'
                        else:
                            text = 'Samples'
                            
                        row.prop(job, 'cycles_samples', text=text)
                    
                    if job.threads == 0:
                        row = layout.row()
                        row.label('Threads will be set auto-detected', 
                                  icon='INFO')
                        
                        
                    if (context.scene.render.engine == 'CYCLES' 
                        and job.cycles_samples == 0):
                        row = layout.row()
                        row.label(('Samples value will be taken' 
                                  ' from Cycles settings'), 
                                  icon='INFO')
                                  
                    if (data.is_batch_format_optional(job.format) 
                        and job.use_custom_format):
                        row = layout.row()
                        row.label(
                            'This format may not be available on your system',
                            icon='INFO')


                # --------------------------------------------------------------
                # Custom Tab

                elif settings.batch.ui_job_tab == 'CUSTOM':
                    
                    # Initial State
                    if len(job.custom_overrides) == 0:
                        
                        row = layout.row()
                        row.scale_y = 1.2
                        row.operator('renderplus.batch_add_custom_override', 
                                     icon='ZOOMIN')
                                     
                        layout.separator()
                        row = layout.row(align=True)
                        col = row.column(align=True)
                        col.scale_y = 0.85
                        col.label(('You can use this section to override any'
                                    ' data in the scene'), icon='TRIA_RIGHT') 
                        col.label(('Use the data path without the "data.'
                                   'scenes" part'), icon='TRIA_RIGHT')
                        col.label(('Note that data values are not checked for ' 
                                   'errors'), icon='INFO')
                                   
                        layout.separator()
                        row = layout.row(align=True)
                        row.scale_y = 1.1
                        row.operator('wm.url_open', 
                                     icon='URL',
                                     text='Learn more about data paths',
                                    ).url=('https://www.blender.org/'      
                                           'api/blender_python_api'
                                            '_current/info_quickstart'
                                            '.html#accessing-'
                                            'attributes')
                        
                                     
                    else:
                        row = layout.row()
                        
                        row.template_list('RP_LT_Batch_Custom_Overrides',
                                          'RP_LT_Batch_Custom_Overrides', 
                                          job, 'custom_overrides', 
                                          job, 'custom_overrides_index')
                        
                        col = row.column(align=True)
                        col.operator('renderplus.batch_add_custom_override', 
                                     text='', icon='ZOOMIN')
                        col.operator('renderplus.batch_remove_custom_override',
                                     text='', icon='ZOOMOUT')
                        
                        col.separator()
                            
                        col.operator('renderplus.batch_clone_override',
                                     text='', icon='GHOST')
                        
                        col.separator()
                        col.operator('renderplus.help', text='', 
                                     icon='QUESTION',
                                     emboss=False).section = 'CUSTOM_OVERRIDES'
                        layout.separator()

                        custom = job.custom_overrides[job.custom_overrides_index]
                        sample = 'bpy.data.scenes[\'{0}\'].{1} = {2}'
                        
                        row = layout.row()
                        row.label('Datapath', icon='RNA')
                        row = layout.row()
                        row.prop(custom, 'path', text='')
                        
                        row = layout.row()
                        row.label('Custom Data', icon='EMPTY_DATA')
                        row = layout.row()
                        row.prop(custom, 'data', text='')
                        
                        if custom.path != '' or custom.data != '':
                            layout.separator()
                            row = layout.row()
                            row.label(sample.format(job.scene, 
                                                    custom.path, 
                                                    custom.data), 
                                       icon='WORDWRAP_ON')
                        
                layout.separator()
                layout.separator()

                # --------------------------------------------------------------
                # Errors

                if len(batch_control.errors) > 0:
                    box = layout.box()

                    for key, err in batch_control.errors.items():
                        error_text = 'Job #' + str(key + 1)
                        error_text += ' has failed. Error: "' + err[:-1] + '"'
                        box.label(text=error_text, icon='ERROR')
                        layout.separator()

                # --------------------------------------------------------------
                # Start / Cancel Button

                if not batch_control.running:
                    split = layout.split(0.9, align=True)
                    col = split.column(align=True)
                    
                    col.scale_y =1.1
                    col.operator('renderplus.process_render_batch',
                                 text='Start Batch')
                                 
                    col = split.column(align=True)
                    col.scale_y =1.1
                    col.operator('renderplus.batch_toggle_mode', text='', 
                                 icon='SCRIPTWIN').mode = 'SETTINGS'
                else:
                    row = layout.row()
                    row.scale_y = 1.1
                    row.operator('renderplus.cancel_batch', text='Cancel Batch')

        layout.separator()


# ------------------------------------------------------------------------------
#  NOTIFICATIONS
# ------------------------------------------------------------------------------

class RP_MT_Notifications(bpy.types.Menu):

    """ Menu with notification options """

    bl_label = ""
    bl_idname = "renderplus.menus.notification_options"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.renderplus

        if utils.sys != "Windows":
            layout.prop(settings, 'notifications_desktop')

        layout.prop(settings, 'notifications_sound')
        layout.prop(settings, 'notifications_mail')


# ------------------------------------------------------------------------------
#  MAIN PANEL
# ------------------------------------------------------------------------------

class RP_PT_Main(bpy.types.Panel):

    """ Main Panel for Render+"""

    bl_label = 'Render+ Settings'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def notification_text(self, settings):
        """ Generates text for notifications menu """
        text = ''

        if settings.notifications_desktop:
            text = 'Desktop'

        if settings.notifications_sound:
            if text != '':
                text += ' + '

            text += 'Sound'

        if settings.notifications_mail:
            if text != '':
                text += ' + '

            text += 'Mail'

        if text == '':
            text = 'Disabled'

        return text

    def slot_text(self, settings):
        """ Title for the slot menu """

        try:
            text = str(settings.active_slot + 1) + '. '
            text += settings.slots[settings.active_slot].name
        except IndexError:
            pass

        return text

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = context.scene.renderplus
        stats_data = context.scene.renderplus.stats
        is_anim = stats_data.remaining + stats_data.average

        # ----------------------------------------------------------------------
        # Preview Render

        row = layout.row()
        box = row.box()
        box.label('OpenGL Render', icon='MONKEY')
        
        row = box.row(align=True)
        split = row.split(0.95)
        col = split.column()
        row = col.row(align=True)
        opengl = row.operator('renderplus.opengl_render', text='Image',
                               icon='RENDER_STILL')
        opengl.animation = False

        opengl_anim = row.operator(
            "renderplus.opengl_render", text="Animation", icon="RENDER_ANIMATION")
        opengl_anim.animation = True
        
        col = split.column()
        icon = 'TRIA_DOWN' if show_opengl_settings else 'TRIA_LEFT'
        col.operator('renderplus.opengl_show_settings', 
                    emboss=False, icon=icon, text='')
        
        if show_opengl_settings:
            row = box.row(align=True)
            col = row.column(align=True)
            row = col.row(align=True)
            row.prop(settings, 'opengl_transparent', toggle=True, 
                     icon='IMAGE_RGB_ALPHA')
                     
            row.prop(settings, 'opengl_use_viewport', toggle=True, 
                     icon='VISIBLE_IPO_ON')
            
            col.prop(settings, 'opengl_percentage')

        layout.separator()
        layout.separator()

        # ----------------------------------------------------------------------
        # Render Slots

        split = layout.split(percentage=0.5)
        split.enabled = (stats_data.total > 0)
        col = split.column()
        col.label(text="Slots", icon='SCENE')
        col = split.column()
        row = col.row(align=True)
        row.menu(
            'renderplus.menus.render_slots',
            text=self.slot_text(settings))
        row.operator('renderplus.set_slot_name', text='', icon='BUTS')

        # ----------------------------------------------------------------------
        # Notifications

        row = layout.row()
        row.label(text="Notifications", icon='LAMP')
        row.menu('renderplus.menus.notification_options',
                 text=self.notification_text(settings))

        if notifications.error:
            row = layout.row()
            row.label(notifications.error, icon='ERROR')

        # ----------------------------------------------------------------------
        # Power Off

        row = layout.row()
        row.label(text="Power Off", icon='QUIT')
        row.prop(settings, "off_options", text="")

        # ---------------------------------------------------------------------
        # Autosave

        row = layout.row()
        row.prop(settings, "autosave")

        # ---------------------------------------------------------------------
        # Stats


        layout.separator()
        layout.separator()
        row = layout.row()
        row.label(text='Stats', icon='TIME')
        row = layout.row()

        if stats.run_once or (stats_data.total > 0):
            time_string = 'Last Render took '
            time_string += utils.time_format(stats_data.total)
        else:
            time_string = "Waiting for the first render"

        if is_anim:
            if stats_data.ui_toggle:
                icon_stats = 'TRIA_DOWN'
            else:
                icon_stats = 'TRIA_RIGHT'

            row.prop(stats_data, 'ui_toggle', icon=icon_stats,
                     text=time_string, emboss=False)
            row.label('  ')  # Pushes text to the left
        else:
            row.label(time_string)

        if stats_data.ui_toggle and is_anim:
            box = layout.box()
            split = box.split(align=True)

            timeString = 'Waiting...'
            col = split.column()

            if stats.is_running():
                time_string = 'Calculating...'
            elif (stats_data.average == 0.0):
                time_string = 'Waiting...'
            else:
                time_string = utils.time_format(stats_data.average)

            col.label('Average time', icon='DISK_DRIVE')
            col.label(time_string)

            col = split.column()

            if stats.is_running():
                time_string = utils.time_format(stats_data.remaining)
                left = str(scene.frame_end - scene.frame_current)
                time_string += str.format(' ({0} frames)', left)
            else:
                # Don't show any time when not rendering
                time_string = 'Not Rendering'

            col.label('Estimated remaining', icon='AUTO')
            col.label(time_string)

            split = box.split(align=True)
            col = split.column()

            if stats.is_running():
                time_string = 'Calculating...'
            elif (stats_data.fastest[1] == 0):
                time_string = 'Waiting...'
            else:
                time_string = utils.time_format(stats_data.fastest[1])
                time_string += ' (#'
                time_string += str(round(stats_data.fastest[0])) + ')'

            col.label('Fastest frame', icon='ZOOMIN')
            col.label(time_string)

            col = split.column()
            if stats.is_running():
                time_string = 'Calculating...'
            elif (stats_data.slowest[1] == 0):
                time_string = 'Waiting...'
            else:
                time_string = utils.time_format(stats_data.slowest[1])
                time_string += ' (#'
                time_string += str(round(stats_data.slowest[0])) + ')'

            col.label('Slowest frame', icon='ZOOMOUT')
            col.label(time_string)
            
        row = layout.row()
        row.prop(settings.stats, "save_file")

        # ----------------------------------------------------------------------
        # Actions

        layout.separator()
        layout.separator()

        box = layout.box()
        row = box.row()
        row.prop(settings, 'pre_enabled', 'Pre-render actions')

        pre = settings.pre_settings
        post = settings.post_settings

        if settings.pre_enabled:
            box.prop(pre, 'option')

            if pre.option == 'command':
                row = box.row()
                row.prop(pre, 'command', '')
            else:
                row = box.row()
                row.prop_search(pre, 'script', bpy.data, 'texts')

            row.operator('renderplus.help', text='', icon='QUESTION',
                         emboss=False).section = 'ACTIONS'

        layout.separator()

        box = layout.box()
        row = box.row()
        row.prop(settings, 'post_enabled', 'Post-render actions')

        if settings.post_enabled:
            box.prop(post, 'option')

            if post.option == 'command':
                row = box.row()
                row.prop(post, 'command', '')
            else:
                row = box.row()
                row.prop_search(post, 'script', bpy.data, 'texts')

            row.operator('renderplus.help', text='', icon='QUESTION',
                         emboss=False).section = 'ACTIONS'

        layout.separator()
        layout.separator()
