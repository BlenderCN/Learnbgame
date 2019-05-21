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

from collections import OrderedDict

import os
import sys
import subprocess

from bpy_extras.io_utils import axis_conversion

# Framework libs
from ..extensions_framework import util as efutil

# Exporter libs
from ..export import ExportContextBase
from ..export import matrix_to_list
from ..export import get_output_subdir
from ..outputs import MtsLog, MtsManager
from ..properties import ExportedVolumes


mitsuba_props = {
    'ref',
    'lookat',
    'scale',
    'matrix',
    'point',
    'vector',
    'rgb',
    'srgb',
    'blackbody',
    'spectrum',
}

mitsuba_tags = {
    'scene',
    'shape',
    'sampler',
    'film',
    'integrator',
    'texture',
    'sensor',
    'emitter',
    'subsurface',
    'medium',
    'volume',
    'phase',
    'bsdf',
    'rfilter',
    'transform',
    'animation',
}

# Tree for plugin types
mitsuba_plugin_tree = [
    # Shapes
    ('shape', {
        'cube',
        'sphere',
        'cylinder',
        'rectangle',
        'disk',
        'shapegroup',
        'instance',
        'serialized',
        'ply',
        'hair',
        'deformable',
    }),
    # Surface scattering models
    ('bsdf', {
        'diffuse',
        'roughdiffuse',
        'dielectric',
        'thindielectric',
        'roughdielectric',
        'conductor',
        'roughconductor',
        'plastic',
        'roughplastic',
        'coating',
        'roughcoating',
        'bumpmap',
        'phong',
        'ward',
        'mixturebsdf',
        'blendbsdf',
        'mask',
        'twosided',
        'difftrans',
        'hk',
        #'irawan',
        'null',
    }),
    # Textures
    ('texture', {
        'bitmap',
        'checkerboard',
        'gridtexture',
        'scale',
        'vertexcolors',
        'wireframe',
        'curvature',
    }),
    # Subsurface
    ('subsurface', {
        'dipole',
        'singlescatter',
    }),
    # Medium
    ('medium', {
        'homogeneous',
        'heterogeneous',
    }),
    # Phase
    ('phase', {
        'isotropic',
        'hg',
    }),
    # Volume
    ('volume', {
        'constvolume',
        'gridvolume',
    }),
    # Emitters
    ('emitter', {
        'point',
        'area',
        'spot',
        'directional',
        'collimated',
        'constant',
        'envmap',
        'sun',
        'sky',
        'sunsky',
    }),
    # Sensors
    ('sensor', {
        'perspective',
        'thinlens',
        'orthographic',
        'telecentric',
        'spherical',
        'perspective_rdist',
    }),
    # Integrators
    ('integrator', {
        'ao',
        'direct',
        'path',
        'volpath_simple',
        'volpath',
        'bdpt',
        'photonmapper',
        'ppm',
        'sppm',
        'pssmlt',
        'mlt',
        'erpt',
        'ptracer',
        'vpl',
        'adaptive',
        'irrcache',
        'multichannel',
    }),
    # Sample generators
    ('sampler', {
        'independent',
        'stratified',
        'ldsampler',
        'halton',
        'hammersley',
        'sobol',
    }),
    # Films
    ('film', {
        'hdrfilm',
        'ldrfilm',
    }),
    # Rfilters
    ('rfilter', {
        'box',
        'tent',
        'gaussian',
        'mitchell',
        'catmullrom',
        'lanczos',
    }),
]


def get_plugin_tag(plugin):
    for plugin_tag, plugin_types in mitsuba_plugin_tree:
        if plugin in plugin_types:
            return plugin_tag

    return plugin


class Files:
    MAIN = 0
    MATS = 1
    GEOM = 2
    VOLM = 3


class FileExportContext(ExportContextBase):
    '''
    File API
    '''

    EXPORT_API_TYPE = 'FILE'

    files = []
    file_names = []
    file_tabs = []
    file_stack = []
    current_file = Files.MAIN

    def wf(self, ind, st, tabs=0):
        '''
        ind                 int
        st                  string
        tabs                int

        Write a string to file index ind.
        Optionally indent the string by a number of tabs

        Returns None
        '''

        if len(self.files) == 0:
            scene = object()
            scene.name = 'untitled'
            scene.frame_current = 1
            self.set_filename(scene, 'default')

        # Prevent trying to write to a file that isn't open
        if self.files[ind] is None:
            ind = 0

        self.files[ind].write('%s%s' % ('\t' * tabs, st))
        self.files[ind].flush()

    def set_filename(self, scene, name, split_files=False):
        '''
        name                string

        Open the main, materials, and geometry files for output,
        using filenames based on the given name.

        Returns None
        '''

        # If any files happen to be open, close them and start again
        for f in self.files:
            if f is not None:
                f.close()

        self.files = []
        self.file_names = []
        self.file_tabs = []
        self.file_stack = []

        if name[-4:] != '.xml':
            name += '.xml'

        self.file_names.append(name)
        self.files.append(open(self.file_names[Files.MAIN], 'w', encoding='utf-8', newline="\n"))
        self.file_tabs.append(0)
        self.file_stack.append([])
        self.writeHeader(Files.MAIN, '# Main Scene File')

        MtsLog('Scene File: %s' % self.file_names[Files.MAIN])

        if split_files:
            subdir = get_output_subdir(scene)

            self.file_names.append('%s/Mitsuba-Materials.xml' % subdir)
            self.files.append(open(self.file_names[Files.MATS], 'w', encoding='utf-8', newline="\n"))
            self.file_tabs.append(0)
            self.file_stack.append([])
            self.writeHeader(Files.MATS, '# Materials File')

            self.file_names.append('%s/Mitsuba-Geometry.xml' % subdir)
            self.files.append(open(self.file_names[Files.GEOM], 'w', encoding='utf-8', newline="\n"))
            self.file_tabs.append(0)
            self.file_stack.append([])
            self.writeHeader(Files.GEOM, '# Geometry File')

            self.file_names.append('%s/Mitsuba-Volumes.xml' % subdir)
            self.files.append(open(self.file_names[Files.VOLM], 'w', encoding='utf-8', newline="\n"))
            self.file_tabs.append(0)
            self.file_stack.append([])
            self.writeHeader(Files.VOLM, '# Volume File')

        self.set_output_file(Files.MAIN)

    def set_output_file(self, file):
        '''
        file                int

        Switch next output to the given file index

        Returns None
        '''

        self.current_file = file

    def writeHeader(self, file, comment):
        self.wf(file, '<?xml version="1.0" encoding="utf-8"?>\n')
        self.wf(file, '<!-- %s -->\n' % comment)

    def openElement(self, name, attributes={}, file=None):
        if file is not None:
            self.set_output_file(file)

        self.wf(self.current_file, '<%s' % name, self.file_tabs[self.current_file])

        for (k, v) in attributes.items():
            self.wf(self.current_file, ' %s=\"%s\"' % (k, v.replace('"', '')))

        self.wf(self.current_file, '>\n')

        # Indent
        self.file_tabs[self.current_file] = self.file_tabs[self.current_file] + 1
        self.file_stack[self.current_file].append(name)

    def closeElement(self, file=None):
        if file is not None:
            self.set_output_file(file)

        # Un-indent
        self.file_tabs[self.current_file] = self.file_tabs[self.current_file] - 1
        name = self.file_stack[self.current_file].pop()

        self.wf(self.current_file, '</%s>\n' % name, self.file_tabs[self.current_file])

    def element(self, name, attributes={}, file=None):
        if file is not None:
            self.set_output_file(file)

        self.wf(self.current_file, '<%s' % name, self.file_tabs[self.current_file])

        for (k, v) in attributes.items():
            self.wf(self.current_file, ' %s=\"%s\"' % (k, v))

        self.wf(self.current_file, '/>\n')

    def parameter(self, paramType, paramName, attributes={}, file=None):
        if file is not None:
            self.set_output_file(file)

        self.wf(self.current_file, '<%s name="%s"' % (paramType, paramName), self.file_tabs[self.current_file])

        for (k, v) in attributes.items():
            self.wf(self.current_file, ' %s=\"%s\"' % (k, v))

        self.wf(self.current_file, '/>\n')

    # Funtions to emulate Mitsuba extension API

    def pmgr_create(self, mts_dict=None, args={}):
        if mts_dict is None or not isinstance(mts_dict, dict) or len(mts_dict) == 0 or 'type' not in mts_dict:
            return

        param_dict = mts_dict.copy()
        plugin_type = param_dict.pop('type')
        plugin = get_plugin_tag(plugin_type)

        # Special case for scale, it can be a transform or a texture
        if plugin_type == 'scale':
            if 'scale' not in param_dict:
                plugin = 'scale'

        if plugin != plugin_type:
            args['type'] = plugin_type

        if plugin == 'scene':
            args['version'] = '0.5.0'

        elif plugin in mitsuba_props:
            args.update(param_dict)
            param_dict = {}

            if plugin == 'ref' and 'id' in args and args['id'] not in self.exported_ids:
                MtsLog('************** Reference ID - %s - exported before referencing **************' % (args['id']))
                #return

            elif plugin in {'matrix', 'lookat', 'scale'}:
                del args['name']

        else:
            if plugin == 'transform' and 'time' in param_dict:
                args['time'] = str(param_dict.pop('time'))
                del args['name']

            if 'id' in param_dict:
                args['id'] = param_dict.pop('id')

                if args['id'] not in self.exported_ids:
                    self.exported_ids.add(args['id'])

                else:
                    MtsLog('************** Plugin - %s - ID - %s - already exported **************' % (plugin_type, args['id']))
                    #return

        try:
            if args['name'] == args['id']:
                del(args['name'])

        except:
            pass

        if len(param_dict) > 0 and plugin in mitsuba_tags:
            self.openElement(plugin, args)

            for param, value in param_dict.items():
                if isinstance(value, dict) and 'type' in value:
                    self.pmgr_create(value, {'name': param})

                elif isinstance(value, str):
                    self.parameter('string', param, {'value': value})

                elif isinstance(value, bool):
                    self.parameter('boolean', param, {'value': str(value).lower()})

                elif isinstance(value, int):
                    self.parameter('integer', param, {'value': '%d' % value})

                elif isinstance(value, float):
                    self.parameter('float', param, {'value': '%f' % value})

                else:
                    MtsLog('************** %s param not supported: %s **************' % (plugin_type, param))
                    MtsLog(value)

            self.closeElement()

        elif len(param_dict) == 0:
            self.element(plugin, args)

        else:
            MtsLog('************** Plugin not supported: %s **************' % plugin_type)
            MtsLog(param_dict)

    def spectrum(self, value, mode=''):
        if not mode:
            mode = self.color_mode

        spec = {}

        if isinstance(value, (dict)):
            if 'type' in value:
                if value['type'] in {'rgb', 'srgb', 'spectrum'}:
                    spec = self.spectrum(value['value'], value['type'])

                else:
                    spec = value

        elif isinstance(value, (float, int)):
            spec = {'value': "%f" % value, 'type': 'spectrum'}

        elif isinstance(value, (str)):
            spec = {'filename': self.get_export_path(value), 'type': 'spectrum'}

        else:
            try:
                items = list(value)

                for i in items:
                    if not isinstance(i, (float, int, tuple)):
                        raise Exception('Error: spectrum list contains an unknown type')

            except:
                items = None

            if items:
                totitems = len(items)

                if isinstance(items[0], (float, int)):
                    if totitems == 3 or totitems == 4:
                        spec = {'value': "%f %f %f" % (items[0], items[1], items[2])}

                        if mode == 'srgb':
                            spec.update({'type': 'srgb'})

                        else:
                            spec.update({'type': 'rgb'})

                    elif totitems == 1:
                        spec = {'value': "%f" % items[0], 'type': 'spectrum'}

                    else:
                        MtsLog('Expected spectrum items to be 1, 3 or 4, got %d.' % len(items), type(items), items)

                else:
                    contspec = []

                    for spd in items:
                        (wlen, val) = spd
                        contspec.append('%d:%f' % (wlen, val))

                    spec = {'value': ", ".join(contspec), 'type': 'spectrum'}

            else:
                MtsLog('Unknown spectrum type.', type(value), value)

        if not spec:
            spec = {'value': "0.0", 'type': 'spectrum'}

        return spec

    def vector(self, x, y, z):
        # Blender is Z up but Mitsuba is Y up, convert the vector
        return {
            'type': 'vector',
            'x': '%f' % x, 'y': '%f' % z, 'z': '%f' % -y
        }

    def point(self, x, y, z):
        # Blender is Z up but Mitsuba is Y up, convert the point
        return {
            'type': 'point',
            'x': '%f' % x, 'y': '%f' % z, 'z': '%f' % -y
        }

    def transform_lookAt(self, origin, target, up, scale=False):
        # Blender is Z up but Mitsuba is Y up, convert the lookAt
        params = OrderedDict()

        if scale:
            params.update([
                ('scale', {
                    'type': 'scale',
                    'x': scale,
                    'y': scale
                })
            ])

        params.update([
            ('type', 'transform'),
            ('lookat', {
                'type': 'lookat',
                'origin': '%f, %f, %f' % (origin[0], origin[2], -origin[1]),
                'target': '%f, %f, %f' % (target[0], target[2], -target[1]),
                'up': '%f, %f, %f' % (up[0], up[2], -up[1])
            })
        ])

        return params

    def animated_lookAt(self, motion):
        if len(motion) == 2 and motion[0][1] == motion[1][1]:
            del motion[1]

        params = {}

        if len(motion) > 1:
            params = OrderedDict([
                ('type', 'animation'),
            ])

            for (t, (origin, target, up, scale)) in motion:
                mat = self.transform_lookAt(origin, target, up, scale)
                mat.update({'time': t})
                params.update([
                    ('trafo%f' % t, mat)
                ])

        else:
            (origin, target, up, scale) = motion[0][1]
            params = self.transform_lookAt(origin, target, up, scale)

        return params

    def transform_matrix(self, matrix):
        # Blender is Z up but Mitsuba is Y up, convert the matrix
        global_matrix = axis_conversion(to_forward="-Z", to_up="Y").to_4x4()
        l = matrix_to_list(global_matrix * matrix)
        value = " ".join(["%f" % f for f in l])

        params = {
            'type': 'transform',
            'matrix': {
                'type': 'matrix',
                'value': value,
            }
        }

        return params

    def animated_transform(self, motion):
        if len(motion) == 2 and motion[0][1] == motion[1][1]:
            del motion[1]

        params = {}

        if len(motion) > 1:
            params = OrderedDict([
                ('type', 'animation'),
            ])

            for (t, m) in motion:
                mat = self.transform_matrix(m)
                mat.update({'time': t})
                params.update([
                    ('trafo%f' % t, mat)
                ])

        else:
            params = self.transform_matrix(motion[0][1])

        return params

    def configure(self):
        '''
        Special handling of configure API.
        '''

        self.pmgr_create(self.scene_data)

        # Close files
        MtsLog('Wrote scene files')
        for f in self.files:
            if f is not None:
                f.close()
                MtsLog(' %s' % f.name)

        # Reset the volume redundancy check
        ExportedVolumes.reset_vol_list()

    def cleanup(self):
        self.exit()

    def exit(self):
        # If any files happen to be open, close them and start again
        for f in self.files:
            if f is not None:
                f.close()


class ExternalRenderContext:
    '''
    Mitsuba External Render
    '''

    RENDER_API_TYPE = 'EXT'

    binary_name = 'mitsuba'
    render_engine = None
    render_scene = None
    mitsuba_process = None
    cmd_args = []
    verbosity_modes = {
        'verbose': '-v',
        'quiet': '-q'
    }

    def __init__(self):
        self.render_engine = MtsManager.RenderEngine
        self.render_scene = MtsManager.CurrentScene

        if self.render_engine.is_preview:
            self.binary_name = 'mitsuba'
            verbosity = 'quiet'

        else:
            self.binary_name = self.render_scene.mitsuba_engine.binary_name
            verbosity = self.render_scene.mitsuba_engine.log_verbosity

        mitsuba_path = efutil.filesystem_path(self.render_engine.preferences.install_path)

        if mitsuba_path == '':
            return ['']

        if mitsuba_path[-1] != '/':
            mitsuba_path += '/'

        if sys.platform == 'darwin':
            if os.path.exists(os.path.join(mitsuba_path, 'Mitsuba.app/Contents/MacOS/')):
                mitsuba_path = os.path.join(mitsuba_path, 'Mitsuba.app/Contents/MacOS/')

            elif os.path.exists(os.path.join(mitsuba_path, 'Contents/MacOS/')):
                mitsuba_path = os.path.join(mitsuba_path, 'Contents/MacOS/')

            mitsuba_path += self.binary_name

            if not os.path.exists(mitsuba_path):
                MtsLog('Mitsuba not found at path: %s' % mitsuba_path, ', trying default Mitsuba location')
                mitsuba_path = '/Applications/Mitsuba.app/Contents/MacOS/%s' % self.binary_name  # try fallback to default installation path

        elif sys.platform == 'win32':
            mitsuba_path += '%s.exe' % self.binary_name

        else:
            mitsuba_path += self.binary_name

        if not os.path.exists(mitsuba_path):
            raise Exception('Mitsuba not found at path: %s' % mitsuba_path)

        self.cmd_args = [mitsuba_path]

        # set log verbosity
        if verbosity != 'default':
            self.cmd_args.append(self.verbosity_modes[verbosity])

        # Set number of threads for external processes
        if not self.render_scene.mitsuba_engine.threads_auto:
            self.cmd_args.extend(['-p', '%i' % self.render_scene.mitsuba_engine.threads])

    def set_scene(self, export_context):
        if export_context.EXPORT_API_TYPE == 'FILE':
            self.filename = export_context.file_names[0]

        else:
            raise Exception('Unknown exporter type')

    def render_start(self, dest_file):
        output_dir, output_file = os.path.split(dest_file)
        self.cmd_args.extend(['-o', dest_file])
        self.cmd_args.append(self.filename)
        MtsLog('Launching: %s' % self.cmd_args)
        self.mitsuba_process = subprocess.Popen(self.cmd_args, cwd=output_dir)

    def render_stop(self):
        # Use SIGTERM because that's the only one supported on Windows
        self.mitsuba_process.send_signal(subprocess.signal.SIGTERM)

    def test_break(self):
        return self.render_engine.test_break()

    def is_running(self):
        return self.mitsuba_process.poll() is None

    def returncode(self):
        return self.mitsuba_process.returncode
