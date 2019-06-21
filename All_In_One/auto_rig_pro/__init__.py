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
	"version": (3, 41, 20),
	"blender": (2, 80, 0),
	"location": "3D View > Properties> Auto-Rig Pro",
	"description": "[BETA VERSION FOR BLENDER 2.8 ONLY] Automatic rig generation based on reference bones and various tools",
	"tracker_url": "https://blendermarket.com/products/auto-rig-pro?ref=46",	
	"category": "Animation",
	"warning": "Experimental"}


if "bpy" in locals():
	import importlib
	if "auto_rig_prefs" in locals():
		importlib.reload(auto_rig_prefs)
	if "rig_functions" in locals():
		importlib.reload(rig_functions)
	if "auto_rig_datas" in locals():
		importlib.reload(auto_rig_datas)
	if "auto_rig" in locals():
		importlib.reload(auto_rig)
	if "auto_rig_smart" in locals():
		importlib.reload(auto_rig_smart)
	if "auto_rig_remap" in locals():
		importlib.reload(auto_rig_remap)
	if "auto_rig_ge" in locals():
		importlib.reload(auto_rig_ge)
	if "arp_fbx_init" in locals():
		importlib.reload(arp_fbx_init)


import bpy
from bpy.app.handlers import persistent
#import script files
from . import auto_rig_prefs
from . import rig_functions
from . import auto_rig
from . import auto_rig_smart
from . import auto_rig_remap
from . import auto_rig_ge

from .export_fbx import arp_fbx_init
	


def menu_func_export(self, context):
	self.layout.operator(auto_rig_ge.ARP_OT_GE_export_fbx_panel.bl_idname, text="Auto-Rig Pro FBX (.fbx)")	
	

def register():	 
	auto_rig_prefs.register()
	auto_rig.register()
	auto_rig_smart.register()	
	auto_rig_remap.register()
	auto_rig_ge.register()
	rig_functions.register()
	arp_fbx_init.register()
	
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
	
	

def unregister():
	auto_rig_prefs.unregister()
	auto_rig.unregister()
	auto_rig_smart.unregister()	
	auto_rig_remap.unregister()
	auto_rig_ge.unregister()
	rig_functions.unregister()
	arp_fbx_init.unregister()
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
		
	

if __name__ == "__main__":
	register()