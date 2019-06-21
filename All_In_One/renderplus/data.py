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

import os
import platform

import bpy
from bpy.props import (IntProperty, 
                       StringProperty,
                       BoolProperty,
                       EnumProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       CollectionProperty,
                       PointerProperty)

from . import utils


# ------------------------------------------------------------------------------
#  CONVENIENCE STUFF
# ------------------------------------------------------------------------------

# Addon preferences
try:
    prefs = bpy.context.user_preferences.addons[__package__].preferences
except KeyError:
    prefs = None


# ------------------------------------------------------------------------------
#  ADDON PREFERENCES
# ------------------------------------------------------------------------------


def default_path_debug():
    """ Create a useful default for support log """
    
    return os.path.expanduser('~' +  os.sep + 'renderplus_support.log')

    
def make_path_sane(key):
    """ Prevent Blender's relative paths of doom """

    if prefs[key] and prefs[key].startswith('//'):
        prefs[key] = utils.sane_path(prefs[key])
    elif key == 'debug_file' and prefs.debug_file == '':       
        prefs['debug_file'] = default_path_debug()


class RP_MT_MailQuickSetup(bpy.types.Menu):
    bl_idname = 'wm.rp_mt_mail_quick_setup'
    bl_label = 'Quick Setup'

    def draw(self, context):
        layout = self.layout

        layout.operator(
            'renderplus.mail_quick_setup',
            text='Gmail').provider = 'GMAIL'
        layout.operator(
            'renderplus.mail_quick_setup',
            text='Yahoo').provider = 'YAHOO'
        layout.operator(
            'renderplus.mail_quick_setup',
            text='MSN/Hotmail/Live').provider = 'LIVE'


class RP_Preferences(bpy.types.AddonPreferences):

    """ Addon preferences for Render+ """

    bl_idname = __package__
    
    # --------------------------------------------------------------------------
    # NOTIFICATIONS TAB

    sound_file = StringProperty(
        name='Custom Sound for notifications',
        description='Use notifications sound',
        subtype='FILE_PATH',
        update=lambda a,b: make_path_sane('sound_file'),
        default=utils.path('assets', 'notification.ogg')
    )

    sound_volume = FloatProperty(
        name='Sound Volume',
        description='Set the volume for sound notifications',
        default=90.0,
        min=0,
        max=100.0
    )

    mail_user = StringProperty(
        name='Username',
        description='User to login into the mail server',
        default=''
    )

    mail_password = StringProperty(
        name='Password',
        description='Password to login into the mail server',
        subtype='PASSWORD',
        default=''
    )

    mail_ssl = BoolProperty(
        name='Use SSL',
        description='Connect to mail server using Secure Sockets',
        default=False,
    )

    mail_server = StringProperty(
        name='Mail server (SMTP)',
        description='Server to send use when sending mails',
        default=''
    )

    mail_to = StringProperty(
        name='Send to',
        description='Address to send mail to',
    )

    # --------------------------------------------------------------------------
    # BATCH TAB

    show_batch = BoolProperty(
        name='Show Batch render panel',
        description='Show Batch rendering panel in render properties',
        default=True,
    )

    batch_refresh_interval = FloatProperty(
        name='Refresh interval for batch panel',
        description=('Time between refreshes in the UI panel while a batch is'
                     'running (in seconds).'),
        default=1.0,
        min=0.2,
        max=60.0
    )
    
    batch_new_dirs = BoolProperty(
        name = 'Automatically create directories when rendering',
        description = ('Try to create directories set in output paths' 
                       ' if they don\'t exist when rendering.'),
        default = True,
    )
    
    batch_use_custom_css  = BoolProperty(
        name = 'Use a custom CSS file for RSS feeds',
        description = 'Use a custom stylesheet for RSS feeds',
        default = False,
    )
    
    batch_custom_css = StringProperty(
        name = 'Custom CSS file',
        description = 'Custom CSS file to use for RSS Feeds',
        default = '',
        update=lambda a,b: make_path_sane('batch_custom_css'),
        subtype = 'FILE_PATH',
    )

    batch_cuda_devices = IntProperty( 
        name='Amount of Cuda devices in system',
        min=-1,
        max=64,
        default=-1,
        )

    batch_cuda_active = StringProperty( 
        name='Cuda device set in preferences',
        default='',
        )
        
    blender_path = StringProperty(
        name='Custom Blender Command',
        description=('Blender to use for batches. Type a'
                     'command or point this to the Blender executable.'),
        update=lambda a,b: make_path_sane('blender_path'),
        subtype='FILE_PATH'
    )

    term_path = StringProperty(
        name='Custom Terminal Command',
        description=('Terminal to use for batches. Type a'
                     'command or point this to a terminal executable.'),
        update=lambda a,b: make_path_sane('term_path'),
        subtype='FILE_PATH'
    )

    # --------------------------------------------------------------------------
    # HELP TAB


    enable_debug = BoolProperty(
        name='Generate support log',
        description=('Enable debugging output. This is used to get information'
                     'when reporting a bug, or requesting support.'),
        default = False,
    )

    debug_file = StringProperty(
        name='Support log file',
        description='Where to save the support log output',
        update=lambda a,b: make_path_sane('debug_file'),
        subtype='FILE_PATH',
        default=default_path_debug(),
    )

    ui_tab = EnumProperty(
        name='Tab',
        description='Tab in the preferences editor',
        items=(('NOTIFICATIONS', 'Notifications', ''),
               ('BATCH', 'Batch', ''),
               ('HELP', 'Help', ''),
               ),
        default='NOTIFICATIONS')



    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, 'ui_tab', expand=True)

        if self.ui_tab == 'NOTIFICATIONS':
            layout.separator()
            layout.prop(self, 'sound_file', icon='PLAY_AUDIO')
            row = layout.row()
            row.label(text='Sound Volume')
            row.prop(self, 'sound_volume', text='', slider=True)
            layout.separator()
            layout.separator()

            split = layout.split(0.75)
            split.label(text='Email Setup', icon='SCRIPTWIN')
            split.menu('wm.rp_mt_mail_quick_setup')

            split = layout.split(1.0)
            col = split.column()
            col.prop(self, 'mail_to')
            col.separator()
            col.prop(self, 'mail_user')
            col.prop(self, 'mail_password')

            col.prop(self, 'mail_server')
            col.prop(self, 'mail_ssl')

        elif self.ui_tab == 'BATCH':
            layout.separator()
            layout.prop(self, 'show_batch')
            
            row = layout.row()
            row.enabled = self.show_batch
            row.prop(self, 'batch_refresh_interval')
            layout.separator()
            
            row = layout.row()
            row.prop(self, 'batch_new_dirs')
            
            split = layout.split(0.4)
            
            col = split.column()
            col.prop(self, 'batch_use_custom_css')
            
            col = split.column()
            col.enabled = self.batch_use_custom_css
            col.prop(self, 'batch_custom_css', text='')

            
            layout.separator()
            layout.prop(self, 'blender_path', icon='BLENDER')
            layout.prop(self, 'term_path', icon='CONSOLE')
            layout.label(text=('Fill this if you want to use a different'
                               ' Blender or Terminal for batches.'
                               ' Leave emtpy to use defaults.'), icon='INFO')
            layout.separator()
            
        elif self.ui_tab == 'HELP':
            layout.prop(self, 'enable_debug')

            layout.separator()

            if self.enable_debug:
                privacy = (
                    'The debug file will contain the following information '
                    'about your system: Operating system, Blender version and branch.')

                layout.prop(self, 'debug_file')
                layout.label(privacy, icon='INFO')

        layout.separator()


# ------------------------------------------------------------------------------
#  BATCH OPERATOR SETTINGS
# ------------------------------------------------------------------------------

# These are settings used by operators. They are set as props here 
# so they can be shown in panels, instead of popups.

suffix_options =(
                  ('NONE', 'None', ''),
                  ('SCENE', 'Scene', ''),
                  ('RENDERLAYER', 'Render Layer', ''),
                  ('CAMERA', 'Camera', ''),
                ) 

class RP_Batch_Ops_OutputChange(bpy.types.PropertyGroup):

    """ Data for Output Change """
    
    # Output 
    # --------------------------------------------------------------------------
    base_directory = StringProperty(
                    name='Base directory',
                    default='', 
                    subtype='FILE_PATH'
                    )
    
    base_filename = StringProperty(
                    name='Base filename',
                    default='', 
                    )

    
    # Suffixes for filenames
    # --------------------------------------------------------------------------
    name_suffix_01 = EnumProperty(
                    items= suffix_options,
                    name='First Suffix',
    )

    name_suffix_02 = EnumProperty(
                    items= suffix_options,
                    name='Second Suffix',
    )

    name_suffix_03 = EnumProperty(
                    items= suffix_options,
                    name='Third Suffix',
    )


    # Subdirectories
    # --------------------------------------------------------------------------
    subdirs_scene = BoolProperty(
                    name='Scenes',
                    description='Make subir for each scene',
                    default=False,
    )

    subdirs_cam = BoolProperty(
                    name='Cameras',
                    description='Make subir for each camera',
                    default=False,
    )
    
    subdirs_layer = BoolProperty(
                    name='Render Layers',
                    description='Make subir for each renderlayer',
                    default=False,
    )


class RP_Batch_Ops_QuickBatch(bpy.types.PropertyGroup):

    """ Data for Quick Batch """
    
    tiles_x = IntProperty( 
                    name='Horizontal Tiles',
                    min=1,
                    max=10,
                    default=2,
                    )

    tiles_y = IntProperty( 
                    name='Vertical Tiles',
                    min=1,
                    max=10,
                    default=2,
                    )

    output_path = StringProperty(
                    name='Output path',
                    default='', 
                    subtype='FILE_PATH'
                    )
                    
    size_x = IntProperty( 
                    name='Width',
                    min=1,
                    max=10000,
                    default=1,
                    subtype='PIXEL',
                    )
                    
    size_y = IntProperty( 
                    name='Height',
                    min=1,
                    max=100000,
                    default=1,
                    subtype='PIXEL',
                    )
    
    scene = StringProperty(default="", name="Scene")
    
    all_scenes = BoolProperty(default=False, name="Use all scenes")
    
    use_animation = BoolProperty( 
                    name='Animation',
                    default=True, 
                    description='Make animation render jobs',
                    )
    
    no_camera = BoolProperty( 
                    name='Don\'t use cameras',
                    default=False, 
                    description='Don\'t setup cameras for render jobs',
                    )
    
    
    
class RP_Batch_Ops(bpy.types.PropertyGroup):
    """ Settings for operators """
    
    output_change = PointerProperty(type=RP_Batch_Ops_OutputChange)
    quick_batch =  PointerProperty(type=RP_Batch_Ops_QuickBatch)
    
    
# ------------------------------------------------------------------------------
#  RENDER JOB
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS


def check_job_name(name):
    """ Make sure the job name is unique """

    def check_duplicate(i, name_to_check):
        """ check new names recursively """
        
        if name_to_check not in seen:
            return name_to_check
        else:
            i += 1
            correct_name =  '{0}.{1:0>3}'.format(name, i) 
            return check_duplicate(i, correct_name)

    # --------------------------------------------------------------------------        
    batch = bpy.context.scene.renderplus.batch.jobs
    seen = set()
    i = 0
        
    for job in batch:
        if job.name not in seen:
            seen.add(job.name)
            
    return  check_duplicate(i, name)


def set_job_name(self, value):
    """ Wrapper to call check_job_name """

    if 'name' in self and self['name'] == value:
        return

    self['name'] = check_job_name(value)


def get_job_name(self):
    """ Get the job's name """

    # Sometimes draw() calls this, before it's defined
    if 'name' in self:
        return self['name']
    else:
        return 'Untitled Render Job'


def default_job_name():
    """ Return the default name for a job """

    return check_job_name('New Render Job')


def fill_job_from_scene(self, context):
    """ Populate all fields for render job from scene data """
    
    batch_list = bpy.context.scene.renderplus.batch.jobs
    index = bpy.context.scene.renderplus.batch.index
    
    if batch_list[index].use_external:
        return
    
    try:
        scene = bpy.data.scenes[batch_list[index].scene]
    except KeyError:
        return
        
    try:
        batch_list[index].camera = scene.camera.name
    except AttributeError:
        pass
            
    try:
        batch_list[index].world = scene.world.name
    except AttributeError:
        pass
        
    batch_list[index].layer = scene.render.layers[0].name
    
    
def set_external(self, context):
    
    batch_list = bpy.context.scene.renderplus.batch.jobs
    index = bpy.context.scene.renderplus.batch.index
    
    if batch_list[index].use_external:
        batch_list[index].scene = ''
        batch_list[index].camera = ''
        batch_list[index].world = ''
        batch_list[index].layer = ''
    else:
        batch_list[index].scene = context.scene.name
        
    

def is_batch_format_optional(format):
    """ Check if a file format is optional """

    optional = (
        'HDR',
        'TIFF',
        'EXR',
        'MULTILAYER',
        'MPEG',
        'AVICODEC',
        'QUICKTIME',
        'CINEON',
        'DPX',
        'DDS')

    return (format in optional)



def generate_GPU_enum(self, context):
    """ Generate list of computing devices for ui """
    
    items = [
                ('DEFAULT', 'Default', 'Don\'t change computing device'),
                ('CPU', 'CPU', 'Render using the CPU')
            ]
    
    for i in range(prefs.batch_cuda_devices):
        items.append(('CUDA_' + str(i), 
                      'GPU #' + str(i+1), 
                      'Use this GPU to render'))
    
    return items

# ------------------------------------------------------------------------------
# CLASSES


class RP_CustomOverride(bpy.types.PropertyGroup):

    """ Custom overrides for a render job """

    path = StringProperty(
        name='Datapath',
        description='Datapath to property',
        default='')

    data = StringProperty(
        name='Data',
        description='Data to use',
        default='')
        
    name = StringProperty(
        name='Name',
        description='Override Name',
        default='New Custom Override')
        
    enabled = BoolProperty(
        name='Enabled',
        description='Enable this override',
        default = True,)


class RP_RenderJob(bpy.types.PropertyGroup):

    """ Render job to put in queue """

    # --------------------------------------------------------------------------
    # BASIC PROPS

    name = StringProperty(
        name='Name',
        description='A name to identify this job in the queue',
        default='Untitled Render Job',
        set=set_job_name,
        get=get_job_name)

    scene = StringProperty(
        name='Scene',
        description='Scene to render',
        default='',
        update=fill_job_from_scene)

    camera = StringProperty(
        name='Camera',
        description='Camera to use in this render',
        default='')

    world = StringProperty(
        name='World',
        description='World to use in this render',
        default='')

    layer = StringProperty(
        name='Render Layer',
        description='Use only this render layer',
        default='')

    enabled = BoolProperty(
        name='Enable this render job',
        description='Process this render job',
        default=True)

    # --------------------------------------------------------------------------
    # EXTERNAL BLEND
    # --------------------------------------------------------------------------

    use_external = BoolProperty(
        name='Use external blendfile',
        description='Use a external blend file for this job',
        default=False,
        update=set_external)

    blend_file = StringProperty(
        name='Blend File',
        description='Path to external blendfile',
        subtype='FILE_PATH',
        default='')

    # --------------------------------------------------------------------------
    # FRAMES AND ANIMATION
    # --------------------------------------------------------------------------

    animation = BoolProperty(
        name='Animation',
        description='Render an animation instead of a still image',
        default=False)

    frame_custom = BoolProperty(
        name='Custom Frame',
        description='Use a custom frame or frame range for this render',
        default=False)

    frame_still = IntProperty(
        name='Frame',
        description='Frame to render',
        default=0)

    frame_start = IntProperty(
        name='Start Frame',
        description='First frame of the animation range',
        default=0)

    frame_end = IntProperty(
        name='End Frame',
        description='Final frame of the animation range',
        default=250)

    # --------------------------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------------------------

    output = StringProperty(
        name='Output',
        description='Filename to output to',
        subtype='FILE_PATH',
        default='')

    use_custom_format = BoolProperty(
        name='Custom File Format',
        description='Use a specific file format for this render job',
        default=False,
    )

    format = EnumProperty(
        name='Format',
        description='Format to use in the render job',
        items=(('TGA', 'Targa', ''),
               ('IRIS', 'Iris', ''),
               ('JPEG', 'Jpeg', ''),
               ('MOVIE', 'Movie', ''),
               ('RAWTGA', 'Raw Targa', ''),
               ('AVIRAW', 'Raw AVI', ''),
               ('AVIJPEG', 'Jpeg AVI', ''),
               ('PNG', 'PNG', ''),
               ('BMP', 'BMP', ''),
               ('HDR', 'Radiance HDR', ''),
               ('TIFF', 'TIFF', ''),
               ('EXR', 'OpenEXR', ''),
               ('MULTILAYER', 'OpenEXR Multilayer', ''),
               ('MPEG', 'MPEG', ''),
               ('QUICKTIME', 'Quicktime', ''),
               ('CINEON', 'Cineon', ''),
               ('DPX', 'DPX', ''),
               ('DDS', 'DDS', ''),
               ),
        default='PNG',
    )
    
    cycles_samples = IntProperty(
        name='Samples',
        description=('Samples to render. Set to 0 to use'
                    ' the value set in the scene'),
        default=0,
        min=0,
        max=10000)

    threads = IntProperty(
        name='Threads',
        description='Threads to use while rendering',
        default=0,
        min=0,
        max=64)

    # --------------------------------------------------------------------------
    # RENDER SIZE
    # --------------------------------------------------------------------------

    size_custom = BoolProperty(
        name='Custom Size',
        description='Use a custom render size for this job',
        default=False)

    size_x = IntProperty(
        name='Width',
        description='Custom render width for this job',
        default=1920,
        min=4)

    size_y = IntProperty(
        name='Height',
        description='Custom render height for this job',
        default=1080,
        min=4)


    use_section = BoolProperty(
        name='Render section',
        description = 'Render only a section of the image',
        default= False,)

    section_x = FloatProperty(
        name='X',
        description='Starting X coordinate for section render',
        default=0,
        min=0,
        max=0.99,)
    
    section_y = FloatProperty(
        name='Y',
        description='Starting Y coordinate for section render',
        default=0,
        min=0,
        max=0.99,)
    
    section_width = FloatProperty(
        name='Width',
        description='Width for section render',
        default=1,
        min=0.01,
        max=1,)
    
    section_height = FloatProperty(
        name='Height',
        description='Height for section render',
        default=1,
        min=0.01,
        max=1,)
    
    device = EnumProperty(
        name='Compute Device',
        description='Compute device to render with',
        items=generate_GPU_enum)

    # --------------------------------------------------------------------------
    # CUSTOM OVERIDES
    # --------------------------------------------------------------------------

    custom_overrides = CollectionProperty(type=RP_CustomOverride)
    
    custom_overrides_index = IntProperty(
        name='Index of current custom override',
        default=0)


# ------------------------------------------------------------------------------
#  RENDER SLOTS
# ------------------------------------------------------------------------------

class RP_RenderSlot(bpy.types.PropertyGroup):

    """ Customizable render slots """

    identifier = IntProperty(
        name='ID',
        description='Int to identify this slot',
        default=0,
        min=0,
        max=8
    )

    name = StringProperty(
        name='Name',
        description='A name to identify this slot',
        default='Slot',
    )

    is_used = BoolProperty(
        name='Slot is used',
        description='True if this slot has been used for render',
        default=False)


# ------------------------------------------------------------------------------
# STATS
# ------------------------------------------------------------------------------
class RP_StatsData(bpy.types.PropertyGroup):

    """ Stats data """

    average = FloatProperty(
        name='Average frame rendertime',
        description='Averaged rendertime for all frames',
        default=0)

    slowest = FloatVectorProperty(
        name='Slowest frame rendertime',
        description='Highest rendertime for all frames',
        size=2,
        default=(0, 0))

    fastest = FloatVectorProperty(
        name='Fastest frame rendertime',
        description='Smallest rendertime of all frames',
        size=2,
        default=(0, 0))

    remaining = FloatProperty(
        name='Time remaining to complete animation',
        description='Estimation of how long rendering will take',
        default=0)

    total = FloatProperty(
        name='Total rendertime',
        description='Time it took to render the last animation',
        default=-1)

    ui_toggle = BoolProperty(
        name='Show time stats',
        description='Show more stats about render time',
        default=False)

    save_file = BoolProperty(
        name='Save stats to a file',
        description='Save the stats to a CSV file',
        default=False)


# ------------------------------------------------------------------------------
# BATCH
# ------------------------------------------------------------------------------
class RP_BatchSettings(bpy.types.PropertyGroup):

    """ Batch Data """

    jobs = CollectionProperty(type=RP_RenderJob)

    index = IntProperty(
        name='Index of current render job in list',
        default=0)

    # Batch Renders Settings -----------------------------
    rss_path = StringProperty(
        name='RSS file',
        description='Filepath to write batch RSS file to',
        default='//feed.rss',
        subtype='FILE_PATH'
    )

    use_rss = BoolProperty(
        name='Write RSS file',
        description='Generate a RSS file to monitor batch process',
        default=False)

    write_logs = BoolProperty(
        name='Write log files',
        description='Write log files for each render job',
        default=False)

    use_global_size = BoolProperty(
        name='Global size',
        description='Override size for all render jobs',
        default=False)

    global_size_x = IntProperty(
        name='Width',
        description='Custom render width for all jobs',
        default=1920,
        min=4)

    global_size_y = IntProperty(
        name='Height',
        description='Custom render height for all jobs',
        default=1080,
        min=4)

    use_global_percentage = BoolProperty(
        name='Global Percentage',
        description='Override size percentage for all jobs',
        default=True)

    global_percentage = FloatProperty(
        name='Percentage',
        description='Custom size percentage for all jobs',
        subtype='PERCENTAGE',
        precision=0,
        min=1,
        max=100,
        default=100)

    ignore_border = BoolProperty(
        name='Ignore render border',
        description='Ignore render border for batch',
        default=False)
    
    use_term = BoolProperty( 
        name='Use terminal',
        description='Run the batch inside a terminal',
        default=False,)

    use_rplus_settings = BoolProperty( 
        name='Use Render+ Settings',
        description='Use notification, poweroff and post/pre actions in batch',
        default=False,)

    # Batch Renders UI 
    # --------------------------------------------------------------------------
    ui_job_tab = EnumProperty(
        name='Tab for render job overrides',
        description='Current tab for render job overrides',
        items=(('SCENE', 'Scene', 'Scene related overrides'),
               ('RENDER', 'Render', 'Rendering related overrides'),
               ('CUSTOM', 'Custom', 'Custom Overrides')),
        default='SCENE')


# ------------------------------------------------------------------------------
# ACTION
# ------------------------------------------------------------------------------

class RP_ActionSettings(bpy.types.PropertyGroup):

    """ Settings for pre/post actions  """

    option = EnumProperty(
        name='Option',
        description='Options to run this action',
        items=(('command', 'Command', 'Run a command'),
               ('script', 'Script', 'Run a Python script')),
        default='command')

    command = StringProperty(
        name='Command',
        description='Command to execute',
        default='')

    script = StringProperty(
        name='Script',
        description='Script to run',
        default='')


# ------------------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------------------


class RP_Settings(bpy.types.PropertyGroup):

    """ Settings and UI States for R+  """

    off_options = EnumProperty(
        name='Power Off',
        description='Power off when rendering is finished',
        items=(('DISABLED', 'Disabled', 'Let the computer on'),
               ('SLEEP', 'Sleep', 'Set computer to sleep'),
               ('OFF', 'Shut down', 'Turn off computer')),
        default='DISABLED')


    notifications_desktop = BoolProperty(
        name='Desktop Notifications',
        description='Notify me using the Desktop',
        default=False)

    notifications_sound = BoolProperty(
        name='Sound',
        description='Notify me using Sound',
        default=False)

    notifications_mail = BoolProperty(
        name='Email',
        description='Send an email to notify me',
        default=False)

    opengl_transparent = BoolProperty(
        name='Transparent',
        description='Make background transparent',
        default=False)
        
    opengl_use_viewport = BoolProperty(
        name='Render Viewport',
        description='Render the entire viewport (including invisible objects)',
        default=False)
        
    opengl_percentage = FloatProperty(
        name='Size Percentage',
        description='Custom size percentage OpenGL renders',
        subtype='PERCENTAGE',
        precision=0,
        min=1,
        max=100,
        default=100)
        
    autosave = BoolProperty(
        name='Autosave image renders',
        description=('Save image renders automatically to the folder in the'
                     'output panel'),
        default=False)

    stats = PointerProperty(type=RP_StatsData)

    batch = PointerProperty(type=RP_BatchSettings)
    
    batch_ops = PointerProperty(type=RP_Batch_Ops)

    # Render Slots 
    # --------------------------------------------------------------------------
    slots = CollectionProperty(type=RP_RenderSlot)

    active_slot = IntProperty(
        name='Index of active slot',
        default=0,
        min=0,
        max=8)

    # Post-render settings 
    # --------------------------------------------------------------------------
    post_enabled = BoolProperty(
        name='Post Render Toggle',
        description='Enable/Disable post render actions',
        default=False)

    post_settings = PointerProperty(type=RP_ActionSettings)

    # Pre-render settings 
    # --------------------------------------------------------------------------
    pre_enabled = BoolProperty(
        name='Pre Render Toggle',
        description='Enable/Disable Pre render actions',
        default=False)

    pre_settings = PointerProperty(type=RP_ActionSettings)
