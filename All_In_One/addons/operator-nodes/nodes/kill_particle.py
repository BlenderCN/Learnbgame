import bpy
from .. base_node_types import ImperativeNode

class KillParticleNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_KillParticleNode"
    bl_label = "Kill Particle"

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")

    def get_code(self):
        yield "KILL"