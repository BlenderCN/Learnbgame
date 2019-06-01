import os
import sys
import pkgutil
import importlib

if "bpy" in locals():

	importlib.reload(operator_anim_export)
	importlib.reload(operator_rig_import)
	importlib.reload(ui_panel_main)
	

else:
	import bpy

	from . import (
		operator_anim_export,
		operator_rig_import,
		ui_panel_main
	)


def register(bl_info):
	operator_anim_export.register()
	operator_rig_import.register()
	ui_panel_main.register()



def unregister(bl_info):
	operator_anim_export.unregister()
	operator_rig_import.unregister()
	ui_panel_main.unregister()