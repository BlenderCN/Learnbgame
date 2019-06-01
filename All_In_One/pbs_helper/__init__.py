# Copyright (C) 2019 ywabygl@gmail.com
#
# PBS Helper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PBS Helper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PBS Helper. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "PBS Helper",
    "author": "ywaby",
    "version": (0, 1, 2),
    "description": "shader bake"
    'material merge'
    'pbr paint helper',
    "blender": (2, 80, 0),
    "location": "Shader Node->Properties->PBS Hepler",
    "warning": "",
    "tracker_url": "http://github.com/ywaby/bl_pbs_helper/issue",
    "wiki_url": "http://github.com/ywaby/bl_pbs_helper",
    "support": "TESTING",
    "category": "Learnbgame",
}

import bpy
from .preset import register as preset_register, unregister as preset_unregister
from .material_bake import register as mat_bake_register, unregister as mat_bake_unregister
from bpy.props import (
    BoolProperty
)
from bpy.types import (
    AddonPreferences
)
class Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    sync_paint_node: BoolProperty(
        name='Paint To Node',
        default=True,
        description='Paint to Active Node'
    )
    auto_save_image: BoolProperty(
        name='Auto Save Image',
        default=True,
        description=''
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "sync_paint_node")
        row.prop(self, "auto_save_image")
        row = layout.row()


classes = [
    Preferences
]

def register():
    mat_bake_register()
    preset_register()
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    preset_unregister()
    mat_bake_unregister()