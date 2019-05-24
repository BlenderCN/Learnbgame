# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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

bl_info = {
    "name": "Ghoul 2 format (.glm/.gla)",
    "author": "Willi Schinmeyer",
    "blender": (2, 6, 2),
    "api": 44136,
    "location": "File > Export",
    "description": "Imports and exports Ghoul 2 models and animations.",
    "warning": "",
    #"wiki_url": "",
    "tracker_url": "https://github.com/mrwonko/Blender-2.6-Ghoul-2-addon/issues",
    #"support": 'OFFICIAL',
    "category": "Learnbgame",
}

# reload won't work properly no matter what I do so I might as well ignore it.
from . import mrw_g2_operators
from . import mrw_g2_panels
import bpy

#called when the plugin is activated
def register():
    mrw_g2_panels.initG2Properties()
    mrw_g2_operators.register()
    bpy.utils.register_module(__name__)

#called when the plugin is deactivated
def unregister():
    #not removing the custom properties here - the user may not want to lose them just because he disabled the addon.
    mrw_g2_operators.unregister()
    bpy.utils.unregister_module(__name__)

# register it if script is called directly    
if __name__ == "__main__":
    register()