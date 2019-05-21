#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *
from PyHSPlasma import *
import random

randomint = random.randint(100, 200)


class PlasmaAgeSettings(bpy.types.PropertyGroup):
    name = StringProperty(name='Age Name', subtype='FILENAME')
    export_dir = StringProperty(name='Export Path', subtype='DIR_PATH')
    prefix = IntProperty(name='Unique Age Prefix', default=randomint, soft_min=0, soft_max=20000)
    plasmaversion = EnumProperty(items=(
                                      ('PVPRIME', 'Uru: Ages Beyond Myst', 'To D\'ni, Untìl Uru: Plasma 2.0 [59.11]'),
                                      ('PVPOTS', 'Uru: Complete Chronicles', 'Path of the Shell: Plasma 2.0 [59.12]'),
                                      ('PVMOUL', 'Myst Online: Uru Live', 'CWE, MOULagain, MagiQuest Online: Plasma 2.0 [70.9]'),
                                      ('PVEOA', 'Myst V: End of Ages', 'Crowthistle: Plasma 2.1'),
                                      ('PVHEX', 'Cosmic Osmo\'s Hex Isle', 'Plasma 3.0')
                                  ),
                                  name='Plasma Version',
                                  description='Plasma Engine Version',
                                  default='PVMOUL')
    isadvanced = BoolProperty(name='Advanced Settings', default=False)
    daylength = FloatProperty(name='Day Length', default=24.0, soft_min=0.0)    
    startdatetime = IntProperty(name='Start Date Time', default=0, soft_min=0)
    maxcapacity = IntProperty(name='Max Capacity', default=150, soft_min=0, soft_max=1000)
    lingertime = IntProperty(name='Linger Time', default=180, soft_min=0)
    releaseversion = IntProperty(name='Release Version', default=0, soft_min=0)
        
class PlasmaPageSettings(bpy.types.PropertyGroup):
    isexport = BoolProperty(name = 'Export', default = True, options = set(),
                        description = 'Export this scene to Plasma')
    load = BoolProperty(name = 'Load On Link', default = True, options = set(),
                        description = 'Load this scene when linking in')
    itinerant = BoolProperty(name = 'Intinerant', default = False, options = set(),
                        description = 'Do not unload this scene')

class plAgeSettingsPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'world'
    bl_label = 'Plasma Age'

    def draw(self,context):
        layout = self.layout
        view = context.world
        pl = view.plasma_age
        
        layout.prop(pl, 'name')
        layout.prop(pl, 'export_dir')
        layout.prop(pl, 'plasmaversion')
        layout.prop(pl, 'prefix')
        if pl.prefix >= 100 and pl.prefix <= 200:
            layout.label(text='This is a temporary development prefix.')
            layout.label(text='Please register for an official prefix.')
        layout.prop(pl, 'isadvanced')
        if pl.isadvanced:
            layout.prop(pl, 'daylength')
            layout.prop(pl, 'startdatetime')
            layout.prop(pl, 'maxcapacity')
            layout.prop(pl, 'lingertime')
            layout.prop(pl, 'releaseversion')

class plPagePanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_label = 'Plasma Scene'

    @classmethod
    def poll(self, context):
        return context.scene != None

    def draw_header(self, context):
        scn = context.scene
        self.layout.prop(scn.plasma_page, 'isexport', text = '')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        pl = scn.plasma_page

        layout.enabled = pl.isexport

        layout.prop(pl, 'load')
        layout.prop(pl, 'itinerant')

class plUnits(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_label = 'Plasma Units'

    @classmethod
    def poll(self, context):
        return context.scene != None

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.label(text = "One Blender Square =")
        layout.operator("scene.plasma_set_foot")
        layout.operator("scene.plasma_set_meter")

class PlasmaSetMeter(bpy.types.Operator):
    '''Set units so that one Blender square is equal to one meter in Plasma'''
    bl_idname = "scene.plasma_set_meter"
    bl_label = "Meter"

    def execute(self, context):
        units = context.scene.unit_settings
        units.system = "METRIC"
        units.scale_length = 0.3048
        return {'FINISHED'}

class PlasmaSetFoot(bpy.types.Operator):
    '''Set units so that one Blender square is equal to one foot in Plasma'''
    bl_idname = "scene.plasma_set_foot"
    bl_label = "Foot"
    
    def execute(self, context):
        units = context.scene.unit_settings
        units.system = "NONE"
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PlasmaAgeSettings)
    bpy.utils.register_class(PlasmaPageSettings)
    bpy.utils.register_class(plAgeSettingsPanel)
    bpy.utils.register_class(plPagePanel)
    bpy.utils.register_class(PlasmaSetMeter)
    bpy.utils.register_class(PlasmaSetFoot)
    bpy.utils.register_class(plUnits)

def unregister():
    bpy.utils.unregister_class(plPagePanel)
    bpy.utils.unregister_class(plAgeSettingsPanel)
    bpy.utils.unregister_class(PlasmaPageSettings)
    bpy.utils.unregister_class(PlasmaAgeSettings)
    bpy.utils.unregister_class(plUnits)
    bpy.utils.unregister_class(PlasmaSetFoot)
    bpy.utils.unregister_class(PlasmaSetMeter)
