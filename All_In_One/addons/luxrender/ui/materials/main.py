# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# ***** END GPL LICENCE BLOCK *****
#
import bpy

from ... import LuxRenderAddon
from ...properties import (find_node, find_node_input)
from ...ui.materials import luxrender_material_base
from ...operators.lrmdb import lrmdb_state
from ...outputs.luxcore_api import UseLuxCore


def cycles_panel_node_draw(layout, id_data, output_type, input_name):
    if not id_data.use_nodes:
        layout.prop(id_data, "use_nodes", icon='NODETREE')
        return False

    ntree = id_data.node_tree

    node = find_node(id_data, output_type)
    if not node:
        layout.label(text="No output node")
    else:
        input = find_node_input(node, input_name)
        layout.template_node_view(ntree, node, input)

    return True


def node_tree_selector_draw(layout, id_data, output_type):
    # layout.prop_search(mat.luxrender_material, "nodetree", bpy.data, "node_groups")
    try:
        layout.prop_search(id_data.luxrender_material, "nodetree", bpy.data, "node_groups")
    except:
        return False

    node = find_node(id_data, output_type)
    if not node:
        if not id_data.luxrender_material.nodetree:
            layout.operator('luxrender.add_material_nodetree', icon='NODETREE')
            return False
    return True


def panel_node_draw(layout, id_data, output_type, input_name):
    node = find_node(id_data, output_type)
    if not node:
        return False
    else:
        if id_data.luxrender_material.nodetree:
            ntree = bpy.data.node_groups[id_data.luxrender_material.nodetree]
            input = find_node_input(node, input_name)
            layout.template_node_view(ntree, node, input)

    return True


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_header(luxrender_material_base):
    """
    Material Editor UI Panel
    """
    bl_label = ''
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        # An exception, dont call the parent poll func because this manages materials for all engine types
        engine = context.scene.render.engine
        return (context.material or context.object) and (engine in cls.COMPAT_ENGINES)

    display_property_groups = [
        ( ('material',), 'luxrender_material' ),
    ]

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=2)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.65)

        if ob:
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()

        node_tree_selector_draw(layout, mat, 'luxrender_material_output_node')
        if not panel_node_draw(layout, mat, 'luxrender_material_output_node', 'Surface'):
            row = self.layout.row(align=True)
            if slot is not None and slot.name:
                row.label("Material type")
                row.menu('MATERIAL_MT_luxrender_type', text=context.material.luxrender_material.type_label)
                super().draw(context)


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_db(luxrender_material_base):
    bl_label = 'LuxRender Materials Database'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if not lrmdb_state._active:
            self.layout.operator('luxrender.lrmdb', text='Enable').invoke_action_id = -1
        else:
            self.layout.operator('luxrender.lrmdb', text='Disable').invoke_action_id = -2

            for action in lrmdb_state.actions:
                if action.callback is None:
                    self.layout.label(text=action.label)
                else:
                    self.layout.operator('luxrender.lrmdb', text=action.label).invoke_action_id = action.aid

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return not context.material.luxrender_material.nodetree
        except:
            return False


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_utils(luxrender_material_base):
    bl_label = 'LuxRender Materials Utils'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("luxrender.load_material", icon="DISK_DRIVE")
        row.operator("luxrender.save_material", icon="DISK_DRIVE").filename = \
            '%s.lbm2' % bpy.path.clean_name(context.material.name)

        row = self.layout.row(align=True)
        row.operator("luxrender.convert_all_materials", icon='WORLD_DATA')

        row = self.layout.row(align=True)
        row.operator("luxrender.convert_material", icon='MATERIAL_DATA')

        # row = self.layout.row(align=True)

    # row.operator("luxrender.material_reset", icon='SOLID')

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return not context.material.luxrender_material.nodetree
        except:
            return False


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_emission(luxrender_material_base):
    """
    Material Emission Settings
    """

    bl_label = 'LuxRender Light Emission'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('material',), 'luxrender_emission' )
    ]

    def draw_header(self, context):
        self.layout.prop(context.material.luxrender_emission, "use_emission", text="")

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return not context.material.luxrender_material.nodetree
        except:
            return False


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_transparency(luxrender_material_base):
    """
    Material Transparency Settings
    """

    bl_label = 'LuxRender Alpha Transparency'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('material',), 'luxrender_transparency' )
    ]

    def draw_header(self, context):
        self.layout.prop(context.material.luxrender_transparency, "transparent", text="")

    @classmethod
    def poll(cls, context):
        if not hasattr(context.material, 'luxrender_transparency'):
            return False
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return super().poll(
                context) and context.material.luxrender_material.type != 'null' and not context.material.luxrender_material.nodetree
        except:
            return super().poll(context)


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_coating(luxrender_material_base):
    """
    Material Glossy Coating Settings
    """

    bl_label = 'LuxRender Glossy Coating'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('material',), 'luxrender_coating')
    ]

    def draw_header(self, context):
        self.layout.prop(context.material.luxrender_coating, "use_coating", text="")

    def draw_coating_ior_menu(self, context):
        """
        This is a draw callback from property_group_renderer, due
        to ef_callback item in luxrender_coating.properties
        """
        lmc = context.material.luxrender_coating

        if lmc.index_floatvalue == lmc.index_presetvalue:
            menu_text = lmc.index_presetstring
        else:
            menu_text = '-- Choose preset --'

        cl = self.layout.column(align=True)

        cl.menu('LUXRENDER_MT_coating_ior_presets', text=menu_text)

    @classmethod
    def poll(cls, context):
        if not hasattr(context.material, 'luxrender_coating'):
            return False
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return super().poll(context) and not context.material.luxrender_material.nodetree
        except:
            return super().poll(context)


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_node_volume(luxrender_material_base):
    bl_label = 'Volumes'

    def draw(self, context):
        layout = self.layout
        mat = context.material
        panel_node_draw(layout, mat, 'luxrender_material_output_node', 'Interior Volume')
        panel_node_draw(layout, mat, 'luxrender_material_output_node', 'Exterior Volume')

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return context.material.luxrender_material.nodetree
        except:
            return False


@LuxRenderAddon.addon_register_class
class ui_luxrender_material_node_emit(luxrender_material_base):
    bl_label = 'Light Emission'

    def draw(self, context):
        layout = self.layout
        mat = context.material
        panel_node_draw(layout, mat, 'luxrender_material_output_node', 'Emission')

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return context.material.luxrender_material.nodetree
        except:
            return False


@LuxRenderAddon.addon_register_class
class ui_luxcore_material(luxrender_material_base):
    """
    Material Emission Settings
    """

    bl_label = 'LuxCore specific settings'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('material',), 'luxcore_material', lambda: UseLuxCore() ),
    ]

    def draw(self, context):
        if not UseLuxCore():
            self.layout.label("Not available with API v1.x")

        super().draw(context)

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine != 'LUXRENDER_RENDER':
            return False
        try:
            return not context.material.luxrender_material.nodetree
        except:
            return False
