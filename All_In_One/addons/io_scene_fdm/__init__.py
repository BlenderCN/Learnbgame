bl_info = {
  "name": "Flightgear Plane & FDM",
  "author": "Thomas Geymayer",
  "version": (0, 1, 'a'),
  "blender": (2, 60, 7),
  "api": 42503,
#  "location": "File > Import-Export",
  "description": "Create and export FlightGear FDM and plane",
  "warning": "Pre Alpha",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Import-Export"
}

# Blender module reloading...
if "bpy" in locals():
	import imp
	imp.reload(props)
	imp.reload(ui)
	imp.reload(export)
else:
	import bpy
	from io_scene_fdm import props
	from io_scene_fdm import ui
	from io_scene_fdm import export
	

def menu_func_export(self, context):
	self.layout.operator(export.Exporter.bl_idname, text='Flightgear FDM (.xml)')

def register():
	bpy.utils.register_module(__name__)
	props.register()
	bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
	register()