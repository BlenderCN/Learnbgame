import bpy
from bpy.props import *
from . particle_force_base import ParticleForceNode

class AttractNode(ParticleForceNode, bpy.types.Node):
    bl_idname = "en_AttractNode"
    bl_label = "Attract"

    def create(self):
        self.new_input("en_VectorSocket", "Center", "center")
        self.new_input("en_FloatSocket", "Strength", "strength", value = 1)
        self.new_output("en_ParticleModifierSocket", "Force")

    def get_force_code(self):
        yield "_difference = center - LOCATION"
        yield "_distance = _difference.length"
        yield "FORCE = _difference.normalized() / _distance ** 2 * strength if _distance > 0 else mathutils.Vector((0, 0, 0))"