# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import time

# Addon imports
from .common import *
from .general import *

# code adapted from https://github.com/bwrsandman/blender-addons/blob/master/render_povray/render.py
def getSmokeInfo(smoke_obj):
    smoke_data = None
    # Search smoke domain target for smoke modifiers
    for mod in smoke_obj.modifiers:
        if hasattr(mod, "smoke_type") and mod.smoke_type == 'DOMAIN':
            smoke_data = mod.domain_settings
            break

    if smoke_data is not None:
        # get channel data
        density_grid = tuple(smoke_data.density_grid)
        flame_grid = tuple(smoke_data.flame_grid)
        color_grid = tuple(smoke_data.color_grid)
        # get resolution
        domain_res = getAdjustedRes(smoke_data, tuple(smoke_data.domain_resolution))
        adapt = smoke_data.use_adaptive_domain
        max_res_i = smoke_data.resolution_max
        max_res = Vector(domain_res) * (max_res_i / max(domain_res))
        max_res = getAdjustedRes(smoke_data, max_res)
        return density_grid, flame_grid, color_grid, domain_res, max_res, adapt
    else:
        return [None]*6


def getAdjustedRes(smoke_data, smoke_res):
    if smoke_data.use_high_resolution:
        smoke_res = [int((smoke_data.amplify + 1) * i) for i in smoke_res]
    return smoke_res
