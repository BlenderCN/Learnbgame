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
from ..extensions_framework import declarative_property_group

from .. import LuxRenderAddon
from ..export import ParamSet


@LuxRenderAddon.addon_register_class
class luxrender_filter(declarative_property_group):
    """
    Storage class for LuxRender PixelFilter settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        'spacer',
        'filter',

        'filter_width',
        'sharpness',

        ['xwidth', 'ywidth'],
        'alpha',
        ['b', 'c'],
        'supersample',
        'tau'
    ]

    visibility = {
        'spacer': {'advanced': True},
        'filter_width': {'advanced': False},
        'sharpness': {'advanced': False, 'filter': 'mitchell'},
        'xwidth': {'advanced': True},
        'ywidth': {'advanced': True},
        'alpha': {'advanced': True, 'filter': 'gaussian'},
        'b': {'advanced': True, 'filter': 'mitchell'},
        'c': {'advanced': True, 'filter': 'mitchell'},
        'supersample': {'advanced': True, 'filter': 'mitchell'},
        'tau': {'advanced': True, 'filter': 'sinc'},
    }

    properties = [
        {
            'type': 'text',
            'attr': 'spacer',
            'name': '',  # This param just draws some blank space in the panel
        },
        {
            'type': 'enum',
            'attr': 'filter',
            'name': 'Filter',
            'description': 'Pixel splatting filter',
            'default': 'blackmanharris',
            'items': [
                ('box', 'Box', 'Box filter'),
                ('gaussian', 'Gaussian', 'Gaussian filter'),
                ('mitchell', 'Mitchell', 'Mitchell-Netravali filter'),
                ('sinc', 'Sinc', 'Sinc filter'),
                ('triangle', 'Triangle', 'Triangle filter'),
                ('catmullrom', 'Catmull-Rom', 'Catmull-Rom filter'),
                ('blackmanharris', 'Blackman-Harris', 'Blackman-Harris filter'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'description': 'Configure advanced filter settings',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'filter_width',
            'name': 'Filter Width',
            'description': 'Width of pixel filter curve. Higher values are smoother and more blurred',
            'default': 2.0,
            'min': 0.5,
            'soft_min': 0.5,
            'max': 10.0,
            'soft_max': 4.0,
            'save_in_preset': True
        },
        # The values for sharpness are not actually tied to the values of B/C, they are completely independent controls!
        {
            'type': 'float',
            'attr': 'sharpness',
            'name': 'Sharpness',
            'description': 'Sets the sharpness of the the Mitchell filter B/C coefficients. Increased sharpness may \
            increase ringing/edge artifacts',
            'default': 1 / 3,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'xwidth',
            'name': 'X Width',
            'description': 'Width of filter in X dimension',
            'default': 3.3,
            'min': 0.5,
            'soft_min': 0.5,
            'max': 10.0,
            'soft_max': 4.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'ywidth',
            'name': 'Y Width',
            'description': 'Width of filter in Y dimension',
            'default': 3.3,
            'min': 0.5,
            'soft_min': 0.5,
            'max': 10.0,
            'soft_max': 4.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'alpha',
            'name': 'Alpha',
            'description': 'Gaussian Alpha parameter',
            'default': 2.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'b',
            'name': 'B',
            'description': 'Mitchell B parameter',
            'default': 1 / 3,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'c',
            'name': 'C',
            'description': 'Mitchell C parameter',
            'default': 1 / 3,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'supersample',
            'name': 'Supersample',
            'description': 'Use filter super-sampling, disabling this is NOT recommended',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'tau',
            'name': 'Tau',
            'description': 'Sinc Tau parameter',
            'default': 3.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'save_in_preset': True
        },
    ]

    def api_output(self):
        """
        Format this class's members into a LuxRender ParamSet

        Returns tuple
        """

        params = ParamSet()

        if self.filter == 'mitchell':

            # See LuxBlend_01.py lines ~3895
            # Always use supersample if advanced filter options are hidden
            if not self.advanced:
                B = C = self.sharpness

                params.add_bool('supersample', True)
                params.add_float('B', B)
                params.add_float('C', C)
            else:
                params.add_bool('supersample', self.supersample)
                params.add_float('B', self.b)
                params.add_float('C', self.c)

        if not self.advanced:
            params.add_float('xwidth', self.filter_width)
            params.add_float('ywidth', self.filter_width)

        if self.advanced:
            params.add_float('xwidth', self.xwidth)
            params.add_float('ywidth', self.ywidth)

            if self.filter == 'gaussian':
                params.add_float('alpha', self.alpha)

            if self.filter == 'sinc':
                params.add_float('tau', self.tau)

        return self.filter, params
