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
from ..extensions_framework.validate import Logic_OR as O, Logic_Operator as LO

from .. import LuxRenderAddon
from ..export import ParamSet
from ..outputs import LuxLog
from ..outputs.pure_api import LUXRENDER_VERSION
# from .engine import check_renderer_settings

@LuxRenderAddon.addon_register_class
class luxrender_volumeintegrator(declarative_property_group):
    """
    Storage class for LuxRender Volume Integrator settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        'spacer',
        'volumeintegrator',
        'stepsize',
    ]

    visibility = {
        'spacer': {'advanced': True},
        'stepsize': {'advanced': True},
    }

    properties = [
        {
            'type': 'text',
            'attr': 'spacer',
            'name': '',  # This param just draws some blank space in the panel
        },
        {
            'type': 'enum',
            'attr': 'volumeintegrator',
            'name': 'Volume Integrator',
            'description': 'Integrator used to calculate volumetric effects',
            'default': 'multi',
            'items': [
                ('emission', 'Emission', 'Calculate volumetric absorption'),
                ('single', 'Single', 'Calculate single scattering and absorption'),
                ('multi', 'Multi', 'Calculate all volumetric effects, including multiple scattering and absorption'),
                ('none', 'None', 'Experimental/Debugging integrator, does not calculate any scattering effects'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'description': 'Configure advanced volume integrator settings',
            'default': False,
            'save_in_preset': True
        },
    ]

    def api_output(self):
        """
        Format this class's members into a LuxRender ParamSet

        Returns dict
        """

        params = ParamSet()

        return self.volumeintegrator, params


@LuxRenderAddon.addon_register_class
class luxrender_integrator(declarative_property_group):
    """
    Storage class for LuxRender SurfaceIntegrator settings.
    """

    ef_attach_to = ['Scene']

    def advanced_switch(self, context):
        context.scene.luxrender_sampler.advanced = self.advanced
        context.scene.luxrender_volumeintegrator.advanced = self.advanced
        context.scene.luxrender_filter.advanced = self.advanced
        context.scene.luxrender_accelerator.advanced = self.advanced

    controls = [
        'advanced',

        'lightstrategy',  # bidir +
        'lightpathstrategy',
        ['eyedepth', 'lightdepth'],
        ['eyerrthreshold', 'lightrrthreshold'],
        'lightraycount',  # dl +
        'maxdepth',  # dp
        ['lbl_direct',
         'directsamples'],
        ['directsampleall',
         'directdiffuse',
         'directglossy'],
        ['lbl_indirect',
         'indirectsamples'],
        ['indirectsampleall',
         'indirectdiffuse',
         'indirectglossy'],
        'lbl_diffuse',
        ['diffusereflectsamples',
         'diffusereflectdepth'],
        ['diffuserefractsamples',
         'diffuserefractdepth'],
        'lbl_glossy',
        ['glossyreflectsamples',
         'glossyreflectdepth'],
        ['glossyrefractsamples',
         'glossyrefractdepth'],
        'lbl_specular',
        ['specularreflectdepth',
         'specularrefractdepth'],
        'lbl_rejection',
        ['diffusereflectreject',
         'diffusereflectreject_threshold'],
        ['diffuserefractreject',
         'diffuserefractreject_threshold'],
        ['glossyreflectreject',
         'glossyreflectreject_threshold'],
        ['glossyrefractreject',
         'glossyrefractreject_threshold'],  # epm
        ['maxeyedepth', 'maxphotondepth'],
        # Exphotonmap uses maxdepth, not maxeyedepth. However, it uses maxeyedepth in the GUI
        # to allow a double-box for both itself and SPPM. This is because maxdepth cannot be used in a double box,
        # since path, igi, and direct use maxdepth by itself. The value of maxeyedepth is exported for the "maxdepth"
        # entry in the lxs when using exphotonmap, see export section
        'directphotons',
        'causticphotons',
        'indirectphotons',
        'radiancephotons',
        'nphotonsused',
        'maxphotondist',
        'renderingmode',
        'finalgather',
        'finalgathersamples',
        'gatherangle',
        'distancethreshold',
        'rrstrategy',
        'rrcontinueprob',  # epm advanced
        'photonmapsfile',  # epm debug
        'debugmode',
        'dbg_enabledirect',
        'dbg_enableradiancemap',
        'dbg_enableindircaustic',
        'dbg_enableindirdiffuse',
        'dbg_enableindirspecular',  # igi
        'nsets',
        'nlights',
        'mindist',  #sppm
        ['hitpointperpass', 'photonperpass'],
        ['startradius', 'alpha'],
        ['directlightsampling', 'includeenvironment'],  #sppm advanced
        'storeglossy',
        'wavelengthstratificationpasses',
        'lookupaccel',
        'parallelhashgridspare',
        'pixelsampler',
        'photonsampler',
        'useproba',  # path + bidir
        'shadowraycount',
    ]

    visibility = {  # bidir +
                    'eyedepth': {'surfaceintegrator': 'bidirectional'},
                    'lightdepth': {'surfaceintegrator': 'bidirectional'},
                    'lightpathstrategy': {'advanced': True, 'surfaceintegrator': 'bidirectional'},
                    'eyerrthreshold': {'advanced': True, 'surfaceintegrator': 'bidirectional'},
                    'lightrrthreshold': {'advanced': True, 'surfaceintegrator': 'bidirectional'},
                    'lightstrategy': {'surfaceintegrator': O(
                        ['directlighting', 'exphotonmap', 'igi', 'path', 'distributedpath', 'bidirectional'])},
                    'lightraycount': {'surfaceintegrator': 'bidirectional'},  # dl +
                    'maxdepth': {'surfaceintegrator': O(['directlighting', 'igi', 'path'])},
                    'shadowraycount': {'advanced': True, 'surfaceintegrator': O(
                        ['exphotonmap', 'directlighting', 'bidirectional', 'path'])},  # dp
                    'lbl_direct': {'surfaceintegrator': 'distributedpath'},
                    'directsampleall': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'directsamples': {'surfaceintegrator': 'distributedpath'},
                    'directdiffuse': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'directglossy': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'lbl_indirect': {'surfaceintegrator': 'distributedpath'},
                    'indirectsampleall': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'indirectsamples': {'surfaceintegrator': 'distributedpath'},
                    'indirectdiffuse': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'indirectglossy': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'lbl_diffuse': {'surfaceintegrator': 'distributedpath'},
                    'diffusereflectdepth': {'surfaceintegrator': 'distributedpath'},
                    'diffusereflectsamples': {'surfaceintegrator': 'distributedpath'},
                    'diffuserefractdepth': {'surfaceintegrator': 'distributedpath'},
                    'diffuserefractsamples': {'surfaceintegrator': 'distributedpath'},
                    'lbl_glossy': {'surfaceintegrator': 'distributedpath'},
                    'glossyreflectdepth': {'surfaceintegrator': 'distributedpath'},
                    'glossyreflectsamples': {'surfaceintegrator': 'distributedpath'},
                    'glossyrefractdepth': {'surfaceintegrator': 'distributedpath'},
                    'glossyrefractsamples': {'surfaceintegrator': 'distributedpath'},
                    'lbl_specular': {'surfaceintegrator': 'distributedpath'},
                    'specularreflectdepth': {'surfaceintegrator': 'distributedpath'},
                    'specularrefractdepth': {'surfaceintegrator': 'distributedpath'},
                    'lbl_rejection': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'diffusereflectreject': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'diffusereflectreject_threshold': {'advanced': True, 'diffusereflectreject': True,
                                                       'surfaceintegrator': 'distributedpath'},
                    'diffuserefractreject': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'diffuserefractreject_threshold': {'advanced': True, 'diffuserefractreject': True,
                                                       'surfaceintegrator': 'distributedpath'},
                    'glossyreflectreject': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'glossyreflectreject_threshold': {'advanced': True, 'glossyreflectreject': True,
                                                      'surfaceintegrator': 'distributedpath'},
                    'glossyrefractreject': {'advanced': True, 'surfaceintegrator': 'distributedpath'},
                    'glossyrefractreject_threshold': {'advanced': True, 'glossyrefractreject': True,
                                                      'surfaceintegrator': 'distributedpath'},  # expm
                    'maxeyedepth': {'surfaceintegrator': O(['exphotonmap', 'sppm'])},
                    'maxphotondepth': {'surfaceintegrator': O(['exphotonmap', 'sppm'])},
                    'directphotons': {'surfaceintegrator': 'exphotonmap'},
                    'causticphotons': {'surfaceintegrator': 'exphotonmap'},
                    'indirectphotons': {'surfaceintegrator': 'exphotonmap'},
                    'radiancephotons': {'surfaceintegrator': 'exphotonmap'},
                    'nphotonsused': {'surfaceintegrator': 'exphotonmap'},
                    'maxphotondist': {'surfaceintegrator': 'exphotonmap'},
                    'renderingmode': {'surfaceintegrator': 'exphotonmap'},
                    'finalgather': {'renderingmode': 'directlighting', 'surfaceintegrator': 'exphotonmap'},
                    'finalgathersamples': {'finalgather': True, 'renderingmode': 'directlighting',
                                           'surfaceintegrator': 'exphotonmap'},
                    'gatherangle': {'finalgather': True, 'renderingmode': 'directlighting',
                                    'surfaceintegrator': 'exphotonmap'},
                    'rrstrategy': {'surfaceintegrator': O(['exphotonmap', 'path'])},
                    'rrcontinueprob': {'rrstrategy': 'probability', 'surfaceintegrator': O(['exphotonmap', 'path'])},
                    'distancethreshold': {'renderingmode': 'path', 'surfaceintegrator': 'exphotonmap'},  # expm advanced
                    'photonmapsfile': {'advanced': True, 'surfaceintegrator': 'exphotonmap'},  # expm debug
                    'debugmode': {'surfaceintegrator': 'exphotonmap'},
                    'dbg_enabledirect': {'debugmode': True, 'surfaceintegrator': 'exphotonmap'},
                    'dbg_enableradiancemap': {'debugmode': True, 'surfaceintegrator': 'exphotonmap'},
                    'dbg_enableindircaustic': {'debugmode': True, 'surfaceintegrator': 'exphotonmap'},
                    'dbg_enableindirdiffuse': {'debugmode': True, 'surfaceintegrator': 'exphotonmap'},
                    'dbg_enableindirspecular': {'debugmode': True, 'surfaceintegrator': 'exphotonmap'},  # igi
                    'nsets': {'surfaceintegrator': 'igi'},
                    'nlights': {'surfaceintegrator': 'igi'},
                    'mindist': {'surfaceintegrator': 'igi'},  # path
                    'includeenvironment': {'surfaceintegrator': O(['sppm', 'path'])},
                    'directlightsampling': {'surfaceintegrator': O(['sppm', 'path'])},  # sppm
                    'photonperpass': {'surfaceintegrator': 'sppm'},
                    'hitpointperpass': {'surfaceintegrator': 'sppm'},
                    'startk': {'surfaceintegrator': 'sppm'},
                    'alpha': {'surfaceintegrator': 'sppm'},
                    'startradius': {'surfaceintegrator': 'sppm'},  # sppm advanced
                    'storeglossy': {'advanced': True, 'surfaceintegrator': 'sppm'},
                    'wavelengthstratificationpasses': {'advanced': True, 'surfaceintegrator': 'sppm'},
                    'lookupaccel': {'advanced': True, 'surfaceintegrator': 'sppm'},
                    'parallelhashgridspare': {'advanced': True, 'lookupaccel': 'parallelhashgrid',
                                              'surfaceintegrator': 'sppm'},
                    'pixelsampler': {'advanced': True, 'surfaceintegrator': 'sppm'},
                    'photonsampler': {'advanced': True, 'surfaceintegrator': 'sppm'},
                    'useproba': {'advanced': True, 'surfaceintegrator': 'sppm'},
    }

    alert = {}

    properties = [
        # This parameter is fed to the "integrator' context, and holds the actual surface integrator setting.
        # The user does not interact with it directly, and it does not appear in the UI.
        # It is set via the Rendering Mode menu and update_rendering_mode function
        {
            'type': 'enum',
            'attr': 'surfaceintegrator',
            'name': 'Surface Integrator',
            'description': 'Surface Integrator',
            'default': 'bidirectional',
            'items': [
                ('bidirectional', 'Bidirectional', 'bidirectional'),
                ('path', 'Path', 'path'),
                ('directlighting', 'Direct Lighting', 'directlighting'),
                ('distributedpath', 'Distributed Path', 'distributedpath'),
                ('igi', 'Instant Global Illumination', 'igi',),
                ('exphotonmap', 'Ex-Photon Map', 'exphotonmap'),
                ('sppm', 'SPPM', 'sppm'),
            ],  # 'update': lambda s,c: check_renderer_settings(c),
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'description': 'Configure advanced render settings',
            'update': advanced_switch,
            'default': False,  # 'update': lambda s,c: check_renderer_settings(c),
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'lightstrategy',
            'name': 'Light Strategy',
            'description': 'Light sampling strategy',
            'default': 'auto',
            'items': [
                ('auto', 'Auto',
                 'Automatically choose between One-Uniform or All-Uniform depending on the number of lights'),
                ('one', 'One Uniform', 'Each ray samples a single lamp, chosen at random'),
                ('all', 'All Uniform', 'Each ray samples all lamps'),
                ('importance', 'Importance', 'Each ray samples a single lamp chosen by importance value'),
                ('powerimp', 'Power', 'Each ray samples a single lamp, chosen by importance value and output power'),
                ('allpowerimp', 'All Power',
                 'Each ray starts a number of samples equal to the number of lamps, and distributes them according to \
                 importance and output power'),
                ('autopowerimp', 'Auto Power',
                 'Automatically choose between Power and All-Power depending on the number of lights'),
                ('logpowerimp', 'Log Power',
                 'Each ray samples a single lamp, chosen by importance value and logarithmic output power')
            ],  # 'update': lambda s,c: check_renderer_settings(c),
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'eyedepth',
            'name': 'Max Eye Depth',
            'description': 'Max recursion depth for ray casting from eye',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'lightdepth',
            'name': 'Max Light Depth',
            'description': 'Max recursion depth for ray casting from light',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'eyerrthreshold',
            'name': 'Eye RR Threshold',
            'default': 0.0,
            'min': 0.0,
            'max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'lightrrthreshold',
            'name': 'Light RR Threshold',
            'default': 0.0,
            'min': 0.0,
            'max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'maxdepth',
            'name': 'Max. Depth',
            'description': 'Max recursion depth for ray casting from eye',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'lightpathstrategy',
            'name': 'Light Path Strategy',
            'description': 'Strategy for choosing which lamp(s) to start light paths from',
            'default': 'auto',
            'items': [
                ('auto', 'Auto',
                 'Automatically choose between One-Uniform or All-Uniform depending on the number of lights'),
                ('one', 'One Uniform', 'A light path is started from a single lamp, chosen at random'),
                ('all', 'All Uniform', 'All lamps start a light path (this can be slow)'),
                ('importance', 'Importance', 'A single light path is started from a lamp chosen by importance value'),
                ('powerimp', 'Power',
                 'A single light path is started from a lamp chosen by importance value and output power'),
                ('allpowerimp', 'All Power',
                 'Starts a number of light paths equal to the number of lamps, the paths will be launched from lamps \
                 chosen by importance value and output power'),
                ('autopowerimp', 'Auto Power',
                 'Automatically choose between Power and All-Power depending on the number of lights'),
                ('logpowerimp', 'Log Power',
                 'A single light path is started from a lamp chosen by importance value and logarithmic output power')
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'shadowraycount',
            'name': 'Shadow Ray Count',
            'description': 'Multiplier for the number of shadow rays traced: higher values are slower overall, but can \
            speed convergence of direct light and soft shadows',
            'default': 1,
            'min': 1,
            'max': 1024,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'lightraycount',
            'name': 'Light Ray Count',
            'description': 'Multiplier for the number of light paths traced: higher values can speed convergence of \
            indirect light and caustics at the expense of reflections and refractions',
            'default': 1,
            'min': 1,
            'max': 1024,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'lbl_direct',
            'name': 'Direct light sampling',
        },
        {
            'type': 'bool',
            'attr': 'directsampleall',
            'name': 'Sample All',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'directsamples',
            'name': 'Samples',
            'default': 1,
            'description': 'Number of shadow rays to start from first path vertex',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'directdiffuse',
            'name': 'Diffuse',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'directglossy',
            'name': 'Glossy',
            'default': True,
            'save_in_preset': True
        },

        {
            'type': 'text',
            'attr': 'lbl_indirect',
            'name': 'Indirect light sampling',
        },
        {
            'type': 'bool',
            'attr': 'indirectsampleall',
            'name': 'Sample All',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'indirectsamples',
            'name': 'Samples',
            'default': 1,
            'description': 'Number of shadows rays to start from subsequent path vertices',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'indirectdiffuse',
            'name': 'Diffuse',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'indirectglossy',
            'name': 'Glossy',
            'default': True,
            'save_in_preset': True
        },

        {
            'type': 'text',
            'attr': 'lbl_diffuse',
            'name': 'Diffuse Settings',
        },
        {
            'type': 'int',
            'attr': 'diffusereflectdepth',
            'name': 'Reflection Depth',
            'description': 'Max recursion depth after bouncing from a diffuse surface',
            'default': 3,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'diffusereflectsamples',
            'name': 'Reflection Samples',
            'description': 'Number of paths to start from a diffuse surface',
            'default': 1,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'diffuserefractdepth',
            'name': 'Refraction Depth',
            'description': 'Max recursion depth after bouncing through a translucent surface',
            'default': 5,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'diffuserefractsamples',
            'name': 'Refraction Samples',
            'description': 'Number of paths to start from a translucent surface',
            'default': 1,
            'min': 0,
            'save_in_preset': True
        },

        {
            'type': 'text',
            'attr': 'lbl_glossy',
            'name': 'Glossy Settings',
        },
        {
            'type': 'int',
            'attr': 'glossyreflectdepth',
            'name': 'Reflection Depth',
            'description': 'Max recursion depth after bouncing from a glossy surface',
            'default': 2,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'glossyreflectsamples',
            'name': 'Reflection Samples',
            'description': 'Number of paths to start from a glossy surface',
            'default': 1,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'glossyrefractdepth',
            'name': 'Refraction Depth',
            'description': 'Max recursion depth after bouncing through a glossy-refraction surface, such as \
            rough glass',
            'default': 5,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'glossyrefractsamples',
            'name': 'Refraction Samples',
            'description': 'Number of paths to start from a glossy-refraction surface, such as rough glass',
            'default': 1,
            'min': 0,
            'save_in_preset': True
        },

        {
            'type': 'text',
            'attr': 'lbl_specular',
            'name': 'Specular Settings',
        },
        {
            'type': 'int',
            'attr': 'specularreflectdepth',
            'name': 'Reflection Depth',
            'description': 'Max recursion depth after a specular reflection',
            'default': 3,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'specularrefractdepth',
            'name': 'Refraction Depth',
            'description': 'Max recursion depth after a specular transmission, such as glass or null',
            'default': 5,
            'min': 0,
            'save_in_preset': True
        },

        {
            'type': 'text',
            'attr': 'lbl_rejection',
            'name': 'Rejection settings',
        },
        {
            'type': 'bool',
            'attr': 'diffusereflectreject',
            'name': 'Diffuse reflection reject',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'diffusereflectreject_threshold',
            'name': 'Threshold',
            'default': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'diffuserefractreject',
            'name': 'Diffuse refraction reject',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'diffuserefractreject_threshold',
            'name': 'Threshold',
            'default': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'glossyreflectreject',
            'name': 'Glossy reflection reject',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'glossyreflectreject_threshold',
            'name': 'Threshold',
            'default': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'glossyrefractreject',
            'name': 'Glossy refraction reject',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'glossyrefractreject_threshold',
            'name': 'Threshold',
            'default': 10.0,
            'save_in_preset': True
        },

        {
            'type': 'int',
            'attr': 'maxphotondepth',
            'name': 'Max. Photon Depth',
            'description': 'Max recursion depth for photon tracing',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'directphotons',
            'name': 'Direct Photons',
            'description': 'Target number of direct light photons',
            'default': 1000000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'causticphotons',
            'name': 'Caustic Photons',
            'description': 'Target number of caustic photons. Use 0 to disable caustics, glass will cast solid shadows',
            'default': 20000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'indirectphotons',
            'name': 'Indirect Photons',
            'description': 'Target number of soft-indirect photons',
            'default': 200000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'radiancephotons',
            'name': 'Radiance Photons',
            'description': 'Target number of final gather photons',
            'default': 200000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'nphotonsused',
            'name': 'Number of Photons Used',
            'default': 50,
            'min': 1,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'maxphotondist',
            'name': 'Max. Photon Distance',
            'default': 0.1,
            'min': 0.01,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'finalgather',
            'name': 'Final Gather',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'finalgathersamples',
            'name': 'Final Gather Samples',
            'description': 'Number of final gather rays to cast for each primary ray. Higher values reduce indirect \
            light noise at the cost of overall speed',
            'default': 16,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'gatherangle',
            'name': 'Gather angle',
            'description': 'Reject final gather rays beyond this angle. Adjusts final gather accuracy, higher values \
            reduce noise at the cost of possible light leaks',
            'default': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'renderingmode',
            'name': 'Eye-Pass Mode',
            'default': 'directlighting',
            'description': 'Switch between direct light + final gather, or experimental photon map-guided path tracing',
            'items': [
                ('directlighting', 'Direct Lighting', 'Direct light sampling with final gathering'),
                ('path', 'Path', 'Experimental path tracer guided by the photon map'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'distancethreshold',
            'name': 'Distance threshold',
            'description': 'Fallbacks to path tracing when rendering corners in order to avoid photon leaks',
            # <--- that's what the wiki says it does.
            'default': 0.5,  # same as maxphotondist, this is how core defaults according to wiki
            'save_in_preset': True
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'photonmapsfile',
            'name': 'Photon Maps File',
            'description': 'Photon map storage path. If no map is found here, the current one will be saved for \
            next time',
            'default': '',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'debugmode',
            'name': 'Enable Debug Mode',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'dbg_enabledirect',
            'name': 'Debug: Enable direct',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'dbg_enableradiancemap',
            'name': 'Debug: Enable radiance map',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'dbg_enableindircaustic',
            'name': 'Debug: Enable indirect caustics',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'dbg_enableindirdiffuse',
            'name': 'Debug: Enable indirect diffuse',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'dbg_enableindirspecular',
            'name': 'Debug: Enable indirect specular',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'nsets',
            'name': 'Number of sets',
            'default': 4,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'nlights',
            'name': 'Number of lights',
            'default': 64,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'mindist',
            'name': 'Min. Distance',
            'default': 0.1,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'rrcontinueprob',
            'name': 'RR continue probability',
            'default': 0.65,
            'min': 0.0,
            'max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'rrstrategy',
            'name': 'RR strategy',
            'default': 'efficiency',
            'items': [
                ('efficiency', 'Efficiency', 'efficiency'),
                ('probability', 'Probability', 'probability'),
                ('none', 'None', 'none'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'includeenvironment',
            'name': 'Include Environment',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'directlightsampling',
            'name': 'Direct Light Sampling',
            'description': 'Turn this off to use brute force path tracing (faster with only "infinite" light (HDRI))',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'maxeyedepth',
            'name': 'Max. Eye Depth',
            'default': 48,
            'description': 'Max recursion depth for ray casting from eye',
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'photonperpass',
            'name': 'Photons Per Pass',
            'description': 'Number of photons to gather before going on to the next pass',
            'default': 1000000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'hitpointperpass',
            'name': 'Hit Points Per Pass',
            'description': 'Number of hit points to store per eye-pass before moving on. Lower values can decrease \
            memory useage at the cost of some performance. 0=one hitpoint per pixel',
            'default': 0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'startradius',
            'name': 'Starting Radius',
            'description': 'Photon radius used for initial pass. Try lowering this if the first pass renders very \
            slowly',
            'default': 2.0,
            'min': 0.0001,
            'save_in_preset': True
        },
        # 		{
        # 			'type': 'int',
        # 			'attr': 'startk',
        # 			'name': 'Starting K',
        # 			'description': 'Adjust starting photon radius to get this many photons. Higher values clear \
        # faster but are less accurate. 0=use initial radius',
        # 			'default': 30,
        # 			'min': 0,
        # 			'save_in_preset': True
        # 		},
        {
            'type': 'float',
            'attr': 'alpha',
            'name': 'Alpha',
            'description': 'Tighten photon search radius by this factor on subsequent passes',
            'default': 0.7,
            'min': 0.01,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'storeglossy',
            'name': 'Store on Glossy',
            'description': 'Use the photon pass to render glossy and metal surfaces. Can introduce noise, but is \
            needed for some corner cases',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'lookupaccel',
            'name': 'Lookup Accelerator',
            'description': 'Acceleration structure for hitpoints (not scene geometry)',
            'default': 'hybridhashgrid',
            'items': [
                ('hashgrid', 'Hash Grid', 'hashgrid'),
                ('kdtree', 'KD Tree', 'kdtree'),
                ('parallelhashgrid', 'Parallel Hash Grid', 'parallelhashgrid'),
                ('hybridhashgrid', 'Hybrid Hash Grid', 'hybridhashgrid'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'parallelhashgridspare',
            'name': 'Parallel Hash Grid Spare',
            'description': 'Higher values are faster but can use more memory',
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'pixelsampler',
            'name': 'Pixel sampler',
            'default': 'hilbert',
            'description': 'Sampling pattern used during the eye pass',
            'items': [
                ('linear', 'Linear', 'Scan top-to-bottom, one pixel line at a time'),
                ('tile', 'Tile', 'Scan in 32x32 blocks'),
                ('vegas', 'Vegas', 'Random sample distribution'),
                ('hilbert', 'Hilbert', 'Scan in a hilbert curve'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'photonsampler',
            'name': 'Photon sampler',
            'default': 'halton',
            'description': 'Sampling method for photons',
            'items': [
                ('amc', 'Adaptive Markov Chain', 'Use adapative markov chain monte carlo sampling'),
                ('halton', 'Halton', 'Use a permuted halton sequence'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'wavelengthstratificationpasses',
            'name': 'Wavelength Stratification Passes',
            'description': 'Use non-random wavelengths for this many passes. Can help with wierd initial coloration \
            due to unsampled wavelengths',
            'default': 8,
            'min': 0,
            'max': 64,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'useproba',
            'name': 'Use PPM Probability',
            'description': 'Use PPM probability for search radius reduction',
            'default': True,
            'save_in_preset': True
        },
    ]

    def api_output(self, scene=None):
        """
        Format this class's members into a LuxRender ParamSet

        Returns tuple
        """

        params = ParamSet()

        # Check to make sure all settings are correct when hybrid is selected. Keep this up to date as hybrid gets \
        # new options in later versions

        if scene.luxrender_rendermode.renderer == 'hybrid':
            #Check each integrator seperately so they don't mess with each other!
            if self.surfaceintegrator == 'bidirectional':
                if self.lightstrategy != ('one'):
                    LuxLog('Incompatible light strategy for Hybrid Bidir (switching to "one uniform").')
                    #					raise Exception('Incompatible render settings')

        hybrid_compat = scene.luxrender_rendermode.renderer == 'hybrid' and self.surfaceintegrator == 'bidirectional'

        # Exphotonmap is not compatible with light groups, warn here instead of light export code so
        # this warning only shows once instead of per lamp
        if not scene.luxrender_lightgroups.ignore and self.surfaceintegrator == 'exphotonmap':
            LuxLog('WARNING: Ex. Photon Map does not support light groups, exporting all lights in the default group.')

        # Warn about multi volume integrator and homogeneous exterior
        if scene.luxrender_world.default_exterior_volume:
            ext_v = scene.luxrender_world.default_exterior_volume

            for volume in scene.luxrender_volumes.volumes:
                if volume.name == ext_v and volume.type == 'homogeneous' and \
                                scene.luxrender_volumeintegrator.volumeintegrator == 'multi':
                    LuxLog('Warning: Default exterior volume is homogeneous, and the "multi" volume integrator is \
                    selected! Performance may be poor, consider using the "single" volume integrator instead')

        # Safety checks for settings end here

        if self.surfaceintegrator == 'bidirectional':
            params.add_integer('eyedepth', self.eyedepth) \
                .add_integer('lightdepth', self.lightdepth) \
                .add_integer('lightraycount', self.lightraycount)

            if not self.advanced:
                # Export the regular light strategy setting for lightpath strat when in non-advanced mode,
                # advanced mode allows them to be set independently
                params.add_string('lightpathstrategy',
                                  self.lightstrategy if not hybrid_compat else 'one')

            if self.advanced:
                params.add_float('eyerrthreshold', self.eyerrthreshold) \
                    .add_float('lightrrthreshold', self.lightrrthreshold) \
                    .add_string('lightpathstrategy', self.lightpathstrategy if not hybrid_compat else 'one') \
                    .add_integer('shadowraycount', self.shadowraycount)

        if self.surfaceintegrator == 'directlighting':
            params.add_integer('maxdepth', self.maxdepth)

            if self.advanced:
                params.add_integer('shadowraycount', self.shadowraycount)

        if self.surfaceintegrator == 'sppm':
            params.add_integer('maxeyedepth', self.maxeyedepth) \
                .add_integer('maxphotondepth', self.maxphotondepth) \
                .add_integer('photonperpass', self.photonperpass) \
                .add_integer('hitpointperpass', self.hitpointperpass) \
                .add_float('startradius', self.startradius) \
                .add_float('alpha', self.alpha) \
                .add_bool('includeenvironment', self.includeenvironment) \
                .add_bool('directlightsampling', self.directlightsampling)

            if self.advanced:
                params.add_bool('storeglossy', self.storeglossy) \
                    .add_bool('useproba', self.useproba) \
                    .add_integer('wavelengthstratificationpasses', self.wavelengthstratificationpasses) \
                    .add_string('lookupaccel', self.lookupaccel) \
                    .add_float('parallelhashgridspare', self.parallelhashgridspare) \
                    .add_string('pixelsampler', self.pixelsampler) \
                    .add_string('photonsampler', self.photonsampler)

        if self.surfaceintegrator == 'distributedpath':
            params.add_integer('directsamples', self.directsamples) \
                .add_integer('indirectsamples', self.indirectsamples) \
                .add_integer('diffusereflectdepth', self.diffusereflectdepth) \
                .add_integer('diffusereflectsamples', self.diffusereflectsamples) \
                .add_integer('diffuserefractdepth', self.diffuserefractdepth) \
                .add_integer('diffuserefractsamples', self.diffuserefractsamples) \
                .add_integer('glossyreflectdepth', self.glossyreflectdepth) \
                .add_integer('glossyreflectsamples', self.glossyreflectsamples) \
                .add_integer('glossyrefractdepth', self.glossyrefractdepth) \
                .add_integer('glossyrefractsamples', self.glossyrefractsamples) \
                .add_integer('specularreflectdepth', self.specularreflectdepth) \
                .add_integer('specularrefractdepth', self.specularrefractdepth)

            if self.advanced:
                params.add_bool('directsampleall', self.directsampleall) \
                    .add_bool('directdiffuse', self.directdiffuse) \
                    .add_bool('directglossy', self.directglossy) \
                    .add_bool('indirectsampleall', self.indirectsampleall) \
                    .add_bool('indirectdiffuse', self.indirectdiffuse) \
                    .add_bool('indirectglossy', self.indirectglossy) \
                    .add_bool('diffusereflectreject', self.diffusereflectreject) \
                    .add_float('diffusereflectreject_threshold', self.diffusereflectreject_threshold) \
                    .add_bool('diffuserefractreject', self.diffuserefractreject) \
                    .add_float('diffuserefractreject_threshold', self.diffuserefractreject_threshold) \
                    .add_bool('glossyreflectreject', self.glossyreflectreject) \
                    .add_float('glossyreflectreject_threshold', self.glossyreflectreject_threshold) \
                    .add_bool('glossyrefractreject', self.glossyrefractreject) \
                    .add_float('glossyrefractreject_threshold', self.glossyrefractreject_threshold)

        if self.surfaceintegrator == 'exphotonmap':
            params.add_integer('maxdepth', self.maxeyedepth) \
                .add_integer('maxphotondepth', self.maxphotondepth) \
                .add_integer('directphotons', self.directphotons) \
                .add_integer('causticphotons', self.causticphotons) \
                .add_integer('indirectphotons', self.indirectphotons) \
                .add_integer('radiancephotons', self.radiancephotons) \
                .add_integer('nphotonsused', self.nphotonsused) \
                .add_float('maxphotondist', self.maxphotondist) \
                .add_bool('finalgather', self.finalgather) \
                .add_integer('finalgathersamples', self.finalgathersamples) \
                .add_string('renderingmode', self.renderingmode) \
                .add_float('gatherangle', self.gatherangle) \
                .add_string('rrstrategy', self.rrstrategy) \
                .add_float('rrcontinueprob', self.rrcontinueprob)

            # Export maxeyedepth as maxdepth, since that is actually the switch the scene file accepts
            if self.advanced:
                params.add_float('distancethreshold', self.distancethreshold) \
                    .add_string('photonmapsfile', self.photonmapsfile) \
                    .add_integer('shadowraycount', self.shadowraycount)

            if self.debugmode:
                params.add_bool('dbg_enabledirect', self.dbg_enabledirect) \
                    .add_bool('dbg_enableradiancemap', self.dbg_enableradiancemap) \
                    .add_bool('dbg_enableindircaustic', self.dbg_enableindircaustic) \
                    .add_bool('dbg_enableindirdiffuse', self.dbg_enableindirdiffuse) \
                    .add_bool('dbg_enableindirspecular', self.dbg_enableindirspecular)

        if self.surfaceintegrator == 'igi':
            params.add_integer('nsets', self.nsets) \
                .add_integer('nlights', self.nlights) \
                .add_integer('maxdepth', self.maxdepth) \
                .add_float('mindist', self.mindist)

        if self.surfaceintegrator == 'path':
            params.add_integer('maxdepth', self.maxdepth) \
                .add_float('rrcontinueprob', self.rrcontinueprob) \
                .add_string('rrstrategy', self.rrstrategy) \
                .add_bool('includeenvironment', self.includeenvironment) \
                .add_bool('directlightsampling', self.directlightsampling)

            if self.advanced:
                params.add_integer('shadowraycount', self.shadowraycount)

        if self.surfaceintegrator not in ('sppm', 'distributedpath'):
            params.add_string('lightstrategy', self.lightstrategy if not hybrid_compat else 'one')

        return self.surfaceintegrator, params
