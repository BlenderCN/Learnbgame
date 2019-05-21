import bpy
from random import random
from mathutils import Vector
from . particle_emitter_base import ParticleEmitterNode

class PointEmitterNode(ParticleEmitterNode, bpy.types.Node):
    bl_idname = "en_PointEmitterNode"
    bl_label = "Point Emitter"

    def create(self):
        self.new_input("en_VectorSocket", "Location", "location")
        self.new_input("en_FloatSocket", "Rate", "rate", value = 5)
        self.new_input("en_FloatSocket", "Randomness", "randomness")

        self.new_output("en_ControlFlowSocket", "On Birth")
        self.new_output("en_ParticleEmitterSocket", "Emitter")

    def get_emit_code(self):
        yield "EMITTED = self.emit(location, rate, randomness, START_TIME, TIME_STEP, NEW_PARTICLE)"

    def emit(self, location, rate, randomness, start_time, time_step, new_particle):
        amount = int(rate * (start_time + time_step)) - int(rate * start_time)

        particles = set()
        for _ in range(amount):
            particle = new_particle()
            offset = randomness * Vector((random() - 0.5, random() - 0.5, random() - 0.5))
            particle.location = location + offset
            particle.velocity = Vector((1, 0, 0))
            particle.born_time = start_time
            particles.add(particle)

        return particles
