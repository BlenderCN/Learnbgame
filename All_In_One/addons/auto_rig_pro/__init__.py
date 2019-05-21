# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Auto-Rig Pro",
	"author": "Artell",
	"version": (3, 1, 8),
	"blender": (2, 7, 9),
	"location": "3D View > Properties> Auto-Rig Pro",
	"description": "Automatic rig creation based on reference bones. Picker panel, smart features, various tools",
	"tracker_url": "https://blendermarket.com/products/auto-rig-pro?ref=46",	
	"category": "Learnbgame"
} 


if "bpy" in locals():
	import importlib
	if "rig_functions" in locals():
		importlib.reload(rig_functions)
	if "auto_rig" in locals():
		importlib.reload(auto_rig)
	if "auto_rig_smart" in locals():
		importlib.reload(auto_rig_smart)
	if "auto_rig_remap" in locals():
		importlib.reload(auto_rig_remap)
	if "auto_rig_ge" in locals():
		importlib.reload(auto_rig_ge)

import bpy
from bpy.app.handlers import persistent
#import script files
from . import rig_functions
from . import auto_rig
from . import auto_rig_smart
from . import auto_rig_remap
from . import auto_rig_ge



def register():	   
	#register classes
	bpy.utils.register_module(__name__)
	#register properties and misc
	auto_rig.register()
	auto_rig_smart.register()
	rig_functions.register()
	auto_rig_remap.register()
	auto_rig_ge.register()
	
	
  
	

def unregister():	
	#unregister classes
	bpy.utils.unregister_module(__name__)
	#unregister properties and misc
	auto_rig.unregister()
	auto_rig_smart.unregister()
	rig_functions.unregister()
	auto_rig_remap.unregister()
	auto_rig_ge.unregister()
	
	
	
	

if __name__ == "__main__":
	register()