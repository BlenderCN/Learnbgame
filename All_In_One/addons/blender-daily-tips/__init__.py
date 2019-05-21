# -----------------------------------------------------------------------------
# Blender Tips - Addon for daily blender tips
# Developed by Patrick W. Crawford
#

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
	"name":        "Daily Tips 'n Tricks",
	"description": "Addon for getting daily tips in blender",
	"author":      "Patrick W. Crawford",
	"version":     (0, 0, 2),
	"blender":     (2, 7, 8),
	"location":    "Popup in 3D view, or Help > Daily Tips",
	"warning":     "In Development",  
	"wiki_url":    "NA",
	"tracker_url": "theduckcow.com/dev/blender",
	"category":    "System"
	}


# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

# updater ops import, all setup in this file
from . import BDT_updater_ops as BDT_updater_ops


# -----------------------------------------------------------------------------
# MODULES
# -----------------------------------------------------------------------------


if "bpy" in locals():
	import importlib
	importlib.reload(conf)
	importlib.reload(BDT_ui)
	importlib.reload(BDT_requests)
	importlib.reload(BDT_updater_ops)

else:
	import bpy

	from . import (
		conf,
		BDT_ui,
		BDT_requests,
		BDT_updater_ops,
	)


# -----------------------------------------------------------------------------
# REGISTRATION
# -----------------------------------------------------------------------------


def register():

	conf.register()
	BDT_ui.register()
	BDT_updater_ops.register(bl_info)
	BDT_requests.register()


def unregister():

	conf.unregister()
	BDT_ui.unregister()
	BDT_requests.unregister()
	BDT_updater_ops.unregister()

