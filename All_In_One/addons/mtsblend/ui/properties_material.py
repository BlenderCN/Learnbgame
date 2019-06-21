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

from bpy.types import Menu, Panel

import bl_ui
from bl_ui.properties_material import MaterialButtonsPanel

from ..extensions_framework import util as efutil

from .. import MitsubaAddon
from ..ui import node_tree_selector_draw, panel_node_draw

from ..data.ior import ior_tree
from ..data.materials import medium_material_tree

cached_spp = None
cached_depth = None


# Add view buttons for viewcontrol to preview panels
def mts_use_alternate_matview(self, context):
    if context.scene.render.engine == 'MITSUBA_RENDER':
        mts_engine = context.scene.mitsuba_engine
        row = self.layout.row()
        row.prop(mts_engine, "preview_depth")
        row.prop(mts_engine, "preview_spp")

        global cached_depth
        global cached_spp

        if mts_engine.preview_depth != cached_depth or mts_engine.preview_spp != cached_spp:
            actualChange = cached_depth is not None
            cached_depth = mts_engine.preview_depth
            cached_spp = mts_engine.preview_spp

            if actualChange:
                efutil.write_config_value('mitsuba', 'defaults', 'preview_spp', str(cached_spp))
                efutil.write_config_value('mitsuba', 'defaults', 'preview_depth', str(cached_depth))

bl_ui.properties_material.MATERIAL_PT_preview.append(mts_use_alternate_matview)


def draw_generator(operator, m_names):

    def draw(self, context):
        sl = self.layout.row()

        for i, (m_name, m_index) in enumerate(m_names):
            if (i % 20 == 0):
                cl = sl.column()

            op = cl.operator(operator, text=m_name)
            op.index = m_index
            op.l_name = m_name

    return draw


def create_material_menu(name, opname, tree):
    submenus = []

    for label, items in tree:
        submenu_idname = 'MITSUBA_MT_%s_cat%s' % (name, label)
        submenus.append(
            MitsubaAddon.addon_register_class(type(
                submenu_idname,
                (Menu,),
                {
                    'bl_idname': submenu_idname,
                    'bl_label': label,
                    'draw': draw_generator(opname, items)
                }
            ))
        )

    return submenus


class mitsuba_menu_base:

    def draw(self, context):
        sl = self.layout

        for sm in self.submenus:
            sl.menu(sm.bl_idname)


@MitsubaAddon.addon_register_class
class MITSUBA_MT_material_presets(mitsuba_menu_base, Menu):
    bl_label = 'Material Presets'

    submenus = create_material_menu('medium_material', 'MATERIAL_OT_mitsuba_set_medium_material', medium_material_tree)


@MitsubaAddon.addon_register_class
class MITSUBA_MT_interior_ior_presets(mitsuba_menu_base, Menu):
    bl_label = 'Interior IOR Presets'

    submenus = create_material_menu('interior_ior', 'MATERIAL_OT_mitsuba_set_int_ior', ior_tree)


@MitsubaAddon.addon_register_class
class MITSUBA_MT_exterior_ior_presets(mitsuba_menu_base, Menu):
    bl_label = 'Exterior IOR Presets'

    submenus = create_material_menu('exterior_ior', 'MATERIAL_OT_mitsuba_set_ext_ior', ior_tree)


class mitsuba_material_node_panel(MaterialButtonsPanel, Panel):
    COMPAT_ENGINES = {'MITSUBA_RENDER'}
    display_node_inputs = []

    def draw(self, context):
        for node, node_input in self.display_node_inputs:
            panel_node_draw(self.layout, context, context.material, node, node_input)

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.material.mitsuba_nodes.nodetree


class mitsuba_material_base(MaterialButtonsPanel, Panel):
    COMPAT_ENGINES = {'MITSUBA_RENDER'}

    @classmethod
    def poll(cls, context):
        return super().poll(context) and not context.material.mitsuba_nodes.nodetree


@MitsubaAddon.addon_register_class
class MitsubaMaterial_PT_header(MaterialButtonsPanel, Panel):
    '''
    Material Editor UI Panel
    '''
    bl_label = ''
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'MITSUBA_RENDER'}

    @classmethod
    def poll(cls, context):
        # An exception, dont call the parent poll func because this manages materials for all engine types
        engine = context.scene.render.engine
        return (context.material or context.object) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=4)

            col = row.column(align=True)

            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.75)

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

        node_tree_selector_draw(layout, context, 'material')


@MitsubaAddon.addon_register_class
class MitsubaMaterialNode_PT_bsdf(mitsuba_material_node_panel):
    '''
    Material Node BSDF UI Panel
    '''

    bl_label = 'Surface Bsdf'
    display_node_inputs = [('MtsNodeMaterialOutput', 'Bsdf')]


@MitsubaAddon.addon_register_class
class MitsubaMaterialNode_PT_surface_interior(mitsuba_material_node_panel):
    '''
    Material Interior Settings
    '''

    bl_label = 'Surface Interior'
    display_node_inputs = [
        ('MtsNodeMaterialOutput', 'Subsurface'),
        ('MtsNodeMaterialOutput', 'Interior Medium'),
    ]


@MitsubaAddon.addon_register_class
class MitsubaMaterialNode_PT_exterior_medium(mitsuba_material_node_panel):
    '''
    Material Exterior Medium Settings
    '''

    bl_label = 'Exterior Medium'
    display_node_inputs = [('MtsNodeMaterialOutput', 'Exterior Medium')]


@MitsubaAddon.addon_register_class
class MitsubaMaterialNode_PT_emitter(mitsuba_material_node_panel):
    '''
    Material Node Emitter Settings
    '''

    bl_label = 'Surface Emitter'
    display_node_inputs = [('MtsNodeMaterialOutput', 'Emitter')]


@MitsubaAddon.addon_register_class
class MitsubaMaterial_PT_bsdf(mitsuba_material_base):
    '''
    Material BSDF UI Panel
    '''

    bl_label = 'Viewport'

    def draw(self, context):
        layout = self.layout
        mat = context.material
        layout.prop(mat, 'diffuse_color', text='Viewport Color')
