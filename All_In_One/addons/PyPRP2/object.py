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
import modifiers
import physics

class PlasmaObjectSettings(bpy.types.PropertyGroup):
    physics = PointerProperty(attr = 'physics', type = physics.PlasmaPhysicsSettings)
    modifiers = CollectionProperty(attr = 'modifiers', type = modifiers.PlasmaModifierLink)

    drawableoverride = BoolProperty(name="Drawable Override", default = False)
    activemodifier = IntProperty(attr = 'activemodifier', default = 0)
    isdrawable = BoolProperty(name="Is Drawable", default=True, description="Export drawable for this object")
    isdynamic = BoolProperty(name="Dynamic", default=False)
    noexport = BoolProperty(name="Disable Export", default=False, description="Do not export this object to an age or prp")

class plObject(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Plasma Object"

    def draw(self,context):
        layout = self.layout
        view = context.object
        pl = view.plasma_settings
        self.layout.prop(pl, "isdrawable")
        self.layout.prop(pl, "isdynamic")
        self.layout.prop(pl, "noexport")

def register():
    bpy.utils.register_class(plObject)
    modifiers.register()
    physics.register()
    bpy.utils.register_class(PlasmaObjectSettings)

def unregister():
    bpy.utils.unregister_class(PlasmaObjectSettings)
    physics.unregister()
    modifiers.unregister()
    bpy.utils.unregister_class(plObject)

