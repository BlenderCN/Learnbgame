import bpy
from bpy.props import *
from . particle_event_trigger_base import ParticleEventTriggerNode

mode_items = [
    ("AGE_REACHED", "Age Reached", ""),
    ("INTERVAL", "Interval", "")
]

class ParticleAgeTriggerNode(ParticleEventTriggerNode, bpy.types.Node):
    bl_idname = "en_ParticleAgeTriggerNode"
    bl_label = "Age Trigger"

    mode: EnumProperty(name = "Mode", default = "AGE_REACHED",
        update = ParticleEventTriggerNode.refresh,
        items = mode_items)

    def create(self):
        self.new_input("en_ParticleTypeSocket", "Particle Type")

        if self.mode == "AGE_REACHED":
            self.new_input("en_FloatSocket", "Age", "trigger_age", value = 1)
        elif self.mode == "INTERVAL":
            self.new_input("en_FloatSocket", "Interval", "interval", value = 1)

        self.new_output("en_ControlFlowSocket", "Next")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")

    def get_trigger_code(self):
        yield "_age = START_TIME - PARTICLE.born_time"
        if self.mode == "AGE_REACHED":
            yield "TRIGGER_TIME = trigger_age - _age"
        elif self.mode == "INTERVAL":
            yield "TRIGGER_TIME = interval - _age % interval if _age > interval / 2 else -1"