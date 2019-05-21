bl_info = {
	"name": "Dynamic Enum Example",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "View3D > Operator Search > Dynamic Enum Example",
	"description": "A very simple example addon to show how to create and use dynamic enums.",
	"warning": "",
	"wiki_url": "",
	"category": "Learnbgame",
}

import bpy
from bpy.props import EnumProperty

# get_enum_items needs to be declared before using it as a callback or Python will complain it doesn't exist
def get_enum_items(self, context):
	enum_list = []
	
	for index, obj in enumerate(context.selected_objects):
		enum_list.append( (obj.name, obj.name, "", "", index) )
	
	return enum_list


class DEE_OT_dynamic_enum_example(bpy.types.Operator):
	"""Gets a list of selected objects and prints the name of the selected enum item"""
	bl_idname = "object.dee_ot_dynamic_enum_example"
	bl_label = "Dynamic Enum Example"
	bl_options = {'REGISTER'}
	
	# Add dynamic enum as an annotation
	# get_enum_items is a callback function
	# get_enum_items takes two args: self and context
	# get_enum_items must return a list of tuples
	# Enum tuple format:
	# ("string_that_will_be_used_in_code", "User Friendly Item Name", "Description of item", "UI_ICON", index)
	obj_name : EnumProperty(
		items=get_enum_items,
		name="Object Name",
		description=""
	)

	@classmethod
	def poll(cls, context):
		return bool(context.selected_objects)
	
	# This just forces a dialog to display before running the operator
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		# To use the enum, simply use its variable name
		# It returns the "string_that_will_be_used_in_code" part of the tuple
		print(self.obj_name)
		
		return {'FINISHED'}


def register():
	bpy.utils.register_class(DEE_OT_dynamic_enum_example)

def unregister():
	bpy.utils.unregister_class(DEE_OT_dynamic_enum_example)

if __name__ == "__main__":
	register()
