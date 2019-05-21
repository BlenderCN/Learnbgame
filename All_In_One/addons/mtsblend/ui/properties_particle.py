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

from bl_ui.properties_particle import ParticleButtonsPanel

from ..extensions_framework.ui import property_group_renderer

from .. import MitsubaAddon


class mitsuba_particle_panel(ParticleButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = {'MITSUBA_RENDER'}


@MitsubaAddon.addon_register_class
class MitsubaParticle_PT_hair(mitsuba_particle_panel):
    bl_label = 'Hair Settings'

    display_property_groups = [
        (('particle_system', 'settings', ), 'mitsuba_hair')
    ]

    @classmethod
    def poll(cls, context):
        psys = context.particle_system
        engine = context.scene.render.engine

        if psys is None:
            return False

        if psys.settings is None:
            return False

        return psys.settings.type == 'HAIR' and (engine in cls.COMPAT_ENGINES)
