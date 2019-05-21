import bpy
from .. base_node_types import FunctionalNode

class ParticleInfoNode(FunctionalNode, bpy.types.Node):
    bl_idname = "en_ParticleInfoNode"
    bl_label = "Particle Info"

    def create(self):
        self.new_output("en_VectorSocket", "Position", "position")
        self.new_output("en_VectorSocket", "Velocity", "velocity")

    def get_code(self, required):
        if self.outputs["Position"] in required:
            yield "position = PARTICLE.location"
        if self.outputs["Velocity"] in required:
            yield "velocity = PARTICLE.velocity"