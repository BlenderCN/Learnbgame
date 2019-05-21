import bpy
from .. base_node_types import DeclarativeNode

class SequencerSelectionNode(DeclarativeNode, bpy.types.Node):
	bl_idname = "en_SequencerSelection"
	bl_label = "Selected strips"

	def create(self):
		self.new_output("en_ControlFlowSocket", "Data out", "data_out")

	def execute(self, context):
		print("executing node", self.bl_idname)

		payload = context.selected_sequences

		for link in self.outputs[0].links:
			link.to_node.execute(context, payload)
