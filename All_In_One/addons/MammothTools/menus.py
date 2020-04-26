import bpy

class AddMammothComponent(bpy.types.Menu):
	bl_label = "Add Mammoth Component"
	bl_idname = "OBJECT_MT_add_mammoth_component_menu"

	def draw(self, context):
		layout = self.layout

		for key in bpy.mammothComponentsLayout.keys():
			layout.operator("wm.add_mammoth_component", text=key).component_name=key