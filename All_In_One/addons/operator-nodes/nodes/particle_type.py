import bpy
from bpy.props import *
from .. base_node_types import DeclarativeNode

class ParticleTypeNode(DeclarativeNode, bpy.types.Node):
    bl_idname = "en_ParticleTypeNode"
    bl_label = "Particle Type"

    type_name: StringProperty(name = "Particle Type Name", default = "Main")

    def create(self):
        self.new_input("en_ParticleEmitterSocket", "Emitter")
        self.new_input("en_ParticleModifierSocket", "Modifiers")
        self.new_output("en_ParticleTypeSocket", "Particle Type")

    def draw(self, layout):
        layout.prop(self, "type_name", text = "", icon = "MOD_PARTICLES")