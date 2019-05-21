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

def createModifier(context, modifier_class, name):
    ob = context.object
    pl = ob.plasma_settings
    mod = pl.modifiers.add()
    mclass = modifier_class.bl_idname.split('.')[1]
    mod.modclass = mclass
    collection = getattr(context.scene.plasma_modifiers, mclass)
    classdata = collection.add()
    classdata.type = mclass
    classdata.name = name
    mod.name = name
    return classdata

def dataNameCallback(self, context):
    if self.name == '':
        collection = getattr(context.scene.plasma_modifiers, self.type)
        new_name = 'unnamed-'
        i = 1
        while new_name+str(i) in collection.keys():
            i+=1
        self.name = 'unnamed-'+str(i)
