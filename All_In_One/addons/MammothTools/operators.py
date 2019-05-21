import bpy
from bpy.props import *

from . import components

class AddMammothComponent(bpy.types.Operator):
	bl_idname = "wm.add_mammoth_component"
	bl_label = "Add Mammoth Component"
	
	component_name = StringProperty(name="component_name")
	
	def execute(self, context):
		obj = context.object
		comp = getattr(obj, "mammoth_component_%s" % self.component_name)
		comp.internal___active = True
		context.area.tag_redraw()
		return {'FINISHED'}
	
class DeleteMammothComponent(bpy.types.Operator):
	bl_idname = "wm.delete_mammoth_component"
	bl_label = "Delete Mammoth Component"
	
	component_name = StringProperty(name="component_name")
	
	def execute(self, context):
		obj = context.object
		comp = getattr(obj, "mammoth_component_%s" % self.component_name)
		comp.internal___active = False
		context.area.tag_redraw()
		return {'FINISHED'}
	
class ReloadMammothComponents(bpy.types.Operator):
	bl_idname = "wm.reload_mammoth_components"
	bl_label = "Reload Mammoth Component"
	
	def execute(self, context):
		components.unload()
		components.loadLayout(context.scene.mammoth_components_settings.definitions_path)
		components.load()
		context.area.tag_redraw()
		return {'FINISHED'}