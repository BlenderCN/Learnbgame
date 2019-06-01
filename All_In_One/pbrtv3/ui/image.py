# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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
from ..extensions_framework.ui import property_group_renderer

from .. import PBRTv3Addon
from ..outputs import PBRTv3Manager as LM
from ..outputs.pure_api import PYLUX_AVAILABLE


@PBRTv3Addon.addon_register_class
class pbrtv3_ui_rendering_controls(property_group_renderer):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "PBRTv3 Rendering Controls"
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    ctx = None

    @classmethod
    def poll(cls, context):
        eng = context.scene.render.engine in cls.COMPAT_ENGINES

        if eng:
            lma = LM.GetActive() is not None and LM.GetActive().started

            if lma:
                cls.ctx = LM.GetActive().lux_context
                ctxc = cls.ctx is not None and cls.ctx.API_TYPE == 'PURE'
                csd = context.space_data

                return PYLUX_AVAILABLE and ctxc and csd

        return False

    display_property_groups = [
        ( ('scene', 'camera', 'data', 'pbrtv3_camera', 'pbrtv3_film'), 'pbrtv3_tonemapping' )
    ]

    def draw(self, context):
        # Draw as normal ...
        property_group_renderer.draw(self, context)

        # ... and live-update the parameters !

        # TODO: Strategy:
        # 1. Detect which parameters have changed
        # 2. Add those to an update queue in tuple form (component, parameter, value)
        # 3. Give queue to FrameBuffer thread, replacing values as needed
        # 4. FB will empty its own queue into the Context upon the next image update call

        if self.ctx is not None and self.ctx.API_TYPE == 'PURE':
            pylux = self.ctx.PYLUX
            tm_data = context.scene.camera.data.pbrtv3_camera.pbrtv3_film.pbrtv3_tonemapping
            tm_map = {
                'reinhard': pylux.ImageFilm.TonemapKernels.Reinhard,
                'linear': pylux.ImageFilm.TonemapKernels.Linear,
                'autolinear': pylux.ImageFilm.TonemapKernels.AutoLinear,
                'contrast': pylux.ImageFilm.TonemapKernels.Contrast,
                'maxwhite': pylux.ImageFilm.TonemapKernels.MaxWhite,
            }

            self.ctx.setAttribute('film', 'TonemapKernel', tm_map[tm_data.type])
