import bpy
from mathutils import Vector
from . particle_force_base import ParticleForceNode

class GravityNode(ParticleForceNode, bpy.types.Node):
    bl_idname = "en_GravityNode"
    bl_label = "Gravity"

    def create(self):
        self.new_input("en_VectorSocket", "Force", "force", value = (0, 0, -1))
        self.new_output("en_ParticleModifierSocket", "Force")

    def get_force_code(self):
        yield "FORCE = force"