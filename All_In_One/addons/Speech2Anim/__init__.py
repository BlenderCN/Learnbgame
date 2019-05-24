'''
Copyright (C) 2017 Gerard del Castillo
gerarddelcastillo@gmail.com

Created by Gerard del Castillo

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy

import sys
sys.path.append(bpy.utils.user_resource("SCRIPTS", "addons")+"/speech2anim/src")

import operators, panels, properties
bl_info = {
    "name": "Speech2Anim",
    "description": "Train models to use with Speech2Anim",
    "author": "Gerard del Castillo",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "Animation",
    "wiki_url": "",
    "category": "Learnbgame",
}


import traceback

def register():
    operators.register()
    panels.register()
    properties.register()
    #    print("=======================================================")
    #print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    print("register main init")

def unregister():
    operators.unregister()
    panels.unregister()
    properties.unregister()
    #except: traceback.print_exc()

    #print("Unregistered {}".format(bl_info["name"]))
    print("unregister main init")
