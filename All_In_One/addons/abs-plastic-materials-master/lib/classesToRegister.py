'''
Copyright (C) 2018 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# Addon imports
from ..ui import *
from ..buttons import *
from .preferences import *
from .. import addon_updater_ops


classes = (
    # abs_plastic_materials/buttons
    ABS_OT_append_materials,
    ABS_OT_mark_outdated,
    # abs_plastic_materials/lib
    ABSPlasticMaterialsPreferences,
    # abs_plastic_materials/ui
    PROPERTIES_PT_abs_plastic_materials,
)
