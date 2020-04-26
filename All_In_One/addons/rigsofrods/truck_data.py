# ##### BEGIN GPL LICENSE BLOCK #####
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
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

"""
    WHAT ARE PRESETS:
    Truckfile format uses directives 'set_node_defaults' and 'set_beam_defaults' to set parameters for following node/beam lines.
    This addon refers to the data as 'presets' because they can be (re)assigned and modified freely using UI.

    Author: Petr Ohlidal 2019
"""


class RoR_Truck(bpy.types.PropertyGroup):
    """ A RoR softbody physics object, traditionally called 'truck' """ 

    @classmethod
    def register(cls):
        cls.beam_presets = bpy.props.CollectionProperty(type=RoR_BeamPreset, name="Beam presets", description="Truckfile: `set_beam_defaults`")
        cls.active_beam_preset_index = bpy.props.IntProperty()

        cls.node_presets = bpy.props.CollectionProperty(type=RoR_NodePreset, name="Node presets", description="Truckfile: `set_node_defaults`")
        cls.active_node_preset_index = bpy.props.IntProperty()
        
        cls.active_node_options = bpy.props.StringProperty(description='Working copy of node options')
        
        cls.truckfile_path = bpy.props.StringProperty(description='Truckfile path')
        cls.truckfile_lines = bpy.props.CollectionProperty(type=RoR_TruckLine, description='Truckfile lines')
        cls.truckfile_nodes_pos = bpy.props.IntProperty(description='Truckfile line index of `nodes`')
        cls.truckfile_beams_pos = bpy.props.IntProperty(description='Truckfile line index of `beams`')
        cls.truckfile_cab_pos = bpy.props.IntProperty(description='Truckfile line index of `cab`')

        bpy.types.Object.ror_truck = bpy.props.PointerProperty(type=cls, name='Truck', description='Truck (Rigs of Rods)')

    @classmethod
    def unregister(cls):
        del bpy.types.Object.rig_def


class RoR_BeamPreset(bpy.types.PropertyGroup):
    """ A preset for physical parameters of softbody edge (aka 'beam' in RoR jargon) """

    @classmethod
    def register(cls):
        cls.args_line = bpy.props.StringProperty(name="Arguments", description="Text line with arguments")


class RoR_NodePreset(bpy.types.PropertyGroup):
    """ A preset for physical parameters of softbody vertex (aka 'node' in RoR jargon) """

    @classmethod
    def register(cls):
        cls.args_line = bpy.props.StringProperty(name="Arguments", description="Text line with arguments")
        
class RoR_TruckLine(bpy.types.PropertyGroup):
    """ Just a string wrapper """

    @classmethod
    def register(cls):
        cls.line = bpy.props.StringProperty(name="Line", description="Truckfile line")