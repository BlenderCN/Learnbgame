# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

from bpy.types import Panel

from bl_ui.properties_texture import TextureButtonsPanel

from .. import MitsubaAddon
from ..ui import draw_node_properties_recursive


@MitsubaAddon.addon_register_class
class MitsubaTexture_PT_context_texture(TextureButtonsPanel, Panel):
    '''
    Mitsuba Texture Context Panel
    Taken from Blender scripts
    '''

    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'MITSUBA_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine

        return ((context.material or
                context.world or
                context.lamp or
                context.texture) and
                (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout

        tex = False

        if context.material:
            id_data = context.material

        elif context.lamp:
            id_data = context.lamp

        try:
            ntree = id_data.mitsuba_nodes.get_node_tree()

            for node in ntree.nodes:
                if node.mitsuba_nodetype == 'TEXTURE':
                    tex = True
                    break

            if tex:
                layout.prop(id_data.mitsuba_nodes, "texture_node", text="Node")

                for node in ntree.nodes:
                    if node.name == id_data.mitsuba_nodes.texture_node:
                        draw_node_properties_recursive(layout, context, ntree, node)
                        break

            else:
                raise Exception()

        except:
            layout.label('No texture found!!')
