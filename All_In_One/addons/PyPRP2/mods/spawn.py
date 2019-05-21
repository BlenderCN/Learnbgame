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

class SpawnModifier(bpy.types.Operator):
    bl_idname = 'object.plspawnmodifier'
    bl_label = 'Link-In Point'
    bl_description = 'Starting point for a player'
    category = 'Avatar'
    application = 'single'
    
    @staticmethod
    def Draw(layout, obj, mod):
        pass

    @staticmethod
    def Export(rm, so, obj, mod):
        spawnmod = plSpawnModifier(mod.name)
        so.addModifier(spawnmod.key)
        rm.AddObject(so.key.location, spawnmod)

    def execute(self, context):
        ob = context.object
        createModifier(context, SpawnModifier, ob.name)
        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        return context.active_object

class SpawnModifierData(bpy.types.PropertyGroup):
    name = StringProperty(update=dataNameCallback)
    type = StringProperty()
    owner = StringProperty()

def register():
    bpy.utils.register_class(SpawnModifierData)
    bpy.utils.register_class(SpawnModifier)
    return [(SpawnModifier, SpawnModifierData)]

def unregister():
    bpy.utils.unregister_class(SpawnModifier)
    bpy.utils.unregister_class(SpawnModifierData)
