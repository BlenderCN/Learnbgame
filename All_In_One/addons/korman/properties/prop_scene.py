#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *

from ..exporter.etlight import _NUM_RENDER_LAYERS

class PlasmaBakePass(bpy.types.PropertyGroup):
    def _get_display_name(self):
        return self.name
    def _set_display_name(self, value):
        for i in bpy.data.objects:
            lm = i.plasma_modifiers.lightmap
            if lm.bake_pass_name == self.name:
                lm.bake_pass_name = value
        self.name = value

    display_name = StringProperty(name="Pass Name",
                                  get=_get_display_name,
                                  set=_set_display_name,
                                  options=set())

    render_layers = BoolVectorProperty(name="Layers to Bake",
                                       description="Render layers to use for baking",
                                       options=set(),
                                       subtype="LAYER",
                                       size=_NUM_RENDER_LAYERS,
                                       default=((True,) * _NUM_RENDER_LAYERS))


class PlasmaScene(bpy.types.PropertyGroup):
    bake_passes = CollectionProperty(type=PlasmaBakePass)
    active_pass_index = IntProperty(options={"HIDDEN"})

    modifier_copy_object = PointerProperty(name="INTERNAL: Object to copy modifiers from",
                                           options={"HIDDEN", "SKIP_SAVE"},
                                           type=bpy.types.Object)
    modifier_copy_id = StringProperty(name="INTERNAL: Modifier to copy from",
                                      options={"HIDDEN", "SKIP_SAVE"})
