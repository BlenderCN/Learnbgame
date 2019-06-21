import bpy
from bpy.props import *
from .. base_node_types import ImperativeNode

class SetObjectAttributeNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_SetObjectAttributeNode"
    bl_label = "Set Object Attribute"

    attribute: StringProperty(name = "Attribute")

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        self.new_input("en_ObjectSocket", "Object", "object")
        self.new_input("en_FloatSocket", "Value", "value")

        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def draw(self, layout):
        layout.prop(self, "attribute", text = "", icon = "RNA")

    def get_code(self):
        yield "if object is not None:"
        yield "    object.{} = value".format(self.attribute)
        yield "NEXT"