# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Michael Klemm
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
import bl_ui
import bpy

from ..extensions_framework.ui import property_group_renderer

from .. import PBRTv3Addon


class hair_panel(bl_ui.properties_particle.ParticleButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.particle_settings.type == 'HAIR'


@PBRTv3Addon.addon_register_class
class pbrtv3_ui_controls(hair_panel):
    """
    Hair settings
    """
    bl_label = "PBRTv3 Hair Rendering"
    display_property_groups = [
        ( ('particle_system', 'settings',), 'pbrtv3_hair' )
    ]

