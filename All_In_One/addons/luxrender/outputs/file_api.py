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

import bpy

from ..extensions_framework import util as efutil

from ..outputs import LuxLog
from ..outputs.pure_api import LUXRENDER_VERSION
from ..properties import ExportedVolumes


class Files(object):
    MAIN = 0
    MATS = 1
    GEOM = 2
    VOLM = 3


class RenderingServerInfo(object):
    """
    Emulate pylux.RenderingServerInfo
    """
    name = None
    port = None
    secsSinceLastContact = None
    serverIndex = None
    sid = None

    def __init__(self, name):
        self.name = name


class Custom_Context(object):
    """
    Imitate the real pylux Context object so that we can
    write to files using the same API
    """

    API_TYPE = 'FILE'

    context_name = ''
    files = []
    file_names = []
    current_file = Files.MAIN
    parse_at_worldend = True

    def __init__(self, name):
        self.context_name = name
        self.has_volumes_file = False

    def wf(self, ind, st, tabs=0):
        """
        ind					int
        st					string
        tabs				int

        Write a string followed by newline to file index ind.
        Optionally indent the string by a number of tabs

        Returns None
        """

        if len(self.files) == 0:
            scene = object()
            scene.name = 'untitled'
            scene.frame_current = 1
            self.set_filename(scene, 'default')

        # Prevent trying to write to a file that isn't open
        if self.files[ind] is None:
            ind = 0

        self.files[ind].write('%s%s\n' % ('\t' * tabs, st))
        self.files[ind].flush()

    def set_filename(self, scene, name, LXV=True):
        """
        name				string

        Open the main, materials, and geometry files for output,
        using filenames based on the given name.

        Returns None
        """

        # If any files happen to be open, close them and start again
        for f in self.files:
            if f is not None:
                f.close()

        self.files = []
        self.file_names = []

        self.file_names.append('%s.lxs' % name)
        self.files.append(open(self.file_names[Files.MAIN], 'w'))
        self.wf(Files.MAIN, '# Main Scene File')

        subdir = '%s%s/%s/%05d' % (efutil.export_path, efutil.scene_filename(), bpy.path.clean_name(scene.name),
                                   scene.frame_current)

        if not os.path.exists(subdir):
            os.makedirs(subdir)

        self.file_names.append('%s/LuxRender-Materials.lxm' % subdir)
        self.files.append(open(self.file_names[Files.MATS], 'w'))
        self.wf(Files.MATS, '# Materials File')

        self.file_names.append('%s/LuxRender-Geometry.lxo' % subdir)
        self.files.append(open(self.file_names[Files.GEOM], 'w'))
        self.wf(Files.GEOM, '# Geometry File')

        self.files.append(None)

        self.set_output_file(Files.MAIN)

    def set_output_file(self, file):
        """
        file				int

        Switch next output to the given file index

        Returns None
        """

        self.current_file = file

    def _api(self, identifier, args=[], file=None):
        """
        identifier			string
        args				list
        file				None or int

        Make a standard pylux.Context API call. In this case
        the identifier followed by its name followed by its
        formatted parameters are written to either the current
        output file, or the file specified by the given index.

        Returns None
        """

        if file is not None:
            self.set_output_file(file)

        # name is a string, and params a list
        name, params = args
        self.wf(self.current_file, '\n%s "%s"' % (identifier, name))
        for p in params:
            self.wf(self.current_file, p.to_string(), 1)

    # Wrapped pylux.Context API calls follow ...

    def objectBegin(self, name, file=None):
        self._api('ObjectBegin ', [name, []], file=file)

    def objectEnd(self, comment=''):
        self._api('ObjectEnd # ', [comment, []])

    def objectInstance(self, name):
        self._api('ObjectInstance ', [name, []])

    def portalInstance(self, name):
        self._api('PortalInstance ', [name, []])

    def renderer(self, *args):
        self._api('Renderer', args)

    def sampler(self, *args):
        self._api('Sampler', args)

    def accelerator(self, *args):
        self._api('Accelerator', args)

    def surfaceIntegrator(self, *args):
        self._api('SurfaceIntegrator', args)

    def volumeIntegrator(self, *args):
        self._api('VolumeIntegrator', args)

    def pixelFilter(self, *args):
        self._api('PixelFilter', args)

    def lookAt(self, *args):
        self.wf(Files.MAIN, '\nLookAt %s' % ' '.join(['%f' % i for i in args]))

    def coordinateSystem(self, name):
        self._api('CoordinateSystem', [name, []])

    def identity(self):
        self._api('Identity #', ['', []])

    def camera(self, *args):
        self._api('Camera', args)

    def film(self, *args):
        self._api('Film', args)

    def worldBegin(self, *args):
        self.wf(Files.MAIN, '\nWorldBegin')

        if self.files[Files.MAIN] is not None:
            # Include the other files if they exist

            for idx in [Files.MATS, Files.GEOM, Files.VOLM]:
                if idx < len(self.file_names) and os.path.exists(self.file_names[idx]):
                    self.wf(Files.MAIN, '\nInclude "%s"' % efutil.path_relative_to_export(self.file_names[idx]))

    def lightGroup(self, *args):
        if args[0] != '':
            self._api('LightGroup', args)

    def lightSource(self, *args):
        self._api('LightSource', args)

    def areaLightSource(self, *args):
        self._api('AreaLightSource', args)

    def motionInstance(self, name, start, stop, motion_name):
        self.wf(self.current_file, '\nMotionInstance "%s" %f %f "%s"' % (name, start, stop, motion_name))

    def attributeBegin(self, comment='', file=None):
        """
        comment				string
        file				None or int

        The AttributeBegin block can be used to switch
        the current output file, seeing as we will probably
        be exporting LightSources to the LXS and other
        geometry to LXO.
        """

        self._api('AttributeBegin # ', [comment, []], file=file)

    def attributeEnd(self):
        self._api('AttributeEnd #', ['', []])

    def transformBegin(self, comment='', file=None):
        """
        comment				string
        file				None or int

        See attributeBegin
        """

        self._api('TransformBegin # ', [comment, []], file=file)

    def transformEnd(self):
        self._api('TransformEnd #', ['', []])

    def motionBegin(self, time_values):
        self.wf(self.current_file, '\nMotionBegin [%s]' % ' '.join(['%0.15f' % i for i in time_values]))

    def motionEnd(self):
        self.wf(self.current_file, '\nMotionEnd')

    def concatTransform(self, values):
        self.wf(self.current_file, '\nConcatTransform [%s]' % ' '.join(['%0.15f' % i for i in values]))

    def transform(self, values):
        self.wf(self.current_file, '\nTransform [%s]' % ' '.join(['%0.15f' % i for i in values]))

    def scale(self, x, y, z):
        self.wf(self.current_file, '\nScale %s' % ' '.join(['%0.15f' % i for i in [x, y, z]]))

    def rotate(self, a, x, y, z):
        self.wf(self.current_file, '\nRotate %s' % ' '.join(['%0.15f' % i for i in [a, x, y, z]]))

    def shape(self, *args):
        self._api('Shape', args, file=self.current_file)

    def portalShape(self, *args):
        self._api('PortalShape', args, file=self.current_file)

    def material(self, *args):
        self._api('Material', args)

    def namedMaterial(self, name):
        self._api('NamedMaterial', [name, []])

    def makeNamedMaterial(self, name, params):
        self.wf(Files.MATS, '\nMakeNamedMaterial "%s"' % name)

        for p in params:
            self.wf(Files.MATS, p.to_string(), 1)

    def makeNamedVolume(self, name, type, params):
        self.wf(Files.MATS, '\nMakeNamedVolume "%s" "%s"' % (name, type))

        for p in params:
            self.wf(Files.MATS, p.to_string(), 1)

    def interior(self, name):
        self._api('Interior ', [name, []])

    def exterior(self, name):
        self._api('Exterior ', [name, []])

    def volume(self, type, params):
        if not self.has_volumes_file:
            self.file_names.append('%s/LuxRender-Volumes.lxv' % subdir)
            self.files.insert(-1, open(self.file_names[Files.VOLM], 'w'))
            self.wf(Files.VOLM, '# Volume File')
            self.has_volumes_file = True

        self.wf(Files.VOLM, '\nVolume "%s"' % type)

        for p in params:
            self.wf(Files.VOLM, p.to_string(), 1)

    def texture(self, name, type, texture, params):
        self.wf(Files.MATS, '\nTexture "%s" "%s" "%s"' % (name, type, texture))

        for p in params:
            self.wf(Files.MATS, p.to_string(), 1)

    def worldEnd(self):
        """
        Special handling of worldEnd API.
        See inline comments for further info
        """

        if self.files[Files.MAIN] is not None:
            # End of the world as we know it
            self.wf(Files.MAIN, 'WorldEnd')

        # Close files
        LuxLog('Wrote scene files')
        for f in self.files:
            if f is not None:
                f.close()
                LuxLog(' %s' % f.name)

        # Reset the volume redundancy check
        ExportedVolumes.reset_vol_list()

    def cleanup(self):
        self.exit()

    def exit(self):
        # If any files happen to be open, close them and start again
        for f in self.files:
            if f is not None:
                f.close()

    def wait(self):
        pass

    # Emulate networking options to pass to real pylux context in parse()

    use_network_servers = False
    serverinterval = 180
    servers = []

    def setNetworkServerUpdateInterval(self, int):
        self.serverinterval = int

    def addServer(self, name):
        self.use_network_servers = True
        self.servers.append(name)

    def getRenderingServersStatus(self):
        return [RenderingServerInfo(name) for name in self.servers]

    def removeServer(self, s):
        self.servers.remove(s)

    def parse(self, filename, async):
        """
        In a deviation from the API, this function returns a new context,
        which must be passed back to LuxManager so that it can control the
        rendering process.
        """
        from ..outputs.pure_api import PYLUX_AVAILABLE

        if PYLUX_AVAILABLE:
            from ..outputs.pure_api import Custom_Context as Pylux_Context

            c = Pylux_Context(self.context_name)

            # propagate networking settings
            if self.use_network_servers:
                c.setNetworkServerUpdateInterval(self.serverinterval)

                for s in self.servers:
                    c.addServer(s)

            c.parse(filename, async)

            self.PYLUX = c.PYLUX

            return c
        else:
            raise Exception('This method requires pylux')
