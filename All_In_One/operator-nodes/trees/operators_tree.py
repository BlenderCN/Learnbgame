import bpy
from . base import NodeTree
from .. base_node_types import ImperativeNode, DeclarativeNode

class OperatorsTree(NodeTree, bpy.types.NodeTree):
	bl_idname = "en_OperatorsTree"
	bl_icon = "PMARKER_ACT"
	bl_label = "Operators"

	def execute(self, context):
		print("executing tree")

		for node in self.nodes:
			if isinstance(node, DeclarativeNode):
				print("calling node", node.bl_idname)
				node.execute(context)
				break
