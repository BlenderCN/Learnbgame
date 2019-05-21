import bpy
bl_info = {
	"name": "Bake Helper",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 78, 0),
	"location": "Properties > Render Tab > Bake Helper Section",
	"description": "Sets up object's materials for baking",
	"warning": "",
	"wiki_url": "",
	"category": "Render",
}


def deselectAllNodes(nodes):
	for node in nodes:
		node.select = False


def getImage(name, size, images):
	"""
	Checks given images for a certain image and returns it, or
	makes new one if it doesn't exist
	"""
	# Check for Image
	image = images.get(name, None)
	# If image doesn't exist
	if image is None:
		# Make a new image with specified size
		image = images.new(name, size, size)

	return image


def getNode(name, nodes, node_type):
	"""
	Checks for given node_name and returns it if it exists in node_tree, or
	makes a new one if it doesn't exist
	"""
	node = nodes.get(name, None)
	# If node doesnt exist
	if node is None:
		# Add node
		node = nodes.new(node_type)
		node.name = name
		node.label = name
		# Deselect since it automatically gets selected when created
		node.select = False

	return node


def prepareBake(context):
	# Loop thru selected objects
	for selected_object in context.selected_objects:
		# Loop thru material slots
		for material_slot in selected_object.material_slots:
			material = material_slot.material
			node_tree = material.node_tree
			# padding for positioning nodes
			padding = 20

			# Get or create necessary nodes
			mat_output = getNode(
				"Material Output",
				node_tree.nodes,
				"ShaderNodeOutputMaterial"
			)
			bake_helper_node = getNode(
				"BakeHelperNode",
				node_tree.nodes,
				"ShaderNodeTexImage"
			)
			bake_helper_uv = getNode(
				"BakeHelperUV",
				node_tree.nodes,
				"ShaderNodeUVMap"
			)

			# Create BakeHelper image if necessary
			if bake_helper_node.image is None:
				bake_helper_image = getImage(
					"BakeHelper",
					1024,
					context.blend_data.images
				)
				#
				bake_helper_node.image = bake_helper_image

			# Set locations
			bake_helper_uv.location = (
				mat_output.location[0],
				mat_output.location[1] - mat_output.height
			)
			bake_helper_node.location = (
				bake_helper_uv.location[0] + bake_helper_uv.width + padding,
				bake_helper_uv.location[1]
			)

			# Link UV node to BakeHelperNode
			node_tree.links.new(bake_helper_node.inputs["Vector"], bake_helper_uv.outputs["UV"])

			# Deselect all nodes
			deselectAllNodes(node_tree.nodes)

			# Select BakeHelperNode
			bake_helper_node.select = True
			node_tree.nodes.active = bake_helper_node


class PrepareBakeOperator(bpy.types.Operator):
	"""Select BakeHelper's nodes and create them if necessary"""
	bl_idname = "object.prepare_bake"
	bl_label = "Prepare Bake"


	@classmethod
	def poll(cls, context):
		return context.active_object is not None


	def execute(self, context):
		prepareBake(context)
		return {'FINISHED'}


class BakeHelperPanel(bpy.types.Panel):
	"""Creates BakeHelperPanel in the Properties window/Render Tab"""
	bl_label = "Bake Helper"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"


	def draw(self, context):
		layout = self.layout

		row = layout.row()
		row.operator("object.prepare_bake", text = "Prepare Bake")
		row = layout.row()
		row.label(text="Bake Checklist")

		row = layout.row()
		# If active object has at least one UV
		if len(bpy.context.active_object.data.uv_layers):
			row.label(text="This model has a UV", icon="FILE_TICK")
		else:
			row.label(text="This model doesn't have a UV!", icon="CANCEL")


classes = [PrepareBakeOperator, BakeHelperPanel]


def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
