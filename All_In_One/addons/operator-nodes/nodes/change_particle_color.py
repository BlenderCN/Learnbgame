import bpy
from bpy.props import *
from .. base_node_types import ImperativeNode

mode_items = [
    ("SET", "Set", ""),
    ("RANDOMIZE", "Randomize", "")
]

class ChangeParticleColorNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_ChangeParticleColorNode"
    bl_label = "Change Color"

    mode: EnumProperty(name = "Mode", default = "SET",
        items = mode_items, update = ImperativeNode.refresh)

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        if self.mode == "SET":
            self.new_input("en_ColorSocket", "Color", "color")
        elif self.mode == "RANDOMIZE":
            self.new_input("en_FloatSocket", "Strength", "strength", value = 1)
        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def get_code(self):
        if self.mode == "SET":
            yield "PARTICLE.color = color"
        elif self.mode == "RANDOMIZE":
            yield "PARTICLE.color.r = random.random() * strength + PARTICLE.color.r * (1 - strength)"
            yield "PARTICLE.color.g = random.random() * strength + PARTICLE.color.g * (1 - strength)"
            yield "PARTICLE.color.b = random.random() * strength + PARTICLE.color.b * (1 - strength)"
        yield "NEXT"