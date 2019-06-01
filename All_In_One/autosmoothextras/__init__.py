'''
Copyright (C) 2017 NIKO RUMMUKAINEN
niko.rummukainen@gmail.com

Created by Niko Rummukainen

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

bl_info = {
    "name": "Auto Smooth Extras",
    "description": "Enhances mesh property normals Auto Smooth function with possibility mark Sharp edges, Bewel weights & Edge greasing by auto smooth angle",
    "author": "Niko Rummukainen",
    "version": (0, 4, 1),
    "blender": (2, 78, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Learnbgame",
}

import bpy
from . import addon_updater_ops

#updater imports and setup
from .addon_updater import Updater as updater # for example
updater.user = "nikorummukainen"
updater.repo = "blender-addon-updater"
updater.current_version = bl_info["version"]

class ASEExtras(bpy.types.AddonPreferences):
	bl_idname = __package__

	# addon updater preferences

	auto_check_update = bpy.props.BoolProperty(
		name = "Auto-check for Update",
		description = "If enabled, auto-check for updates using an interval",
		default = False,
		)
	
	updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description = "Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description = "Number of days between checking for updates",
		default=7,
		min=0,
		)
	updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description = "Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description = "Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)

	def draw(self, context):
		
		layout = self.layout

		# updater draw function
		addon_updater_ops.update_settings_ui(self,context)

# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

def register():
	# addon updater code and configurations
	# in case of broken version, try to register the updater first
	# so that users can revert back to a working version
    addon_updater_ops.register(bl_info)
    
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
	# addon updater unregister
    addon_updater_ops.unregister()

    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))