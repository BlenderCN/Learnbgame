import bpy
from .. base_node_types import ImperativeNode

class ConditionNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_ConditionNode"
    bl_label = "Condition"

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        self.new_input("en_BooleanSocket", "Condition", "condition")

        self.new_output("en_ControlFlowSocket", "True", "IF_TRUE")
        self.new_output("en_ControlFlowSocket", "False", "IF_FALSE")

    def get_code(self):
        yield "if condition:"
        yield "    IF_TRUE"
        yield "else:"
        yield "    IF_FALSE"