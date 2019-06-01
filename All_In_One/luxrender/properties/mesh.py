# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Daniel Genrich
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
from ..extensions_framework.validate import Logic_Operator as LO

from .. import LuxRenderAddon
from ..export import ParamSet
from ..export.materials import get_texture_from_scene
from ..properties.material import texture_append_visibility
from ..properties.texture import FloatTextureParameter
from ..util import dict_merge
from ..outputs import LuxManager


class MeshFloatTextureParameter(FloatTextureParameter):
    def texture_slot_set_attr(self):
        # Looks in a different location than other FloatTextureParameters
        return lambda s, c: c.luxrender_mesh


TF_displacementmap = MeshFloatTextureParameter(
    'dm',
    'Displacement Map',
    real_attr='displacementmap',
    add_float_value=False
)


@LuxRenderAddon.addon_register_class
class luxrender_mesh(declarative_property_group):
    """
    Storage class for LuxRender Mesh settings.
    """

    ef_attach_to = ['Mesh', 'SurfaceCurve', 'TextCurve', 'Curve', 'MetaBall']

    controls = [
                   'mesh_type',
                   'instancing_mode',
                   'portal',
                   'generatetangents',
                   'subdiv',
                   'sublevels',
                   'mdsublevels',
                   'nsmooth',
                   ['sharpbound', 'splitnormal'],
               ] + \
               TF_displacementmap.controls + \
               [
                   ['dmscale', 'dmoffset']
               ]

    visibility = dict_merge({
                                'nsmooth': {'subdiv': 'loop'},
                                'sharpbound': {'subdiv': 'loop'},
                                'splitnormal': {'subdiv': 'loop'},
                                'sublevels': {'subdiv': 'loop'},
                                'mdsublevels': {'subdiv': 'microdisplacement'},
                                'dmscale': {'subdiv': LO({'!=': 'None'}), 'dm_floattexturename': LO({'!=': ''})},
                                'dmoffset': {'subdiv': LO({'!=': 'None'}), 'dm_floattexturename': LO({'!=': ''})},
                            }, TF_displacementmap.visibility)

    visibility = texture_append_visibility(visibility, TF_displacementmap, {'subdiv': LO({'!=': 'None'})})

    properties = [
                     {
                         'type': 'enum',
                         'attr': 'mesh_type',
                         'name': 'Export as',
                         'items': [
                             ('global', 'Use Default Setting', 'global'),
                             ('native', 'LuxRender Mesh', 'native'),
                             ('binary_ply', 'Binary PLY', 'binary_ply')
                         ],
                         'default': 'global'
                     },
                     {
                         'type': 'enum',
                         'attr': 'instancing_mode',
                         'name': 'Instancing',
                         'items': [
                             ('auto', 'Automatic', 'Let the exporter code decide'),
                             ('always', 'Always', 'Always export this mesh as instances'),
                             ('never', 'Never', 'Never export this mesh as instances')
                         ],
                         'default': 'auto'
                     },
                     {
                         'type': 'bool',
                         'attr': 'portal',
                         'name': 'Exit Portal',
                         'description': 'Use this mesh as an exit portal (geometry should be open/planar)',
                         'default': False,
                     },
                     {
                         'type': 'bool',
                         'attr': 'generatetangents',
                         'name': 'Generate Tangents',
                         'description': 'Generate tanget space for this mesh. Enable when using a bake-generated \
                         normal map',
                         'default': False,
                     },
                     {
                         'type': 'enum',
                         'attr': 'subdiv',
                         'name': 'Subdivision Scheme',
                         'default': 'None',
                         'items': [
                             ('None', 'None', 'None'),
                             ('loop', 'Loop', 'loop'),
                             ('microdisplacement', 'Microdisplacement', 'microdisplacement')
                         ]
                     },
                     {
                         'type': 'bool',
                         'attr': 'nsmooth',
                         'name': 'Normal smoothing',
                         'description': 'Re-smooth normals after subdividing',
                         'default': True,
                     },
                     {
                         'type': 'bool',
                         'attr': 'sharpbound',
                         'name': 'Sharpen Bounds',
                         'description': 'Perserve hard borders in geometry',
                         'default': False,
                     },
                     {
                         'type': 'bool',
                         'attr': 'splitnormal',
                         'name': 'Keep Split Edges',
                         'default': False,
                         'description': 'Preserves effects of split-edges by splitting at breaks in the normal. \
                         WARNING: This will cause solid-shaded meshes to rip open!'},
                     {
                         'type': 'int',
                         'attr': 'sublevels',
                         'name': 'Subdivision Levels',
                         'default': 2,
                         'min': 0,
                         'soft_min': 0,
                         'max': 6,
                         'soft_max': 6
                     },
                     {
                         'type': 'int',
                         'attr': 'mdsublevels',
                         'name': 'Microsubdivision Levels',
                         'default': 50,
                         'min': 0,
                         'soft_min': 0,
                         'max': 1000,
                         'soft_max': 1000
                     },
                 ] + \
                 TF_displacementmap.properties + \
                 [
                     {
                         'type': 'float',
                         'attr': 'dmscale',
                         'name': 'Scale',
                         'description': 'Displacement Map Scale',
                         'default': 1.0,
                         'precision': 6,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH'
                     },
                     {
                         'type': 'float',
                         'attr': 'dmoffset',
                         'name': 'Offset',
                         'description': 'Displacement Map Offset',
                         'default': 0.0,
                         'precision': 6,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH'
                     },
                 ]

    def get_paramset(self):
        params = ParamSet()

        # Export generatetangents
        params.add_bool('generatetangents', self.generatetangents)

        # check if subdivision is used
        if self.subdiv != 'None':
            params.add_string('subdivscheme', self.subdiv)

            if self.subdiv == 'loop':
                params.add_integer('nsubdivlevels', self.sublevels)
            elif self.subdiv == 'microdisplacement':
                params.add_integer('nsubdivlevels', self.mdsublevels)

            params.add_bool('dmnormalsmooth', self.nsmooth)
            params.add_bool('dmsharpboundary', self.sharpbound)
            params.add_bool('dmnormalsplit', self.splitnormal)

        export_dm = TF_displacementmap.get_paramset(self)

        if self.dm_floattexturename and len(export_dm) > 0:
            texture_name = getattr(self, 'dm_floattexturename')
            texture = get_texture_from_scene(LuxManager.CurrentScene, texture_name)

            if texture.type in ('IMAGE', 'OCEAN') and texture.luxrender_texture.type == 'BLENDER':
                params.add_texture('displacementmap', '%s_float' % self.dm_floattexturename)
            else:
                params.add_texture('displacementmap', self.dm_floattexturename)

            params.add_float('dmscale', self.dmscale)
            params.add_float('dmoffset', self.dmoffset)

        return params
