from .. base_node_types import DeclarativeNode

class ParticleEmitterNode(DeclarativeNode):
    def get_emit_code(self):
        raise NotImplementedError()