import bpy
from bpy.props import *
from .. base_node_types import ImperativeNode

mode_items = [
    ("SET", "Set", ""),
    ("RANDOMIZE", "Randomize", ""),
    ("RELATIVE", "Relative", "")
]

class ChangeParticleVelocityNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_ChangeParticleVelocityNode"
    bl_label = "Change Velocity"

    mode: EnumProperty(name = "Mode", default = "RANDOMIZE",
        items = mode_items, update = ImperativeNode.refresh)

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        if self.mode == "SET":
            self.new_input("en_FloatSocket", "Velocity", "velocity")
        elif self.mode == "RANDOMIZE":
            self.new_input("en_FloatSocket", "Strength", "strength", value = 1)
        elif self.mode == "RELATIVE":
            self.new_input("en_FloatSocket", "Factor", "factor", value = 1)
        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def get_code(self):
        if self.mode == "SET":
                yield "PARTICLE.velocity = PARTICLE.velocity.normalized() * velocity"
        elif self.mode == "RANDOMIZE":
            yield "PARTICLE.velocity *= (random.random() + 0.5) ** strength"
        elif self.mode == "RELATIVE":
            yield "PARTICLE.velocity *= factor"
        yield "NEXT"