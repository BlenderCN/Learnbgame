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
from ..outputs import LuxLog
from ..outputs.pure_api import LUXRENDER_VERSION


class Custom_Context(object):
    """
    Imitate the real pylux Context object so that we can
    write materials to LBM2 files using the same API
    """

    API_TYPE = 'FILE'

    context_name = ''
    output_file = None

    def __init__(self, name):
        self.context_name = name

    def open(self, filename):
        self.output_file = open(filename, 'w')
        self.output_file.write('# LXM File saved by LuxBlend25\n')

    def close(self):
        if self.output_file is not None:
            self.output_file.close()

    def getRenderingServersStatus(self):
        return []

    def wf(self, st, tabs=0):
        self.output_file.write('%s%s\n' % ('\t' * tabs, st))
        self.output_file.flush()

    def set_output_file(self, file):
        pass

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

        # name is a string, and params a list
        name, params = args
        self.wf('\n%s "%s"' % (identifier, name))

        for p in params:
            self.wf(p.to_string(), 1)

    # Wrapped pylux.Context API calls follow ...

    def objectBegin(self, name, file=None):
        self._api('ObjectBegin ', [name, []], file=file)

    def objectEnd(self, comment=''):
        self._api('ObjectEnd # ', [comment, []])

    def objectInstance(self, name):
        self._api('ObjectInstance ', [name, []])

    def portalInstance(self, name):
        # Backwards compatibility
        if LUXRENDER_VERSION < '0.8':
            LuxLog('WARNING: Exporting PortalInstance as ObjectInstance; Portal will not be effective')
            self._api('ObjectInstance ', [name, []])
        else:
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
        self.wf('\nLookAt %s' % ' '.join(['%f' % i for i in args]))

    def coordinateSystem(self, name):
        self._api('CoordinateSystem', [name, []])

    def identity(self):
        self._api('Identity #', ['', []])

    def camera(self, *args):
        self._api('Camera', args)

    def film(self, *args):
        self._api('Film', args)

    def worldBegin(self, *args):
        self.wf('\nWorldBegin')

    def lightGroup(self, *args):
        self._api('LightGroup', args)

    def lightSource(self, *args):
        self._api('LightSource', args)

    def areaLightSource(self, *args):
        self._api('AreaLightSource', args)

    def motionInstance(self, name, start, stop, motion_name):
        self.wf('\nMotionInstance "%s" %f %f "%s"' % (name, start, stop, motion_name))

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
        self.wf('\nMotionBegin [%s]' % ' '.join(['%0.15f' % i for i in time_values]))

    def motionEnd(self):
        self.wf('\nMotionEnd')

    def concatTransform(self, values):
        self.wf('\nConcatTransform [%s]' % ' '.join(['%0.15f' % i for i in values]))

    def transform(self, values):
        self.wf('\nTransform [%s]' % ' '.join(['%0.15f' % i for i in values]))

    def scale(self, x, y, z):
        self.wf('\nScale %s' % ' '.join(['%0.15f' % i for i in [x, y, z]]))

    def rotate(self, a, x, y, z):
        self.wf('\nRotate %s' % ' '.join(['%0.15f' % i for i in [a, x, y, z]]))

    def shape(self, *args):
        self._api('Shape', args, file=self.current_file)

    def portalShape(self, *args):
        self._api('PortalShape', args, file=self.current_file)

    def material(self, *args):
        self._api('Material', args)

    def namedMaterial(self, name):
        self._api('NamedMaterial', [name, []])

    def makeNamedMaterial(self, name, params):
        self.wf('\nMakeNamedMaterial "%s"' % name)
        for p in params:
            self.wf(p.to_string(), 1)

    def makeNamedVolume(self, name, type, params):
        self.wf('\nMakeNamedVolume "%s" "%s"' % (name, type))
        for p in params:
            self.wf(p.to_string(), 1)

    def interior(self, name):
        self._api('Interior ', [name, []])

    def exterior(self, name):
        self._api('Exterior ', [name, []])

    def volume(self, type, params):
        self.wf('\nVolume "%s"' % type)
        for p in params:
            self.wf(p.to_string(), 1)

    def texture(self, name, type, texture, params):
        self.wf('\nTexture "%s" "%s" "%s"' % (name, type, texture))
        for p in params:
            self.wf(p.to_string(), 1)

    def worldEnd(self):
        self.wf('WorldEnd')

    def cleanup(self):
        self.exit()

    def exit(self):
        self.close()

    def wait(self):
        pass
