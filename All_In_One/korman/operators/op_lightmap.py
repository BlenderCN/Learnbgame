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

from ..exporter.etlight import LightBaker
from ..helpers import UiHelper

class _LightingOperator:

    @classmethod
    def poll(cls, context):
        if context.mode != "OBJECT":
            return False
        if context.object is not None:
            return context.scene.render.engine == "PLASMA_GAME"


class LightmapAutobakePreviewOperator(_LightingOperator, bpy.types.Operator):
    bl_idname = "object.plasma_lightmap_preview"
    bl_label = "Preview Lightmap"
    bl_options = {"INTERNAL"}

    def __init__(self):
        super().__init__()

    def execute(self, context):
        with UiHelper(context):
            with LightBaker() as bake:
                if not bake.bake_static_lighting([context.active_object,]):
                    self.report({"INFO"}, "No valid lights found to bake.")
                    return {"FINISHED"}

        tex = bpy.data.textures.get("LIGHTMAPGEN_PREVIEW")
        if tex is None:
            tex = bpy.data.textures.new("LIGHTMAPGEN_PREVIEW", "IMAGE")
        tex.extension = "CLIP"
        tex.image = bpy.data.images["{}_LIGHTMAPGEN.png".format(context.active_object.name)]

        return {"FINISHED"}
