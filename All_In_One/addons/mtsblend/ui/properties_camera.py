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

import bl_ui
from bl_ui.properties_data_camera import CameraButtonsPanel

from ..extensions_framework.ui import property_group_renderer

from .. import MitsubaAddon


# Add radial distortion options to lens panel
def mts_use_rdist(self, context):
    if context.scene.render.engine == 'MITSUBA_RENDER' and context.camera.type not in {'ORTHO', 'PANO'}:
        col = self.layout.column()
        col.active = context.camera.mitsuba_camera.use_dof is not True
        col.prop(context.camera.mitsuba_camera, "use_rdist", text="Use Radial Distortion")

        if context.camera.mitsuba_camera.use_rdist is True:
            row = col.row(align=True)
            row.prop(context.camera.mitsuba_camera, "kc0", text="kc0")
            row.prop(context.camera.mitsuba_camera, "kc1", text="kc1")

bl_ui.properties_data_camera.DATA_PT_lens.append(mts_use_rdist)


# Add Mitsuba dof elements to blender dof panel
def mts_use_dof(self, context):
    if context.scene.render.engine == 'MITSUBA_RENDER':
        row = self.layout.row()
        row.prop(context.camera.mitsuba_camera, "use_dof", text="Use Depth of Field")

        if context.camera.mitsuba_camera.use_dof is True:
            row = self.layout.row()
            row.prop(context.camera.mitsuba_camera, "apertureRadius", text="DOF Aperture Radius")

bl_ui.properties_data_camera.DATA_PT_camera_dof.append(mts_use_dof)


class mts_camera_panel(CameraButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = {'MITSUBA_RENDER'}


@MitsubaAddon.addon_register_class
class MitsubaCamera_PT_camera(mts_camera_panel):
    '''
    Camera Settings
    '''

    bl_label = 'Camera Settings'

    display_property_groups = [
        (('camera',), 'mitsuba_camera')
    ]


@MitsubaAddon.addon_register_class
class MitsubaCamera_PT_film(mts_camera_panel):
    '''
    Camera Film Settings
    '''

    bl_label = 'Film Settings'

    display_property_groups = [
        (('camera', 'mitsuba_camera'), 'mitsuba_film'),
    ]
