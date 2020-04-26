import bpy
from bpy.app.handlers import persistent
from .. core.util import getInstallPath, getAddonDir
from ..extensions_framework.util import find_config_value, write_config_value

from .. import export, bl_info
from .. core.util import PlatformInformation, getInstallPath
import os


def find_indigo():
    rp = getInstallPath()
    if rp != "": return getInstallPath()

    return find_config_value(getAddonDir(), 'defaults', 'install_path', '')

@persistent
def indigo_scene_load_render_settings(context):
    ''' Prevent using the Indigo install dir from blend files if it doesn't exist on the local machine,
    also reset the output path if it doesn't exist on the local machine
    '''
    for s in bpy.data.scenes:
        # If the Indigo path in the scene doesn't exist.
        if not os.path.exists(s.indigo_engine.install_path):
            # Find Indigo.
            indigo_path = find_indigo()

            # If Indigo was found.
            if indigo_path != '' and os.path.exists(indigo_path):
                export.indigo_log("Scene '%s' Indigo install path was adjusted for local machine" % s.name)
                s.indigo_engine.install_path = indigo_path
            else:
                export.indigo_log("Failed %s to find Indigo installation" % s.name)

        # Get the output path for frame 1. s.render.filepath will return the raw
        # output path, potentially including # characters. s.render.frame_path(1)
        # handles # characters correctly. Not handling them correctly will result
        # in false positives for the output path adjusting.
        output_dir = os.path.dirname(s.render.frame_path(1))

        if not os.path.exists(output_dir):
            export.indigo_log("Scene '%s' output path was adjusted for local machine" % s.name)
            s.render.filepath = bpy.app.tempdir

if hasattr(bpy.app, 'handlers') and hasattr(bpy.app.handlers, 'load_post'):
    bpy.app.handlers.load_post.append(indigo_scene_load_render_settings)

def set_render_mode(self, context):
    if self.render_mode == 'bidir':
        self.bidir = True
        self.metro = False
        self.foreground_alpha = False
        self.gpu = False
        self.shadow = False
    if self.render_mode == 'bidir_mlt':
        self.bidir = True
        self.metro = True
        self.foreground_alpha = False
        self.gpu = False
        self.shadow = False
    if self.render_mode == 'path_cpu':
        self.bidir = False
        self.metro = False
        self.foreground_alpha = False
        self.gpu = False
        self.shadow = False
    if self.render_mode == 'path_gpu':
        self.bidir = False
        self.metro = False
        self.foreground_alpha = False
        self.gpu = True
        self.shadow = False
    if self.render_mode == 'shadow':
        self.bidir = False
        self.metro = False
        self.foreground_alpha = False
        self.gpu = False
        self.shadow = True

def set_filter_preset(self, context):
    if self.filter_preset == 'default':
        self.splat_filter = 'fastbox'
        self.ds_filter = 'mitchell'
        self.ds_filter_blur = 1.0
        self.ds_filter_ring = 0.0
        self.ds_filter_radius = 1.65
    if self.filter_preset == 'crisp':
        self.splat_filter = 'fastbox'
        self.ds_filter = 'mitchell'
        self.ds_filter_blur = 1/3
        self.ds_filter_ring = 1/3
        self.ds_filter_radius = 2.0
    if self.filter_preset == 'strong':
        self.splat_filter = 'radial'
        self.ds_filter = 'sharp'

def set_export_console_output(self, context):
    export.PRINT_CONSOLE = self.console_output
    write_config_value(getAddonDir(), 'defaults', 'console_output', self.console_output)

class IndigoDevice(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        cls.id = bpy.props.IntProperty(name="ID")
        cls.platform = bpy.props.StringProperty(name="Platform")
        cls.device = bpy.props.StringProperty(name="Device")
        cls.vendor = bpy.props.StringProperty(name="Vendor")
        cls.use = bpy.props.BoolProperty(name="Use", default=False)

properties = [
    {
        'type': 'bool',
        'attr': 'use_output_path',
        'name': 'Use output directory for .igs files',
        'description': 'Use the directory specified under Output to write the scene files to. When disabled the .igs export path can be customised below',
        'default': True
    },
    {
        'type': 'string',
        'subtype': 'FILE_PATH',
        'attr': 'export_path',
        'name': 'Scene (.igs) export path',
        'description': 'Directory/name to save Indigo scene files. # characters define location and length of frame numbers',
        'default': bpy.app.tempdir
    },
    {
        'type': 'string',
        'subtype': 'DIR_PATH',
        'attr': 'install_path',
        'name': 'Path to Indigo installation',
        'description': 'Location of Indigo',
        'default': find_indigo()
    },
    {
        # Internal var use for regression testing
        'type': 'bool',
        'attr': 'wait_for_process',
        'default': False
    },
    {
        # Internal var use for regression testing
        'type': 'bool',
        'attr': 'use_console',
        'default': False
    },
    {
        # Internal var use for regression testing
        'type': 'bool',
        'attr': 'skip_version_check',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'auto_start',
        'name': 'Auto Start',
        'description': 'Auto start Indigo after export',
        'default': find_config_value(getAddonDir(), 'defaults', 'auto_start', True)
    },

    {
        'type': 'enum',
        'attr': 'render_mode',
        'name': 'Rendering Mode',
        'description': 'Choose the rendering mode to use',
        'items': [
            ('bidir', 'BiDir (CPU)', 'Bidirectional Path Tracing on the CPU'),
            ('bidir_mlt', 'BiDir MLT (CPU)', 'Bidirectional Path Tracing with Metropolis Light Transport on the CPU'),
            ('path_cpu', 'Path (CPU)', 'Path Tracing on the CPU'),
            ('path_gpu', 'Path (GPU)', 'GPU accelerated Path Tracing'),
            ('shadow', 'Shadow Pass', 'Render shadow pass for compositing'),
            ('custom', 'Custom', 'Choose your own settings')
        ],
        'default': 'bidir',
        'update': set_render_mode
    },

    {
        'type': 'bool',
        'attr': 'gpu',
        'name': 'GPU rendering',
        'description': 'Use the GPU to accelerate rendering',
        'default': False
    },
    {
        # legacy
        'type': 'bool',
        'attr': 'alpha_mask',
        'name': 'Alpha Mask',
        'description': 'Enable Alpha Mask Rendering',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'metro',
        'name': 'Metropolis',
        'description': 'Enable Metropolis Light Transport',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'shadow',
        'name': 'Shadow Pass',
        'description': 'Enable Shadow Pass Rendering',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'bidir',
        'name': 'Bi-Directional',
        'description': 'Enable Bi-Directional Tracing',
        'default': True
    },
    {
        'type': 'bool',
        'attr': 'hybrid',
        'name': 'Hybrid',
        'description': 'Enable Hybrid Metropolis/Path',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'motionblur',
        'name': 'Motion Blur',
        'description': 'Enable Motion Blur',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'logging',
        'name': 'Logging',
        'description': 'Enable Logging to Text File',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'ov_info',
        'name': 'Info Overlay',
        'description': 'Enable Info Overlay on Render',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'ov_watermark',
        'name': 'Watermark',
        'description': 'Enable Indigo watermark on Render',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'threads_auto',
        'name': 'Auto Threads',
        'description': 'Let Indigo decide how many threads to use',
        'default': True
    },
    {
        'type': 'int',
        'attr': 'threads',
        'name': 'Render Threads',
        'description': 'Number of threads to use',
        'default': 1,
        'min': 1,
        'soft_min': 1,
        'max': 64,
        'soft_max': 64
    },
    {
        'type': 'bool',
        'attr': 'save_exr_utm',
        'name': 'Un-tonemapped EXR',
        'description': 'Save Raw (un-tonemapped) EXR format',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'save_exr_tm',
        'name': 'Tonemapped EXR',
        'description': 'Save (tonemapped) EXR format',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'save_igi',
        'name': 'Indigo Image',
        'description': 'Save native IGI format',
        'default': False
    },
    {
        'type': 'bool',
        'attr': 'clamp_contributions',
        'name': 'Clamping',
        'description': 'Enable contribution clamping',
        'default': False
    },
    {
        'type': 'int',
        'attr': 'max_contribution',
        'name': 'Max Contrib',
        'description': 'Max contribution brightness, lower this as a last resort to suppress fireflies',
        'default': 10,
        'min': 1,
        'soft_min': 1,
        'max': 64,
        'soft_max': 64
    },
    {
        'type': 'int',
        'attr': 'halttime',
        'name': 'Halt Time',
        'description': 'Number of seconds to run rendering (-1 == disable)',
        'default': -1,
        'min': -1,
        'soft_min': -1,
        'max': 86400,
        'soft_max': 86400
    },
    {
        'type': 'int',
        'attr': 'haltspp',
        'name': 'Halt Samples/px',
        'description': 'Number of samples/px to run rendering (-1 == disable)',
        'default': -1,
        'min': -1,
        'soft_min': -1,
        'max': 64000,
        'soft_max': 64000
    },
    {
        'type': 'bool',
        'attr': 'skip_existing_meshes',
        'name': 'Skip writing existing meshes',
        'default': False,
    },
    {
        'type': 'int',
        'attr': 'period_save',
        'name': 'Save interval',
        'description': 'Number of seconds to save output',
        'default': 1800,
        'min': 20,
        'soft_min': 20,
        'max': 86400,
        'soft_max': 86400
    },
    {
        'type': 'bool',
        'attr': 'foreground_alpha',
        'name': 'Foreground Alpha',
        'default': False,
    },
    {
        'type': 'enum',
        'attr': 'filter_preset',
        'name': 'Filter Preset',
        'description': 'Filtering methods to use; affects image sharpness',
        'items': [
            ('default', 'Default', 'Prevents black edges, good overall performance - Splat: fastbox; Downsize: mn_cubic'),
            ('crisp', 'Crisp', 'Splat: fastbox; Downsize: mn_cubic'),
            ('strong', 'Strong', 'Splat: radial; Downsize: sharp'),
            ('custom', 'Custom', 'Choose your own settings')
        ],
        'default': 'default',
        'update': set_filter_preset
    },
    {
        'type': 'enum',
        'attr': 'splat_filter',
        'name': 'Splat',
        'description': 'Splat Filter Type',
        'default': 'fastbox',
        'items': [
            ('mitchell', 'Mitchell-Netraveli', 'mitchell'),
            ('gaussian', 'Gaussian', 'gaussian'),
            ('box', 'Box', 'box'),
            ('fastbox', 'Fast Box', 'fastbox'),
            ('radial', 'Radial', 'radial'),
            # ('sharp', 'Sharp', 'sharp')
        ]
    },
    {
        'type': 'float',
        'attr': 'splat_filter_blur',
        'name': 'Splat Blur',
        'description': 'Splat Mitchell Filter Blur Amount',
        'default': 1.0,
        'min': 0,
        'soft_min': 0,
        'max': 1,
        'soft_max': 1,
    },
    {
        'type': 'float',
        'attr': 'splat_filter_ring',
        'name': 'Splat Ring',
        'description': 'Splat Mitchell Filter Ring Amount',
        'default': 0.0,
        'min': 0,
        'soft_min': 0,
        'max': 1,
        'soft_max': 1,
    },
    {
        'type': 'enum',
        'attr': 'ds_filter',
        'name': 'Downsize',
        'description': 'Downsize Filter Type',
        'default': 'mitchell',
        'items': [
            ('mitchell', 'Mitchell-Netraveli', 'mitchell'),
            ('gaussian', 'Gaussian', 'gaussian'),
            ('box', 'Box', 'box'),
            ('radial', 'Radial', 'radial'),
            ('sharp', 'Sharp', 'sharp')
        ]
    },
    {
        'type': 'float',
        'attr': 'ds_filter_blur',
        'name': 'Downsize Blur',
        'description': 'Downsize Mitchell Filter Blur Amount',
        'default': 1.0,
        'min': 0,
        'soft_min': 0,
        'max': 1,
        'soft_max': 1,
    },
    {
        'type': 'float',
        'attr': 'ds_filter_ring',
        'name': 'Downsize Ring',
        'description': 'Downsize Mitchell Filter Ring Amount',
        'default': 0.0,
        'min': 0,
        'soft_min': 0,
        'max': 1,
        'soft_max': 1,
    },
    {
        'type': 'float',
        'attr': 'ds_filter_radius',
        'name': 'Downsize Radius',
        'description': 'Downsize Mitchell Filter Radius Amount',
        'default': 1.65,
        'min': 1,
        'soft_min': 1,
        'max': 3,
        'soft_max': 3,
    },
    {
        'type': 'int',
        'attr': 'supersample',
        'name': 'Supersamples',
        'description': 'x Oversampling',
        'default': 2,
        'min': 1,
        'max': 10,
    },
    {
        'type': 'int',
        'attr': 'bih_tri_threshold',
        'name': 'BIH Tri Threshold',
        'description': 'BIH Tri Threshold',
        'default': 1100000,
        'min': 1,
        'soft_min': 1,
        'max': 10000000,
        'soft_max': 10000000,
    },    
    {
        'type': 'enum',
        'attr': 'network_mode',
        'name': 'Network mode',
        'default': 'off',
        'items': [
            ('off', 'Off', 'Do not use networking'),
            ('master', 'Master', 'Start Indigo as a Master node (doesn\'t render)'),
            ('working_master', 'Working Master', 'Start Indigo as a Working Master node'),
            # ('manual', 'Manual', 'Connect manually to a running slave')
        ]
    },
    {
        'type': 'string',
        'attr': 'network_host',
        'name': 'Slave IP/hostname',
        'description': 'IP address or hostname of running slave'
    },
    {
        'type': 'int',
        'attr': 'network_port',
        'name': 'Network port',
        'description': 'Network render port use',
        'default': 7100,
        'min': 1025,
        'soft_min': 1025,
        'max': 32768,
        'soft_max': 32768
    },
    {
        'type': 'bool',
        'attr': 'console_output',
        'name': 'Print export progress to console',
        'default': find_config_value(getAddonDir(), 'defaults', 'console_output', False),
        'update': set_export_console_output
    },
    {
        'type': 'collection',
        'attr': 'render_devices',
        'name': 'Render Devices',
        'ptype': IndigoDevice,
    },
    {
        'type': 'bool',
        'attr': 'channel_direct_lighting',
        'name': 'Diffuse Direct Lighting',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_indirect_lighting',
        'name': 'Diffuse Indirect Lighting',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_specular_reflection_lighting',
        'name': 'Specular Reflection Lighting',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_refraction_lighting',
        'name': 'Refraction Lighting',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_transmission_lighting',
        'name': 'Transmission Lighting',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_emission_lighting',
        'name': 'Emission',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_participating_media_lighting',
        'name': 'Participating Media',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_sss_lighting',
        'name': 'Sub-Surface Scattering',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_normals',
        'name': 'Normals',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_normals_pre_bump',
        'name': 'Normals Pre-Bump',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_depth',
        'name': 'Depth',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_position',
        'name': 'Position',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_material_id',
        'name': 'Material ID',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_object_id',
        'name': 'Object ID',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_alpha',
        'name': 'Alpha',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_material_mask',
        'name': 'Material Masks',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'channel_object_mask',
        'name': 'Object Masks',
        'default': False,
    },
    {
        'type': 'bool',
        'attr': 'save_render_channels_exr',
        'name': 'Render Channels EXR',
        'description': 'Save render channels in EXR format',
        'default': False
    },
]

##########
# compute devices
default_devices = []
def load_default_devices():
    # previously saved devices are considered new defaults
    import re, os
    from .. core.util import getSettingsPath
    settings_file = getSettingsPath()
    
    global default_devices
    
    try:
        from xml.etree import ElementTree as ET
        root = ET.parse(settings_file)
        devices = root.find('selected_opencl_devices').findall('device')
        default_devices = [(d.find('device_name').text, d.find('vendor_name').text) for d in devices]
        print("Loaded default devices:", default_devices)
    except Exception:
        print('Loading default computing devices from settings.xml failed')
load_default_devices()
        
device_list = []
device_list_updated = False
def get_render_devices(refresh=False):
    global device_list
    global device_list_updated
    if refresh:
        import subprocess
        from .. core.util import getConsolePath
        
        indigo_path = getConsolePath(bpy.context.scene)
        if not os.path.exists(indigo_path):
            print('Wrong Indigo path')
            return device_list
        
        out = subprocess.run([indigo_path, '--gpu_info'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        
        device_list = []
        platforms = out.stdout.decode('utf-8', 'replace')
        platforms = platforms.split("platform_id: ")[1:]
        
        device_counters = {}

        for p in platforms:
            devices = p.split("----------- Device")
            p = devices[0]
            p = p.splitlines()
            
            for l in p:
                if l.startswith("platform_name"):
                    platform_name = l.split(": ")[1]
                    
            for l in p:
                if l.startswith("platform_vendor"):
                    platform_vendor = l.split(": ")[1]
                    
            for d in devices[1:]:
                d = d.splitlines()
                #device_id = int(d[0].split()[0])
                for l in d[1:]:
                    if l.startswith("device_name"):
                        device_name = l.split(": ")[1]
                
                # devices ids differentiate devices with the same name. Dis
                did = '{} {}'.format(device_name, platform_vendor)
                if device_counters.keys().isdisjoint([did]):
                    device_counters[did] = 0
                else:
                    device_counters[did] += 1
                device_id = device_counters[did]
                
                device_list.append((platform_name, device_name, platform_vendor, device_id))
            
        #print('\n********\n', device_list, '\n*******')
        return device_list
    else:
        return device_list

#get_render_devices(True)

###########

import time

from . import register_properties_dict
@register_properties_dict
class Indigo_Engine_Properties(bpy.types.PropertyGroup, export.xml_builder):
    properties = properties
    
    def refresh_device_collection(self):
        devices = device_list[:]
        first_refresh = False
        if len(devices) and len(self.render_devices) == 0:
            # self.render_devices refreshed for the first time. Use default_devices to activate suitable entries
            first_refresh = True
        
        previously_active = [d for d in self.render_devices if d.use]
        # remove obsolete entries
        k = 0
        while k < len(self.render_devices):
            d = self.render_devices[k]
            
            found = False
            for i, dl in enumerate(devices):
                found = False
                if (d.platform, d.device, d.vendor, d.id) == dl:
                    del devices[i]
                    found = True
                    break
                
            if not found:
                self.render_devices.remove(k)
                k -= 1

            k += 1
        
        #add new entries    
        for d in devices:
            device = self.render_devices.add()
            device.platform = d[0]
            device.device = d[1]
            device.vendor = d[2]
            device.id = d[3]
            
        if first_refresh:
            for dd in default_devices:
                for d in self.render_devices:
                    if (d.device, d.vendor) == dd and not d.use:
                        d.use = True
                        break
            
        
    
    # xml_builder members

    def build_xml_element(self, scene):
        xml = self.Element('scene')
        xres = scene.render.resolution_x * scene.render.resolution_percentage // 100
        yres = scene.render.resolution_y * scene.render.resolution_percentage // 100
        xml_format = {
            'metadata' : {
                'created_date':    [time.strftime('%Y-%m-%d %H:%M:%S GMT', time.gmtime())],
                'exporter':        ['Blendigo ' + '.'.join(['%i'%v for v in bl_info['version']])],
                'platform':        ['%s - %s - Python %s' % (PlatformInformation.platform_id, PlatformInformation.uname, PlatformInformation.python)],
                'author':        [PlatformInformation.user],
            },
            'renderer_settings': {
                'width':  [xres],
                'height': [yres],
                'bih_tri_threshold': 'bih_tri_threshold',
                'metropolis': 'metro',

                'logging': 'logging',
                'bidirectional': 'bidir',
                'save_untonemapped_exr': 'save_exr_utm',
                'save_tonemapped_exr': 'save_exr_tm',
                'save_igi': 'save_igi',
                'save_render_channels_exr': 'save_render_channels_exr',
                'image_save_period': 'period_save',
                'halt_time': 'halttime',
                'halt_samples_per_pixel': 'haltspp',
                'hybrid': 'hybrid',

                'super_sample_factor': 'supersample',
                'watermark': 'ov_watermark',
                'info_overlay': 'ov_info',

                'aperture_diffraction': [str(scene.camera.data.indigo_camera.ad).lower()],
                'vignetting': [str(scene.camera.data.indigo_camera.vignetting).lower()],
                'post_process_diffraction': [str(scene.camera.data.indigo_camera.ad_post).lower()],
                'render_foreground_alpha': 'foreground_alpha',
                'max_contribution': 'max_contribution',
                'clamp_contributions': 'clamp_contributions',
                
                'shadow_pass': 'shadow',

                'gpu': 'gpu',

                'normals_channel': 'channel_normals',
                'normals_pre_bump_channel': 'channel_normals_pre_bump',
                'position_channel': 'channel_depth',
                'depth_channel': 'channel_position',
                'material_id_channel': 'channel_material_id',
                'object_id_channel': 'channel_object_id',
                'foreground_channel': 'channel_alpha',
                'material_masks': 'channel_material_mask',
                'object_masks': 'channel_object_mask',
                'direct_lighting_channel': 'channel_direct_lighting',
                'indirect_lighting_channel': 'channel_indirect_lighting',
                'specular_reflection_lighting_channel': 'channel_specular_reflection_lighting',
                'refraction_lighting_channel': 'channel_refraction_lighting',
                'transmission_lighting_channel': 'channel_transmission_lighting',
                'emission_lighting_channel': 'channel_emission_lighting',
                'participating_media_lighting_channel': 'channel_participating_media_lighting',
                'sss_lighting_channel': 'channel_sss_lighting',
            },
        }

        # Auto threads setting
        xml_format['renderer_settings']['auto_choose_num_threads'] = 'threads_auto'
        if not self.threads_auto:
            xml_format['renderer_settings']['num_threads'] = 'threads'

        # Make splat filter element
        if self.splat_filter in ['box', 'gaussian', 'fastbox']:
            xml_format['renderer_settings']['splat_filter'] = { self.splat_filter: '' } # generate an empty element
        elif self.splat_filter == 'mitchell':
            xml_format['renderer_settings']['splat_filter'] = {
                'mn_cubic': {
                    'blur': 'splat_filter_blur',
                    'ring': 'splat_filter_ring'
                }
            }

        # Make downsize filter element
        if self.ds_filter in ['box', 'gaussian']:
            xml_format['renderer_settings']['downsize_filter'] = { self.ds_filter: '' } # generate an empty element
        elif self.ds_filter == 'mitchell':
            xml_format['renderer_settings']['downsize_filter'] = {
                'mn_cubic': {
                    'blur': 'ds_filter_blur',
                    'ring': 'ds_filter_ring',
                    'radius': 'ds_filter_radius'
                }
            }

        # Region rendering
        if scene.render.use_border:
            x1 = int(xres*scene.render.border_min_x)
            y1 = int(yres-(yres*scene.render.border_max_y))
            x2 = int(xres*scene.render.border_max_x)
            y2 = int(yres-(yres*scene.render.border_min_y))
            xml_format['renderer_settings']['render_region'] = {
                'x1': [x1],
                'x2': [x2],
                'y1': [y1],
                'y2': [y2]
            }

        self.build_subelements(scene, xml_format, xml)

        return xml
