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

from bpy.types import Operator
from bpy.props import IntProperty, StringProperty

from .. import MitsubaAddon

from ..data.ior import ior_dict
from ..data.materials import medium_material_dict


@MitsubaAddon.addon_register_class
class MATERIAL_OT_mitsuba_set_medium_material(Operator):
    bl_idname = 'material.mitsuba_set_medium_material'
    bl_label = 'Apply Medium Material preset'

    index = IntProperty()
    l_name = StringProperty()

    def execute(self, context):
        material = medium_material_dict[self.properties.index]
        name = self.properties.l_name

        try:
            ntree = context.nodetree

        except:
            ntree = context.space_data.node_tree

        try:
            node = context.node
            node_name = node.bl_idname
            mat_type = node_name.rpartition('_')[2]

            if mat_type in {'hk', 'homogeneous', 'dipole', 'singlescatter'}:
                node.preset_material = name
                node.preset_sigmaS = material[0]
                node.preset_sigmaA = material[1]
                node.preset_g = material[2]
                node.useAlbSigmaT = False
                ntree.unlink(node.inputs['Scattering Coefficient'])
                ntree.unlink(node.inputs['Absorption Coefficient'])
                ntree.unlink(node.inputs['Anisotropy'])
                node.inputs['Scattering Coefficient'].default_value = material[0]
                node.inputs['Absorption Coefficient'].default_value = material[1]
                node.inputs['Anisotropy'].default_value = material[2]
                node.material = name

        except:
            pass

        return {'FINISHED'}


@MitsubaAddon.addon_register_class
class MATERIAL_OT_mitsuba_set_int_ior(Operator):
    bl_idname = 'material.mitsuba_set_int_ior'
    bl_label = 'Apply Interior IOR preset'

    index = IntProperty()
    l_name = StringProperty()

    def execute(self, context):
        ior = ior_dict[self.properties.index]
        name = self.properties.l_name
        mat_type = ''

        try:
            node = context.node
            node_name = node.bl_idname
            mat_type = node_name.rpartition('_')[2]

            if mat_type in {'dielectric', 'plastic', 'coating', 'dipole'}:
                node.intIOR = ior
                node.intIOR_presetvalue = ior
                node.intIOR_presetstring = name

        except:
            pass

        return {'FINISHED'}


@MitsubaAddon.addon_register_class
class MATERIAL_OT_mitsuba_set_ext_ior(Operator):
    bl_idname = 'material.mitsuba_set_ext_ior'
    bl_label = 'Apply Exterior IOR preset'

    index = IntProperty()
    l_name = StringProperty()

    def execute(self, context):
        ior = ior_dict[self.properties.index]
        name = self.properties.l_name
        mat_type = ''

        try:
            node = context.node
            node_name = node.bl_idname
            mat_type = node_name.rpartition('_')[2]

            if mat_type in {'dielectric', 'plastic', 'coating', 'dipole'}:
                node.extIOR = ior
                node.extIOR_presetvalue = ior
                node.extIOR_presetstring = name

            elif mat_type == 'conductor':
                node.extEta = ior
                node.extEta_presetvalue = ior
                node.extEta_presetstring = name

        except:
            pass

        return {'FINISHED'}
