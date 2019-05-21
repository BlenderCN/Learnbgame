bl_info = {
	'name': 'Mammoth Tools',
	'description': 'Various tools for adding components to objects and exporting the result as Mammoth JSON',
	'author': 'Kenton Hamaluik',
	'version': (0, 0, 11),
	'blender': (2, 78, 0),
	'location': 'Properties > Object',
	'warning': 'Still very much under development!',
	'wiki_url': 'https://github.com/BlazingMammothGames/mammoth_blender_tools',
	'tracker_url': 'https://github.com/BlazingMammothGames/mammoth_blender_tools/issues',
	'support': 'TESTING',
	'category': 'Game Engine'
}

if "bpy" in locals():
	import imp
	imp.reload(panels)
	imp.reload(components)
	imp.reload(settings)
	imp.reload(operators)
	imp.reload(menus)
	imp.reload(exporter)
	print("Reloaded mammoth tools")
else:
	from . import panels
	from . import components
	from . import settings
	from . import operators
	from . import menus
	from . import exporter
	print("Imported mammoth tools")

import bpy
from bpy.props import *

def register():
	bpy.utils.register_class(panels.MammothSettingsPanel)
	bpy.utils.register_class(panels.MammothTransformPanel)
	bpy.utils.register_class(panels.MammothComponentsPanel)
	bpy.utils.register_class(panels.MammothDataPanel)
	bpy.utils.register_class(settings.MammothComponents)
	bpy.types.Scene.mammoth_components_settings = PointerProperty(type=settings.MammothComponents)
	bpy.utils.register_class(operators.AddMammothComponent)
	bpy.utils.register_class(operators.DeleteMammothComponent)
	bpy.utils.register_class(operators.ReloadMammothComponents)
	bpy.utils.register_class(menus.AddMammothComponent)
	components.load()
	bpy.utils.register_class(exporter.MammothExporter)

def unregister():
	bpy.utils.unregister_class(panels.MammothSettingsPanel)
	bpy.utils.unregister_class(panels.MammothTransformPanel)
	bpy.utils.unregister_class(panels.MammothComponentsPanel)
	bpy.utils.unregister_class(panels.MammothDataPanel)
	bpy.utils.unregister_class(settings.MammothComponents)
	del bpy.types.Scene.mammoth_components_settings
	bpy.utils.unregister_class(operators.AddMammothComponent)
	bpy.utils.unregister_class(operators.DeleteMammothComponent)
	bpy.utils.unregister_class(operators.ReloadMammothComponents)
	bpy.utils.unregister_class(menus.AddMammothComponent)
	components.unload()
	bpy.utils.unregister_class(exporter.MammothExporter)

if __name__ == '__main__':
	register()