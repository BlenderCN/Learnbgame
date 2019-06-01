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


class PlasmaRenderEngine(bpy.types.RenderEngine):

    bl_idname = "PLASMA_GAME"
    bl_label = "Korman"

    pass


# Explicitly whitelist compatible Blender panels...
from bl_ui import properties_material
properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_diffuse.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_shading.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_specular.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_options.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_transp.COMPAT_ENGINES.add("PLASMA_GAME")
properties_material.MATERIAL_PT_shadow.COMPAT_ENGINES.add("PLASMA_GAME")
del properties_material

from bl_ui import properties_data_mesh
properties_data_mesh.DATA_PT_uv_texture.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_mesh.DATA_PT_vertex_colors.COMPAT_ENGINES.add("PLASMA_GAME")
del properties_data_mesh

def _whitelist_all(mod):
    for i in dir(mod):
        attr = getattr(mod, i)
        if hasattr(attr, "COMPAT_ENGINES"):
            getattr(attr, "COMPAT_ENGINES").add("PLASMA_GAME")

from bl_ui import properties_data_lamp
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_preview.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_lamp.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_shadow.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_area.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_spot.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_falloff_curve.COMPAT_ENGINES.add("PLASMA_GAME")
properties_data_lamp.DATA_PT_custom_props_lamp.COMPAT_ENGINES.add("PLASMA_GAME")
del properties_data_lamp

from bl_ui import properties_render
_whitelist_all(properties_render)
del properties_render

from bl_ui import properties_texture
_whitelist_all(properties_texture)
del properties_texture

from bl_ui import properties_world
properties_world.WORLD_PT_ambient_occlusion.COMPAT_ENGINES.add("PLASMA_GAME")
properties_world.WORLD_PT_environment_lighting.COMPAT_ENGINES.add("PLASMA_GAME")
properties_world.WORLD_PT_indirect_lighting.COMPAT_ENGINES.add("PLASMA_GAME")
properties_world.WORLD_PT_gather.COMPAT_ENGINES.add("PLASMA_GAME")
del properties_world
