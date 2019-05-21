import bpy
from .. base_node_types import ImperativeNode

class SequencerMoveNode(ImperativeNode, bpy.types.Node):
	bl_idname = "en_SequencerMoveNode"
	bl_label = "Move up"

	def create(self):
		self.new_input("en_ControlFlowSocket", "Data in")

		self.new_output("en_ControlFlowSocket", "Data out", "data_out")

	def execute(self, context, payload):
		print("executing node", self.bl_idname)

		for strip in payload:
			strip.channel += 1

		for link in self.outputs[0].links:
			link.to_node.execute(context, payload)
