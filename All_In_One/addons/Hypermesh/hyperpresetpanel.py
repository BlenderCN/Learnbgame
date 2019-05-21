# This file is part of Hypermesh.
#
# Hypermesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hypermesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hypermesh.  If not, see <http://www.gnu.org/licenses/>.

import bpy


class HyperPresetPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "object"
    bl_label = "Select projection"

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        ob = context.active_object
        if ob.type != 'MESH':
            return False
        return True

    def draw(self, context):
        me = context.active_object.data
        layout = self.layout
        if not me.hypersettings.hyper:
            layout.operator("hyper.makehyper", text="Make hyper")
            return
        layout.template_list("preset_list", "notsurewhattoputhere",
                             context.scene, "hyperpresets",
                             me.hypersettings, "preset")
