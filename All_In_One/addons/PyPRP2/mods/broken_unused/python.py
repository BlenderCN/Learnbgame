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
from PyHSPlasma import *

class PythonModifier(bpy.types.Operator):
    bl_idname = 'object.plpythonmodifier'
    bl_label = 'Python File'
    category = 'Logic'

    @staticmethod
    def InitProperties(mod):
        mod.BoolProperty(attr="testprop", name="Test Prop", description="Turning this on does precisely nothing.", default=False)

    @staticmethod
    def Export(rm, so, mod):
        #example of exporting
        #plasmaclass.fTest = mod.testprop
        pass

    def execute(self, context):
        ob = context.object
        pl = ob.plasma_settings
        mod = pl.modifiers.add()
        mod.name = ob.name
        PythonModifier.InitProperties(mod)
        mod.modclass = PythonModifier.bl_idname.split('.')[1]
        return {'FINISHED'}

class PythonFileModPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'constraint'
    bl_label = 'Python File Modifier'

    @classmethod
    def poll(self, context):
        ob = context.active_object
        if not ob is None:
            pl = ob.plasma_settings
            if len(pl.modifiers) > 0:
                return pl.modifiers[pl.activemodifier].modclass == PythonModifier.bl_idname.split('.')[1]
        return False

    def draw(self, context):
        layout = self.layout
        
        ob = context.active_object
        pl = ob.plasma_settings
        plmod = pl.modifiers[pl.activemodifier]
        layout.prop(plmod, "testprop")
        
        layout.label(text = 'STOP!')
        layout.label(text = 'An 11/10 neurologists warn against looking at this panel.')
        layout.label(text = 'Side effects include pain, agony, and the ability to see')
        layout.label(text = 'only 4-dimensional objects.')
        layout.label(text = 'For your safety (and sanity), this panel has been hidden.')

def register():
    bpy.types.register(PythonModifier)
    bpy.types.register(PythonFileModPanel)
    return [PythonModifier]

def unregister():
    bpy.types.unregister(PythonModifier)
    bpy.types.unregister(PythonFileModPanel)
