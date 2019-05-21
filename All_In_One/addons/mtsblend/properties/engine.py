# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

import multiprocessing

from ..extensions_framework import declarative_property_group
from ..extensions_framework import util as efutil
from ..extensions_framework.validate import Logic_OR as O, Logic_AND as A

from .. import MitsubaAddon
from ..ui import refresh_preview


def get_cpu_count():
    try:
        return multiprocessing.cpu_count()

    except:
        return 1

addon_prefs = None
pymts_available = False


@MitsubaAddon.addon_register_class
class mitsuba_engine(declarative_property_group):
    '''
    Storage class for Mitsuba Engine settings.
    '''

    ef_attach_to = ['Scene']
    cpu_count = get_cpu_count()

    def find_apis(self, context):
        global addon_prefs
        global pymts_available
        apis = [
            ('EXT', 'External', 'EXT'),
        ]

        if addon_prefs is None:
            addon_prefs = MitsubaAddon.get_prefs()

            if addon_prefs is not None:
                from ..outputs.pure_api import PYMTS_AVAILABLE
                pymts_available = PYMTS_AVAILABLE

        if pymts_available:
            apis.append(('INT', 'Internal', 'INT'))

        return apis

    controls = [
        #'export_type',  # Drawn in core/init
        #'binary_name',
        #'write_files',
        ['export_particles', 'export_hair'],
        'mesh_type',
        'partial_export',
        'render',
        'refresh_interval',
        'threads_auto',
        'threads',
        'log_verbosity',
    ]

    visibility = {
        'write_files': {'export_type': 'INT'},
        'mesh_type': O([{'export_type':'EXT'}, A([{'export_type':'INT'}, {'write_files': True}])]),
        'binary_name': {'export_type': 'EXT'},
        'render': O([{'write_files': True}, {'export_type': 'EXT'}]),  # We need run renderer unless we are set for internal-pipe mode, which is the only time both of these are false
        'threads': {'threads_auto': False},
        'refresh_interval': {'binary_name': 'mitsuba', 'render': True}
    }

    properties = [
        {
            'type': 'bool',
            'attr': 'threads_auto',
            'name': 'Auto Threads',
            'description': 'Let Mitsuba decide how many threads to use',
            'default': True
        },
        {
            'type': 'int',
            'attr': 'threads',
            'name': 'Render Threads',
            'description': 'Number of threads to use',
            'default': cpu_count,
            'min': 0,
            'soft_min': 0,
            'max': cpu_count,
            'soft_max': cpu_count
        },
        {
            'type': 'enum',
            'attr': 'export_type',
            'name': 'Export Type',
            'description': 'Run Mitsuba inside or outside of Blender',
            'items': find_apis,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'render',
            'name': 'Run Renderer',
            'description': 'Run renderer after export',
            'default': efutil.find_config_value('mitsuba', 'defaults', 'auto_start', True),
        },
        {
            'type': 'bool',
            'attr': 'partial_export',
            'name': 'Partial Mesh Export',
            'description': 'Skip exporting Mesh files that already exist. Try disabling this if you have geometry issues',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'binary_name',
            'name': 'External Type',
            'description': 'Choose full GUI or console renderer',
            'default': 'mitsuba',
            'items': [
                ('mitsuba', 'Mitsuba Console', 'mitsuba'),
                ('mtsgui', 'Mitsuba GUI', 'mtsgui')
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'write_files',
            'name': 'Write to Disk',
            'description': 'Write scene files to disk',
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
            'type': 'enum',
            'attr': 'mesh_type',
            'name': 'Mesh Format',
            'description': 'Sets whether to export scene geometry as Serialized or PLY files. Serialized is faster and recommended',
            'items': [
                ('serialized', 'Serialized Mesh', 'serialized'),
                ('binary_ply', 'Binary PLY', 'binary_ply')
            ],
            'default': 'serialized',
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
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'refresh_interval',
            'name': 'Refresh interval',
            'description': 'Period for updating rendering on screen (in seconds)',
            'default': 5,
            'min': 1,
            'soft_min': 1,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'preview_depth',
            'name': 'Depth',
            'description': 'Max. path depth used when generating the preview (2: direct illumination, 3: one-bounce indirect, etc.)',
            'default': int(efutil.find_config_value('mitsuba', 'defaults', 'preview_depth', '2')),
            'min': 2,
            'max': 10,
            'update': refresh_preview,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'preview_spp',
            'name': 'SPP',
            'description': 'Samples per pixel used to generate the preview',
            'default': int(efutil.find_config_value('mitsuba', 'defaults', 'preview_spp', '16')),
            'min': 1,
            'max': 128,
            'update': refresh_preview,
            'save_in_preset': True
        },
    ]


@MitsubaAddon.addon_register_class
class mitsuba_testing(declarative_property_group):
    """
    Properties related to exporter and scene testing
    """

    ef_attach_to = ['Scene']

    controls = [
        'object_analysis',
        're_raise'
    ]

    visibility = {}

    properties = [
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
