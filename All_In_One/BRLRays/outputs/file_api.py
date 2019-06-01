#TODO port to python3?

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
from ..outputs import BrlLog, BrlManager
from ..properties import ExportedVolumes


brlrays_props = {
    'scale',
    'matrix',
    'point',
    'vector',
    'rgb',
    'blackbody',
    'spectrum',
}

brlrays_tags = {
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
brlrays_plugin_tree = [
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
    for plugin_tag, plugin_types in brlrays_plugin_tree:
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

        if name[-2:] != '.g':
            name += '.g'

        self.file_names.append(name)
        self.files.append(open(self.file_names[Files.MAIN], 'w', encoding='utf-8', newline="\n"))
        self.file_tabs.append(0)
        self.file_stack.append([])
        self.writeHeader(Files.MAIN, '# Main Scene File')

        BrlLog('Scene File: %s' % self.file_names[Files.MAIN])

        #TODO -- delete?
        if split_files:
            subdir = get_output_subdir(scene)

            self.file_names.append('%s/brlrays-Materials.xml' % subdir)
            self.files.append(open(self.file_names[Files.MATS], 'w', encoding='utf-8', newline="\n"))
            self.file_tabs.append(0)
            self.file_stack.append([])
            self.writeHeader(Files.MATS, '# Materials File')

            self.file_names.append('%s/brlrays-Geometry.xml' % subdir)
            self.files.append(open(self.file_names[Files.GEOM], 'w', encoding='utf-8', newline="\n"))
            self.file_tabs.append(0)
            self.file_stack.append([])
            self.writeHeader(Files.GEOM, '# Geometry File')

            self.file_names.append('%s/brlrays-Volumes.xml' % subdir)
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
        self.wf(file, 'title {%s}\n' % comment)
        self.wf(file, 'units mm\n') #TODO take blender unit

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

    # Funtions to emulate brlrays extension API

    def pmgr_create(self, brl_dict=None, args={}):
        if brl_dict is None or not isinstance(brl_dict, dict) or len(brl_dict) == 0 or 'type' not in brl_dict:
            return

        param_dict = brl_dict.copy()
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

        elif plugin in brlrays_props:
            args.update(param_dict)
            param_dict = {}

            if plugin == 'ref' and 'id' in args and args['id'] not in self.exported_ids:
                BrlLog('************** Reference ID - %s - exported before referencing **************' % (args['id']))
                return

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
                    BrlLog('************** Plugin - %s - ID - %s - already exported **************' % (plugin_type, args['id']))
                    return

        try:
            if args['name'] == args['id']:
                del(args['name'])

        except:
            pass

        if len(param_dict) > 0 and plugin in brlrays_tags:
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
                    BrlLog('************** %s param not supported: %s **************' % (plugin_type, param))
                    BrlLog(value)

            self.closeElement()

        elif len(param_dict) == 0:
            self.element(plugin, args)

        else:
            BrlLog('************** Plugin not supported: %s **************' % plugin_type)
            BrlLog(param_dict)

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
                        BrlLog('Expected spectrum items to be 1, 3 or 4, got %d.' % len(items), type(items), items)

                else:
                    contspec = []

                    for spd in items:
                        (wlen, val) = spd
                        contspec.append('%d:%f' % (wlen, val))

                    spec = {'value': ", ".join(contspec), 'type': 'spectrum'}

            else:
                BrlLog('Unknown spectrum type.', type(value), value)

        if not spec:
            spec = {'value': "0.0", 'type': 'spectrum'}

        return spec

    def vector(self, x, y, z):
        #TODO is brlrays is Y up?
        # Blender is Z up but brlrays is Y up, convert the vector
        return {
            'type': 'vector',
            'x': '%f' % x, 'y': '%f' % z, 'z': '%f' % -y
        }

    def point(self, x, y, z):
        # Blender is Z up but brlrays is Y up, convert the point
        return {
            'type': 'point',
            'x': '%f' % x, 'y': '%f' % z, 'z': '%f' % -y
        }

    def transform_lookAt(self, origin, target, up, scale=False):
        # Blender is Z up but brlrays is Y up, convert the lookAt
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
        # Blender is Z up but brlrays is Y up, convert the matrix
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
        BrlLog('Wrote scene files')
        for f in self.files:
            if f is not None:
                f.close()
                BrlLog(' %s' % f.name)

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
    brlrays External Render
    '''

    RENDER_API_TYPE = 'EXT'

    binary_name = 'brlrays'
    render_engine = None
    render_scene = None
    brlrays_process = None
    cmd_args = []
    verbosity_modes = {
        'verbose': '-v',
        'quiet': '-q'
    }

    def __init__(self):
        self.render_engine = BrlManager.RenderEngine
        self.render_scene = BrlManager.CurrentScene

        if self.render_engine.is_preview:
            self.binary_name = 'brlrays'
            verbosity = 'quiet'

        else:
            self.binary_name = self.render_scene.brlrays_engine.binary_name
            verbosity = self.render_scene.brlrays_engine.log_verbosity

        brlrays_path = efutil.filesystem_path(self.render_engine.preferences.install_path)

        if brlrays_path == '':
            return ['']

        if brlrays_path[-1] != '/':
            brlrays_path += '/'

        if sys.platform == 'darwin':
            if os.path.exists(os.path.join(brlrays_path, 'brlrays.app/Contents/MacOS/')):
                brlrays_path = os.path.join(brlrays_path, 'brlrays.app/Contents/MacOS/')

            elif os.path.exists(os.path.join(brlrays_path, 'Contents/MacOS/')):
                brlrays_path = os.path.join(brlrays_path, 'Contents/MacOS/')

            brlrays_path += self.binary_name

            if not os.path.exists(brlrays_path):
                BrlLog('brlrays not found at path: %s' % brlrays_path, ', trying default brlrays location')
                brlrays_path = '/Applications/brlrays.app/Contents/MacOS/%s' % self.binary_name  # try fallback to default installation path

        elif sys.platform == 'win32':
            brlrays_path += '%s.exe' % self.binary_name

        else:
            brlrays_path += self.binary_name

        if not os.path.exists(brlrays_path):
            raise Exception('brlrays not found at path: %s' % brlrays_path)

        self.cmd_args = [brlrays_path]

        # set log verbosity
        if verbosity != 'default':
            self.cmd_args.append(self.verbosity_modes[verbosity])

        # Set number of threads for external processes
        if not self.render_scene.brlrays_engine.threads_auto:
            self.cmd_args.extend(['-p', '%i' % self.render_scene.brlrays_engine.threads])

    def set_scene(self, export_context):
        if export_context.EXPORT_API_TYPE == 'FILE':
            self.filename = export_context.file_names[0]

        else:
            raise Exception('Unknown exporter type')

    def render_start(self, dest_file):
        output_dir, output_file = os.path.split(dest_file)
        self.cmd_args.extend(['-o', dest_file])
        self.cmd_args.append(self.filename)
        BrlLog('Launching: %s' % self.cmd_args)
        self.brlrays_process = subprocess.Popen(self.cmd_args, cwd=output_dir)

    def render_stop(self):
        # Use SIGTERM because that's the only one supported on Windows
        self.brlrays_process.send_signal(subprocess.signal.SIGTERM)

    def test_break(self):
        return self.render_engine.test_break()

    def is_running(self):
        return self.brlrays_process.poll() is None

    def returncode(self):
        return self.brlrays_process.returncode
