import bpy
from bpy.props import *
from .. base_node_types import ImperativeNode

mode_items = [
    ("SET", "Set", ""),
    ("RANDOMIZE", "Randomize", "")
]

class ChangeParticleDirectionNode(ImperativeNode, bpy.types.Node):
    bl_idname = "en_ChangeParticleDirectionNode"
    bl_label = "Change Direction"

    mode: EnumProperty(name = "Mode", default = "RANDOMIZE",
        items = mode_items, update = ImperativeNode.refresh)

    keep_velocity: BoolProperty(name = "Keep Velocity", default = True)

    fade: BoolProperty(name = "Fade", default = False,
        update = ImperativeNode.refresh)

    def create(self):
        self.new_input("en_ControlFlowSocket", "Previous")
        if self.mode == "SET":
            self.new_input("en_VectorSocket", "Direction", "direction")
        elif self.mode == "RANDOMIZE":
            self.new_input("en_FloatSocket", "Strength", "strength", value = 1)

        if self.fade:
            self.new_input("en_FloatSocket", "Duration", "duration", value = 1)

        self.new_output("en_ControlFlowSocket", "Next", "NEXT")

    def draw(self, layout):
        layout.prop(self, "mode", text = "")
        if self.mode == "SET":
            layout.prop(self, "keep_velocity")
        layout.prop(self, "fade")

    def get_code(self):
        if self.mode == "SET":
            if self.keep_velocity:
                yield "_final_direction = direction.normalized() * PARTICLE.velocity.length"
            else:
                yield "_final_direction = direction"
        elif self.mode == "RANDOMIZE":
            yield "_rotation = mathutils.Euler([(random.random() - 0.5) * strength * math.pi * 2 for _ in range(3)])"
            yield "_final_direction = _rotation.to_matrix() @ PARTICLE.velocity"

        if self.fade:
            yield "PARTICLE.effects.add(self.get_change_direction_effect(PARTICLE.velocity, _final_direction, CURRENT_TIME, duration))"
        else:
            yield "PARTICLE.velocity = _final_direction"
        yield "NEXT"

    def get_change_direction_effect(self, start_direction, end_direction, start_time, duration):
        duration = max(duration, 0.001)

        def effect(particle, current_time):
            if current_time >= start_time + duration:
                particle.velocity = end_direction
                return False
            t = (current_time - start_time) / duration
            particle.velocity = start_direction * (1 - t) + end_direction * t
            return True
        return effect