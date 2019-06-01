#
# Copyright(C) 2017-2018 Samuel Villarreal
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

import os
import bpy

# -----------------------------------------------------------------------------
#
def load(operator, context, filepath, global_matrix):
    from io_scene_forsaken import forsaken_utils
    
    forsaken_utils.load_mx(filepath, global_matrix)
    return {'FINISHED'}
    