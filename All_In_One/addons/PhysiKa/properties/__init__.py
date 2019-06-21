# Blender FLIP Fluid Add-on
# Copyright (C) 2018 Ryan L. Guy
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

if "bpy" in locals():
    import importlib
    reloadable_modules = [
        # 'preferences_properties',
        # 'custom_properties',
        # 'preset_properties',
        'state_properties',
        'physika_properties',
        'object_properties',
        # 'material_properties',
        # 'helper_properties'
    ]
    for module_name in reloadable_modules:
        if module_name in locals():
            importlib.reload(locals()[module_name])

import bpy

from . import (
    object_properties,
    physika_properties,
    state_properties
    )


def scene_update_post(scene):
    # object_properties.scene_update_post(scene)
    physika_properties.scene_update_post(scene)



def register():
    # preferences_properties.register()
    # custom_properties.register()
    # preset_properties.register()
    state_properties.register()
    physika_properties.register()
    object_properties.register()
    # material_properties.register()
    # helper_properties.register()


def unregister():
    # preferences_properties.unregister()
    # custom_properties.unregister()
    # preset_properties.unregister()
    state_properties.unregister()
    physika_properties.unregister()
    object_properties.unregister()
    # material_properties.unregister()
    # helper_properties.unregister()


