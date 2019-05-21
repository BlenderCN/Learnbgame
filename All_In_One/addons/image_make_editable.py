bl_info = {
	"name": "Make Image Editable",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 79, 0),
	"location": "Image Editor > Properties > Make Image Editable",
	"description": "Makes images that have been saved to hard drive editable again.",
	"warning": "Always save before using. Can be slow if image is big. Data loss is possible.",
	"wiki_url": "",
	"category": "Image"
}

import bpy


def main(context, image):
	# Get image size
	size = tuple(i for i in image.size)
	# Copy pixels
	pixels = tuple(p for p in image.pixels)
	# Make new image as Generated to make editable again (this clears image)
	image_copy = context.blend_data.images.new(image.name, image.size[0], image.size[1])
	# Paste pixels into image
	image_copy.pixels = pixels
	return image_copy


class MakeImageEditableIE(bpy.types.Operator):
	"""Makes saved image editable again."""
	bl_idname = "image.make_image_editable_ie"
	bl_label = "Make Image Editable (IE)"
	"""
		REGISTER
			Display in info window and support redo toolbar panel
		UNDO
			Push an undo event, needed for operator redo
		BLOCKING
			Block anthing else from moving the cursor
		MACRO
			?
		GRAB_POINTER
			Enables wrapping when continuous grab is enabled
		PRESET
			Display a preset button with operator settings
		INTERNAL
			Removes operator from search results
	"""
	bl_options = {'REGISTER','UNDO'}

	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR'

	def execute(self, context):
		# Get active image from image editor
		image = context.space_data.image
		main(context, image)
		return {'FINISHED'}


class MakeImageEditableNE(bpy.types.Operator):
	"""Makes saved image editable again."""
	bl_idname = "image.make_image_editable_ne"
	bl_label = "Make Image Editable (NE)"
	"""
		REGISTER
			Display in info window and support redo toolbar panel
		UNDO
			Push an undo event, needed for operator redo
		BLOCKING
			Block anthing else from moving the cursor
		MACRO
			?
		GRAB_POINTER
			Enables wrapping when continuous grab is enabled
		PRESET
			Display a preset button with operator settings
		INTERNAL
			Removes operator from search results
	"""
	bl_options = {'REGISTER','UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object.active_material.node_tree.nodes.active is not None and context.active_object.active_material.node_tree.nodes.active.type == "TEX_IMAGE" and context.active_object.active_material.node_tree.nodes.active.image is not None

	def execute(self, context):
		# Get image from image node
		image = context.active_object.active_material.node_tree.nodes.active.image
		image_copy = main(context, image)
		context.active_object.active_material.node_tree.nodes.active.image = image_copy
		return {'FINISHED'}


def make_image_editable_button(self, context):
	layout = self.layout

	row = layout.row()
	row.operator("image.make_image_editable_ie")


def register():
	bpy.utils.register_class(MakeImageEditableNE)
	bpy.utils.register_class(MakeImageEditableIE)
	bpy.types.IMAGE_PT_image_properties.append(make_image_editable_button)


def unregister():
	bpy.types.IMAGE_PT_image_properties.remove(make_image_editable_button)
	bpy.utils.unregister_class(MakeImageEditableIE)
	bpy.utils.unregister_class(MakeImageEditableNE)
	


if __name__ == "__main__":
	register()

