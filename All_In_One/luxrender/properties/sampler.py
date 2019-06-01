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
from ..extensions_framework.validate import Logic_OR as O, Logic_AND as A

from .. import LuxRenderAddon
from ..export import ParamSet


@LuxRenderAddon.addon_register_class
class luxrender_sampler(declarative_property_group):
    """
    Storage class for LuxRender Sampler settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        'spacer',
        'sampler',

        'pixelsampler',
        'pixelsamples',

        # 'adaptive_largemutationprob',
        'usecooldown',
        'noiseaware',
        'largemutationprob',  # 'mutationrange',
        'maxconsecrejects',
        'usersamplingmap_filename',
    ]

    visibility = {
        'spacer': {'advanced': True},
        'pixelsampler': {'sampler': O(['lowdiscrepancy', 'random'])},
        'pixelsamples': {'sampler': O(['lowdiscrepancy', 'random'])},
        # 'adaptive_largemutationprob':	{ 'sampler': 'metropolis' },
        'largemutationprob': A([{'sampler': 'metropolis'}, ]),  # { 'adaptive_largemutationprob': False },
        'usecooldown': A([{'advanced': True}, {'sampler': 'metropolis'}, ]),
        # { 'adaptive_largemutationprob': False },
        'maxconsecrejects': A([{'advanced': True}, {'sampler': 'metropolis'}, ]),
        'usersamplingmap_filename': {'advanced': True},
    }

    properties = [
        {
            'type': 'text',
            'attr': 'spacer',
            'name': '',  # This param just draws some blank space in the panel
        },
        {
            'type': 'enum',
            'attr': 'sampler',
            'name': 'Sampler',
            'description': 'Pixel sampling algorithm to use',
            'default': 'metropolis',
            'items': [
                ('metropolis', 'Metropolis', 'Keleman-style metropolis light transport'),
                ('sobol', 'Sobol', 'Use a Sobol sequence'),
                ('lowdiscrepancy', 'Low Discrepancy', 'Use a low discrepancy sequence'),
                ('random', 'Random', 'Completely random sampler')
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'description': 'Configure advanced sampler settings',
            'default': False,
            'save_in_preset': True
        },
        # {
        # 'type': 'bool',
        # 'attr': 'adaptive_largemutationprob',
        # 'name': 'Adaptive Large Mutation Probability',
        # 'description': 'Automatically determine the probability of completely random mutations vs guided ones',
        # 'default': False,
        # 'save_in_preset': True
        # },
        {
            'type': 'float',
            'attr': 'largemutationprob',
            'name': 'Large Mutation Probability',
            'description': 'Probability of a completely random mutation rather than a guided one. Lower values \
            increase sampler strength',
            'default': 0.4,
            'min': 0,
            'max': 1,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'maxconsecrejects',
            'name': 'Max. Consecutive Rejections',
            'description': 'Maximum amount of samples in a particular area before moving on. Setting this too low \
            may mute lamps and caustics',
            'default': 512,
            'min': 128,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'noiseaware',
            'name': 'Noise-Aware Sampling',
            'description': 'Enable noise-guided adaptive sampling',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'usersamplingmap_filename',
            'name': 'User Sampling Map',
            'description': 'Image map to guide sample distribution, none = disabled. Extension is added \
            automatically (.exr)',
            'default': ''
        },
        {
            'type': 'bool',
            'attr': 'usecooldown',
            'name': 'Use Cooldown',
            'description': 'Use fixed large mutation probability at the beginning of the render, to avoid \
            convergence errors with extreme settings',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'mutationrange',
            'name': 'Mutation Range',
            'default': 256,
            'min': 1,
            'max': 32768,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'pixelsampler',
            'name': 'Pixel Sampler',
            'description': 'Pixel sampling strategy',
            'default': 'lowdiscrepancy',
            'items': [
                ('linear', 'Linear', 'Scan top-to-bottom, one pixel line at a time'),
                ('tile', 'Tile', 'Scan in 32x32 blocks'),
                ('vegas', 'Vegas', 'Random sample distribution'),
                ('lowdiscrepancy', 'Low Discrepancy', 'Distribute samples in a standard low discrepancy pattern'),
                ('hilbert', 'Hilbert', 'Scan in a hilbert curve'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'pixelsamples',
            'name': 'Pixel Samples',
            'description': 'Average number of samples taken per pixel. More samples create a higher quality image at \
            the cost of render time',
            'default': 4,
            'min': 1,
            'max': 8192,
            'save_in_preset': True
        },
    ]

    def api_output(self):
        """
        Format this class's members into a LuxRender ParamSet

        Returns tuple
        """

        params = ParamSet()

        if self.sampler in ['random', 'lowdiscrepancy']:
            params.add_integer('pixelsamples', self.pixelsamples)
            params.add_string('pixelsampler', self.pixelsampler)

            # if self.sampler == 'metropolis':
        # params.add_bool('adaptive_largemutationprob', self.adaptive_largemutationprob)
        # if not self.adaptive_largemutationprob:
        # params.add_float('largemutationprob', self.largemutationprob)
        # params.add_bool('usecooldown', self.usecooldown)

        if self.sampler == 'metropolis':
            params.add_float('largemutationprob', self.largemutationprob)

        params.add_bool('noiseaware', self.noiseaware)

        if self.advanced:
            if self.sampler == 'metropolis':
                params.add_integer('maxconsecrejects', self.maxconsecrejects)
                params.add_bool('usecooldown', self.usecooldown)

            if self.usersamplingmap_filename:
                params.add_string('usersamplingmap_filename', self.usersamplingmap_filename)

        return self.sampler, params
