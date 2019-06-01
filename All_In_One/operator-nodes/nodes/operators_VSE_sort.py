import bpy
from .. base_node_types import ImperativeNode

class SequencerSortNode(ImperativeNode, bpy.types.Node):
	bl_idname = "en_SequencerSortNode"
	bl_label = "Sort: start frame"

	def create(self):
		self.new_input("en_ControlFlowSocket", "Data in")

		self.new_output("en_ControlFlowSocket", "Data out", "data_out")

	def execute(self, context, payload):
		print("executing node", self.bl_idname)

		payload = sorted(payload, key=lambda strip: strip.frame_final_start)

		for link in self.outputs[0].links:
			link.to_node.execute(context, payload)
