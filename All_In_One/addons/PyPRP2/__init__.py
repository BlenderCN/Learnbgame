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

bl_info = {
    'name': 'Plasma Development Environment',
    'author': 'PyPRP2 Project Team',
    'version': (1,),
    'blender': (2, 5, 7),
    'api': 36138,       # The official 2.57 build
    'location': 'View3D > Plasma',
    'description': 'Plasma engine settings and development tools.',
    'warning': 'beta',
#    'url': 'http://www.guildofwriters.com/wiki/',
    "category": "Learnbgame",
}


# this is a dirty dirty hack
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))


import bpy
from bpy.props import *
from bl_ui import properties_data_modifier,space_info
import headers
import world
import object
import geometry

def register():
    headers.register()
    world.register()
    object.register()
    geometry.register()
    bpy.types.Object.plasma_settings = PointerProperty(attr = 'plasma_settings',
                                                       type = object.PlasmaObjectSettings,
                                                       name = 'Plasma Settings',
                                                       description = 'Plasma Engine Object Settings')
    bpy.types.World.plasma_age = PointerProperty(attr = 'plasma_age',
                                                     type = world.PlasmaAgeSettings,
                                                     name = 'Plasma Settings',
                                                     description = 'Plasma Engine Object Settings')
    
    bpy.types.Scene.plasma_page = PointerProperty(attr = 'plasma_page',
                                                       type = world.PlasmaPageSettings,
                                                       name = 'Plasma Settings',
                                                       description = 'Plasma Engine Object Settings')

def unregister():
    geometry.unregister()
    object.unregister()
    world.unregister()
    headers.unregister()

if __name__ == "__main__":
    register()

