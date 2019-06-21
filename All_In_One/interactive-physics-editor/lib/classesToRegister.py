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

from ..operators.setup_phys import *
from ..ui import *
from .preferences import *
from .reportError import *
from .. import addon_updater_ops

classes = (
    # interactive_physics_editor/operators
    PHYSICS_OT_setup_interactive_sim,
    # interactive_physics_editor/ui
    PHYSICS_PT_interactive_editor,
    # interactive_physics_editor/lib
    INTERPHYS_PT_preferences,
    SCENE_OT_report_error,
    SCENE_OT_close_report_error,
)
