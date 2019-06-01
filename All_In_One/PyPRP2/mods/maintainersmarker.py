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
from modifier_tools import *

class MaintainersMarkerModifier(bpy.types.Operator):
    bl_idname = 'object.plmaintainersmarkermodifier'
    bl_label = 'Maintainer\'s Marker'
    bl_description = 'GPS Coordinate Marker'
    category = 'Markers'
    application = 'single'
    
    @staticmethod
    def Draw(layout, obj, mod):
        layout.prop(mod, 'calibration')

    @staticmethod
    def Export(rm, so, obj, mod):
        maintmarkmod = plMaintainersMarkerModifier(mod.name)
        maintmarkmod.calibration = int(mod.calibration)
        so.addModifier(maintmarkmod.key)
        rm.AddObject(so.key.location, maintmarkmod)

    def execute(self, context):
        ob = context.object
        createModifier(context, MaintainersMarkerModifier, ob.name)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return context.active_object

class MaintainersMarkerModifierData(bpy.types.PropertyGroup):
    name = StringProperty(update=dataNameCallback)
    type = StringProperty()
    owner = StringProperty()
    calibration = EnumProperty(
        items=(
            ('0', 'Broken', ''),
            ('1', 'Repaired', ''),
            ('2', 'Calibrated', '')
            ),
            name='Calibration',
            description='Calibration',
            default='0')

def register():
    bpy.utils.register_class(MaintainersMarkerModifierData)
    bpy.utils.register_class(MaintainersMarkerModifier)
    return [(MaintainersMarkerModifier, MaintainersMarkerModifierData)]

def unregister():
    bpy.utils.unregister_class(MaintainersMarkerModifier)
    bpy.utils.unregister_class(MaintainersMarkerModifierData)
