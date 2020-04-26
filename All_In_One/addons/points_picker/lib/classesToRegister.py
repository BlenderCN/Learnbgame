# Copyright (C) 2018 Christopher Gearhart
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

from .reportError import *
from .preferences import POINTSPICKER_PT_preferences
from ..ui import VIEW3D_PT_tools_points_picker
from ..operators.points_picker import VIEW3D_OT_points_picker

classes = [
    POINTSPICKER_PT_preferences,
    VIEW3D_PT_tools_points_picker,
    VIEW3D_OT_points_picker,
]
