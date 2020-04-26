# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Procedural building generator
#  Copyright (C) 2019 Luka Simic
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from bpy.types import Panel, PropertyGroup
from bpy.props import FloatProperty, BoolProperty, EnumProperty, IntProperty


class PBGPropertyGroup(PropertyGroup):
    # TODO: docstring

    building_width = FloatProperty(
        name="Building width",
        default=25.0
    )

    building_depth = FloatProperty(
        name="Building depth",
        default=15.0
    )

    building_chamfer = FloatProperty(
        name="Chamfer size",
        default=1
    )

    building_wedge_depth = FloatProperty(
        name="Wedge depth",
        default=1.5
    )

    building_wedge_width = FloatProperty(
        name="Wedge width",
        default=8
    )

    floor_first_offset = FloatProperty(
        name="FIrst floor offset",
        default=0.7
    )

    floor_height = FloatProperty(
        name="Floor height",
        default=3
    )

    floor_count = IntProperty(
        name="Number of floors",
        default=2
    )

    floor_separator_include = BoolProperty(
        name="Separator between floors",
        default=True
    )

    floor_separator_height = FloatProperty(
        name="Separator height",
        default=0.5
    )

    floor_separator_width = FloatProperty(
        name="Separator width",
        default=0.5
    )

    window_width = FloatProperty(
        name="Total window width",
        default=1.2
    )

    distance_window_window = FloatProperty(
        name="Distance between windows",
        default=2.5
    )

    generate_pillar = BoolProperty(
        name="Generate Pillar",
        default=True
    )

    distance_window_pillar = FloatProperty(
        name="Distance Window to Pillar",
        default=0.8
    )

    pillar_width = FloatProperty(
        name="Pillar width",
        default=0.2
    )

    pillar_depth = FloatProperty(
        name="Pillar depth",
        default=0.15
    )

    pillar_chamfer = FloatProperty(
        name="Pillar Chamfer",
        default=0.05
    )

    pillar_offset_height = FloatProperty(
        name="Pillar Offset Height",
        default=0.7
    )

    pillar_offset_size = FloatProperty(
        name="Pillar Offset Size",
        default=0.05
    )

    pillar_include_floor_separator = BoolProperty(
        name="Include floor separator",
        default=True
    )

    pillar_include_first_floor = BoolProperty(
        name="Include first floor",
        default=True
    )

    wall_types = [
        ("FLAT", "FLAT", "", 0),
        ("ROWS", "ROWS", "", 1)
    ]

    wall_type = EnumProperty(
        items=wall_types,
        default="ROWS"
    )

    wall_mortar_size = FloatProperty(
        name="Mortar size",
        default=0.02
    )

    wall_section_size = FloatProperty(
        name="Brick section size",
        default=0.04
    )

    wall_row_count = IntProperty(
        name="Rows per floor",
        default=7
    )

    wall_offset_size = FloatProperty(
        name="Wall offset size",
        default=0.1
    )

    wall_offset_type = EnumProperty(
        items=wall_types,
        default="ROWS"
    )

    wall_offset_mortar_size = FloatProperty(
        name="Offset Mortar size",
        default=0.03
    )

    wall_offset_section_size = FloatProperty(
        name="Offset Brick section size",
        default=0.06
    )

    wall_offset_row_count = IntProperty(
        name="Offset Rows per floor",
        default=3
    )

    window_height = FloatProperty(
        name="Window total height",
        default=1.0
    )

    window_offset = FloatProperty(
        name="Window offset",
        default=0.5
    )

    window_under_types = [
        ("WALL", "WALL", "", 0),
        ("PILLARS", "PILLARS", "", 1),
        ("SIMPLE", "SIMPLE", "", 2),
        ("SINE", "SINE", "", 3),
        ("CYCLOID", "CYCLOID", "", 4)
    ]

    windows_under_type = EnumProperty(
        items=window_under_types,
        default="WALL"
    )

    windows_under_width = FloatProperty(
        name="under window offset width",
        default=0.1
    )

    windows_under_height = FloatProperty(
        name="Under Window offset height",
        default=0.1
    )

    windows_under_depth = FloatProperty(
        name="under Window offset depth",
        default=0.05
    )

    windows_under_inset_depth = FloatProperty(
        name="under Window inset depth",
        default=0.1
    )

    windows_under_amplitude = FloatProperty(
        name="under Window amplitude",
        default=0.05
    )

    windows_under_period_count = IntProperty(
        name="under Window period count",
        default=8
    )

    windows_under_simple_width = FloatProperty(
        name="Under window simple width",
        default=0.04
    )

    windows_under_simple_depth = FloatProperty(
        name="Under window simple depth",
        default=0.03
    )

    windows_under_pillar_base_diameter = FloatProperty(
        name="Under window pillar base diameter",
        default=0.08
    )

    windows_under_pillar_base_height = FloatProperty(
        name="Under window pillar base height",
        default=0.04
    )

    windows_under_pillar_min_diameter = FloatProperty(
        name="Under window pillar min diameter",
        default=0.05
    )

    windows_under_pillar_max_diameter = FloatProperty(
        name="Under window pillar max diameter",
        default=0.08
    )

    door_size = FloatProperty(
        name="Door size",
        default=2.5
    )
# end PBGPropertyGroup


class PBGToolbarGeneralPanel(Panel):
    # TODO: docstring
    bl_label = "General Settings"
    bl_category = "PBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.PBGPropertyGroup

        col = layout.column(align=True)
        col.label(text="Overall Building Dimensions")
        col.prop(properties, "building_width")
        col.prop(properties, "building_depth")
        col.prop(properties, "building_chamfer")
        col.prop(properties, "building_wedge_depth")
        col.prop(properties, "building_wedge_width")

        col.label(text="Floor and separator layout")
        col.prop(properties, "floor_count")
        col.prop(properties, "floor_height")
        col.prop(properties, "floor_first_offset")
        col.prop(properties, "floor_separator_include")
        col.prop(properties, "floor_separator_width")
        col.prop(properties, "floor_separator_height")
    # end draw
# end PBGToolbarPanel


class PBGToolbarLayoutPanel(Panel):
    # TODO: docstring
    bl_label = "Layout Settings"
    bl_category = "PBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.PBGPropertyGroup

        col = layout.column(align=True)
        col.prop(properties, "distance_window_window")
        col.prop(properties, "distance_window_pillar")
    # end draw
# end PBGLayoutPanel


class PBGToolbarPillarPanel(Panel):
    # TODO: docstring
    bl_label = "Pillar Settings"
    bl_category = "PBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.PBGPropertyGroup

        col = layout.column(align=True)
        col.prop(properties, "generate_pillar")
        col.prop(properties, "pillar_width")
        col.prop(properties, "pillar_depth")
        col.prop(properties, "pillar_chamfer")
        col.prop(properties, "pillar_offset_height")
        col.prop(properties, "pillar_offset_size")
        col.prop(properties, "pillar_include_floor_separator")
        col.prop(properties, "pillar_include_first_floor")
    # end draw
# end PBGPillarPanel


class PBGToolbarWallPanel(Panel):
    # TODO: docstring
    bl_label = "Wall settings"
    bl_category = "PBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.PBGPropertyGroup

        col = layout.column(align=True)
        col.label(text="Wall settings")
        col.prop(properties, "wall_type")
        col.prop(properties, "wall_mortar_size")
        col.prop(properties, "wall_section_size")
        col.prop(properties, "wall_row_count")

        col.label(text="First floor offset settings")
        col.prop(properties, "wall_offset_size")
        col.prop(properties, "wall_offset_type")
        col.prop(properties, "wall_offset_mortar_size")
        col.prop(properties, "wall_offset_section_size")
        col.prop(properties, "wall_offset_row_count")
    # end draw
# end PBGToolbarWallPanel


class PBGToolbarWindowPanel(Panel):
    bl_label = "Window Settings"
    bl_category = "PBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.PBGPropertyGroup

        col = layout.column(align=True)
        col.label(text="Overall window dimensions")
        col.prop(properties, "window_width")
        col.prop(properties, "window_height")
        col.prop(properties, "window_offset")

        col.label(text="Under windows area")
        col.prop(properties, "windows_under_type")
        col.prop(properties, "windows_under_width")
        col.prop(properties, "windows_under_height")
        col.prop(properties, "windows_under_depth")
        col.prop(properties, "windows_under_inset_depth")

        col.label(text="Sine/Cycloid params")
        col.prop(properties, "windows_under_amplitude")
        col.prop(properties, "windows_under_period_count")

        col.label(text="Simple params")
        col.prop(properties, "windows_under_simple_width")
        col.prop(properties, "windows_under_simple_depth")

        col.label(text="Pillar params")
        col.prop(properties, "windows_under_pillar_base_diameter")
        col.prop(properties, "windows_under_pillar_base_height")
        col.prop(properties, "windows_under_pillar_min_diameter")
        col.prop(properties, "windows_under_pillar_max_diameter")
    # end draw
# end PBGToolbarWindowPanel


class PBGToolbarGeneratePanel(Panel):
    # TODO: docstring
    bl_label = "Generate"
    bl_category = "PBG"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("pbg.generate_building", text="Generate")
    # end draw
# end PBGGeneratePanel
