# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import os

from ..extensions_framework import declarative_property_group
from ..extensions_framework import util as efutil
from ..extensions_framework.validate import Logic_OR as O, Logic_AND as A, Logic_Operator as LO

from .. import LuxRenderAddon
from ..outputs.pure_api import PYLUX_AVAILABLE
from ..outputs.luxcore_api import PYLUXCORE_AVAILABLE, UseLuxCore


def check_renderer_settings(context):
    lre = context.scene.luxrender_rendermode
    lri = context.scene.luxrender_integrator

    def clear_renderer_alert():
        if 'surfaceintegrator' in lri.alert.keys():
            del lri.alert['surfaceintegrator']

        if 'lightstrategy' in lri.alert.keys():
            del lri.alert['lightstrategy']

        if 'advanced' in lri.alert.keys():
            del lri.alert['advanced']

    # Check hybrid renderer and surfaceintegrator compatibility
    hybrid_valid = (lri.surfaceintegrator == 'path' and lri.lightstrategy in ['one', 'all', 'auto'])

    if ((lre.renderer == 'hybrid' and hybrid_valid) or lre.renderer != 'hybrid'):
        clear_renderer_alert()
    elif lre.renderer == 'hybrid' and not hybrid_valid:
        # These logical tests should evaluate to True if the setting is incompatible
        lri.alert['surfaceintegrator'] = {'surfaceintegrator': LO({'!=': ['path', 'bidirectional']})}
        lri.alert['lightstrategy'] = {'lightstrategy': LO({'!=': ['one', 'all', 'auto']})}

        return

    # check compatible SPPM mode
    sppm_valid = lri.surfaceintegrator == 'sppm'

    if ((lre.renderer == 'sppm' and sppm_valid) or lre.renderer != 'sppm'):
        clear_renderer_alert()
    elif lre.renderer == 'sppm' and not sppm_valid:
        lri.alert['surfaceintegrator'] = {'surfaceintegrator': LO({'!=': 'sppm'})}

        return


def find_apis():
    apis = [('EXT', 'External', 'EXT'),]

    if PYLUX_AVAILABLE:
        apis.append(('INT', 'Internal', 'INT'))

    return apis


@LuxRenderAddon.addon_register_class
class luxrender_testing(declarative_property_group):
    """
    Properties related to exporter and scene testing
    """

    ef_attach_to = ['Scene']

    controls = [
        'clay_render',
        'object_analysis',
        're_raise'
    ]

    visibility = {}

    properties = [
        {
            'type': 'bool',
            'attr': 'clay_render',
            'name': 'Clay Render',
            'description': 'Export all non-glass materials as default "clay"',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'object_analysis',
            'name': 'Debug: Print Object Analysis',
            'description': 'Show extra output as objects are processed',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 're_raise',
            'name': 'Debug: Show Error Traceback Messages',
            'description': 'Show export error messages in the UI as well as the console',
            'default': False
        },
    ]


@LuxRenderAddon.addon_register_class
class luxrender_engine(declarative_property_group):
    """
    Storage class for LuxRender Engine settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        # 'export_type', #Drawn in core/init
        #       'binary_name',
        #       'write_files',
        ['export_particles', 'export_hair'],
        'embed_filedata',
        'mesh_type',
        'partial_ply',
        ['render', 'monitor_external'],
        'fixed_seed',
        # ['threads_auto', 'fixed_seed'],
        # 'threads',
        'log_verbosity',
        ['min_epsilon', 'max_epsilon'],
    ]

    visibility = {
        'write_files': {'export_type': 'INT'},
        'embed_filedata': O([{'export_type': 'EXT'}, A([{'export_type': 'INT'}, {'write_files': True}])]),
        'mesh_type': O([{'export_type': 'EXT'}, A([{'export_type': 'INT'}, {'write_files': True}])]),
        'binary_name': {'export_type': 'EXT'},
        'render': O([{'write_files': True}, {'export_type': 'EXT'}]),
        # We need run renderer unless we are set for internal-pipe mode, which is the only time both of these are false
        'monitor_external': {'export_type': 'EXT', 'binary_name': 'luxrender', 'render': True},
        'partial_ply': O([{'export_type': 'EXT'}, A([{'export_type': 'INT'}, {'write_files': True}])]),
        'threads_auto': O([A([{'write_files': False}, {'export_type': 'INT'}]),
                           A([O([{'write_files': True}, {'export_type': 'EXT'}]), {'render': True}])]),
        # The flag options must be present for any condition where run renderer is present and checked,
        # as well as internal-pipe mode
        'threads': O([A([{'write_files': False}, {'export_type': 'INT'}, {'threads_auto': False}]), A(
            [O([{'write_files': True}, {'export_type': 'EXT'}]), {'render': True}, {'threads_auto': False}])]),
        # Longest logic test in the whole plugin! threads-auto is in both sides,
        # since we must check that it is false for either internal-pipe mode, or when using run-renderer.
        'fixed_seed': O([A([{'write_files': False}, {'export_type': 'INT'}]),
                         A([O([{'write_files': True}, {'export_type': 'EXT'}]), {'render': True}])]),
        'log_verbosity': O([A([{'write_files': False}, {'export_type': 'INT'}]),
                            A([O([{'write_files': True}, {'export_type': 'EXT'}]), {'render': True}])]),
        'min_epsilon': O([A([{'write_files': False}, {'export_type': 'INT'}]), A(
            [O([{'write_files': True}, {'export_type': 'EXT'}]), {'render': True},
             O([{'binary_name': 'luxrender'}, {'binary_name': 'luxconsole'}])])]),
        'max_epsilon': O([A([{'write_files': False}, {'export_type': 'INT'}]), A(
            [O([{'write_files': True}, {'export_type': 'EXT'}]), {'render': True},
             O([{'binary_name': 'luxrender'}, {'binary_name': 'luxconsole'}])])]),
    }

    alert = {}

    properties = [
        {
            'type': 'bool',
            'attr': 'threads_auto',
            'name': 'Auto Threads',
            'description': 'Let LuxRender decide how many threads to use',
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
            'type': 'enum',
            'attr': 'export_type',
            'name': 'Export Type',
            'description': 'Run LuxRender inside or outside of Blender',
            'default': 'EXT',  # if not PYLUX_AVAILABLE else 'INT',
            'items': find_apis(),
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'integratedimaging',
            'name': 'Integrated imaging workflow',
            'description': 'Transfer rendered image directly to Blender without saving to disk (adds Z-buffer support \
             and is more stable, but may take longer to refresh)',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'render',
            'name': 'Run Renderer',
            'description': 'Run renderer after export',
            'default': efutil.find_config_value('luxrender', 'defaults', 'auto_start', True),
        },
        {
            'type': 'bool',
            'attr': 'monitor_external',
            'name': 'Monitor External',
            'description': 'Monitor external GUI rendering; when selected, LuxBlend will copy the render image from \
            the external GUI',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'selected_luxrender_api',
            'name': 'LuxRender API version',
            'description': 'Choose between LuxRender v1.x and v2.x API',
            'default': 'classic',
            'items': [
                         ('classic', 'Classic API', 'Use LuxRender v1.x API'),
                     ] + ([
                         ('luxcore', 'LuxCore API (Experimental)', 'Use LuxRender v2.x API (experimental and unstable!)')
                     ] if PYLUXCORE_AVAILABLE else []),
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'partial_ply',
            'name': 'Use Cached PLY Files',
            'description': 'Only export PLY files for new or modified objects',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'binary_name',
            'name': 'External Type',
            'description': 'Choose full GUI, console renderer or real-time rendering',
            'default': 'luxrender',
            'items': [
                ('luxrender', 'LuxRender GUI', 'Render with the LuxRender GUI application'),
                ('luxconsole', 'LuxConsole', 'Render with LuxConsole and feed the result to the UV/Image Editor'),
                ('luxvr', 'LuxVR', 'Render with the LuxVR realtime preview tool'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'write_files',
            'name': 'Write to Disk',
            'description': 'Write scene files to disk (allows use of PLY file cache)',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'export_hair',
            'name': 'Export Hair',
            'description': 'Export particle hair systems',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'export_particles',
            'name': 'Export Particles',
            'description': 'Export particle system dupli objects',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'embed_filedata',
            'name': 'Embed File Data',
            'description': 'Embed all external files (images etc) inline into the exporter output',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'is_saving_lbm2',
            'name': '<for internal use>',
            'default': False,
            'save_in_preset': False
        },
        {
            'type': 'enum',
            'attr': 'mesh_type',
            'name': 'Mesh Format',
            'description': 'Sets whether to export scene geometry as PLY files or directly in the LXO file, PLY is \
            faster and recommended. This can be overridden per mesh from the mesh properties panel',
            'items': [
                ('native', 'LuxRender mesh', 'native'),
                ('binary_ply', 'Binary PLY', 'binary_ply')
            ],
            'default': 'binary_ply',
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'log_verbosity',
            'name': 'Log Verbosity',
            'description': 'Logging verbosity level',
            'default': 'default',
            'items': [
                ('verbose', 'Verbose', 'verbose'),
                ('default', 'Default', 'default'),
                ('quiet', 'Quiet', 'quiet'),
                ('very-quiet', 'Very quiet', 'very-quiet'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'min_epsilon',
            'name': 'Min Epsilon',
            'description': 'Minimum epsilon value (0 for auto)',
            'default': 0,
            'min': 0,
            'soft_min': 0,
            'max': 1.0,
            'soft_max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'max_epsilon',
            'name': 'Max Epsilon',
            'description': 'Maximum epsilon value (0 for auto)',
            'default': 0,
            'min': 0,
            'soft_min': 0,
            'max': 1.0,
            'soft_max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'fixed_seed',
            'name': 'Use Fixed Seeds',
            'description': 'Use fixed seeds for render threads. Helps with keeping noise even for animations',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'preview_stop',
            'name': 'Stop Preview',
            'description': 'preview_stop',
            'default': False
        },
    ]

    def allow_file_embed(self):
        saving_files = (self.export_type == 'EXT' or (self.export_type == 'INT' and self.write_files))

        return self.is_saving_lbm2 or (saving_files and self.embed_filedata)


@LuxRenderAddon.addon_register_class
class luxrender_networking(declarative_property_group):
    ef_attach_to = ['Scene']

    controls = [
        'servers',
        'serverinterval'
    ]

    visibility = {
        'servers': {'use_network_servers': True},
        'serverinterval': {'use_network_servers': True},
    }

    properties = [
        {  # drawn in panel header
           'type': 'bool',
           'attr': 'use_network_servers',
           'name': 'Use Networking',
           'default': efutil.find_config_value('luxrender', 'defaults', 'use_network_servers', False),
           'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'servers',
            'name': 'Servers',
            'description': 'Comma separated list of Lux server IP addresses',
            'default': efutil.find_config_value('luxrender', 'defaults', 'servers', ''),
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'serverinterval',
            'name': 'Upload interval',
            'description': 'Interval for server image transfers (seconds)',
            'default': int(efutil.find_config_value('luxrender', 'defaults', 'serverinterval', '180')),
            'min': 10,
            'soft_min': 10,
            'save_in_preset': True
        },
    ]
