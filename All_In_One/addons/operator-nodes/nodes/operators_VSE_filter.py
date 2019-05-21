import bpy
from .. base_node_types import ImperativeNode

class SequencerFilterNode(ImperativeNode, bpy.types.Node):
	bl_idname = "en_SequencerFilterNode"
	bl_label = "Filter odd"

	def create(self):
		self.new_input("en_ControlFlowSocket", "Data in")

		self.new_output("en_ControlFlowSocket", "Data out", "data_out")

	def execute(self, context, payload):
		print("executing node", self.bl_idname)

		payload = payload[1::2]

		for link in self.outputs[0].links:
			link.to_node.execute(context, payload)
